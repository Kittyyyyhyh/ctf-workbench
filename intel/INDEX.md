# intel 索引卡

> **用法**：这是全库唯一建议常驻上下文的目录卡。需要背景资料、命令速查或找灵感时，
> 先扫本卡，再按需读具体文件。本卡只列"**有什么**"，不含任何方法指导 ——
> 查不查、信不信、用不用，由你自行判断。
>
> 检索技巧：`grep -ri "<关键词>" intel/ --include="*.md"` 比逐个读文件快。
>
> **外部馆藏**：`intel/external/` 下挂载外部公开语料（当前：Des-CTF-Knowledge，
> 1156 篇历年 WP + 12 篇深度文章 + Payload 速查，MIT）。入口是
> [external/Des-CTF-Knowledge/AI-SEARCH-INDEX.md](external/Des-CTF-Knowledge/AI-SEARCH-INDEX.md)
> （未 clone 时先看 [EXTERNAL.md](EXTERNAL.md) 的获取命令）。使用纪律同上：先索引后正文。

## techniques/（技术笔记）

| 文件 | 方向 | 标签 | 一句话 |
|---|---|---|---|
| [techniques/web/ssti-basics.md](techniques/web/ssti-basics.md) | web | ssti, jinja2, flask | 服务端模板注入：检测信号与 jinja2 利用面速查 |
| [techniques/ai/prompt-injection-basics.md](techniques/ai/prompt-injection-basics.md) | ai | prompt-injection, llm, agent | AI 注入题的四类攻击面分类法与固定排查动作 |
| [techniques/ai/llm-tool-hardening.md](techniques/ai/llm-tool-hardening.md) | ai | llm, tool-abuse | LLM 工具滥用题三段式：根因→复现→加固 |
| [techniques/web/modern-auth-bypass.md](techniques/web/modern-auth-bypass.md) | web | oauth, jwt, rsc | 现代 auth 链审计清单：OAuth/JWT/网关签名/RSC 逐项过 |
| [techniques/forensics/protocol-replay.md](techniques/forensics/protocol-replay.md) | forensics | pcap, scapy | 私有协议流量取证与重放六步流程 |
| [techniques/defense/memory-webshell.md](techniques/defense/memory-webshell.md) | defense | 内存马 | 内存马形态/检测（运行时 vs 静态 diff）/清除 |
| [techniques/defense/breakfix-patterns.md](techniques/defense/breakfix-patterns.md) | defense | breakfix, awdp | 业务不中断约束下的最小修复模式与清持久化清单 |
| [techniques/pentest/pivot-tunneling.md](techniques/pentest/pivot-tunneling.md) | pentest | pivot, chisel | 内网横移四模式选型：直路由/ssh-D/chisel 反向 socks/socat |

## cheatsheets/（工具速查）

| 文件 | 工具 | 一句话 |
|---|---|---|
| [cheatsheets/pwntools.md](cheatsheets/pwntools.md) | pwntools | 本地/远程进程、打包、偏移计算等高频片段 |
| [cheatsheets/mathkit.md](cheatsheets/mathkit.md) | mathkit | RSA/格/离散对数一条命令（ctf-crypto 内置 /opt/mathkit） |
| [cheatsheets/miskit.md](cheatsheets/miskit.md) | miskit | CRC 爆破/PNG 修复/USB 流量/TTL/嵌套 base/steghide 爆破（forensics 内置） |
| [cheatsheets/pentest-kit.md](cheatsheets/pentest-kit.md) | pentest-kit | netexec/impacket/hydra/kerbrute 一行命令（pentest 攻击机内置） |
| [cheatsheets/vision-workflow.md](cheatsheets/vision-workflow.md) | 多模态+镜像 | CC 看图 vs 容器解码的分工：PDF/PNG 转换、二维码修复、频谱图 |

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

ir-forensics（应急取证）、ai-injection（AI 注入，本地 LLM）、pentest-basic（两跳内网）、
defense-audit（防御审计与加固报告）。
启动与题面：`python -m ctfcli scenario list` + 对应场景 README。

## 维护

- 新增条目：先读 `docs/intel-spec.md` 的 front-matter 规范，然后在上方对应表格加一行
  （路径 / 方向 / 标签 / 一句话）。
- CI 会校验 front-matter（`scripts/check_intel.py`），缺字段会被拦下。
