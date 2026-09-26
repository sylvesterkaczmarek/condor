import os
from pathlib import Path
import subprocess
import sys

source = Path(os.environ["SOURCE"])
logs = Path(os.environ["LOGS"])
logs.mkdir(parents=True, exist_ok=True)

def run(command, name, failure=False):
    process = subprocess.run(command, cwd=source, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (logs / (name + ".log")).write_text(process.stdout)
    print(name, process.stdout[-2000:], flush=True)
    if failure:
        assert process.returncode != 0, "Original implementation unexpectedly passed"
    else:
        assert process.returncode == 0, process.stdout
    return process.stdout

run([sys.executable, "-m", "pytest", "-q"], "full-fixed")
path = source / "src/condor/fields.py"
saved = path.read_bytes()
try:
    path.write_bytes(subprocess.check_output(["git", "show", os.environ["BASE"] + ":src/condor/fields.py"], cwd=source))
    output = run([sys.executable, "-m", "pytest", "-q", "tests/test_fields.py"], "original-api", failure=True)
    assert "8 failed, 3 passed" in output, output
finally:
    path.write_bytes(saved)
run([sys.executable, "-m", "pytest", "-q"], "full-restored")
run(["ruff", "check", "src/condor/fields.py", "tests/test_fields.py"], "ruff")
run(["ruff", "format", "--check", "src/condor/fields.py", "tests/test_fields.py"], "format")
run(["git", "diff", "--exit-code"], "clean-source")
(logs / "source-commit.txt").write_text(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True))
