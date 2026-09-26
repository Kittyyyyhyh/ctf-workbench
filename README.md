# ctf-workbench

给 Claude Code（或任何 coding agent）的 CTF 工作台：**Docker 沙箱武器库 + 按需查阅的知识库 + 薄集成层**。

> 设计原则：**提供能力，不提供思路。** 完整设计见 [docs/DESIGN.md](docs/DESIGN.md)。

## 它解决什么

| 问题 | 方案 |
|---|---|
| CTF 工具又多又大，装宿主机互相污染 | `armory/` 按方向的 Docker 镜像，随叫随到、用完即弃 |
| 知识库要么太薄要么"喂"给 agent 污染思路 | `intel/` 纯 markdown，一张索引卡 + agent 按需检索；WP 带一句话提示，防锚定 |
| 新题型（渗透 / 应急响应 / AI 注入 / 综合防御） | 专属镜像 + 可复现靶场场景（v1）+ SOP 知识（标注"非必循"） |
| agent 不会用环境 | 零依赖 `ctf` CLI + 一份只声明资产、不规定做法的 `CLAUDE.md` |

## 快速开始

前置：Docker Desktop（WSL2 后端）、Python 3.8+、Git Bash（Windows）或任意 POSIX shell。

```bash
# 1. 环境自检
./ctf doctor          # 等价：python -m ctfcli doctor

# 2. 构建镜像（MVP 提供 base / web / pwn）
./ctf update base && ./ctf update web && ./ctf update pwn

# 国内网络可先设置镜像加速（也可写入 shell 配置）：
#   export APT_MIRROR=https://mirrors.tuna.tsinghua.edu.cn/ubuntu
#   export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
#   export GH_PROXY=https://ghproxy.net/

# 3. 起一道示例题
./ctf init ssti --type web --from examples/web-ssti

# 4. 让 CC 读仓库根目录 CLAUDE.md 开工；或手动：
./ctf exec --detach ssti bash -c "cd /ctf/attachments && sh start.sh >/tmp/svc.log 2>&1"
./ctf exec ssti curl -s http://127.0.0.1:5000/
```

## 目录结构

```
ctf-workbench/
├── CLAUDE.md            # agent 进场第一份文件：资产清单 + 工作约定（不含任何解题方法）
├── ctfcli/              # ctf CLI：零依赖 Python，python -m ctfcli / ./ctf / ctf.cmd
├── armory/              # 武器库：Dockerfile + compose（base → web/pwn/… 分层）
├── intel/               # 知识库：INDEX.md 索引卡 + techniques/cheatsheets/writeups/…
├── skills/              # agent skills：ctf-env（环境操作）、postmortem（赛后入库）
├── examples/            # 示例题模板（init --from 一键起题）
├── docs/                # 设计文档、CLI 手册、intel 规范
└── workspace/           # 每道题的工作目录（gitignore，不进仓库）
```

## 路线图

- **MVP ✅**：仓库骨架 + ctf CLI + base/web/pwn 镜像 + intel 索引骨架 + 两道示例题
- **v1 ✅**：crypto/reverse/forensics/ir/ai 镜像、应急响应检查单与报告模板、
  AI 注入靶场（本地 ollama）、渗透两跳内网场景、`ctf scenario` 场景管理
- **v2**：赛后飞轮实战打磨、GHCR 镜像发布、更多场景库、攻防对照表扩充

详见 [docs/DESIGN.md](docs/DESIGN.md) §8。

## 免责声明

本项目仅用于 CTF 竞赛与**授权**环境的安全测试及教育用途。所有工具均为开源软件或用户自备 license 的商业工具（后者通过挂载注入，不随仓库分发）。使用者需遵守当地法律与比赛规则。

## License

[MIT](LICENSE)
