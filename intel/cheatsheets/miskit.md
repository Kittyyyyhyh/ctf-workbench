---
type: cheatsheet
domain: forensics
tags: [miskit, misc, crc, usb, stego, 脚本]
source: 原创
date: 2026-09-27
---

# miskit 速查（ctf-forensics 镜像内置 /opt/miskit）

杂项攻击一条命令。泛化自 Des-CTF-Knowledge 的脚本模板（思路来源，MIT），
输入全部参数化，结果可直接用。

## 命令

```bash
miskit crc 0x1b2ee359 0x2c1a3d4f --len 3 --charset abcdefghijklmnopqrstuvwxyz
    # 已知若干小文件 CRC32，爆原内容（默认长度 1-4，默认字符集字母数字+{}_-）
miskit pngfix broken.png [--max 1024]
    # 图片尺寸被改导致打不开：按 IHDR CRC 爆真实宽高并输出 <file>.fixed.png
miskit usbkey reports.txt
    # USB 键盘流量（tshark -e usb.capdata 导出的 HID 报文行）还原敲键内容
    #   生成报文: tshark -r x.pcap -T fields -e usb.capdata | grep -v ':00:00'
miskit ttl ttl.txt --base 128 [--mode diff|lsb]
    # TTL 隐写：diff = 每包 TTL 与基准(128 win/64 linux)之差即字符；lsb = 逐包最低位
miskit base 'ZmxhZ3s...=' [--layers 5]
    # 嵌套 base 自动识别（hex/32/58/64/64url/85），逐层剥到明文
miskit stegcrack pic.jpg wordlist.txt [--extract out]
    # steghide 密码爆破（注意：steghide 只支持 jpg/bmp/wav/au，不支持 png）
```

## 提醒

- CRC 爆破超过 4 字节基本不现实（搜索空间爆炸），长内容考虑已知明文片段。
- pngfix 一次跑不出来时，图片可能还改了 CRC 外的东西（内容压缩数据损坏），
  用 PIL 打开 `fixed.png` 确认。
- 这些命令的思路原型在外部馆藏（`intel/external/`）的脚本目录里有硬编码版本，
  参数化版以本卡为准。
