import os
import sys
import json
import uuid
import time
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from reportlab.pdfgen import canvas

import qdrant_client
qc = qdrant_client.QdrantClient(location=":memory:")
import app.db.qdrant
app.db.qdrant.qdrant_client = qc

from app.services.chat_engine import ChatEngine
from app.services.chat_service import ChatService
from app.services.indexing_pipeline import run as pipeline_run
from app.models.pdf import PDF, PDFStatus

def setup_real_docs():
    docs = {
        "Mars_Colonization.pdf": {
            "text": "The primary energy requirements for a Mars colony can be satisfied by a mix of solar and nuclear sources to sustain long-term survival.",
            "pdf_id": str(uuid.uuid4())
        },
        "Deep_Learning_Fundamentals.pdf": {
            "text": "Gradient descent decay refers to applying a momentum factor that mathematically restricts wild oscillation across neural layers.",
            "pdf_id": str(uuid.uuid4())
        }
    }
    # True PDF generation natively readable by PyMuPDF sequentially
    for filename, data in docs.items():
        c = canvas.Canvas(filename)
        # Using a very basic text layout to ensure it's parseable
        c.drawString(72, 800, data["text"])
        c.save()
    return docs

async def evaluate_ingestion_success_rate(mock_docs, project_id):
    print("\n--- Evaluating Real Ingestion Pipeline ---")
    mock_db = MagicMock()
    mock_session = AsyncMock()
    mock_db.return_value.__aenter__.return_value = mock_session
    
    success_count = 0
    traces = []
    
    # We patch Postgres ONLY. The parser and embedder run for real!
    with patch("app.services.indexing_pipeline.AsyncSessionLocal", new=mock_db):
        for filename, data in mock_docs.items():
            pdf_id = data["pdf_id"]
            mock_pdf = MagicMock()
            mock_pdf.id = pdf_id
            mock_pdf.project_id = project_id
            mock_pdf.filename = filename
            mock_pdf.file_path = filename
            
            # mock status property natively
            status_trace = ["queued"]
            def set_status(self, val):
                status_trace.append(str(val))
            type(mock_pdf).status = property(lambda self: status_trace[-1], set_status)
                
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_pdf
            mock_session.execute.return_value = mock_result
            
            try:
                # Runs actual PDFParserService, EmbeddingService, VectorStoreService(:memory:) natively!
                await pipeline_run(project_id, filename, uuid.uuid4())
                success_count += 1
                traces.append({"doc": filename, "trace": status_trace})
            except Exception as e:
                print(f"Ingestion failed for {filename}: {e}")
                
    success_rate = success_count / len(mock_docs) if mock_docs else 0
    print(f"Ingestion Success Rate: {success_rate * 100}%")
    for t in traces:
        print(f"  {t['doc']}: {' -> '.join(t['trace'])}")
        
    return success_rate, traces

async def evaluate_chat_pipeline(mock_docs, project_id):
    print("\n--- Evaluating Real Chat Agent Pipeline ---")
    
    with open("benchmark_queries.json", "r") as f:
        queries = json.load(f)
        
    eval_results = []
    
    mock_db = AsyncMock()
    mock_chat_service = ChatService(db=mock_db)
    mock_sess = MagicMock()
    mock_sess.project_id = project_id
    mock_chat_service.get_session_details = AsyncMock(return_value=(mock_sess, []))
    mock_chat_service.add_message = AsyncMock(return_value=MagicMock(id=uuid.uuid4()))
    mock_chat_service.update_message_verification = AsyncMock()
    
    engine = ChatEngine(chat_service=mock_chat_service)
    
    overall_supportable = []
    overall_unsupportable = []
    overall_latency = []
    overall_recall = []
    
    # We patch only database orchestrative methods keeping ALL Gemini + Qdrant logic true!
    with patch("app.services.research_service.ResearchService.update_research_step") as mock_urs, \
         patch("app.services.research_service.ResearchService.create_research_run") as mock_cr, \
         patch("app.services.research_service.ResearchService.add_research_steps") as mock_ars:
         
        mock_cr_run = MagicMock()
        mock_cr_run.id = uuid.uuid4()
        mock_cr.return_value = mock_cr_run
        
        mock_urs.return_value = {}
        
        def mock_add_steps(run_id, steps_data):
            for s in steps_data:
                s["id"] = str(uuid.uuid4())
            return steps_data
        mock_ars.side_effect = mock_add_steps
        
        for i, q in enumerate(queries):
            print(f"Running Eval Query: {q['query']}")
            
            target_pdf_id = mock_docs[q['gt_source_doc']]['pdf_id']
            
            start_time = time.monotonic()
            outputs = []
            # TRUE EXECUTION THROUGH LLM AGENTS
            try:
                async for chunk in engine.stream_chat(uuid.uuid4(), uuid.uuid4(), project_id, q['query'], pdf_ids=[target_pdf_id]):
                    outputs.append(chunk)
            except Exception as e:
                print(f"Pipeline crashed critically natively: {e}")
                
            latency = time.monotonic() - start_time
            overall_latency.append(latency)
            print(f"  Latency: {latency:.2f}s")
            
            # --- METRICS CALCULATIONS ---
            # 1. Recall
            recorded_chunks = [json.loads(o.replace('data: ', ''))['content'] for o in outputs if '"type": "artifact"' in o and '"step": "retrieval"' in o]
            recall_score = 0.0
            if recorded_chunks:
                # Check mapping against ground truth keywords natively!
                retrieved_text = " ".join([c.get("text", "").lower() for c in recorded_chunks[0].get("chunks", [])])
                hits = sum(1 for kw in q['gt_keywords'] if kw.lower() in retrieved_text)
                recall_score = hits / len(q['gt_keywords']) if q['gt_keywords'] else 0.0
            overall_recall.append(recall_score)
            
            # 2. Groundedness
            v_arts = [json.loads(o.replace('data: ', ''))['content'] for o in outputs if '"type": "artifact"' in o and '"step": "verification"' in o]
            if v_arts:
                supp = v_arts[0].get("supported_count", 0)
                unsupp = v_arts[0].get("unsupported_count", 0)
                tot = supp + unsupp
                grounded_fraction = supp / tot if tot > 0 else 0
                unsupp_fraction = unsupp / tot if tot > 0 else 0
            else:
                grounded_fraction = 0.0
                unsupp_fraction = 1.0 # Failed gracefully yielding full drop
                
            overall_supportable.append(grounded_fraction)
            overall_unsupportable.append(unsupp_fraction)
            print(f"  Groundedness: {grounded_fraction:.2%} | Unsupported: {unsupp_fraction:.2%}")
            
            # 3. Citation Check
            final_ans = "".join([json.loads(o.replace('data: ', ''))['content'] for o in outputs if '"type": "token"' in o])
            print(f"  [GENERATED SYNTHESIS DUMP]: {final_ans}")
            citation_correct = "Source: " in final_ans or "Source" in final_ans or "[1]" in final_ans # Very basic syntactical assert covering true LLM variations natively
            print(f"  Citation Syntactically Present: {citation_correct}")
            
            eval_results.append({
                "query": q["query"],
                "latency_s": latency,
                "recall_score": recall_score,
                "grounded_fraction": grounded_fraction,
                "unsupported_fraction": unsupp_fraction,
                "citation_correct": citation_correct
            })
            
    return eval_results, overall_latency, overall_recall, overall_supportable, overall_unsupportable

async def main():
    # Make sure Qdrant Collection exists inside the memory store
    from app.db.qdrant import ensure_collection
    ensure_collection()
    
    project_id = str(uuid.uuid4())
    mock_docs = setup_real_docs()
    
    # Run exact pipeline limits securely against actual models natively!
    ingestion_rate, traces = await evaluate_ingestion_success_rate(mock_docs, project_id)
    chat_results, lats, recalls, supps, unsupps = await evaluate_chat_pipeline(mock_docs, project_id)
    
    report = {
        "summary": {
            "ingestion_success_rate": ingestion_rate,
            "average_latency_s": sum(lats)/len(lats) if lats else 0,
            "average_recall": sum(recalls)/len(recalls) if recalls else 0,
            "average_groundedness": sum(supps)/len(supps) if supps else 0,
            "average_unsupported_rate": sum(unsupps)/len(unsupps) if unsupps else 0,
        },
        "query_results": chat_results,
        "ingestion_traces": traces
    }
    
    with open("eval_results.json", "w") as f:
        json.dump(report, f, indent=2)
        
    print("\n================ EVALUATION SUMMARY ================")
    print(json.dumps(report["summary"], indent=2))
    print("====================================================")
    print("Results logged to eval_results.json natively.\n")

if __name__ == "__main__":
    asyncio.run(main())
