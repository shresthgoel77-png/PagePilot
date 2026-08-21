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
from app.services.evidence_verifier import EvidenceVerifier
from app.services.research_service import ResearchService

logger = logging.getLogger("researchos.chat_engine")

class ChatEngine:
    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service
        self.research_service = ResearchService()
        self.retrieval_service = RetrievalService()
        self.evidence_verifier = EvidenceVerifier()
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def _reformulate_query(self, message: str, db_messages: List[Any]) -> str:
        if not db_messages:
            return message
            
        history_text = []
        for m in db_messages[-5:]:
            role = "User" if m.role == "user" else "Assistant"
            history_text.append(f"{role}: {m.content}")
            
        history_str = "\n".join(history_text)
        
        prompt = (
            "Given the following conversation history and the user's follow-up message, "
            "reformulate the follow-up message to be a standalone search query that captures all necessary context. "
            "If the message is already standalone, return it exactly as is.\n\n"
            f"History:\n{history_str}\n\n"
            f"Follow-up: {message}\n\n"
            "Standalone Query:"
        )
        
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt
            )
            reformulated = response.text.strip()
            logger.info(f"Original query: '{message}' | Reformulated: '{reformulated}'")
            return reformulated
        except Exception as e:
            logger.error(f"Query reformulation failed, falling back to original message: {e}")
            return message

    async def _classify_query(self, message: str) -> str:
        prompt = (
            "Classify the following user query into one of two categories:\n"
            "1. 'SIMPLE': A single-pass factual question or single-document query that can be answered immediately using existing context.\n"
            "2. 'COMPLEX': A multi-step research task requiring decomposition, synthesizing multiple sub-topics, or pulling information from various distinct documents systematically.\n"
            "Return exactly one word: SIMPLE or COMPLEX.\n\n"
            f"Query: {message}\n"
        )
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt
            )
            classification = response.text.strip().upper()
            if "COMPLEX" in classification:
                logger.info(f"Supervisor classified query '{message}' as COMPLEX.")
                return "COMPLEX"
            logger.info(f"Supervisor classified query '{message}' as SIMPLE.")
            return "SIMPLE"
        except Exception as e:
            logger.error(f"Classification failed, defaulting to SIMPLE: {e}")
            return "SIMPLE"

    async def _decompose_query(self, message: str) -> list[dict]:
        prompt = (
            "You are an expert research supervisor. The user has submitted a complex query that requires multi-step research.\n"
            "Your task is to decompose this query into a concrete list of sub-tasks.\n"
            "Produce exactly a JSON array of objects. Each object must have:\n"
            ' - "type": exactly one of ["retrieval", "analysis", "comparison", "verification", "synthesis"]\n'
            ' - "description": a clear, executable instruction for what this step must accomplish (e.g., "retrieve evidence for claim X in doc A")\n\n'
            "Return ONLY the JSON array, no markdown formatting.\n"
            f"Query: {message}"
        )
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            data = json.loads(response.text.strip())
            return data
        except Exception as e:
            print(f"DEBUG EXCEPTION in _decompose_query: {repr(e)}")
            logger.error(f"Decomposition failed: {e}")
            return [{"type": "synthesis", "description": "Synthesize the provided documents based on the complex query."}]

    async def _agent_workflow_placeholder(self, user_id: UUID, session_id: UUID, project_id: UUID, message: str, pdf_ids: List[UUID] = None) -> AsyncGenerator[str, None]:
        logger.info("Routing query to agent workflow placeholder.")
        yield f"data: {json.dumps({'type': 'status', 'content': 'Decomposing complex query into sub-tasks...'})}\n\n"
        
        # Phase 6.2: Decompose and persist
        run = await self.research_service.create_research_run(session_id, message)
        steps_data = await self._decompose_query(message)
        steps = await self.research_service.add_research_steps(run.id, steps_data)
        
        plan_text = "Here is the structured decomposition plan for your research:\n"
        for idx, step in enumerate(steps_data):
            plan_text += f"{idx + 1}. **[{step.get('type', 'task').upper()}]** {step.get('description', '')}\n"
        
        yield f"data: {json.dumps({'type': 'token', 'content': plan_text})}\n\n"
        
        await asyncio.sleep(0.5)
        text = "\n\n*(Routing to the agent workflow to execute this plan will be built in Phases 6.2-6.5...)*"
        yield f"data: {json.dumps({'type': 'token', 'content': text})}\n\n"
        yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"
        
        full_text = plan_text + text
        await self.chat_service.add_message(session_id, "user", message)
        await self.chat_service.add_message(session_id, "assistant", full_text, [])

    async def stream_chat(self, user_id: UUID, session_id: UUID, project_id: UUID, message: str, pdf_ids: List[UUID] = None) -> AsyncGenerator[str, None]:

        
        # Verify strict local bounds implicitly bypassing isolated configurations cleanly parsing native execution seamlessly 
        session, db_messages = await self.chat_service.get_session_details(session_id, user_id)
        if session.project_id != project_id:
            logger.error("Security Vault Alert: Execution parameters crossing disconnected logical project contexts robustly caught.")
            yield f"data: {json.dumps({'type': 'error', 'content': 'System constraints explicitly failed execution boundaries (Project ID mismatch).'})}\n\n"
            return

        classification = await self._classify_query(message)
        if classification == "COMPLEX":
            async for chunk in self._agent_workflow_placeholder(user_id, session_id, project_id, message, pdf_ids):
                yield chunk
            return

        contents = []
        for m in db_messages[-10:]:
            role = "user" if m.role == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m.content)]))

        # Invoke CrossEncoder mappings executing strict vector constraints implicitly locating boundaries efficiently 
        search_query = await self._reformulate_query(message, db_messages)
        
        yield f"data: {json.dumps({'type': 'status', 'content': 'retrieving'})}\n\n"
        
        try:
            retrieved_chunks = await asyncio.to_thread(
                self.retrieval_service.retrieve,
                project_id=str(project_id), 
                query=search_query, 
                top_k=50, 
                final_k=30, 
                pdf_ids=[str(pid) for pid in pdf_ids] if pdf_ids else None
            )
        except Exception as e:
            logger.error(f"Retrieval crashed natively bounded globally: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': f'Retrieval failed structurally: {str(e)}'})}\n\n"
            return

        sources_payload = []
        if not retrieved_chunks:
            yield f"data: {json.dumps({'type': 'error', 'content': 'No relevant evidence found matching your query bounds in the selected documents.'})}\n\n"
            return
            
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
        
        yield f"data: {json.dumps({'type': 'status', 'content': 'generating'})}\n\n"
        
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
            
            # Store completed context mapping accurately initially before long-running evaluation natively 
            msg = await self.chat_service.add_message(session_id, "assistant", full_response, sources_payload)
            
            if retrieved_chunks:
                ver_results = await asyncio.to_thread(
                    self.evidence_verifier.verify_claims, full_response, retrieved_chunks
                )
                yield f"data: {json.dumps({'type': 'verification', 'content': ver_results})}\n\n"
                
                # Attach structured data natively 
                await self.chat_service.update_message_verification(msg.id, "verified", ver_results)
            
        except Exception as e:
            logger.error(f"Gemini orchestration collapsed safely globally intrinsically bounded inherently mapped: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': f'Generation failed structurally: {str(e)}'})}\n\n"
