---
type: technique
domain: forensics
tags: [pcap, protocol, replay, scapy, 流量取证]
source: 原创
date: 2026-09-26
---

# 私有协议流量取证与重放

> 赛题形态（如 2026 初赛 ghostpatch / AegisTrace）：给一段加密/私有协议的 pcap
> （+ 可能给服务端二进制），要求恢复会话材料，再对活体副本**重放攻击**拿 flag。
> 套路固定，按六步走。

## 六步流程

1. **流提取**：wireshark/tshark 跟 TCP 流，`tshark -r a.pcap -q -z conv,tcp`
   找会话；`-T fields -e tcp.payload` 导出原始字节。
2. **结构推断**：找固定头（magic/版本号）、长度域（4 字节 LE/BE）、
   序号字段；画出最小帧格式图（写进 wp，阅卷加分）。
3. **加密识别**：熵分析区分压缩/加密；固定 magic + 异或循环（找重复 key 长度）、
   RC4/ChaCha（记录密钥流前缀）、TLS 则找 keylog。
4. **密钥恢复**：优先级 = 明文内置 key（strings 二进制）＞ 可逆编码
   （base64/xor 链）＞ 协商交互（重放握手即可）＞ 弱随机（PRNG 种子可预测）。
5. **重放**：scapy 构造同结构帧打到活体副本端口；注意序号/时间戳/校验字段
   要按新会话重算——纯字节重放通常只在"服务器无状态"时可行。
6. **验证**：重放后观察响应变化（回显 flag/命令输出）。

## scapy 重放模板

```python
from scapy.all import IP, TCP, sr1, RandShort
pkt = IP(dst="127.0.0.1")/TCP(sport=RandShort(), dport=9999, flags="PA")/payload
resp = sr1(pkt, timeout=3)
```

长交互用 socket 原生写（scapy 无状态收发对多回合协议麻烦）：
先 `tshark` 读出会话字节序，用 python socket 逐帧回放并解析响应。

## 工具

- ctf-forensics 镜像：tshark、scapy、pyshark、binwalk（从固件更新包里剥协议实现）
- 服务端二进制分析：ctf-reverse 镜像（ghidra headless 找解析函数/硬编码 key）

## 关联

- 实操数据源：自己的场景 + `examples/`（可以拿 tshark 抓自己服务的流量练手）
