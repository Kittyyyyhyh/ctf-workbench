# ir-forensics（应急响应取证练习场景）

## 题面

`web-prod-01` 运维疑似失陷：监控发现服务器夜间有异常出网行为。你是应急响应人员，
进入现场排查 **入侵路径、持久化手段、攻击者行为**，并产出应急报告。

- 进入现场：`python -m ctfcli scenario up ir-forensics`，然后
  `python -m ctfcli scenario exec ir-forensics ir-scene bash`（或用 `ctf exec` 风格的
  一次性命令：`scenario exec ir-forensics ir-scene <命令>`）
- 现场容器内没有网络连接需求的出站限制；所有痕迹每次 `up` 重新布置

## 建议产出（报告要素）

排查报告至少覆盖：攻击源 IP 与时间线、恶意账号与后门、持久化机制（全部找出）、
webshell 位置与功能、攻击者操作痕迹、处置建议（哪些文件删除/哪些配置回滚）。

## 说明

- 这是训练场景：所有入侵痕迹由 `plant.sh` 布置，源码即参考答案；正式练习时先不看它。
- 完整流程参考 `intel/playbooks/ir-checklist.md`（注意其"非必循"头注）。
- 收尾：`python -m ctfcli scenario down ir-forensics`
