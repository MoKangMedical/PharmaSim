/**
 * PharmaSim × Creem Payment Integration
 * ======================================
 * 支持两种模式：
 *   1. 直链模式：按钮直接跳转 Creem 托管结账页
 *   2. API 代理模式：通过后端创建 checkout session（更灵活）
 */

// ── 配置 ─────────────────────────────────────────────
const CREEM = {
  testMode: true,
  checkoutBase: 'https://checkout.creem.io',
  testCheckoutBase: 'https://test.checkout.creem.io',

  // 产品 ID（在 Creem Dashboard 创建产品后替换）
  products: {
    research:   'prod_REPLACE_RESEARCH',
    pro:        'prod_REPLACE_PRO',
    enterprise: 'prod_REPLACE_ENTERPRISE',
  },

  // 成功/取消回调 URL
  get successUrl() {
    return window.location.origin + window.location.pathname + '?payment=success';
  },
  get cancelUrl() {
    return window.location.origin + window.location.pathname + '?payment=cancelled';
  },

  // 可选：Cloudflare Worker 代理 URL
  apiProxy: null,
};

// ── 核心函数 ─────────────────────────────────────────

/**
 * 方案A：直链跳转（最快上线，无需后端）
 * 用户点击按钮 → 直接跳转到 Creem 托管的结账页
 */
function buyNow(planKey) {
  const productId = CREEM.products[planKey];
  if (!productId || productId.startsWith('prod_REPLACE')) {
    showNotification('⚠️ Payment coming soon! Product setup in progress.', 'info');
    return;
  }

  const base = CREEM.testMode ? CREEM.testCheckoutBase : CREEM.checkoutBase;
  const url = `${base}/checkout/${productId}?` + new URLSearchParams({
    success_url: CREEM.successUrl,
    cancel_url: CREEM.cancelUrl,
    metadata_source: 'pharmasim_web',
    metadata_plan: planKey,
  }).toString();

  window.open(url, '_blank');
}

/**
 * 方案B：通过 API 代理创建 checkout session
 * 需要部署后端代理（Cloudflare Worker / Vercel Edge Function）
 */
async function createCheckout(planKey) {
  const productId = CREEM.products[planKey];
  if (!productId || productId.startsWith('prod_REPLACE')) {
    showNotification('⚠️ Payment coming soon! Product setup in progress.', 'info');
    return;
  }

  if (!CREEM.apiProxy) {
    // 降级到直链模式
    buyNow(planKey);
    return;
  }

  try {
    showNotification('🔄 Creating checkout session...', 'info');

    const resp = await fetch(CREEM.apiProxy + '/api/checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_id: productId,
        success_url: CREEM.successUrl,
        request_id: 'req_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8),
        metadata: {
          source: 'pharmasim_web',
          plan: planKey,
          timestamp: new Date().toISOString(),
        },
      }),
    });

    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();

    if (data.checkout_url) {
      window.location.href = data.checkout_url;
    } else {
      throw new Error('No checkout URL returned');
    }
  } catch (err) {
    console.error('Checkout creation failed:', err);
    showNotification('❌ Payment error. Please try again.', 'error');
  }
}

// ── Webhook 验证（服务端参考） ───────────────────────
// Creem Webhook 处理逻辑（Node.js 示例，需部署到后端）
const WEBHOOK_HANDLER_CODE = `
// Cloudflare Worker / Vercel Edge Function 示例
export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // 创建 checkout session
    if (url.pathname === '/api/checkout' && request.method === 'POST') {
      const body = await request.json();
      const resp = await fetch('https://api.creem.io/v1/checkouts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': env.CREEM_API_KEY,
        },
        body: JSON.stringify({
          product_id: body.product_id,
          success_url: body.success_url,
          request_id: body.request_id,
          metadata: body.metadata,
        }),
      });
      const data = await resp.json();
      return new Response(JSON.stringify({
        checkout_url: data.checkout_url || data.url,
        checkout_id: data.id,
      }), {
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      });
    }

    // Webhook 接收
    if (url.pathname === '/api/webhook' && request.method === 'POST') {
      const event = await request.json();
      console.log('Creem webhook:', event.type);

      switch (event.type) {
        case 'checkout.completed':
          // 用户完成支付 → 激活订阅
          console.log('Payment completed:', event.data);
          break;
        case 'subscription.active':
          // 订阅激活
          break;
        case 'subscription.cancelled':
          // 订阅取消
          break;
      }

      return new Response('OK', { status: 200 });
    }

    return new Response('Not Found', { status: 404 });
  },
};
`;

// ── UI 辅助 ─────────────────────────────────────────

function showNotification(message, type = 'info') {
  let container = document.getElementById('creem-notifications');
  if (!container) {
    container = document.createElement('div');
    container.id = 'creem-notifications';
    container.style.cssText = 'position:fixed;top:80px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:8px';
    document.body.appendChild(container);
  }

  const colors = { info: '#3b82f6', success: '#10b981', error: '#ef4444' };
  const toast = document.createElement('div');
  toast.style.cssText = `background:${colors[type]||colors.info};color:#fff;padding:12px 20px;border-radius:10px;font-size:.85rem;font-weight:500;box-shadow:0 4px 20px rgba(0,0,0,.3);animation:fadeIn .3s ease;max-width:350px`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity .3s'; setTimeout(() => toast.remove(), 300); }, 4000);
}

// ── 初始化 ─────────────────────────────────────────

function initCreem() {
  // 检查 URL 参数（支付回调）
  const params = new URLSearchParams(window.location.search);
  if (params.get('payment') === 'success') {
    showNotification('✅ Payment successful! Your subscription is now active.', 'success');
    // 清除 URL 参数
    window.history.replaceState({}, '', window.location.pathname);
    // 如果在 pricing 页面，刷新状态
    if (window.go) window.go('pricing');
  } else if (params.get('payment') === 'cancelled') {
    showNotification('Payment cancelled. No charges were made.', 'info');
    window.history.replaceState({}, '', window.location.pathname);
  }

  // 绑定定价按钮
  document.querySelectorAll('[data-creem-plan]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const plan = btn.dataset.creemPlan;
      if (plan === 'free') {
        // Free plan 直接跳转到 demo
        if (window.go) window.go('select');
        return;
      }
      buyNow(plan);
    });
  });
}

// 页面加载后自动初始化
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initCreem);
} else {
  initCreem();
}

// 暴露全局 API
window.CreemPayment = { buyNow, createCheckout, showNotification, CREEM };
