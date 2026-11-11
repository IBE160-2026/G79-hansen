const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(__dirname+'/key-study.html','utf8');
const elements=new Map();let document;
function element(id){if(!elements.has(id))elements.set(id,{id,value:'',selectedIndex:0,hidden:false,disabled:false,files:[],dataset:{},attrs:{},classList:{toggle(){}},setAttribute(k,v){this.attrs[k]=String(v)},focus(){document.activeElement=this},contains(el){return ['generate','material','subject','language','detail','reset'].includes(el?.id)},addEventListener(){}});return elements.get(id)}
for(const m of html.matchAll(/id="([^"]+)"/g))element(m[1]);
element('material').value='Example source';
const tabs=['summary','concepts','cards','quiz'].map(t=>{const el=element('tab-'+t);el.dataset.tab=t;return el});
Object.defineProperty(element('content'),'innerHTML',{set(v){this.html=v;for(const m of v.matchAll(/<button id="([^"]+)"([^>]*)>/g)){const el=element(m[1]);el.disabled=m[2].includes('disabled')}if(v.includes('id="answer"'))element('answer').hidden=/id="answer"[^>]*hidden/.test(v)},get(){return this.html}});
let nextTimer,details={open:false};
document={activeElement:null,getElementById:element,querySelectorAll:()=>tabs,querySelector:()=>details};
const context=vm.createContext({document,console,setTimeout:fn=>(nextTimer=fn,1),clearTimeout:()=>{nextTimer=null}});
vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)?.[1]||html.slice(html.indexOf('<script>')+8,html.indexOf('</script>')),context);
const run=s=>vm.runInContext(s,context),$=element;
assert.equal($('material-body').hidden,false);assert.equal($('results').hidden,true);
$('generate').focus();$('generate').onclick();assert.equal($('generate').disabled,true);nextTimer();
assert.equal($('material-body').hidden,true);assert.equal(document.activeElement.id,'edit-material');assert.equal($('results').hidden,false);
$('tab-cards').onclick();$('reveal').onclick();assert.equal($('answer').hidden,false);$('next').onclick();assert.equal(run('positions.cards'),1);assert.equal($('answer').hidden,true);
$('tab-quiz').onclick();$('next').onclick();assert.equal(run('positions.quiz'),1);$('tab-cards').onclick();assert.equal(run('positions.cards'),1);$('previous').onclick();assert.equal($('answer').hidden,false);
$('edit-material').onclick();assert.equal($('material-body').hidden,false);assert.equal(run('positions.cards'),0);
$('reset').onclick();assert.equal($('material').value,'');assert.equal($('results').hidden,true);assert.equal($('material-body').hidden,false);assert.equal($('language').selectedIndex,0);assert.equal($('detail').selectedIndex,0);
$('generate').onclick();assert.equal($('generate').disabled,false);assert.match($('status').textContent,/Legg inn/);
$('material').value='x'.repeat(30001);$('generate').onclick();assert.match($('status').textContent,/30 000/);assert.equal($('material-body').hidden,false);
console.log('PASS: initial state, busy/success, collapse focus, independent tab positions, reveal persistence, edit preservation, reset, empty and oversized input. Node DOM stub, not browser rendering/accessibility test.');

$('material').value='Preserved input';$('subject').value='IBE160';$('language').selectedIndex=1;
$('example-state').value='error';$('preview-state').onclick();assert.equal($('retry').hidden,false);assert.equal($('material-body').hidden,false);assert.equal($('results').hidden,true);
$('retry').onclick();assert.equal($('generate').disabled,true);nextTimer();assert.equal($('results').hidden,false);assert.equal($('retry').hidden,true);assert.equal($('material').value,'Preserved input');assert.equal($('subject').value,'IBE160');assert.equal($('language').selectedIndex,1);
$('example-state').value='partial';$('preview-state').onclick();assert.match($('state-message').textContent,/2 og 4/);assert.match($('content').innerHTML,/Side 3/);$('tab-quiz').onclick();$('reveal').onclick();assert.match($('content').innerHTML,/Side 3/);
$('example-state').value='unreadable';$('preview-state').onclick();assert.equal($('results').hidden,true);assert.equal($('material-body').hidden,false);assert.equal($('retry').hidden,true);
$('example-state').value='insufficient';$('preview-state').onclick();for(const tab of tabs){tab.onclick();assert.match($('content').innerHTML,/ikke nok grunnlag/);assert.doesNotMatch($('content').innerHTML,/id="next"|1 av 0/);}
$('reset').onclick();assert.equal($('state-notice').hidden,true);assert.equal($('material').value,'');
console.log('PASS: error/retry preserves inputs/settings, partial-PDF page references, unreadable PDF blocks results, insufficiency in all tabs without fake navigation, reset clears notices.');

$('example-state').value='normal';$('preview-state').onclick();$('save').onclick();$('tab-cards').onclick();$('next').onclick();$('tab-quiz').onclick();$('next').onclick();$('reset').onclick();$('resume-demo').onclick();assert.equal(run('positions.cards'),1);assert.equal(run('positions.quiz'),1);assert.equal($('results').hidden,false);console.log('PASS: saved fixed example resumes independent card/quiz positions after workspace reset; in-memory prototype only.');

$('login-open').onclick();assert.equal($('auth-panel').hidden,false);assert.equal($('study-workspace').hidden,true);$('auth-signup').onclick();$('auth-submit').onclick();assert.match($('auth-message').textContent,/Demo:/);$('auth-back-login').onclick();$('auth-forgot').onclick();$('auth-submit').onclick();assert.match($('auth-message').textContent,/ingen e-post/);$('auth-back-login').onclick();$('auth-submit').onclick();assert.equal($('logout').hidden,false);assert.equal($('study-workspace').hidden,false);$('logout').onclick();assert.equal($('login-open').hidden,false);assert.equal($('results').hidden,true);assert.equal(run('savedDemo'),null);console.log('PASS: simulated signup/recovery/login/logout, no-email messages, private-view and saved-fixture clearing. No actual authentication test.');

$('library-open').onclick();assert.equal($('library-empty').hidden,false);$('library-back').onclick();
$('subject').value='Document A';$('example-state').value='normal';$('preview-state').onclick();$('save').onclick();const firstId=run('savedDemo.id');$('tab-cards').onclick();$('next').onclick();
$('reset').onclick();$('subject').value='<Document B>';$('preview-state').onclick();$('save').onclick();const secondId=run('savedDemo.id');assert.notEqual(firstId,secondId);
$('library-open').onclick();assert.equal(run('demoDocuments.length'),2);assert.match($('library-list').innerHTML,/&lt;Document B&gt;/);$('open-document-'+firstId).onclick();assert.equal(run('positions.cards'),1);assert.equal($('subject').value,'Document A');assert.equal($('library-panel').hidden,true);
$('library-open').onclick();$('delete-document-'+firstId).onclick();assert.equal($('delete-panel').hidden,false);$('delete-cancel').onclick();assert.equal(run('demoDocuments.length'),2);$('delete-document-'+firstId).onclick();$('delete-confirm').onclick();assert.equal(run('demoDocuments.length'),1);assert.equal($('results').hidden,true);assert.equal(run('savedDemo'),null);
$('open-document-'+secondId).onclick();assert.equal(run('positions.cards'),0);$('library-open').onclick();$('delete-document-'+secondId).onclick();$('delete-confirm').onclick();assert.equal($('library-empty').hidden,false);console.log('PASS: library empty/list, multiple documents, escaped titles, owner-fixture reopen/progress, cancel/delete and active-view clearing. In-memory examples only.');
