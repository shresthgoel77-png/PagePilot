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

logger = logging.getLogger("researchos.chat_engine")

class ChatEngine:
    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service
        self.retrieval_service = RetrievalService()
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)



    async def stream_chat(self, user_id: UUID, session_id: UUID, project_id: UUID, message: str, pdf_ids: List[UUID] = None) -> AsyncGenerator[str, None]:
        
        # Verify strict local bounds implicitly bypassing isolated configurations cleanly parsing native execution seamlessly 
        session, db_messages = await self.chat_service.get_session_details(session_id, user_id)
        if session.project_id != project_id:
            logger.error("Security Vault Alert: Execution parameters crossing disconnected logical project contexts robustly caught.")
            yield f"data: {json.dumps({'type': 'error', 'content': 'System constraints explicitly failed execution boundaries.'})}\n\n"
            return

        contents = []
        for m in db_messages[-10:]:
            role = "user" if m.role == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m.content)]))

        # Invoke CrossEncoder mappings executing strict vector constraints implicitly locating boundaries efficiently 
        retrieved_chunks = await asyncio.to_thread(
            self.retrieval_service.retrieve,
            project_id=str(project_id), 
            query=message, 
            top_k=50, 
            final_k=10, 
            pdf_ids=[str(pid) for pid in pdf_ids] if pdf_ids else None
        )

        sources_payload = []
        if not retrieved_chunks:
            system_instruction = "The assembled evidence context does not contain enough evidence to answer this question."
            context_string = ""
        else:
            context_string = ContextAssembler.assemble_context(retrieved_chunks)
            system_instruction = (
                "You are a research assistant. Answer based ONLY on the provided assembled evidence context.\n"
                "If the evidence is insufficient to answer the question, explicitly state that there is not enough information in the provided context, rather than filling gaps from your own knowledge.\n"
                "Never invent document names or page numbers.\n"
                "Preserve the exact identity (filename and page number) of each source referenced in your answer, citing them as [Source: filename, Page X].\n\n"
                f"Context Boundaries:\n{context_string}"
            )
            for c in retrieved_chunks:
                sources_payload.append({
                    "pdf_id": c["pdf_id"],
                    "filename": c["filename"],
                    "page": c["page_number"],
                    "text": c["text"],
                    "score": c.get("score")
                })
                
        # Register user state persistently tracking database mapping structures gracefully natively properly 
        await self.chat_service.add_message(session_id, "user", message)
        
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=message)]))
        
        if not retrieved_chunks:
            yield f"data: {json.dumps({'type': 'token', 'content': system_instruction})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"
            await self.chat_service.add_message(session_id, "assistant", system_instruction, [])
            return

        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
            )
            
            # Asynchronous generation explicitly emitting Server-Sent streams effectively executing natively locally safely 
            response_stream = await self.client.aio.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=contents,
                config=config
            )
            
            response_contents = []
            async for chunk in response_stream:
                if chunk.text:
                    response_contents.append(chunk.text)
                    payload = json.dumps({"type": "token", "content": chunk.text})
                    yield f"data: {payload}\n\n"
                    # Synchronize OS buffer bounds actively resolving explicitly mapping loops smoothly implicitly securely 
                    await asyncio.sleep(0.01)
                    
            full_response = "".join(response_contents)
            yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"
            
            # Store completed context mapping accurately capturing nested payloads inherently locally securely 
            await self.chat_service.add_message(session_id, "assistant", full_response, sources_payload)
            
        except Exception as e:
            logger.error(f"Gemini orchestration collapsed safely globally intrinsically bounded inherently mapped: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': 'Context Provider unresolvable intrinsically tracking limits.'})}\n\n"
