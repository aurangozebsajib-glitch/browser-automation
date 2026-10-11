export default {
  async fetch(request, env, ctx) {
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Content-Type": "application/json"
    };
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });

    const url = new URL(request.url);
    const path = url.pathname;
    const kv = env.STUDIO_DATA;

    if (path === "/api/status") {
      return new Response(JSON.stringify({ status: "online", kv:!!kv, time: new Date().toISOString() }), { headers: cors });
    }
    if (path === "/api/job-package" && request.method === "GET") {
      const prompts = (await kv.get("studio_prompts", "json")) || {};
      const ideas = (await kv.get("studio_ideas", "json")) || [];
      return new Response(JSON.stringify({ prompts, ideas }), { headers: cors });
    }
    if (path === "/api/prompts" && request.method === "POST") {
      const body = await request.json();
      await kv.put("studio_prompts", JSON.stringify(body));
      return new Response(JSON.stringify({ ok: true }), { headers: cors });
    }
    if (path === "/api/results" && request.method === "POST") {
      const body = await request.json();
      let list = (await kv.get("studio_ideas", "json")) || [];
      list.unshift({ id: "JOB_" + Date.now(), raw: (body.raw_response || "").slice(0, 80000), at: new Date().toISOString() });
      await kv.put("studio_ideas", JSON.stringify(list.slice(0,100)));
      await kv.put("last_result", JSON.stringify(list[0]));
      return new Response(JSON.stringify({ ok: true }), { headers: cors });
    }
    if (path === "/api/results/latest") {
      const last = await kv.get("last_result", "json");
      return new Response(JSON.stringify(last || null), { headers: cors });
    }
    return env.ASSETS.fetch(request);
  }
}
