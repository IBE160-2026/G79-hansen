/* Real browser + real application HTTP routes, explicitly test-only provider adapter. */
const assert = require('node:assert/strict');
const {spawn} = require('node:child_process');
const path = require('node:path');
const net = require('node:net');
const fs = require('node:fs/promises');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
const password = 'BROWSER_PRIVATE_PASSWORD';
let count = 0;
async function check(name, action) { await action(); console.log(`PASS ${name}`); count++; }
async function freePort() {
  const socket = net.createServer();
  await new Promise(resolve => socket.listen(0, '127.0.0.1', resolve));
  const port = socket.address().port;
  await new Promise(resolve => socket.close(resolve));
  return port;
}
async function fill(page, action, email, secret = password) {
  await page.locator(`#${action}-email`).fill(email);
  await page.locator(`#${action}-password`).fill(secret);
}
async function submit(page, action) { await page.locator(`#${action}-form button`).click(); }
async function ready(page) { await page.locator('#account-forms').waitFor({state: 'visible'}); }

async function main() {
  let server, browser, output = '', baseURL;
  const messages = [], errors = [];
  try {
    const port = await freePort();
    baseURL = `http://127.0.0.1:${port}`;
    const python = path.join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
    server = spawn(python, ['-m', 'uvicorn', 'auth_browser_app:app', '--app-dir', 'tests', '--host', '127.0.0.1', '--port', String(port)], {
      cwd: root, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'], env: {...process.env, AUTH_TEST_ORIGIN: baseURL},
    });
    server.stdout.on('data', data => { output += data; });
    server.stderr.on('data', data => { output += data; });
    for (let i = 0; i < 100; i++) {
      try { if ((await fetch(`${baseURL}/health`)).ok) break; } catch {}
      if (server.exitCode !== null) throw new Error(`Test server stopped: ${output}`);
      await pause(100);
    }
    if (process.env.DEMO_BROWSER_CHANNEL) browser = await chromium.launch({channel: process.env.DEMO_BROWSER_CHANNEL});
    else { try { browser = await chromium.launch(); } catch { browser = await chromium.launch({channel: 'msedge'}); } }
    const first = await browser.newContext({viewport: {width: 1280, height: 1000}});
    const second = await browser.newContext({viewport: {width: 1280, height: 1000}});
    for (const context of [first, second]) {
      context.on('page', page => {
        page.on('console', message => messages.push(message.text()));
        page.on('pageerror', error => errors.push(error.message));
      });
    }
    const page = await first.newPage();
    const other = await second.newPage();
    await page.goto(`${baseURL}/account`);
    await ready(page);
    await other.goto(`${baseURL}/account`);
    await ready(other);

    await check('Norwegian labels, autocomplete, status headers and accessible form controls', async () => {
      assert.equal(await page.getByLabel('E-post', {exact: true}).count(), 2);
      assert.equal(await page.locator('#login-password').getAttribute('autocomplete'), 'current-password');
      assert.equal(await page.locator('#signup-password').getAttribute('autocomplete'), 'new-password');
      const response = await first.request.get(`${baseURL}/api/v1/auth/status`);
      assert.equal(response.headers()['cache-control'], 'no-store');
      assert.equal(response.headers()['referrer-policy'], 'no-referrer');
      const tree = await page.locator('main').ariaSnapshot();
      assert.match(tree, /heading "Konto"/);
      assert.match(tree, /textbox "E-post"/);
    });

    await check('real browser context rejects missing/wrong Origin and CSRF before signup', async () => {
      const status = await (await first.request.get(`${baseURL}/api/v1/auth/status`)).json();
      for (const protection of [{}, {Origin: 'https://attacker.test', 'X-CSRF-Token': status.csrfToken}, {Origin: baseURL, 'X-CSRF-Token': 'wrong'}]) {
        const response = await first.request.post(`${baseURL}/api/v1/auth/signup`, {headers: protection, data: {email: 'first@example.test', password}});
        assert.equal(response.status(), 403);
        assert.equal(response.headers()['cache-control'], 'no-store');
      }
      assert.deepEqual(await (await fetch(`${baseURL}/__test/links`)).json(), []);
    });

    await check('signup clears password, stays unauthenticated and supports independent attempts', async () => {
      for (let i = 0; i < 2; i++) {
        await fill(page, 'signup', 'first@example.test');
        await submit(page, 'signup');
        await page.waitForFunction(() => document.getElementById('account-status').textContent.includes('får du en e-post'));
        assert.equal(await page.locator('#signup-password').inputValue(), '');
        assert.equal(await page.locator('#signup-email').inputValue(), 'first@example.test');
      }
      const links = await (await fetch(`${baseURL}/__test/links`)).json();
      assert.equal(links.length, 2);
      assert.notEqual(links[0].url, links[1].url);
      assert.equal((await first.cookies()).some(cookie => cookie.name === 'sb_session'), false);
    });

    await check('wrong browser cannot consume confirmation; correct browser confirms and replay fails cleanly', async () => {
      const links = await (await fetch(`${baseURL}/__test/links`)).json();
      await other.goto(links[0].url);
      await other.locator('#account-error').waitFor({state: 'visible'});
      assert.match(await other.locator('#account-error').innerText(), /samme nettleser/);
      assert.equal(new URL(other.url()).search, '');
      await page.goto(links[0].url);
      await page.locator('#account-signed-in').waitFor({state: 'visible'});
      assert.equal(await page.locator('#account-email').innerText(), 'first@example.test');
      assert.equal(page.url(), `${baseURL}/account`);
      const original = (await first.cookies()).find(cookie => cookie.name === 'sb_session').value;
      await page.goto(links[0].url);
      await page.locator('#account-error').waitFor({state: 'visible'});
      assert.equal(page.url(), `${baseURL}/account`);
      await page.goto(links[1].url);
      await page.locator('#account-signed-in').waitFor({state: 'visible'});
      const rotated = (await first.cookies()).find(cookie => cookie.name === 'sb_session').value;
      assert.notEqual(rotated, original);
    });

    await check('login error focuses safe message, retains email and clears password; browsers stay independent', async () => {
      await other.goto(`${baseURL}/account`);
      await ready(other);
      await fill(other, 'login', 'second@example.test', 'wrong-password');
      await submit(other, 'login');
      await other.locator('#account-error').waitFor({state: 'visible'});
      assert.equal(await other.evaluate(() => document.activeElement.id), 'account-error');
      assert.equal(await other.locator('#login-email').inputValue(), 'second@example.test');
      assert.equal(await other.locator('#login-password').inputValue(), '');
      await fill(other, 'login', 'second@example.test');
      await submit(other, 'login');
      await other.locator('#account-signed-in').waitFor({state: 'visible'});
      assert.equal(await other.locator('#account-email').innerText(), 'second@example.test');
      await page.reload();
      await page.locator('#account-signed-in').waitFor({state: 'visible'});
      assert.equal(await page.locator('#account-email').innerText(), 'first@example.test');
      assert.notEqual((await first.cookies()).find(c => c.name === 'sb_session').value, (await second.cookies()).find(c => c.name === 'sb_session').value);
    });

    await check('opaque HttpOnly cookies and no tokens/passwords in browser storage, DOM, URL or output', async () => {
      for (const [context, current] of [[first, page], [second, other]]) {
        const cookies = await context.cookies();
        for (const cookie of cookies.filter(c => ['sb_session', 'sb_browser'].includes(c.name))) {
          assert.equal(cookie.httpOnly, true);
          assert.equal(cookie.sameSite, 'Lax');
          assert.doesNotMatch(cookie.value, /BROWSER_PRIVATE/);
        }
        const stored = await current.evaluate(() => ({local: {...localStorage}, session: {...sessionStorage}, cookies: document.cookie}));
        assert.deepEqual(stored, {local: {}, session: {}, cookies: ''});
        assert.doesNotMatch(await current.content(), /BROWSER_PRIVATE/);
        assert.doesNotMatch(current.url(), /BROWSER_PRIVATE/);
      }
      assert.doesNotMatch(messages.join('\n') + output, /BROWSER_PRIVATE/);
    });

    await check('session end/restart clears display on revalidation and implicit fragments are discarded', async () => {
      await fetch(`${baseURL}/__test/end-sessions`, {method: 'POST'});
      await page.reload();
      await ready(page);
      assert.equal(await page.locator('#account-signed-in').isVisible(), false);
      assert.equal(await page.locator('#account-email').textContent(), '');
      await page.goto(`${baseURL}/account#access_token=BROWSER_PRIVATE_ACCESS`);
      await page.locator('#account-error').waitFor({state: 'visible'});
      assert.equal(page.url(), `${baseURL}/account`);
      assert.equal(await page.locator('#account-signed-in').isVisible(), false);
      await page.goto(`${baseURL}/account?code=BROWSER_PRIVATE_CODE`);
      await page.locator('#account-error').waitFor({state: 'visible'});
      assert.equal(page.url(), `${baseURL}/account`);
      assert.match(await page.locator('#account-error').innerText(), /Start registreringen på nytt/);
    });

    await check('missing config, provider outage and malformed success never fabricate authentication', async () => {
      await page.route('**/api/v1/auth/status', route => route.fulfill({json: {available: false, authenticated: false}}), {times: 1});
      await page.reload();
      await page.waitForFunction(() => document.getElementById('account-status').textContent.includes('ikke tilgjengelig'));
      assert.equal(await page.locator('#account-forms').isVisible(), false);
      await page.locator('#account-retry').click();
      await ready(page);
      await fill(page, 'login', 'outage@example.test');
      await submit(page, 'login');
      await page.locator('#account-error').waitFor({state: 'visible'});
      assert.equal(await page.locator('#login-password').inputValue(), '');
      await page.route('**/api/v1/auth/login', route => route.fulfill({json: {authenticated: true}}), {times: 1});
      await fill(page, 'login', 'first@example.test');
      await submit(page, 'login');
      await page.locator('#account-error').waitFor({state: 'visible'});
      assert.equal(await page.locator('#account-signed-in').isVisible(), false);
    });

    await check('null, arrays, malformed JSON and raw provider errors become fixed safe retry messages', async () => {
      for (const body of ['null', '[]', '"BROWSER_PRIVATE_BODY"', '{"BROWSER_PRIVATE_BODY"', '{"available":true}']) {
        await page.route('**/api/v1/auth/status', route => route.fulfill({contentType: 'application/json', body}), {times: 1});
        await page.reload();
        await page.locator('#account-error').waitFor({state: 'visible'});
        assert.equal(await page.locator('#account-retry').isVisible(), true);
        assert.doesNotMatch(await page.locator('#account-error').innerText(), /BROWSER_PRIVATE/);
        await page.locator('#account-retry').click();
        await ready(page);
      }
      await page.route('**/api/v1/auth/login', route => route.fulfill({status: 503, json: {message: 'BROWSER_PRIVATE_BODY'}}), {times: 1});
      await fill(page, 'login', 'first@example.test');
      await submit(page, 'login');
      await page.locator('#account-error').waitFor({state: 'visible'});
      assert.doesNotMatch(await page.locator('#account-error').innerText(), /BROWSER_PRIVATE/);
    });

    await check('duplicate submissions are suppressed and page changes defeat uncancellable late replies', async () => {
      await page.addScriptTag({content: `(() => {const real = window.fetch.bind(window);window.fetch = (url, options) => {const {signal, ...rest} = options;return real(url, rest);};})();`});
      let release, intercepted;
      const held = new Promise(resolve => { release = resolve; });
      const entered = new Promise(resolve => { intercepted = resolve; });
      let calls = 0;
      await page.route('**/api/v1/auth/login', async route => { calls++; intercepted(); await held; await route.fulfill({json: {authenticated: true, email: 'late@example.test'}}); });
      await fill(page, 'login', 'first@example.test');
      await submit(page, 'login');
      await entered;
      assert.equal(await page.locator('#login-form button').isDisabled(), true);
      await page.locator('#login-form').evaluate(form => { form.requestSubmit(); form.requestSubmit(); });
      assert.equal(calls, 1);
      await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pagehide')));
      release();
      await page.waitForTimeout(150);
      assert.equal(await page.locator('#account-signed-in').isVisible(), false);
      assert.equal(await page.locator('#account-email').textContent(), '');
      await page.unroute('**/api/v1/auth/login');
      await page.reload();
      await ready(page);
    });

    await check('15 second auth timeout retains email, clears password and supports retry', async () => {
      let pending;
      await page.route('**/api/v1/auth/login', route => { pending = route; });
      await fill(page, 'login', 'first@example.test');
      const started = Date.now();
      await submit(page, 'login');
      await page.locator('#account-error').waitFor({state: 'visible', timeout: 20000});
      assert(Date.now() - started >= 14000);
      assert.match(await page.locator('#account-error').innerText(), /lang tid/);
      assert.equal(await page.locator('#login-email').inputValue(), 'first@example.test');
      assert.equal(await page.locator('#login-password').inputValue(), '');
      await pending.abort();
      await page.unroute('**/api/v1/auth/login');
    });

    await check('keyboard focus, narrow screens and 200 percent reflow remain usable', async () => {
      await page.locator('#login-email').focus();
      await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'login-password');
      assert.equal(await page.locator('#login-password').evaluate(node => getComputedStyle(node).outlineStyle), 'solid');
      for (const width of [320, 390, 480, 1280]) {
        await page.setViewportSize({width, height: 1000});
        assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
      }
      await page.evaluate(() => { document.documentElement.style.zoom = '200%'; });
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
      await fs.mkdir(path.join(root, 'test-results'), {recursive: true});
      await page.screenshot({path: path.join(root, 'test-results/account-200-percent.png'), fullPage: true});
      await page.evaluate(() => { document.documentElement.style.zoom = ''; });
      await page.screenshot({path: path.join(root, 'test-results/account-desktop.png'), fullPage: true});
    });
    assert.deepEqual(errors, []);
    assert.doesNotMatch(messages.join('\n') + output, /BROWSER_PRIVATE/);
    console.log(`${count} real-browser auth scenarios passed (test-only provider; live acceptance pending).`);
  } finally {
    if (browser) await browser.close();
    if (server?.pid) {
      server.kill();
      await new Promise(resolve => server.exitCode !== null ? resolve() : server.once('exit', resolve));
    }
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
