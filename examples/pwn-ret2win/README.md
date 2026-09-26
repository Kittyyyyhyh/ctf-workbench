# warmup-ret2win（pwn 示例题，用于验证工作台闭环）

## 题面

一道经典的入门栈题。源码在 `attachments/`（需要先在容器里编译），flag 位于赛方环境
的 `/flag.txt`。本题在沙箱本地运行，不连远程。

## 环境（工具链操作，非解法提示）

```bash
python -m ctfcli init ret2win --type pwn --from examples/pwn-ret2win
python -m ctfcli exec ret2win sh /ctf/attachments/start.sh     # 初始化赛方环境
python -m ctfcli exec ret2win make -C /ctf/attachments         # 编译
python -m ctfcli exec ret2win /ctf/attachments/vuln < /dev/null
```

> 说明：本题为工作台冒烟测试题，flag 以 base64 藏在 start.sh 里 —— 这对真实比赛环境
> 意味着"flag 在容器文件系统上，源码里没有"。
