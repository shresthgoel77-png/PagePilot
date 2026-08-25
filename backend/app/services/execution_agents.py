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
from app.services.evidence_verifier import EvidenceVerifier

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
            return artifact
            
        except Exception as e:
            logger.error(f"RetrievalAgent failed: {e}")
            raise
            
class AnalysisAgent:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def execute(self, step_id: UUID, document_id: str, retrieved_chunks: List[Dict[str, Any]], query: str) -> dict:
        """
        Synthesizes findings from a single document's retrieved evidence.
        """
        logger.info(f"AnalysisAgent executing step {step_id} for doc {document_id}")
        
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
                    model="gemini-3.5-flash",
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
            return artifact
            
        except Exception as e:
            logger.error(f"AnalysisAgent failed: {e}")
            raise

class ComparisonAgent:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def execute(self, step_id: UUID, documents_findings: List[Dict[str, Any]], query: str, force_unsupported_claim: bool = False) -> dict:
        """
        Takes findings from >=2 documents and identifies agreements/contradictions.
        """
        logger.info(f"ComparisonAgent executing step {step_id}")
        
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
            
            if force_unsupported_claim:
                system_instruction += "\nCRITICAL INSTRUCTION: You MUST deliberately include one completely unsupported fake contradiction claim about 'Neo-Tokyo is the capital of Mars' in your contradictions list."

            
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json"
            )
            
            prompt = f"Query: {query}\n\nAnalyses:\n{combined_context}"
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-3.5-flash",
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
            return artifact
            
        except Exception as e:
            raise

class VerificationAgent:
    def __init__(self):
        self.evidence_verifier = EvidenceVerifier()

    async def execute(self, step_id: UUID, artifact_to_verify: dict, retrieved_chunks: List[Dict[str, Any]]) -> dict:
        logger.info(f"VerificationAgent executing step {step_id}")
        
        try:
            results = await asyncio.to_thread(self.evidence_verifier.verify_claims, artifact_to_verify, retrieved_chunks)
            
            supported_claims = [r for r in results if r["supported"]]
            unsupported_claims = [r for r in results if not r["supported"]]
            
            artifact = {
                "agent": "VerificationAgent",
                "verified_claims": results,
                "supported_count": len(supported_claims),
                "unsupported_count": len(unsupported_claims),
                "success": True
            }
            return artifact
            
        except Exception as e:
            logger.error(f"VerificationAgent failed: {e}")
            raise

class SynthesisAgent:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def execute(self, step_id: UUID, verified_artifact: dict, query: str) -> dict:
        """Fallback synchronous method for testing or backwards compatibility."""
        logger.info(f"SynthesisAgent executing step {step_id}")
        
        try:
            supported_claims = [r for r in verified_artifact.get("verified_claims", []) if r.get("supported")]
            claims_text = "\n".join([f"- {c.get('claim')} [Source: {c.get('filename')}, Page: {c.get('page')}]" for c in supported_claims])
            
            system_instruction = (
                "You are a Synthesis Agent. You are given a list of VERIFIED claims from previous research steps.\n"
                "Write a final cohesive narrative responding to the user query using only these verified claims.\n"
                "If the evidence is insufficient to answer the question, explicitly state that there is not enough information in the provided context, rather than filling gaps from your own knowledge.\n"
                "Never invent document names or page numbers.\n"
                "Include markdown citations natively inline (e.g., '[Source.pdf, p.4]')."
            )
            
            config = types.GenerateContentConfig(
                system_instruction=system_instruction
            )
            
            prompt = f"Query: {query}\n\nVerified Claims:\n{claims_text}"
            
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-3.5-flash",
                contents=prompt,
                config=config
            )
            
            artifact = {
                "agent": "SynthesisAgent",
                "query": query,
                "synthesis": response.text,
                "input_claims_used": [c.get('claim') for c in supported_claims],
                "success": True
            }
            
            return artifact
            
        except Exception as e:
            logger.error(f"SynthesisAgent failed: {e}")
            raise

    async def execute_stream(self, step_id: UUID, verified_artifact: dict, query: str):
        """Asynchronous generator yielding syntax tokens directly for SSE broadcasting."""
        logger.info(f"SynthesisAgent executing sequence stream {step_id}")
        
        try:
            supported_claims = [r for r in verified_artifact.get("verified_claims", []) if r.get("supported")]
            claims_text = "\n".join([f"- {c.get('claim')} [Source: {c.get('filename')}, Page: {c.get('page')}]" for c in supported_claims])
            
            system_instruction = (
                "You are a front-facing Synthesis Agent. You are given a list of strictly VERIFIED claims from deep-dive research.\n"
                "Write a final cohesive, natural-language narrative responding to the user query using only these verified claims.\n"
                "If the valid claims are insufficient to answer the overarching question fully, explicitly admit what remains unproven or unsupported.\n"
                "Never invent document names or assume extra technical facts outside this curated list.\n"
                "Include markdown citations natively inline, perfectly matching the provided Source names (e.g., '[Source.pdf, p.4]')."
            )
            
            config = types.GenerateContentConfig(
                system_instruction=system_instruction
            )
            prompt = f"Query: {query}\n\nVerified Claims:\n{claims_text}"
            
            response_stream = await self.client.aio.models.generate_content_stream(
                model="gemini-3.5-flash",
                contents=prompt,
                config=config
            )
            
            full_text = []
            async for chunk in response_stream:
                if chunk.text:
                    full_text.append(chunk.text)
                    yield chunk.text
                    
            final_synthesis = "".join(full_text)
            
            artifact = {
                "agent": "SynthesisAgent",
                "query": query,
                "synthesis": final_synthesis,
                "input_claims_used": [c.get('claim') for c in supported_claims],
                "success": True
            }
            
        except Exception as e:
            logger.error(f"SynthesisAgent stream failed globally logically tracked: {e}")
            raise
