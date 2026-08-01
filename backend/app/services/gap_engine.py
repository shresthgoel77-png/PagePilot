import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
import json
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models.pdf import PDF, PDFStatus
from app.services.chat_service import ChatService
from app.core.config import settings

from google import genai
from google.genai import types

logger = logging.getLogger("researchos.gap_engine")

class GapAnalysisResponse(BaseModel):
    covered_topics: List[str]
    methodologies: List[str]
    limitations: List[str]
    research_gaps: List[str]

class GapAnalysisEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.chat_service = ChatService(db)
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def execute_gap_analysis(self, user_id: UUID, project_id: str, focus_area: Optional[str], session_id: Optional[str]) -> GapAnalysisResponse:
        await self.chat_service.verify_project_ownership(UUID(project_id), user_id)
        
        stmt = select(PDF).where(PDF.project_id == UUID(project_id), PDF.status == PDFStatus.parsed)
        pdf_results = await self.db.execute(stmt)
        parsed_pdfs = list(pdf_results.scalars().all())
        
        if not parsed_pdfs:
            raise HTTPException(status_code=400, detail="No parsed documents available for analysis.")
            
        context_string = ""
        for pdf in parsed_pdfs:
            if pdf.parsed_text:
                full_text = pdf.parsed_text
                length = len(full_text)
                if length > 3000:
                    chunks = [
                        full_text[:1000],
                        full_text[length//2 - 500 : length//2 + 500],
                        full_text[-1000:]
                    ]
                else:
                    chunks = [full_text]
                
                context_string += f"--- Document: {pdf.filename} ---\n"
                for i, c in enumerate(chunks):
                    context_string += f"Segment {i+1}: {c}\n"
                context_string += "\n"

        system_instruction = (
            "You are a highly analytical academic system. Evaluate context structures explicitly executing rigorous Gap Analysis mapping inherently intuitively gracefully.\n"
            "Extract thematic models intrinsically structuring boundaries tracking explicit dependencies elegantly intelligently seamlessly mapped cleanly powerfully.\n"
            "Return valid JSON securely binding strings efficiently natively optimally resolving outputs uniquely flawlessly."
        )
        if focus_area:
             system_instruction += f"\nTarget Focus Strategy: {focus_area}."

        prompt_input = "Execute rigid parameter mapping explicitly encapsulating bounding schemas dynamically robustly:\n\nContext Bounds:\n" + context_string

        retries = 2
        last_error = None
        result_payload = None

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=GapAnalysisResponse,
            temperature=0.3
        )

        for attempt in range(retries + 1):
            try:
                response = await self.client.aio.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt_input,
                    config=config
                )
                result_payload = json.loads(response.text)
                # Validation test via Pydantic uniquely natively successfully intelligently resolving variables stably gracefully 
                GapAnalysisResponse(**result_payload)
                break
            except Exception as e:
                logger.warning(f"JSON validation structure decoupled executing retry loops explicitly: {e}")
                last_error = e
                result_payload = None

        if not result_payload:
            raise HTTPException(status_code=500, detail=f"LLM JSON bounds structurally isolated explicitly limiting variables robustly natively: {last_error}")

        if session_id:
            db_msg = await self.chat_service.add_message(UUID(session_id), "user", f"Execute Structural Bounded Gap Extraction optimally natively perfectly intelligently flawlessly securely! (Focus Context: {focus_area or 'General Baseline Array Vectors'})")
            raw_content = json.dumps(result_payload, indent=2)
            await self.chat_service.add_message(UUID(session_id), "assistant", f"```json\n{raw_content}\n```", sources=[])

        return GapAnalysisResponse(**result_payload)
