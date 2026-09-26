#!/bin/bash
# 场景装料脚本：布置一批典型的配置缺陷（练习用，源码即参考答案）
set -e

# 1) sudo 全员免密
mkdir -p /etc/sudoers.d
echo 'ALL ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/011-wheel-nopasswd
chmod 440 /etc/sudoers.d/011-wheel-nopasswd

# 2) world-writable 的 cron 任务（可被任意用户篡改后以 root 执行）
cat > /etc/cron.daily/backup <<'EOF'
#!/bin/sh
tar czf /var/backups/$(date +%F).tar.gz /var/www 2>/dev/null
EOF
chmod 777 /etc/cron.daily/backup

# 3) 弱口令账号 deploy（密码 123456）
useradd -m -s /bin/bash deploy 2>/dev/null || true
usermod -p '$6$abcdef$weakhashplaceholder1234567890' deploy

# 4) /etc/passwd 全局可写
chmod 666 /etc/passwd

# 5) GTFOBin：SUID find
chmod u+s /usr/bin/find

# 6) 业务目录里的明文密钥文件，全局可读
mkdir -p /var/www/html
cat > /var/www/html/.env <<'EOF'
DB_PASSWORD=prod-db-Sup3rSecret!
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
EOF
chmod 644 /var/www/html/.env

# 7) root 家目录对所有人可读
chmod 755 /root
echo 'internal: jira token dXNlcjpwYXNz' > /root/secrets.txt
chmod 644 /root/secrets.txt

# 8) 不安全的内核参数建议文件（审计项：写了但没人看）
cat > /etc/sysctl.d/99-insecure.conf <<'EOF'
net.ipv4.conf.all.accept_redirects = 1
net.ipv4.conf.default.accept_source_route = 1
EOF

# 9) 审计与日志转发形同虚设（auditd 未安装、无远端日志）——现场自查发现
echo "[plant] misconfigurations planted at $(date)"
