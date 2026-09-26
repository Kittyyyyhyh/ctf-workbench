---
type: technique
domain: web
tags: [oauth, jwt, auth-bypass, gateway, rsc, nextjs]
source: 原创
date: 2026-09-26
---

# 现代 auth 链审计清单（OAuth / JWT / 网关签名 / RSC）

> 赛题信号（如 2026 初赛 OOOOOOOAuth、AegisCore"零信任网关"）：题目自建鉴权
> 体系（OAuth 流程、JWT、签名网关、Next.js RSC/Server Action），考**链式绕过**。
> 按下面四张清单逐项过，别凭感觉打。

## OAuth

- redirect_uri 校验：宽松匹配（子域/路径前缀/URL 编码）→ 劫持 code
- state 缺失/可预测 → CSRF 登录绑定
- code 复用/未绑定 client_id → 换客户端兑换
- token 换取端点：是否校验 client_secret？授权范围是否透传
- 身份混淆：用 email/用户名做唯一标识而非 sub → 注册抢占

## JWT

- alg=none / 算法混淆（RS256 公钥当 HS256 密钥）
- kid 注入（路径穿越/SQL）、jku/x5u 指向攻击者 JWKS
- 校验只解不验（decode 不 verify）、过期/aud/iss 不查
- 弱密钥：hashcat -m 16500 直接爆

## 网关签名（自建"零信任"最常见）

- 签名覆盖不全：body/查询串/时间戳没进签名 → 篡改重放
- 时间窗校验缺失或过宽 → 重放旧请求
- nonce 可复用；签名算法可降级（"alg"参数可控）
- 权限放 header/cookie 且网关只验签名不验角色 → 横向提权

## RSC / Server Action（Next.js）

- Server Action ID 可枚举 → 未授权调用内部 action
- Flight 协议数据可伪造 → 客户端传参直接进服务端逻辑
- middleware 只保护页面不保护 API route / action
- 环境变量/配置经由 RSC payload 泄露到客户端

## 通用思路

这类题 flag 在链尾：**每一环独立看都是"半修"状态**，画完整鉴权数据流
（登录→发证→验签→鉴权→业务）再逐环找"信任了不该信的输入"。
