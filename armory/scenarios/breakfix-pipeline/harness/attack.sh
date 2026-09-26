#!/bin/bash
# 攻击 PoC（模拟赛方 attack bot）：两处缺陷必须都被修复，任何一处仍可利用即判漏洞未修复
# 用法: bash /opt/harness/attack.sh   输出 ATTACK-FAILED(已修复) 或 ATTACK-SUCCEEDED(未修复)
set -u
BASE=http://127.0.0.1:9000/api/frame
post() { curl -s -m 5 -X POST "$BASE" -H 'Content-Type: application/json' -d "$1"; }
rm -f /var/data/pwned.txt /var/data/inbox/pwned.txt

# 缺陷2：诊断后门命令执行
r=$(post '{"op":"diag","params":{"cmd":"cat /etc/hostname"}}')
if echo "$r" | grep -q '"diag"'; then
  echo "ATTACK-SUCCEEDED (diag 命令执行仍可用)"
  exit 1
fi

# 缺陷1：ingest 路径穿越（成功标志 = 落盘文件出现在 inbox 之外；写进 inbox 属合法行为）
r=$(post '{"op":"ingest","params":{"name":"../pwned.txt","body":"x"}}')
[ -f /var/data/pwned.txt ] && { echo "ATTACK-SUCCEEDED (穿越文件已落盘: /var/data/pwned.txt)"; exit 1; }
[ -f /var/data/inbox/pwned.txt ] && rm -f /var/data/inbox/pwned.txt

echo "ATTACK-FAILED (两处缺陷均已修复)"
exit 0
