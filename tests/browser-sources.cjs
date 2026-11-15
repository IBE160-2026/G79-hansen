/* Real browser and application HTTP routes. All material/accounts are synthetic. */
const assert = require('node:assert/strict');
const {spawn} = require('node:child_process');
const path = require('node:path');
const fs = require('node:fs/promises');
const net = require('node:net');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
let count = 0;
async function check(name, action) { await action(); console.log(`PASS ${name}`); ++count; }
async function port() {
  const server = net.createServer(); await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const result = server.address().port; await new Promise(resolve => server.close(resolve)); return result;
}
async function main() {
  let server, browser, output = '';
  const errors = [], messages = [];
  try {
    const selectedPort = await port(), base = `http://127.0.0.1:${selectedPort}`;
    server = spawn(path.join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python'),
      ['-m', 'uvicorn', 'sources_browser_app:app', '--app-dir', 'tests', '--host', '127.0.0.1', '--port', String(selectedPort)],
      {cwd: root, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'], env: {...process.env, AUTH_TEST_ORIGIN: base}});
    server.stdout.on('data', chunk => { output += chunk; }); server.stderr.on('data', chunk => { output += chunk; });
    for (let attempt = 0; attempt < 100; attempt++) {
      try { if ((await fetch(`${base}/health`)).ok) break; } catch {}
      if (server.exitCode !== null) throw new Error(`Test server stopped: ${output}`);
      await pause(100);
    }
    if (process.env.DEMO_BROWSER_CHANNEL) browser = await chromium.launch({channel: process.env.DEMO_BROWSER_CHANNEL});
    else { try { browser = await chromium.launch(); } catch { browser = await chromium.launch({channel: 'msedge'}); } }
    async function context() {
      const value = await browser.newContext({viewport: {width: 1280, height: 1000}});
      value.on('page', page => {
        page.on('pageerror', error => errors.push(error.message));
        page.on('console', message => messages.push(message.text()));
      });
      return value;
    }
    const first = await context(), second = await context();
    const page = await first.newPage(), other = await second.newPage();
    async function login(current, email = 'source@example.test') {
      const state = await (await current.request.get(`${base}/api/v1/auth/status`)).json();
      const response = await current.request.post(`${base}/api/v1/auth/login`, {
        headers: {Origin: base, 'X-CSRF-Token': state.csrfToken}, data: {email, password: 'BROWSER_PRIVATE_PASSWORD'},
      });
      assert.equal(response.status(), 200);
    }
    async function ready(current) {
      await current.locator('#source-form').waitFor({state: 'visible'});
      await current.waitForFunction(() => !document.querySelector('#source-controls').disabled);
    }
    async function enter(current, value = 'PRIVATE_SOURCE_MARKER\r\n\r\nSecond 😀') {
      await current.locator('#source-kind').selectOption('paste');
      await current.locator('#source-text').fill(value);
    }
    async function accept(current) {
      await current.locator('#check-source').click();
      await current.locator('#source-preview').waitFor({state: 'visible'});
      await current.waitForFunction(() => !document.querySelector('#check-source').disabled);
    }
    async function observe(current) {
      const response = current.waitForResponse(response => response.url().endsWith('/api/v1/auth/status'));
      await current.evaluate(() => window.dispatchEvent(new Event('focus'))); await response;
    }
    await page.goto(`${base}/workspace`);
    await check('unauthenticated source entry offers login and private response headers', async () => {
      await page.locator('#source-sign-in').waitFor({state: 'visible'});
      assert.equal(await page.locator('#source-form').isVisible(), false);
      assert.equal((await first.request.get(`${base}/workspace`)).headers()['cache-control'], 'no-store');
      assert.equal((await first.request.post(`${base}/api/v1/sources/extract`, {data: {text: 'PRIVATE_SOURCE_MARKER'}})).status(), 403);
    });
    await login(first); await login(second, 'other@example.test');
    await page.reload(); await ready(page); await other.goto(`${base}/workspace`); await ready(other);
    await check('paragraph locations, independent settings, safe text rendering and keyboard focus', async () => {
      await enter(page, 'PRIVATE_SOURCE_MARKER <img src=x onerror="window.compromised=true">\n\nSecond 😀');
      await page.locator('#source-subject').fill('IBE160');
      await page.locator('#source-language').selectOption('en');
      await page.locator('#source-detail').selectOption('detailed');
      const response = page.waitForResponse(response => response.url().endsWith('/api/v1/sources/extract'));
      await page.locator('#check-source').focus(); await page.keyboard.press('Enter');
      const payload = await (await response).json();
      await page.locator('#source-preview').waitFor({state: 'visible'});
      assert.deepEqual(payload.settings, {language: 'en', detail: 'detailed', subject: 'IBE160'});
      assert.equal(payload.clientRevision > 0, true);
      assert.deepEqual(await page.locator('#source-units h3').allTextContents(), ['Avsnitt 1', 'Avsnitt 2']);
      assert.match(await page.locator('#source-units').innerText(), /<img src=x/);
      assert.equal(await page.locator('#source-units img').count(), 0);
      assert.equal(await page.evaluate(() => window.compromised), undefined);
      assert.equal(await page.evaluate(() => document.activeElement.id), 'source-preview-heading');
      const tree = await page.locator('main').ariaSnapshot();
      assert.match(tree, /heading "Avsnitt 1"/); assert.match(tree, /textbox "Tekst"/);
      await page.locator('#source-subject').focus(); await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'source-language');
    });
    await check('editing settings invalidates preview and background revalidation preserves controls', async () => {
      await page.locator('#source-subject').fill('retained subject');
      assert.equal(await page.locator('#source-preview').isVisible(), false);
      await page.locator('#source-subject').focus();
      const draft = await page.locator('#source-text').inputValue();
      await observe(page);
      assert.equal(await page.locator('#source-text').inputValue(), draft);
      assert.equal(await page.locator('#source-subject').inputValue(), 'retained subject');
      assert.equal(await page.locator('#source-language').inputValue(), 'en');
      assert.equal(await page.locator('#source-detail').inputValue(), 'detailed');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'source-subject');
      // A fan signal is observed against the server; it cannot itself end access.
      await page.evaluate(() => { const signal = new BroadcastChannel('studybuddy-session'); signal.postMessage('ended'); signal.close(); });
      await pause(150);
      assert.equal(await page.locator('#source-text').inputValue(), draft);
    });
    await check('technical failure preserves input/settings and explicit retry succeeds', async () => {
      await page.route('**/api/v1/sources/extract', route => route.fulfill({status: 503, json: {code: 'worker_failed', message: 'PRIVATE_SERVER_DIAGNOSTIC'}}), {times: 1});
      await page.locator('#check-source').click(); await page.locator('#source-error').waitFor({state: 'visible'});
      assert.equal(await page.locator('#source-subject').inputValue(), 'retained subject');
      assert.equal(await page.locator('#source-error').innerText(), 'Materialet kunne ikke behandles. Prøv igjen.');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'source-error');
      await page.locator('#source-retry').click(); await page.locator('#source-preview').waitFor({state: 'visible'});
    });
    await check('UTF-8 BOM file and retained file selection; method change allows one active input', async () => {
      await page.locator('#source-kind').selectOption('text-file');
      assert.equal(await page.locator('#source-text').inputValue(), '');
      await page.locator('#source-file').setInputFiles({name: 'PRIVATE_FILENAME.txt', mimeType: 'text/plain', buffer: Buffer.from('\ufeffFile first\r\n\r\nFile second 😀')});
      await accept(page);
      assert.deepEqual(await page.locator('#source-units .canonical-text').allTextContents(), ['File first', 'File second 😀']);
      await observe(page);
      assert.equal(await page.locator('#source-file').evaluate(input => input.files.length), 1);
      const data = await (await first.request.get(`${base}/api/v1/auth/status`)).json();
      const wrong = await second.request.post(`${base}/api/v1/sources/extract`, {headers: {Origin: base, 'X-CSRF-Token': data.csrfToken, 'X-Session-View': data.sessionViewId}, data: {text: 'PRIVATE_SOURCE_MARKER'}});
      assert.equal(wrong.status(), 403);
    });
    await check('actual contained PDF preview preserves physical gaps and text-only coverage', async () => {
      assert.equal(process.platform, 'win32', 'Required contained-PDF browser row must run on the supported Windows host');
      const pdf = Buffer.from(await (await first.request.get(`${base}/__test/source-pdf`)).body());
      await page.locator('#source-kind').selectOption('pdf');
      await page.locator('#source-file').setInputFiles({name: 'synthetic.pdf', mimeType: 'application/pdf', buffer: pdf});
      await accept(page);
      assert.deepEqual(await page.locator('#source-units h3').allTextContents(), ['Side 1', 'Side 3']);
      assert.deepEqual(await page.locator('#source-units .canonical-text').allTextContents(), ['Physical page one', 'Physical page three']);
      assert.match(await page.locator('#source-count').innerText(), /4 fysiske sider/);
      assert.match(await page.locator('#source-coverage').innerText(), /2, 4/);
      assert.match(await page.locator('#source-coverage').innerText(), /Bilder, tabeller og figurer tolkes ikke/);
    });
    await check('late success cannot restore edited or reset material', async () => {
      for (const action of ['edit', 'reset']) {
        await enter(page);
        let release, intercepted;
        const held = new Promise(resolve => { release = resolve; });
        const arrived = new Promise(resolve => { intercepted = resolve; });
        await page.route('**/api/v1/sources/extract', async route => {
          const response = await route.fetch(); intercepted(); await held;
          try { await route.fulfill({response}); } catch {}
        }, {times: 1});
        await page.locator('#check-source').click(); await arrived;
        if (action === 'edit') await page.locator('#source-text').fill('New draft');
        else await page.locator('#reset-source').click();
        release(); await pause(200);
        assert.equal(await page.locator('#source-preview').isVisible(), false);
        assert.equal(await page.locator('#source-text').inputValue(), action === 'edit' ? 'New draft' : '');
      }
      assert.equal(await page.locator('#source-file').evaluate(input => input.files.length), 0);
      assert.equal(await page.locator('#source-subject').inputValue(), '');
      assert.equal(await page.locator('#source-language').inputValue(), 'nb');
      assert.equal(await page.locator('#source-detail').inputValue(), 'short');
    });
    await check('same-account relogin clears old drafts and stale success', async () => {
      await enter(page);
      let release, intercepted;
      const held = new Promise(resolve => { release = resolve; }), arrived = new Promise(resolve => { intercepted = resolve; });
      await page.route('**/api/v1/sources/extract', async route => {
        const response = await route.fetch(); intercepted(); await held; try { await route.fulfill({response}); } catch {}
      }, {times: 1});
      await page.locator('#check-source').click(); await arrived;
      await login(first); await observe(page); await ready(page);
      assert.equal(await page.locator('#source-text').inputValue(), '');
      release(); await pause(200);
      assert.equal(await page.locator('#source-preview').isVisible(), false);
    });
    await check('320px and 200% reflow, labelled controls and visible keyboard focus', async () => {
      await enter(page, 'PRIVATE_SOURCE_MARKER ' + 'longword'.repeat(120)); await accept(page);
      await fs.mkdir(path.join(root, 'test-results'), {recursive: true});
      for (const width of [320, 640]) {
        await page.setViewportSize({width, height: 900});
        await page.evaluate(zoom => { document.documentElement.style.zoom = String(zoom); }, width === 640 ? 2 : 1);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true);
        await page.locator('#check-source').focus();
        const outline = await page.locator('#check-source').evaluate(element => getComputedStyle(element).outlineWidth);
        assert.notEqual(outline, '0px');
        await page.screenshot({path: path.join(root, 'test-results', `sources-${width}.png`), fullPage: true});
      }
      await page.evaluate(() => { document.documentElement.style.zoom = ''; }); await page.setViewportSize({width: 1280, height: 1000});
    });
    await check('pagehide clears private inputs/display and restoration revalidates', async () => {
      await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pagehide')));
      assert.equal(await page.locator('#source-text').inputValue(), '');
      assert.equal(await page.locator('#source-preview').isVisible(), false);
      await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pageshow', {persisted: true})));
      await ready(page); assert.equal(await page.locator('#source-text').inputValue(), '');
    });
    await check('logout fan observation clears active drafts while another browser stays independent', async () => {
      await enter(page); await accept(page); await enter(other, 'OTHER_PRIVATE_SOURCE'); await accept(other);
      const account = await first.newPage(); await account.goto(`${base}/account`);
      await account.locator('#account-signed-in').waitFor({state: 'visible'});
      await account.locator('#account-signed-in [data-account-logout]').click();
      await page.locator('#source-sign-in').waitFor({state: 'visible'});
      assert.equal(await page.locator('#source-text').inputValue(), '');
      assert.equal(await page.locator('#source-preview').isVisible(), false);
      assert.equal(await other.locator('#source-preview').isVisible(), true);
      await account.close();
    });
    await check('provider denial, expiry and server restart clear private drafts/display', async () => {
      for (const scenario of ['provider-denial', 'deadline', 'restart']) {
        await login(first); await page.reload(); await ready(page); await enter(page); await accept(page);
        await first.request.post(`${base}/__test/${scenario}`);
        await observe(page);
        if (scenario === 'deadline') await page.waitForTimeout(1200);
        await page.locator('#source-sign-in').waitFor({state: 'visible'});
        assert.equal(await page.locator('#source-text').inputValue(), '');
        assert.equal(await page.locator('#source-preview').isVisible(), false);
      }
    });
    await check('focus during post-extraction observation still renders the accepted source', async () => {
      await login(first); await page.reload(); await ready(page); await enter(page);
      let release, entered;
      const held = new Promise(resolve => { release = resolve; });
      const arrived = new Promise(resolve => { entered = resolve; });
      await page.route('**/api/v1/auth/status', async route => {
        const response = await route.fetch(); entered(); await held;
        try { await route.fulfill({response}); } catch {}
      }, {times: 1});
      await page.locator('#check-source').click(); await arrived;
      await page.evaluate(() => window.dispatchEvent(new Event('focus')));
      release();
      await page.locator('#source-preview').waitFor({state: 'visible'});
      assert.match(await page.locator('#source-units').innerText(), /PRIVATE_SOURCE_MARKER/);
      assert.match(await page.locator('#source-status').innerText(), /kontrollert/);
    });
    await check('old uncancellable authenticated observation cannot reopen access after a source denial', async () => {
      await login(first); await page.reload(); await ready(page); await enter(page);
      await page.evaluate(() => {
        const original = window.fetch.bind(window);
        window.fetch = (url, options) => {
          if (url.endsWith('/api/v1/auth/status')) { const {signal, ...rest} = options; return original(url, rest); }
          return original(url, options);
        };
      });
      let release, entered;
      const held = new Promise(resolve => { release = resolve; });
      const arrived = new Promise(resolve => { entered = resolve; });
      await page.route('**/api/v1/auth/status', async route => {
        const response = await route.fetch(); entered(); await held;
        try { await route.fulfill({response}); } catch {}
      }, {times: 1});
      await page.evaluate(() => window.dispatchEvent(new Event('focus'))); await arrived;
      await first.request.post(`${base}/__test/provider-denial`);
      await page.locator('#check-source').click();
      await page.locator('#source-sign-in').waitFor({state: 'visible'});
      release(); await pause(200);
      assert.equal(await page.locator('#source-form').isVisible(), false);
      assert.equal(await page.locator('#source-text').inputValue(), '');
      assert.equal(await page.locator('#source-sign-in').isVisible(), true);
    });
    await check('workspace logout is acknowledged once and ends authority and private state', async () => {
      await login(first); await page.reload(); await ready(page); await enter(page); await accept(page);
      let calls = 0;
      const listener = request => { if (request.url().endsWith('/api/v1/auth/logout')) ++calls; };
      page.on('request', listener);
      const acknowledged = page.waitForResponse(r => r.url().endsWith('/api/v1/auth/logout'));
      await page.locator('#source-logout').evaluate(button => { button.click(); button.click(); });
      assert.equal((await acknowledged).status(), 200);
      await page.locator('#source-sign-in').waitFor({state: 'visible'});
      await page.waitForFunction(() => document.querySelector('#source-status').textContent.includes('logget ut'));
      assert.equal(calls, 1); page.off('request', listener);
      assert.equal(await page.locator('#source-text').inputValue(), '');
      assert.equal(await page.locator('#source-preview').isVisible(), false);
      assert.equal((await (await first.request.get(`${base}/api/v1/auth/status`)).json()).authenticated, false);
      assert.equal((await first.cookies()).some(c => c.name.startsWith('sb_session')), false);
    });
    await check('failed workspace logout retains POST retry across focus and page restoration', async () => {
      await login(first); await page.reload(); await ready(page); await enter(page); await accept(page);
      await page.route('**/api/v1/auth/logout', route => route.abort(), {times: 1});
      await page.locator('#source-logout').click();
      await page.locator('#source-error').waitFor({state: 'visible'});
      assert.equal((await (await first.request.get(`${base}/api/v1/auth/status`)).json()).authenticated, true);
      await page.evaluate(() => {
        window.dispatchEvent(new Event('focus'));
        window.dispatchEvent(new PageTransitionEvent('pagehide'));
        window.dispatchEvent(new PageTransitionEvent('pageshow', {persisted: true}));
      });
      assert.equal(await page.locator('#source-form').isVisible(), false);
      assert.equal(await page.locator('#source-text').inputValue(), '');
      assert.equal(await page.locator('#source-retry').isVisible(), true);
      assert.equal(await page.locator('#source-retry').isEnabled(), true);
      const acknowledged = page.waitForResponse(r => r.url().endsWith('/api/v1/auth/logout'));
      await page.locator('#source-retry').click(); assert.equal((await acknowledged).status(), 200);
      await page.waitForFunction(() => document.querySelector('#source-status').textContent.includes('logget ut'));
      assert.equal((await (await first.request.get(`${base}/api/v1/auth/status`)).json()).authenticated, false);
    });
    await check('workspace logout retry token acquisition has a bounded deadline', async () => {
      await login(first); await page.reload(); await ready(page); await enter(page);
      await page.route('**/api/v1/auth/logout', route => route.abort(), {times: 1});
      await page.locator('#source-logout').click(); await page.locator('#source-error').waitFor({state: 'visible'});
      await page.clock.install();
      let pending, entered;
      const arrived = new Promise(resolve => { entered = resolve; });
      await page.route('**/api/v1/auth/status', route => { pending = route; entered(); }, {times: 1});
      await page.locator('#source-retry').click(); await arrived;
      await page.clock.fastForward(15001);
      await page.locator('#source-error').waitFor({state: 'visible'});
      assert.equal(await page.locator('#source-retry').isEnabled(), true);
      assert.equal(await page.locator('#source-form').isVisible(), false);
      await pending.abort().catch(() => {}); await page.clock.resume();
      const acknowledged = page.waitForResponse(r => r.url().endsWith('/api/v1/auth/logout'));
      await page.locator('#source-retry').click(); assert.equal((await acknowledged).status(), 200);
      await page.waitForFunction(() => document.querySelector('#source-status').textContent.includes('logget ut'));
    });
    await check('oversized canonical paste is rejected before serialization or a source request', async () => {
      await login(first); await page.reload(); await ready(page);
      let requests = 0;
      const listener = request => { if (request.url().endsWith('/api/v1/sources/extract')) ++requests; };
      page.on('request', listener);
      await enter(page, '😀'.repeat(30001));
      await page.locator('#check-source').click(); await page.locator('#source-error').waitFor({state: 'visible'});
      assert.match(await page.locator('#source-error').innerText(), /30 000/);
      assert.equal(requests, 0);
      assert.equal([...(await page.locator('#source-text').inputValue())].length, 30001);
      await enter(page, '😀'.repeat(30000)); await accept(page);
      assert.equal(requests, 1); page.off('request', listener);
      assert.match(await page.locator('#source-count').innerText(), /30000 tegn/);
    });
    const modelState = async () => (await first.request.get(`${base}/__test/model-state`)).json();
    async function generatePrivate() {
      await page.locator('#generate').click();
      await page.locator('#results').waitFor({state: 'visible'});
      await page.waitForFunction(() => !document.querySelector('#generate').disabled);
    }
    await check('one primary action extracts and generates once, collapses controls and renders safe sections', async () => {
      await enter(page, 'Synthetic source for generation.\n\nSecond source paragraph.');
      const before = (await modelState()).calls;
      await page.locator('#generate').evaluate(button => { button.click(); button.click(); });
      await page.locator('#results').waitFor({state: 'visible'});
      assert.equal((await modelState()).calls, before + 1);
      assert.equal(await page.locator('#material-body').isVisible(), false);
      assert.equal(await page.locator('#edit-material').isVisible(), true);
      assert.equal(await page.locator('#tab-summary').getAttribute('aria-selected'), 'true');
      assert.match(await page.locator('#content').innerText(), /Synthetic summary <img/);
      assert.equal(await page.locator('#content img').count(), 0);
      assert.equal(await page.evaluate(() => window.compromised), undefined);
      await page.locator('#edit-material').click();
      assert.equal(await page.locator('#results').isVisible(), true);
      assert.match(await page.locator('#source-text').inputValue(), /Synthetic source/);
    });
    await check('practice positions and reveals are independent, accessible and make no model requests', async () => {
      const before = (await modelState()).calls;
      await page.locator('#tab-flashcards').focus(); await page.keyboard.press('Enter');
      assert.equal(await page.locator('#answer').isVisible(), false);
      await page.locator('#reveal').click(); assert.equal(await page.locator('#answer').isVisible(), true);
      assert.match(await page.locator('#answer').innerText(), /Avsnitt 1/);
      await page.locator('#next').click(); assert.equal(await page.locator('#answer').isVisible(), false);
      await page.locator('#tab-quiz').click(); await page.locator('#reveal').click();
      await page.locator('#tab-flashcards').click(); assert.match(await page.locator('#content').innerText(), /Kort 2 av 2/);
      await page.locator('#previous').click(); assert.equal(await page.locator('#answer').isVisible(), true);
      await page.locator('#tab-quiz').focus(); await page.keyboard.press('Home');
      assert.equal(await page.locator('#tab-summary').getAttribute('aria-selected'), 'true');
      assert.equal((await modelState()).calls, before);
    });
    await check('generation failure retains selected file and settings; retry and regeneration reset reveals', async () => {
      await page.locator('#source-kind').selectOption('text-file');
      await page.locator('#source-file').setInputFiles({name: 'PRIVATE_FILENAME.txt', mimeType: 'text/plain', buffer: Buffer.from('Synthetic source file')});
      await page.locator('#source-language').selectOption('en'); await page.locator('#source-detail').selectOption('detailed');
      await page.locator('#source-subject').fill('retained generation settings');
      await first.request.post(`${base}/__test/model-failure`);
      await page.locator('#generate').click(); await page.locator('#source-error').waitFor({state: 'visible'});
      assert.equal(await page.locator('#results').isVisible(), false);
      assert.equal(await page.locator('#material-body').isVisible(), true);
      assert.equal(await page.locator('#source-file').evaluate(input => input.files.length), 1);
      assert.equal(await page.locator('#source-language').inputValue(), 'en');
      assert.equal(await page.locator('#source-detail').inputValue(), 'detailed');
      assert.equal(await page.locator('#source-subject').inputValue(), 'retained generation settings');
      await page.locator('#source-retry').click(); await page.locator('#results').waitFor({state: 'visible'});
      assert.deepEqual((await modelState()).settings, {language: 'en', detail: 'detailed'});
      await page.locator('#tab-flashcards').click(); assert.equal(await page.locator('#answer').isVisible(), false);
      await page.locator('#reveal').click(); await page.locator('#edit-material').click(); await generatePrivate();
      await page.locator('#tab-flashcards').click(); assert.equal(await page.locator('#answer').isVisible(), false);
    });
    await check('insufficient sections keep tabs and explanations without invented practice navigation', async () => {
      await page.locator('#edit-material').click(); await first.request.post(`${base}/__test/model-insufficient`);
      await generatePrivate();
      for (const name of ['summary', 'concepts', 'flashcards', 'quiz']) {
        await page.locator(`#tab-${name}`).click();
        assert.match(await page.locator('#content').innerText(), /not contain enough evidence/);
        assert.equal(await page.locator('#reveal').count(), 0); assert.equal(await page.locator('#next').count(), 0);
      }
      await page.locator('#edit-material').click();
    });
    await check('failed invalidation blocks generation until an explicit retry acknowledges edits', async () => {
      const before = (await modelState()).calls;
      await page.route('**/api/v1/workspaces/invalidate', route => route.abort());
      await page.locator('#source-subject').fill('changed subject'); await page.locator('#generate').click();
      await page.locator('#source-error').waitFor({state: 'visible'});
      assert.equal((await modelState()).calls, before);
      assert.equal(await page.locator('#results').isVisible(), false);
      await page.unroute('**/api/v1/workspaces/invalidate');
      await page.locator('#source-retry').click(); await page.locator('#results').waitFor({state: 'visible'});
      assert.equal((await modelState()).calls, before + 1);
    });
    await check('subject Enter generates once; partial insufficiency and prose languages survive reversible disclosure', async () => {
      if (await page.locator('#material-body').isHidden()) await page.locator('#edit-material').click();
      const pdf = Buffer.from(await (await first.request.get(`${base}/__test/source-pdf`)).body());
      await page.locator('#source-kind').selectOption('pdf');
      await page.locator('#source-file').setInputFiles({name: 'locale-synthetic.pdf', mimeType: 'application/pdf', buffer: pdf});
      await page.locator('#source-language').selectOption('en');
      await page.locator('#source-subject').fill('Synthetic language and insufficiency check');
      await page.route('**/api/v1/generation', async route => {
        const response = await route.fetch(), body = await response.json();
        body.bundle.warnings.push('A generated English warning.');
        for (const name of ['summary', 'concepts', 'flashcards', 'quiz']) body.bundle.insufficiency[name] = 'Some source evidence is unavailable.';
        await route.fulfill({response, json: body});
      }, {times: 1});
      const before = (await modelState()).calls;
      await page.locator('#source-subject').focus(); await page.keyboard.press('Enter');
      await page.locator('#results').waitFor({state: 'visible'});
      assert.equal((await modelState()).calls, before + 1);
      assert.deepEqual(await page.locator('#generation-warnings p').evaluateAll(nodes => nodes.map(node => node.lang)), ['nb', 'nb', 'en']);
      for (const name of ['summary', 'concepts', 'flashcards', 'quiz']) {
        await page.locator(`#tab-${name}`).click();
        assert.equal(await page.locator('#content .section-insufficiency').getAttribute('lang'), 'en');
        assert.equal(await page.locator('#content h2').getAttribute('lang'), 'nb');
        assert.match(await page.locator('#content').innerText(), /Some source evidence is unavailable/);
        if (name === 'summary') assert.equal(await page.locator('#content > p[lang="en"]').count(), 2);
        else assert.equal(await page.locator('#content h3').getAttribute('lang'), 'en');
        if (name === 'flashcards' || name === 'quiz') {
          await page.locator('#reveal').click();
          assert.equal(await page.locator('#answer p:not(.reference)').getAttribute('lang'), 'en');
          assert.equal(await page.locator('#reveal').getAttribute('lang'), 'nb');
          assert.equal(await page.locator('#answer strong').getAttribute('lang'), 'nb');
        }
        assert.equal(await page.locator('#content .reference').first().getAttribute('lang'), 'nb');
      }
      await page.locator('#next').click();
      assert.equal(await page.locator('#source-status span[lang="en"]').count(), 1);
      await page.locator('#previous').click();
      const content = await page.locator('#content').innerText();
      await page.locator('#edit-material').click();
      assert.equal(await page.locator('#edit-material').getAttribute('aria-expanded'), 'true');
      assert.equal(await page.locator('#edit-material').isVisible(), true);
      await page.locator('#edit-material').click();
      assert.equal(await page.locator('#edit-material').getAttribute('aria-expanded'), 'false');
      assert.equal(await page.locator('#material-body').isVisible(), false);
      assert.equal(await page.locator('#content').innerText(), content);
      assert.equal(await page.locator('#answer').isVisible(), true);
      assert.equal((await modelState()).calls, before + 1);
    });
    await check('late uncancellable generation replies cannot revive edited, reset, ended or rotated sessions', async () => {
      for (const action of ['edit', 'reset', 'pagehide', 'rotate', 'logout']) {
        if (await page.locator('#edit-material').isVisible()) await page.locator('#edit-material').click();
        await enter(page, 'Synthetic source before late completion');
        await page.evaluate(() => {
          if (window.originalGenerationFetch) return;
          window.originalGenerationFetch = window.fetch.bind(window);
          window.fetch = (url, options) => {
            if (url === '/api/v1/generation') { const {signal, ...rest} = options; return window.originalGenerationFetch(url, rest); }
            return window.originalGenerationFetch(url, options);
          };
        });
        let release, intercepted;
        const held = new Promise(resolve => { release = resolve; }), arrived = new Promise(resolve => { intercepted = resolve; });
        await page.route('**/api/v1/generation', async route => {
          const response = await route.fetch(); intercepted(); await held; try { await route.fulfill({response}); } catch {}
        }, {times: 1});
        await page.locator('#generate').click(); await arrived;
        if (action === 'edit') await page.locator('#source-text').fill('new draft');
        else if (action === 'reset') await page.locator('#reset-source').click();
        else if (action === 'pagehide') await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pagehide')));
        else if (action === 'rotate') { await login(first); await observe(page); }
        else await page.locator('#source-logout').click();
        release(); await pause(150);
        assert.equal(await page.locator('#results').isVisible(), false);
        if (action === 'pagehide') { await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pageshow', {persisted: true}))); await ready(page); }
        if (action === 'rotate') await ready(page);
      }
      await login(first); await page.reload(); await ready(page);
    });
    await check('browser generation deadline fences an uncancellable reply and keeps the draft', async () => {
      await enter(page, 'Synthetic deadline source');
      await page.evaluate(() => {
        const original = window.fetch.bind(window);
        window.fetch = (url, options) => {
          if (url === '/api/v1/generation') { const {signal, ...rest} = options; return original(url, rest); }
          return original(url, options);
        };
      });
      let release, intercepted;
      const held = new Promise(resolve => { release = resolve; }), arrived = new Promise(resolve => { intercepted = resolve; });
      await page.route('**/api/v1/generation', async route => {
        const response = await route.fetch(); intercepted(); await held; try { await route.fulfill({response}); } catch {}
      }, {times: 1});
      await page.clock.install(); await page.locator('#generate').click(); await arrived;
      // Passive session checks stay valid; the generation wait expires at 70s.
      await page.clock.fastForward(70001);
      await page.locator('#source-error').waitFor({state: 'visible'});
      assert.equal(await page.locator('#source-text').inputValue(), 'Synthetic deadline source');
      assert.equal(await page.locator('#generate').isEnabled(), true);
      release(); await pause(150); assert.equal(await page.locator('#results').isVisible(), false);
      await page.clock.resume();
    });
    await check('generated content reflows at 320px and 200% with keyboard flow intact', async () => {
      await generatePrivate();
      for (const width of [320, 640]) {
        await page.setViewportSize({width, height: 900});
        await page.evaluate(zoom => { document.documentElement.style.zoom = String(zoom); }, width === 640 ? 2 : 1);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true);
        await page.locator('#tab-summary').focus(); await page.keyboard.press('End');
        assert.equal(await page.locator('#tab-quiz').getAttribute('aria-selected'), 'true');
        await page.screenshot({path: path.join(root, 'test-results', `generation-${width}.png`), fullPage: true});
      }
      await page.evaluate(() => { document.documentElement.style.zoom = ''; }); await page.setViewportSize({width: 1280, height: 1000});
    });
    await check('private material stays outside browser storage, logs and demo requests', async () => {
      assert.equal(await page.evaluate(() => JSON.stringify({...localStorage, ...sessionStorage})), '{}');
      const demo = await first.newPage(), requests = [];
      demo.on('request', request => { if (request.url().includes('/api/v1/demo/')) requests.push(request.postData() || ''); });
      await demo.goto(base); await demo.locator('#generate:not(:disabled)').waitFor(); await demo.locator('#generate').click();
      await demo.locator('#results').waitFor({state: 'visible'});
      assert.equal(requests.some(value => value.includes('PRIVATE_SOURCE_MARKER')), false);
      assert.equal(output.includes('PRIVATE_SOURCE_MARKER') || output.includes('PRIVATE_FILENAME'), false);
      assert.equal(messages.some(value => value.includes('PRIVATE_SOURCE_MARKER') || value.includes('PRIVATE_SERVER_DIAGNOSTIC')), false);
      assert.deepEqual(errors, []);
    });
    console.log(`${count} browser source checks passed`);
  } finally {
    if (browser) await browser.close();
    if (server && server.exitCode === null) {
      server.kill(); await Promise.race([new Promise(resolve => server.once('exit', resolve)), pause(3000)]);
    }
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
