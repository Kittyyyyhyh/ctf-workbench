---
type: cheatsheet
domain: crypto
tags: [mathkit, rsa, lattice, dlog, script]
source: 原创
date: 2026-09-27
---

# mathkit 速查（ctf-crypto 镜像内置 /opt/mathkit）

常用数学攻击一条命令，省掉每次现写脚本。全部输入支持十进制/十六进制；
结果若可打印会同时给出 bytes。

## 命令

```bash
mathkit factor <n>                        # factordb 优先，小 n 回退 sympy（大 n 提示用 yafu）
mathkit cuberoot <c> [--k 3]              # 小指数无填充：整数 e 次方根
mathkit rsadecrypt <n> <e> <c> [p q]      # 解密；不给 p q 则问 factordb
mathkit wiener <n> <e> [c]                # d 过小（连分数）
mathkit fermat <n> [--steps N]            # p、q 相近（费马分解）
mathkit commonmod <n> <e1> <e2> <c1> <c2> # 共模攻击（gcd(e1,e2)=1）
mathkit hastad <c1,n1> <c2,n2> ...        # Håstad 广播：e 组密文，CRT+开方
mathkit dlog <g> <h> <p>                  # 离散对数（sympy，小群/光滑群）
mathkit lll matrix.json                   # LLL 格基规约（纯 python，含分数 GSO）
```

## 什么时候手写而不是用 mathkit

- 格攻击题目（隐藏数问题/背包）先 `lll` 规约基，但**目标向量的构造**要按题意来；
- Coppersmith（已知高位/小根）需要 sage —— `INSTALL_SAGE=1` 构建 ctf-crypto 后
  在 sage 里写小根脚本，mathkit 不覆盖；
- 国密：`gmalg`/`gmssl` 已装，SM2/SM3/SM4 直接 `python3 -c` 调（网鼎杯/强网杯系
  常客）。

## 溯源

脚本在仓库 `armory/crypto/mathkit/mathkit.py`；改进直接提 PR，重建镜像生效。
