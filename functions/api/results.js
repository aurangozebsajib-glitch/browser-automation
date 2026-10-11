export async function onRequestPost({ request, env }) {
  const body = await request.json();
  let list = await env.STUDIO_DATA.get("studio_ideas", "json") || [];
  list.unshift({ id: "JOB_"+Date.now(), raw: body.raw_response?.slice(0,50000), at: new Date().toISOString() });
  await env.STUDIO_DATA.put("studio_ideas", JSON.stringify(list.slice(0,100)));
  await env.STUDIO_DATA.put("last_result", JSON.stringify(list[0]));
  return new Response(JSON.stringify({ok:true}), { headers: { "Access-Control-Allow-Origin": "*" } });
}
export async function onRequestGet({ env }) {
  const last = await env.STUDIO_DATA.get("last_result", "json");
  return new Response(JSON.stringify(last), { headers: { "Access-Control-Allow-Origin": "*" } });
}
export async function onRequestOptions() {
  return new Response(null, { headers: { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type" } });
}
