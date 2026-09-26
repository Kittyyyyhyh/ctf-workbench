#!/bin/bash
# 提交验证（模拟 AWDP 的 check+attack 双验证）：业务不中断 + 漏洞已修复 + 持久化已清除
# 用法: bash /opt/harness/submit.sh
set -u

echo "== [0/3] 重新部署服务（AWDP 语义：提交 patch 即重启业务） =="
pkill -f "python3 app.py" 2>/dev/null; sleep 1
(cd /opt/service && nohup python3 app.py > /var/log/datapipe.log 2>&1 &)
sleep 2

echo "== [1/3] 业务功能 checker =="
if ! bash /opt/harness/check.sh; then
  echo "submit: 业务被破坏，修复无效（AWDP 中等同 patch 被判负）"; exit 1
fi

echo "== [2/3] 攻击 PoC =="
if bash /opt/harness/attack.sh; then :; else
  echo "submit: 漏洞仍可利用"; exit 1
fi

echo "== [3/3] 持久化与运行时后门清理 =="
hyg=0
[ "$(awk -F: '$3==0' /etc/passwd | wc -l)" -le 1 ] || { echo "  存在 uid=0 后门账号"; hyg=1; }
[ ! -f /etc/cron.d/system-backup ] || { echo "  cron 持久化仍在"; hyg=1; }
[ ! -f /tmp/.sysupdate/.backup ] || { echo "  恶意二进制仍在"; hyg=1; }
grep -q backup@off /root/.ssh/authorized_keys 2>/dev/null && { echo "  ssh 后门公钥仍在"; hyg=1; }
code=$(curl -s -o /dev/null -w '%{http_code}' -m 3 'http://127.0.0.1:9000/_mnt/sync?k=m3m0ry')
[ "$code" != "200" ] || { echo "  运行时隐藏路由仍可访问（内存马未清）"; hyg=1; }
[ "$hyg" = "0" ] || { echo "submit: 现场清理不彻底"; exit 1; }

echo
echo "=============================================="
echo "  BREAKFIX PASSED —— flag3:"
cat /opt/flags/flag3_template; echo
echo "=============================================="
date > /tmp/.breakfix-passed
exit 0
