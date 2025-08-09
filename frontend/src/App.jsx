import React, { useEffect, useMemo, useRef, useState } from "react";

// ==============================================
// AI Sports Coach – Hackathon Build (Client-only)
// ==============================================
// Implements the requested workflow & UI:
// Tabs (left→right): Ask Coach → Training Regimen → Video → Goals → Diary → Dashboard
// - Ask Coach: chat-only UI with sessions, speaking mode, persona multi-select,
//   and answers that incorporate context from Goals/Diary/Readiness/History.
// - Training Regimen: derives a weekly plan from other tabs (dummy logic).
// - Video: upload file, location+weather input, feedback (issues/positives/alternatives).
// - Goals: goals grouped by category.
// - Diary: entries grouped by date & activity type.
// - Dashboard: performance + readiness tiles moved here; upload health file (Fitbit CSV)
//   and show line charts for sleep, stress, steps, cardio, active minutes, distance, calories.
// Also adds a best-effort ElevenLabs TTS call (via /api/voice/tts if a backend is running),
// else falls back to Web Speech synthesis.

// ---------------- Dummy players & telemetry ----------------
const PLAYERS = [
  { id: "p1", name: "Ava Patel", sport: "soccer", position: "Forward", team: "Blue Tigers", metrics: [
    { ts: "2025-08-01T10:00:00Z", speed_kmh: 28.1, accel: 3.1, hr: 152, xg: 0.7, shots: 5, pass_pct: 78 },
    { ts: "2025-08-02T10:00:00Z", speed_kmh: 29.4, accel: 3.4, hr: 156, xg: 0.6, shots: 3, pass_pct: 82 },
    { ts: "2025-08-03T10:00:00Z", speed_kmh: 30.2, accel: 3.6, hr: 158, xg: 0.8, shots: 6, pass_pct: 80 },
  ]},
  { id: "p2", name: "Diego Santos", sport: "soccer", position: "Midfielder", team: "Blue Tigers", metrics: [
    { ts: "2025-08-01T10:00:00Z", speed_kmh: 26.0, accel: 2.9, hr: 148, xg: 0.2, shots: 1, pass_pct: 89 },
    { ts: "2025-08-02T10:00:00Z", speed_kmh: 27.5, accel: 3.0, hr: 151, xg: 0.3, shots: 2, pass_pct: 90 },
    { ts: "2025-08-03T10:00:00Z", speed_kmh: 27.1, accel: 2.8, hr: 147, xg: 0.25, shots: 2, pass_pct: 88 },
  ]},
];

const READINESS = {
  p1: { sleep_score: 78, hr_rest: 56, hrv: 78, fatigue: "moderate" },
  p2: { sleep_score: 88, hr_rest: 52, hrv: 92, fatigue: "low" },
};

const PERSONAS = ["Calm mentor", "Tough coach", "Data analyst"];

const API = (typeof window !== 'undefined' && window.__VITE_API__) || ""; // optional, for ElevenLabs relay
const ELEVEN_ASR_WS = API ? `${API.replace(/^http/, 'ws')}/api/voice/asr` : ""; // optional websocket relay

// ---------------- Helpers & tiny LangGraph-ish router ----------------
const KEYWORDS = {
  performance: ["speed","xg","form","fitness","stats","performance","passing","accel","shot"],
  tactics: ["tactic","formation","press","counter","defend","attack","build-up"],
  training: ["drill","training","practice","plan","session","warmup","cooldown","recovery"],
  mental: ["mindset","confidence","focus","visualization","breath","anxiety","pep","motivation"],
};
const avg = xs => Math.round((xs.reduce((a,b)=>a+b,0)/Math.max(xs.length,1))*100)/100;
const route = q => { const s=(q||"").toLowerCase(); const hits=Object.entries(KEYWORDS).filter(([,ks])=>ks.some(k=>s.includes(k))).map(([k])=>k); return hits.length===0?"performance":(hits.length===1?hits[0]:"multi"); };

function performanceAgent(player){
  const m = player.metrics;
  const facts = { speed_avg: avg(m.map(x=>x.speed_kmh)), accel_avg: avg(m.map(x=>x.accel)), xg_avg: avg(m.map(x=>x.xg)), pass_pct: avg(m.map(x=>x.pass_pct)) };
  const insight = `${player.name} — speed ${facts.speed_avg} km/h, accel ${facts.accel_avg} m/s², xG ${facts.xg_avg}, pass ${facts.pass_pct}%.`;
  return { insight, facts: { performance: facts } };
}
function tacticsAgent(player){
  const forward = player.position.toLowerCase()==="forward";
  const formation = forward?"4-3-3":"4-2-3-1";
  const note = forward?"High press; isolate 9 in half-spaces.":"Double pivot for buildup; protect transitions.";
  return { insight: `Tactics: ${note}`, facts: { tactics: { formation, note } } };
}
function trainingAgent(perf, readiness){
  const drills=[]; if((perf?.accel_avg??10)<3.3) drills.push("Resisted sprints 6×20m (walk-back recovery)"); if((perf?.pass_pct??100)<85) drills.push("Rondo 6v2 two-touch 4×3min"); if((perf?.xg_avg??1)<0.6) drills.push("Finishing patterns: cutback & near-post 4×6 reps"); if((readiness?.fatigue??"low")==="moderate") drills.push("Reduce volume −10% + 10min mobility"); if(!drills.length) drills.push("Maintain: mobility + small-sided 5v5 3×6min");
  const weather = Math.random()>0.5?"Mild (75°F). Intervals + extended warmup.":"Hot (83°F). Morning tempo + hydrate.";
  return { insight: `Training: ${drills.join("; ")}`, facts: { training: { drills, weather } } };
}
function mentalAgent(player){ return { insight: "Mental routine prepared.", facts: { mental: { script: `Pep talk for ${player.name}: Breathe 4-4-8. Visualize first touch forward. Trust your pace.` }}}; }

function runGraph({ question, player, readiness }){
  const r = route(question); let insights=[]; let facts={ readiness };
  if(r==="performance"||r==="multi"){ const p=performanceAgent(player); insights.push(p.insight); facts={...facts, ...p.facts}; }
  if(r==="tactics"||r==="multi"){ const t=tacticsAgent(player); insights.push(t.insight); facts={...facts, ...t.facts}; }
  if(r==="training"||r==="multi"){ const tr=trainingAgent(facts.performance, readiness); insights.push(tr.insight); facts={...facts, ...tr.facts}; }
  if(r==="mental"||r==="multi"){ const m=mentalAgent(player); insights.push(m.insight); facts={...facts, ...m.facts}; }
  return { insights, facts };
}

// ---------------- Voice: ElevenLabs (fallback to Web Speech) ----------------
async function speakEleven(text){
  if(!API){ // no backend available in-canvas; fallback
    const synth = window.speechSynthesis; if(!synth) return; const u=new SpeechSynthesisUtterance(text); synth.cancel(); synth.speak(u); return;
  }
  try{
    const res = await fetch(`${API}/api/voice/tts`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(text) });
    const blob = await res.blob(); const url = URL.createObjectURL(blob); const audio = new Audio(url); await audio.play();
  }catch(e){ const synth=window.speechSynthesis; if(synth){ const u=new SpeechSynthesisUtterance(text); synth.cancel(); synth.speak(u);} }
}

// ElevenLabs ASR (optional via WS relay) + Web Speech fallback
function useASR(){
  const webkitOK = (typeof window!=="undefined" && "webkitSpeechRecognition" in window);
  const [listening, setListening] = useState(false);
  const wsRef = useRef(null);

  async function startEleven(onText){
    if(!ELEVEN_ASR_WS) return false;
    try{
      const ws = new WebSocket(ELEVEN_ASR_WS);
      wsRef.current = ws;
      ws.binaryType = 'arraybuffer';
      const media = await navigator.mediaDevices.getUserMedia({audio:true});
      const Ctx = window.AudioContext || window.webkitAudioContext;
      const ctx = new Ctx({ sampleRate: 16000 });
      const src = ctx.createMediaStreamSource(media);
      const proc = ctx.createScriptProcessor(4096,1,1);
      src.connect(proc); proc.connect(ctx.destination);
      ws.addEventListener('open', ()=>{ setListening(true); });
      ws.addEventListener('message', ev=>{ try{ const msg = JSON.parse(ev.data); if(msg.text){ onText(msg.text); } }catch{} });
      proc.onaudioprocess = (e)=>{
        if(ws.readyState!==1) return;
        const pcm = e.inputBuffer.getChannelData(0);
        const buf = new ArrayBuffer(pcm.length*2); const view = new DataView(buf);
        for(let i=0;i<pcm.length;i++){ let s=Math.max(-1,Math.min(1,pcm[i])); view.setInt16(i*2, s<0?s*0x8000:s*0x7FFF, true); }
        ws.send(buf);
      };
      const cleanup = ()=>{ try{proc.disconnect(); src.disconnect(); ctx.close();}catch{}; try{media.getTracks().forEach(t=>t.stop());}catch{} };
      ws.addEventListener('close', ()=>{ cleanup(); setListening(false); });
      ws.addEventListener('error', ()=>{ cleanup(); setListening(false); });
      return true;
    }catch(e){ console.warn('ASR WS failed', e); return false; }
  }

  function startWebkit(onText){
    if(!webkitOK) return false; const rec = new window.webkitSpeechRecognition();
    rec.continuous=false; rec.lang='en-US';
    rec.onresult=e=>{ onText(e.results[0][0].transcript); stop(); };
    rec.onend=()=>setListening(false);
    rec.start(); setListening(true);
    wsRef.current = { close: ()=>{} };
    return true;
  }

  async function listen(onText){ if(ELEVEN_ASR_WS){ const ok = await startEleven(onText); if(ok) return; } startWebkit(onText); }
  function stop(){ if(wsRef.current){ try{ wsRef.current.close(); }catch{} } setListening(false); }
  return { listen, stop, listening, engine: ELEVEN_ASR_WS? 'ElevenLabs (WS)' : (webkitOK? 'Web Speech' : 'None') };
}

// ---------------- Generic UI Bits ----------------
const Tab = ({label,active,onClick}) => (<button onClick={onClick} className={'px-4 py-2 rounded-2xl border '+(active?'bg-black text-white':'')}>{label}</button>);
const Card = ({title,children}) => (<div className='p-4 border rounded-2xl shadow-sm min-h-[140px]'><div className='font-semibold mb-2'>{title}</div>{children}</div>);
const KeyVal = ({label,value}) => (<div className='flex justify-between mb-1'><span className='opacity-70'>{label}</span><span>{value ?? '—'}</span></div>);

// ---------------- Tiny charts for Dashboard ----------------
function Spark({values,width=320,height=70}){ const max=Math.max(...values),min=Math.min(...values); const pts=values.map((v,i)=>`${(i/(values.length-1))*width},${height-((v-min)/(max-min+1e-9))*height}`).join(' '); return <svg width={width} height={height}><polyline fill='none' stroke='currentColor' strokeWidth='2' points={pts}/></svg>; }
function Gauge({value,max}){ const pct=Math.max(0,Math.min(1,value/max)); return <div className='w-full h-3 bg-gray-200 rounded-full overflow-hidden'><div style={{width:(pct*100)+'%'}} className='h-3 bg-black'></div></div>; }

// ====================== CSV Parser + Tests =======================
function parseHealthCSV(text, period){
  // Expect header: date,sleep,stress,steps,cardio,active,dist,cal
  const lines = String(text).trim().split(/\r?\n+/);
  if(!lines.length) return [];
  const data = lines.slice(1).filter(Boolean).slice(-(period==='week'?7:30));
  return data.map(l=>{
    const [date,sleep,stress,steps,cardio,active,dist,cal] = l.split(',');
    return { date, sleep:+sleep, stress:+stress, steps:+steps, cardio:+cardio, active:+active, dist:+dist, cal:+cal };
  });
}

function testHealthCsvParser(){
  // Mixed newlines + blank line, ensure slicing works
  const sample = `date,sleep,stress,steps,cardio,active,dist,cal
2025-08-01,7.5,30,8000,50,35,6.2,2200

2025-08-02,8,32,8300,52,36,6.4,2210
2025-08-03,7.8,34,8600,54,37,6.5,2225`;
  const rows = parseHealthCSV(sample, 'week');
  console.assert(rows.length===3, 'CSV parse: expected 3 rows, got', rows.length);
  console.assert(rows[0].date==='2025-08-01', 'CSV parse: first date mismatch');
  console.assert(rows[1].steps===8300, 'CSV parse: steps mismatch');
}

// ================================== App ==================================
export default function App(){
  const [tab, setTab] = useState('Ask Coach');
  const [playerId, setPlayerId] = useState('p1');
  const player = useMemo(()=> PLAYERS.find(p=>p.id===playerId) ?? PLAYERS[0], [playerId]);
  const readiness = READINESS[player.id] ?? { sleep_score:75, hr_rest:58, hrv:70, fatigue:'low' };

  // Goals (with categories) & Diary (with activity types)
  const [goals, setGoals] = useState([ // seed examples
    { id:'g1', cat:'speed', text:'Hit 31 km/h top speed', created:'2025-07-30' },
    { id:'g2', cat:'passing', text:'Reach 88% pass accuracy', created:'2025-07-31' },
  ]);
  const [newGoal, setNewGoal] = useState("");
  const [newGoalCat, setNewGoalCat] = useState('speed');

  const [diary, setDiary] = useState([
    { id:'d1', date:'2025-08-02', type:'training', text:'5v5 small-sided, good pop' },
    { id:'d2', date:'2025-08-03', type:'eating', text:'Carb load pre-session' },
  ]);
  const [entryText, setEntryText] = useState("");
  const [entryType, setEntryType] = useState('training');

  // Chat sessions for Ask Coach
  const [sessions, setSessions] = useState([ { id:'s1', title:'Session 1', persona:[PERSONAS[0]], speaking:true, messages: [] } ]);
  const [activeSessionId, setActiveSessionId] = useState('s1');
  const activeSession = sessions.find(s=>s.id===activeSessionId);
  const { listen, stop, listening, engine } = useASR();
  const [chatInput, setChatInput] = useState('How is my form and what drills for this week?');

  useEffect(()=>{ testHealthCsvParser(); },[]);

  function newSession(){
    const id = 's'+Date.now();
    setSessions(s=>[...s, { id, title:`Session ${s.length+1}`, persona:[PERSONAS[0]], speaking:true, messages: [] }]);
    setActiveSessionId(id);
  }
  function toggleSpeaking(){ setSessions(ss=>ss.map(s=> s.id===activeSessionId? {...s, speaking: !s.speaking}:s)); }
  function updatePersona(arr){ setSessions(ss=>ss.map(s=> s.id===activeSessionId? {...s, persona: arr}:s)); }

  // Compose contextual answer (dummy + tab context) with streaming effect
  async function sendChat(){
    if(!chatInput.trim()) return;
    const ctxGoals = goals.map(g=>`[goal:${g.cat}] ${g.text}`).join(' | ');
    const ctxDiary = diary.slice(-3).map(d=>`[${d.date}:${d.type}] ${d.text}`).join(' | ');
    const persona = activeSession.persona.join(', ');

    // Add user message
    const userMsg = { role:'user', text: chatInput, ts: new Date().toISOString() };
    setSessions(ss=>ss.map(s=> s.id===activeSessionId? {...s, messages: [...s.messages, userMsg]}:s));

    // Run agents
    const g = runGraph({ question: chatInput, player, readiness });
    // Synthesize combined answer using context
    const answer = `${persona} — Using context from goals & diary: ${ctxGoals || '—'} ${ctxDiary? ' | '+ctxDiary:''}. `+
                   `${g.insights.join(' | ')}`;

    // Streaming effect
    const botMsg = { role:'assistant', text:"", ts: new Date().toISOString() };
    setSessions(ss=>ss.map(s=> s.id===activeSessionId? {...s, messages: [...s.messages, botMsg]}:s));
    for(let i=0;i<answer.length;i+=4){
      await new Promise(r=>setTimeout(r, 8));
      setSessions(ss=>ss.map(s=> s.id===activeSessionId? {
        ...s,
        messages: s.messages.map((m,idx)=> idx===s.messages.length-1? {...m, text: answer.slice(0, i)}: m)
      }:s));
    }
    // Finalize text & speak
    setSessions(ss=>ss.map(s=> s.id===activeSessionId? {
      ...s,
      messages: s.messages.map((m,idx)=> idx===s.messages.length-1? {...m, text: answer}: m)
    }:s));
    if(activeSession.speaking){ await speakEleven(answer); }
    setChatInput("");
  }

  // ---------------- Training Regimen (derived) ----------------
  function buildRegimen(){
    const perf = performanceAgent(player).facts.performance;
    const gcats = goals.reduce((acc,g)=>{ acc[g.cat]=(acc[g.cat]||0)+1; return acc;},{});
    const fatigue = readiness.fatigue;
    const week = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]; 
    // simple allocator
    const plan = week.map((d,i)=>({ day:d, focus: i%2===0? (gcats.speed?"speed":"finishing") : (gcats.passing?"passing":"conditioning"), volume: fatigue==='moderate'?0.9:1.0 }));
    const drills = trainingAgent(perf, readiness).facts.training.drills;
    return { plan, drills };
  }

  // ---------------- Video (analysis + weather/location) ----------------
  const [videoResult, setVideoResult] = useState(null);
  const [location, setLocation] = useState('Chicago');
  const [weather, setWeather] = useState('Mild (75°F)');
  const fileRef = useRef(null);
  function analyzeVideo(){
    const issues = ["Overstriding at frames ~30–40","Hips drop on cutback" ];
    const positives = ["Cadence steady ~180","Good arm swing symmetry" ];
    const alternatives = weather.includes('Hot')? ["Shorter tempo early AM","Pool intervals"] : ["Longer intervals on pitch","Hill sprints (shade)"];
    setVideoResult({ issues, positives, alternatives, location, weather });
  }

  // ---------------- Goals (categorized) ----------------
  function addGoalItem(){ if(!newGoal.trim()) return; setGoals(g=>[...g, { id:'g'+Date.now(), cat:newGoalCat, text:newGoal, created:new Date().toISOString().slice(0,10)}]); setNewGoal(''); }
  const goalsByCat = PERSONAS.reduce((acc,_)=>acc,{}) || {}; // no-op just to avoid eslint noise
  const groupedGoals = goals.reduce((acc,g)=>{ (acc[g.cat]=acc[g.cat]||[]).push(g); return acc;},{});

  // ---------------- Diary (group by date and type) ----------------
  function addDiaryItem(){ if(!entryText.trim()) return; setDiary(d=>[...d, { id:'d'+Date.now(), date:new Date().toISOString().slice(0,10), type:entryType, text:entryText }]); setEntryText(''); }
  const groupedDiary = diary.reduce((acc,d)=>{ const k=d.date; (acc[k]=acc[k]||[]).push(d); return acc;},{});

  // ---------------- Dashboard: health data upload + charts ----------------
  const [healthRows, setHealthRows] = useState([]);
  const [period, setPeriod] = useState('week');
  function onUploadHealth(e){
    const f = e.target.files?.[0]; if(!f) return; const reader = new FileReader();
    reader.onload = () => {
      // Expect CSV with date,sleep,stress,steps,cardio,active,dist,cal
      const rows = parseHealthCSV(reader.result, period);
      setHealthRows(rows);
    };
    reader.readAsText(f);
  }
  // fallback dummy timeline when none uploaded
  const timeline = healthRows.length? healthRows : (
    period==='week'
      ? [1,2,3,4,5,6,7].map(i=>({date:`D${i}`, sleep:7+i%2, stress:30+i*2, steps:8000+i*300, cardio:50+i*2, active:35+i, dist:6+i*0.2, cal:2200+i*10}))
      : [ ...Array(30).keys() ].map(i=>({date:`d${i+1}`, sleep:6.5+(i%3)*0.3, stress:25+i, steps:7000+i*100, cardio:40+i*1.2, active:30+i*0.5, dist:5+i*0.1, cal:2100+i*8}))
  );

  // ---------------- Render ----------------
  return (
    <div className='font-sans max-w-6xl mx-auto p-6'>
      <h1 className='text-3xl font-semibold mb-1'>AI Sports Coach — Competition Build</h1>
      <p className='opacity-70 mb-4'>End-to-end workflow • voice chat • sessions • context-aware answers • regimen • video analysis • goals/diary • dashboard.</p>

      <div className='flex gap-2 mb-4 flex-wrap'>
        {['Ask Coach','Training Regimen','Video','Goals','Diary','Dashboard'].map(t=> (
          <Tab key={t} label={t} active={tab===t} onClick={()=>setTab(t)} />
        ))}
        <div className='ml-auto flex items-center gap-2'>
          <select className='border rounded-2xl p-2' value={playerId} onChange={e=>setPlayerId(e.target.value)}>
            {PLAYERS.map(p=> <option key={p.id} value={p.id}>{p.name} — {p.position}</option>)}
          </select>
        </div>
      </div>

      {tab==='Ask Coach' && (
        <div className='grid grid-cols-12 gap-4'>
          {/* Sessions list */}
          <div className='col-span-3 border rounded-2xl p-3 h-[560px] flex flex-col'>
            <div className='font-semibold mb-2'>Sessions</div>
            <div className='space-y-2 overflow-auto'>
              {sessions.map(s=> (
                <div key={s.id} onClick={()=>setActiveSessionId(s.id)} className={'p-2 rounded-xl border cursor-pointer '+(activeSessionId===s.id?'bg-black text-white':'')}>{s.title}</div>
              ))}
            </div>
            <button className='mt-auto px-3 py-2 rounded-xl border' onClick={newSession}>+ New session</button>
          </div>

          {/* Chat area */}
          <div className='col-span-9 border rounded-2xl h-[560px] flex flex-col'>
            <div className='p-3 border-b flex items-center gap-2'>
              <label className='text-sm'>Persona</label>
              <select multiple value={activeSession.persona} onChange={e=>updatePersona(Array.from(e.target.selectedOptions).map(o=>o.value))} className='border rounded-xl p-1'>
                {PERSONAS.map(p=>(<option key={p} value={p}>{p}</option>))}
              </select>
              <label className='ml-4 text-sm flex items-center gap-2'><input type='checkbox' checked={activeSession.speaking} onChange={toggleSpeaking}/> Speaking mode</label>
              <span className='opacity-60 text-xs ml-auto'>ASR: {engine} · Context: goals + diary + readiness + history</span>
            </div>

            <div className='flex-1 overflow-auto p-4 space-y-3'>
              {activeSession.messages.map((m,i)=> (
                <div key={i} className={'max-w-[80%] p-3 rounded-2xl '+(m.role==='user'?'ml-auto bg-gray-100':'bg-white border')}>
                  <div className='opacity-60 text-xs mb-1'>{m.role==='user'?'You':'Coach'}</div>
                  <div>{m.text}</div>
                </div>
              ))}
              {!activeSession.messages.length && <div className='opacity-60 text-sm'>Ask anything to get started. Your goals and diary will be used for context.</div>}
            </div>

            <div className='p-3 border-t flex items-center gap-2'>
              <input className='border rounded-2xl p-2 flex-1' value={chatInput} onChange={e=>setChatInput(e.target.value)} placeholder='Ask the coach…' />
              <button className='px-4 py-2 rounded-2xl border' onClick={sendChat}>Send</button>
              <button className='px-4 py-2 rounded-2xl border' onClick={()=> listening ? stop() : listen(setChatInput)}>{listening?'⏹️ Stop':'🎙️ Speak'}</button>
            </div>
          </div>
        </div>
      )}

      {tab==='Training Regimen' && (()=>{ const r=buildRegimen(); return (
        <div className='grid md:grid-cols-2 gap-4'>
          <Card title='This week plan'>
            <table className='w-full text-sm'>
              <thead><tr><th className='text-left'>Day</th><th className='text-left'>Focus</th><th className='text-left'>Volume</th></tr></thead>
              <tbody>{r.plan.map((d,i)=>(<tr key={i}><td>{d.day}</td><td>{d.focus}</td><td>{Math.round(d.volume*100)}%</td></tr>))}</tbody>
            </table>
          </Card>
          <Card title='Recommended drills (from agents + context)'>
            <ul className='list-disc pl-5'>{r.drills.map((d,i)=>(<li key={i}>{d}</li>))}</ul>
            <div className='opacity-70 text-xs mt-2'>Derived using performance trends, readiness, and your goals/diary.</div>
          </Card>
        </div>
      ); })()}

      {tab==='Video' && (
        <div className='p-4 border rounded-2xl shadow-sm'>
          <div className='grid md:grid-cols-2 gap-4'>
            <div>
              <div className='font-semibold mb-2'>Technique check</div>
              <input type='file' accept='video/*' ref={fileRef} />
              <div className='mt-2 flex gap-2'>
                <input className='border rounded-xl p-2' value={location} onChange={e=>setLocation(e.target.value)} placeholder='Location (e.g., Chicago)'/>
                <select className='border rounded-xl p-2' value={weather} onChange={e=>setWeather(e.target.value)}>
                  <option>Mild (75°F)</option>
                  <option>Hot (83°F)</option>
                  <option>Cold (45°F)</option>
                </select>
                <button className='px-3 py-2 rounded-xl border' onClick={analyzeVideo}>Analyze</button>
              </div>
            </div>
            <div>
              <div className='font-semibold mb-2'>Findings</div>
              {videoResult? (
                <>
                  <div className='mb-1 text-sm opacity-70'>Context: {videoResult.location} · {videoResult.weather}</div>
                  <div className='mt-1'><b>Issues</b><ul className='list-disc pl-5'>{videoResult.issues.map((x,i)=><li key={i}>{x}</li>)}</ul></div>
                  <div className='mt-1'><b>Positives</b><ul className='list-disc pl-5'>{videoResult.positives.map((x,i)=><li key={i}>{x}</li>)}</ul></div>
                  <div className='mt-1'><b>Alternative exercises</b><ul className='list-disc pl-5'>{videoResult.alternatives.map((x,i)=><li key={i}>{x}</li>)}</ul></div>
                </>
              ) : <div className='opacity-60 text-sm'>Upload a clip and analyze to see feedback.</div>}
            </div>
          </div>
        </div>
      )}

      {tab==='Goals' && (
        <div className='p-4 border rounded-2xl shadow-sm'>
          <div className='grid md:grid-cols-2 gap-4'>
            <div>
              <div className='font-semibold mb-2'>Add goal</div>
              <div className='flex gap-2 mb-2'>
                <select className='border rounded-xl p-2' value={newGoalCat} onChange={e=>setNewGoalCat(e.target.value)}>
                  <option value='speed'>Speed</option>
                  <option value='passing'>Passing</option>
                  <option value='stamina'>Stamina</option>
                  <option value='finishing'>Finishing</option>
                </select>
                <input className='border rounded-xl p-2 flex-1' value={newGoal} onChange={e=>setNewGoal(e.target.value)} placeholder='e.g., 31 km/h by Sep 1' />
                <button className='px-3 py-2 rounded-xl border' onClick={addGoalItem}>Add</button>
              </div>
            </div>
            <div>
              <div className='font-semibold mb-2'>Goals by category</div>
              {Object.entries(groupedGoals).map(([cat,arr])=> (
                <div key={cat} className='mb-2'>
                  <div className='font-semibold capitalize'>{cat}</div>
                  <ul className='list-disc pl-5'>{arr.map(g=> (<li key={g.id}>{g.text} <span className='opacity-50 text-xs'>({g.created})</span></li>))}</ul>
                </div>
              ))}
              {Object.keys(groupedGoals).length===0 && <div className='opacity-60 text-sm'>No goals yet.</div>}
            </div>
          </div>
        </div>
      )}

      {tab==='Diary' && (
        <div className='p-4 border rounded-2xl shadow-sm'>
          <div className='font-semibold mb-2'>Add log</div>
          <div className='flex gap-2 mb-4'>
            <select className='border rounded-xl p-2' value={entryType} onChange={e=>setEntryType(e.target.value)}>
              <option value='training'>Training</option>
              <option value='eating'>Eating</option>
              <option value='sleep'>Sleep</option>
              <option value='recovery'>Recovery</option>
            </select>
            <input className='border rounded-xl p-2 flex-1' value={entryText} onChange={e=>setEntryText(e.target.value)} placeholder='e.g., Easy 30min jog, RPE 4' />
            <button className='px-3 py-2 rounded-xl border' onClick={addDiaryItem}>Log</button>
          </div>
          <div className='font-semibold mb-2'>Logs by date</div>
          {Object.entries(groupedDiary).map(([date,items])=> (
            <div key={date} className='mb-2'>
              <div className='font-semibold'>{date}</div>
              <ul className='list-disc pl-5'>{items.map(it=> (<li key={it.id}><span className='opacity-60 text-xs mr-1'>[{it.type}]</span>{it.text}</li>))}</ul>
            </div>
          ))}
        </div>
      )}

      {tab==='Dashboard' && (
        <div className='grid gap-4'>
          <div className='flex items-center gap-3'>
            <label className='px-3 py-2 rounded-xl border cursor-pointer'>⬆️ Upload health data (Fitbit CSV)
              <input type='file' accept='.csv' className='hidden' onChange={onUploadHealth}/>
            </label>
            <select className='border rounded-xl p-2' value={period} onChange={e=>setPeriod(e.target.value)}>
              <option value='week'>Last 7 days</option>
              <option value='month'>Last 30 days</option>
            </select>
          </div>

          {/* Tiles */}
          <div className='grid md:grid-cols-3 gap-4'>
            <Card title='Performance (last 3)'>
              {(()=>{ const p=performanceAgent(player).facts.performance; return (<>
                <KeyVal label='Avg Speed' value={`${p.speed_avg} km/h`} />
                <KeyVal label='Accel' value={`${p.accel_avg} m/s²`} />
                <KeyVal label='xG' value={p.xg_avg} />
                <KeyVal label='Pass %' value={p.pass_pct} />
              </>); })()}
            </Card>
            <Card title='Readiness'>
              <KeyVal label='Sleep' value={readiness.sleep_score} />
              <KeyVal label='HR Rest' value={readiness.hr_rest} />
              <KeyVal label='HRV' value={readiness.hrv} />
              <KeyVal label='Fatigue' value={readiness.fatigue} />
              <div className='mt-2'><Gauge value={readiness.sleep_score} max={100} /></div>
            </Card>
            <Card title='Persona'>
              <div className='text-sm opacity-80'>Active in chat: {activeSession.persona.join(', ')}</div>
            </Card>
          </div>

          {/* Timeline charts */}
          <div className='grid md:grid-cols-2 gap-4'>
            <Card title='Sleep (h)'><Spark values={timeline.map(r=>r.sleep)} /></Card>
            <Card title='Stress'><Spark values={timeline.map(r=>r.stress)} /></Card>
            <Card title='Steps'><Spark values={timeline.map(r=>r.steps)} /></Card>
            <Card title='Cardio score'><Spark values={timeline.map(r=>r.cardio)} /></Card>
            <Card title='Active zone (min)'><Spark values={timeline.map(r=>r.active)} /></Card>
            <Card title='Distance (km)'><Spark values={timeline.map(r=>r.dist)} /></Card>
            <Card title='Calories'><Spark values={timeline.map(r=>r.cal)} /></Card>
          </div>
        </div>
      )}

      <footer className='mt-6 opacity-60 text-xs'>Tip: set window.__VITE_API__ to your FastAPI base URL to enable ElevenLabs voice streaming. Otherwise, the app uses browser speech synthesis.</footer>
    </div>
  );
}
