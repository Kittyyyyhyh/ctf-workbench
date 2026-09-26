# warmup-ssti（web 示例题，用于验证工作台闭环）

## 题面

Greeting Card Service 1.0 —— 给朋友写张贺卡吧。

- 服务：沙箱容器内 `http://127.0.0.1:5000`（源码在 `attachments/`）
- flag 位于赛方环境的 `/flag.txt`

## 环境（工具链操作，非解法提示）

```bash
python -m ctfcli init ssti --type web --from examples/web-ssti
python -m ctfcli exec ssti bash -c "cd /ctf/attachments && sh start.sh >/tmp/svc.log 2>&1 &"
python -m ctfcli exec ssti curl -s 'http://127.0.0.1:5000/?name=guest'
```

> 说明：本题为工作台冒烟测试题，flag 以 base64 藏在部署脚本里 —— 这对真实比赛环境
> 意味着"flag 在容器文件系统上，源码里没有"。
