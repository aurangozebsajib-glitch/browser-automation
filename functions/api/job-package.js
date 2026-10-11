export async function onRequestGet({ env }) {
  const prompts = await env.STUDIO_DATA.get("studio_prompts", "json") || {};
  const ideas = await env.STUDIO_DATA.get("studio_ideas", "json") || [];
  const selected = ideas.find(i => i.selected) || null;
  return new Response(JSON.stringify({ prompts, selected_idea: selected, ideas: ideas.slice(0,20) }), { headers: { "Access-Control-Allow-Origin": "*" } });
}
