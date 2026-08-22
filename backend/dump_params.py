import re
import subprocess
import json

path = 'scripts/test_auth_ingestion.py'
content = open(path).read()

# Replace any print("PARAMS X DUMP") with writing to file
content = content.replace(
    'assert "PARAMS=" + str(params) == ""',
    'open("params_dump_2.json", "w").write(str(params))\n            assert any(p.get("status") == JobStatus.retry for p in params)'
)
content = content.replace(
    'print("PARAMS 1 DUMP:", params)',
    'open("params_dump_1.json", "w").write(str(params))'
)
open(path, 'w').write(content)

subprocess.run(['python', '-m', 'pytest', 'scripts/test_auth_ingestion.py::test_embedding_failure_zero_vectors', 'scripts/test_auth_ingestion.py::test_ocr_and_qdrant_failure'])

print("DUMP 1:", open("params_dump_1.json").read())
print("DUMP 2:", open("params_dump_2.json").read())
