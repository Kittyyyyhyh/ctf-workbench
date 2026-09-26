# breakfix-pipeline（Break-Fix 综合场景：溯源 → 内存马 → 修复 → 加固 → 数据恢复）

对标长城杯/CISCN 半决赛 ISW 与"综合防御"题型（参考：2026 初赛"沉默的数据管道"系列、
半决赛 AWDP patch 提交制）。四个 flag、五个任务，`down && up` 完全重置现场。

## 现场

业务 DataPipe 跑在容器内 `http://127.0.0.1:9000`（源码 `/opt/service/app.py`）。
监控报告：该主机 02:47 左右疑似失联异常，可能有外部回连。

```bash
python -m ctfcli scenario up breakfix-pipeline
python -m ctfcli scenario exec breakfix-pipeline breakfix bash
```

## 任务（按赛题形态分阶段）

| 阶段 | 任务 | 验证方式 |
|---|---|---|
| 溯源 | 从现场日志定位攻击源 IP 与登录时间，在攻击者留下的笔记旁找到 flag1 | `/var/backups/` |
| 内存马 | 服务运行时存在一条**源码里看不到**的路由（运行时注入）——找到它并取 flag2 | 对比运行时路由与静态源码 |
| 修复 | 源码里有两处缺陷：遗留的诊断后门（命令执行）、ingest 路径穿越。**修复且业务不中断** | `bash /opt/harness/submit.sh`（= AWDP 的 check+attack 双验证，通过给 flag3） |
| 加固 | 清除全部持久化后门（账号/任务/公钥/隐藏路由） | submit.sh 第 3 步 |
| 恢复 | `/var/data/ledger.json` 被篡改，依据基线恢复 | `bash /opt/harness/verify_data.sh`（给 flag4） |

修复提示：改 `/opt/service/app.py` 后用 submit 提交即可（脚本会自动重启业务），
需要业务 checker 全绿 + 攻击 PoC 全失效才算修复成功——**大刀阔斧删功能会被 checker 判负**。

## 说明

- 训练场景：`scene/plant.sh` 是布置脚本（源码即参考答案），正式练习先不读；
  `harness/` 是赛方脚本，玩家只管跑。
- 相关知识：内存马排查 `intel/techniques/defense/memory-webshell.md`；
  修复模式速查 `intel/techniques/defense/breakfix-patterns.md`。
- 收尾：`python -m ctfcli scenario down breakfix-pipeline`
