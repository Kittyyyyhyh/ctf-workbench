---
name: ctf-env
description: 操作 ctf-workbench 沙箱（ctf CLI）的细节与常见坑。当需要建题、在容器里执行命令、起本地服务、调 pwn 或排查 docker 环境问题时使用。
---

# ctf-env：沙箱操作手册

命令入口 `python -m ctfcli`（简写 `ctf`；Git Bash 可用 `./ctf`）。环境异常先跑
`ctf doctor`。完整命令参考：docs/cli.md。

## 标准循环

1. `ctf init <名> --type web|pwn [--from examples/<模板>]` → workspace + 容器
2. 宿主机在 `workspace/<名>/exploit/` 写脚本（容器内路径是 `/ctf/exploit/`）
3. `ctf exec <名> python3 /ctf/exploit/exploit.py` 执行并看输出，迭代
4. `ctf stop|rm <名>` 收尾（workspace 保留，供赛后复盘）

## exec 细节（最容易踩的坑）

- argv **直传容器，不经过 shell**：需要管道、通配符、变量展开、后台时，套一层
  `ctf exec <名> bash -c "..."`。
- 退出码透传，可用于判断成败。
- **起常驻服务必须用 `--detach`**（普通 exec 退出后子进程会被回收）：
  `ctf exec --detach <名> bash -c "cd /ctf/attachments && sh start.sh >/tmp/svc.log 2>&1"`；
  日志用 `ctf exec <名> cat /tmp/svc.log` 查看。
- Git Bash 会把 `/ctf/...`、`/tmp/...` 参数改写成 Windows 路径，CLI 已自动还原，
  无需关心；但**不要**自己给容器内路径加引号转义。
- 无 TTY：脚本里用 `process()`/`remote()`，不要以 `io.interactive()` 结尾；
  交互调试让人类走 `ctf shell`。

## pwn 题注意

- 容器已带 `SYS_PTRACE` + `seccomp=unconfined`，可直接 gdb。
- `PWNLIB_NOTERM=1` 已设置；本地 libc 匹配用 `pwnlib.libcdb` 在线查询，
  或 `patchelf --set-interpreter --set-rpath`（镜像已装）。
- 32 位环境就绪（libc6:i386）；`make` 编译题目源码用
  `ctf exec <名> make -C /ctf/attachments`。

## Windows 坑

- CRLF：容器内报 `'\r'` 相关错误时
  `ctf exec <名> bash -c "sed -i 's/\r$//' /ctf/exploit/*.py"`。
- 中文文件名正常（容器 locale 为 UTF-8）。
- 宿主机访问容器端口需 `init --publish HOST:CONTAINER`（映射到 127.0.0.1）。

## 场景（scenarios）

多容器练习场景（应急取证 / AI 注入 / 渗透内网）不走 `ctf init`，走：
`ctf scenario list | up <名> [--build] | ps | logs <名> [-f] | exec <名> <服务> <命令> | down <名>`。
场景题面在 `armory/scenarios/<名>/README.md`；场景容器不挂 workspace，
文件进出用 `scenario exec ... cat` 或 docker cp。

## 缺工具

容器内直接 `pip install` / `apt-get update && apt-get install -y`，装坏了
`ctf rm` 重建。长期缺失的工具记进 notes.md，postmortem 时提 Dockerfile 修改建议。
