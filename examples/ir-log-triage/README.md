# warmup-ir（应急响应示例题，用于验证工具链闭环）

## 题面

某主机被报告异常登录。`attachments/` 里有现场导出的材料：

- `auth.log` —— 认证日志
- `history.txt` —— ops 用户的命令历史
- `cron.list` —— 排查时导出的定时任务

回答两问，flag 均在现场材料内：

1. 攻击者成功登录的**来源 IP** 与其留下的**后门持久化**（持久化条目下方有一行 base64，
   解码即 flag1）；
2. 攻击者通过 base64 传递执行的命令所写的文件路径与内容（即 flag2）。

## 环境（工具链操作，非解法提示）

```bash
python -m ctfcli init ir1 --type ir --from examples/ir-log-triage
python -m ctfcli exec ir1 bash -c "cd /ctf/attachments && grep -n 'Accepted' auth.log"
```

> 说明：本题为工作台冒烟测试题。完整排查方法论见
> `intel/playbooks/ir-checklist.md`（注意其"非必循"头注）。
