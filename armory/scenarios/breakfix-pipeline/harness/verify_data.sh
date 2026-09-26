#!/bin/bash
# 数据恢复验证：ledger.json 必须与 .manifest 校验和一致
# 用法: bash /opt/harness/verify_data.sh
set -u
cur=$(sha256sum /var/data/ledger.json | awk '{print $1}')
exp=$(cat /var/data/.manifest)
if [ "$cur" = "$exp" ]; then
  echo "DATA-RESTORED —— flag4:"
  cat /opt/flags/flag4_template; echo
  exit 0
fi
echo "DATA-STILL-TAMPERED（账本数据与基线不一致，先恢复）"
exit 1
