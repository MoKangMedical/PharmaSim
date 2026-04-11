# Second Me 集成指南

## 概述

PharmaSim 通过 A2A (Agent-to-Agent) 协议与 Second Me 平台深度集成，允许用户将自己的"数字分身"(Shade) 带入药品模拟场景。

## 集成架构

```
┌──────────────────────────────────────────────────────┐
│                  用户 (通过 Second Me 登录)              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐              │
│  │ 研究者  │  │ 临床医生 │  │ 药企BD  │              │
│  └────┬────┘  └────┬────┘  └────┬────┘              │
│       │            │            │                     │
│       └────────────┼────────────┘                     │
│                    ▼                                  │
│         ┌──────────────────┐                          │
│         │  Second Me OAuth │                          │
│         │  + 用户身份识别   │                          │
│         └────────┬─────────┘                          │
│                  ▼                                    │
│  ┌──────────────────────────────────────────────┐    │
│  │         PharmaSim A2A 协作层                  │    │
│  │                                               │    │
│  │  用户分身 ←→ 模拟Agent群 ←→ 数据Agent        │    │
│  │    (Shade)    (8个专业Agent)   (校准器)       │    │
│  └──────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

## 接入步骤

### 1. 注册 Second Me 应用

访问 https://develop.second.me/skill 注册 PharmaSim 应用：
- 应用名: PharmaSim
- 回调 URL: `https://mokangmedical.github.io/PharmaSim/api/auth/callback`
- 权限: profile, email, shades:read

### 2. 配置 OAuth

在 `src/a2a/secondme_integration.py` 中填入:
```python
SECONDME_CLIENT_ID = "你的client_id"
SECONDME_CLIENT_SECRET = "你的client_secret"
```

### 3. 用户登录流程

1. 用户点击 "Second Me 登录"
2. 跳转到 `https://go.second.me/oauth/authorize`
3. 用户授权后返回 auth code
4. 后端用 code 换取 access_token
5. 获取用户的 Shade 列表
6. 用户选择要参与模拟的 Shade

### 4. 分身参与模拟

用户的 Shade 可以扮演:
- **药企决策者**: 参与定价和上市策略决策
- **临床专家**: 提供疾病领域深度见解
- **投资人**: 评估药品商业价值和投资回报

## A2A 协议端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/a2a/discovery` | GET | Agent能力发现 |
| `/api/a2a/message` | POST | 消息传递 |
| `/api/a2a/task` | POST | 任务分配 |
| `/api/a2a/status` | GET | 状态查询 |

## API 基础 URL

- Second Me API: `https://api.mindverse.com/gate/lab`
- OAuth 授权: `https://go.second.me/oauth/authorize`
- 开发者门户: `https://develop.second.me/skill`
