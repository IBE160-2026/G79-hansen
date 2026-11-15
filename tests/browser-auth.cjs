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
    async function recoveryPage(email) {
      const context = await browser.newContext();
      context.on('page', current => {
        current.on('console', message => messages.push(message.text()));
        current.on('pageerror', error => errors.push(error.message));
      });
      const current = await context.newPage();
      await openRecovery(current, email);
      return {context, current};
    }
    async function openRecovery(current, email) {
      await current.goto(`${baseURL}/account`);
      await ready(current);
      await current.locator('#recovery-email').fill(email);
      await current.locator('#recovery-form button').click();
      await current.waitForFunction(() => document.querySelector('#account-status').textContent.includes('Hvis kontoen finnes'));
      const links = await (await fetch(`${baseURL}/__test/links`)).json();
      await current.goto(links.at(-1).url);
      await current.locator('#account-recovery').waitFor({state: 'visible'});
    }

    await check('Norwegian labels, autocomplete, status headers and accessible form controls', async () => {
      assert.equal(await page.getByLabel('E-post', {exact: true}).count(), 3);
      assert.equal(await page.locator('#login-password').getAttribute('autocomplete'), 'current-password');
      assert.equal(await page.locator('#signup-password').getAttribute('autocomplete'), 'new-password');
      const response = await first.request.get(`${baseURL}/api/v1/auth/status`);
      assert.equal(response.headers()['cache-control'], 'no-store');
      assert.equal(response.headers()['referrer-policy'], 'no-referrer');
      const tree = await page.locator('main').ariaSnapshot();
      assert.match(tree, /heading "Konto"/);
      assert.match(tree, /textbox "E-post"/);
    });

    await check('window focus revalidation preserves unsubmitted passwords and field focus', async () => {
      await page.bringToFront();
      await ready(page);
      await page.waitForFunction(() => !document.querySelector('#login-form button').disabled);
      await fill(page, 'login', 'draft@example.test', 'UNSUBMITTED_DRAFT');
      await page.locator('#login-password').focus();
      await other.bringToFront();
      const revalidated = page.waitForResponse(response => response.url().endsWith('/api/v1/auth/status'));
      await page.bringToFront();
      // Headless Chromium does not consistently emit native window focus.
      await page.evaluate(() => window.dispatchEvent(new Event('focus')));
      await revalidated;
      await page.waitForFunction(() => !document.querySelector('#login-form button').disabled);
      assert.equal(await page.locator('#login-email').inputValue(), 'draft@example.test');
      assert.equal(await page.locator('#login-password').inputValue(), 'UNSUBMITTED_DRAFT');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'login-password');
      await page.reload();
      await ready(page);
      assert.equal(await page.locator('#login-password').inputValue(), '');
    });

    await check('unavailable background validation offers retry without inert visible forms', async () => {
      await fill(page, 'login', 'draft@example.test', 'UNSUBMITTED_DRAFT');
      await page.route('**/api/v1/auth/status', route => route.fulfill({json: {available: false, authenticated: false}}), {times: 1});
      await page.evaluate(() => window.dispatchEvent(new Event('focus')));
      await page.locator('#account-retry').waitFor({state: 'visible'});
      assert.equal(await page.locator('#account-forms').isVisible(), false);
      await page.locator('#account-retry').click();
      await ready(page);
      assert.equal(await page.locator('#login-password').inputValue(), '');
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

    await check('confirmation error is consumed once and cannot return after login and focus', async () => {
      const isolated = await browser.newContext();
      try {
        const current = await isolated.newPage();
        await current.goto(`${baseURL}/account?confirmation=invalid`);
        await current.locator('#account-error').waitFor({state: 'visible'});
        await fill(current, 'login', 'confirmed@example.test');
        await submit(current, 'login');
        await current.locator('#account-signed-in').waitFor({state: 'visible'});
        const response = current.waitForResponse(reply => reply.url().endsWith('/api/v1/auth/status'));
        await current.evaluate(() => window.dispatchEvent(new Event('focus')));
        await response;
        await current.locator('#account-signed-in').waitFor({state: 'visible'});
        assert.equal(await current.locator('#account-error').isVisible(), false);
        assert.equal(await current.locator('#account-email').innerText(), 'confirmed@example.test');
      } finally { await isolated.close(); }
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

    await check('recovery stays browser-bound, restricts access, validates matching passwords and requires normal login', async () => {
      await page.goto(`${baseURL}/account`);
      await ready(page);
      await other.goto(`${baseURL}/account`);
      await ready(other);
      await fill(other, 'login', 'second@example.test');
      await submit(other, 'login');
      await other.locator('#account-signed-in').waitFor({state: 'visible'});
      for (let index = 0; index < 2; index++) {
        await page.locator('#recovery-email').fill('first@example.test');
        await page.locator('#recovery-form button').click();
        await page.waitForFunction(() => document.querySelector('#account-status').textContent.includes('Hvis kontoen finnes'));
      }
      const links = (await (await fetch(`${baseURL}/__test/links`)).json()).filter(link => link.purpose === 'recovery');
      assert.equal(links.length, 2);
      assert.notEqual(links[0].url, links[1].url);
      await other.goto(links[0].url);
      await other.locator('#account-error').waitFor({state: 'visible'});
      assert.match(await other.locator('#account-error').innerText(), /ny lenke.*samme nettleser/);
      assert.equal(other.url(), `${baseURL}/account`);
      assert.equal(await other.locator('#account-email').innerText(), 'second@example.test');
      const normal = await (await second.request.get(`${baseURL}/api/v1/auth/status`)).json();
      const denied = await second.request.post(`${baseURL}/api/v1/auth/recovery/password`, {headers: {Origin: baseURL, 'X-CSRF-Token': normal.csrfToken}, data: {password: 'BROWSER_NEW_PASSWORD'}});
      assert.equal(denied.status(), 401);
      await page.goto(links[0].url);
      await page.locator('#account-recovery').waitFor({state: 'visible'});
      assert.equal(page.url(), `${baseURL}/account`);
      assert.equal(await page.locator('#account-forms').isVisible(), false);
      assert.equal(await page.locator('#account-signed-in').isVisible(), false);
      const restricted = await (await first.request.get(`${baseURL}/api/v1/auth/status`)).json();
      assert.equal(restricted.authenticated, false);
      assert.equal(restricted.recoveryAvailable, true);
      assert.equal('email' in restricted, false);
      assert.equal(await page.locator('#recovery-password-confirm').getAttribute('autocomplete'), 'new-password');
      await page.locator('#recovery-password').focus();
      await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'recovery-password-confirm');
      for (const width of [320, 390, 480, 1280]) {
        await page.setViewportSize({width, height: 1000});
        assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
      }
      await page.evaluate(() => { document.documentElement.style.zoom = '200%'; });
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
      await fs.mkdir(path.join(root, 'test-results'), {recursive: true});
      await page.screenshot({path: path.join(root, 'test-results/account-recovery-200-percent.png'), fullPage: true});
      await page.evaluate(() => { document.documentElement.style.zoom = ''; });
      const tree = await page.locator('main').ariaSnapshot();
      assert.match(tree, /heading "Velg nytt passord"/);
      await page.locator('#recovery-password').fill('BROWSER_NEW_PASSWORD');
      const background = page.waitForResponse(response => response.url().endsWith('/api/v1/auth/status'));
      await page.evaluate(() => window.dispatchEvent(new Event('focus')));
      await background;
      await page.waitForFunction(() => !document.querySelector('#recovery-password-form button').disabled);
      assert.equal(await page.locator('#recovery-password').inputValue(), 'BROWSER_NEW_PASSWORD');
      await page.locator('#recovery-password-confirm').fill('BROWSER_MISMATCH');
      await page.locator('#recovery-password-form button').click();
      assert.equal(await page.locator('#recovery-password-confirm').evaluate(input => input.validationMessage), 'Passordene må være like.');
      assert.deepEqual(await (await fetch(`${baseURL}/__test/updates`)).json(), []);
      await page.locator('#recovery-password-confirm').fill('BROWSER_NEW_PASSWORD');
      await page.locator('#recovery-password-form button').click();
      await page.waitForFunction(() => document.querySelector('#account-status').textContent.includes('Passordet er endret'));
      assert.equal(await page.locator('#account-recovery').isVisible(), false);
      assert.equal(await page.locator('#recovery-password').inputValue(), '');
      assert.equal(await page.locator('#recovery-password-confirm').inputValue(), '');
      await page.goto(links[0].url);
      await page.locator('#account-error').waitFor({state: 'visible'});
      await fill(page, 'login', 'first@example.test', 'BROWSER_NEW_PASSWORD');
      await submit(page, 'login');
      await page.locator('#account-signed-in').waitFor({state: 'visible'});
      const refreshed = page.waitForResponse(response => response.url().endsWith('/api/v1/auth/status'));
      await page.evaluate(() => window.dispatchEvent(new Event('focus')));
      await refreshed;
      assert.equal(await page.locator('#account-error').isVisible(), false);
      await other.reload();
      await other.locator('#account-signed-in').waitFor({state: 'visible'});
      assert.equal(await other.locator('#account-email').innerText(), 'second@example.test');
      await fetch(`${baseURL}/__test/end-sessions`, {method: 'POST'});
      await page.reload();
      await ready(page);
    });

    await check('uncertain recovery update consumes the grant and explains new-link or login outcome', async () => {
      await page.locator('#recovery-email').fill('uncertain@example.test');
      await page.locator('#recovery-form button').click();
      await page.waitForFunction(() => document.querySelector('#account-status').textContent.includes('Hvis kontoen finnes'));
      const links = await (await fetch(`${baseURL}/__test/links`)).json();
      await page.goto(links.at(-1).url);
      await page.locator('#account-recovery').waitFor({state: 'visible'});
      await page.locator('#recovery-password').fill('BROWSER_UNCERTAIN_PASSWORD');
      await page.locator('#recovery-password-confirm').fill('BROWSER_UNCERTAIN_PASSWORD');
      await page.locator('#recovery-password-form button').click();
      await page.locator('#account-error').waitFor({state: 'visible'});
      assert.match(await page.locator('#account-error').innerText(), /kan være endret.*ny lenke/);
      assert.equal(await page.locator('#account-recovery').isVisible(), false);
      assert.equal(await page.locator('#account-forms').isVisible(), true);
      assert.equal(await page.locator('#recovery-password').inputValue(), '');
      const state = await (await first.request.get(`${baseURL}/api/v1/auth/status`)).json();
      assert.equal(state.recoveryAvailable, false);
      await fill(page, 'login', 'uncertain@example.test', 'BROWSER_UNCERTAIN_PASSWORD');
      await submit(page, 'login');
      await page.locator('#account-signed-in').waitFor({state: 'visible'});
      await fetch(`${baseURL}/__test/end-sessions`, {method: 'POST'});
      await page.reload();
      await ready(page);
    });

    await check('duplicate recovery submissions and stale password replies cannot restore hidden authority', async () => {
      let requestCount = 0;
      await page.route('**/api/v1/auth/recovery/request', async route => {
        requestCount++;
        await pause(80);
        await route.continue();
      });
      await page.locator('#recovery-email').fill('duplicate@example.test');
      await page.locator('#recovery-form').evaluate(form => { form.requestSubmit(); form.requestSubmit(); });
      await page.waitForFunction(() => document.querySelector('#account-status').textContent.includes('Hvis kontoen finnes'));
      assert.equal(requestCount, 1);
      await page.unroute('**/api/v1/auth/recovery/request');
      const links = await (await fetch(`${baseURL}/__test/links`)).json();
      await page.goto(links.at(-1).url);
      await page.locator('#account-recovery').waitFor({state: 'visible'});
      await page.addScriptTag({content: `(() => {const real = window.fetch.bind(window);window.fetch = (url, options) => {const {signal, ...rest} = options;return real(url, rest);};})();`});
      let release, enter;
      const held = new Promise(resolve => { release = resolve; });
      const entered = new Promise(resolve => { enter = resolve; });
      let writes = 0;
      await page.route('**/api/v1/auth/recovery/password', async route => {
        writes++; enter(); await held;
        await route.fulfill({json: {status: 'password_updated', authenticated: false, recoveryAvailable: false}});
      });
      await page.locator('#recovery-password').fill('BROWSER_DUPLICATE_PASSWORD');
      await page.locator('#recovery-password-confirm').fill('BROWSER_DUPLICATE_PASSWORD');
      await page.locator('#recovery-password-form button').click();
      await entered;
      await page.locator('#recovery-password-form').evaluate(form => { form.requestSubmit(); form.requestSubmit(); });
      assert.equal(writes, 1);
      await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pagehide')));
      release();
      await pause(100);
      assert.equal(await page.locator('#account-recovery').isVisible(), false);
      assert.equal(await page.locator('#recovery-password').inputValue(), '');
      assert.doesNotMatch(await page.locator('#account-status').innerText(), /Passordet er endret/);
      await page.unroute('**/api/v1/auth/recovery/password');
      await fetch(`${baseURL}/__test/end-sessions`, {method: 'POST'});
      await page.reload();
      await ready(page);
    });

    await check('recovery cleanup clears fragments, passwords, storage and console secrets', async () => {
      await page.goto(`${baseURL}/account?recovery=invalid#access_token=BROWSER_PRIVATE_ACCESS`);
      await page.locator('#account-error').waitFor({state: 'visible'});
      assert.equal(page.url(), `${baseURL}/account`);
      assert.match(await page.locator('#account-error').innerText(), /Gjenopprettingslenken/);
      const stored = await page.evaluate(async () => ({local: {...localStorage}, session: {...sessionStorage}, cookies: document.cookie,
        databases: (await indexedDB.databases()).length, caches: (await caches.keys()).length}));
      assert.deepEqual(stored, {local: {}, session: {}, cookies: '', databases: 0, caches: 0});
      assert.doesNotMatch(await page.content(), /BROWSER_(PRIVATE|NEW|UNCERTAIN|DUPLICATE|MISMATCH)/);
      assert.doesNotMatch(messages.join('\n') + output, /BROWSER_(PRIVATE|NEW|UNCERTAIN|DUPLICATE|MISMATCH)/);
      await page.reload();
      await ready(page);
    });

    await check('recovery password bounds count Unicode code points at both supplementary-character boundaries', async () => {
      const {context, current} = await recoveryPage('unicode@example.test');
      try {
        const writes = (await (await fetch(`${baseURL}/__test/updates`)).json()).length;
        const submitted = [];
        current.on('request', request => {
          if (request.url().endsWith('/api/v1/auth/recovery/password')) submitted.push(request.postDataJSON().password);
        });
        for (const length of [4, 7, 1025]) {
          const value = '😀'.repeat(length);
          await current.locator('#recovery-password').fill(value);
          await current.locator('#recovery-password-confirm').fill(value);
          assert.equal(await current.locator('#recovery-password').inputValue(), value);
          await current.locator('#recovery-password-form button').click();
          assert.equal(await current.locator('#recovery-password').evaluate(input => input.validationMessage), 'Bruk 8–1024 tegn i passordet.');
          assert.equal(submitted.length, 0);
          assert.equal((await (await fetch(`${baseURL}/__test/updates`)).json()).length, writes);
          assert.equal(await current.locator('#account-recovery').isVisible(), true);
        }
        for (const [index, length] of [8, 1024].entries()) {
          if (index) await openRecovery(current, 'unicode@example.test');
          const value = '😀'.repeat(length);
          await current.locator('#recovery-password').fill(value);
          await current.locator('#recovery-password-confirm').fill(value);
          await current.locator('#recovery-password-form button').click();
          await current.waitForFunction(() => document.querySelector('#account-status').textContent.includes('Passordet er endret'));
          assert.equal(submitted[index], value);
          assert.equal((await (await fetch(`${baseURL}/__test/updates`)).json()).length, writes + index + 1);
        }
      } finally { await context.close(); }
    });

    await check('pre-admission password errors keep recovery correctable while unknown and admitted errors stay conservative', async () => {
      const {context, current} = await recoveryPage('correctable@example.test');
      try {
        const writes = (await (await fetch(`${baseURL}/__test/updates`)).json()).length;
        for (const [code, status, guidance] of [
          ['invalid_request', 422, /Kontroller passordet/],
          ['request_rejected', 403, /kontrollere tilgangen på nytt/],
          ['auth_unavailable', 503, /ikke tilgjengelig nå/],
        ]) {
          await current.route('**/api/v1/auth/recovery/password', route => route.fulfill({status, json: {code, message: 'BROWSER_PRIVATE_BODY'}}), {times: 1});
          await current.locator('#recovery-password').fill('BROWSER_CORRECTABLE_PASSWORD');
          await current.locator('#recovery-password-confirm').fill('BROWSER_CORRECTABLE_PASSWORD');
          await current.locator('#recovery-password-form button').click();
          await current.locator('#account-error').waitFor({state: 'visible'});
          const text = await current.locator('#account-error').innerText();
          assert.match(text, guidance);
          assert.match(text, /Passordet er ikke endret/);
          assert.doesNotMatch(text, /kan være endret|BROWSER_PRIVATE/);
          assert.equal(await current.locator('#account-recovery').isVisible(), true);
          assert.equal(await current.locator('#account-forms').isVisible(), false);
          assert.equal(await current.locator('#recovery-password').inputValue(), '');
          assert.equal((await (await context.request.get(`${baseURL}/api/v1/auth/status`)).json()).recoveryAvailable, true);
          assert.equal((await (await fetch(`${baseURL}/__test/updates`)).json()).length, writes);
          if (code !== 'invalid_request') {
            await current.locator('#account-retry').click();
            await current.locator('#account-recovery').waitFor({state: 'visible'});
            await current.waitForFunction(() => !document.querySelector('#recovery-password-form button').disabled);
          }
        }
        for (const code of ['recovery_failed', 'unknown_failure']) {
          await current.route('**/api/v1/auth/recovery/password', route => route.fulfill({status: 503, json: {code}}), {times: 1});
          await current.locator('#recovery-password').fill('BROWSER_CORRECTABLE_PASSWORD');
          await current.locator('#recovery-password-confirm').fill('BROWSER_CORRECTABLE_PASSWORD');
          await current.locator('#recovery-password-form button').click();
          await current.locator('#account-error').waitFor({state: 'visible'});
          assert.match(await current.locator('#account-error').innerText(), /kan være endret/);
          assert.equal(await current.locator('#account-recovery').isVisible(), false);
          await current.reload();
          await current.locator('#account-recovery').waitFor({state: 'visible'});
        }
        await current.locator('#recovery-password').fill('BROWSER_CORRECTABLE_PASSWORD');
        await current.locator('#recovery-password-confirm').fill('BROWSER_CORRECTABLE_PASSWORD');
        await current.locator('#recovery-password-form button').click();
        await current.waitForFunction(() => document.querySelector('#account-status').textContent.includes('Passordet er endret'));
        assert.equal((await (await fetch(`${baseURL}/__test/updates`)).json()).length, writes + 1);
      } finally { await context.close(); }
    });

    await check('recovery can return to normal login and signed-in users can request recovery without a password write', async () => {
      const {context, current} = await recoveryPage('navigation@example.test');
      try {
        const writes = (await (await fetch(`${baseURL}/__test/updates`)).json()).length;
        const cookies = await context.cookies();
        const grant = cookies.find(cookie => cookie.name === 'sb_session').value;
        const binding = cookies.find(cookie => cookie.name === 'sb_browser').value;
        await current.locator('#recovery-password').fill('BROWSER_NAVIGATION_DRAFT');
        await current.locator('#recovery-login').click();
        await ready(current);
        assert.equal(await current.locator('#recovery-password').inputValue(), '');
        assert.equal(await current.locator('#account-recovery').isVisible(), false);
        assert.equal(await current.evaluate(() => document.activeElement.id), 'login-email');
        const focusStatus = current.waitForResponse(response => response.url().endsWith('/api/v1/auth/status'));
        await current.evaluate(() => window.dispatchEvent(new Event('focus')));
        await focusStatus;
        await current.waitForFunction(() => !document.querySelector('#login-form button').disabled);
        assert.equal(await current.locator('#account-forms').isVisible(), true);
        await fill(current, 'login', 'navigation@example.test');
        await submit(current, 'login');
        await current.locator('#account-signed-in').waitFor({state: 'visible'});
        const state = await (await context.request.get(`${baseURL}/api/v1/auth/status`)).json();
        assert.equal(state.authenticated, true);
        assert.equal(state.recoveryAvailable, false);
        const old = await (await fetch(`${baseURL}/api/v1/auth/status`, {headers: {Cookie: `sb_browser=${binding}; sb_session=${grant}`}})).json();
        assert.equal(old.authenticated, false);
        assert.equal(old.recoveryAvailable, false);
        await current.locator('#account-show-forms').click();
        await ready(current);
        assert.equal(await current.locator('#recovery-form button').isVisible(), true);
        await current.locator('#recovery-email').fill('navigation@example.test');
        await current.locator('#recovery-form button').click();
        await current.waitForFunction(() => document.querySelector('#account-status').textContent.includes('Hvis kontoen finnes'));
        const links = await (await fetch(`${baseURL}/__test/links`)).json();
        await current.goto(links.at(-1).url);
        await current.locator('#account-recovery').waitFor({state: 'visible'});
        assert.equal((await (await context.request.get(`${baseURL}/api/v1/auth/status`)).json()).authenticated, false);
        assert.equal((await (await fetch(`${baseURL}/__test/updates`)).json()).length, writes);
      } finally { await context.close(); }
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

    await check('inherited, null and unknown response codes use only the fixed unavailable message', async () => {
      for (const code of ['constructor', 'toString', null, 'BROWSER_PRIVATE_UNKNOWN']) {
        await page.route('**/api/v1/auth/login', route => route.fulfill({status: 503, json: {code, message: 'BROWSER_PRIVATE_BODY'}}), {times: 1});
        await fill(page, 'login', 'first@example.test');
        await submit(page, 'login');
        await page.locator('#account-error').waitFor({state: 'visible'});
        assert.equal(await page.locator('#account-error').innerText(), 'Innlogging er ikke tilgjengelig nå. Studiedemoen kan fortsatt brukes.');
        assert.equal(await page.locator('#login-password').inputValue(), '');
      }
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

    await check('normal logout clears sibling tabs and keeps another browser on the same account signed in', async () => {
      const left = await browser.newContext(), right = await browser.newContext();
      try {
        const a = await left.newPage(), b = await right.newPage();
        for (const current of [a, b]) {
          await current.goto(`${baseURL}/account`); await ready(current);
          await fill(current, 'login', 'same-account@example.test'); await submit(current, 'login');
          await current.locator('#account-signed-in').waitFor({state: 'visible'});
          await current.waitForFunction(() => !document.querySelector('#login-form button').disabled);
        }
        const sibling = await left.newPage();
        await sibling.goto(`${baseURL}/account`);
        await sibling.locator('#account-signed-in').waitFor({state: 'visible'});
        await a.locator('#account-signed-in [data-account-logout]').focus();
        await a.keyboard.press('Enter');
        await ready(a); await ready(sibling);
        assert.equal(await sibling.locator('#account-email').textContent(), '');
        assert.match(await sibling.locator('#account-status').innerText(), /Logg inn/);
        assert.equal((await (await right.request.get(`${baseURL}/api/v1/auth/status`)).json()).authenticated, true);
        assert.equal((await (await left.request.get(`${baseURL}/api/v1/auth/status`)).json()).authenticated, false);
        assert.equal((await left.cookies()).some(cookie => cookie.name === 'sb_session'), false);
        await fill(a, 'login', 'same-account@example.test'); await submit(a, 'login');
        await a.locator('#account-signed-in').waitFor({state: 'visible'});
      } finally { await left.close(); await right.close(); }
    });

    await check('focused page clears normal and recovery display at the observed deadline without activity', async () => {
      for (const restricted of [false, true]) {
        const context = await browser.newContext();
        try {
          const current = await context.newPage();
          if (restricted) await openRecovery(current, 'expiry@example.test');
          else {
            await current.goto(`${baseURL}/account`); await ready(current);
            await fill(current, 'login', 'expiry@example.test'); await submit(current, 'login');
            await current.locator('#account-signed-in').waitFor({state: 'visible'});
          }
          await current.waitForFunction(() => !document.querySelector('#login-form button').disabled);
          await context.request.post(`${baseURL}/__test/deadline`);
          const observed = current.waitForResponse(response => response.url().endsWith('/api/v1/auth/status'));
          await current.evaluate(() => window.dispatchEvent(new Event('focus')));
          await observed;
          await ready(current);
          assert.equal(await current.locator('#account-email').textContent(), '');
          assert.equal(await current.locator('#account-recovery').isVisible(), false);
          assert.equal((await (await context.request.get(`${baseURL}/api/v1/auth/status`)).json()).authenticated, false);
        } finally { await context.close(); }
      }
    });

    await check('visible passive checks observe restart and permit a fresh login with preserved old cookies', async () => {
      const context = await browser.newContext();
      try {
        const current = await context.newPage();
        await current.clock.install();
        await current.goto(`${baseURL}/account`); await ready(current);
        await fill(current, 'login', 'restart@example.test'); await submit(current, 'login');
        await current.locator('#account-signed-in').waitFor({state: 'visible'});
        await current.waitForFunction(() => !document.querySelector('#login-form button').disabled);
        await context.request.post(`${baseURL}/__test/restart`);
        const checked = current.waitForResponse(response => response.url().endsWith('/api/v1/auth/status'));
        await current.clock.fastForward(30001);
        await checked; await ready(current);
        assert.equal(await current.locator('#account-email').textContent(), '');
        await fill(current, 'login', 'restart@example.test'); await submit(current, 'login');
        await current.locator('#account-signed-in').waitFor({state: 'visible'});
      } finally { await context.close(); }
    });

    await check('a tab termination signal discards a login reply that ignores cancellation', async () => {
      const context = await browser.newContext();
      try {
        const a = await context.newPage();
        await a.goto(`${baseURL}/account`); await ready(a);
        await fill(a, 'login', 'late-tab@example.test'); await submit(a, 'login');
        await a.locator('#account-signed-in').waitFor({state: 'visible'});
        await a.waitForFunction(() => !document.querySelector('#login-form button').disabled);
        const sibling = await context.newPage();
        await sibling.goto(`${baseURL}/account`);
        await sibling.locator('#account-signed-in').waitFor({state: 'visible'});
        await sibling.waitForFunction(() => !document.querySelector('#login-form button').disabled);
        await sibling.locator('#account-show-forms').click();
        await sibling.evaluate(() => {
          const original = window.fetch.bind(window);
          window.fetch = async (...args) => {
            const response = await original(...args);
            if (args[0].endsWith('/login')) {
              window.__loginReady = true;
              await new Promise(resolve => { window.__releaseLogin = resolve; });
            }
            return response;
          };
        });
        await fill(sibling, 'login', 'late-tab@example.test'); await submit(sibling, 'login');
        await sibling.waitForFunction(() => window.__loginReady);
        await a.locator('#account-signed-in [data-account-logout]').click(); await ready(a);
        await sibling.waitForFunction(() => document.querySelector('#account-status').textContent.includes('avsluttet'));
        await sibling.evaluate(() => window.__releaseLogin());
        await sibling.waitForTimeout(150);
        assert.equal(await sibling.locator('#account-signed-in').isVisible(), false);
        assert.equal(await sibling.locator('#account-email').textContent(), '');
        const stored = await sibling.evaluate(() => ({local: {...localStorage}, session: {...sessionStorage}}));
        assert.deepEqual(stored, {local: {}, session: {}});
      } finally { await context.close(); }
    });

    await check('restricted logout is keyboard operable and clears password drafts at narrow reflow', async () => {
      const {context, current} = await recoveryPage('logout-recovery@example.test');
      try {
        await current.setViewportSize({width: 320, height: 800});
        await current.locator('#recovery-password').fill('UNSUBMITTED_PRIVATE_DRAFT');
        await current.locator('#account-recovery [data-account-logout]').focus();
        await current.keyboard.press('Enter'); await ready(current);
        assert.equal(await current.locator('#recovery-password').inputValue(), '');
        assert.equal(await current.locator('#account-recovery').isVisible(), false);
        assert(await current.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
      } finally { await context.close(); }
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
