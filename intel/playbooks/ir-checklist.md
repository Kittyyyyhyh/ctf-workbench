---
type: playbook
domain: ir
tags: [incident-response, checklist, forensics, report]
source: 原创
date: 2026-09-26
---

# 应急响应检查单

> **参考流程，非必循；与现场证据冲突时以现场为准。**
> 本清单服务于"限时排查"型赛题与真实 IR 的第一阶段；赛场按分值取舍步骤。

## 0. 固定证据（动手改配置之前）

- [ ] 记录当前时间、主机名、内核版本：`date; hostname; uname -a`
- [ ] 全量快照式收集（容器内则先 `docker cp` 出关键目录）：
      `ps auxww`、`ss -antup`、`lsof +D /tmp`（或至少 `/proc` 扫描）
- [ ] 之后每一步只读优先；需要删除/回滚的，先记录再动手

## 1. 账号与登录

- [ ] 可疑账号：`cat /etc/passwd`（重点 uid=0、新增、shell 为 /bin/bash 的）、
      `cat /etc/shadow` 时间戳
- [ ] 登录记录：`last -f /var/log/wtmp`、`lastb`（爆破）、
      `/var/log/auth.log`（或 secure）：Accepted/Failed password、useradd
- [ ] ssh 后门：`authorized_keys`（root 与所有普通用户）、`sshd_config` 改动

## 2. 持久化排查（每个位置都要看，不是抽查）

- [ ] cron：`/etc/crontab`、`/etc/cron.d/`、`/var/spool/cron/`、
      用户 crontab；注意隐藏目录里的二进制
- [ ] systemd：`systemctl list-unit-files --state=enabled`、
      `/etc/systemd/system/`、`/usr/lib/systemd/system/` 近期修改
- [ ] 启动项：`/etc/rc.local`、`/etc/profile`、`/etc/profile.d/`、`~/.bashrc`、`~/.bash_profile`
- [ ] 驱动/LKM：`lsmod`（少见模块）
- [ ] 预加载：`/etc/ld.so.preload`；别名后门：`~/.bashrc` alias
- [ ] SUID：`find / -perm -4000 -type f 2>/dev/null`（对照基线）

## 3. 进程与网络

- [ ] 异常进程：名字伪装（kworker 多实例、路径在 /tmp/.dev）、无对应二进制的、已删除但仍运行的
      `ps auxww | grep deleted`、`ls -l /proc/*/exe`
- [ ] 异常网络：对外连接 `ss -antup`（反弹端口 4444/8888 等、非常见协议）、DNS 异常
- [ ] 挖矿特征：高 CPU、`/dev/shm`、池域名
- [ ] rootkit 初筛：`chkrootkit`、`rkhunter --check`（结果人工复核）

## 4. web 层（若业务含 web）

- [ ] webshell：近期修改的脚本文件
      `find /var/www -mtime -3 -name "*.php"`；特征：eval/assert/base64_decode/反引号
- [ ] 中间件/框架已知漏洞时间线对齐（结合业务版本）
- [ ] 访问日志：POST 到可疑路径、异常 UA、大流量上行

## 5. 文件与时间线

- [ ] 全盘近期改动：`find / -mtime -3 -type f 2>/dev/null | grep -v ^/proc`（容器内注意挂载）
- [ ] 攻击者文件常见落点：/tmp、/dev/shm、/var/tmp、隐藏目录（`.开头的非常规名`）
- [ ] 操作痕迹：`~/.bash_history`（注意被 unset HISTFILE 截断的点）、`/var/log/` 其余日志
- [ ] 时间线整理：把 login → 提权 → 落文件 → 持久化 → 外连 串成表（报告核心）

## 6. 恶意样本处置

- [ ] 不删除先留存：拷贝到隔离目录并计算 `sha256sum`、`file`、`strings` 初筛
- [ ] 联网行为确认：样本外连的 C2（结合 ss/dns 日志）

## 7. 报告与处置建议

- [ ] 按模板输出：`playbooks/templates/ir-report.md`
- [ ] 处置建议区分：立即阻断（封 IP/下线）、清除（文件/账号/持久化项）、加固（改密/升级/监控）
