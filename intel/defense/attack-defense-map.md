---
type: technique
domain: defense
tags: [defense, hardening, detection, attack-defense-map]
source: 原创
date: 2026-09-26
---

# 攻防对照表（从攻击手法反推检测与加固）

> 综合防御题的考点是"给攻击手法配防御"。本表按攻击链组织，行 = 攻击手法，
> 列 = 检测思路与加固基线。做题时从题目给的手法出发反查，比从加固清单正向背快。

| 攻击手法 | 检测思路（日志/规则） | 加固基线 |
|---|---|---|
| 密码爆破 ssh/rdp | auth.log 高频 Failed → fail2ban/阈值告警 | 禁 root 密码登录、密钥认证、限源 IP |
| uid=0 隐藏账号 | /etc/passwd 审计（uid=0 非 root、与基线 diff） | 账号基线快照 + 定期 diff；禁直接 root 远程 |
| cron/systemd 持久化 | 单元文件与 crontab 的 mtime 监控、异常路径执行 | 最小权限运行、/etc/cron.d 只读、审计规则 |
| webshell | 静态特征（eval/变量函数）+ 访问日志（POST 大 body 到罕见路径） | 上传目录禁执行、WAF、代码上线 diff 审计 |
| 反弹 shell / 异常外连 | netflow/主机外连基线，非常见端口与新域名 | 出网白名单、DNS 监控、容器默认禁外网 |
| SUID 提权 | SUID 清单基线 diff（find -perm -4000） | 去除非必要 SUID、nosuid 挂载敏感分区 |
| sudo 滥用 | sudoers diff、sudo 日志关键字（ALL=(ALL) NOPASSWD） | sudo 白名单命令、日志集中 |
| 内核 rootkit | lsmod 基线 diff、/etc/ld.so.preload 存在性 | 内核模块签名、.selinux/apparmor 强制 |
| 日志清除（unset HISTFILE、log 删改） | 日志文件 inode/大小突变、journald 远端转发 | 日志远端化（不可篡改副本）、auditd |
| 供应链/依赖投毒 | lockfile diff、构建时依赖审计 | 固定版本+hash、内源代理、CI 审计 |
| AI 提示词注入 | 模型输出进入执行器前的协议校验告警 | 数据/指令隔离、工具白名单+参数校验、最小权限 |

## 做题套路

1. 题目给"已发生的手法"或"一段日志/镜像" → 在表中定位行；
2. 检测列写"告警规则怎么下"（尽量给出可直接用的伪规则/sigma 思路）；
3. 加固列写"基线怎么改"，区分**立即止血**与**长期基线**两档（分值常在这）。
