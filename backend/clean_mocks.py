import re

path = 'scripts/test_auth_ingestion.py'
content = open(path).read()

# Remove all bad lines injected
content = re.sub(r'[ \t]*mock_db\.execute\.return_value\.scalar_one_or_none\.return_value\.file_path = job\.file_path\n', '', content)

# Find all 'await worker.process_job(job)' and fix their indentation uniformly to match the line after it!
lines = content.split('\n')
for i in range(len(lines)):
    line = lines[i]
    if 'await worker.process_job(job)' in line:
        # Find the indentation of the NEXT non-empty line
        for j in range(i+1, len(lines)):
            if lines[j].strip():
                next_indent = len(lines[j]) - len(lines[j].lstrip())
                # Replace line i with correct indent + file_path update
                indent_str = " " * next_indent
                lines[i] = f"{indent_str}mock_db.execute.return_value.scalar_one_or_none.return_value.file_path = job.file_path\n{indent_str}await worker.process_job(job)"
                break

open(path, 'w').write('\n'.join(lines))
