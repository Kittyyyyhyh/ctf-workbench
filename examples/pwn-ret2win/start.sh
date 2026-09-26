#!/bin/sh
# 模拟赛方环境准备：把 flag 放进容器根目录
printf %s 'ZmxhZ3tyZXQyd2luX3dhcm11cF8yMDI2fQ==' | base64 -d > /flag.txt
chmod 644 /flag.txt
