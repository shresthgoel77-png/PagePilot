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
from app.services.execution_agents import RetrievalAgent, AnalysisAgent, ComparisonAgent, VerificationAgent, SynthesisAgent

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

    async def _execute_complex_research(self, user_id: UUID, session_id: UUID, project_id: UUID, message: str, pdf_ids: List[UUID] = None) -> AsyncGenerator[str, None]:
        logger.info("Routing query to unified multi-agent architecture.")
        yield f"data: {json.dumps({'type': 'status', 'content': 'Decomposing complex query into sub-tasks...'})}\n\n"
        
        # Phase 6.2: Decomposing explicitly maps sub tasks sequentially safely tracking dynamically 
        run = await self.research_service.create_research_run(
            session_id=session_id, 
            project_id=project_id, 
            user_id=user_id, 
            query=message,
            mode="complex"
        )
        steps_data = await self._decompose_query(message)
        steps = await self.research_service.add_research_steps(run.id, steps_data)
        
        plan_text = "Here is the structured decomposition plan for your research:\n"
        for idx, step in enumerate(steps_data):
            plan_text += f"{idx + 1}. **[{step.get('type', 'task').upper()}]** {step.get('description', '')}\n"
        
        yield f"data: {json.dumps({'type': 'token', 'content': plan_text})}\n\n"
        await asyncio.sleep(0.5)
        
        retrieval_agent = RetrievalAgent()
        analysis_agent = AnalysisAgent()
        comparison_agent = ComparisonAgent()
        verification_agent = VerificationAgent()
        synthesis_agent = SynthesisAgent()
        
        retrieval_step = next((s for s in steps if s.get("type") == "retrieval"), None)
        analysis_steps = [s for s in steps if s.get("type") == "analysis"]
        comparison_step = next((s for s in steps if s.get("type") == "comparison"), None)
        verification_step = next((s for s in steps if s.get("type") == "verification"), None)
        synthesis_step = next((s for s in steps if s.get("type") == "synthesis"), None)
        
        async def run_with_retry(agent_exec_coro, step_id, max_retries=3):
            for attempt in range(max_retries):
                try:
                    res = await agent_exec_coro()
                    yield res
                    return
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    logger.warning(f"Agent transient failure on step {step_id}: {e}. Retrying ({attempt + 1}/{max_retries})...")
                    # Broadcast transient retry status
                    error_msg = f"Transient failure internally handled gracefully globally securely mapped inherently: {e}. Retrying step ({attempt + 1}/{max_retries})..."
                    yield f"data: {json.dumps({'type': 'step_status', 'step': {'id': str(step_id), 'status': 'retrying', 'error': error_msg}})}\n\n"
                    await asyncio.sleep(1 * (attempt + 1))
        
        retrieval_artifact = {"chunks": []}
        if retrieval_step:
            updated_step = await self.research_service.update_research_step(run.id, retrieval_step.get("id"), "running")
            if updated_step: yield f"data: {json.dumps({'type': 'step_status', 'step': updated_step})}\n\n"
            
            try:
                # Wrap inside transient retry loop
                async def execute_retrieval():
                    return await retrieval_agent.execute(
                        step_id=retrieval_step.get("id"), project_id=str(project_id), query=message, pdf_ids=[str(p) for p in pdf_ids] if pdf_ids else None
                    )
                retrieval_artifact = None
                async for res in run_with_retry(execute_retrieval, retrieval_step.get("id")):
                    if isinstance(res, dict) and "chunks" in res:
                        retrieval_artifact = res
                    else:
                        yield res
                
                updated_step = await self.research_service.update_research_step(run.id, retrieval_step.get("id"), "complete", retrieval_artifact)
                if updated_step: yield f"data: {json.dumps({'type': 'step_status', 'step': updated_step})}\n\n"
                
                # Send structured finding bounds dynamically masking raw processes elegantly natively successfully 
                yield f"data: {json.dumps({'type': 'artifact', 'step': 'retrieval', 'content': {'retrieved_count': retrieval_artifact.get('retrieved_count', 0)}})}\n\n"
            except Exception as e:
                updated_step = await self.research_service.update_research_step(run.id, retrieval_step.get("id"), "error", {"error": str(e)})
                if updated_step: yield f"data: {json.dumps({'type': 'step_status', 'step': updated_step})}\n\n"
                yield f"data: {json.dumps({'type': 'error', 'content': f'Agent pipeline failed gracefully. Retrieval step encountered an error: {str(e)}'})}\n\n"
                return

        chunks = retrieval_artifact.get("chunks", [])
        doc_map = {}
        for c in chunks:
            doc_map.setdefault(c.get("pdf_id"), []).append(c)

        analysis_artifacts = []
        for doc_id, doc_chunks in doc_map.items():
            if not analysis_steps:
               break
            a_step = analysis_steps.pop(0)
            
            updated_step = await self.research_service.update_research_step(run.id, a_step.get("id"), "running")
            if updated_step: yield f"data: {json.dumps({'type': 'step_status', 'step': updated_step})}\n\n"
            
            try:
                # Wrap inside transient retry loop
                async def execute_analysis():
                    return await analysis_agent.execute(a_step.get("id"), str(doc_id), doc_chunks, message)
                a_artifact = None
                async for res in run_with_retry(execute_analysis, a_step.get("id")):
                    if isinstance(res, dict):
                        a_artifact = res
                    else:
                        yield res
                
                updated_step = await self.research_service.update_research_step(run.id, a_step.get("id"), "complete", a_artifact)
                if updated_step: yield f"data: {json.dumps({'type': 'step_status', 'step': updated_step})}\n\n"
                
                analysis_artifacts.append(a_artifact)
                # Mask content structurally exposing key bounds strictly isolating internals transparently inherently safely 
                yield f"data: {json.dumps({'type': 'artifact', 'step': 'analysis', 'document_id': str(doc_id), 'content': a_artifact.get('analysis', {})})}\n\n"
            except Exception as e:
                updated_step = await self.research_service.update_research_step(run.id, a_step.get("id"), "error", {"error": str(e)})
                if updated_step: yield f"data: {json.dumps({'type': 'step_status', 'step': updated_step})}\n\n"
                yield f"data: {json.dumps({'type': 'error', 'content': f'Agent pipeline failed gracefully. Analysis step encountered an error: {str(e)}'})}\n\n"
                return

        comparison_artifact = None
        if comparison_step and len(analysis_artifacts) >= 2:
            updated_step = await self.research_service.update_research_step(run.id, comparison_step.get("id"), "running")
            if updated_step: yield f"data: {json.dumps({'type': 'step_status', 'step': updated_step})}\n\n"
            
            try:
                async def execute_comparison():
                    return await comparison_agent.execute(comparison_step.get("id"), analysis_artifacts, message)
                comparison_artifact = None
                async for res in run_with_retry(execute_comparison, comparison_step.get("id")):
                    if isinstance(res, dict):
                        comparison_artifact = res
                    else:
                        yield res
                
                updated_step = await self.research_service.update_research_step(run.id, comparison_step.get("id"), "complete", comparison_artifact)
                if updated_step: yield f"data: {json.dumps({'type': 'step_status', 'step': updated_step})}\n\n"
                
                yield f"data: {json.dumps({'type': 'artifact', 'step': 'comparison', 'content': comparison_artifact.get('comparison', {})})}\n\n"
            except Exception as e:
                updated_step = await self.research_service.update_research_step(run.id, comparison_step.get("id"), "error", {"error": str(e)})
                if updated_step: yield f"data: {json.dumps({'type': 'step_status', 'step': updated_step})}\n\n"
                logger.error(f"Comparison internally lapsed natively handled carefully globally securely mapped inherently: {e}")
                yield f"data: {json.dumps({'type': 'error', 'content': f'Agent pipeline failed gracefully. Comparison step encountered an error: {str(e)}'})}\n\n"
                return
                
        verification_artifact = None
        if comparison_artifact:
            v_step_id = verification_step.get("id") if verification_step else comparison_step.get("id")
            if verification_step:
                updated_step = await self.research_service.update_research_step(run.id, v_step_id, "running")
                if updated_step: yield f"data: {json.dumps({'type': 'step_status', 'step': updated_step})}\n\n"
            
            try:
                async def execute_verification():
                    return await verification_agent.execute(v_step_id, comparison_artifact, chunks)
                verification_artifact = None
                async for res in run_with_retry(execute_verification, v_step_id):
                    if isinstance(res, dict):
                        verification_artifact = res
                    else:
                        yield res
                
                if verification_step:
                    updated_step = await self.research_service.update_research_step(run.id, v_step_id, "complete", verification_artifact)
                    if updated_step: yield f"data: {json.dumps({'type': 'step_status', 'step': updated_step})}\n\n"
                    
                yield f"data: {json.dumps({'type': 'artifact', 'step': 'verification', 'content': {'supported_count': verification_artifact.get('supported_count', 0), 'unsupported_count': verification_artifact.get('unsupported_count', 0)}})}\n\n"
            except Exception as e:
                if verification_step:
                    updated_step = await self.research_service.update_research_step(run.id, v_step_id, "error", {"error": str(e)})
                    if updated_step: yield f"data: {json.dumps({'type': 'step_status', 'step': updated_step})}\n\n"
                yield f"data: {json.dumps({'type': 'error', 'content': f'Agent pipeline failed gracefully. Verification step encountered an error: {str(e)}'})}\n\n"
                return

        full_synthesis = ""
        if synthesis_step:
            updated_step = await self.research_service.update_research_step(run.id, synthesis_step.get("id"), "running")
            if updated_step: yield f"data: {json.dumps({'type': 'step_status', 'step': updated_step})}\n\n"
            
            yield f"data: {json.dumps({'type': 'token', 'content': '\n\n**Final Verified Synthesis:**\n\n'})}\n\n"

            v_artifact = verification_artifact or {"verified_claims": []}
            
            async for chunk in synthesis_agent.execute_stream(synthesis_step.get("id"), v_artifact, message):
                full_synthesis += chunk
                yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
                await asyncio.sleep(0.01)
                
            updated_step = await self.research_service.update_research_step(run.id, synthesis_step.get("id"), "complete")
            if updated_step: yield f"data: {json.dumps({'type': 'step_status', 'step': updated_step})}\n\n"

        yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"
        
        full_text = plan_text + "\n\n**Final Verified Synthesis:**\n\n" + full_synthesis
        await self.chat_service.add_message(session_id, "user", message)
        
        # Persist the final SSE payloads securely inside the unified structured history explicitly maintaining sources safely cleanly.
        sources_payload = []
        for c in chunks:
            sources_payload.append({
                "pdf_id": c["pdf_id"],
                "filename": c["filename"],
                "page": c["page_number"],
                "text": c["text"],
                "score": c.get("score")
            })
            
        await self.chat_service.add_message(session_id, "assistant", full_text, sources_payload)

    async def stream_chat(self, user_id: UUID, session_id: UUID, project_id: UUID, message: str, pdf_ids: List[UUID] = None) -> AsyncGenerator[str, None]:

        
        # Verify strict local bounds implicitly bypassing isolated configurations cleanly parsing native execution seamlessly 
        session, db_messages = await self.chat_service.get_session_details(session_id, user_id)
        if session.project_id != project_id:
            logger.error("Security Vault Alert: Execution parameters crossing disconnected logical project contexts robustly caught.")
            yield f"data: {json.dumps({'type': 'error', 'content': 'System constraints explicitly failed execution boundaries (Project ID mismatch).'})}\n\n"
            return

        classification = await self._classify_query(message)
        if classification == "COMPLEX":
            async for chunk in self._execute_complex_research(user_id, session_id, project_id, message, pdf_ids):
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
