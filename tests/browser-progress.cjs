/* Synthetic UI evidence; real CAS/RLS is verified by the local RPC harness. */
'use strict';
const assert=require('node:assert/strict'),{spawn}=require('node:child_process'),path=require('node:path'),net=require('node:net');
const {chromium}=require('playwright'),root=path.resolve(__dirname,'..');
const pause=ms=>new Promise(r=>setTimeout(r,ms));
async function freePort(){const s=net.createServer();await new Promise(r=>s.listen(0,'127.0.0.1',r));const p=s.address().port;await new Promise(r=>s.close(r));return p;}
async function main(){let server,browser,output='',count=0;const errors=[];
  try{
    const port=await freePort(),base=`http://127.0.0.1:${port}`;
    server=spawn(path.join(root,'.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python'),
      ['-m','uvicorn','documents_browser_app:app','--app-dir','tests','--host','127.0.0.1','--port',String(port)],
      {cwd:root,windowsHide:true,stdio:['ignore','pipe','pipe'],env:{...process.env,AUTH_TEST_ORIGIN:base}});
    server.stdout.on('data',c=>output+=c);server.stderr.on('data',c=>output+=c);
    for(let i=0;i<100;i++){try{if((await fetch(base+'/health')).ok)break;}catch{}if(server.exitCode!==null)throw Error(output);await pause(100);}
    try{browser=await chromium.launch(process.env.DEMO_BROWSER_CHANNEL?{channel:process.env.DEMO_BROWSER_CHANNEL}:{});}catch{browser=await chromium.launch({channel:'msedge'});}
    const context=await browser.newContext({viewport:{width:1280,height:1000}}),page=await context.newPage();
    page.on('pageerror',e=>errors.push(e.message));
    const state=async()=> (await context.request.get(base+'/__test/save-state')).json();
    async function check(name,fn){await fn();count++;console.log('PASS '+name);}
    async function login(email='progress@example.test'){
      const s=await(await context.request.get(base+'/api/v1/auth/status')).json();
      assert.equal((await context.request.post(base+'/api/v1/auth/login',{headers:{Origin:base,'X-CSRF-Token':s.csrfToken},data:{email,password:'BROWSER_PRIVATE_PASSWORD'}})).status(),200);
    }
    async function ready(p=page){await p.goto(base+'/workspace');await p.locator('#source-form').waitFor({state:'visible'});await p.waitForFunction(()=>!document.querySelector('#source-controls').disabled);}
    async function open(p=page){await p.locator('#document-library').click();await p.locator('.library-document').first().waitFor();await p.locator('.library-document').first().getByRole('button',{name:'Åpne',exact:true}).click();await p.waitForFunction(()=>document.querySelector('#save-status').textContent.startsWith('Lagret versjon'));}
    async function saved(p=page){await p.waitForFunction(()=>document.querySelector('#progress-status').textContent==='Fremdriften er lagret.');}
    async function tab(p,name){await p.locator('#tab-'+name).click();}
    async function at(p,n){assert.match(await p.locator('#content .label').textContent(),new RegExp(` ${n} av `));}
    await login();await ready();
    await page.locator('#source-text').fill('SYNTHETIC_PROGRESS_SOURCE Water freezes and becomes solid.');await page.locator('#generate').click();await page.locator('#results').waitFor({state:'visible'});
    await check('unsaved navigation has no persistence',async()=>{await tab(page,'flashcards');await page.locator('#next').click();await tab(page,'quiz');await page.locator('#next').click();assert.equal((await state()).progressMutations,0);});
    await page.locator('#save-document').click();await page.waitForFunction(()=>document.querySelector('#save-status').textContent.startsWith('Lagret privat.'));await saved();
    const first=(await state()).modelCalls;
    await check('saved backward navigation persists both independent IDs',async()=>{await tab(page,'flashcards');await page.locator('#previous').click();await saved();const s=await state();assert.equal(s.progressRevisions[0],2);assert.equal(s.progressMutations,1);await tab(page,'quiz');await at(page,2);});
    await check('tab changes preserve revealed answers',async()=>{await page.locator('#reveal').click();await tab(page,'summary');await tab(page,'quiz');assert.equal(await page.locator('#answer').isVisible(),true);});
    await check('rapid navigation serializes and coalesces without moving visible item back',async()=>{
      let entered,release;const arrived=new Promise(r=>entered=r),held=new Promise(r=>release=r),requests=[];
      const handler=async route=>{requests.push(route.request().postDataJSON());const response=await route.fetch();if(requests.length===1){entered();await held;}await route.fulfill({response});};
      await page.route('**/api/v1/progress/write',handler);await tab(page,'flashcards');await page.locator('#next').click();await arrived;
      await page.locator('#previous').click();await page.locator('#next').click();await tab(page,'quiz');await page.locator('#previous').click();await at(page,1);
      release();await saved();await page.waitForFunction(()=>document.querySelector('#progress-status').textContent==='Fremdriften er lagret.');await pause(100);
      assert.equal(requests.length,2);assert.equal(requests[1].expectedProgressRevision,requests[0].expectedProgressRevision+1);await at(page,1);await page.unroute('**/api/v1/progress/write',handler);
    });
    const second=await context.newPage();second.on('pageerror',e=>errors.push(e.message));await ready(second);await open(second);
    await check('fresh visit restores acknowledged positions and hides answers without inference',async()=>{await tab(second,'flashcards');await at(second,2);assert.equal(await second.locator('#answer').isVisible(),false);await tab(second,'quiz');await at(second,1);assert.equal((await state()).modelCalls,first);});
    await check('stale view blocks until explicit successful fresh fetch',async()=>{
      await tab(page,'flashcards');await page.locator('#previous').click();await saved();
      await tab(second,'flashcards');await second.locator('#previous').click();await second.getByText('Fremdriften er endret på en annen enhet',{exact:true}).waitFor();
      const before=(await state()).progressMutations;await second.locator('#next').click();await pause(80);assert.equal((await state()).progressMutations,before);
      await second.route('**/api/v1/progress/read',r=>r.fulfill({status:503,json:{code:'progress_pending'}}),{times:1});await second.locator('#progress-fetch').click();
      await second.getByText('Siste fremdrift kunne ikke hentes.',{exact:false}).waitFor();await second.locator('#previous').click();await pause(80);assert.equal((await state()).progressMutations,before);
      await second.locator('#reveal').click();await second.locator('#progress-fetch').click();await second.getByText('Siste fremdrift er hentet. Svarene er skjult.',{exact:true}).waitFor();await at(second,1);assert.equal(await second.locator('#answer').isVisible(),false);
      await second.locator('#next').click();await saved(second);await second.locator('#previous').click();await saved(second);
    });
    await second.close();await open();
    await check('lost committed reply automatically retries the exact mutation once',async()=>{
      const before=await state(),requests=[];const record=r=>{if(r.url().endsWith('/api/v1/progress/write'))requests.push(r.postDataJSON());};page.on('request',record);
      await context.request.post(base+'/__test/progress-lose-ready');await tab(page,'flashcards');await page.locator('#next').click();await saved();page.off('request',record);
      assert.equal(requests.length,2);assert.deepEqual(requests[0],requests[1]);const after=await state();assert.equal(after.progressRevisions[0],before.progressRevisions[0]+1);assert.equal(after.progressMutations,before.progressMutations+1);
    });
    await check('two uncertain replies stop writes and explicit retry keeps frozen payload',async()=>{
      const requests=[];await page.route('**/api/v1/progress/write',r=>{requests.push(r.request().postDataJSON());return r.fulfill({status:503,json:{code:'progress_pending'}});},{times:2});
      await page.locator('#previous').click();await page.locator('#progress-retry').waitFor({state:'visible'});assert.equal(requests.length,2);assert.deepEqual(requests[0],requests[1]);
      await page.locator('#next').click();await pause(80);assert.equal(requests.length,2);
      const recovery=[];const record=r=>{if(r.url().endsWith('/api/v1/progress/write'))recovery.push(r.postDataJSON());};page.on('request',record);
      await page.locator('#progress-retry').click();await saved();await pause(100);page.off('request',record);
      assert.deepEqual(recovery[0],requests[0]);assert.equal(recovery.length,2);await at(page,2);
    });
    await check('same-document acknowledgement survives library open and back',async()=>{
      let entered,release;const arrived=new Promise(r=>entered=r),held=new Promise(r=>release=r);
      await page.route('**/api/v1/progress/write',async r=>{const response=await r.fetch();entered();await held;await r.fulfill({response});},{times:1});
      await page.locator('#previous').click();await arrived;await page.locator('#document-library').click();await page.locator('#library-back').click();release();await saved();
      await page.locator('#next').click();await saved();assert.equal(await page.locator('#progress-fetch').isVisible(),false);
    });
    await check('late completion after reset cannot restore progress or send queued intent',async()=>{
      let entered,release;const arrived=new Promise(r=>entered=r),held=new Promise(r=>release=r);
      await page.route('**/api/v1/progress/write',async r=>{const response=await r.fetch();entered();await held;await r.fulfill({response}).catch(()=>{});},{times:1});
      await page.locator('#previous').click();await arrived;await page.locator('#next').click();const before=(await state()).progressMutations;
      await page.locator('#edit-material').click();await page.locator('#reset-source').click();release();await pause(150);
      assert.equal(await page.locator('#progress-status').textContent(),'');assert.equal(await page.locator('#results').isVisible(),false);assert.equal((await state()).progressMutations,before);
    });
    await check('restart reopens durable acknowledged progress with hidden answers',async()=>{await context.request.post(base+'/__test/save-restart');await page.reload();await page.locator('#source-sign-in').waitFor({state:'visible'});await login();await ready();await open();await tab(page,'flashcards');await at(page,1);assert.equal(await page.locator('#answer').isVisible(),false);assert.equal((await state()).modelCalls,first);});
    await check('changed generation stays blocked until saved document is reopened',async()=>{
      await page.route('**/api/v1/progress/write',r=>r.fulfill({status:409,json:{code:'progress_generation'}}),{times:1});
      await page.locator('#next').click();await page.getByText('Dokumentet har en ny versjon.',{exact:false}).waitFor();assert.equal(await page.locator('#progress-retry').isVisible(),false);
      const before=(await state()).progressMutations;
      await page.route('**/api/v1/progress/read',r=>r.fulfill({status:409,json:{code:'progress_generation'}}),{times:1});await page.locator('#progress-fetch').click();await page.getByText('Siste fremdrift kunne ikke hentes.',{exact:false}).waitFor();
      await page.locator('#previous').click();await pause(80);assert.equal((await state()).progressMutations,before);await open();await tab(page,'flashcards');await at(page,1);
    });
    await check('late explicit fetch after edit cannot restore positions or answers',async()=>{
      await page.route('**/api/v1/progress/write',r=>r.fulfill({status:409,json:{code:'progress_conflict'}}),{times:1});await page.locator('#next').click();await page.locator('#progress-fetch').waitFor({state:'visible'});
      let entered,release;const arrived=new Promise(r=>entered=r),held=new Promise(r=>release=r);
      await page.route('**/api/v1/progress/read',async r=>{const response=await r.fetch();entered();await held;await r.fulfill({response}).catch(()=>{});},{times:1});
      await page.locator('#progress-fetch').click();await arrived;await page.locator('#edit-material').click();await page.locator('#source-text').fill('NEWER_EDIT_FENCES_PROGRESS_FETCH');release();await pause(120);
      assert.equal(await page.locator('#results').isVisible(),false);assert.equal(await page.locator('#progress-status').textContent(),'');assert.equal(await page.locator('#source-text').inputValue(),'NEWER_EDIT_FENCES_PROGRESS_FETCH');await page.locator('#reset-source').click();await open();
    });
    await check('late write after open is ignored while next navigation uses fetched revision',async()=>{
      await tab(page,'flashcards');let entered,release;const arrived=new Promise(r=>entered=r),held=new Promise(r=>release=r);
      await page.route('**/api/v1/progress/write',async r=>{const response=await r.fetch();entered();await held;await r.fulfill({response}).catch(()=>{});},{times:1});
      await page.locator('#next').click();await arrived;await open();release();await pause(100);await tab(page,'flashcards');await at(page,2);await page.locator('#previous').click();await saved();assert.equal(await page.locator('#progress-fetch').isVisible(),false);
    });
    await check('progress controls reflow at320 pixels and200 percent',async()=>{await page.setViewportSize({width:320,height:900});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);await page.setViewportSize({width:640,height:900});await page.evaluate(()=>document.body.style.zoom='200%');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);});
    await check('late completion after logout and new owner cannot restore private progress',async()=>{
      await page.evaluate(()=>document.body.style.zoom='');await page.setViewportSize({width:1280,height:1000});let entered,release;const arrived=new Promise(r=>entered=r),held=new Promise(r=>release=r);
      await page.route('**/api/v1/progress/write',async r=>{const response=await r.fetch();entered();await held;await r.fulfill({response}).catch(()=>{});},{times:1});
      await page.locator('#next').click();await arrived;await page.locator('#source-logout').click();await page.locator('#source-sign-in').waitFor({state:'visible'});await login('other-progress@example.test');await ready();release();await pause(100);
      assert.equal(await page.locator('#progress-status').textContent(),'');assert.equal(await page.locator('#results').isVisible(),false);await page.locator('#document-library').click();await page.getByText('Du har ingen lagrede dokumenter.',{exact:false}).waitFor();assert.equal(await page.locator('.library-document').count(),0);
    });
    assert.deepEqual(errors,[]);console.log(`${count} progress browser scenarios passed`);
  }finally{await browser?.close();server?.kill();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
