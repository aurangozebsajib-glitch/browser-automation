
const API = location.origin;
let unsaved=false;
const ideaEl=document.getElementById('ideaPrompt');
const indicator=document.getElementById('saveIndicator');

async function api(path, opts={}){
  const r=await fetch(API+path, {headers:{'Content-Type':'application/json'}, ...opts});
  if(!r.ok) throw new Error(await r.text());
  return r.json();
}
async function loadCurrent(){
  try{
    const cur=await api('/api/prompts/current?prompt_type=idea');
    ideaEl.value=cur.content||'';
    indicator.textContent=cur.content?'saved':'empty';
    document.getElementById('promptMeta').textContent=cur.created_at?`Last saved: ${cur.created_at}`:'';
  }catch(e){console.error(e)}
  loadJobs(); loadIdeas(); loadQueue(); loadSettings();
}
ideaEl.addEventListener('input',()=>{unsaved=true; indicator.textContent='unsaved*'; indicator.style.background='#ff4d4d'});

document.getElementById('btnSave').onclick=async()=>{
  await api('/api/prompts/save',{method:'POST', body:JSON.stringify({prompt_type:'idea', content:ideaEl.value})});
  unsaved=false; indicator.textContent='saved'; indicator.style.background='#222';
  loadCurrent();
};
document.getElementById('btnRestore').onclick=loadCurrent;
document.getElementById('btnTest').onclick=async()=>{
  const r=await api('/api/run/test_prompt',{method:'POST', body:JSON.stringify({prompt:ideaEl.value, use_saved:false, dry_run:true})});
  document.getElementById('rawResult').textContent=JSON.stringify(r,null,2);
};
document.getElementById('btnRunNow').onclick=async()=>{
  document.getElementById('rawResult').textContent='Running via Camoufox...';
  try{
    const r=await api('/api/run/now',{method:'POST', body:JSON.stringify({use_saved:true})});
    document.getElementById('rawResult').textContent=JSON.stringify(r,null,2);
    if(r.selected) document.getElementById('selectedIdea').innerHTML=`<h4>Selected: ${r.selected.title}</h4><small>${r.selected.id}</small>`;
    loadJobs(); loadIdeas(); loadQueue();
  }catch(e){document.getElementById('rawResult').textContent='Error: '+e;}
};

async function loadJobs(){
  const jobs=await api('/api/jobs'); const tbody=document.querySelector('#jobsTable tbody'); tbody.innerHTML='';
  jobs.forEach(j=>{tbody.innerHTML+=`<tr><td>${j.run_id}</td><td>${j.status}</td><td>${j.stage}</td><td>${j.start_time||''}</td></tr>`});
  if(jobs[0]) document.getElementById('lastRun').textContent=jobs[0].run_id+' '+jobs[0].status;
}
async function loadIdeas(){
  const ideas=await api('/api/ideas/history'); const tbody=document.querySelector('#ideasTable tbody'); tbody.innerHTML='';
  ideas.forEach(i=>{tbody.innerHTML+=`<tr><td>${i.idea_id}</td><td>${i.title}</td><td>${i.is_selected?'✅':''}</td><td>${i.is_duplicate?'dup':''}</td></tr>`});
}
async function loadQueue(){
  const tasks=await api('/api/tasks'); const tbody=document.querySelector('#queueTable tbody'); tbody.innerHTML='';
  tasks.forEach(t=>{tbody.innerHTML+=`<tr><td>${t.task_id}</td><td>${t.type}</td><td>${t.status}</td><td>${t.episode_id}</td></tr>`});
}
async function loadSettings(){
  const s=await api('/api/settings');
  document.getElementById('dailyTime').value=s.daily_time||'09:00';
  document.getElementById('scheduleEnabled').checked=!!s.schedule_enabled;
  document.getElementById('missedPolicy').value=s.missed_run_policy||'run_on_startup';
  document.getElementById('provider').value=s.provider||'generic';
  document.getElementById('camExe').value=s.camoufox?.executable_path||'';
  document.getElementById('connectUrl').value=s.camoufox?.connect_url||'';
  document.getElementById('nextRun').textContent=(s.schedule_enabled? s.daily_time+' Asia/Dhaka':'disabled');
}
document.getElementById('btnSaveSettings').onclick=async()=>{
  const payload={
    daily_time: document.getElementById('dailyTime').value,
    schedule_enabled: document.getElementById('scheduleEnabled').checked,
    missed_run_policy: document.getElementById('missedPolicy').value,
    provider: document.getElementById('provider').value,
    camoufox:{
      executable_path: document.getElementById('camExe').value,
      connect_url: document.getElementById('connectUrl').value||null
    }
  };
  await api('/api/settings',{method:'POST', body:JSON.stringify(payload)});
  alert('Settings saved'); loadSettings();
};
document.getElementById('btnTestCamoufox').onclick=async()=>{
  const r=await api('/api/camoufox/test'); document.getElementById('camTest').textContent=JSON.stringify(r,null,2);
};
// tabs
document.querySelectorAll('.sidebar nav button').forEach(b=>{
  b.onclick=()=>{
    document.querySelectorAll('.sidebar nav button').forEach(x=>x.classList.remove('active'));
    b.classList.add('active');
    document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
    document.getElementById('tab-'+b.dataset.tab).classList.add('active');
  };
});

loadCurrent();
setInterval(()=>{loadJobs(); loadQueue();}, 8000);
