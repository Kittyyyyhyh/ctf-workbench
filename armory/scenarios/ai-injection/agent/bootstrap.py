"""等待 ollama 就绪并拉取模型，然后启动 agent 应用。"""
import json
import os
import sys
import time

import requests

BASE = os.environ.get("OLLAMA_URL", "http://ollama:11434")
MODEL = os.environ.get("MODEL", "qwen2.5:0.5b")


def wait_ollama(timeout_s=180):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            requests.get(f"{BASE}/api/version", timeout=3)
            return
        except Exception:
            time.sleep(2)
    sys.exit("[bootstrap] ollama not reachable")


def pull_model():
    print(f"[bootstrap] pulling {MODEL} (first start downloads it)...", flush=True)
    r = requests.post(f"{BASE}/api/pull", json={"name": MODEL}, stream=True, timeout=None)
    status = ""
    for line in r.iter_lines():
        if not line:
            continue
        d = json.loads(line)
        if "error" in d:
            sys.exit(f"[bootstrap] pull failed: {d['error']}")
        if d.get("status") and d["status"] != status:
            status = d["status"]
            print(f"[bootstrap] {status}", flush=True)
    print(f"[bootstrap] model {MODEL} ready", flush=True)


if __name__ == "__main__":
    wait_ollama()
    pull_model()
    os.execvp("python3", ["python3", "/app/app.py"])
