# CTF Workbench 设计文档

> 给 Claude Code 的 CTF 工作台：武器库（armory）+ 知识库（intel）+ 薄集成层（cc bridge）。
> 设计原则只有一句话：**提供能力，不提供思路。**

---

## 1. 定位与设计哲学

### 1.1 这个项目是什么

一个可以开源到 GitHub 的 CTF 选手工作台，服务对象是 Claude Code（下称 CC）。它解决三个问题：

1. **工具环境问题**：CTF 工具又多又杂又大，装在宿主机上会互相污染。本项目把工具链封装进按方向的 Docker 沙箱镜像，随叫随到，用完即弃。
2. **知识供给问题**：选手（和 CC）需要技术笔记、命令速查、历史 WP。本项目维护一个纯 markdown 的本地知识库，CC 按需查阅，**不做预注入、不做 RAG 强喂**。
3. **新题型覆盖问题**：现代 CTF 除 web/pwn/crypto/re/misc 外，还有渗透、应急响应、AI 注入、综合防御等题型。本项目为它们提供专属工具链、可复现的靶场环境和流程支撑。

### 1.2 三条铁律

| 铁律 | 含义 | 落实方式 |
|---|---|---|
| 工具随叫随到 | 工具零安装、秒级可用、互不污染 | docker 镜像按方向分层，`ctf` CLI 一条命令拉起 |
| 知识按需查阅 | 知识库是图书馆不是课本，CC 自己决定查不查 | 唯一进上下文的是一张薄索引卡 `intel/INDEX.md`；WP 带"一句话提示"字段，允许只看提示不看解法，防锚定 |
| 能力清单而非流程清单 | 暴露"有什么"，不规定"怎么做" | CLAUDE.md 只写资产清单和工作约定；唯一例外是应急响应这类真有行业 SOP 的题型，流程放 playbooks 且标注"可参考，非必循" |

### 1.3 刻意不做的设计（防思路污染）

- **不上向量检索 / RAG**。被动喂检索结果 = 替 CC 做了"该看什么"的判断，会把它的注意力锚定在检索命中上。CC 的 grep/模糊搜索 + 一张好索引，效果更好且思路自主。
- **不在 CLAUDE.md 写任何解题步骤**。不出现"web 题先 fuzz 参数，再试 sqlmap"这类句子。
- **WP 库分级阅读**。每篇 WP 的 front-matter 带 `hint`（一句话技术提示）。CC 想找灵感时只读 hint 列表，读不到完整解法就不被既有解法锚定；确认需要时再读全文。

---

## 2. 总体架构

```
ctf-workbench/
├── CLAUDE.md               # CC 进场第一份文件：资产清单 + 工作约定（无任何解题指导）
├── docs/                   # 本设计文档、使用手册
├── ctfcli/                 # ctf CLI（零依赖 Python 包），CC 操作沙箱的唯一入口
│   ├── cli.py              #   全部实现（仅标准库）
│   └── __main__.py         #   python -m ctfcli
├── ctf, ctf.cmd            # 仓库根可执行包装（Git Bash / cmd）
├── examples/               # 示例题模板（ctf init --from 一键起题）
├── armory/                 # 武器库：所有 Dockerfile 与镜像定义
│   ├── base/               #   底座镜像（所有方向共用）
│   ├── web/ pwn/ crypto/ reverse/ forensics/
│   ├── ir/ ai/ osint/      #   新题型镜像
│   ├── scenarios/          #   靶场环境（可攻击的多容器场景，见 §5）
│   └── docker-compose.yml  #   profile 化编排
├── intel/                  # 知识库（纯 markdown，结构见 §4）
│   ├── INDEX.md
│   ├── techniques/ cheatsheets/ writeups/ playbooks/ defense/
├── skills/                 # 给 CC 的薄 skill（能力翻译，非方法论）
├── workspace/              # 每道题一个目录（.gitignore，不进仓库）
└── .github/workflows/      # CI：Dockerfile lint、链接检查、可选每周重建
```

运行时拓扑：

```
宿主机 (Windows + Docker Desktop / WSL2)
└── CC 在仓库根目录工作
    ├── workspace/<题目>/          # 附件、exploit 脚本、笔记，双向挂载
    └── docker: ctf-net 网络
        ├── <题目>-web        ← armory-web 镜像实例（挂载 workspace）
        ├── <题目>-pwn        ← armory-pwn 镜像实例
        └── scenario-*        ← 靶场场景容器组（ir/ai/渗透 多机内网）
```

---

## 3. 武器库（armory）详细设计

### 3.1 镜像分层体系

三层构建，控制体积与构建时间：

```
armory/base  (~800MB)
  ubuntu LTS + python3/pip + git/curl/wget/zip + file/xxd/binwalk 基础件
  + 通用 python 库 (requests, pwntools-lite 依赖等)
  └── 按方向继承：
       web       (~2.5GB)  sqlmap ffuf nuclei dirsearch gobuster httpx 装 Burp CLI 生态
                           各语言反序列化 gadget 库、phantomjs/headless chrome、tls 客户端
       pwn       (~3GB)    pwntools gdb+pwndbg+gef one_gadget ROPgadget seccomp-tools
                           libc-database 索引、patchelf、qemu-user、musl/glibc 多版本运行时
       crypto    (~2.5GB)  sagemath(独立层，最大件) yafu RsaCtfTool hashcat
                           格密码/LPN 工具、各种数论库
       reverse   (~3GB)    ghidra(+headless) radare2/rizin binary ninja CLI(若有lic)
                           unicorn frida android sdk-tools apktool jeb(本机注入,见3.4)
       forensics (~2.5GB)  volatility3 binwalk zsteg stegsolve tshark autopsy-cli
                           exiftool outguess steghide erofs/squashfs 工具
       ir        (~1.5GB)  日志分析套件(lnav/goaccess/jq) chkrootkit rkhunter lynis
                           RegRipper3.0、evtx_dump、sigma-cli、windows 取证 cli
       ai        (~1.2GB)  LLM 攻击工具链(openai/anthropic sdk)、tesseract OCR、
                           prompt 注入 payload 集；ollama 运行时不进镜像（见 §9）
       osint     (~1GB)    sherlock maigret dork 工具、exif/图片定位辅助、爬虫工具链
```

体积预算：全家桶约 20GB。构建采用 `docker build` 按方向独立 tag，**比赛期间只构建/拉取需要的方向**。base 层缓存共享，新增一个方向镜像的边际成本约 1-3GB + 10 分钟。

### 3.2 `ctf` CLI —— CC 的唯一入口

Python 实现，**仅依赖标准库**（argparse）——满足"新 clone 零安装即可用"的验收标准：
`python -m ctfcli`（Git Bash 可用根目录 `./ctf`，cmd 用 `ctf.cmd`）。命令集：

```
ctf init <题目名> --type web|pwn|crypto|re|forensics|ir|ai|osint|misc
      # workspace/<题目>/ 建目录(attachments/ exploit/ notes.md)
      # 起对应容器，workspace 双向挂载到 /ctf，登记题目元信息到 .ctf.yaml
ctf exec <题目名> <命令...>     # 容器内执行，stdout/stderr 回传给 CC
ctf shell <题目名>              # 交互 shell（人类用；CC 走 exec）
ctf debug <题目名>              # pwn 专用：容器内起 gdbserver，宿主 gdb remote
ctf serve <题目名> [port]       # 把 attachments 用 http 起来，模拟远程下载/回连
ctf target <题目名> <host:port> # 登记远程靶机地址，写入 .ctf.yaml
ctf stop|rm <题目名>            # 收尾；容器即弃即扔
ctf ps                          # 当前题目/容器状态一览
ctf tool <方向> <工具名> [args] # 一次性调用：起临时容器跑单个工具后销毁
ctf doctor                      # 自检：docker 可用性、镜像齐缺、版本、网络
ctf update [方向]               # 重建指定镜像（base 缓存加速）
ctf scenario list|up|down|ps|logs|exec   # 练手场景编排（armory/scenarios/*）
```

设计要点：

- **`ctf exec` 是 CC 的主通道**：CC 在宿主机写 `exploit.py`，`ctf exec pwn1 python3 exploit.py` 执行，输出直接回到 CC 的 Bash 工具结果里。调试循环不离开 CC 的原生工作流。
- **`.ctf.yaml` 是题目状态机**：类型、容器 id、远程靶机、本地服务端口。CC 可读，人也可读。
- **`ctf tool` 满足长尾需求**：80% 的操作走常驻题目容器，20% 的奇形怪状工具走一次性容器，互不影响。
- **缺工具现场装**：CLAUDE.md 明确授权 CC 在容器内 `pip install / apt install`——容器即弃即扔，装坏了 `ctf rm` 重建即可，宿主机永远干净。这是"不限制 CC"在武器层的体现。

### 3.3 网络设计

- 默认自建 bridge 网络 `ctf-net`，题目容器互通、可出网（连比赛远程靶机）。
- 靶场场景（§5）使用 `ctf-net-internal` 无出网段，模拟内网横移时防止误触真实主机。
- 端口约定：题目本地服务统一映射 `127.0.0.1:32768+`，避免占用常用端口。

### 3.4 商业工具的处理（合规）

IDA Pro、Burp Pro、JEB 等有 license 的工具**不进镜像、不进仓库**。约定挂载注入机制：用户本机安装后，`ctf init` 自动探测可选的本地工具目录并只读挂载进容器。仓库里只留"探测与挂载"逻辑，不含任何二进制。README 明确声明本项目只分发自带 license 的开源工具。

### 3.5 Windows 适配要点（本机环境：win32 + Git Bash）

- 依赖 Docker Desktop（WSL2 后端）。重活全在容器里，宿主 NTFS 的 IO 劣势影响很小；若追求极致，workspace 可放 WSL 文件系统内、仓库用符号链接（`ctf doctor` 会检测并建议）。
- `ctf` CLI 用 Python 而非 bash/bat，规避 Git Bash 的路径转换与引号坑。
- 仓库加 `.gitattributes` 强制 `* text=auto eol=lf`，防止 Windows 检出 CRLF 弄坏脚本与 Dockerfile。
- 附件/题目名允许中文，容器内统一 UTF-8 locale（在 base 镜像里固化）。

---

## 4. 知识库（intel）详细设计

### 4.1 目录结构与内容边界

```
intel/
├── INDEX.md              # 全库唯一强制入口：一张"有什么"的目录卡（≤200 行）
├── techniques/           # 技术笔记，按方向分子目录 web/ pwn/ crypto/ re/
│   │                     #   forensics/ ir/ ai/ defense/ …
├── cheatsheets/          # 一工具一卡：适用场景、常用命令组合、坑
├── writeups/             # WP 库：<赛事>/<年份>/<方向>/…（含 self/ 子目录=本人战史）
├── playbooks/            # ⚠️ 仅限真有行业 SOP 的机械流程：应急响应检查单、
│   │                     #   取证时间线规范、报告模板。每个文件头部标注：
│   │                     #   "参考流程，非必循；与现场证据冲突时以现场为准。"
└── defense/              # 综合防御：加固基线、sigma/yara 规则、攻防对照表
```

### 4.2 文件规范（front-matter）

所有 intel 文件带 YAML front-matter，让 CC 能 grep 元数据而不必读正文：

```yaml
---
type: technique | writeup | cheatsheet | playbook
domain: web | pwn | crypto | re | forensics | ir | ai | osint | defense
tags: [sqli, deserialization]
source: 原创 | 转载(含 url 与授权说明)
date: 2026-09-26
hint: "用伪协议绕过 include 的 include 截断"   # writeup 专用：一句话技术提示
---
```

`INDEX.md` 只列 type/domain/tags/文件路径/hint，**不含正文**。CC 的工作流是：查索引 → 决定是否读某文件 → 自己判断信不信。全程是 CC 主动拉取，不是被推送。

### 4.3 赛后飞轮（知识库自我生长）

每场比赛结束跑一次 `skill-postmortem`（§6）：

1. CC 汇总 workspace 里每道题的 notes.md 与过程文件；
2. 产出三样东西写入 intel：该题 WP（front-matter 齐全）、新 trick 的 cheatsheet 卡、INDEX.md 追加条目；
3. 若发现武器库缺工具 → 提 PR 式的 Dockerfile 修改建议（人审核后合并）。

这个飞轮是本项目长期最大的价值：打得越多，索引越厚，但 CC 每次进场时上下文成本恒定（永远只是一张索引卡）。

### 4.4 合规边界

- 公开仓库只含：本人原创笔记、明确授权转载的 WP、公开课程/文档的整理与引用（注明出处）。
- 比赛在禁赛期内的 WP 不入库（front-matter 加 `embargo: true`，CI 检查拦截）。

---

## 5. 新题型支持设计

### 5.1 渗透题型 —— scenario 靶场

`armory/scenarios/` 提供可复现的多机场景（docker-compose 定义，人也不心疼炸掉重来）：

- `scenarios/pentest-basic/`：攻击机 + DMZ web 机 + 内网机（双网卡、无出网），内置已知漏洞链与 flag 播放器；
- 攻击机角色直接复用 `armory-web/osint` 镜像加挂载实现，不另建镜像；
- 场景由 `ctf init lab-pentest --scenario pentest-basic` 一键拉起，`ctf ps` 可看网络拓扑。

### 5.2 应急响应题型

- 工具：`armory-ir`（§3.1）；
- 流程：`intel/playbooks/ir-checklist.md`（初始访问排查、持久化排查、横向痕迹、时间线整理、报告要素）——这是全库唯一带"步骤"性质的内容，头注声明"参考，非必循"；
- 场景：`scenarios/ir-forensics/`——预置被入侵痕迹的镜像（脏 crontab、异常进程、恶意样本、被篡改的 webshell）+ 一份被切割的日志卷，供平时练习；
- 报告产出：题目要求的应急报告模板放 `playbooks/templates/`，CC 填内容是其强项。

### 5.3 AI 注入题型

- 场景：`scenarios/ai-injection/`——ollama 小模型 + 简单 agent 应用（带工具调用、带 RAG、带 system prompt 防护），复刻典型赛题形态；
- 工具：`armory-ai` 内置 prompt 变异、编码绕过、间接注入 payload 构造脚本；
- 关键设计：**本地模型**让 CC 可以无成本反复试错，不受线上次数限制；笔记沉淀到 `techniques/ai/`。

### 5.4 综合防御题型

- `intel/defense/`：加固基线（CIS 摘要）、检测规则库（sigma/yara/suricata 常用规则）、**攻防对照表**（每种攻击手法对应的检测与加固点）——防御题考的是从攻击视角反推防御，这张表是最贴合的知识形态；
- 工具：forensics 镜像 + ir 镜像复用，另补 suricata/auditd 本地起环境的能力。

---

## 6. Claude Code 集成层

### 6.1 CLAUDE.md（定稿模板）

```markdown
# CTF Workbench

本仓库是 CTF 比赛工作台。你（CC）在本仓库内工作。

## 资产清单
- `ctf` CLI：沙箱管理。`ctf init --type <方向>` 建题、`ctf exec` 容器内执行、
  `ctf doctor` 自检。详见 `docs/cli.md`。
- `armory/`：各方向 docker 镜像定义。常用镜像已构建；缺的方向先 `ctf update <方向>`。
- `intel/`：知识库。`intel/INDEX.md` 是全库目录。当你需要背景资料、命令速查、
  历史 WP 或想找灵感时，先查索引，再按需读文件。**查不查、信不信、用不用由你
  自行判断；本库是参考而非约束。**
- `skills/`：ctf-env（环境操作）、postmortem（赛后复盘入库）。

## 工作约定
- 每道题目录 = `workspace/<题目名>/`：attachments/ exploit/ notes.md（随手记过程）。
- 容器是消耗品：可以任意 pip/apt install；坏了 `ctf rm` 重建。
- 比赛结束时运行 postmortem 流程，把 WP 与新技巧入库。

## 边界
- 只对题目授权范围内的靶机/服务进行测试。
- 不将任何 payload 指向比赛平台之外的目标。
```

注意：全文没有任何一句"应该怎么解题"。

### 6.2 skills（能力翻译，不做方法论）

| skill | 内容 | 行数预算 |
|---|---|---|
| `ctf-env` | ctf CLI 命令详解、容器内目录约定、常见故障（端口冲突/挂载失败）处理 | ≤80 行 |
| `postmortem` | 赛后流程：读 workspace → 产出 WP/cheatsheet/INDEX 更新 → armory 缺工具建议 | ≤100 行 |

每个 skill 头部同样声明："本 skill 描述工具用法，不规定解题方法。"

### 6.3 可选进阶（v2 再考虑）

- hook：`PostToolUse` 拦截 `ctf exec` 的输出自动摘要进 notes.md（防止长输出淹没上下文）；
- MCP server：把 ctf CLI 暴露为 MCP 工具（收益有限，CLI 已经足够好使，暂缓）。

---

## 7. 仓库形态与开源策略

| 内容 | 仓库 |
|---|---|
| 框架、ctf CLI、Dockerfile、compose、skills、INDEX 结构、文档 | 公开仓库 `ctf-workbench` |
| 本人 WP、私有笔记 | `intel/writeups/self/` 用 git submodule 指向私有仓库（或本地 .gitignore） |

其他：

- `workspace/`、镜像缓存 `.ctf/` 全部 gitignore；
- CI（GitHub Actions）：hadolint + shellcheck + markdown lint + intel 链接检查 + `embargo: true` 泄漏检查；镜像构建不在 CI 做（runner 磁盘/时长不够），仅本地构建并推送 GHCR 可选；
- README 顶部放免责声明：仅用于 CTF 与授权测试教育用途。

---

## 8. 实施路线图

### MVP（先跑通闭环，预计 2 个工作日）

- [ ] 仓库骨架 + CLAUDE.md 定稿 + .gitattributes/.gitignore
- [ ] `armory/base` + `armory/web` + `armory/pwn` 三个 Dockerfile
- [ ] `ctf` CLI：init / exec / shell / stop / rm / doctor（先够用）
- [ ] intel/INDEX.md 骨架 + front-matter 规范文档
- [ ] 一道示例题（本地 web + 本地 pwn 各一）全流程验证：init → 写 exploit → exec → flag

**MVP 验收标准**：CC 在全新 clone 的仓库里，不借助任何人工解释，仅凭 CLAUDE.md 与 ctf --help，能独立完成示例题。

### v1（第一场实战前）

- [ ] crypto / reverse / forensics 镜像
- [ ] ir / ai 镜像 + ir-checklist + ai-injection 场景
- [ ] skills：ctf-env、postmortem
- [ ] docs/cli.md、docs/usage.md 完整手册

### v2（实战迭代后）

- [x] GHCR 镜像发布（.github/workflows/publish.yml + `ctf install-images`）
- [x] osint 镜像、defense-audit 防御审计场景
- [ ] pentest 多机场景扩展、defense 知识补全
- [ ] hook 自动笔记、更多场景库

---

## 9. 关键取舍记录（为什么这样设计）

| 决策 | 备选 | 选择理由 |
|---|---|---|
| 知识库不搞 RAG | 向量库+检索注入 | 检索即预判断，会锚定 CC 思路；grep + 好索引让 CC 自主 |
| WP 带 hint 字段 | 全文直读 | 防止被既有解法锚定；先看提示找灵感，确认需要再读全文 |
| 多镜像按方向 | 单一全家桶镜像 | 比赛时按需构建，边际成本低；单镜像 20GB+ 拉取/重建都慢 |
| CLI 用 Python | bash/bat/make | Windows Git Bash 兼容性；未来可打包 pipx 分发 |
| 商业工具挂载注入 | 塞进镜像 | 合规；IDA/Burp Pro 不能进公开仓库 |
| 知识库纯 markdown | 数据库/Notion API | CC 原生可读可写可 grep；赛后飞轮就是 git commit，零依赖 |
| playbooks 例外放流程 | 一律不放流程 | 应急响应/取证真有行业 SOP，不放才是缺陷；头注声明"非必循" |
| CLI 零依赖 argparse | click + pipx 安装 | 验收标准要求全新 clone 零安装即可用；pipx 安装是额外一步且可能踩环境 |
| ollama 进场景不进镜像 | 烘焙进 ai 镜像 | 模型本质是运行时拉取的大文件，烘焙无意义；scenarios/ai-injection 用独立 ollama 服务按需拉取 |
| 商业工具挂载注入 | 塞进镜像 | 合规；IDA/Burp Pro 不能进公开仓库 |
