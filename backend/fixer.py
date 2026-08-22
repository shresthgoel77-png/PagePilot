import sys
import re

path = 'scripts/test_auth_ingestion.py'
content = open(path).read()

# Add a global autouse fixture that mocks EVERYTHING properly
fixture_code = """
@pytest.fixture(autouse=True)
def mock_all_db_sessions():
    with mock.patch("app.services.job_worker.AsyncSessionLocal") as m1, \\
         mock.patch("app.services.indexing_pipeline.AsyncSessionLocal", create=True) as m2:
        m1.return_value.__aenter__.return_value = mock_db
        m2.return_value.__aenter__.return_value = mock_db
        yield
"""

if "def mock_all_db_sessions" not in content:
    content = content.replace('client = TestClient(app)', 'client = TestClient(app)\n' + fixture_code)

# Remove the contextual 'with mock.patch("app.services.job_worker.AsyncSessionLocal")' from all tests!
import textwrap

for test in ['test_normal_ingestion', 'test_large_pdf_ingestion', 'test_embedding_failure_zero_vectors', 'test_ocr_and_qdrant_failure']:
    content = content.replace('    with mock.patch("app.services.job_worker.AsyncSessionLocal") as sf_mock:\n        sf_mock.return_value.__aenter__.return_value = mock_db\n', '')

content = content.replace("        with mock.patch", "    with mock.patch")
# Re-indent the subsequent lines automatically by running autopep8 or just using a safe find-replace
def unindent_block(match):
    block = match.group(0)
    lines = block.split('\n')
    unindented = [line[4:] if line.startswith('    ') else line for line in lines]
    return '\n'.join(unindented)

# Run a lazy generic replacement on the lines inside the async test functions
def fix_indent(func_name):
    global content
    idx = content.find(f"async def {func_name}")
    if idx == -1: return
    idx2 = content.find("async def test_", idx + 10)
    if idx2 == -1: idx2 = len(content)
    test_body = content[idx:idx2]
    # Remove the 4 extra spaces of indentation introduced by the removed context manager
    new_body = "\n".join([line[4:] if line.startswith("            ") else (line[4:] if line.startswith("        ") and "with mock" not in line and "job =" not in line and "c.args" not in line else line) for line in test_body.split("\n")])
    # Very manual, let's just let the test tests run!
    
open(path, 'w').write(content)
