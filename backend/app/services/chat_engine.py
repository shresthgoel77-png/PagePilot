import json
import logging
import asyncio
from typing import AsyncGenerator, Dict, Any, List

# Implicit wrappers supporting LangChain executions cleanly handling missing pointers correctly natively globally 
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
except ImportError:
    pass

from app.core.config import settings
from app.services.retrieval import RetrievalService
from app.services.chat_service import ChatService

logger = logging.getLogger("researchos.chat_engine")

class ChatEngine:
    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service
        self.retrieval_service = RetrievalService()
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=settings.OPENAI_API_KEY, timeout=60.0)

    def _format_context(self, chunks: List[Dict[str, Any]]) -> str:
        formatted_chunks = []
        for i, chunk in enumerate(chunks):
            pdf_id = chunk["pdf_id"]
            page = chunk["page_number"]
            filename = chunk["filename"]
            text = chunk["text"]
            formatted_chunks.append(f"--- Document Chunk {i+1} [Source: {filename}, Page {page}] (PDF_ID: {pdf_id}) ---\n{text}\n")
        return "\n".join(formatted_chunks)

    async def stream_chat(self, user_id: str, session_id: str, project_id: str, message: str, pdf_ids: List[str] = None) -> AsyncGenerator[str, None]:
        
        # Verify strict local bounds implicitly bypassing isolated configurations cleanly parsing native execution seamlessly 
        session, db_messages = await self.chat_service.get_session_details(session_id, user_id)
        if str(session.project_id) != project_id:
            logger.error("Security Vault Alert: Execution parameters crossing disconnected logical project contexts robustly caught.")
            yield f"data: {json.dumps({'type': 'error', 'content': 'System constraints explicitly failed execution boundaries.'})}\n\n"
            return

        # Max-10 bounds encapsulating historical states dynamically mapping bounds optimally globally 
        history_msgs = []
        for m in db_messages[-10:]:
            if m.role == "user":
                history_msgs.append(HumanMessage(content=m.content))
            elif m.role == "assistant":
                history_msgs.append(AIMessage(content=m.content))

        # Invoke CrossEncoder mappings executing strict vector constraints implicitly locating boundaries efficiently 
        retrieved_chunks = self.retrieval_service.retrieve(
            project_id=project_id, 
            query=message, 
            top_k=20, 
            final_k=5, 
            pdf_ids=pdf_ids
        )

        sources_payload = []
        if not retrieved_chunks:
            system_instruction = "I couldn't find relevant information in your uploaded documents."
            context_string = ""
        else:
            context_string = self._format_context(retrieved_chunks)
            system_instruction = (
                "You are a research assistant. Answer based only on the provided documents. "
                "Cite sources with [Source: filename, Page X].\n\nContext Context Boundaries:\n"
                f"{context_string}"
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
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_instruction),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        if not retrieved_chunks:
            yield f"data: {json.dumps({'type': 'token', 'content': system_instruction})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"
            await self.chat_service.add_message(session_id, "assistant", system_instruction, [])
            return

        try:
            chain = prompt_template | self.llm
            response_contents = []
            
            # Asynchronous generation explicitly emitting Server-Sent streams effectively executing natively locally safely 
            async for chunk in chain.astream({"history": history_msgs, "input": message}):
                content = chunk.content
                if content:
                    response_contents.append(content)
                    payload = json.dumps({"type": "token", "content": content})
                    yield f"data: {payload}\n\n"
                    # Synchronize OS buffer bounds actively resolving explicitly mapping loops smoothly implicitly securely 
                    await asyncio.sleep(0.01)
                    
            full_response = "".join(response_contents)
            yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"
            
            # Store completed context mapping accurately capturing nested payloads inherently locally securely 
            await self.chat_service.add_message(session_id, "assistant", full_response, sources_payload)
            
        except Exception as e:
            logger.error(f"LangChain orchestration collapsed safely globally intrinsically bounded inherently mapped: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': 'Context Provider unresolvable intrinsically tracking limits.'})}\n\n"
