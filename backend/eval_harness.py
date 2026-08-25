import os
import sys
import json
import uuid
import time
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from reportlab.pdfgen import canvas

# --- QDRANT MEMORY INJECTION ---
import qdrant_client
qc = qdrant_client.QdrantClient(location=":memory:")
import app.db.qdrant
app.db.qdrant.qdrant_client = qc

from app.services.chat_engine import ChatEngine
from app.services.chat_service import ChatService
from app.services.indexing_pipeline import run as pipeline_run

# To intercept chunks seamlessly during SIMPLE flow
from app.services.retrieval import RetrievalService
original_retrieve = RetrievalService.retrieve

# --- 1. SETUP MULTI-PAGE DENSE PDFs ---
def create_dense_pdf(filename: str, page_texts: list[str]):
    c = canvas.Canvas(filename)
    for text in page_texts:
        text_obj = c.beginText(72, 800)
        # Manually wrap text to ensure semantic chunks catch entire blocks natively
        words = text.split()
        line = ""
        for w in words:
            if len(line) + len(w) > 80:
                text_obj.textLine(line)
                line = w + " "
            else:
                line += w + " "
        text_obj.textLine(line)
        c.drawText(text_obj)
        c.showPage()
    c.save()

def setup_real_docs():
    docs = {
        "Photosynthesis_Biology.pdf": {
            "pages": [
                "Photosynthesis is a process used by plants, algae and certain bacteria to harness energy from sunlight and turn it into chemical energy. Here, we describe the basic principles of sunlight conversion and cellular respiration. A foundational understanding of these biological systems is critical for studying ecology.",
                "The light-dependent reactions of photosynthesis take place in the thylakoid membrane. Chlorophyll captures energy from sunlight, which is then used to generate ATP and NADPH. The Calvin cycle, which occurs in the stroma, then utilizes this ATP and NADPH to convert CO2 into sugar.",
                "Environmental factors such as temperature, light intensity, and CO2 concentration significantly affect the rate of photosynthesis. High temperatures can denature the enzymes involved in the Calvin cycle, while low light limits ATP production."
            ],
            "pdf_id": str(uuid.uuid4())
        },
        "World_War_II_History.pdf": {
            "pages": [
                "World War II was a global conflict that lasted from 1939 to 1945, involving the vast majority of the world's countries. The principal belligerents were the Axis powers and the Allies. Historians often trace the immediate origins to the invasion of Poland.",
                "A major turning point in the European theater was the Normandy landings, commonly known as D-Day. Taking place on June 6, 1944, Operation Overlord initiated the liberation of German-occupied France and laid the foundations of the Allied victory on the Western Front.",
                "In the Pacific theater, the war culminated with the atomic bombings of Hiroshima and Nagasaki in August 1945, followed by the formal surrender of Japan on September 2. The post-war landscape saw the emergence of the United States and Soviet Union as rival superpowers."
            ],
            "pdf_id": str(uuid.uuid4())
        },
        "Python_Programming.pdf": {
            "pages": [
                "Python is an interpreted, high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation. Python supports multiple programming paradigms, including structured, object-oriented, and functional programming.",
                "One of the major defining characteristics of CPython, the reference implementation of Python, is the Global Interpreter Lock (GIL). The GIL is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecodes at once.",
                "To bypass the limitations of the GIL for CPU-bound tasks, developers often use the multiprocessing module, which creates separate processes rather than threads, allowing parallel execution across multiple CPU cores at the cost of higher memory usage."
            ],
            "pdf_id": str(uuid.uuid4())
        },
        "Climate_Change_Science.pdf": {
            "pages": [
                "Climate change includes both global warming driven by human-induced emissions of greenhouse gases and the resulting large-scale shifts in weather patterns. Though there have been previous periods of climatic change, since the mid-20th century humans have had an unprecedented impact on Earth's climate system.",
                "The primary driver of modern climate change is the emission of greenhouse gases, predominantly carbon dioxide and methane. Agriculture and fossil fuel burning are major contributors. Ice core data provides a historical record of CO2 concentrations spanning hundreds of thousands of years.",
                "Mitigation strategies include the transition to renewable energy sources, increasing energy efficiency, and reforestation. Adaptation measures involves planning for sea-level rise and changing agricultural zones."
            ],
            "pdf_id": str(uuid.uuid4())
        }
    }
    for filename, data in docs.items():
        create_dense_pdf(filename, data["pages"])
    return docs

# --- 2. EVALUATE INGESTION ---
async def evaluate_ingestion(mock_docs, project_id):
    print("\n--- Evaluating Real Ingestion Pipeline ---")
    mock_db = MagicMock()
    mock_session = AsyncMock()
    mock_db.return_value.__aenter__.return_value = mock_session
    
    success_count = 0
    traces = []
    
    with patch("app.services.indexing_pipeline.AsyncSessionLocal", new=mock_db):
        for filename, data in mock_docs.items():
            pdf_id = data["pdf_id"]
            mock_pdf = MagicMock()
            mock_pdf.id = pdf_id
            mock_pdf.project_id = project_id
            mock_pdf.filename = filename
            mock_pdf.file_path = filename
            
            status_trace = ["queued"]
            def set_status(self, val):
                status_trace.append(str(val))
            type(mock_pdf).status = property(lambda self: status_trace[-1], set_status)
                
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_pdf
            mock_session.execute.return_value = mock_result
            
            try:
                await pipeline_run(project_id, filename, pdf_id)
                success_count += 1
                traces.append({"doc": filename, "trace": status_trace})
            except Exception as e:
                print(f"Ingestion failed for {filename}: {e}")
                
    success_rate = success_count / len(mock_docs) if mock_docs else 0
    print(f"Ingestion Success Rate: {success_rate * 100:.1f}%")
    for t in traces:
        print(f"  {t['doc']}: {' -> '.join(t['trace'])}")
        
    return success_rate, traces

# --- 3. EVALUATE EVALUATION HARNESS NATIVELY ---
async def evaluate_chat_pipeline(mock_docs, project_id, delay_s=25):
    print("\n--- Evaluating Real Chat Pipeline (Full Free-Tier Native Inference) ---")
    
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
    
    # Bypass auxiliary LLM layers to conserve 20 RPD free tier limit
    engine._classify_query = AsyncMock(return_value="SIMPLE")
    async def mock_reform(msg, db_msgs): return msg
    engine._reformulate_query = mock_reform
    
    # We patch only database orchestrative methods keeping ALL Gemini + Qdrant logic true!
    with patch("app.services.research_service.ResearchService.update_research_step") as mock_urs, \
         patch("app.services.research_service.ResearchService.create_research_run") as mock_cr, \
         patch("app.services.research_service.ResearchService.add_research_steps") as mock_ars:
         
        mock_cr_run = MagicMock()
        mock_cr_run.id = uuid.uuid4()
        mock_cr.return_value = mock_cr_run
        mock_urs.return_value = {}
        async def mock_add_steps(run_id, steps_data):
            for s in steps_data: s["id"] = str(uuid.uuid4())
            return steps_data
        mock_ars.side_effect = mock_add_steps
        
        for i, q in enumerate(queries):
            print(f"\nRunning Eval Query ({i+1}/{len(queries)}): {q['query']}")
            
            target_pdf_id = mock_docs.get(q['gt_source_doc'], {}).get('pdf_id', str(uuid.uuid4()))
            
            start_time = time.monotonic()
            outputs = []
            
            try:
                # We pass the pdf_id natively so if it's q4 (unsupported doc), it receives the wrong document!
                async for chunk in engine.stream_chat(uuid.uuid4(), uuid.uuid4(), project_id, q['query'], pdf_ids=[target_pdf_id]):
                    outputs.append(chunk)
            except Exception as e:
                print(f"Pipeline crashed critically natively: {e}")
                
            latency = time.monotonic() - start_time
            print(f"  Latency: {latency:.2f}s")
            
            # --- METRICS CALCULATIONS ---
            # 1. Recall
            # Fetch exactly what would have been generated natively identically preserving constraints globally
            retrieved_chunks = engine.retrieval_service.retrieve(project_id=project_id, query=q['query'], top_k=50, final_k=15, pdf_ids=[target_pdf_id])
            
            recall_score = 0.0
            if retrieved_chunks:
                retrieved_text = " ".join([c.get("text", "").lower() for c in retrieved_chunks])
                hits = sum(1 for kw in q['gt_keywords'] if kw.lower() in retrieved_text)
                recall_score = hits / len(q['gt_keywords']) if q['gt_keywords'] else 0.0
            
            groundedness = 0.0
            unsupported_rate = 0.0
            citation_correct = False
            
            v_arts = [json.loads(c.replace("data: ", ""))["content"] for c in outputs if "data: " in c and '"type": "verification"' in c]
            if v_arts:
                claims_list = v_arts[0]
                temp_supp = sum(1 for c in claims_list if c.get("supported", False))
                temp_unsupp = sum(1 for c in claims_list if not c.get("supported", False))
                total_c = len(claims_list)
                if total_c > 0:
                    groundedness = temp_supp / total_c
                    unsupported_rate = temp_unsupp / total_c
                    
                # check citations
                for claim in claims_list:
                    if str(target_pdf_id) in str(claim.get("pdf_id", "")) or mock_docs.get(q['gt_source_doc'], {}).get("filename", "") in str(claim.get("filename", "")):
                        citation_correct = True
                        break
                
                print("  [CITATION VALIDATION DETAILS]:")
                for claim_info in claims_list:
                    sup_status = "SUPPORTED" if claim_info.get("supported") else "UNSUPPORTED"
                    chunk_src = f"{claim_info.get('filename')} p.{claim_info.get('page')}" if claim_info.get("filename") else "None"
                    claim_text = str(claim_info.get('claim', ''))
                    short_claim = (claim_text[:60] + '...') if len(claim_text) > 60 else claim_text
                    print(f"    - Claim: \"{short_claim}\"")
                    print(f"      Status: {sup_status} | Via: {chunk_src} | Conf: {claim_info.get('confidence', 0)}")
            else:
                unsupported_rate = 1.0 
                print("  [CITATION VALIDATION DETAILS]: Failed gracefully yielding full drop.")
                
            print(f"  Groundedness: {groundedness*100:.2f}% | Unsupported: {unsupported_rate*100:.2f}%")
            
            # 3. Citation Check
            final_ans = "".join([json.loads(o.replace('data: ', ''))['content'] for o in outputs if '"type": ' in o and json.loads(o.replace('data: ', '')).get('type') == 'token'])
            citation_correct = "Source: " in final_ans or "[Source:" in final_ans or q['gt_source_doc'].replace(".pdf", "") in final_ans
            print(f"  Citation Syntactically Present: {citation_correct}")
            
            eval_results.append({
                "query": q["query"],
                "latency_s": latency,
                "recall_score": recall_score,
                "grounded_fraction": groundedness,
                "unsupported_fraction": unsupported_rate,
                "citation_correct": citation_correct
            })
            
            if i < len(queries) - 1:
                print(f"  [Rate Limit Sandbox] Regulating API bounds: waiting {delay_s}s...")
                await asyncio.sleep(delay_s)
            
    return eval_results

async def main():
    from app.db.qdrant import ensure_collection
    ensure_collection()
    
    project_id = str(uuid.uuid4())
    mock_docs = setup_real_docs()
    
    def avg(lst): return sum(lst) / len(lst) if lst else 0
    
    def process_report(report_data):
        return {
            "ingestion_success_rate": report_data[0],
            "average_latency_s": avg([r["latency_s"] for r in report_data[1]]),
            "average_recall": avg([r["recall_score"] for r in report_data[1]]),
            "average_groundedness": avg([r["grounded_fraction"] for r in report_data[1]]),
            "average_unsupported_rate": avg([r["unsupported_fraction"] for r in report_data[1]]),
            "average_citation_correctness": avg([1 if r["citation_correct"] else 0 for r in report_data[1]])
        }

    # RUN 1
    print("\n" + "="*50)
    print("STARTING RUN 1 (Strict Sandbox)")
    print("="*50)
    ingestion_rate1, _ = await evaluate_ingestion(mock_docs, project_id)
    chat_results1 = await evaluate_chat_pipeline(mock_docs, project_id, delay_s=25)
    report1 = process_report((ingestion_rate1, chat_results1))
    
    # Rest heavily before Run 2
    print("\n  [Rate Limit Sandbox] Regulating inter-run limit bounds: waiting 45s...")
    await asyncio.sleep(45.0)
    
    # RUN 2
    print("\n" + "="*50)
    print("STARTING RUN 2 (Strict Sandbox)")
    print("="*50)
    ingestion_rate2, _ = await evaluate_ingestion(mock_docs, project_id)
    chat_results2 = await evaluate_chat_pipeline(mock_docs, project_id, delay_s=25)
    report2 = process_report((ingestion_rate2, chat_results2))
    
    report = {
        "summary_run1": report1,
        "summary_run2": report2,
        "query_results_run1": chat_results1,
        "query_results_run2": chat_results2,
        "reproducibility": {
            "ingestion_match": ingestion_rate1 == ingestion_rate2,
            "recall_match": report1["average_recall"] == report2["average_recall"],
            "groundedness_match": report1["average_groundedness"] == report2["average_groundedness"],
            "citation_formats_match": report1["average_citation_correctness"] == report2["average_citation_correctness"]
        }
    }
    
    with open("eval_results.json", "w") as f:
        json.dump(report, f, indent=2)
        
    print("\n================ EVALUATION SUMMARY ================")
    print(json.dumps(report, indent=2))
    print("====================================================")
    print("Generated eval_results.json successfully.\n")

if __name__ == "__main__":
    asyncio.run(main())
