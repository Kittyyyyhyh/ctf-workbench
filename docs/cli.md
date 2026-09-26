# ctf CLI 手册

入口：`python -m ctfcli`（Git Bash 下可用根目录 `./ctf`，cmd/PowerShell 用 `ctf.cmd`）。
下文以 `ctf` 简写。环境异常先跑 `ctf doctor`。

## 概念

- **题目（challenge）** = `workspace/<题目名>/` 目录 + 一个常驻沙箱容器 `ctf-<题目名>`。
- **workspace 布局**：`attachments/`（题目附件/源码）、`exploit/`（你的脚本）、
  `notes.md`（过程记录）、`.ctf.yaml`（题目元信息，人机共读）。
- **挂载**：workspace 双向挂载到容器内 `/ctf`。宿主机写文件，容器里立即可见，反之亦然。
- **容器是消耗品**：可随意装包改环境；坏了 `ctf rm` 重建（workspace 保留）。

## 命令

### ctf init `<名>` `--type <方向>` [`--from <模板目录>`] [`--image <img>`] [`--publish HOST:CONTAINER`]

建 workspace + 启动沙箱容器。方向：`web pwn crypto reverse forensics ir ai osint misc`。

```bash
./ctf init ssti --type web --from examples/web-ssti
./ctf init pwn1 --type pwn                      # pwn 容器自动带 SYS_PTRACE + seccomp=unconfined
./ctf init web1 --type web --publish 8080:80    # 需要从宿主机/浏览器访问时
```

### ctf exec `<名>` `<命令...>`

在容器内执行命令（**主通道**）。argv 直传容器、不经过 shell；退出码透传。
stdout/stderr 实时流式返回。

```bash
./ctf exec ssti python3 /ctf/exploit/exploit.py
./ctf exec --detach ssti bash -c "cd /ctf/attachments && sh start.sh >/tmp/svc.log 2>&1"  # 后台起服务
./ctf exec ssti cat /tmp/svc.log
./ctf exec pwn1 make -C /ctf/attachments
```

注意：

- `ctf exec` 无 TTY，交互式程序（io.interactive()、gdb）请走 `ctf shell`。
- **常驻服务必须用 `--detach`**：普通 exec 退出后其子进程会被一并回收，
  `bash -c "... &"` 在这个通道下不可靠。
- Git Bash 会把 `/ctf/...`、`/tmp/...` 这类参数改写成 Windows 路径 —— CLI 会自动
  还原（MSYS 修复），无需特殊处理；`./ctf` 包装脚本还额外设置了
  `MSYS_NO_PATHCONV=1` 双保险。

### ctf shell `<名>`

交互式 bash（人类用），workdir `/ctf`。

### ctf target `<名>` `HOST:PORT`

登记远程靶机到 `.ctf.yaml` 的 `remote` 字段（保持元信息集中，脚本里只引用它）。

### ctf ps

列出所有题目：workspace / 镜像 / 容器状态 / 远程地址。

### ctf stop `<名>` / ctf rm `<名>` [`--files` `--yes`]

停容器；`rm` 删容器（workspace 默认保留，`--files --yes` 连 workspace 一起删）。

### ctf doctor

自检：python、docker cli/daemon/compose、三个镜像、`ctf-net` 网络、磁盘余量。
有 `[FAIL]` 项会给出修复命令；全部通过才能正常 `init`。

### ctf update `<方向...>` [`--no-cache`]

构建镜像（docker compose build）。MVP 提供 `base web pwn`；构建 web/pwn 前会自动先建 base。
国内加速：构建前 `export` 三个环境变量（compose 会读取）：

```bash
export APT_MIRROR=https://mirrors.tuna.tsinghua.edu.cn/ubuntu
export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
export GH_PROXY=https://ghproxy.net/          # 注意保留结尾斜杠
./ctf update web pwn
```

## 典型闭环（CC 的视角）

```bash
./ctf init chal --type web --from examples/web-ssti                                  # 1. 起题
./ctf exec --detach chal bash -c "cd /ctf/attachments && sh start.sh >/tmp/svc.log 2>&1"  # 2. 起服务
# 3. 在 workspace/chal/exploit/ 写脚本（宿主机侧，任意编辑器）
./ctf exec chal python3 /ctf/exploit/exploit.py       # 4. 执行、看输出、迭代
./ctf rm chal                                          # 5. 收尾（workspace 留档）
```

## 疑难

| 症状 | 处理 |
|---|---|
| `image 'ctf-x' not built yet` | `ctf update <方向>` |
| `docker daemon unreachable` | 启动 Docker Desktop 后重试 |
| 容器内报 `'\r'` 错误 | Windows CRLF：`ctf exec <名> bash -c "sed -i 's/\r$//' /ctf/exploit/*.py"` |
| 端口冲突 | `init` 的 `--publish` 映射到 127.0.0.1 随机高位端口 |
| 缺工具 | 容器内直接 `pip install` / `apt install`；长期缺失走 postmortem 提 Dockerfile 建议 |
| 宿主机访问容器端口 | init 时加 `--publish`；默认只建议容器内自测 |
