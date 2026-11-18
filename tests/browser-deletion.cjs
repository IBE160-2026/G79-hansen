/* Synthetic UI only; SQL and real Storage acceptance run separately. */
const assert=require('node:assert/strict'),{spawn}=require('node:child_process');
const path=require('node:path'),net=require('node:net'),{chromium}=require('playwright');
const root=path.resolve(__dirname,'..'),pause=ms=>new Promise(r=>setTimeout(r,ms));
async function main(){
 let server,browser,output='',checks=0;const errors=[];
 const check=async(name,fn)=>{await fn();checks++;console.log('PASS '+name);};
 try{
  const socket=net.createServer();await new Promise(r=>socket.listen(0,'127.0.0.1',r));const port=socket.address().port;await new Promise(r=>socket.close(r));
  const base=`http://127.0.0.1:${port}`;
  server=spawn(path.join(root,'.venv',process.platform==='win32'?'Scripts/python.exe':'bin/python'),['-m','uvicorn','documents_browser_app:app','--app-dir','tests','--host','127.0.0.1','--port',String(port)],{cwd:root,windowsHide:true,stdio:['ignore','pipe','pipe'],env:{...process.env,AUTH_TEST_ORIGIN:base}});
  server.stdout.on('data',c=>output+=c);server.stderr.on('data',c=>output+=c);
  for(let i=0;i<100;i++){try{if((await fetch(base+'/health')).ok)break;}catch{}if(server.exitCode!==null)throw Error(output);await pause(100);}
  try{browser=await chromium.launch();}catch{browser=await chromium.launch({channel:'msedge'});}
  const context=await browser.newContext({viewport:{width:390,height:844}}),page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
  async function login(){const state=await(await context.request.get(base+'/api/v1/auth/status')).json();assert.equal((await context.request.post(base+'/api/v1/auth/login',{headers:{Origin:base,'X-CSRF-Token':state.csrfToken},data:{email:'deletion@example.test',password:'BROWSER_PRIVATE_PASSWORD'}})).status(),200);}
  async function ready(){await page.locator('#source-form').waitFor({state:'visible'});await page.waitForFunction(()=>!document.querySelector('#source-controls').disabled);}
  async function save(title){await page.locator('#source-text').fill('SYNTHETIC_DELETE_SOURCE Water freezes and becomes solid.');await page.locator('#generate').click();await page.locator('#results').waitFor({state:'visible'});await page.waitForFunction(()=>!document.querySelector('#generate').disabled);await page.locator('#save-title').fill(title);await page.locator('#save-document').click();await page.waitForFunction(()=>document.querySelector('#save-status').textContent.startsWith('Lagret privat.'));}
  async function library(){await page.locator('#document-library').click();await page.waitForFunction(()=>!document.querySelector('#library').hidden && document.querySelector('#library').getAttribute('aria-busy')==='false');}
  async function state(){return(await context.request.get(base+'/__test/save-state')).json();}
  await login();await page.goto(base+'/workspace');await ready();await save('Privat <img src=x>');
  for(const status of [404,503]) await check(`unavailable deletion backend ${status} preserves library and disables deletion`,async()=>{
   let mutations=0;
   const onRequest=request=>{if(request.url().endsWith('/documents/delete'))mutations++;};page.on('request',onRequest);
   await page.route('**/api/v1/documents/deletions',route=>route.fulfill({status,json:status===404?{detail:'Not Found'}:{code:'save_pending'}}),{times:1});
   await library();const row=page.locator('.library-document').first();
   assert.equal(await page.locator('#library-status').textContent(),'Dokumentene er klare.');
   assert.equal(await row.getByRole('button',{name:'Slett',exact:true}).isDisabled(),true);
   assert.equal(await row.getByRole('button',{name:'Åpne',exact:true}).isEnabled(),true);
   await row.getByRole('button',{name:'Slett',exact:true}).evaluate(button=>button.click());
   assert.equal(await row.locator('.delete-confirmation').count(),0);assert.equal(mutations,0);
   await row.getByRole('button',{name:'Åpne',exact:true}).click();await page.locator('#results').waitFor({state:'visible'});
   await page.waitForFunction(()=>document.querySelector('#library').hidden);page.off('request',onRequest);
  });
  await check('named inline confirmation safe title cancel preserves material progress and focus',async()=>{
   const before=await state();await library();const row=page.locator('.library-document').first();const remove=row.getByRole('button',{name:'Slett',exact:true});await remove.click();
   await row.getByText('Kilden, læringsmaterialet og fremdriften blir slettet.',{exact:false}).waitFor();assert.equal(await row.locator('img').count(),0);
   await row.getByRole('button',{name:'Avbryt',exact:true}).click();assert.equal(await remove.evaluate(n=>n===document.activeElement),true);assert.deepEqual(await state(),before);
   await page.locator('#library-back').click();assert.equal(await page.locator('#results').isVisible(),true);
  });
  await check('confirmation clears active workspace removes entry and returns accessible focus',async()=>{
   await library();const row=page.locator('.library-document').first();await row.getByRole('button',{name:'Slett',exact:true}).click();await row.getByRole('button',{name:'Bekreft sletting'}).click();
   await page.getByText('Dokumentet, kilden, læringsmaterialet og fremdriften er slettet.',{exact:true}).waitFor();assert.equal((await state()).documents,0);assert.equal((await state()).operations,0);
   assert.equal(await page.locator('#library-heading').evaluate(n=>n===document.activeElement),true);await page.locator('#library-back').click();assert.equal(await page.locator('#results').isVisible(),false);assert.equal(await page.locator('#source-text').inputValue(),'');
  });
  await save('Retry document');
  await check('failed deletion remains discoverable after restart and fresh login',async()=>{
   await library();await context.request.post(base+'/__test/deletion-failure');const row=page.locator('.library-document').first();await row.getByRole('button',{name:'Slett',exact:true}).click();await row.getByRole('button',{name:'Bekreft sletting'}).click();
   await row.getByText('Slettingen er ikke fullført.',{exact:false}).waitFor();assert.equal((await state()).documents,1);
   await context.request.post(base+'/__test/save-restart');await login();await page.reload();await ready();await library();
   const pending=page.locator('.deleting-document');await pending.getByText('Retry document',{exact:true}).waitFor();await pending.getByRole('button',{name:'Prøv sletting igjen'}).click();await pending.waitFor({state:'detached'});assert.equal((await state()).documents,0);
   await page.locator('#library-back').click();
  });
  await save('Lost reply');
  await check('lost successful reply retries the exact operation without duplicate mutation',async()=>{
   await library();let operation;
   await page.route('**/api/v1/documents/delete',async route=>{operation=route.request().postDataJSON().operationId;await route.fetch();await route.abort();},{times:1});
   const row=page.locator('.library-document').first();await row.getByRole('button',{name:'Slett',exact:true}).click();await row.getByRole('button',{name:'Bekreft sletting'}).click();await row.getByRole('button',{name:'Prøv sletting igjen'}).waitFor({state:'visible'});await page.waitForFunction(()=>!document.querySelector('.delete-confirmation button').disabled);
   assert.equal((await state()).documents,0);let replay;
   page.once('request',()=>{});await page.route('**/api/v1/documents/delete',async route=>{replay=route.request().postDataJSON().operationId;await route.continue();},{times:1});await row.getByRole('button',{name:'Prøv sletting igjen'}).click();await row.waitFor({state:'detached'});assert.equal(replay,operation);
  });
  await check('narrow view reflows without script errors',async()=>{assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);assert.deepEqual(errors,[]);});
  console.log(`${checks} deletion browser checks passed`);
 }finally{if(browser)await browser.close();if(server){server.kill();await new Promise(r=>server.once('exit',r));}}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
