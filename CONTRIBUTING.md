# Contributing to ctf-workbench

欢迎 PR。设计原则先读一遍：[docs/DESIGN.md](docs/DESIGN.md) —— 尤其是三条铁律
（工具随叫随到 / 知识按需查阅 / 能力清单而非流程清单）。

## 可以贡献什么

| 类型 | 位置 | 要求 |
|---|---|---|
| 新工具进镜像 | `armory/<方向>/Dockerfile` | 开源工具；说明用途；控制体积 |
| 新方向镜像 | `armory/<新方向>/` | 先开 issue 讨论；遵守 base 分层结构 |
| 技术笔记/cheatsheet | `intel/techniques/` `intel/cheatsheets/` | front-matter 齐全 + 登记 INDEX.md |
| 公开授权 WP | `intel/writeups/` | 必须有授权说明；`hint` 字段必填 |
| 练手场景 | `armory/scenarios/<名>/` | compose + plant 脚本 + 题面 README；可一键起停 |
| CLI 改进 | `ctfcli/cli.py` | 仅标准库；Windows Git Bash 兼容 |

## 红线（CI 会拦，但请自觉）

- 不提交任何需要 license 的商业工具二进制（IDA/Burp Pro 等，走挂载注入）。
- 不提交禁赛期/未公开赛事内容（`embargo`）。
- 不在 CLAUDE.md、INDEX.md、skills 里写"解题步骤"——这是本项目的核心设计，
  流程类内容只进 playbooks 且头注声明"非必循"。

## 本地验证

```bash
python -m py_compile ctfcli/cli.py ctfcli/__main__.py
python scripts/check_intel.py
shellcheck ctf armory/scenarios/*/plant.sh
./ctf doctor && ./ctf init <名> --type <方向>   # 改动 CLI/镜像后跑一遍闭环
```

## 提交规范

一个 PR 一件事；改动 armory 镜像请在描述里附本地构建成功的输出（`ctf update <方向>` 的末尾几行）。
