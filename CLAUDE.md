# CTF Workbench

CTF 比赛工作台。你在本仓库内工作，职责是辅助（或在人类要求时独立）解题。

## 资产清单

- **沙箱 CLI**：`python -m ctfcli`（下文简写 `ctf`；Git Bash 下也可用 `./ctf`）。管理按方向的 Docker 沙箱：
  - `ctf init <题目名> --type web|pwn [--from examples/<模板>]` 建题并启动沙箱容器
  - `ctf exec <题目名> <命令...>` 在容器内执行命令 —— 你的主通道：宿主机写的脚本直接在容器里跑；常驻服务用 `--detach` 起后台
  - `ctf shell <题目名>` 交互 shell（人类用）
  - `ctf target <题目名> host:port` 登记远程靶机地址
  - `ctf ps` / `ctf stop <题目名>` / `ctf rm <题目名>` 查看与收尾（workspace 保留）
  - `ctf doctor` 环境自检；`ctf update <方向>` 构建镜像
  - 完整用法见 `docs/cli.md`；环境报错先跑 `doctor`
- **armory/**：按方向的沙箱镜像定义。已覆盖 web/pwn/crypto/reverse/forensics/ir/ai/osint；
  镜像未构建时 `init` 会提示，可选 `ctf update <方向>` 本地构建或 `ctf install-images <方向>`
  拉预构建镜像。容器是消耗品：可以任意 `pip install` / `apt install`，装坏了 `rm` 重建即可。
- **intel/**：知识库（图书馆，不是课本）。`intel/INDEX.md` 是全库目录卡：需要背景资料、命令速查、历史 WP 或想找灵感时，先查目录再按需读文件。**查不查、信不信、用不用由你判断；本库是参考，不是约束。**
  - **外部馆藏**：`intel/external/`（gitignore，需先 clone，见 `intel/EXTERNAL.md`）挂有外部公开语料——找历年 WP 思路时先读其 `AI-SEARCH-INDEX.md` 索引卡，只看标题与 WP 开头段落，不要整篇读。
- **examples/**：示例题模板，`ctf init <名> --type <方向> --from examples/<模板>` 一键起题。
- **armory/scenarios/**：练手场景（应急取证 / AI 注入 / 渗透内网 / 防御审计 / Break-Fix 修复）。
  `ctf scenario list` 查看，`ctf scenario up|down|exec|logs <场景名>` 操作，题面在场景目录 README。
- **skills/**：`ctf-env`（沙箱操作细节与坑）、`postmortem`（赛后复盘入库流程）。

## 工作约定

- 每道题一个目录 `workspace/<题目名>/`：`attachments/`（题目附件）、`exploit/`（你的脚本）、`notes.md`（过程随手记，赛后复盘依赖它）。
- 解题期间只改 `workspace/` 里的东西；`intel/` 与 `armory/` 的修改走 postmortem 流程或人类确认。
- 远程靶机地址用 `ctf target` 登记，不要散落在脚本里。
- 一场比赛全部结束（或人类要求复盘）时，按 `skills/postmortem` 把 WP 与新技巧入库，并同步更新 `intel/INDEX.md`。

## 边界

- 只对题目授权范围内的靶机与服务进行测试，不把任何 payload 指向比赛平台之外的目标。
- 禁赛期或未公开赛事的内容不入库（见 `docs/intel-spec.md` 的 embargo 政策）。
