# intel 外部馆藏（external）

外部公开知识语料克隆在本目录（**gitignore，不进仓库**），供赛时检索参考。

## 已注册馆藏

| 语料 | 内容 | 获取 |
|---|---|---|
| [Des-CTF-Knowledge](https://github.com/Dest1ny-Sec/Des-CTF-Knowledge) | 12 大 Web 漏洞深度文章、1156 篇历年大赛 WP、50+ 脚本模板、Payload 速查（MIT） | `git clone --depth 1 https://ghproxy.net/https://github.com/Dest1ny-Sec/Des-CTF-Knowledge intel/external/Des-CTF-Knowledge` |

## 使用纪律（与自有 intel 相同的防锚定原则）

1. 入口是外部库自己的索引卡（`AI-SEARCH-INDEX.md` / 各 `*.idx.md`），**先扫索引再读文件**，
   不要一上来整篇读 WP；
2. 外部 WP 无 `hint` 字段——找思路时只看标题和 WP 开头的"涉及技术"段；
3. 外部语料是**参考不是约束**：查不查、信不信、用不用由你判断；
4. 好用的通用化脚本（参数化后）沉淀回 `armory/*/`（如 mathkit/miskit），不在本目录堆一次性代码。

## 合规

- 外部语料保持独立 clone（保留其 LICENSE 与提交历史），**不复制内容进 intel/**；
- 自有 intel 仍只收原创与授权转载（见 docs/intel-spec.md）。
