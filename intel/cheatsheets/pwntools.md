---
type: cheatsheet
domain: pwn
tags: [pwntools, python, exploit]
source: 原创
date: 2026-09-26
---

# pwntools 高频片段

> 环境变量 `PWNLIB_NOTERM=1` 已在 ctf-pwn 镜像里设置（容器内非交互执行不卡终端）。

## 打本地 / 打远程

```python
from pwn import *
context.log_level = 'info'
context.arch = 'amd64'          # 或 i386

io = process('./vuln')                          # 本地（ctf exec 时在容器内跑）
io = remote('1.2.3.4', 9999)                    # 远程（地址先用 ctf target 登记）
io = process(['./vuln'], env={'LD_PRELOAD':'./libc.so.6'})   # 换 libc 跑
```

## 打包与偏移

```python
p64(0x40123a); p32(...)                         # 打包； Flat() 可拼接
cyclic(200)                                     # 生成 pattern
cyclic_find(0x61616162)                         # 从 crash 地址回算偏移
io.sendline(cyclic(200))
```

## ELF / libc

```python
elf = ELF('./vuln')
elf.symbols['win']                              # 符号地址（no-pie 时即绝对地址）
libc = ELF('./libc.so.6')
libc.address = leaked - libc.symbols['puts']    # 泄露后定位基址
one = next(libc.search(asm('sh;ret')))          # 简易 one_gadget 替代（镜像里有真 one_gadget）
```

## ROP

```python
rop = ROP(elf)
rop.call(elf.symbols['win'])
rop.chain()
```

## 交互模板

```python
io.recvuntil(b'input> ')
io.sendline(payload)
io.interactive()          # 人用；ctf exec 非交互环境下不要以它结尾
io.recvall(timeout=2)     # 抓全部输出
```

## 调试

- `gdb.debug('./vuln', 'gdbscript')` 需要终端，容器内建议直接 `ctf exec` 里起 gdb 调。
- 换 libc：`patchelf --set-interpreter` + `--set-rpath`（镜像已装 patchelf）。
- 在线查 libc：`from pwn import libcdb; libcdb.search_by_build_id(...)`。
