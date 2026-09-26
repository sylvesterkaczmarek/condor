import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

source = Path(os.environ["SOURCE"])
logs = Path(os.environ["LOGS"])
logs.mkdir(parents=True, exist_ok=True)


def suite(name):
    report = logs / (name + ".xml")
    process = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--junitxml=" + str(report)],
        cwd=source, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    (logs / (name + ".log")).write_text(process.stdout)
    print(name, process.stdout[-1800:], flush=True)
    assert process.returncode == 1, process.stdout
    failures = {}
    for test in ET.parse(report).getroot().iter("testcase"):
        failure = test.find("failure")
        if failure is not None:
            failures[(test.get("classname"), test.get("name"))] = failure.get("message")
    return failures


fixed = suite("python39-full-with-fix")
files = ["src/condor/fields.py", "tests/test_fields.py"]
saved = {name: (source / name).read_bytes() for name in files}
try:
    for name in files:
        (source / name).write_bytes(subprocess.check_output(
            ["git", "show", os.environ["BASE"] + ":" + name], cwd=source))
    baseline = suite("python39-full-upstream")
finally:
    for name, data in saved.items():
        (source / name).write_bytes(data)
assert fixed == baseline, (fixed, baseline)
assert len(baseline) == 8, baseline
assert all("zip() takes no keyword arguments" in message for message in baseline.values()), baseline
print("Python 3.9 has the same eight pre-existing trajectory failures on upstream and this contribution.")
process = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "tests/test_fields.py"],
    cwd=source, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
)
(logs / "python39-new-and-existing-field-tests.log").write_text(process.stdout)
print(process.stdout, flush=True)
assert process.returncode == 0, process.stdout
subprocess.run(["git", "diff", "--exit-code"], cwd=source, check=True)
