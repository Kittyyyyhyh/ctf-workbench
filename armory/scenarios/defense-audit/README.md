# defense-audit（综合防御练习场景：安全审计 + 加固报告）

## 题面

`app-prod-02` 将在下周上线。你是安全工程师，入场做一次**配置审计**：
找出全部安全缺陷（每项给出证据与风险等级），输出加固报告，并为每类缺陷
写一条**检测规则**（sigma/auditd 伪规则均可）。

- 进入现场：`python -m ctfcli scenario up defense-audit`，然后
  `python -m ctfcli scenario exec defense-audit audit-scene bash`
- 现场是容器，可以任意改动验证利用性（改完 `down && up` 即恢复）

## 产出要求

报告至少覆盖：

1. **缺陷清单**：位置、证据（命令 + 输出摘录）、风险等级（高/中/低）
2. **利用性验证**：挑 2-3 项演示攻击路径（如 SUID 提权、密码破解）
3. **加固项**：每项缺陷给出可直接执行的修复命令
4. **检测规则**：每类缺陷一条（对照 `intel/defense/attack-defense-map.md`）

## 说明

- 训练场景：所有缺陷由 `plant.sh` 布置（源码即参考答案），正式练习先不读。
- 报告模板参考 `intel/playbooks/templates/ir-report.md` 的结构（可裁剪）。
- 收尾：`python -m ctfcli scenario down defense-audit`
