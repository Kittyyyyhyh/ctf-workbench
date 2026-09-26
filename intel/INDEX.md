# intel 索引卡

> **用法**：这是全库唯一建议常驻上下文的目录卡。需要背景资料、命令速查或找灵感时，
> 先扫本卡，再按需读具体文件。本卡只列"**有什么**"，不含任何方法指导 ——
> 查不查、信不信、用不用，由你自行判断。
>
> 检索技巧：`grep -ri "<关键词>" intel/ --include="*.md"` 比逐个读文件快。

## techniques/（技术笔记）

| 文件 | 方向 | 标签 | 一句话 |
|---|---|---|---|
| [techniques/web/ssti-basics.md](techniques/web/ssti-basics.md) | web | ssti, jinja2, flask | 服务端模板注入：检测信号与 jinja2 利用面速查 |
| [techniques/ai/prompt-injection-basics.md](techniques/ai/prompt-injection-basics.md) | ai | prompt-injection, llm, agent | AI 注入题的四类攻击面分类法与固定排查动作 |

## cheatsheets/（工具速查）

| 文件 | 工具 | 一句话 |
|---|---|---|
| [cheatsheets/pwntools.md](cheatsheets/pwntools.md) | pwntools | 本地/远程进程、打包、偏移计算等高频片段 |

## writeups/（题解库）

按 `<赛事>/<年份>/<方向>/` 组织，本人战史在 `writeups/self/`。
当前为空 —— 首场比赛后由 postmortem 流程填充（见 skills/postmortem）。
每篇 WP 的 front-matter 带 `hint` 一句话提示：**找灵感先只扫 hint，确认需要再读全文**，
避免被既有解法锚定。

## playbooks/（仅限有行业 SOP 的机械流程，头注均声明"非必循"）

| 文件 | 一句话 |
|---|---|
| [playbooks/ir-checklist.md](playbooks/ir-checklist.md) | 应急响应排查检查单：账号/持久化/进程网络/web/时间线/报告 |
| [playbooks/templates/ir-report.md](playbooks/templates/ir-report.md) | 应急响应报告模板（按节填空） |

## defense/（综合防御）

| 文件 | 一句话 |
|---|---|
| [defense/attack-defense-map.md](defense/attack-defense-map.md) | 攻防对照表：从攻击手法反查检测规则与加固基线 |

## 练手场景（配合 armory/scenarios/）

ir-forensics（应急取证）、ai-injection（AI 注入，本地 LLM）、pentest-basic（两跳内网）。
启动与题面：`python -m ctfcli scenario list` + 对应场景 README。

## 维护

- 新增条目：先读 `docs/intel-spec.md` 的 front-matter 规范，然后在上方对应表格加一行
  （路径 / 方向 / 标签 / 一句话）。
- CI 会校验 front-matter（`scripts/check_intel.py`），缺字段会被拦下。
