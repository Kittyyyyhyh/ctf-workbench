---
name: postmortem
description: 赛后复盘入库流程。当一场比赛结束或人类要求复盘时使用：把 WP、新技巧、缺失工具沉淀进 intel/ 与 armory/，让知识库自我生长。
---

# postmortem：赛后复盘入库

前提：`workspace/` 里的每道题有 `notes.md` 与 exploit 过程文件。
产出规范：`docs/intel-spec.md`。

## 步骤

1. **清点**：`ctf ps` + 遍历 `workspace/*/notes.md`，列出每道题 solved/unsolved 与关键思路。
2. **逐题写 WP** → `intel/writeups/<赛事>/<年份>/<方向>/<题目名>.md`：
   - front-matter 齐全；`hint` 必填（一句话技术提示，供未来的自己防锚定地扫读）；
   - 正文结构建议：题面复述 → 思路演化（**死胡同也要写**，复用价值最高）→ 最终解法 →
     可复用结论；
   - unsolved 题写"预期解学习笔记"并注明来源（赛后公开 WP 等）。
3. **新技巧沉淀**：通用化的思路 → `intel/techniques/<方向>/`；工具心得 →
   `intel/cheatsheets/<工具>.md`。
4. **更新 `intel/INDEX.md`**：每个新文件一行（路径 / 方向 / 标签 / 一句话），不写方法指导。
5. **武器库复盘**：比赛中现场装过的工具 → 对应 `armory/<方向>/Dockerfile` 的修改建议。
   只提建议，人类确认后再改。
6. **收尾**：确认 `ctf ps` 无遗留容器；提醒人类 git 提交。

## 红线

- 禁赛期 / 未公开赛事的内容一律不入库（embargo 政策见 docs/intel-spec.md）。
- 不删改历史 WP，只追加与文末勘误。
- 本 skill 是入库流程，不规定任何"以后该怎么解题"。
