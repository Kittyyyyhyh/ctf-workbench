#!/bin/sh
# 模拟赛方部署脚本：把 flag 写进环境后启动服务
printf %s 'ZmxhZ3tzc3RpX3dhcm11cF8yMDI2fQ==' | base64 -d > /flag.txt
chmod 644 /flag.txt
exec python3 "$(dirname "$0")/app.py"
