'use strict';
// Local GET-only browser regression. No forms, mailto or external navigation.
const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert');
const {chromium}=require('/home/philipp/.npm/_npx/e41f203b7505f1fb/node_modules/playwright');
const ROOT=path.resolve(__dirname,'..'),OUT=process.env.QA_OUT;
assert(OUT,'QA_OUT required');fs.mkdirSync(OUT,{recursive:true});
const expected=JSON.parse(fs.readFileSync(path.join(ROOT,'tests/copy_expected_nodes.json'),'utf8'));
const ld=JSON.parse(fs.readFileSync(path.join(ROOT,'tests/layout_copy_delta.json'),'utf8'));for(const lang of ['de','en'])for(const op of [...ld.languages[lang].operations].reverse()){assert.deepStrictEqual(expected[lang].slice(op.old_start,op.old_end),op.old);expected[lang].splice(op.old_start,op.old_end-op.old_start,...op.new);}
const rd=JSON.parse(fs.readFileSync(path.join(ROOT,'tests/rc3_copy_delta.json'),'utf8'));for(const lang of ['de','en'])for(const op of [...rd.languages[lang]].reverse()){assert.deepStrictEqual(expected[lang].slice(op.old_start,op.old_end),op.old);expected[lang].splice(op.old_start,op.old_end-op.old_start,...op.new);}
const r4d=JSON.parse(fs.readFileSync(path.join(ROOT,'tests/rc4_copy_delta.json'),'utf8'));for(const lang of ['de','en'])for(const op of [...r4d.languages[lang]].reverse()){assert.deepStrictEqual(expected[lang].slice(op.old_start,op.old_end),op.old);expected[lang].splice(op.old_start,op.old_end-op.old_start,...op.new);}
const selection=JSON.parse(fs.readFileSync(path.join(ROOT,'tests/copy_selection.json'),'utf8'));
const rows=[],errors=[];let browser;
const server=http.createServer((q,r)=>{try{assert(q.method==='GET');let f=path.resolve(ROOT,'.'+decodeURIComponent(new URL(q.url,'http://local').pathname));if(fs.statSync(f).isDirectory())f=path.join(f,'index.html');assert(fs.realpathSync(f).startsWith(ROOT+'/'));r.setHeader('Content-Type',({'.html':'text/html','.jpg':'image/jpeg','.svg':'image/svg+xml','.ttf':'font/ttf','.woff2':'font/woff2'})[path.extname(f)]||'application/octet-stream');r.end(fs.readFileSync(f));}catch{r.writeHead(404);r.end();}});
(async()=>{try{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const base='http://127.0.0.1:'+server.address().port;
 browser=await chromium.launch({executablePath:'/opt/google/chrome/chrome',headless:true,chromiumSandbox:true});
 const probe=await browser.newPage();await probe.goto('chrome://sandbox');const sandbox=await probe.locator('body').innerText();assert(/adequately sandboxed/i.test(sandbox));fs.writeFileSync(path.join(OUT,'SANDBOX.txt'),sandbox);await probe.close();
 for(const lang of ['de','en'])for(const width of [320,390,768,1280]){
  const c=await browser.newContext({viewport:{width,height:900},reducedMotion:'reduce',serviceWorkers:'block'});
  await c.route('**/*',r=>r.request().method()==='GET'&&r.request().url().startsWith(base+'/')?r.continue():r.abort());
  const p=await c.newPage(),row={lang,width,checks:[],pageErrors:[]};p.on('pageerror',e=>row.pageErrors.push(e.message));
  function check(ok,msg){row.checks.push({ok:!!ok,msg});if(!ok)errors.push(`${lang}-${width}: ${msg}`);}
  await p.goto(base+(lang==='en'?'/en/':'/'));await p.evaluate(()=>document.fonts.ready);
  // Exercise actual summary controls rather than manufacturing open DOM state.
  const details=p.locator('details');row.detailsCount=await details.count();
  row.closed=await p.evaluate(()=>({viewport:innerWidth,scroll:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight}));
  for(let i=0;i<await details.count();i++){const d=details.nth(i);if(!await d.evaluate(e=>e.open))await d.locator('summary').click();check(await d.evaluate(e=>e.open),'details opens via summary '+i);}
  // Trigger content reveal by visiting every section, then capture fully open page.
  for(const s of await p.locator('main section').all()){await s.scrollIntoViewIfNeeded();await p.waitForTimeout(30);}
  for(const image of await p.locator('img').all()){await image.scrollIntoViewIfNeeded();await image.evaluate(i=>i.decode());}
  await p.waitForTimeout(250);
  const data=await p.evaluate(()=>{const walker=document.createTreeWalker(document,NodeFilter.SHOW_TEXT),nodes=[];while(walker.nextNode()){const n=walker.currentNode;if(n.parentElement?.closest('script,style'))continue;const t=n.textContent.replace(/\s+/g,' ').trim();if(t)nodes.push(t);}return {nodes,text:document.body.innerText,viewport:innerWidth,scroll:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight,images:[...document.images].map(i=>({src:i.getAttribute('src'),loaded:i.naturalWidth>0&&i.naturalHeight>0})),overflows:[...document.querySelectorAll('main *')].filter(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width&&s.display!=='none'&&s.visibility!=='hidden'&&(r.right>innerWidth+1||r.left< -1)}).map(e=>({tag:e.tagName,id:e.id,cls:e.className,text:e.textContent.slice(0,100),right:e.getBoundingClientRect().right})).slice(0,20)};});
  row.open={viewport:data.viewport,scroll:data.scroll,height:data.height};row.overflows=data.overflows;
  check(JSON.stringify(data.nodes)===JSON.stringify(expected[lang]),'all ordered actual DOM text nodes equal baseline plus approved deltas');
  check(row.closed.scroll<=width,'no closed document horizontal overflow');check(data.scroll<=width,'no open document horizontal overflow');
  for(const e of selection.entries){if(typeof e.id!=='number')continue;const old=(e['alt_'+lang]||'').trim();check(!old||!data.text.includes(old),'removed fragment absent from rendered open text ID '+e.id);}
  check(!data.text.includes(lang==='de'?'Beim Personal Training begleite ich dich als':'In personal training I support you as a personal trainer;'),'W07 redundant role removed');
  for(const id of ['personal-training','sportpsychologie']){
   const t=await p.locator('#'+id).innerText();
   check(t.includes(selection.entries.find(e=>e.id==='HRV-definition')['neu_'+lang]),id+' positive HRV definition rendered');
   check(!t.includes(lang==='de'?'Falls dir dabei schwindlig oder unwohl wird':'If you feel dizzy or unwell, we stop the exercise'),id+' W02 exact rejected paragraph removed');
  }
  check(data.images.every(i=>i.loaded),'all images actually loaded');check(!row.pageErrors.length,'no page errors');
  fs.writeFileSync(path.join(OUT,`${lang}-${width}-rendered.txt`),data.text);
  await p.evaluate(()=>scrollTo(0,0));await p.screenshot({path:path.join(OUT,`${lang}-${width}-open.png`),fullPage:true});
  rows.push(row);await c.close();
 }
}finally{if(browser)await browser.close();await new Promise(r=>server.close(r));fs.writeFileSync(path.join(OUT,'COPY_BROWSER.json'),JSON.stringify({ok:!errors.length,errors,rows},null,2));}
console.log(JSON.stringify({ok:!errors.length,rows:rows.length,checks:rows.reduce((n,r)=>n+r.checks.length,0),errors},null,2));if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
