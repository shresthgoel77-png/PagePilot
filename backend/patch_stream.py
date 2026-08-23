import json
import re

file_path = 'test_prompt_7_3_chat_and_agent_real.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

bad_text = '''        # Mock stream synthesis
        async def mock_stream(*args, **kwargs):
            class Chunk:
                def __init__(self, t): self.text = t
            yield Chunk("The answer is ")
            yield Chunk("X. [Source: doc, Page 1]")'''

good_text = '''        # Mock stream synthesis
        async def mock_stream_generator(*args, **kwargs):
            class Chunk:
                def __init__(self, t): self.text = t
            yield Chunk("The answer is ")
            yield Chunk("X. [Source: doc, Page 1]")
            
        async def mock_stream(*args, **kwargs):
            return mock_stream_generator(*args, **kwargs)'''
        
if bad_text in text:
    text = text.replace(bad_text, good_text)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Patched successfully stream syntax")
else:
    print("Failed to match stream syntax")
