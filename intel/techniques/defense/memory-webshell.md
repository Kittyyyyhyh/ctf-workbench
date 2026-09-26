---
type: technique
domain: defense
tags: [memory-webshell, 内存马, java, python, incident-response]
source: 原创
date: 2026-09-26
---

# 内存马：形态、检测与清除

> 赛题信号：题目出现"清除内存马且不中断业务"、"服务重启即失分"时就是它。
> 本质：**恶意逻辑只活在进程内存里，静态源码/磁盘上不存在（或已删除）**。

## 常见形态

| 运行时 | 形态 | 注入路径 |
|---|---|---|
| Java | Filter / Servlet / Listener / Valve 型 | 反序列化 RCE 后反射注册到 Tomcat/Spring 容器；agent attach |
| Java | Spring Controller/Interceptor 动态注册 | AbstractUrlHandlerMapping.registerHandler |
| PHP | opcache / fastcgi 常驻 worker 内的函数表污染 | 少见，多配合 include 任意文件 |
| Python | 运行时路由注册 / monkey-patch / .pth 钩子 / import hook | 本仓库 breakfix-pipeline 场景即 .pth 形态 |
| .NET | HttpModule 动态注册 | 类似 Java Filter |

## 检测思路（核心 = 运行时与静态的 diff）

1. **路由 diff**：`app.url_map`（Flask）/ `RequestMappingHandlerMapping`（Spring）
   与源码中 `@app.route`/`@RequestMapping` 对比，多出来的就是嫌疑。
2. **类加载器 dump**（Java）：`jcmd GC.class_histogram`、
   `jmap -dump` + arthas `sc -d *Filter*` 找来源 classloader 异常的类。
3. **字节码来源追溯**：正常类来自 jar；内存马来自 `defineClass`/`Unsafe`，
   class 文件落盘路径为空。
4. **Python**：`python3 -c "import site; print(site.getsitepackages())"` 里查
   `.pth`（每个 .pth 的 import 行都会在解释器启动时执行）；检查
   `sitecustomize.py`、`usercustomize.py`。
5. **行为侧**：进程有外连但磁盘无可疑文件；访问日志中出现源码不存在的路径。

## 清除

- **Java**：kill 单个 worker/热卸载在比赛中不可靠，标准答案是"找到注入源头
  （通常是先修 RCE）→ 重启进程"。真赛题"不重启清除"要求先写反注册代码，
  报告里给结论即可。
- **Python/.pth**：删除 .pth 与对应模块 → **必须重启服务**才生效（这正是
  "运行时 vs 磁盘"差异）。
- 清除顺序：先修注入入口（RCE/反序列化），再清马，否则重启后又被注入。

## 关联

- 实操场景：`armory/scenarios/breakfix-pipeline`（.pth 运行时路由注入形态）
- 对照：初赛综合防御题（2026"沉默的数据管道"）明确包含"清除内存马"任务
