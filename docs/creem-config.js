/**
 * Creem Payment Configuration
 * ============================
 * 1. 登录 https://creem.io/dashboard
 * 2. 创建4个产品（对应4个定价方案）
 * 3. 把产品ID填到下面对应的字段
 * 4. 在 Developers 页面获取 API Key（仅服务端用）
 */
const CREEM_CONFIG = {
  // === 产品ID（从 Creem Dashboard 获取） ===
  products: {
    free:      null,  // Free Trial - 无需支付
    research:  'prod_RESEARCH_ID',   // Research $99/mo
    pro:       'prod_PRO_ID',        // Professional $199/mo
    enterprise:'prod_ENTERPRISE_ID', // Enterprise $799/mo
  },

  // === 结账页配置 ===
  checkout: {
    successUrl: window.location.origin + '/PharmaSim/?payment=success',
    cancelUrl:  window.location.origin + '/PharmaSim/?payment=cancelled',
  },

  // === API 代理（可选，用于动态创建 checkout） ===
  // 部署 Cloudflare Worker 后填入 URL
  apiProxy: null, // e.g. 'https://pharmasim-payment.yourname.workers.dev'

  // === 测试模式 ===
  testMode: true,  // 设为 false 切换到生产环境
};

// 根据 testMode 切换 API 基础URL
CREEM_CONFIG.apiBase = CREEM_CONFIG.testMode
  ? 'https://test-api.creem.io/v1'
  : 'https://api.creem.io/v1';

CREEM_CONFIG.checkoutBase = CREEM_CONFIG.testMode
  ? 'https://test.checkout.creem.io'
  : 'https://checkout.creem.io';

export default CREEM_CONFIG;
