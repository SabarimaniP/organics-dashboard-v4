import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
cube = open(os.path.join(HERE, "_cube.json"), encoding="utf-8").read()
OUT = os.environ.get("FUNNEL_OUT") or os.path.join(BASE, "Organics_Dashboard.html")

HTML = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Organics Dashboard</title>
<style>
:root{
  --navy:#0b2545; --navy2:#13315c; --navy3:#1d4373; --soft:#5b6b82; --line:#e3e8ef;
  --bg:#f4f6f9; --surface:#ffffff; --ink:#1c2b3a;
  --green:#107c41; --g1:#6cc096; --g2:#1f8f5c; --g3:#0a5730; --grey:#b9c2ce;
  --red:#c0392b; --amber:#fab219; --chip:#eef2f7;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:14px;line-height:1.5}
.wrap{max-width:1400px;margin:0 auto;padding:24px 20px 70px}
header{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
h1{font-size:21px;color:var(--navy);margin:0;letter-spacing:-.01em}
.badge{font-size:11px;font-weight:700;padding:3px 9px;border-radius:99px;background:var(--chip);color:var(--navy2)}
.sub{color:var(--soft);font-size:12.5px;margin:4px 0 18px}.sub b{color:var(--ink)}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin-bottom:14px}
.controls{display:flex;gap:16px;flex-wrap:wrap;align-items:flex-end}
.ctl{display:flex;flex-direction:column;gap:5px}
.ctl label{font-size:10.5px;text-transform:uppercase;letter-spacing:.05em;color:var(--soft);font-weight:700}
select{font:inherit;font-size:13px;color:var(--ink);background:#fbfcfe;border:1.5px solid var(--line);border-radius:7px;padding:7px 10px;min-width:150px}
.seg{display:inline-flex;border:1.5px solid var(--navy2);border-radius:7px;overflow:hidden}
.seg button{font:inherit;font-size:12.5px;border:0;background:#fff;color:var(--navy2);padding:7px 15px;cursor:pointer;font-weight:600}
.seg button[aria-pressed="true"]{background:var(--navy2);color:#fff}
.seg button:disabled{opacity:.4;cursor:not-allowed}
nav.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}
nav.tabs button{font:inherit;font-size:13.5px;font-weight:600;padding:9px 16px;border-radius:7px;
  border:1.5px solid var(--navy2);background:#fff;color:var(--navy2);cursor:pointer}
nav.tabs button[aria-selected="true"]{background:var(--navy2);color:#fff}
.panelbox{display:none}.panelbox.on{display:block}
h2{font-size:14px;margin:0 0 3px;color:var(--navy)}
.hint{font-size:12px;color:var(--soft);margin:0 0 13px;font-style:italic}
.two{display:grid;gap:14px}@media(min-width:1000px){.two{grid-template-columns:1fr 1fr}}
table{border-collapse:collapse;width:100%;font-size:13px;font-variant-numeric:tabular-nums}
th{background:var(--navy2);color:#fff;padding:9px 8px;text-align:center;font-weight:600;font-size:12px;white-space:nowrap}
th.sub2{background:var(--navy3);font-size:11px;padding:6px 8px}
th.lft,td.lft{text-align:left}
td{padding:8px;text-align:center;border-bottom:1px solid var(--line)}
tr:nth-child(even) td{background:#fafbfd}
td.wk{font-weight:700;color:var(--navy);text-align:left;white-space:nowrap}
td.base{font-weight:700;background:#f2f5f9 !important}
tr.tot td{border-top:2px solid var(--navy2);background:var(--chip) !important;font-weight:700}
.cnt{font-weight:700;display:block}.pct{font-size:10.5px;color:#3d4c60;display:block}
td.dark .cnt,td.dark .pct{color:#fff}
.tblwrap{overflow-x:auto}
.legend{display:flex;align-items:center;gap:9px;font-size:11.5px;color:var(--soft);margin:0 0 11px;flex-wrap:wrap}
.legend .bar{width:110px;height:11px;border-radius:6px;background:linear-gradient(to right,#fff,var(--green));border:1px solid var(--line)}
.fnl td.stage{text-align:left;font-weight:600;color:var(--navy);white-space:nowrap}
.fnl tr.saletop td{border-top:2px solid var(--line)}
.fnl td.stage .hint{font-weight:400;font-style:normal;font-size:11px;color:var(--soft);margin:0}
.fnl td.rev{white-space:nowrap;color:var(--navy);font-variant-numeric:tabular-nums}
.infobtn{font:inherit;font-size:11px;line-height:1;font-weight:700;color:var(--navy2);background:var(--chip);
  border:1px solid var(--line);border-radius:50%;width:16px;height:16px;padding:0;cursor:pointer;vertical-align:middle}
.infobtn:hover{background:var(--navy2);color:#fff;border-color:var(--navy2)}
.infonote{display:none;white-space:normal;font-weight:400;font-size:11.5px;line-height:1.45;color:var(--soft);
  background:var(--chip);border:1px solid var(--line);border-left:3px solid var(--navy2);border-radius:5px;
  padding:7px 9px;margin:6px 0 2px;max-width:330px}
.infonote.on{display:block}
.barwrap{background:var(--chip);border-radius:3px;height:15px;min-width:70px}
.bar{height:100%;border-radius:3px;background:var(--navy2)}
.bar.roll{background:var(--green)}
.step{font-weight:600}.up{color:var(--green)}.down{color:var(--red)}
.finding{border-left:3px solid var(--navy2);padding:1px 0 1px 12px;margin:0 0 12px}
.finding.bad{border-left-color:var(--red)}.finding.good{border-left-color:var(--green)}
.finding p{margin:0;font-size:13.5px}.finding .why{color:var(--soft);font-size:12.5px;margin-top:2px}
.note{font-size:11.5px;color:var(--soft);margin-top:12px;line-height:1.6}.note b{color:var(--ink)}
.sechead{font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--navy);
  background:var(--chip);padding:7px 9px;border-radius:5px;margin:16px 0 9px}
.sechead:first-child{margin-top:0}
.ms{position:relative;display:inline-block}
.msbtn{font:inherit;font-size:11.5px;color:var(--navy2);background:#fbfcfe;border:1.5px solid var(--line);
  border-radius:6px;padding:4px 9px;cursor:pointer;white-space:nowrap;max-width:190px;overflow:hidden;text-overflow:ellipsis}
.msbtn.on{border-color:var(--navy2);background:var(--chip);font-weight:700}
.msmenu{display:none;position:absolute;top:calc(100% + 4px);left:0;z-index:40;background:#fff;
  border:1px solid var(--line);border-radius:8px;box-shadow:0 10px 28px rgba(11,37,69,.18);padding:8px;width:250px}
.msmenu.open{display:block}
.mssearch{width:100%;font:inherit;font-size:12px;padding:5px 7px;border:1px solid var(--line);border-radius:5px;margin-bottom:6px}
.msact{display:flex;gap:6px;margin-bottom:6px}
.msact button{font:inherit;font-size:11px;border:1px solid var(--line);background:#f7f9fb;border-radius:4px;padding:2px 8px;cursor:pointer;color:var(--navy2)}
.msopts{max-height:210px;overflow-y:auto}
.msopts label{display:flex;gap:6px;align-items:center;font-size:12px;padding:3px 2px;cursor:pointer}
.msopts label:hover{background:#f2f5f9;border-radius:4px}
.msopts .none{font-size:11.5px;color:var(--soft);padding:6px 2px}
.cardfilt{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin:0 0 11px}
.cardfilt .lb{font-size:10.5px;text-transform:uppercase;letter-spacing:.04em;color:var(--soft);font-weight:700;margin-right:2px}
#f0 .msbtn,#f1 .msbtn,#f2 .msbtn{font-size:13px;padding:7px 10px;min-width:150px;max-width:220px}
.fhead{font-size:12.5px;color:var(--ink);background:var(--chip);border-radius:6px;padding:9px 12px;margin:0 0 16px;font-variant-numeric:tabular-nums}
.fhead b{color:var(--navy)}
ol.findlist{margin:0;padding:0 0 0 4px;list-style:none;counter-reset:f}
ol.findlist li{counter-increment:f;display:grid;grid-template-columns:26px 1fr;gap:12px;
  align-items:baseline;padding:11px 4px;border-bottom:1px solid var(--line)}
ol.findlist li:last-child{border-bottom:0}
ol.findlist li::before{content:counter(f);font-weight:700;color:var(--navy2);font-size:14px}
.ftext{font-size:13.5px}
.ftext b{color:var(--navy)}
.fsub{display:block;font-size:12px;color:var(--soft);margin-top:2px}
.mssel{font:inherit;font-size:11.5px;color:var(--navy2);background:#fbfcfe;border:1.5px solid var(--line);
  border-radius:6px;padding:4px 7px;min-width:auto}
/* min card width must leave room for the bar: the 4 fixed bkrow columns + gaps + padding come to
   ~197px, so keep the minimum comfortably above that or the 1fr bar collapses to nothing. */
.bkgrid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(252px,1fr))}
.bkcard{border:1px solid var(--line);border-radius:9px;overflow:hidden;background:#fff}
.bkcard h3{margin:0;font-size:12.5px;font-weight:700;color:#fff;background:var(--navy2);
  padding:8px 10px;display:flex;justify-content:space-between;gap:8px;align-items:baseline}
.bkcard h3 span{font-weight:400;font-size:11px;opacity:.85}
/* 4 columns: label | bar | count | step % off the stage above */
.bkrow{display:grid;grid-template-columns:60px 1fr 50px 46px;gap:7px;align-items:center;
  padding:5px 10px;border-bottom:1px solid #f1f4f8;font-size:12px}
.bkrow:last-child{border-bottom:0}
.bkrow .lbl{color:var(--soft)}
.bkrow .n{text-align:right;font-weight:700;font-variant-numeric:tabular-nums}
.bkrow .s{text-align:right;font-size:10.5px;color:var(--green);font-variant-numeric:tabular-nums;font-weight:700}
.bkrow .p{text-align:right;font-size:10.5px;color:#3d4c60;font-variant-numeric:tabular-nums;font-weight:700}
.bkrow .p.up{color:var(--green)}.bkrow .p.down{color:var(--red)}
.bkhead{display:grid;grid-template-columns:60px 1fr 50px 46px;gap:7px;padding:4px 10px 3px;
  font-size:9.5px;letter-spacing:.04em;text-transform:uppercase;color:var(--soft);
  border-bottom:1px solid var(--line);background:#fafbfd}
.bkhead span:nth-child(3),.bkhead span:nth-child(4){text-align:right}
.mini{background:var(--chip);border-radius:2px;height:11px;min-width:34px}
.mini>i{display:block;height:100%;border-radius:2px;background:var(--navy2)}
#tip{position:fixed;pointer-events:none;opacity:0;transition:opacity .08s;z-index:99;background:var(--navy);
  color:#fff;font-size:12px;line-height:1.45;padding:7px 10px;border-radius:6px;box-shadow:0 6px 20px rgba(0,0,0,.28);max-width:300px}
</style></head><body>
<div class="wrap">

<header><h1>Organics Dashboard</h1><span class="badge" id="through"></span></header>

<div class="panel"><div class="controls">
  <div class="ctl"><label for="period">Period</label><select id="period"></select></div>
  <div class="ctl"><label>Lead set</label><div class="seg" id="lens">
    <button data-l="r" aria-pressed="false">Rolling</button>
    <button data-l="c" aria-pressed="true">Cohort</button>
    <button data-l="b" aria-pressed="false">Both</button></div></div>
  <div class="ctl"><label>Source</label><div id="f0"></div></div>
  <div class="ctl"><label>Grade</label><div id="f1"></div></div>
  <div class="ctl"><label>State</label><div id="f2"></div></div>
</div>
</div>

<nav class="tabs" id="tabs">
  <button aria-selected="true" data-t="ov">Overview</button>
  <button aria-selected="false" data-t="wk">Weekly View</button>
  <button aria-selected="false" data-t="mtd">MTD View</button>
  <button aria-selected="false" data-t="cmp">Compare</button>
</nav>

<section class="panelbox on" id="p-ov">
  <div class="two">
    <div class="panel"><h2>Cohort funnel — <span class="pn"></span></h2>
      <div class="cardfilt" id="cfC"></div><div id="fnlC"></div></div>
    <div class="panel"><h2>Rolling funnel — <span class="pn"></span></h2>
      <div class="cardfilt" id="cfR"></div><div id="fnlR"></div></div>
  </div>
  <div class="panel"><h2>Combined — cohort + rolling — <span class="pn"></span></h2>
    <div class="cardfilt" id="cfB"></div><div id="fnlB"></div></div>

  <div class="panel"><div class="sechead">Breakup by source — <span id="ttSrc"></span></div>
    <div class="cardfilt" id="bfSrc"></div>
    <div class="bkgrid" id="bkSrc"></div></div>
  <div class="panel"><div class="sechead">Breakup by grade — <span id="ttGrade"></span></div>
    <div class="cardfilt" id="bfGrade"></div>
    <div class="bkgrid" id="bkGrade"></div></div>
  <div class="panel"><div class="sechead">Breakup by state — <span id="ttState"></span></div>
    <div class="cardfilt" id="bfState"></div>
    <div class="bkgrid" id="bkState"></div></div>
</section>

<section class="panelbox" id="p-wk">
  <div class="panel">
    <nav class="tabs" id="wviews" style="margin:0 0 14px"></nav>
    <div id="wtables"></div>
  </div>
</section>

<section class="panelbox" id="p-mtd">
  <div class="panel">
    <div class="controls" style="margin-bottom:14px">
      <div class="ctl"><label>Columns</label><div class="seg" id="mtdmode">
        <button data-m="mtd" aria-pressed="true">Months (weeks)</button>
        <button data-m="cal" aria-pressed="false">Months (calendar)</button>
        <button data-m="wk" aria-pressed="false">Weekly</button></div></div>
      <div class="ctl"><label>Break down by</label><div class="seg" id="mtdbrk">
        <button data-b="none" aria-pressed="true">Total only</button>
        <button data-b="0" aria-pressed="false">Source</button>
        <button data-b="1" aria-pressed="false">Grade</button>
        <button data-b="2" aria-pressed="false">State</button></div></div>
      <div class="ctl" id="brkmwrap"><label for="brkm">Breakup shows</label><select id="brkm"></select></div>
    </div>
    <div id="mtdbody"></div>
  </div>
</section>

<section class="panelbox" id="p-cmp">
  <div class="panel">
    <div class="controls" style="margin-bottom:16px">
      <div class="ctl"><label for="cA">A</label><select id="cA"></select></div>
      <div class="ctl"><label for="cB">B</label><select id="cB"></select></div>
    </div>
    <div id="cmpbody"></div>
  </div>
</section>

</div><div id="tip"></div>

<script>
const CUBE=__CUBE__;
const WEEKS=CUBE.weeks, MONTHS=CUBE.months, DIMS=CUBE.dims, DEN=CUBE.den, ROWS=CUBE.rows;
const NW=WEEKS.length, BUCK=CUBE.buckets, SPD=CUBE.speed, ELAPSED=CUBE.elapsed;
/* the calendar timeline: real dates, 1st of the month to month end or to today */
const CALM=(CUBE.calMonths||[]);
const BSTART=[0,4,8,15,31,61], SSTART=[0,4,8];
/* row: 0 dim 1 cmonth 2 cwk 3 assigned | 4 firstCall 5 secondCall 6 firstAns 7 firstDemo 8 firstDc
        9 saleWk | 10 callMask 11 ansMask 12 dbMask 13 dcMask | 14..17 ageing buckets | 18 speed */
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const fmt=n=>Math.round(n).toLocaleString('en-IN');
const pc=(a,b)=>b>0?100*a/b:0,p1=v=>v.toFixed(1)+'%',p2=v=>v.toFixed(2)+'%';
/* money in lakh/crore - 40L reads faster than 4,007,364 in a funnel cell. inrFull keeps the exact
   rupee figure for the tooltip, so nothing is lost to rounding. */
const inr=n=>{n=Math.round(n||0);
  if(n>=1e7)return'₹'+(n/1e7).toFixed(2).replace(/\.00$/,'')+'Cr';
  if(n>=1e5)return'₹'+(n/1e5).toFixed(1).replace(/\.0$/,'')+'L';
  return'₹'+n.toLocaleString('en-IN');};
const inrFull=n=>'₹'+Math.round(n||0).toLocaleString('en-IN');
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const has=(m,b)=>((m>>b)&1)===1;
const STAGES=[['leads','Leads created'],['assigned','Lead assigned'],['called','Called'],
  ['answered','Answered'],['db','Demo booked'],['dc','Demo conducted'],['sale','Sale']];
const FLAB=['Source','Grade','State'];
let PKEY='m7',LENS='c',WVIEW=0,MTDMODE='mtd',MTDBRK='none',BRKM='leads';

/* ---------------- filters ---------------- */
const OPTS=FLAB.map((_,i)=>[...new Set(DIMS.map(d=>d[i]))].sort((a,b)=>
  a==='Blank/Unknown'?1:b==='Blank/Unknown'?-1:a.localeCompare(b)));
/* SEL = the global filter (scopes every tab). CSEL = one extra filter per funnel card so each box
   can be sliced on its own. A card's effective mask is global AND card. */
const SEL=[null,null,null];
const CSEL={c:[null,null,null],r:[null,null,null],b:[null,null,null]};
/* each breakup section carries its own lens and its own filters on the OTHER two dimensions */
const BSEL={0:{lens:'c',sel:[null,null,null],pkey:null},
            1:{lens:'c',sel:[null,null,null],pkey:null},
            2:{lens:'c',sel:[null,null,null],pkey:null}};
const okv=(sel,v)=>!sel||sel.has(v);
const buildMask=extra=>DIMS.map(d=>d.every((v,i)=>okv(SEL[i],v)&&okv(extra&&extra[i],v)));
let DIMOK=[];
const computeDimOK=()=>DIMOK=buildMask(null);

/* ---------------- period ---------------- */
function ctx(k){
  if(k[0]==='c'){const M=CALM.find(x=>x.id===+k.slice(1));
    return {kind:'cm',m:M.id,label:M.name+(M.complete?'':' to date'),range:M.from+' \u2013 '+M.to,
            complete:M.complete,weeks:WEEKS.filter(w=>w.month===M.id).map(w=>w.id),
            roll:'the two calendar months before',rollMonths:M.rollMonths};}
  if(k[0]==='m'){const m=MONTHS.find(x=>x.id===+k.slice(1));
    return {kind:'m',m:m.id,label:m.name,range:m.range,weeks:m.weeks,roll:m.roll,rollMonths:m.rollMonths};}
  const w=+k.slice(1),W=WEEKS[w-1],m=MONTHS.find(x=>x.id===W.month);
  return {kind:'w',w,m:W.month,label:W.label,range:W.range,weeks:[w],roll:m.roll,rollMonths:m.rollMonths};
}
/* cohort = created inside the period. rolling = created in the two months before the period's month,
   or earlier in the same month when a single week is selected. everything older = outside. */
function memb(cm,cwk,C){
  if(C.kind==='cm'){                          /* calendar: created in the month = cohort */
    if(cm===C.m) return 1;
    if(C.rollMonths.includes(cm)) return 2;
    return 3;}
  if(cwk&&C.weeks.includes(cwk)) return 1;
  if(C.rollMonths.includes(cm)) return 2;
  if(C.kind==='w'&&cm===C.m&&cwk>0&&cwk<C.w) return 2;
  return 3;
}
const bitsOf=C=>C.weeks.reduce((a,w)=>a|(1<<w),0);
/* a week-group period reads the week masks (10-13, sale week 9); a calendar period reads the
   calendar-month masks (19-22, sale month 23). Same counting rule, different clock. */
const CAL=C=>C.kind==='cm';
const PBITS=C=>CAL(C)?(1<<C.m):bitsOf(C);
const FLD=C=>CAL(C)?[19,20,21,22]:[10,11,12,13];
const SALEIN=(r,C)=>CAL(C)?r[23]===C.m:!!(r[9]&&C.weeks.includes(r[9]));
function bases(C,msk){
  const M=msk||DIMOK;
  const o={1:{leads:0,assigned:0},2:{leads:0,assigned:0}};
  for(const d of DEN){ if(!M[d[2]])continue;
    const g=memb(d[0],d[1],C); if(g!==1&&g!==2)continue;
    o[g].leads+=d[4]; if(d[3])o[g].assigned+=d[4]; }
  return o;
}
function stages(C,msk){
  const M=msk||DIMOK;
  const B=bases(C,M),o={1:{...B[1]},2:{...B[2]},3:{leads:0,assigned:0}};
  /* saleTracked = sales carried by a real lead row. sale = that plus the hand-added ones.
     m0/ref/react/oth are the August sale classes and always sum to saleTracked. */
  [1,2,3].forEach(g=>{o[g].called=o[g].answered=o[g].db=o[g].dc=o[g].sale=o[g].saleTracked
    =o[g].m0=o[g].roll=o[g].react=o[g].refIn=0;
    /* collected revenue, carried per bucket alongside the unit counts. August only - every other
       period leaves these at 0 and the Revenue column renders as a dash. */
    o[g].saleRev=o[g].m0Rev=o[g].rollRev=o[g].reactRev=o[g].refInRev=0;});
  const bits=PBITS(C),F=FLD(C);
  /* The source-pair classification is AUGUST ONLY. Every other period counts sales exactly as it
     always did - straight into the bucket its lead's creation date gives it - and renders a single
     Sale row, because m0/ref/react/oth stay at zero. */
  const AUG=(C.kind==='cm'&&C.m===8);
  for(const r of ROWS){ if(!M[r[0]])continue;
    const g=memb(r[1],r[2],C),x=o[g];
    if(r[F[0]]&bits)x.called++;
    if(r[F[1]]&bits)x.answered++;
    if(r[F[2]]&bits)x.db++;
    if(r[F[3]]&bits)x.dc++;
    if(SALEIN(r,C)&&!AUG){x.sale++;x.saleTracked++;} }
  if(AUG){
    /* AUGUST ONLY - three buckets, straight from the sales sheet: M0 | Rolling | Reactivation.
       M0 is the only fresh-lead bucket so it is the only one that can be cohort; Rolling and
       Reactivation sit on the rolling side. Referral is carried as a subset of Rolling.
       Hand-added sales are NOT applied here: each is already a row in the sheet. */
    /* summed per dimension so the Source / Grade / State filters apply - a flat total would sit
       there unchanged while every other stage went to zero. */
    /* the 4th element is collected revenue, on the same key as the count, so filtering the money
       and filtering the units cannot drift apart */
    let m0=0,rl=0,rc=0,rf=0,m0R=0,rlR=0,rcR=0,rfR=0;
    for(const [d,b,n,rv] of (CUBE.augSaleDim||[])){ if(!M[d])continue;
      const v=rv||0;
      if(b===1){m0+=n;m0R+=v;}
      else if(b===3){rc+=n;rcR+=v;}
      else {rl+=n;rlR+=v; if(b===4){rf+=n;rfR+=v;}} }
    o[1].m0=m0; o[1].sale=o[1].saleTracked=m0;
    o[1].m0Rev=m0R; o[1].saleRev=m0R;
    o[2].roll=rl; o[2].react=rc; o[2].refIn=rf;
    o[2].rollRev=rlR; o[2].reactRev=rcR; o[2].refInRev=rfR;
    o[2].sale=o[2].saleTracked=rl+rc;
    o[2].saleRev=rlR+rcR;
  } else if(C.weeks&&(C.weeks.includes(13)||C.weeks.includes(14)||C.weeks.includes(15))){
    /* week-group views keep the old row-based behaviour, hand-added sales included */
    const H=CUBE.hardcodedAugByClass||{};
    Object.keys(H).forEach(k=>{ o[2].sale+=H[k]; });
  }
  return o;
}
/* sale-class codes, mirrored from build_cube.py */
const CLS={M0:1,REF:2,REACT:3,OTHER:4};
/* the funnel needs the class counters summed alongside the named STAGES */
const SUMK=[...STAGES.map(([k])=>k),'saleTracked','m0','roll','react','refIn',
  'saleRev','m0Rev','rollRev','reactRev','refInRev'];
const both=C=>{const s=stages(C),o={};SUMK.forEach(k=>o[k]=s[1][k]+s[2][k]);return o;};
const cur=C=>{const s=stages(C);return LENS==='c'?s[1]:LENS==='r'?s[2]:both(C);};
const pick=(s,w)=>{ if(w==='c')return s[1]; if(w==='r')return s[2];
  const o={};SUMK.forEach(k=>o[k]=s[1][k]+s[2][k]);return o; };
const tip=$('#tip');
document.addEventListener('mouseover',e=>{const t=e.target.closest('[data-tip]');
  if(!t){tip.style.opacity=0;return;}tip.innerHTML=t.dataset.tip;tip.style.opacity=1;});
document.addEventListener('mousemove',e=>{if(tip.style.opacity!=='1')return;
  tip.style.left=Math.min(e.clientX+14,innerWidth-320)+'px';tip.style.top=Math.max(8,e.clientY-12-tip.offsetHeight)+'px';});
function heat(p,mx){if(!(p>0)||!(mx>0))return{bg:'#fff',dark:false};
  const t=Math.min(1,p/mx);return{bg:`hsl(147 60% ${96-52*t}%)`,dark:t>0.58};}

/* ---------------- searchable, multi-select filter ---------------- */
let MSN=0;
function multiSelect(host,fi,getSel,setSel,onDone){
  const lab=FLAB[fi], opts=OPTS[fi];
  const el=document.createElement('div'); el.className='ms'; el.id='ms'+(MSN++);
  el.innerHTML='<button class="msbtn"></button><div class="msmenu">'
    +'<input class="mssearch" placeholder="Search '+lab.toLowerCase()+'">'
    +'<div class="msact"><button data-a="all">Select all</button><button data-a="clear">Clear</button></div>'
    +'<div class="msopts"></div></div>';
  const menu=el.querySelector('.msmenu'), box=el.querySelector('.msopts'),
        search=el.querySelector('.mssearch'), btn=el.querySelector('.msbtn');
  const paint=()=>{const sel=getSel();
    btn.textContent=(!sel?lab+': All':sel.size===0?lab+': none':sel.size===1?lab+': '+[...sel][0]
      :lab+': '+sel.size+' selected')+' \u25be';
    btn.classList.toggle('on',!!sel);};
  const draw=()=>{const q=search.value.trim().toLowerCase(), sel=getSel();
    const list=opts.filter(o=>!q||o.toLowerCase().includes(q));
    box.innerHTML=list.length?list.map(o=>'<label><input type="checkbox" value="'+esc(o)+'"'
      +((!sel||sel.has(o))?' checked':'')+'>'+esc(o)+'</label>').join('')
      :'<div class="none">nothing matches that search</div>';};
  btn.onclick=e=>{e.stopPropagation();
    const open=menu.classList.contains('open');
    document.querySelectorAll('.msmenu').forEach(m=>m.classList.remove('open'));
    if(!open){menu.classList.add('open');search.value='';draw();search.focus();}};
  menu.onclick=e=>e.stopPropagation();
  search.oninput=draw;
  box.onchange=e=>{const t=e.target; if(!t.matches('input[type=checkbox]'))return;
    let sel=getSel(); if(!sel)sel=new Set(opts);
    if(t.checked)sel.add(t.value); else sel.delete(t.value);
    setSel(sel.size===opts.length?null:sel); paint(); onDone();};
  el.querySelector('.msact').onclick=e=>{const a=e.target.dataset.a; if(!a)return;
    setSel(a==='all'?null:new Set()); draw(); paint(); onDone();};
  host.appendChild(el); paint();
}
document.addEventListener('click',()=>document.querySelectorAll('.msmenu').forEach(m=>m.classList.remove('open')));
const BKEL=['bkSrc','bkGrade','bkState'], BKTT=['ttSrc','ttGrade','ttState'];
function calOptions(){
  return CALM.map(m=>'<option value="c'+m.id+'">'+m.name+' \u00b7 '+m.from+'\u2013'+m.to
    +(m.complete?'':' (to date)')+'</option>').join('');
}
function periodOptions(extraFirst){
  return (extraFirst?'<option value="">Same as above</option>':'')
    +'<optgroup label="Months \u2013 groups of weeks">'
    +MONTHS.map(m=>'<option value="m'+m.id+'">'+m.name+' \u00b7 '+m.range+'</option>').join('')
    +'</optgroup><optgroup label="Months \u2013 calendar dates">'+calOptions()
    +'</optgroup><optgroup label="Weeks">'
    +WEEKS.map(w=>'<option value="w'+w.id+'">'+w.label+' \u00b7 '+w.range+'</option>').join('')
    +'</optgroup>';
}
function breakupControls(hostId,fi){
  const host=$('#'+hostId), B=BSEL[fi];
  host.innerHTML='<span class="lb">This box</span>';
  const per=document.createElement('select');
  per.className='mssel'; per.innerHTML=periodOptions(true); per.value=B.pkey||'';
  per.onchange=()=>{B.pkey=per.value||null; breakup(BKEL[fi],fi);};
  host.appendChild(per);
  const seg=document.createElement('div'); seg.className='seg';
  [['r','Rolling'],['c','Cohort'],['b','Both']].forEach(([v,t])=>{
    const b=document.createElement('button');
    b.textContent=t; b.setAttribute('aria-pressed',String(B.lens===v));
    b.onclick=()=>{B.lens=v;[...seg.children].forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
      breakup(['bkSrc','bkGrade','bkState'][fi],fi);};
    seg.appendChild(b);});
  host.appendChild(seg);
  /* filters for the OTHER two dimensions - splitting by X and filtering X at once is meaningless */
  [0,1,2].filter(x=>x!==fi).forEach(o=>multiSelect(host,o,()=>B.sel[o],v=>B.sel[o]=v,
    ()=>breakup(['bkSrc','bkGrade','bkState'][fi],fi)));
}
function cardFilters(hostId,which){
  const host=$('#'+hostId); host.innerHTML='<span class="lb">Filter this box</span>';
  [0,1,2].forEach(fi=>multiSelect(host,fi,()=>CSEL[which][fi],v=>CSEL[which][fi]=v,()=>overview()));
}

/* ---------------- breakup funnels, one pass per dimension ---------------- */
const TOPN={0:99,1:99,2:8};
/* fixed display order the team asked for; anything unlisted falls in after, and Blank/Unknown last */
const FIXED={0:['IL Website','Learn App','IL Surge'],
             1:['6-10','11-12','1-5','13 (Dropper)','Blank/Unknown'],2:null};
/* the comparison period: a month against the month before, a week against the same-position week
   of the month before (July's 1st week vs June's 1st week, July's last vs June's last) */
function prevKey(C){
  if(C.kind==='cm'){                /* a part-month has no fair baseline, so show none */
    if(!C.complete) return null;
    const j=CALM.findIndex(x=>x.id===C.m);
    return j<=0?null:'c'+CALM[j-1].id;}
  const i=MONTHS.findIndex(m=>m.id===C.m);
  if(i<=0) return null;
  if(C.kind==='m') return 'm'+MONTHS[i-1].id;
  const idx=MONTHS[i].weeks.indexOf(C.w), pw=MONTHS[i-1].weeks;
  return 'w'+pw[Math.min(idx,pw.length-1)];
}
const BLANKS=['Blank/Unknown','Blank','Other'];
function orderCats(fi,names){
  const fx=FIXED[fi];
  if(fx){ const rest=names.filter(x=>!fx.includes(x)).sort();
    return fx.filter(x=>names.includes(x)).concat(rest); }
  const blank=names.filter(x=>BLANKS.includes(x));
  return names.filter(x=>!BLANKS.includes(x)).concat(blank);   /* blank/unknown last */
}
function breakupData(C,fi,msk,lens){
  const L=lens||LENS;
  const bits=PBITS(C), F=FLD(C), M=msk||DIMOK, out={};
  const blank=()=>({leads:0,assigned:0,called:0,answered:0,db:0,dc:0,sale:0});
  const get=k=>out[k]||(out[k]=blank());
  const want=g=>L==='b'?(g===1||g===2):L==='c'?g===1:g===2;
  for(const d of DEN){ if(!M[d[2]])continue;
    const g=memb(d[0],d[1],C); if(!want(g))continue;
    const o=get(DIMS[d[2]][fi]); o.leads+=d[4]; if(d[3])o.assigned+=d[4]; }
  for(const r of ROWS){ if(!M[r[0]])continue;
    const g=memb(r[1],r[2],C); if(!want(g))continue;
    const o=get(DIMS[r[0]][fi]);
    if(r[F[0]]&bits)o.called++;
    if(r[F[1]]&bits)o.answered++;
    if(r[F[2]]&bits)o.db++;
    if(r[F[3]]&bits)o.dc++;
    if(!(C.kind==='cm'&&C.m===8)&&SALEIN(r,C))o.sale++; }
  /* August sales come from the sheet, not from lead rows, so they are added here from the same
     per-dimension table the funnel uses - otherwise these cards would undercount and disagree
     with it. M0 is the cohort side; Rolling and Reactivation are the rolling side. */
  if(C.kind==='cm'&&C.m===8){
    for(const [d,b,n] of (CUBE.augSaleDim||[])){ if(!M[d])continue;
      if(!want(b===1?1:2))continue;
      get(DIMS[d][fi]).sale+=n; }
  }
  return out;                     /* raw, ungrouped: name -> funnel */
}
/* order, then fold the tail into "Other" while remembering which names went in */
function breakupParts(raw,fi){
  const blank=()=>({leads:0,assigned:0,called:0,answered:0,db:0,dc:0,sale:0});
  let names=orderCats(fi,Object.keys(raw));
  if(!FIXED[fi]) names=names.sort((a,b)=>{
    const ab=BLANKS.includes(a),bb=BLANKS.includes(b);
    if(ab!==bb) return ab?1:-1;
    return (raw[b].leads||0)-(raw[a].leads||0);});
  let arr=names.map(x=>({name:x,members:[x],f:raw[x]}));
  const n=TOPN[fi];
  if(arr.length>n){
    const head=arr.filter(x=>!BLANKS.includes(x.name)), tail=[];
    const keep=[];
    head.forEach(x=>keep.length<n?keep.push(x):tail.push(x));
    arr.filter(x=>BLANKS.includes(x.name)).forEach(x=>tail.push(x));
    if(tail.length){
      const agg=blank(), mem=[];
      tail.forEach(x=>{mem.push(...x.members);STAGES.forEach(([k])=>agg[k]+=x.f[k]);});
      keep.push({name:'Other ('+tail.length+' more)',members:mem,f:agg});
    }
    arr=keep;
  }
  return arr;
}
const SHORT=['Created','Assigned','Called','Answered','Booked','Conducted','Sale'];
function breakup(elId,fi){
  const B=BSEL[fi], C=ctx(B.pkey||PKEY), msk=buildMask(B.sel);
  const tt=$('#'+BKTT[fi]); if(tt) tt.textContent=C.label+' \u00b7 '+C.range;
  const raw=breakupData(C,fi,msk,B.lens), parts=breakupParts(raw,fi);
  const tot=parts.reduce((a,x)=>a+x.f.leads,0);
  const pk=prevKey(C);
  const praw=pk?breakupData(ctx(pk),fi,msk,B.lens):null;
  const plab=pk?ctx(pk).label:null;
  const pv=(members,k)=>!praw?null:members.reduce((a,m)=>a+((praw[m]&&praw[m][k])||0),0);
  $('#'+elId).innerHTML=parts.map(c=>{
    const mx=c.f.leads||1;
    return '<div class="bkcard"><h3>'+esc(c.name)
      +'<span>'+p1(pc(c.f.leads,tot))+' of leads</span></h3>'
      +'<div class="bkhead"><span>Stage</span><span></span><span>Count</span><span>Step</span></div>'
      +STAGES.map(([k,l],i)=>{
        const prev=i?c.f[STAGES[i-1][0]]:null, st=prev===null?null:pc(c.f[k],prev);
        /* the previous period is tooltip-only now - it is no longer a column */
        const was=pv(c.members,k);
        return '<div class="bkrow" data-tip="<b>'+esc(c.name)+' \u00b7 '+l+'</b><br>'+fmt(c.f[k])
          +(k==='leads'?'':'<br>'+p2(pc(c.f[k],c.f.assigned))+' of assigned')
          +(st===null?'':'<br>step '+p1(st))
          +(was===null?'':'<br>'+plab+': '+fmt(was))+'">'
          +'<span class="lbl">'+SHORT[i]+'</span>'
          +'<span class="mini"><i style="width:'+Math.max(.8,100*c.f[k]/mx).toFixed(1)+'%"></i></span>'
          +'<span class="n">'+fmt(c.f[k])+'</span>'
          +'<span class="s">'+(st===null?'—':p1(st))+'</span></div>';}).join('')
      +'</div>';}).join('');
}

/* ---------------- funnels ---------------- */
/* Lead assigned is read off the lead's current owner, so it cannot say WHEN a lead was assigned.
   The + next to that row says so. */
const ASSIGN_NOTE=`Lead assigned is derived from the lead owner, not from a date.
The lead may have been assigned on a different date &mdash; ownership is what is counted here.`;
function funnel(el,o,cls){
  const mx=o.leads||1;
  const bar=v=>`<td><div class="barwrap"><div class="bar ${cls||''}" style="width:${Math.max(.6,100*v/mx).toFixed(1)}%"></div></div></td>`;
  /* rows up to Demo conducted come from STAGES; the sale block below is built by hand so that
     Referral can be split out of Sale without touching the MTD, Compare or breakup views. */
  const head=STAGES.slice(0,-1);
  /* Sale is the total. The August identifiers sit under it and always sum to Sale. Outside
     August the class counters are all zero, so only the plain Sale row renders - previous
     months read exactly as they did before. */
  /* NB: do not name this `cls` - that is funnel()'s CSS-class parameter, and redeclaring it is a
     SyntaxError that kills the whole script. */
  const nBuckets=(o.m0||0)+(o.roll||0)+(o.react||0);
  const rhint=(o.refIn||0)>0
    ? ` <span class="hint">incl. ${o.refIn} referral · ${inr(o.refInRev||0)}</span>` : '';
  /* [label, count, extra-html, revenue] */
  const saleRows=nBuckets>0
    ? [['Sale',o.sale||0,'',o.saleRev||0],['M0',o.m0||0,'',o.m0Rev||0],
       ['Rolling',o.roll||0,rhint,o.rollRev||0],['Reactivation',o.react||0,'',o.reactRev||0]]
      .filter(([l,v])=>l==='Sale'||v>0)
    : [['Sale',o.sale||0,'',o.saleRev||0]];
  const anyRev=saleRows.some(([,,,rv])=>rv>0);
  el.innerHTML=`<table class="fnl"><thead><tr><th class="lft">Stage</th><th>Count</th>
    <th>% of assigned</th><th>Step</th>`+(anyRev?`<th>Revenue</th>`:``)+
    `<th style="width:120px">Shape</th></tr></thead><tbody>`+
  head.map(([k,l],i)=>{const prev=i?o[head[i-1][0]]:null,step=prev===null?null:pc(o[k],prev);
    const tag=k==='assigned'
      ? `${l} <button type="button" class="infobtn" title="How this is derived"
           onclick="this.parentNode.querySelector('.infonote').classList.toggle('on')">+</button>
         <div class="infonote">${ASSIGN_NOTE.split('\n').map(x=>`<div>${x}</div>`).join('')}</div>`
      : l;
    return `<tr><td class="stage">${tag}</td><td style="font-weight:700">${fmt(o[k])}</td>
      <td>${k==='leads'?'—':p2(pc(o[k],o.assigned))}</td>
      <td>${step===null?'—':`<span class="step up">${p1(step)}</span>`}</td>`
      +(anyRev?`<td class="rev">&mdash;</td>`:``)+bar(o[k])+`</tr>`;
  }).join('')
  /* every sale row steps off Demo conducted, so the percentages stay meaningful */
  +saleRows.map(([l,v,extra,rv],i)=>`<tr${i===0?' class="saletop"':''}><td class="stage"${
      i?' style="padding-left:20px;font-weight:500"':''}>${i?'&mdash; ':''}${l}${extra||''}</td>
    <td style="font-weight:${i?500:700}">${fmt(v)}</td><td>${p2(pc(v,o.assigned))}</td>
    <td><span class="step up">${p1(pc(v,o.dc))}</span></td>`
    +(anyRev?`<td class="rev" data-tip="${v?`${inrFull(rv)} across ${v} sale${v===1?'':'s'} · avg ${inrFull(Math.round(rv/v))}`:'no sales'}"${
       i?'':' style="font-weight:700"'}>${rv>0?inr(rv):'&mdash;'}</td>`:``)
    +bar(v)+`</tr>`).join('')
  +`</tbody></table>`;
}
function overview(){
  const C=ctx(PKEY);
  funnel($('#fnlC'),pick(stages(C,buildMask(CSEL.c)),'c'));
  funnel($('#fnlR'),pick(stages(C,buildMask(CSEL.r)),'r'),'roll');
  funnel($('#fnlB'),pick(stages(C,buildMask(CSEL.b)),'b'));
  breakup('bkSrc',0); breakup('bkGrade',1); breakup('bkState',2);
  const s=stages(C), outSale=s[3].sale;
}

/* ---------------- Weekly View (ageing, cohort rows) ---------------- */
const WV=[{n:'1 · Lead → Fresh Dial',f:14,den:'assigned',
   d:'Each lead counted <b>once</b>, in the bucket of its <b>first</b> outbound call — calendar days from the week’s Monday.'},
 {n:'2 · Lead → Redial',f:15,den:'assigned',
   d:'Each lead counted <b>once</b>, in the bucket of its <b>second</b> call.'},
 {n:'3 · Lead → Answered',f:16,den:'assigned',
   d:'Each lead counted <b>once</b>, in the bucket where it was <b>first answered</b>. Answered in D0–D3 counts there and never again in a later bucket.'},
 {n:'4 · Lead → Demo Booking',f:17,den:'assigned',
   d:'Each lead counted <b>once</b>, in the bucket of its <b>first</b> demo booking.'},
 {n:'5 · Answered → Demo',f:18,den:'answered',speed:true,
   d:'The answered leads, then their demos bucketed by the gap from <b>that lead’s own first answered call</b> — not from the week’s Monday.'}];
function weeklyRows(){
  const V=WV[WVIEW],B=V.speed?SPD.slice(0,3):BUCK,nb=B.length;
  const L=new Array(NW).fill(0),A=new Array(NW).fill(0),AN=new Array(NW).fill(0);
  const M=WEEKS.map(()=>new Array(nb).fill(0)); let noans=0;
  for(const d of DEN){ if(!DIMOK[d[2]]||d[1]<1)continue;
    L[d[1]-1]+=d[4]; if(d[3])A[d[1]-1]+=d[4]; }
  for(const r of ROWS){ if(!DIMOK[r[0]]||r[2]<1)continue;
    if(r[11])AN[r[2]-1]++;
    const b=r[V.f];
    if(V.speed){ if(b>=1&&b<=3)M[r[2]-1][b-1]++; else if(b===4)noans++; }
    else if(b>=1&&b<=nb)M[r[2]-1][b-1]++; }
  return {B,L,A,AN,M,noans};
}
function weekly(){
  $('#wviews').innerHTML=WV.map((v,i)=>`<button data-w="${i}" aria-selected="${i===WVIEW}">${v.n}</button>`).join('');
  const V=WV[WVIEW];
  const {B,L,A,AN,M,noans}=weeklyRows(), starts=V.speed?SSTART:BSTART;
  let mx=0;
  WEEKS.forEach((w,i)=>{const den=V.den==='answered'?AN[i]:A[i];
    M[i].forEach(v=>mx=Math.max(mx,pc(v,den)));});
  let h=`<div class="tblwrap"><table><thead><tr>
    <th rowspan="2" class="lft">Week (cohort)</th><th rowspan="2">Leads created</th><th rowspan="2">Lead assigned</th>`
    +(V.speed?`<th rowspan="2">Answered</th>`:'')
    +B.map(b=>`<th>${b}</th>`).join('')+`<th rowspan="2">Total</th></tr>
    <tr>${B.map(()=>`<th class="sub2">${V.speed?'Demos':'Leads'}</th>`).join('')}</tr></thead><tbody>`;
  const T=new Array(B.length).fill(0); let TL=0,TA=0,TAN=0;
  [...WEEKS].reverse().forEach(w=>{
    const i=w.id-1,el=ELAPSED[String(w.id)],den=V.den==='answered'?AN[i]:A[i];
    const tot=M[i].reduce((a,b)=>a+b,0);
    h+=`<tr><td class="wk">${w.label} · ${w.range}</td><td class="base">${fmt(L[i])}</td>
        <td class="base"><span class="cnt">${fmt(A[i])}</span><span class="pct">${p1(pc(A[i],L[i]))}</span></td>`;
    if(V.speed)h+=`<td class="base">${fmt(AN[i])}</td>`;
    M[i].forEach((v,j)=>{const p=pc(v,den),hh=heat(p,mx),open=starts[j]<=el;
      h+=`<td class="${hh.dark?'dark':''}" style="background:${open?hh.bg:'#f7f8fa'}"
        data-tip="<b>${w.label} · ${esc(B[j])}</b><br>${fmt(v)} ${V.speed?'demos':'leads'}<br>${p2(p)} of ${V.speed?'answered':'assigned'}${open?'':'<br><i>window not yet elapsed</i>'}">
        ${open?`<span class="cnt">${fmt(v)}</span><span class="pct">${p2(p)}</span>`:`<span class="pct">·</span>`}</td>`;});
    h+=`<td class="base">${fmt(tot)}</td></tr>`;
    M[i].forEach((v,j)=>T[j]+=v); TL+=L[i]; TA+=A[i]; TAN+=AN[i];});
  h+=`<tr class="tot"><td class="lft">All ${NW} weeks</td><td>${fmt(TL)}</td><td>${fmt(TA)}</td>`
    +(V.speed?`<td>${fmt(TAN)}</td>`:'')
    +T.map(v=>`<td>${fmt(v)}<div class="pct">${p2(pc(v,V.den==='answered'?TAN:TA))}</div></td>`).join('')
    +`<td>${fmt(T.reduce((a,b)=>a+b,0))}</td></tr></tbody></table></div>`;
  $('#wtables').innerHTML=h;
}

/* ---------------- MTD View ---------------- */
function mtd(){
  const cols=MTDMODE==='mtd'?MONTHS.map(m=>({k:'m'+m.id,label:m.name,sub:m.range}))
    :MTDMODE==='cal'?CALM.map(m=>({k:'c'+m.id,label:m.name+(m.complete?'':'*'),
                                   sub:m.from+' \u2013 '+m.to}))
    :WEEKS.map(w=>({k:'w'+w.id,label:w.label,sub:w.range}));
  const V={}; cols.forEach(c=>V[c.k]=cur(ctx(c.k)));
  const head=`<thead><tr><th class="lft">&nbsp;</th>${cols.map(c=>
    `<th>${c.label}<div style="font-weight:400;font-size:10px;opacity:.85">${c.sub}</div></th>`).join('')}</tr></thead>`;
  const row=(lab,f,cls)=>`<tr${cls?' class="'+cls+'"':''}><td class="lft" style="font-weight:600">${lab}</td>`
    +cols.map(c=>`<td>${f(V[c.k])}</td>`).join('')+`</tr>`;
  let h=`<div class="sechead">Lead generation</div><div class="tblwrap"><table>${head}<tbody>`
   +row('Leads created',o=>fmt(o.leads))
   +row('Lead assigned',o=>`<span class="cnt">${fmt(o.assigned)}</span><span class="pct">${p1(pc(o.assigned,o.leads))} of created</span>`)
   +`</tbody></table></div>`;
  h+=`<div class="sechead">Consumption</div><div class="tblwrap"><table>${head}<tbody>`
   +row('Consumed (called)',o=>`<span class="cnt">${fmt(o.called)}</span><span class="pct">${p1(pc(o.called,o.assigned))} of assigned</span>`)
   +row('Consumed → Answered',o=>`<span class="cnt">${fmt(o.answered)}</span><span class="pct">${p1(pc(o.answered,o.called))}</span>`)
   +row('Answered → Booked',o=>`<span class="cnt">${fmt(o.db)}</span><span class="pct">${p2(pc(o.db,o.answered))}</span>`)
   +row('Booked → Conducted',o=>`<span class="cnt">${fmt(o.dc)}</span><span class="pct">${p1(pc(o.dc,o.db))}</span>`)
   +row('Conducted → Sale',o=>`<span class="cnt">${fmt(o.sale)}</span><span class="pct">${p1(pc(o.sale,o.dc))}</span>`)
   +`</tbody></table></div>`;
  $('#brkmwrap').style.display=MTDBRK==='none'?'none':'flex';
  if(MTDBRK!=='none'){
    const fi=+MTDBRK,names=OPTS[fi],lab=STAGES.find(s=>s[0]===BRKM)[1];
    /* one extra pass per category, using the same aggregation with the filter forced */
    const save=SEL[fi],data={};
    names.forEach(n=>{SEL[fi]=n;computeDimOK();data[n]={};cols.forEach(c=>data[n][c.k]=cur(ctx(c.k))[BRKM]);});
    SEL[fi]=save;computeDimOK();
    h+=`<div class="sechead">${lab} broken down by ${FLAB[fi].toLowerCase()}</div><div class="tblwrap"><table>${head}<tbody>`;
    const tot={};cols.forEach(c=>tot[c.k]=names.reduce((a,n)=>a+data[n][c.k],0));
    names.map(n=>({n,v:names.reduce((a,x)=>a,0),s:cols.reduce((a,c)=>a+data[n][c.k],0)}))
      .sort((a,b)=>b.s-a.s).forEach(({n})=>{
        h+=`<tr><td class="lft" style="font-weight:600">${esc(n)}</td>`
          +cols.map(c=>{const v=data[n][c.k];
            return `<td><span class="cnt">${fmt(v)}</span><span class="pct">${p1(pc(v,tot[c.k]))}</span></td>`;}).join('')+`</tr>`;});
    h+=`<tr class="tot"><td class="lft">Total</td>${cols.map(c=>`<td>${fmt(tot[c.k])}</td>`).join('')}</tr></tbody></table></div>`;
  }
  $('#mtdbody').innerHTML=h;
}

/* ---------------- Compare (counts only) ---------------- */
function compare(){
  const A=$('#cA'),B=$('#cB');
  if(!A.options.length){const o=periodOptions(false);
    A.innerHTML=o;B.innerHTML=o;A.value='m7';B.value='m6';A.onchange=B.onchange=compare;}
  const ca=ctx(A.value),cb=ctx(B.value),oa=cur(ca),ob=cur(cb);
  $('#cmpbody').innerHTML=`<div class="tblwrap"><table><thead><tr><th class="lft">&nbsp;</th>
    <th>A · ${ca.label}<div style="font-weight:400;font-size:10px;opacity:.85">${ca.range}</div></th>
    <th>B · ${cb.label}<div style="font-weight:400;font-size:10px;opacity:.85">${cb.range}</div></th>
    <th>Difference</th><th>Change</th></tr></thead><tbody>`
   /* each count carries its step % off the stage above, so A and B are comparable stage by stage */
   +STAGES.map(([k,l],i)=>{const d=oa[k]-ob[k], pk=i?STAGES[i-1][0]:null;
     const cell=o=>`<span class="cnt">${fmt(o[k])}</span>`
       +(pk?`<span class="pct">${p1(pc(o[k],o[pk]))} step</span>`:'');
     return `<tr><td class="lft" style="font-weight:600">${l}</td><td>${cell(oa)}</td><td>${cell(ob)}</td>
       <td class="${d>=0?'up':'down'}" style="font-weight:700">${d>=0?'+':''}${fmt(d)}</td>
       <td>${ob[k]?(d>=0?'+':'')+p1(pc(d,ob[k])):'—'}</td></tr>`;}).join('')
   +`</tbody></table></div>`;
}

/* ---------------- wiring ---------------- */
function render(){
  computeDimOK();
  const C=ctx(PKEY);
  $$('.pn').forEach(e=>e.textContent=C.label+' \u00b7 '+C.range);
  overview(); weekly(); mtd(); compare();
}
FLAB.forEach((l,i)=>{const host=$('#f'+i); host.innerHTML='';
  multiSelect(host,i,()=>SEL[i],v=>{SEL[i]=v;},()=>render());});
$('#brkm').innerHTML=STAGES.map(([k,l])=>`<option value="${k}">${l}</option>`).join('');
$('#brkm').value='leads';
$('#brkm').onchange=e=>{BRKM=e.target.value;mtd();};
$('#period').innerHTML=periodOptions(false);
$('#period').value='m7';
$('#period').onchange=e=>{PKEY=e.target.value;render();};
$('#lens').onclick=e=>{const b=e.target.closest('button');if(!b)return;LENS=b.dataset.l;
  $$('#lens button').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));render();};
$('#tabs').onclick=e=>{const b=e.target.closest('button');if(!b)return;
  $$('#tabs button').forEach(x=>x.setAttribute('aria-selected',String(x===b)));
  $$('.panelbox').forEach(p=>p.classList.toggle('on',p.id==='p-'+b.dataset.t));};
$('#wviews').onclick=e=>{const b=e.target.closest('button');if(!b)return;WVIEW=+b.dataset.w;weekly();};
$('#mtdmode').onclick=e=>{const b=e.target.closest('button');if(!b)return;MTDMODE=b.dataset.m;
  $$('#mtdmode button').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));mtd();};
$('#mtdbrk').onclick=e=>{const b=e.target.closest('button');if(!b)return;MTDBRK=b.dataset.b;
  $$('#mtdbrk button').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));mtd();};
cardFilters('cfC','c'); cardFilters('cfR','r'); cardFilters('cfB','b');
breakupControls('bfSrc',0); breakupControls('bfGrade',1); breakupControls('bfState',2);
$('#through').textContent='Data to '+CUBE.throughLabel;
render();
</script></body></html>"""

open(OUT, "w", encoding="utf-8").write(HTML.replace("__CUBE__", cube))
print("wrote", OUT, round(os.path.getsize(OUT) / 1024), "KB")
