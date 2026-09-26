#!/bin/bash
# 业务功能验证（模拟赛方 checker）：修复时不得破坏这些功能
# 用法: bash /opt/harness/check.sh   成功输出 BUSINESS-OK，失败输出 BUSINESS-BROKEN
set -u
BASE=http://127.0.0.1:9000/api/frame
fail=0

post() { curl -s -m 5 -X POST "$BASE" -H 'Content-Type: application/json' -d "$1"; }

r=$(post '{"op":"ping"}')
echo "$r" | grep -q '"pong": *true' || { echo "FAIL ping: $r"; fail=1; }

r=$(post '{"op":"echo","params":{"text":"hello-datapipe"}}')
echo "$r" | grep -q 'hello-datapipe' || { echo "FAIL echo: $r"; fail=1; }

r=$(post '{"op":"stat"}')
echo "$r" | grep -q '"queued"' || { echo "FAIL stat: $r"; fail=1; }

r=$(post '{"op":"ingest","params":{"name":"record-1.json","body":"{\"k\":1}"}}')
echo "$r" | grep -q '"saved":"record-1.json"' || { echo "FAIL ingest(合法): $r"; fail=1; }
grep -q '{"k":1}' /var/data/inbox/record-1.json 2>/dev/null || { echo "FAIL ingest 内容未落盘"; fail=1; }

[ "$fail" = "0" ] && echo "BUSINESS-OK" || echo "BUSINESS-BROKEN"
exit $fail
