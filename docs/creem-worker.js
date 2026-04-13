/**
 * Cloudflare Worker — Creem Payment Proxy for PharmaSim
 * ======================================================
 * 
 * 部署步骤：
 * 1. 安装 wrangler: npm i -g wrangler
 * 2. 登录: wrangler login
 * 3. 创建项目: wrangler init pharmasim-payment
 * 4. 把此文件复制到 src/index.js
 * 5. 设置 secret: wrangler secret put CREEM_API_KEY
 * 6. 部署: wrangler deploy
 * 
 * 环境变量（在 Cloudflare Dashboard 或 wrangler secret 设置）：
 * - CREEM_API_KEY: 你的 Creem API Key (creem_开头)
 */

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = request.headers.get('Origin') || '';

    // CORS 预检
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }

    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json',
    };

    // ── 创建 Checkout Session ──────────────────────
    if (url.pathname === '/api/checkout' && request.method === 'POST') {
      try {
        const body = await request.json();
        const { product_id, success_url, request_id, metadata } = body;

        const creemResp = await fetch('https://api.creem.io/v1/checkouts', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': env.CREEM_API_KEY,
          },
          body: JSON.stringify({
            product_id,
            success_url: success_url || `${origin}/?payment=success`,
            request_id: request_id || `req_${Date.now()}`,
            metadata: metadata || {},
          }),
        });

        const data = await creemResp.json();

        if (!creemResp.ok) {
          return new Response(JSON.stringify({ error: data.message || 'Creem API error' }), {
            status: creemResp.status,
            headers: corsHeaders,
          });
        }

        return new Response(JSON.stringify({
          checkout_url: data.url || data.checkout_url,
          checkout_id: data.id,
        }), { headers: corsHeaders });

      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), {
          status: 500,
          headers: corsHeaders,
        });
      }
    }

    // ── Webhook 接收 ──────────────────────────────
    if (url.pathname === '/api/webhook' && request.method === 'POST') {
      try {
        const event = await request.json();
        console.log('Creem webhook:', JSON.stringify(event));

        // TODO: 处理不同事件类型
        switch (event.type) {
          case 'checkout.completed':
            // 支付完成 → 激活用户订阅
            // 可接入数据库记录
            break;
          case 'subscription.active':
            // 订阅激活
            break;
          case 'subscription.updated':
            // 订阅更新（升级/降级）
            break;
          case 'subscription.cancelled':
            // 订阅取消
            break;
          case 'subscription.paused':
            // 订阅暂停
            break;
        }

        return new Response('OK', { status: 200 });
      } catch (err) {
        console.error('Webhook error:', err);
        return new Response('Error', { status: 400 });
      }
    }

    // ── 健康检查 ──────────────────────────────────
    if (url.pathname === '/api/health') {
      return new Response(JSON.stringify({
        status: 'ok',
        timestamp: new Date().toISOString(),
        creem_configured: !!env.CREEM_API_KEY,
      }), { headers: corsHeaders });
    }

    return new Response('Not Found', { status: 404 });
  },
};
