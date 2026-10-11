/**
 * Qwen Prompt Studio - Worker.js
 * Role: Meta AI (Tool Maker) - Upgraded with Auth + Parser
 */

function parseQwenResponse(raw) {
  if (!raw) return [];
  let text = raw.trim();
  text = text.replace(/Here are \d+.*?:/i, '').trim();
  let prompts = [];
  const numbered = [...text.matchAll(/(?:^|\n)\s*(?:\*\*)?\s*\d+[\.\)]\s*\*?\*?\s*(.+?)(?=\n\s*\d+[\.\)]|$)/gs)];
  if (numbered.length >= 2) {
    prompts = numbered.map(m => m[1].trim().replace(/\*\*/g,'')).filter(p => p.length > 10);
  }
  if (prompts.length < 2) {
    const bullets = [...text.matchAll(/(?:^|\n)\s*[-•*]\s+(.+)/g)];
    if (bullets.length >= 2) {
      prompts = bullets.map(m => m[1].trim()).filter(p => p.length > 10);
    }
  }
  if (prompts.length < 2) {
    const codeBlocks = [...text.matchAll(/```(?:[a-z]*)\n?([\s\S]*?)```/g)];
    if (codeBlocks.length > 0) {
      const inside = codeBlocks.map(b => b[1]).join('\n');
      prompts = inside.split('\n').map(s => s.trim()).filter(s => s.length > 15);
    }
  }
  if (prompts.length < 2) {
    prompts = text.split('\n').map(s => s.replace(/^\d+[\.\)]\s*/, '').replace(/^[-•*]\s*/, '').trim()).filter(s => s.length > 15 && s.length < 500);
  }
  prompts = prompts.map(p => p.replace(/^["']|["']$/g, '').trim()).filter((v,i,a) => a.indexOf(v) === i);
  return prompts.slice(0, 100);
}

export default {
  async fetch(request, env, ctx) {
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, X-API-KEY",
      "Content-Type": "application/json"
    };
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });
    const url = new URL(request.url);
    const path = url.pathname;
    const kv = env.STUDIO_DATA;
    const apiKey = env.API_KEY;
    const isApiRoute = path.startsWith("/api/");
    const isPublicRoute = path === "/api/status" || path === "/api/parse";
    if (apiKey && isApiRoute && !isPublicRoute) {
      const provided = request.headers.get("X-API-KEY") || url.searchParams.get("key");
      if (provided !== apiKey) {
        return new Response(JSON.stringify({ error: "Unauthorized - Invalid X-API-KEY" }), { status: 401, headers: cors });
      }
    }
    if (path === "/api/status") {
      return new Response(JSON.stringify({ status: "online", kv: !!kv, hasAuth: !!apiKey, time: new Date().toISOString() }), { headers: cors });
    }
    if (path === "/api/parse" && request.method === "POST") {
      try {
        const body = await request.json();
        const raw = body.text || body.raw_response || "";
        const prompts = parseQwenResponse(raw);
        return new Response(JSON.stringify({ prompts, count: prompts.length, raw_length: raw.length }), { headers: cors });
      } catch (e) {
        return new Response(JSON.stringify({ error: e.message, prompts: [] }), { status: 400, headers: cors });
      }
    }
    if (path === "/api/job-package" && request.method === "GET") {
      try {
        const prompts = (await kv.get("studio_prompts", "json")) || {};
        const ideas = (await kv.get("studio_ideas", "json")) || [];
        const last = await kv.get("last_result", "json");
        return new Response(JSON.stringify({ prompts, ideas, last, serverTime: new Date().toISOString() }), { headers: cors });
      } catch (e) {
        return new Response(JSON.stringify({ prompts: {}, ideas: [], error: e.message }), { headers: cors });
      }
    }
    if (path === "/api/prompts" && request.method === "POST") {
      const body = await request.json();
      await kv.put("studio_prompts", JSON.stringify(body));
      return new Response(JSON.stringify({ ok: true, saved: Object.keys(body).length }), { headers: cors });
    }
    if (path === "/api/results" && request.method === "POST") {
      const body = await request.json();
      const raw = body.raw_response || body.text || "";
      const parsed = parseQwenResponse(raw);
      let list = (await kv.get("studio_ideas", "json")) || [];
      const entry = {
        id: "JOB_" + Date.now(),
        raw: raw.slice(0, 80000),
        parsed: parsed,
        count: parsed.length,
        at: new Date().toISOString()
      };
      list.unshift(entry);
      list = list.slice(0, 100);
      await kv.put("studio_ideas", JSON.stringify(list));
      await kv.put("last_result", JSON.stringify(entry));
      return new Response(JSON.stringify({ ok: true, id: entry.id, count: parsed.length, prompts: parsed }), { headers: cors });
    }
    if (path === "/api/results/latest") {
      const last = await kv.get("last_result", "json");
      return new Response(JSON.stringify(last || null), { headers: cors });
    }
    try {
      return await env.ASSETS.fetch(request);
    } catch {
      return new Response(JSON.stringify({ error: "Not found, use /api/*" }), { status: 404, headers: cors });
    }
  }
}
