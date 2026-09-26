# Security Policy

## 范围

本仓库交付的是 CTF 练习/比赛工具链。安全问题主要涉及：

- `ctfcli` CLI 的命令注入 / 路径处理缺陷；
- Dockerfile / 场景脚本中的供应链问题（固定来源、最小安装）；
- 场景与示例中的"故意漏洞"越界到宿主机（所有场景容器均应保持隔离）。

## 报告

- 请通过 GitHub Security Advisories（Security 标签页 → Report a vulnerability）私密报告，
  不要直接开公开 issue。
- 48 小时内确认，修复随下一个 patch 版本发布。

## 使用边界（同时是免责声明）

- 本项目仅用于 CTF 竞赛与**授权**环境的安全测试及教育用途。
- 所有练手场景的"漏洞"都封在容器内；请勿将任何 payload 指向比赛/授权范围之外的目标。
- 商业工具（IDA/Burp Pro 等）不随仓库分发，由用户自备 license 通过挂载注入。
