# intel 文件规范

知识库全部是纯 markdown。为保证 CC 能只读元数据就决定要不要读正文，所有文件（除
`INDEX.md` 与各目录 README）必须带 YAML front-matter。

## front-matter 字段

| 字段 | 必填 | 说明 |
|---|---|---|
| `type` | ✅ | `technique` / `writeup` / `cheatsheet` / `playbook` |
| `domain` | ✅ | `web` / `pwn` / `crypto` / `re` / `forensics` / `ir` / `ai` / `osint` / `defense` / `misc` |
| `date` | ✅ | `YYYY-MM-DD`（创作或最后大改日期） |
| `tags` | 建议 | 列表，检索的主要入口 |
| `source` | 建议 | `原创` 或 `转载(<url>, 授权说明)` |
| `hint` | writeup 必填 | **一句话技术提示**。作用：找灵感时只 grep 所有 hint（`grep '^hint:' intel/writeups -r`），不读全文，避免被既有解法锚定 |
| `embargo` | 特殊 | 赛事禁赛期内**根本不要提交该文件**；CI 会拦截 `embargo: true` |

## writeup 目录约定

```
writeups/<赛事>/<年份>/<方向>/<题目名>.md
writeups/self/<赛事>/<年份>/...        # 本人战史（可指向私有 submodule）
```

正文建议结构（非强制）：题面复述 → 思路演化（**含死胡同**，死胡同最有复用价值）→
最终解法 → 可复用结论。

## 为什么不上 RAG / 向量检索

检索即预判断：被动把"最相似"的内容喂给 agent，等于替它决定了"该看什么"，会把注意力
锚定在检索命中上。这里的替代机制是：

1. 一张薄索引卡（`INDEX.md`）常驻上下文，只回答"库里有什么"；
2. front-matter 让 `grep` 成为精准检索入口；
3. 何时查、查什么、信不信，全部由 agent 自己决定 —— `CLAUDE.md` 只声明"这里是参考，
   不是约束"。

## 设计红线

- `INDEX.md` 不写方法指导，只写"有什么"。
- playbook 类文件（应急响应等真有行业 SOP 的除外）不进这个库；进来的必须头部标注
  "参考流程，非必循；与现场证据冲突时以现场为准"。
- 转载内容必须有授权说明；禁赛期内容不提交（CI 强制）。
