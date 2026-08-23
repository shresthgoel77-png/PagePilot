import json
import re

file_path = 'test_prompt_7_3_chat_and_agent_real.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

old_func = re.search(r'def mock_generate_content\(\*args, \*\*kwargs\):.*?return MagicMock\(text="OK"\)', text, re.DOTALL)

if old_func:
    new_func = """    def mock_generate_content(*args, **kwargs):
        content = str(kwargs.get("contents", ""))
        config = kwargs.get("config", None)
        sys_inst = str(getattr(config, "system_instruction", "")) if config else ""
        
        combined = content + " " + sys_inst
        
        # Mocking classification
        if "Classify the following" in combined:
            return MagicMock(text="COMPLEX")
        # Mocking decomposition
        elif "expert research supervisor" in combined:
            return MagicMock(text=json.dumps([
                {"type": "retrieval", "description": "retrieve..."},
                {"type": "analysis", "description": "analyze..."},
                {"type": "analysis", "description": "analyze 2..."},
                {"type": "comparison", "description": "compare..."},
                {"type": "verification", "description": "verify..."},
                {"type": "synthesis", "description": "synthesize..."}
            ]))
        # Mocking analysis
        elif "Analysis Agent" in combined:
             return MagicMock(text=json.dumps({
                "document_id": "doc1",
                "key_findings": ["finding 1"],
                "summary": "Sum"
             }))
        # Mocking comparison
        elif "Comparison Agent" in combined:
             return MagicMock(text=json.dumps({
                "agreements": ["A1"], "contradictions": [], "synthesis_summary": "Sum"
             }))
        # Default mock
        return MagicMock(text="OK")"""
        
    text = text.replace(old_func.group(0), new_func.strip())
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Patched successfully via regex")
else:
    print("Failed to match regex")
