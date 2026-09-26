"""DataPipe 报文接入服务（练习场景：源码中存在两处待修复缺陷）

业务功能（check 会验证，修复时不得破坏）：
  op=ping / echo / stat / ingest(合法文件名)

缺陷（attack 会验证是否修好）：
  1) op=diag          —— 遗留的"诊断后门"，直接执行客户端命令
  2) op=ingest 的文件名未校验 —— 路径穿越，可任意写文件
"""
import json
import os

from flask import Flask, jsonify, request

BASE = "/var/data/inbox"

app = Flask(__name__)


def op_ping(p):
    return {"pong": True, "svc": "datapipe"}


def op_echo(p):
    return {"echo": str(p.get("text", ""))[:64]}


def op_stat(p):
    return {"queued": len(os.listdir(BASE)) if os.path.isdir(BASE) else 0}


def op_ingest(p):
    name = p.get("name", "record.json")
    body = str(p.get("body", ""))
    target = os.path.join(BASE, name)  # 缺陷1：name 未做 basename 白名单
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    with open(target, "w") as f:
        f.write(body)
    return {"saved": name}


def op_diag(p):
    out = os.popen(str(p.get("cmd", "id"))).read()  # 缺陷2：遗留诊断后门
    return {"diag": out[:2000]}


OPS = {"ping": op_ping, "echo": op_echo, "stat": op_stat,
       "ingest": op_ingest, "diag": op_diag}


@app.post("/api/frame")
def frame():
    req = request.get_json(force=True, silent=True) or {}
    handler = OPS.get(str(req.get("op", "")))
    if handler is None:
        return jsonify(error="unknown op"), 400
    return jsonify(handler(req.get("params") or {}))


if __name__ == "__main__":
    os.makedirs(BASE, exist_ok=True)
    app.run(host="0.0.0.0", port=9000, threaded=True)
