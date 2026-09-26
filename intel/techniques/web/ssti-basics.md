---
type: technique
domain: web
tags: [ssti, jinja2, flask, python]
source: 原创
date: 2026-09-26
---

# SSTI 基础：检测信号与 jinja2 利用面

## 检测

注入点回显后，先区分"模板渲染"还是"纯字符串拼接"：

- `{{7*7}}` → 页面出现 `49`：jinja2/twig 类
- `${7*7}` → 出现 `49`：freemarker/mvel 类
- `<%= 7*7 %>` → ERB 类
- 出现 500/空白但语法无错：大概率注入点存在，payload 语法不对

## jinja2 常用利用面

全局对象：`config`、`request`、`g`、`session`（部分被沙箱移除时绕过思路不同）。

payload 构造套路：从字符串/元组等基础对象 `.__class__.__mro__` 爬到 `object`，
再 `__subclasses__()` 找 `subprocess.Popen` / `os._wrap_close`（读 `__globals__` 拿
`__builtins__`）。

过滤绕过方向（按过滤对象记，不要背 payload）：

- 过滤 `.`：`|attr()` 过滤器或 `[]` + `request` 对象传参
- 过滤 `_`：`request.args`/`request.headers` 拼接、`|attr("__class__")` 变体、编码
- 过滤 `[` `]`：`__getitem__`、`|list` + tuple 解包
- 盲注（无回显）：外带（DNS/HTTP 回连）、`{% for %}` 布尔侧信道

## 常见坑

- `render_template_string(用户输入)` 才是 SSTI；`render_template(固定文件)` 不是。
- flask 默认 jinja2 沙箱模式对 `config` 等有限制，但没有开真正的 SandboxedEnvironment
  时不要被"沙箱"字样误导。
- `{{ }}` 被 WAF 吃掉时，考虑 `{% if %}` 分支侧信道或模板固定文件 + 用户数据注入点的组合。

## 关联

- 示例题：`examples/web-ssti`（本仓库，用于验证工具链闭环）
