---
type: technique
domain: ai
tags: [prompt-injection, llm, agent, tool-hijack]
source: 原创
date: 2026-09-26
---

# 提示词注入基础：攻击面与防锚定思路

> AI 注入题的本质：**模型输出会进入某个执行器**（回显/工具/SQL/模板），而模型
> 无法可靠区分"指令"与"数据"。围绕这一点找攻击面，不要背 payload。

## 四类攻击面（做题先分类）

1. **提示词提取**：system prompt 里有 flag/密钥/规则。目标不是"越狱"而是让模型
   原样输出它被告知不能输出的东西。绕过方向：角色重置、编码输出、逐字复述、
   借"翻译/总结上文"之手。
2. **直接注入**：用户输入直接拼进 system/开发者消息，或过滤黑名单。绕过方向：
   编码（base64/unicode）、拆分拼接、多语言切换、伪造系统标记（`---END OF SYSTEM---`）。
3. **间接注入**：模型读取外部内容（文档/RAG/网页/邮件）——**文档的读者是模型**。
   在数据里嵌指令（HTML 注释、脚注、alt 文本、chunk 首行）。
4. **工具劫持**：模型能调工具（shell/HTTP/SQL）。让模型"自己决定"执行攻击者命令，
   或借合法参数夹带（路径穿越、模板串、SQL 拼接）。

## 排查题目的固定动作

- 读 API 面：有没有 docs 上传、history 回放、system 参数暴露？
- 看输出回显：模型输出直接给用户还是经过解析（找 `SYS-CMD:` 类协议）？
- 问一次"复述规则"试探过滤强度（被拒记下拒绝模式，换编码再试）。

## 防御侧视角（综合防御题用）

指令层级要隔离（数据永远不进 system）、输出进执行器前白名单校验、工具最小权限、
对"文档中的指令"做内容安全标记。对照表见 `defense/attack-defense-map.md`。

## 本地练手

`armory/scenarios/ai-injection`：本地 ollama + 带 SYS-CMD 工具与文档摄入的 agent，
可无成本反复试错；payload 思路库在 `armory/ai/payloads/prompt-injection.txt`。
