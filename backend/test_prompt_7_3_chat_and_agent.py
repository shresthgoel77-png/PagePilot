import pytest
import asyncio
import json
import uuid
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.chat_engine import ChatEngine
from app.services.execution_agents import SynthesisAgent, ComparisonAgent, VerificationAgent

# --- Test 1: SSE Streaming Token Sequences ---
@pytest.mark.asyncio
async def test_sse_streaming_delivers_tokens():
    mock_chat_service = AsyncMock()
    # Mocking standard prompt delivery
    session_id = uuid.uuid4()
    user_id = uuid.uuid4()
    project_id = uuid.uuid4()
    
    # Mock session
    mock_class = MagicMock()
    mock_class.project_id = project_id
    mock_chat_service.get_session_details.return_value = (mock_class, [])
    
    engine = ChatEngine(chat_service=mock_chat_service)
    engine._classify_query = AsyncMock(return_value="SIMPLE")
    engine._reformulate_query = AsyncMock(return_value="Ref")
    
    # Mock retrieval
    engine.retrieval_service.retrieve = MagicMock(return_value=[{"pdf_id": str(uuid.uuid4()), "filename": "x.pdf", "page_number": 1, "text": "foo"}])
    
    # Mock response streams 
    async def mock_generator():
        class Chunk:
            def __init__(self, text):
                self.text = text
        yield Chunk("Hello")
        yield Chunk(" World")
        
    engine.client.aio.models.generate_content_stream = AsyncMock(return_value=mock_generator())
    
    outputs = []
    async for chunk in engine.stream_chat(user_id, session_id, project_id, "Test"):
        outputs.append(chunk)
        
    # Ensure standard token sequences
    token_outputs = [o for o in outputs if '"type": "token"' in o]
    assert len(token_outputs) == 2
    assert "Hello" in token_outputs[0]
    assert "World" in token_outputs[1]
    
    done_outputs = [o for o in outputs if '"type": "done"' in o]
    assert len(done_outputs) == 1


# --- Test 2: Chat message and source persistence (4.3) ---
@pytest.mark.asyncio
async def test_chat_message_and_source_persistence():
    mock_chat_service = AsyncMock()
    session_id = uuid.uuid4()
    user_id = uuid.uuid4()
    project_id = uuid.uuid4()
    
    mock_class = MagicMock()
    mock_class.project_id = project_id
    mock_chat_service.get_session_details.return_value = (mock_class, [])
    
    engine = ChatEngine(chat_service=mock_chat_service)
    engine._classify_query = AsyncMock(return_value="SIMPLE")
    engine._reformulate_query = AsyncMock(return_value="Ref")
    
    doc_id = str(uuid.uuid4())
    engine.retrieval_service.retrieve = MagicMock(return_value=[{"pdf_id": doc_id, "filename": "x.pdf", "page_number": 1, "text": "foo"}])
    
    async def mock_generator():
        class Chunk:
            def __init__(self, text):
                self.text = text
        yield Chunk("Response text")
        
    engine.client.aio.models.generate_content_stream = AsyncMock(return_value=mock_generator())
    
    mock_msg = MagicMock()
    mock_msg.id = uuid.uuid4()
    mock_chat_service.add_message.return_value = mock_msg
    
    async for chunk in engine.stream_chat(user_id, session_id, project_id, "Persistence test"):
        pass
        
    # Assert chat service persistence was called properly twice: once for user, once for assistant with sources
    assert mock_chat_service.add_message.call_count == 2
    add_user_call = mock_chat_service.add_message.call_args_list[0]
    add_assistant_call = mock_chat_service.add_message.call_args_list[1]
    
    assert add_user_call[0][1] == "user"
    assert add_assistant_call[0][1] == "assistant"
    # Check sources presence
    sources_payload = add_assistant_call[0][3]
    assert sources_payload[0]["pdf_id"] == doc_id


# --- Test 3: Multi-turn follow-up context resolution (5.1) ---
@pytest.mark.asyncio
async def test_multi_turn_follow_up_context_resolution():
    mock_chat_service = AsyncMock()
    engine = ChatEngine(chat_service=mock_chat_service)
    
    class MockDbMsg:
        def __init__(self, role, content):
            self.role = role
            self.content = content
            
    db_messages = [MockDbMsg("user", "Who is the CEO?"), MockDbMsg("assistant", "Tim Cook.")]
    
    class MockResponse:
        text = "Tim Cook details"
        
    with patch("asyncio.to_thread", new_callable=AsyncMock) as mocked_thread:
        mocked_thread.return_value = MockResponse()
        result = await engine._reformulate_query("And when did he join?", db_messages)
        
        # Ensures that the previous db msgs are passed down for context reformulating
        call_args = mocked_thread.call_args[1]
        assert "Who is the CEO?" in call_args["contents"]
        assert "Tim Cook" in call_args["contents"]
        assert "And when did he join?" in call_args["contents"]
        assert result == "Tim Cook details"


# --- Test 4: Document-scoped query filtering (5.2) ---
@pytest.mark.asyncio
async def test_document_scoped_query_filtering():
    mock_chat_service = AsyncMock()
    session_id = uuid.uuid4()
    user_id = uuid.uuid4()
    project_id = uuid.uuid4()
    pdf_ids = [uuid.uuid4(), uuid.uuid4()]
    
    mock_class = MagicMock()
    mock_class.project_id = project_id
    mock_chat_service.get_session_details.return_value = (mock_class, [])
    
    engine = ChatEngine(chat_service=mock_chat_service)
    engine._classify_query = AsyncMock(return_value="SIMPLE")
    engine._reformulate_query = AsyncMock(return_value="Ref")
    
    dummy_retrieve = MagicMock(return_value=[]) 
    engine.retrieval_service.retrieve = dummy_retrieve
    
    async for chunk in engine.stream_chat(user_id, session_id, project_id, "Test", pdf_ids=pdf_ids):
        pass
        
    assert dummy_retrieve.called
    kwargs = dummy_retrieve.call_args[1]
    assert "pdf_ids" in kwargs
    assert kwargs["pdf_ids"] == [str(p) for p in pdf_ids]


# --- Test 5: Decomposition produces valid step plans (6.2) ---
@pytest.mark.asyncio
async def test_agent_decomposition_produces_valid_step_plans():
    mock_chat_service = AsyncMock()
    engine = ChatEngine(chat_service=mock_chat_service)
    
    class MockResponse:
        text = '[{"type": "retrieval", "description": "some doc"}, {"type": "analysis", "description": "do analysis"}]'
        
    with patch("asyncio.to_thread", new_callable=AsyncMock) as mocked_thread:
        mocked_thread.return_value = MockResponse()
        
        result = await engine._decompose_query("complex query here")
        assert len(result) == 2
        assert result[0]["type"] == "retrieval"
        assert result[1]["type"] == "analysis"


# --- Test 6: Each agent stage executes correctly (6.3, 6.5) ---
@pytest.mark.asyncio
async def test_agent_stages_execute_entirely():
    mock_chat_service = AsyncMock()
    session_id = uuid.uuid4()
    user_id = uuid.uuid4()
    project_id = uuid.uuid4()
    
    mock_class = MagicMock()
    mock_class.project_id = project_id
    mock_chat_service.get_session_details.return_value = (mock_class, [])
    
    engine = ChatEngine(chat_service=mock_chat_service)
    engine._classify_query = AsyncMock(return_value="COMPLEX")
    engine._decompose_query = AsyncMock(return_value=[
        {"id": uuid.uuid4(), "type": "retrieval"},
        {"id": uuid.uuid4(), "type": "analysis"}
    ])
    
    # Mocking standard research step updating
    mock_run = MagicMock()
    mock_run.id = uuid.uuid4()
    engine.research_service.create_research_run = AsyncMock(return_value=mock_run)
    engine.research_service.add_research_steps = AsyncMock(return_value=[
        {"id": uuid.uuid4(), "type": "retrieval"},
        {"id": uuid.uuid4(), "type": "analysis"}
    ])
    engine.research_service.update_research_step = AsyncMock(return_value={"id": str(uuid.uuid4())})
    
    # Mock execution agents
    with patch('app.services.chat_engine.RetrievalAgent') as MockRetrievalAgent, \
         patch('app.services.chat_engine.AnalysisAgent') as MockAnalysisAgent:
         
        mock_ra = MockRetrievalAgent.return_value
        mock_aa = MockAnalysisAgent.return_value
        
        mock_ra.execute = AsyncMock(return_value={"chunks": [{"pdf_id": "1", "filename": "data.pdf", "page_number": 1, "text": "foo"}]})
        mock_aa.execute = AsyncMock(return_value={"analysis": "good"})
        
        outputs = []
        async for chunk in engine.stream_chat(user_id, session_id, project_id, "Complex Question"):
            outputs.append(chunk)
            
        assert mock_ra.execute.called
        assert mock_aa.execute.called
        # Check that proper agent steps are streamed effectively
        assert any("step_status" in o for o in outputs)
        assert any("artifact" in o and "retrieval" in o for o in outputs)


# --- Test 7: Verification correctly flags unsupported claims (6.4) ---
@pytest.mark.asyncio
async def test_verification_flags_unsupported_claims():
    agent = VerificationAgent()
    agent.research_service = AsyncMock()  # Mock this to ignore internal logging errors
    agent.evidence_verifier.verify_claims = MagicMock(return_value={
        "supported_claims": [],
        "unsupported_claims": [{"claim": "Fake claim", "reason": "Not in text"}],
        "contradictions": []
    })
    
    with patch("asyncio.to_thread", new_callable=AsyncMock) as threaded:
        threaded.return_value = [
            {"supported": False, "claim": "Fake claim", "reason": "Not in text"}
        ]
        result = await agent.execute(uuid.uuid4(), {"comparison": {}}, [{"text": "real evidence"}])
    assert result["unsupported_count"] == 1
    assert "Fake claim" in result["verified_claims"][0]["claim"]


# --- Test 8: Mid-pipeline agent failure aborts gracefully (9, 10) ---
@pytest.mark.asyncio
async def test_agent_mid_pipeline_failure_aborts_run():
    mock_chat_service = AsyncMock()
    session_id = uuid.uuid4()
    user_id = uuid.uuid4()
    project_id = uuid.uuid4()
    
    mock_class = MagicMock()
    mock_class.project_id = project_id
    mock_chat_service.get_session_details.return_value = (mock_class, [])
    
    engine = ChatEngine(chat_service=mock_chat_service)
    engine._classify_query = AsyncMock(return_value="COMPLEX")
    engine._decompose_query = AsyncMock(return_value=[
        {"id": uuid.uuid4(), "type": "retrieval"},
        {"id": uuid.uuid4(), "type": "analysis"},
        {"id": uuid.uuid4(), "type": "analysis"},
        {"id": uuid.uuid4(), "type": "comparison"},
        {"id": uuid.uuid4(), "type": "synthesis"}
    ])
    
    mock_run = MagicMock()
    mock_run.id = uuid.uuid4()
    engine.research_service.create_research_run = AsyncMock(return_value=mock_run)
    engine.research_service.add_research_steps = AsyncMock(return_value=[
        {"id": uuid.uuid4(), "type": "retrieval"},
        {"id": str(uuid.uuid4()), "type": "analysis"},
        {"id": str(uuid.uuid4()), "type": "analysis"},
        {"id": str(uuid.uuid4()), "type": "comparison"},
        {"id": str(uuid.uuid4()), "type": "synthesis"}
    ])
    engine.research_service.update_research_step = AsyncMock(return_value={"id": "status"})
    
    with patch('app.services.chat_engine.RetrievalAgent') as MockRA, \
         patch('app.services.chat_engine.AnalysisAgent') as MockAA, \
         patch('app.services.chat_engine.ComparisonAgent') as MockCA:
         
        ra = MockRA.return_value
        aa = MockAA.return_value
        ca = MockCA.return_value
        
        ra.execute = AsyncMock(return_value={"chunks": [{"pdf_id": "1"}, {"pdf_id": "2"}]})
        aa.execute = AsyncMock(return_value={"analysis": "good"})
        
        # FORCE AN EXCEPTION 
        ca.execute = AsyncMock(side_effect=Exception("Critical Mid-Pipeline Failure Native Evaluation"))
        
        outputs = []
        async for chunk in engine.stream_chat(user_id, session_id, project_id, "Fail this run"):
            outputs.append(chunk)
            
        print(outputs)
        
        # Test error state was correctly sent to SSE stream instead of proceeding silently 
        error_chunk = [o for o in outputs if '"type": "error"' in o]
        assert len(error_chunk) == 1
        assert "Agent pipeline failed gracefully. Comparison step encountered an error: Critical Mid-Pipeline Failure Native Evaluation" in error_chunk[0]
        
        # Ensure Synthesis was NEVER reached directly (synthesis step status should not fire)
        synthesis_tokens = [o for o in outputs if 'Final Verified Synthesis' in o]
        assert len(synthesis_tokens) == 0

