# warmup-crypto（crypto 示例题，用于验证工具链闭环）

## 题面

截获了一段 RSA 加密流量，参数如下（`attachments/output.txt`）。
解出明文，flag 即其中内容。

```
n = 1023 位
e = 3
c = 621 位
```

## 环境（工具链操作，非解法提示）

```bash
python -m ctfcli init rsa --type crypto --from examples/crypto-rsa-warmup
python -m ctfcli exec rsa python3 -c "import gmpy2, sympy; print('crypto-ok')"
```

> 说明：本题为工作台冒烟测试题，用 ctf-crypto 镜像内的 gmpy2/sympy/RsaCtfTool
> 均可解。
