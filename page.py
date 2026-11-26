# The web page, embedded so it always ships with the serverless function.
HTML = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Heart Disease Model Demo</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600&family=Public+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{--bg:#EEF1F5;--sf:#fff;--ink:#1B2238;--mu:#5A6479;--ln:#CBD3E0;--ac:#2F6FA8;--wb:#FFF4D6;--wi:#5C4300;--wl:#E3C363;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#141A2B;--sf:#1E2640;--ink:#EAEEF7;--mu:#A3ADC4;--ln:#36415F;--ac:#6FAEE6;--wb:#3A3012;--wi:#F2DFA0;--wl:#7A6824;color-scheme:dark}}
:root[data-theme=dark]{--bg:#141A2B;--sf:#1E2640;--ink:#EAEEF7;--mu:#A3ADC4;--ln:#36415F;--ac:#6FAEE6;--wb:#3A3012;--wi:#F2DFA0;--wl:#7A6824;color-scheme:dark}
*,*::before,*::after{box-sizing:inherit}html{scroll-padding-top:env(safe-area-inset-top,0px)}
body{margin:0;background:var(--bg);color:var(--ink);font:400 16px/1.5 "Public Sans",system-ui,sans-serif}
main{max-width:980px;margin:0 auto;padding:24px 20px 48px}
header{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
h1{font:600 clamp(24px,4vw,34px)/1.15 Fraunces,Georgia,serif;margin:0}h2{font:600 18px Fraunces,Georgia,serif;margin:0 0 12px}
.warn{background:var(--wb);color:var(--wi);border:1px solid var(--wl);border-radius:10px;padding:12px 14px;margin:16px 0 0;font-size:15px}
nav{display:flex;gap:6px;margin:18px 0;border-bottom:1px solid var(--ln);overflow-x:auto}
nav button{border:0;border-bottom:3px solid transparent;border-radius:0;padding:10px 14px;color:var(--mu);white-space:nowrap}
nav button[aria-selected=true]{color:var(--ink);border-color:var(--ac)}
button,select,input{font:500 14px "Public Sans",sans-serif;color:var(--ink)}
button{background:transparent;border:1px solid var(--ln);border-radius:8px;padding:8px 12px;cursor:pointer}button:hover{border-color:var(--ink)}
select,input[type=number]{background:var(--sf);border:1px solid var(--ln);border-radius:8px;padding:7px 8px}
:focus-visible{outline:3px solid var(--ac);outline-offset:2px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}@media(max-width:760px){.grid{grid-template-columns:1fr}}
.panel{background:var(--sf);border:1px solid var(--ln);border-radius:14px;padding:20px;margin-bottom:20px}
.row{margin-bottom:12px}.row label{display:flex;justify-content:space-between;align-items:center;font-weight:500;margin-bottom:4px;gap:8px}
.row input[type=number]{width:84px;text-align:right}input[type=range]{width:100%;accent-color:var(--ac);height:26px}.row select{width:110px}
.big{font:600 clamp(40px,8vw,56px)/1 Fraunces,Georgia,serif;margin:6px 0}.mu{color:var(--mu);font-size:14px}.err{color:#C0392B}
.track{position:relative;height:14px;background:var(--bg);border-radius:7px;margin:18px 0 6px}.fill{height:100%;border-radius:7px;background:var(--ac);transition:width .3s}
.mark{position:absolute;top:-6px;width:2px;height:26px;background:var(--ink)}
.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:14px;font-variant-numeric:tabular-nums}
th,td{padding:7px 10px;border-bottom:1px solid var(--ln);text-align:right;white-space:nowrap}th:first-child,td:first-child{text-align:left}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin-bottom:16px}.card{border:1px solid var(--ln);border-radius:10px;padding:12px}
.card b{display:block;font:600 26px Fraunces,Georgia,serif}.drop{border:2px dashed var(--ln);border-radius:12px;padding:20px;text-align:center}
svg{max-width:100%;height:auto}ul.w{margin:8px 0 0;padding-left:20px}
</style></head><body><main>
<header><h1>Heart disease model demo</h1><button id="theme" type="button" aria-label="Toggle light or dark theme">Theme</button></header>
<div class="warn" role="note"><b>Demonstration only, not medical advice.</b> This model was trained on a synthetic dataset and performs no better than guessing (see the Model report tab). Never use it to make decisions about anyone’s health.</div>
<nav role="tablist" id="tabs"></nav>

<section id="t-predict"><div class="grid">
 <div class="panel"><h2>Patient details</h2><div id="inputs"></div></div>
 <div class="panel" aria-live="polite"><h2>Model output</h2><div class="mu">Estimated probability of heart disease</div>
  <div class="big" id="pct">–</div><div class="track"><div class="fill" id="fill" style="width:0"></div><div class="mark" id="mark"></div></div>
  <div class="mu" id="cmp"></div><ul class="w mu" id="warns"></ul>
  <p class="mu" style="margin-top:16px">The black marker is the dataset’s overall rate. Because the model has almost no real signal, its estimates stay close to it.</p></div>
</div></section>

<section id="t-batch" hidden><div class="panel"><h2>Batch prediction</h2>
 <div class="drop"><p style="margin-top:0">Upload a CSV with columns <code>age, sex, blood_pressure, cholesterol, bmi, smoker, diabetes, physical_activity, family_history, stress_level</code>.<br><span class="mu">Sex is Male or Female, the other three are Yes or No. Up to 1,000 rows.</span></p>
 <input type="file" id="file" accept=".csv,text/csv" aria-label="CSV file"> <button type="button" id="demo">Try sample data</button></div>
 <p id="bmsg" class="mu" role="status"></p><div class="scroll" id="btab"></div><p><button type="button" id="dl" hidden>Download results (CSV)</button></p></div></section>

<section id="t-model" hidden><div class="panel"><h2>Model report</h2><div id="info" class="mu">Loading…</div></div></section>
</main>
<script>
const NUM=[["age","Age (years)",30,79,55,1],["blood_pressure","Blood pressure (mmHg)",90,179,130,1],["cholesterol","Cholesterol (mg/dL)",150,299,220,1],["bmi","BMI",18,40,29,.1],["physical_activity","Physical activity (0–4)",0,4,2,1],["stress_level","Stress level (1–9)",1,9,5,1]];
const CAT=[["sex","Sex",["Female","Male"]],["smoker","Smoker",["No","Yes"]],["diabetes","Diabetes",["No","Yes"]],["family_history","Family history",["No","Yes"]]];
const KEYS=[...NUM.map(n=>n[0]),...CAT.map(c=>c[0])];
const $=id=>document.getElementById(id);let lastBatch=[],tok=0,timer;
const T=[["predict","Predict"],["batch","Batch CSV"],["model","Model report"]];
T.forEach(([id,n],i)=>{const b=document.createElement("button");b.type="button";b.role="tab";b.textContent=n;b.id="tab-"+id;b.setAttribute("aria-selected",i==0);
 b.onclick=()=>{T.forEach(([k])=>{$("t-"+k).hidden=k!=id;$("tab-"+k).setAttribute("aria-selected",k==id)});if(id=="model")info()};$("tabs").appendChild(b)});
$("theme").onclick=()=>{const d=document.documentElement,dark=(d.dataset.theme||(matchMedia("(prefers-color-scheme:dark)").matches?"dark":"light"))=="dark";d.dataset.theme=dark?"light":"dark"};

const el={};
NUM.forEach(([k,l,lo,hi,d,s])=>{const r=document.createElement("div");r.className="row";
 r.innerHTML=`<label for="n_${k}">${l}<input type="number" id="n_${k}" step="${s}" value="${d}"></label><input type="range" id="r_${k}" min="${lo}" max="${hi}" step="${s}" value="${d}" aria-label="${l} slider">`;
 $("inputs").appendChild(r);const n=r.querySelector("[type=number]"),g=r.querySelector("[type=range]");el[k]=n;
 g.oninput=()=>{n.value=g.value;go()};n.oninput=()=>{g.value=n.value;go()}});
CAT.forEach(([k,l,o])=>{const r=document.createElement("div");r.className="row";
 r.innerHTML=`<label for="s_${k}">${l}<select id="s_${k}">${o.map(v=>`<option>${v}</option>`).join("")}</select></label>`;$("inputs").appendChild(r);el[k]=r.querySelector("select");el[k].onchange=go});
const go=()=>{clearTimeout(timer);timer=setTimeout(update,80)};
async function post(url,body){const r=await fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});const j=await r.json();if(!r.ok)throw new Error(j.error||"Request failed");return j}
async function update(){const t=++tok,b=Object.fromEntries(KEYS.map(k=>[k,el[k].value]));let o;
 try{o=await post("/predict",b)}catch(e){$("pct").textContent="–";$("cmp").textContent=e.message;$("cmp").className="err";$("warns").innerHTML="";return}
 if(t!=tok)return;const p=o.probability*100,d=(o.probability-o.base_rate)*100;
 $("pct").textContent=p.toFixed(1)+"%";$("fill").style.width=p+"%";$("mark").style.left=o.base_rate*100+"%";$("cmp").className="mu";
 $("cmp").textContent=`${Math.abs(d).toFixed(1)} points ${d>=0?"above":"below"} the dataset average of ${(o.base_rate*100).toFixed(1)}%`;
 $("warns").innerHTML=o.warnings.map(w=>`<li>${w}</li>`).join("")}

function parse(t){const ln=t.trim().split(/\r?\n/).map(l=>l.split(",").map(s=>s.trim().replace(/^"|"$/g,"")));
 const h=ln[0].map(s=>s.toLowerCase().replace(/[\s.]+/g,"_")),ix=KEYS.map(k=>h.indexOf(k));if(ix.some(i=>i<0))return null;
 return ln.slice(1).filter(r=>r.length>=h.length&&r.some(c=>c)).map(r=>Object.fromEntries(KEYS.map((k,j)=>[k,r[ix[j]]])))}
async function runBatch(text){const m=$("bmsg"),rows=parse(text);m.className="mu";
 if(!rows||!rows.length){m.className="err";m.textContent="Couldn’t find all ten columns. Check the header names.";return}
 try{const o=await post("/predict_batch",{rows});lastBatch=rows.map((r,i)=>[...KEYS.map(k=>r[k]),o.results[i].probability]);
  const avg=lastBatch.reduce((a,r)=>a+r[10],0)/lastBatch.length;m.textContent=`${rows.length} rows scored. Average estimated probability: ${(avg*100).toFixed(1)}%.`+(rows.length>200?" Showing the first 200.":"");
  $("btab").innerHTML=`<table><thead><tr><th>#</th>${KEYS.map(k=>`<th>${k.replace(/_/g," ")}</th>`).join("")}<th>probability</th></tr></thead><tbody>`+
   lastBatch.slice(0,200).map((r,i)=>`<tr><td>${i+1}</td>${r.slice(0,10).map(v=>`<td>${v}</td>`).join("")}<td><b>${(r[10]*100).toFixed(1)}%</b></td></tr>`).join("")+"</tbody></table>";$("dl").hidden=false}
 catch(e){m.className="err";m.textContent=e.message}}
$("file").onchange=e=>{const f=e.target.files[0];if(f)f.text().then(runBatch)};
$("demo").onclick=()=>runBatch(["age,sex,blood_pressure,cholesterol,bmi,smoker,diabetes,physical_activity,family_history,stress_level","68,Male,105,191,38.0,Yes,Yes,0,No,2","58,Female,97,249,22.0,Yes,Yes,0,No,4","44,Female,93,190,23.2,No,Yes,0,No,8","72,Male,93,183,39.4,No,No,3,Yes,1","37,Female,145,166,22.0,No,Yes,4,Yes,1"].join("\n"));
$("dl").onclick=()=>{const csv=[...KEYS,"probability"].join(",")+"\n"+lastBatch.map(r=>r.join(",")).join("\n");const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv"}));a.download="heart_model_predictions.csv";a.click()};

let loaded=false;async function info(){if(loaded)return;try{const i=await (await fetch("/api/info")).json(),pc=v=>(v*100).toFixed(1)+"%",t=i.test;loaded=true;$("info").className="";
 const ef=i.effects,mx=Math.max(...ef.map(e=>Math.max(Math.abs(e.lo),Math.abs(e.hi)))),W=560,X=v=>280+v/mx*250;
 const svg=`<svg viewBox="0 0 ${W} ${ef.length*26+10}" role="img" aria-label="Effect of each feature with 95% confidence interval"><line x1="280" x2="280" y1="0" y2="${ef.length*26+6}" style="stroke:var(--mu)"/>`+
  ef.map((e,k)=>{const y=k*26+14,sig=e.lo>0||e.hi<0;return `<text x="0" y="${y+4}" font-size="12" style="fill:var(--ink)">${e.name.replace(/_/g," ")}</text><line x1="${X(e.lo)}" x2="${X(e.hi)}" y1="${y}" y2="${y}" stroke-width="2" style="stroke:var(--${sig?"ac":"mu"})"/><circle cx="${X(e.coef)}" cy="${y}" r="4.5" style="fill:var(--${sig?"ac":"mu"})"/>`}).join("")+"</svg>";
 $("info").innerHTML=`<p style="color:var(--ink)"><b>Bottom line:</b> on ${t.confusion.flat().reduce((a,b)=>a+b)} patients the model never saw, it scored ${pc(t.accuracy)} against ${pc(t.baseline)} for always answering “yes”. Its AUC of ${t.auc.toFixed(2)} is what pure chance gives (0.50). The features in this dataset do not predict the outcome, which is typical of synthetic data with randomly assigned labels.</p>
 <div class="cards"><div class="card"><b>${pc(t.accuracy)}</b>Test accuracy<br><span class="mu">95% range ${pc(t.ci[0])} to ${pc(t.ci[1])}</span></div><div class="card"><b>${pc(t.baseline)}</b>Guess-the-majority baseline</div><div class="card"><b>${t.auc.toFixed(3)}</b>Test AUC<br><span class="mu">0.5 = coin flip</span></div></div>
 <h2>Cross-validation on ${i.n_train} training patients</h2><div class="scroll"><table><thead><tr><th>Model</th><th>Accuracy</th><th>AUC</th></tr></thead><tbody>${i.models.map(m=>`<tr><td>${m.name}</td><td>${pc(m.acc)} ± ${(m.acc_sd*100).toFixed(1)}</td><td>${m.auc.toFixed(3)} ± ${m.auc_sd.toFixed(3)}</td></tr>`).join("")}</tbody></table></div>
 <h2 style="margin-top:20px">Confusion matrix (test set)</h2><div class="scroll"><table><thead><tr><th>Actual ↓ / Predicted →</th><th>No disease</th><th>Disease</th></tr></thead><tbody><tr><td>No disease</td><td>${t.confusion[0][0]}</td><td>${t.confusion[0][1]}</td></tr><tr><td>Disease</td><td>${t.confusion[1][0]}</td><td>${t.confusion[1][1]}</td></tr></tbody></table></div>
 <h2 style="margin-top:20px">Effect of each feature</h2><div class="scroll">${svg}</div>
 <p>Dots show each feature’s weight in the model, lines show a 95% range from 300 resamples. Lines crossing the centre mean no reliable effect. Only <b>smoker</b> clears zero, but it is the best of ${i.n_tests} features tested (p = ${i.best_p.toFixed(3)}), and with that many comparisons one such result is expected by chance (the stricter cut-off would be ${i.bonferroni.toFixed(3)}).</p>
 <p>The model is logistic regression on ${i.n_total} patients. I chose it because nothing beat it, and a simple model is the honest choice when there is no signal to find.</p>`}catch(e){$("info").textContent="Couldn’t load the model report."}}
update();
</script></body></html>
"""
