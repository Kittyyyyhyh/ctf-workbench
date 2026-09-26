---
type: technique
domain: defense
tags: [breakfix, patch, awdp, business-continuity, incident-response]
source: 原创
date: 2026-09-26
---

# Break-Fix 修复模式速查（业务不中断约束下）

> 半决赛 ISW/AWDP 与综合防御题的核心交互：**修漏洞（attack bot 验证失效），
> 同时业务不中断（checker 验证全绿）**。删功能糊修复会被 checker 判负。

## 通用方法论

1. 先跑一遍 checker/读业务文档，列出**不可破坏的功能面**；
2. 找到漏洞入口后，选"最小修复"：收紧输入校验，而不是删除整个功能；
3. 修复后自查：checker 全绿 + 用题目给的原版 PoC（或自己写的）确认失效；
4. AWDP 提交制：patch 通常以源码 diff/so 形式提交，提交即重新部署——
   修复必须自洽（不能依赖你手工做的环境改动）。

## 高频漏洞 → 最小修复模式

| 漏洞 | ❌ 会挂 checker 的修法 | ✅ 最小修复 |
|---|---|---|
| 命令拼接 | 禁用整个"诊断/导出"功能 | 白名单参数（正则 ^[A-Za-z0-9_.-]+$）+ `subprocess` 数组形式替代 `shell=True` |
| 路径穿越 | 禁用文件上传/下载 | `os.path.basename()` + 实路径 `realpath` 前缀校验 + 扩展名白名单 |
| SQL 注入 | 关闭查询接口 | 参数化查询（占位符），保留功能 |
| 反序列化 | 换数据格式 | 白名单类（ObjectInputFilter/resolveClass 钩子） |
| 任意路由/调试接口 | 直接删路由 | 加鉴权 + 仅监听 127.0.0.1 |
| JWT/签名 | 关闭鉴权 | 修算法白名单、校验 aud/exp，密钥不走客户端 |

## 清持久化清单（修复后自查，报告里逐条给证据）

- 账号：`awk -F: '$3==0' /etc/passwd`（uid=0 只剩 root）
- 任务：`/etc/cron.*`、`/var/spool/cron/`、systemd 单元 mtime
- 公钥：所有用户 `~/.ssh/authorized_keys`
- 文件：`/tmp`、`/dev/shm` 隐藏目录、SUID 异常
- 运行时：内存马/隐藏路由（见 memory-webshell 卡）

## 关联

- 实操场景：`armory/scenarios/breakfix-pipeline`（含 check/attack/submit 双验证 harness）
- 2026 初赛综合防御题（沉默的数据管道）与半决赛 AWDP 均为此形态
