import json
import logging
import asyncio
from typing import List, Dict, Any, Optional
from uuid import UUID

from google import genai
from google.genai import types

from app.core.config import settings
from app.services.retrieval import RetrievalService
from app.services.research_service import ResearchService
from app.services.context_assembler import ContextAssembler

logger = logging.getLogger("researchos.execution_agents")

class RetrievalAgent:
    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.research_service = ResearchService()

    async def execute(self, step_id: UUID, project_id: str, query: str, pdf_ids: Optional[List[str]] = None) -> dict:
        """
        Executes a retrieval step, pulling evidence from the vector store via the existing Phase 3 pipeline.
        Saves a structured artifact with the retrieved data.
        """
        logger.info(f"RetrievalAgent executing step {step_id} for query: {query}")
        await self.research_service.update_research_step(step_id, status="in_progress")
        
        try:
            chunks = await asyncio.to_thread(
                self.retrieval_service.retrieve,
                project_id=project_id,
                query=query,
                top_k=50,
                final_k=15,
                pdf_ids=pdf_ids
            )
            
            artifact = {
                "agent": "RetrievalAgent",
                "query": query,
                "pdf_ids": pdf_ids,
                "retrieved_count": len(chunks),
                "chunks": chunks
            }
            
            await self.research_service.update_research_step(step_id, status="completed", result_data=artifact)
            return artifact
            
        except Exception as e:
            logger.error(f"RetrievalAgent failed: {e}")
            await self.research_service.update_research_step(step_id, status="failed", result_data={"error": str(e)})
            raise

class AnalysisAgent:
    def __init__(self):
        self.research_service = ResearchService()
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def execute(self, step_id: UUID, document_id: str, retrieved_chunks: List[Dict[str, Any]], query: str) -> dict:
        """
        Synthesizes findings from a single document's retrieved evidence.
        """
        logger.info(f"AnalysisAgent executing step {step_id} for doc {document_id}")
        await self.research_service.update_research_step(step_id, status="in_progress")
        
        try:
            if not retrieved_chunks:
                artifact = {
                    "document_id": document_id,
                    "findings": "No evidence retrieved for this document.",
                    "success": False
                }
            else:
                context_string = ContextAssembler.assemble_context(retrieved_chunks, max_chars=30000)
                
                system_instruction = (
                    "You are an Analysis Agent. Your job is to extract findings from the assembled context related to the user's query.\n"
                    "Output a valid JSON object with the following schema:\n"
                    "{\n"
                    '  "document_id": "' + document_id + '",\n'
                    '  "key_findings": ["finding 1", "finding 2"],\n'
                    '  "summary": "Brief summary of the findings"\n'
                    "}\n"
                    "Respond with ONLY the JSON, starting with '{'."
                )
                
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json"
                )
                
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model="gemini-2.5-flash",
                    contents=query,
                    config=config
                )
                
                llm_json = response.text.strip()
                parsed_findings = json.loads(llm_json)
                
                artifact = {
                    "agent": "AnalysisAgent",
                    "query": query,
                    "document_id": document_id,
                    "analysis": parsed_findings,
                    "success": True
                }
            
            await self.research_service.update_research_step(step_id, status="completed", result_data=artifact)
            return artifact
            
        except Exception as e:
            logger.error(f"AnalysisAgent failed: {e}")
            await self.research_service.update_research_step(step_id, status="failed", result_data={"error": str(e)})
            raise

class ComparisonAgent:
    def __init__(self):
        self.research_service = ResearchService()
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def execute(self, step_id: UUID, documents_findings: List[Dict[str, Any]], query: str) -> dict:
        """
        Takes findings from >=2 documents and identifies agreements/contradictions.
        """
        logger.info(f"ComparisonAgent executing step {step_id}")
        await self.research_service.update_research_step(step_id, status="in_progress")
        
        try:
            if len(documents_findings) < 2:
                raise ValueError("ComparisonAgent requires findings from at least 2 documents.")
                
            context_pieces = []
            for item in documents_findings:
                doc_id = item.get("document_id", "Unknown")
                findings_str = json.dumps(item.get("analysis", {}), indent=2)
                context_pieces.append(f"--- Document: {doc_id} ---\n{findings_str}\n")
                
            combined_context = "\n".join(context_pieces)
            
            system_instruction = (
                "You are a Comparison Agent. You are given synthesized findings from multiple documents.\n"
                "Your task is to identify key agreements and contradictions across these documents regarding the overarching query.\n"
                "Output a valid JSON object with the exact schema:\n"
                "{\n"
                '  "agreements": ["agreement 1", ...],\n'
                '  "contradictions": ["contradiction 1", ...],\n'
                '  "synthesis_summary": "Overall synthesis"\n'
                "}\n"
                "Respond with ONLY the JSON object."
            )
            
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json"
            )
            
            prompt = f"Query: {query}\n\nAnalyses:\n{combined_context}"
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt,
                config=config
            )
            
            llm_json = response.text.strip()
            parsed_comparison = json.loads(llm_json)
            
            artifact = {
                "agent": "ComparisonAgent",
                "query": query,
                "comparison": parsed_comparison,
                "success": True
            }
            
            await self.research_service.update_research_step(step_id, status="completed", result_data=artifact)
            return artifact
            
        except Exception as e:
            logger.error(f"ComparisonAgent failed: {e}")
            await self.research_service.update_research_step(step_id, status="failed", result_data={"error": str(e)})
            raise
