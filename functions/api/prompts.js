export async function onRequestPost({ request, env }) {
  const body = await request.json();
  await env.STUDIO_DATA.put("studio_prompts", JSON.stringify(body));
  return new Response(JSON.stringify({ok:true}), { headers: { "Access-Control-Allow-Origin": "*" } });
}
export async function onRequestOptions() {
  return new Response(null, { headers: { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type" } });
}
