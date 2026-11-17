/* Synthetic UI evidence; database/Storage evidence lives in the local integration suite. */
const assert = require('node:assert/strict');
const {spawn} = require('node:child_process');
const path = require('node:path');
const net = require('node:net');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
let count = 0;
async function check(name, action) { await action(); console.log(`PASS ${name}`); count++; }
async function port() { const server = net.createServer(); await new Promise(r => server.listen(0,'127.0.0.1',r)); const p=server.address().port; await new Promise(r=>server.close(r)); return p; }
async function main() {
  let server, browser, output=''; const errors=[];
  try {
    const selectedPort=await port(), base=`http://127.0.0.1:${selectedPort}`;
    server=spawn(path.join(root,'.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python'),
      ['-m','uvicorn','documents_browser_app:app','--app-dir','tests','--host','127.0.0.1','--port',String(selectedPort)],
      {cwd:root,windowsHide:true,stdio:['ignore','pipe','pipe'],env:{...process.env,AUTH_TEST_ORIGIN:base}});
    server.stdout.on('data',chunk=>output+=chunk); server.stderr.on('data',chunk=>output+=chunk);
    for(let i=0;i<100;i++){try {if((await fetch(base+'/health')).ok)break;}catch{} if(server.exitCode!==null)throw new Error(output); await pause(100);}
    try {browser=await chromium.launch(process.env.DEMO_BROWSER_CHANNEL?{channel:process.env.DEMO_BROWSER_CHANNEL}:{});} catch {browser=await chromium.launch({channel:'msedge'});}
    const context=await browser.newContext({viewport:{width:1280,height:1000}}), page=await context.newPage();let lastSave;
    page.on('request',request=>{if(request.url().endsWith('/api/v1/documents/save'))lastSave=request.postDataJSON();});
    page.on('pageerror',error=>errors.push(error.message));
    async function login(email='save@example.test') {
      const state=await(await context.request.get(base+'/api/v1/auth/status')).json();
      const response=await context.request.post(base+'/api/v1/auth/login',{headers:{Origin:base,'X-CSRF-Token':state.csrfToken},data:{email,password:'BROWSER_PRIVATE_PASSWORD'}});
      assert.equal(response.status(),200);
    }
    async function ready(){await page.locator('#source-form').waitFor({state:'visible'});await page.waitForFunction(()=>!document.querySelector('#source-controls').disabled);}
    async function generate(value='SYNTHETIC_PRIVATE_SAVE_SOURCE Water freezes and becomes solid.'){
      await page.locator('#source-text').fill(value); await page.locator('#generate').click();
      await page.locator('#results').waitFor({state:'visible'}); await page.waitForFunction(()=>!document.querySelector('#generate').disabled);
    }
    async function saved(){await page.waitForFunction(()=>document.querySelector('#save-status').textContent.startsWith('Lagret privat.'));}
    await login();await page.goto(base+'/workspace');await ready();
    await check('Save is explicit; generated content remains transient',async()=>{
      await generate();assert.equal((await(await context.request.get(base+'/__test/save-state')).json()).operations,0);
      assert.equal(await page.locator('#save-document').isEnabled(),true);
    });
    await check('independent practice positions captured once with title and no model call',async()=>{
      await page.locator('#tab-flashcards').click();await page.locator('#next').click();
      await page.locator('#tab-quiz').click();await page.locator('#next').click();
      await page.locator('#save-title').fill('Privat 😀 <img src=x>');
      const before=await(await context.request.get(base+'/__test/save-state')).json();
      await page.locator('#save-document').click();await saved();
      const after=await(await context.request.get(base+'/__test/save-state')).json();
      assert.equal(after.modelCalls,before.modelCalls);assert.equal(after.documents,1);
      assert.deepEqual(after.positions[0],lastSave.positions);
      assert.equal(lastSave.positions.flashcardId,lastSave.bundle.flashcards[1].id);
      assert.equal(lastSave.positions.quizId,lastSave.bundle.quiz[1].id);
      assert.equal(await page.locator('#save-document').isDisabled(),true);
      assert.equal(await page.locator('#save-title').isDisabled(),true);
    });
    await check('practice navigation does not create another Save',async()=>{
      await page.locator('#previous').click();
      assert.equal(await page.locator('#save-document').isDisabled(),true);
      assert.equal((await(await context.request.get(base+'/__test/save-state')).json()).documents,1);
    });
    await check('technical failure preserves results and exact retry',async()=>{
      await page.locator('#edit-material').click();await generate('Second synthetic source.');
      await context.request.post(base+'/__test/save-failure');
      await page.locator('#save-document').click();await page.locator('#save-again').waitFor({state:'visible'});
      assert.equal(await page.locator('#results').isVisible(),true);
      const before=await(await context.request.get(base+'/__test/save-state')).json();
      await page.locator('#save-again').click();await saved();
      const after=await(await context.request.get(base+'/__test/save-state')).json();
      assert.equal(after.modelCalls,before.modelCalls);assert.equal(after.documents,1);assert.equal(after.operations,before.operations);
    });
    await check('conflict preserves draft and offers explicit choices',async()=>{
      await page.locator('#edit-material').click();await generate('Third synthetic source.');
      await context.request.post(base+'/__test/save-conflict');
      await page.locator('#save-document').click();await page.locator('#save-new').waitFor({state:'visible'});
      assert.equal(await page.locator('#save-reload').isVisible(),true);
      assert.equal(await page.locator('#results').isVisible(),true);
    });
    await check('Save as new retains old document',async()=>{
      await page.locator('#tab-flashcards').click();await page.locator('#next').click();
      await page.locator('#tab-quiz').click();await page.locator('#next').click();
      await page.locator('#save-new').click();await saved();
      assert.equal((await(await context.request.get(base+'/__test/save-state')).json()).documents,2);
    });
    await check('explicit reload restores saved source and hides practice answers',async()=>{
      await page.locator('#edit-material').click();await generate('Unsaved source to discard explicitly.');
      await context.request.post(base+'/__test/save-conflict');await page.locator('#save-document').click();
      await page.locator('#save-reload').waitFor({state:'visible'});await page.locator('#save-reload').click();
      await page.locator('#document-replace-confirm').click();
      await page.waitForFunction(()=>document.querySelector('#save-status').textContent.startsWith('Lagret versjon'));
      assert.equal(await page.locator('#source-text').inputValue(),'Third synthetic source.');
      await page.locator('#tab-flashcards').click();
      assert.equal(await page.locator('#content .label').textContent(),'Kort 2 av 2');
      assert.equal(await page.locator('#content h3').textContent(),'Practice question 2');
      assert.equal(await page.locator('#answer').isVisible(),false);
      await page.locator('#tab-quiz').click();
      assert.equal(await page.locator('#content .label').textContent(),'Spørsmål 2 av 2');
      assert.equal(await page.locator('#content h3').textContent(),'Practice question 2');
      assert.equal(await page.locator('#answer').isVisible(),false);
      assert.equal(await page.locator('#save-document').isDisabled(),true);
    });
    await check('new session detaches target without deleting saved documents',async()=>{
      await page.locator('#edit-material').click();await page.locator('#reset-source').click();
      assert.equal(await page.locator('#results').isVisible(),false);
      assert.equal((await(await context.request.get(base+'/__test/save-state')).json()).documents,2);
      await generate('Recovery synthetic source.'); await context.request.post(base+'/__test/save-failure');
      await page.locator('#save-document').click();await page.locator('#save-again').waitFor({state:'visible'});
    });
    await check('restart requires fresh login and discovers only durable pending operation',async()=>{
      await context.request.post(base+'/__test/save-restart');await page.reload();
      await page.locator('#source-sign-in').waitFor({state:'visible'});
      await login();await page.reload();await ready();await page.locator('#save-recovery').waitFor({state:'visible'});
      assert.equal(await page.locator('#source-text').inputValue(),'');assert.equal(await page.locator('#results').isVisible(),false);
    });
    await check('same-owner recovery succeeds without generation or old proof',async()=>{
      const before=await(await context.request.get(base+'/__test/save-state')).json();
      await page.getByRole('button',{name:'Fortsett lagring',exact:true}).click();
      await page.locator('#save-recovery-items').getByText('Lagret privat.',{exact:true}).last().waitFor();
      const after=await(await context.request.get(base+'/__test/save-state')).json();assert.equal(after.modelCalls,before.modelCalls);assert.equal(after.documents,3);
    });
    await check('keyboard Save and Unicode title bound',async()=>{
      await generate('Keyboard synthetic source.');await page.locator('#save-title').fill('😀'.repeat(161));
      await page.locator('#save-document').focus();await page.keyboard.press('Enter');
      await page.waitForFunction(()=>document.querySelector('#save-status').textContent.includes('160 tegn'));
      await page.locator('#save-title').fill('Keyboard');await page.locator('#save-document').focus();await page.keyboard.press('Enter');await saved();
    });
    await check('narrow viewport and 200 percent layout remains within viewport',async()=>{
      await page.setViewportSize({width:320,height:900});
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true);
      await page.setViewportSize({width:640,height:900});await page.evaluate(()=>document.body.style.zoom='200%');
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true);
      await page.evaluate(()=>document.body.style.zoom='');await page.setViewportSize({width:1280,height:1000});
    });
    await check('logout clears saved target, recovery and private results without browser storage',async()=>{
      await page.locator('#source-logout').click();await page.locator('#source-sign-in').waitFor({state:'visible'});
      assert.equal(await page.locator('#save-recovery').isVisible(),false);assert.equal(await page.locator('#results').isVisible(),false);
      assert.equal(await page.locator('#save-title').inputValue(),'');
      assert.equal(await page.evaluate(()=>localStorage.length+sessionStorage.length),0);
    });
    await check('file recovery requests same bytes and rejects a different file',async()=>{
      await login();await page.reload();await ready();
      await page.locator('#source-kind').selectOption('text-file');
      const original={name:'synthetic.txt',mimeType:'text/plain',buffer:Buffer.from('Synthetic file source for exact recovery.')};
      await page.locator('#source-file').setInputFiles(original);await page.locator('#generate').click();
      await page.locator('#results').waitFor({state:'visible'});await context.request.post(base+'/__test/save-upload-failure');
      await page.locator('#save-document').click();await page.locator('#save-again').waitFor({state:'visible'});await page.reload();await ready();
      await page.locator('#save-recovery').waitFor({state:'visible'});
      const row=page.locator('.recovery-operation').filter({has:page.locator('input[type=file]')});
      await row.locator('input').setInputFiles({name:'wrong.txt',mimeType:'text/plain',buffer:Buffer.from('Wrong file')});
      await row.getByRole('button',{name:'Fortsett lagring',exact:true}).click();
      await row.getByText('Materialet eller filen samsvarer ikke med lagringen.').waitFor();
      const before=await(await context.request.get(base+'/__test/save-state')).json();
      await row.locator('input').setInputFiles(original);await row.getByRole('button',{name:'Fortsett lagring',exact:true}).click();
      await page.locator('#save-recovery-items').getByText('Lagret privat.',{exact:true}).last().waitFor();
      const after=await(await context.request.get(base+'/__test/save-state')).json();assert.equal(after.modelCalls,before.modelCalls);
    });
    await check('ready superseded-file cleanup survives reload and preserves current ready file',async()=>{
      await page.locator('#source-kind').selectOption('text-file');
      await page.locator('#source-file').setInputFiles({name:'before.txt',mimeType:'text/plain',buffer:Buffer.from('Synthetic original before replacement.')});
      await page.locator('#generate').click();await page.locator('#results').waitFor({state:'visible'});
      await page.waitForFunction(()=>!document.querySelector('#generate').disabled);
      await page.locator('#save-document').click();await saved();await page.locator('#edit-material').click();
      await page.locator('#source-file').setInputFiles({name:'after.txt',mimeType:'text/plain',buffer:Buffer.from('Synthetic original after replacement.')});
      await page.locator('#generate').click();await page.locator('#results').waitFor({state:'visible'});
      await page.waitForFunction(()=>!document.querySelector('#generate').disabled);
      await page.locator('#save-document').click();await saved();await page.reload();await ready();
      const panel=page.locator('#save-recovery');await panel.waitFor({state:'visible'});
      await panel.getByText('Avsluttet lagring venter på opprydding.').waitFor();
      assert.equal(await panel.getByRole('button',{name:'Fortsett lagring',exact:true}).count(),0);
      assert.equal(await panel.locator('input[type=file]').count(),0);
      const before=await(await context.request.get(base+'/__test/save-state')).json();
      await panel.getByRole('button',{name:'Rydd opp',exact:true}).click();
      await panel.getByText('Opprydding venter på bekreftelse.').waitFor();
      const cleanupAgain=panel.getByRole('button',{name:'Rydd opp',exact:true});
      await page.waitForFunction(()=>[...document.querySelectorAll('#save-recovery button')].some(button=>button.textContent==='Rydd opp'&&!button.disabled));
      const repeated=page.waitForResponse(response=>response.url().endsWith('/api/v1/documents/cleanup'));
      await cleanupAgain.click();assert.equal((await repeated).status(),200);
      await page.waitForFunction(()=>[...document.querySelectorAll('#save-recovery button')].some(button=>button.textContent==='Rydd opp'&&!button.disabled));
      const after=await(await context.request.get(base+'/__test/save-state')).json();
      assert.equal(after.files,before.files-1);assert.equal(after.documents,before.documents);assert.equal(after.modelCalls,before.modelCalls);
    });
    await check('lost ready response survives server and page restart as confirmed completion',async()=>{
      await page.locator('#source-kind').selectOption('paste');await generate('Lost successful response synthetic source.');
      await context.request.post(base+'/__test/save-lose-ready');
      await page.locator('#save-document').click();await page.locator('#save-again').waitFor({state:'visible'});
      const operationId=lastSave.operationId, before=await(await context.request.get(base+'/__test/save-state')).json();
      await context.request.post(base+'/__test/save-restart');await page.reload();
      await page.locator('#source-sign-in').waitFor({state:'visible'});await login();await page.reload();await ready();
      await page.locator('#save-recovery-items').getByText('Lagret privat.',{exact:true}).last().waitFor();
      const state=await(await context.request.get(base+'/api/v1/auth/status')).json();
      const recovered=await context.request.post(base+'/api/v1/documents/pending',{headers:{Origin:base,'X-CSRF-Token':state.csrfToken,'X-Session-View':state.sessionViewId},data:{schemaVersion:'1.0'}});
      const row=(await recovered.json()).operations.find(value=>value.operationId===operationId);
      assert.equal(row.recoveryState,'ready');assert.equal(row.outcome.status,'ready');
      assert.equal(await page.getByRole('button',{name:'Fortsett lagring',exact:true}).count(),0);
      assert.equal((await(await context.request.get(base+'/__test/save-state')).json()).modelCalls,before.modelCalls);
    });
    await check('whitespace and control titles permit correction before any admission',async()=>{
      await generate('Title validation synthetic source.');
      const before=await(await context.request.get(base+'/__test/save-state')).json();
      for(const title of ['   ','\u0085','bad\u0001title']) {
        await page.locator('#save-title').fill(title);await page.locator('#save-document').click();
        await page.waitForFunction(()=>document.querySelector('#save-status').textContent.includes('kontrolltegn'));
        assert.equal(await page.locator('#save-title').isEnabled(),true);
        assert.equal((await(await context.request.get(base+'/__test/save-state')).json()).operations,before.operations);
      }
      await page.locator('#save-title').fill('Corrected title');await page.locator('#save-document').click();await saved();
      assert.equal(await page.locator('#save-title').isDisabled(),true);
    });
    await check('definite unadmitted invalid input unlocks title while uncertain retry retains identity',async()=>{
      await page.locator('#edit-material').click();await generate('Definite invalid request synthetic source.');
      await page.route('**/api/v1/documents/save',route=>route.fulfill({status:422,contentType:'application/json',body:JSON.stringify({code:'invalid_input'})}),{times:1});
      await page.locator('#save-document').click();await page.waitForFunction(()=>document.querySelector('#save-status').textContent.length>0&&!document.querySelector('#save-title').disabled);
      await page.locator('#save-title').fill('Correctable server rejection');await page.locator('#save-document').click();await saved();
      await page.locator('#edit-material').click();await generate('Uncertain invalid retry synthetic source.');
      await page.route('**/api/v1/documents/save',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({code:'save_pending'})}),{times:1});
      await page.locator('#save-document').click();await page.locator('#save-again').waitFor({state:'visible'});
      const frozen=JSON.stringify(lastSave);
      await page.route('**/api/v1/documents/save',route=>route.fulfill({status:422,contentType:'application/json',body:JSON.stringify({code:'invalid_input'})}),{times:1});
      await page.locator('#save-again').click();await page.waitForFunction(()=>document.querySelector('#save-status').textContent.length>0&&!document.querySelector('#save-again').disabled);
      assert.equal(await page.locator('#save-title').isDisabled(),true);assert.equal(JSON.stringify(lastSave),frozen);
      await page.locator('#save-again').click();await saved();
    });
    await check('discovery failure is visible and explicitly retryable',async()=>{
      await page.route('**/api/v1/documents/pending',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({code:'save_unavailable'})}),{times:1});
      await page.reload();await ready();
      await page.locator('#save-recovery').getByText('Tidligere lagringer kunne ikke hentes.').waitFor();
      await page.locator('#save-recovery').getByRole('button',{name:'Prøv igjen',exact:true}).click();
      await page.locator('#save-recovery-items').getByText('Lagret privat.',{exact:true}).last().waitFor();
      assert.equal(await page.getByText('Tidligere lagringer kunne ikke hentes.').count(),0);
    });
    await check('explicitly disabled Save keeps recovery discovery unobtrusive',async()=>{
      await page.route('**/api/v1/documents/pending',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({code:'save_unavailable',saveDisabled:true})}),{times:1});
      await page.reload();await ready();await pause(100);
      assert.equal(await page.locator('#save-recovery').isVisible(),false);
    });
    await check('late same-session discovery cannot erase a newer response',async()=>{
      for(const obsolete of [{json:{operations:[]}},{status:401,json:{code:'session_ended'}}]) {
      let release, entered;const arrived=new Promise(resolve=>entered=resolve), held=new Promise(resolve=>release=resolve);let calls=0;
      const row={operationId:'10000000-0000-4000-8000-000000000001',status:'pending',title:'Newest synthetic recovery',digest:'a'.repeat(64)};
      const handler=async route=>{calls++;if(calls===1){entered();await held;await route.fulfill(obsolete);}else await route.fulfill({json:{operations:[row]}});};
      await page.route('**/api/v1/documents/pending',handler);await page.reload();await ready();await arrived;
      await generate('Newer discovery synthetic source.');await page.locator('#save-document').click();await saved();
      await page.getByText(row.title,{exact:true}).waitFor();release();await pause(100);
      assert.equal(await page.getByText(row.title,{exact:true}).count(),1);
      assert.equal(await page.locator('#source-sign-in').isVisible(),false);
      assert.equal(await page.locator('#source-controls').isDisabled(),false);
      await page.unroute('**/api/v1/documents/pending',handler);
      }
    });
    await check('stale pagination cannot append actions after a refreshed list',async()=>{
      let release, entered;const arrived=new Promise(resolve=>entered=resolve), held=new Promise(resolve=>release=resolve);
      const row=title=>({operationId:crypto.randomUUID(),status:'pending',title,digest:'a'.repeat(64)});let roots=0;
      const handler=async route=>{
        if(route.request().postDataJSON().cursor){entered();await held;await route.fulfill({json:{operations:[row('Stale synthetic page')]}});}
        else {roots++;await route.fulfill({json:{operations:[row(roots===1?'First synthetic page':'Refreshed synthetic list')],nextCursor:roots===1?'20000000-0000-4000-8000-000000000001':null}});}
      };
      await page.route('**/api/v1/documents/pending',handler);await page.reload();await ready();
      await page.getByRole('button',{name:'Vis flere lagringer',exact:true}).click();await arrived;
      await generate('Pagination fence synthetic source.');await page.locator('#save-document').click();await saved();
      await page.getByText('Refreshed synthetic list',{exact:true}).waitFor();release();await pause(100);
      assert.equal(await page.getByText('Stale synthetic page',{exact:true}).count(),0);
      assert.equal(await page.getByRole('button',{name:'Fortsett lagring',exact:true}).count(),1);
      await page.unroute('**/api/v1/documents/pending',handler);
    });
    await check('object-free cancellation completes and disappears while its identity remains durable',async()=>{
      await page.locator('#edit-material').click();await page.locator('#reset-source').click();
      await generate('Object-free cancellation synthetic source.');await page.locator('#save-title').fill('Object-free pending title');
      await context.request.post(base+'/__test/save-failure');await page.locator('#save-document').click();
      await page.locator('#save-again').waitFor({state:'visible'});const operationId=lastSave.operationId;
      await page.reload();await ready();await page.getByText('Object-free pending title',{exact:true}).waitFor();
      const state=await(await context.request.get(base+'/api/v1/auth/status')).json();
      const response=await context.request.post(base+'/api/v1/documents/cleanup',{headers:{Origin:base,'X-CSRF-Token':state.csrfToken,'X-Session-View':state.sessionViewId},data:{schemaVersion:'1.0',operationId}});
      assert.equal((await response.json()).status,'cleanup_complete');
      const before=await(await context.request.get(base+'/__test/save-state')).json();
      await page.reload();await ready();await page.locator('#save-recovery-items').getByText('Lagret privat.',{exact:true}).last().waitFor();
      assert.equal(await page.getByText('Object-free pending title',{exact:true}).count(),0);
      assert.equal((await(await context.request.get(base+'/__test/save-state')).json()).operations,before.operations);
    });
    await check('terminal recovery errors refresh to cleanup or object-free completion',async()=>{
      for(const terminal of ['expired','conflict']) for(const withFile of [false,true]) {
        await login();await page.reload();await ready();
        const title=`Terminal ${terminal} ${withFile?'file':'paste'} synthetic`;
        await page.locator('#source-kind').selectOption(withFile?'text-file':'paste');
        if(withFile) {
          await page.locator('#source-file').setInputFiles({name:'terminal.txt',mimeType:'text/plain',buffer:Buffer.from('Terminal synthetic source.')});
          await page.locator('#generate').click();await page.locator('#results').waitFor({state:'visible'});
          await page.waitForFunction(()=>!document.querySelector('#generate').disabled);
          await context.request.post(base+'/__test/save-upload-failure');
        } else {await generate('Terminal synthetic source.');await context.request.post(base+'/__test/save-failure');}
        await page.locator('#save-title').fill(title);await page.locator('#save-document').click();
        await page.locator('#save-again').waitFor({state:'visible'});const operationId=lastSave.operationId;
        await page.reload();await ready();
        const row=page.locator(`.recovery-operation[data-operation-id="${operationId}"]`);
        await row.getByText(title,{exact:true}).waitFor();
        await context.request.post(base+`/__test/save-terminal/${operationId}/${terminal}`);
        await row.getByRole('button',{name:'Fortsett lagring',exact:true}).click();
        if(withFile) {
          await row.getByRole('button',{name:'Rydd opp',exact:true}).waitFor();
          assert.equal(await row.getByRole('button',{name:'Fortsett lagring',exact:true}).count(),0);
          assert.equal(await row.locator('input[type=file]').count(),0);
          assert.equal(await row.getByText(title,{exact:true}).count(),0);
        } else await row.waitFor({state:'detached'});
      }
    });
    await check('obsolete reload failure after edit and generation cannot overwrite status',async()=>{
      await page.locator('#source-kind').selectOption('paste');await generate('Saved reload fence synthetic source.');
      await page.locator('#save-document').click();await saved();
      await page.locator('#edit-material').click();await generate('Unsaved before delayed reload.');
      await context.request.post(base+'/__test/save-conflict');await page.locator('#save-document').click();
      await page.locator('#save-reload').waitFor({state:'visible'});
      let release,entered;const arrived=new Promise(resolve=>entered=resolve),held=new Promise(resolve=>release=resolve);
      await page.route('**/api/v1/documents/reload',async route=>{entered();await held;await route.fulfill({status:503,json:{code:'save_pending'}});},{times:1});
      await page.locator('#save-reload').click();await page.locator('#document-replace-confirm').click();await arrived;
      await page.locator('#edit-material').click();await generate('New generation wins over delayed reload failure.');
      assert.equal(await page.locator('#save-status').textContent(),'');
      release();await page.waitForFunction(()=>!document.querySelector('#save-document').disabled);
      assert.equal(await page.locator('#save-status').textContent(),'');
      assert.equal(await page.locator('#source-text').inputValue(),'New generation wins over delayed reload failure.');
    });
    assert.deepEqual(errors,[]);console.log(`${count} Save browser scenarios passed`);
  } finally {await browser?.close();server?.kill();}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
