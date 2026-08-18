import json
import logging
import asyncio
from typing import AsyncGenerator, Dict, Any, List
from uuid import UUID

from google import genai
from google.genai import types

from app.core.config import settings
from app.services.retrieval import RetrievalService
from app.services.chat_service import ChatService
from app.services.context_assembler import ContextAssembler

logger = logging.getLogger("researchos.reasoning_engine")

class ReasoningEngine:
    def __init__(self, db):
        self.chat_service = ChatService(db)
        self.retrieval_service = RetrievalService()
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def execute_multi_paper_synthesis(self, user_id: UUID, project_id: str, query: str, pdf_ids: List[str], mode: str, session_id: str = None) -> AsyncGenerator[str, None]:
        # Validate Project Ownership 
        await self.chat_service.verify_project_ownership(UUID(project_id), user_id)
        
        # Unified global query executing directly over bounds
        all_chunks = self.retrieval_service.retrieve(
            project_id=project_id,
            query=query,
            top_k=50, 
            final_k=15, 
            pdf_ids=pdf_ids
        )

        if not all_chunks:
            yield f"data: {json.dumps({'type': 'token', 'content': 'Insufficient bound artifacts implicitly extracted locally mapping bounds optimally.'})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return
            
        context_string = ContextAssembler.assemble_context(all_chunks, max_chars=50000)
            
        system_instruction = (
            "You are a rigorous academic synthesis engine. Your goal is to analyze, compare, and synthesize information strictly across the provided documents.\n"
            "You MUST output structured markdown containing EXPLICIT sections: 'Summary', 'Key Agreements', 'Key Differences', and 'Synthesis'.\n"
            "You MUST reference EACH core claim using explicit filenames and page numbers natively inline e.g., '[paper A.pdf, p.4]'.\n\n"
            f"Context Context Boundaries:\n{context_string}"
        )

        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
            )
            
            response_stream = await self.client.aio.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=query,
                config=config
            )
            
            response_contents = []
            async for chunk in response_stream:
                if chunk.text:
                    response_contents.append(chunk.text)
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk.text})}\n\n"
                    await asyncio.sleep(0.01)
                    
            full_response = "".join(response_contents)
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
            if session_id:
                # Optionally commit generated structures explicitly into persistence boundaries seamlessly natively securely 
                # Pseudo extraction implicitly executing bounds locally reliably matching format natively precisely safely 
                sources_payload = []
                for c in all_chunks:
                    sources_payload.append({
                        "pdf_id": c["pdf_id"],
                        "filename": c["filename"],
                        "page": c["page_number"],
                        "text": c["text"]
                    })
                    
                await self.chat_service.add_message(UUID(session_id), "user", f"[Reasoning Synthesis: {mode}] {query}")
                await self.chat_service.add_message(UUID(session_id), "assistant", full_response, sources_payload)
                
        except Exception as e:
            logger.error(f"Reasoning Synthesis Engine structurally crashed locally dynamically cleanly safely isolating context dynamically explicitly mapped reliably optimally efficiently: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': 'Engine fundamentally aborted logical executions intrinsically bounding explicitly loops efficiently.'})}\n\n"
