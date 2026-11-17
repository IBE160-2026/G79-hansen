/* Synthetic UI evidence. Actual owner RLS and uncached S3 are tested separately. */
const assert = require('node:assert/strict');
const {spawn} = require('node:child_process');
const path = require('node:path');
const net = require('node:net');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
const pause = ms => new Promise(resolve => setTimeout(resolve,ms));
let count=0;
async function check(name, action) { await action(); console.log('PASS '+name); count++; }
async function port() { const server=net.createServer();await new Promise(r=>server.listen(0,'127.0.0.1',r));const value=server.address().port;await new Promise(r=>server.close(r));return value; }
async function main() {
  let server,browser,output=''; const errors=[];
  try {
    const selectedPort=await port(),base=`http://127.0.0.1:${selectedPort}`;
    server=spawn(path.join(root,'.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python'),
      ['-m','uvicorn','documents_browser_app:app','--app-dir','tests','--host','127.0.0.1','--port',String(selectedPort)],
      {cwd:root,windowsHide:true,stdio:['ignore','pipe','pipe'],env:{...process.env,AUTH_TEST_ORIGIN:base}});
    server.stdout.on('data',chunk=>output+=chunk);server.stderr.on('data',chunk=>output+=chunk);
    for(let i=0;i<100;i++){try {if((await fetch(base+'/health')).ok)break;}catch{}if(server.exitCode!==null)throw new Error(output);await pause(100);}
    try {browser=await chromium.launch(process.env.DEMO_BROWSER_CHANNEL?{channel:process.env.DEMO_BROWSER_CHANNEL}:{});}catch{browser=await chromium.launch({channel:'msedge'});}
    const context=await browser.newContext({viewport:{width:1280,height:1000}}),page=await context.newPage();
    page.on('pageerror',error=>errors.push(error.message));
    async function login(email='library@example.test') {
      const state=await(await context.request.get(base+'/api/v1/auth/status')).json();
      assert.equal((await context.request.post(base+'/api/v1/auth/login',{headers:{Origin:base,'X-CSRF-Token':state.csrfToken},data:{email,password:'BROWSER_PRIVATE_PASSWORD'}})).status(),200);
    }
    async function ready(){await page.locator('#source-form').waitFor({state:'visible'});await page.waitForFunction(()=>!document.querySelector('#source-controls').disabled);}
    async function generate(value){await page.locator('#source-text').fill(value);await page.locator('#generate').click();await page.locator('#results').waitFor({state:'visible'});await page.waitForFunction(()=>!document.querySelector('#generate').disabled);}
    async function save(title){await page.locator('#save-title').fill(title);await page.locator('#save-document').click();await page.waitForFunction(()=>document.querySelector('#save-status').textContent.startsWith('Lagret privat.'));}
    async function library(){await page.locator('#document-library').click();await page.waitForFunction(()=>document.querySelector('#library-status').textContent!=='Henter dokumenter …');}
    async function back(){await page.locator('#library-back').click();}
    async function choose(row=page.locator('.library-document').first()){await row.getByRole('button',{name:'Åpne',exact:true}).click();if(await page.locator('#document-replace').isVisible())await page.locator('#document-replace-confirm').click();}
    async function restored(){await page.waitForFunction(()=>document.querySelector('#save-status').textContent.startsWith('Lagret versjon'));}
    async function state(){return(await context.request.get(base+'/__test/save-state')).json();}
    await login();await page.goto(base+'/workspace');await ready();
    await check('empty library explains explicit Save and returns focus',async()=>{
      await page.locator('#document-library').focus();await page.keyboard.press('Enter');
      await page.getByText('Du har ingen lagrede dokumenter.',{exact:false}).waitFor();
      assert.equal(await page.locator('#library-heading').evaluate(node=>node===document.activeElement),true);
      await back();assert.equal(await page.locator('#document-library').evaluate(node=>node===document.activeElement),true);
    });
    await check('list and back preserve unsaved source settings and no inference',async()=>{
      await page.locator('#source-text').fill('Unsaved original input');await page.locator('#source-subject').fill('IBE160');
      const before=await state();await library();await back();
      assert.equal(await page.locator('#source-text').inputValue(),'Unsaved original input');assert.equal(await page.locator('#source-subject').inputValue(),'IBE160');
      assert.equal((await state()).modelCalls,before.modelCalls);
    });
    await generate('SYNTHETIC_LIBRARY_CANONICAL_SOURCE Water freezes and becomes solid.');
    await page.locator('#tab-flashcards').click();await page.locator('#next').click();
    await page.locator('#tab-quiz').click();await page.locator('#next').click();
    await save('Privat <img src=x> ☃');
    await check('owner list has safe title date independent positions and no original-file action for paste',async()=>{
      await library();const row=page.locator('.library-document').first();
      assert.equal(await row.locator('h3').textContent(),'Privat <img src=x> ☃');assert.equal(await row.locator('img').count(),0);
      await row.getByText('Kort 2 av 2 · Spørsmål 2 av 2',{exact:true}).waitFor();assert.equal(await row.getByText('Lagret:',{exact:false}).count(),1);
      assert.equal(await row.getByRole('button',{name:'Last ned originalfil'}).count(),0);await back();
    });
    await check('cancel replacement preserves draft and reveal state',async()=>{
      await page.locator('#edit-material').click();await generate('UNSAVED_LIBRARY_DRAFT');
      await page.locator('#tab-flashcards').click();await page.locator('#reveal').click();
      await library();await page.locator('.library-document').first().getByRole('button',{name:'Åpne',exact:true}).click();
      await page.locator('#document-replace-cancel').click();await back();
      assert.equal(await page.locator('#source-text').inputValue(),'UNSAVED_LIBRARY_DRAFT');assert.equal(await page.locator('#answer').isVisible(),true);
    });
    await check('failed open preserves complete draft',async()=>{
      await library();await page.route('**/api/v1/documents/reload',route=>route.fulfill({status:503,json:{code:'library_unavailable'}}),{times:1});
      await choose();await page.getByText('Dokumentene kunne ikke hentes.',{exact:false}).waitFor();await back();
      assert.equal(await page.locator('#source-text').inputValue(),'UNSAVED_LIBRARY_DRAFT');assert.equal(await page.locator('#answer').isVisible(),true);
    });
    for(const malformed of ['missing acceptance version','unsupported acceptance version','unknown flashcard position']) {
      await check('HTTP 200 '+malformed+' preserves source results and revealed answer',async()=>{
        const originalContent=await page.locator('#content').innerHTML(),before=await state();
        await library();await page.route('**/api/v1/documents/reload',async route=>{
          const response=await route.fetch(),data=await response.json();
          if(malformed==='missing acceptance version')delete data.acceptance.schemaVersion;
          else if(malformed==='unsupported acceptance version')data.acceptance.schemaVersion='2.0';
          else data.positions.flashcardId='unknown-flashcard';
          await route.fulfill({status:200,json:data});
        },{times:1});
        await choose();await page.getByText('Dokumentene kunne ikke hentes.',{exact:false}).waitFor();await back();
        assert.equal(await page.locator('#source-text').inputValue(),'UNSAVED_LIBRARY_DRAFT');
        assert.equal(await page.locator('#results').isVisible(),true);assert.equal(await page.locator('#answer').isVisible(),true);
        assert.equal(await page.locator('#content').innerHTML(),originalContent);assert.equal((await state()).modelCalls,before.modelCalls);
      });
    }
    await check('reopen exact sections source settings positions and hidden answers without model',async()=>{
      const before=await state();await library();await choose();await restored();
      assert.equal(await page.locator('#source-text').inputValue(),'SYNTHETIC_LIBRARY_CANONICAL_SOURCE Water freezes and becomes solid.');
      assert.equal(await page.locator('#source-subject').inputValue(),'IBE160');
      for(const [section,label] of [['flashcards','Kort 2 av 2'],['quiz','Spørsmål 2 av 2']]) {
        await page.locator('#tab-'+section).click();assert.equal(await page.locator('#content .label').textContent(),label);assert.equal(await page.locator('#answer').isVisible(),false);
      }
      await page.locator('#tab-concepts').click();assert.equal(await page.locator('#content h3').count()>0,true);
      assert.equal((await state()).modelCalls,before.modelCalls);assert.equal(await page.locator('#save-document').isDisabled(),true);
    });
    await check('new session clears workspace while retaining library rows',async()=>{
      await page.locator('#edit-material').click();await page.locator('#reset-source').click();
      assert.equal(await page.locator('#source-text').inputValue(),'');assert.equal(await page.locator('#results').isVisible(),false);
      await library();assert.equal(await page.locator('.library-document').count(),1);await back();
    });
    await check('ungenerated input and settings require confirmation and Cancel sends no reload',async()=>{
      await page.locator('#source-text').fill('UNGENERATED_PRIVATE_DRAFT');await page.locator('#source-subject').fill('Unsaved subject');
      await page.locator('#source-language').selectOption('en');await page.locator('#source-detail').selectOption('detailed');
      const before=await state();let reloads=0;
      const listener=request=>{if(request.url().endsWith('/api/v1/documents/reload'))reloads++;};page.on('request',listener);
      await library();await page.locator('.library-document').first().getByRole('button',{name:'Åpne',exact:true}).click();
      await page.locator('#document-replace').waitFor({state:'visible'});await page.locator('#document-replace-cancel').click();await back();
      await pause(150);page.off('request',listener);assert.equal(reloads,0);
      assert.equal(await page.locator('#source-text').inputValue(),'UNGENERATED_PRIVATE_DRAFT');
      assert.equal(await page.locator('#source-subject').inputValue(),'Unsaved subject');assert.equal(await page.locator('#source-language').inputValue(),'en');
      assert.equal(await page.locator('#source-detail').inputValue(),'detailed');assert.equal(await page.locator('#results').isVisible(),false);
      assert.equal((await state()).modelCalls,before.modelCalls);await page.locator('#reset-source').click();
    });
    await check('restart same-owner fresh login reopens without old receipt',async()=>{
      const before=await state();await context.request.post(base+'/__test/save-restart');await page.reload();await page.locator('#source-sign-in').waitFor({state:'visible'});
      await login();await page.reload();await ready();await library();await choose();await restored();
      assert.equal((await state()).modelCalls,before.modelCalls);assert.equal(await page.locator('#save-document').isDisabled(),true);
    });
    await check('late list success after back cannot reappear',async()=>{
      let entered,release;const arrived=new Promise(r=>entered=r),held=new Promise(r=>release=r);
      await page.route('**/api/v1/documents/library',async route=>{const response=await route.fetch();entered();await held;await route.fulfill({response});},{times:1});
      await page.locator('#document-library').click();await arrived;await back();release();await pause(150);
      assert.equal(await page.locator('#library').isVisible(),false);assert.equal(await page.locator('.library-document').count(),0);
    });
    await check('Back immediately enables Save while obsolete open remains pending and later edit wins',async()=>{
      await page.locator('#edit-material').click();await generate('BACK_RETURNS_SAVEABLE_DRAFT');
      assert.equal(await page.locator('#save-document').isEnabled(),true);
      await library();let entered,release;const arrived=new Promise(r=>entered=r),held=new Promise(r=>release=r);
      await page.route('**/api/v1/documents/reload',async route=>{const response=await route.fetch();entered();await held;await route.fulfill({response});},{times:1});
      await choose();await arrived;await back();assert.equal(await page.locator('#save-document').isEnabled(),true);
      await page.locator('#edit-material').click();await page.locator('#source-text').fill('NEWER_DRAFT_WINS');release();await pause(150);
      assert.equal(await page.locator('#source-text').inputValue(),'NEWER_DRAFT_WINS');assert.equal(await page.locator('#results').isVisible(),false);
    });
    await check('delayed conflict reload cannot replace or abort a newer generation without an edit',async()=>{
      await generate('SEQUENCE_FENCE_UNSAVED_SOURCE');await context.request.post(base+'/__test/save-conflict');
      await page.locator('#save-document').click();await page.locator('#save-reload').waitFor({state:'visible'});
      let enteredReload,releaseReload,enteredGeneration,releaseGeneration;
      const reloadArrived=new Promise(r=>enteredReload=r),reloadHeld=new Promise(r=>releaseReload=r);
      const generationArrived=new Promise(r=>enteredGeneration=r),generationHeld=new Promise(r=>releaseGeneration=r);
      await page.route('**/api/v1/documents/reload',async route=>{const response=await route.fetch();enteredReload();await reloadHeld;await route.fulfill({response});},{times:1});
      await page.locator('#save-reload').click();await page.locator('#document-replace-confirm').click();await reloadArrived;
      const holdGeneration=async route=>{enteredGeneration();await generationHeld;await route.continue();};
      await page.route('**/api/v1/generation',holdGeneration);
      await page.locator('#edit-material').click();await page.locator('#generate').click();await generationArrived;
      assert.equal(await page.locator('#results').isVisible(),false,'new generation must be pending before releasing reload');
      const oldReply=page.waitForResponse(response=>response.url().endsWith('/api/v1/documents/reload'));
      releaseReload();await oldReply;await pause(150);
      assert.equal(await page.locator('#source-text').inputValue(),'SEQUENCE_FENCE_UNSAVED_SOURCE');
      assert.equal(await page.locator('#results').isVisible(),false);
      assert.equal(await page.locator('#generate').isDisabled(),true,await page.locator('#source-status').textContent());
      releaseGeneration();await page.locator('#results').waitFor({state:'visible'});await page.waitForFunction(()=>!document.querySelector('#generate').disabled);
      await page.unroute('**/api/v1/generation',holdGeneration);
      assert.equal(await page.locator('#source-text').inputValue(),'SEQUENCE_FENCE_UNSAVED_SOURCE');
      assert.equal(await page.locator('#save-status').textContent(),'');
      assert.equal(await page.locator('#save-document').isEnabled(),true);
      await page.locator('#edit-material').click();
    });
    await check('original-file attachment retains exact bytes without inference',async()=>{
      await page.locator('#reset-source').click();await page.locator('#source-kind').selectOption('text-file');
      const original=Buffer.from('SYNTHETIC_LIBRARY_ORIGINAL ☃\n');await page.locator('#source-file').setInputFiles({name:'original.txt',mimeType:'text/plain',buffer:original});
      await page.locator('#generate').click();await page.locator('#results').waitFor({state:'visible'});await page.waitForFunction(()=>!document.querySelector('#generate').disabled);await save('Originalfil');
      const before=await state();await library();const row=page.locator('.library-document').filter({hasText:'Originalfil'});
      const pending=page.waitForEvent('download');await row.getByRole('button',{name:'Last ned originalfil'}).click();
      const download=await pending;const stream=await download.createReadStream();const chunks=[];for await(const chunk of stream)chunks.push(chunk);
      assert.deepEqual(Buffer.concat(chunks),original);assert.equal((await state()).modelCalls,before.modelCalls);await back();
    });
    await check('late download after back is ignored',async()=>{
      await library();let entered,release;const arrived=new Promise(r=>entered=r),held=new Promise(r=>release=r);let downloaded=false;
      const listener=()=>downloaded=true;page.on('download',listener);
      await page.route('**/api/v1/documents/file',async route=>{const response=await route.fetch();entered();await held;await route.fulfill({response});},{times:1});
      await page.locator('.library-document').filter({hasText:'Originalfil'}).getByRole('button',{name:'Last ned originalfil'}).click();
      await arrived;await back();release();await pause(200);assert.equal(downloaded,false);page.off('download',listener);
    });
    await check('list error retries without clearing selected file or results',async()=>{
      await page.route('**/api/v1/documents/library',route=>route.fulfill({status:503,json:{code:'library_unavailable'}}),{times:1});
      await library();await page.locator('#library-retry').click();await page.locator('.library-document').first().waitFor();await back();
      assert.equal(await page.locator('#results').isVisible(),true);assert.equal(await page.locator('#source-file').evaluate(node=>node.files.length),1);
    });
    await check('bounded pagination appends unique records with stable cursor',async()=>{
      await context.request.post(base+'/__test/library-fixtures');await library();assert.equal(await page.locator('.library-document').count(),50);
      await page.locator('#library-more').click();await page.waitForFunction(()=>document.querySelectorAll('.library-document').length===55);
      assert.equal(await page.locator('#library-more').isVisible(),false);
      const titles=await page.locator('.library-document h3').allTextContents();assert.equal(new Set(titles).size,55);
    });
    await check('library mobile and 200 percent reflow',async()=>{
      await page.setViewportSize({width:320,height:900});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
      await page.setViewportSize({width:640,height:900});await page.evaluate(()=>document.body.style.zoom='200%');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
      await page.evaluate(()=>document.body.style.zoom='');await page.setViewportSize({width:1280,height:1000});
    });
    await check('late list after logout and fresh owner login cannot resurrect private rows',async()=>{
      await back();let entered,release;const arrived=new Promise(r=>entered=r),held=new Promise(r=>release=r);
      await page.route('**/api/v1/documents/library',async route=>{const response=await route.fetch();entered();await held;await route.fulfill({response});},{times:1});
      await page.locator('#document-library').click();await arrived;await page.locator('#source-logout').click();await page.locator('#source-sign-in').waitFor({state:'visible'});
      assert.equal(await page.locator('.library-document').count(),0);await login('other-library@example.test');await page.evaluate(()=>window.dispatchEvent(new Event('focus')));await ready();release();await pause(150);
      assert.equal(await page.locator('#library').isVisible(),false);assert.equal(await page.locator('.library-document').count(),0);
      await library();assert.equal(await page.locator('.library-document').count(),0);assert.equal(await page.evaluate(()=>localStorage.length+sessionStorage.length),0);
    });
    assert.deepEqual(errors,[]);console.log(`${count} library browser scenarios passed`);
  } finally {await browser?.close();server?.kill();}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
