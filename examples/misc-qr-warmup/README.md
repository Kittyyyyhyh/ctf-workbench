# warmup-misc-qr（misc 示例题：验证视觉输入工作链）

## 题面

拿到一张二维码图片（`attachments/qr.png`），flag 就编码在里面。

## 双通道解法（工具链操作，非解法提示）

通道 A（CC 视觉直读）—— 宿主机侧直接 Read 图片，先人工确认图形完整性与类型；
通道 B（容器工具解码）——

```bash
python -m ctfcli init qr --type forensics --from examples/misc-qr-warmup
python -m ctfcli exec qr zbarimg --raw /ctf/attachments/qr.png
```

> 说明：本题为工作台冒烟测试题。二维码扫不出时的修复套路（尺寸篡改、定位角
> 缺损、反色、白边）见 `intel/cheatsheets/vision-workflow.md`。
