# Creem 支付接入指南

## 快速上线（5分钟）

### 步骤 1：创建 Creem 账号
1. 访问 https://creem.io 注册
2. 完成商家验证

### 步骤 2：创建产品
在 Creem Dashboard → Products 页面创建4个产品：

| 产品名 | 价格 | 周期 | 对应方案 |
|--------|------|------|----------|
| PharmaSim Research | $99 | Monthly | Research |
| PharmaSim Professional | $199 | Monthly | Professional |
| PharmaSim Enterprise | $799 | Monthly | Enterprise |

### 步骤 3：获取产品 ID
每个产品创建后会有一个 `prod_xxxxxxx` 格式的 ID，复制它们。

### 步骤 4：更新配置
编辑 `creem-integration.js`，替换产品 ID：

```javascript
products: {
  research:   'prod_你的真实ID',
  pro:        'prod_你的真实ID',
  enterprise: 'prod_你的真实ID',
},
```

### 步骤 5：设置 Webhook（推荐）
在 Creem Dashboard → Developers → Webhooks 添加：
- URL: `https://你的worker域名/api/webhook`
- Events: checkout.completed, subscription.active, subscription.cancelled

### 步骤 6：测试
1. 确保 `testMode: true`（使用测试环境）
2. 用测试卡号 4242 4242 4242 4242 测试支付
3. 测试通过后改为 `testMode: false`

---

## 进阶：部署 API 代理（Cloudflare Worker）

如果需要动态创建 checkout session（更灵活，支持自定义字段），部署 Worker：

```bash
# 安装 wrangler
npm i -g wrangler

# 登录
wrangler login

# 进入项目目录
cd ~/Desktop/PharmaSim/docs

# 设置 API Key（安全存储，不会暴露到前端）
wrangler secret put CREEM_API_KEY
# 输入: creem_你的API密钥

# 部署
wrangler deploy

# 部署成功后，把 Worker URL 填入 creem-integration.js 的 apiProxy 字段
```

---

## 文件说明

| 文件 | 用途 |
|------|------|
| `creem-integration.js` | 前端支付集成（按钮绑定、支付回调） |
| `creem-config.js` | 配置文件（备选，当前未使用） |
| `creem-worker.js` | Cloudflare Worker 后端代理 |
| `wrangler.toml` | Worker 部署配置 |

## 测试卡号

| 卡号 | 结果 |
|------|------|
| 4242 4242 4242 4242 | 支付成功 |
| 4000 0000 0000 0002 | 支付失败 |
| 4000 0000 0000 9995 | 需要 3D 验证 |

过期日期：任意未来日期（如 12/28）
CVC：任意 3 位数字（如 123）
