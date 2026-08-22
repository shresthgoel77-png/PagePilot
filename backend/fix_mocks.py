import re

path = 'scripts/test_auth_ingestion.py'
content = open(path).read()

# 1. Fix created_at missing validation for corrupt PDF duplicate exit
content = content.replace(
    'status=PDFStatus.uploaded)', 
    'status=PDFStatus.uploaded, created_at=datetime.now(timezone.utc))'
)

# 2. Inject `file_path = job.file_path` dynamically into the active mock before execution
# I'll just replace 'await worker.process_job(job)' with the patched execution sequence
for match in re.finditer(r'([ \t]+)await worker\.process_job\(job\)', content):
    indent = match.group(1)
    original = f'{indent}await worker.process_job(job)'
    replacement = f'{indent}mock_db.execute.return_value.scalar_one_or_none.return_value.file_path = job.file_path\n{indent}await worker.process_job(job)'
    content = content.replace(original, replacement)

open(path, 'w').write(content)
