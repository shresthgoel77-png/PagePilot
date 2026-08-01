import subprocess
import time

def run_cmd(cmd):
    print(f"--- RUNNING: {cmd} ---")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("ERRORS:")
        print(result.stderr)
    return result.stdout

run_cmd("docker system prune -a --volumes -f")
run_cmd("docker system df")
run_cmd("docker build -t genai-backend-test .")
res = subprocess.run("docker run -d -p 8011:8000 --env-file ../.env genai-backend-test", shell=True, capture_output=True, text=True)
cid = res.stdout.strip()
print(f"Container ID: {cid}")
if cid and len(cid) == 64:
    time.sleep(7)
    run_cmd(f"docker logs {cid}")
    run_cmd(f"docker rm -f {cid}")
run_cmd("docker system prune -a --volumes -f")
run_cmd("docker system df")
