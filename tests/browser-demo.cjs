/* Real-browser integration checks. Starts its own local server unless DEMO_BASE_URL is set. */
const assert = require('node:assert/strict');
const {spawn} = require('node:child_process');
const fs = require('node:fs/promises');
const net = require('node:net');
const path = require('node:path');
const {chromium} = require('playwright');

const root = path.resolve(__dirname, '..');
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
let checks = 0;
async function check(name, action) { await action(); checks++; console.log(`PASS ${name}`); }
async function visible(page, id, expected = true) { assert.equal(await page.locator(id).isVisible(), expected, `${id} visibility`); }
async function ready(page) { await page.waitForFunction(() => !document.getElementById('generate').disabled); }
async function generate(page) { await page.locator('#generate').click(); await page.locator('#results').waitFor({state: 'visible'}); }
async function noOverflow(page) { assert(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1), 'horizontal overflow'); }

async function freePort() {
  const server = net.createServer();
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;
  await new Promise(resolve => server.close(resolve));
  return port;
}

async function main() {
  let server;
  let browser;
  let serverOutput = '';
  try {
    let baseURL = process.env.DEMO_BASE_URL;
    if (!baseURL) {
      const port = await freePort();
      baseURL = `http://127.0.0.1:${port}`;
      const python = path.join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
      server = spawn(python, ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(port), '--no-access-log'], {cwd: root, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe']});
      server.on('error', error => { serverOutput += error.message; });
      server.stdout.on('data', data => { serverOutput += data; });
      server.stderr.on('data', data => { serverOutput += data; });
      let started = false;
      for (let attempt = 0; attempt < 100; attempt++) {
        try { if ((await fetch(`${baseURL}/health`)).ok) { started = true; break; } } catch {}
        if (!server.pid || server.exitCode !== null) break;
        await pause(100);
      }
      assert(started, `Local uvicorn did not start: ${serverOutput}`);
    }
    if (process.env.DEMO_BROWSER_CHANNEL) browser = await chromium.launch({channel: process.env.DEMO_BROWSER_CHANNEL});
    else {
      try { browser = await chromium.launch(); }
      catch { browser = await chromium.launch({channel: 'msedge'}); }
    }
    console.log(`Browser: ${browser.version()}`);
    const context = await browser.newContext({viewport: {width: 1280, height: 1000}});
    // A response that ignores cancellation proves the sequence guard as well as abort behavior.
    await context.addInitScript(() => {
      const realFetch = window.fetch.bind(window);
      window.fetch = (url, options) => {
        if ((window.ignoreGenerationAbort && String(url).endsWith('/generate')) ||
            (window.ignoreFixtureAbort && String(url).endsWith('/fixture'))) {
          const {signal, ...withoutSignal} = options;
          return realFetch(url, withoutSignal);
        }
        return realFetch(url, options);
      };
    });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    let generationCalls = 0;
    page.on('request', request => { if (request.url().endsWith('/api/v1/demo/generate')) generationCalls++; });
    await page.goto(baseURL);
    await ready(page);
    const validFixture = await (await fetch(`${baseURL}/api/v1/demo/fixture`)).json();
    const validBundle = await (await fetch(`${baseURL}/api/v1/demo/generate`, {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({schemaVersion: '1.0', fixtureId: 'memory-basics-v1'}),
    })).json();

    await check('startup failure and malformed fixture source/settings recover through explicit retry', async () => {
      const malformedFixtures = [
        fixture => { fixture.source.id = 'wrong-source'; },
        fixture => { fixture.source.units = 'not-an-array'; },
        fixture => { fixture.source.units[0].text = null; },
        fixture => { fixture.source.units[1].id = fixture.source.units[0].id; },
        fixture => { fixture.source.units[0].location = 0; },
        fixture => { fixture.settings.language = 'en'; },
        fixture => { delete fixture.settings.detail; },
      ];
      const responses = [{status: 503, body: '{}'}, ...malformedFixtures.map(mutate => {
        const fixture = structuredClone(validFixture);
        mutate(fixture);
        return {json: fixture};
      })];
      for (const response of responses) {
        const fresh = await context.newPage();
        fresh.on('pageerror', error => errors.push(error.message));
        try {
          await fresh.route('**/api/v1/demo/fixture', route => route.fulfill(response), {times: 1});
          await fresh.goto(baseURL);
          await fresh.locator('#state-notice').waitFor({state: 'visible'});
          assert.equal(await fresh.locator('#generate').isDisabled(), true);
          assert.equal(await fresh.locator('#method').isDisabled(), true);
          assert.equal(await fresh.locator('#retry').isDisabled(), false);
          await fresh.locator('#retry').click();
          await ready(fresh);
          assert.match(await fresh.locator('#material').innerText(), /Arbeidsminnet holder/);
          await visible(fresh, '#state-notice', false);
        } finally { await fresh.close(); }
      }
    });

    await check('stalled initial fixture times out at 15 seconds and can be retried', async () => {
      const fresh = await context.newPage();
      fresh.on('pageerror', error => errors.push(error.message));
      let pendingRoute;
      try {
        await fresh.route('**/api/v1/demo/fixture', route => { pendingRoute = route; });
        const started = Date.now();
        await fresh.goto(baseURL);
        await fresh.locator('#state-notice').waitFor({state: 'visible', timeout: 20000});
        assert(Date.now() - started >= 14000, 'fixture timeout should use the production 15 second bound');
        assert.equal(await fresh.locator('#retry').isDisabled(), false);
        assert.equal(await fresh.locator('#generate').isDisabled(), true);
        await pendingRoute.abort();
        await fresh.unroute('**/api/v1/demo/fixture');
        await fresh.locator('#retry').click();
        await ready(fresh);
        assert.match(await fresh.locator('#material').innerText(), /Arbeidsminnet holder/);
      } finally { await fresh.close(); }
    });

    await check('reset wins over uncancellable delayed initial fixture success', async () => {
      const fresh = await context.newPage();
      fresh.on('pageerror', error => errors.push(error.message));
      await fresh.addInitScript(() => { window.ignoreFixtureAbort = true; });
      let pendingRoute;
      try {
        await fresh.route('**/api/v1/demo/fixture', route => { pendingRoute = route; });
        await fresh.goto(baseURL);
        await fresh.waitForFunction(() => document.getElementById('status').textContent.includes('Henter'));
        assert(pendingRoute, 'initial fixture request should be held');
        await fresh.locator('#reset').click();
        const delivered = fresh.waitForResponse('**/api/v1/demo/fixture');
        await pendingRoute.fulfill({json: validFixture});
        await delivered;
        await fresh.waitForTimeout(150);
        assert.equal(await fresh.locator('#method').inputValue(), '');
        assert.equal(await fresh.locator('#generate').isDisabled(), true);
        assert.doesNotMatch(await fresh.locator('#material').innerText(), /Arbeidsminnet holder/);
        assert.match(await fresh.locator('#status').innerText(), /Ny økt/);
        await visible(fresh, '#material-body');
        await visible(fresh, '#results', false);
        await fresh.unroute('**/api/v1/demo/fixture');
        await fresh.locator('#retry').click();
        await ready(fresh);
      } finally { await fresh.close(); }
    });

    await check('fixed source, readable tokens, health and first four-part generation', async () => {
      assert.deepEqual(await (await fetch(`${baseURL}/health`)).json(), {status: 'ok', mode: 'demo'});
      await visible(page, '#material-body');
      assert.match(await page.locator('#material').innerText(), /Avsnitt 3/);
      assert.equal(await page.locator('body').evaluate(node => getComputedStyle(node).fontSize), '16px');
      await generate(page);
      await visible(page, '#material-body', false);
      await visible(page, '#reset');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'edit-material');
      assert.equal(await page.locator('[role=tab]').count(), 4);
      assert.match(await page.locator('#content').innerText(), /Kilde: Avsnitt 1, Avsnitt 2, Avsnitt 3/);
      assert.equal(generationCalls, 1);
    });

    await check('independent practice positions, per-item reveals, references and request count', async () => {
      await page.locator('#tab-concepts').click();
      assert.equal(await page.locator('#content h3').count(), 3);
      await page.locator('#tab-flashcards').click();
      await visible(page, '#answer', false);
      assert.equal(await page.locator('#previous').isDisabled(), true);
      await page.locator('#reveal').click();
      assert.match(await page.locator('#answer').innerText(), /Kilde: Avsnitt 1/);
      await page.locator('#next').click();
      await visible(page, '#answer', false);
      await page.locator('#reveal').click();
      await page.locator('#tab-quiz').click();
      await visible(page, '#answer', false);
      await page.locator('#next').click();
      assert.equal(await page.locator('#next').isDisabled(), true);
      assert.equal(await page.evaluate(() => document.activeElement.id), 'previous');
      await page.locator('#reveal').click();
      assert.match(await page.locator('#answer').innerText(), /Kilde: Avsnitt 3/);
      await page.locator('#tab-flashcards').click();
      assert.match(await page.locator('#content').innerText(), /Kort 2 av 3/);
      await visible(page, '#answer');
      await page.locator('#previous').click();
      await visible(page, '#answer');
      await page.locator('#next').click();
      await page.locator('#edit-material').click();
      assert.match(await page.locator('#material').innerText(), /Arbeidsminnet holder/);
      assert.match(await page.locator('#content').innerText(), /Kort 2 av 3/);
      await visible(page, '#answer');
      await page.locator('#tab-quiz').click();
      assert.match(await page.locator('#content').innerText(), /Spørsmål 2 av 2/);
      await visible(page, '#answer');
      assert.equal(generationCalls, 1);
    });

    await check('keyboard tabs, reveal, source expansion and visible focus', async () => {
      await page.locator('#tab-summary').focus();
      await page.keyboard.press('ArrowRight');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'tab-concepts');
      await page.keyboard.press('End');
      assert.equal(await page.locator('#tab-quiz').getAttribute('aria-selected'), 'true');
      await page.keyboard.press('Home');
      assert.equal(await page.locator('#tab-summary').getAttribute('tabindex'), '0');
      await page.keyboard.press('ArrowLeft');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'tab-quiz');
      assert.equal(await page.locator('#tab-quiz').evaluate(node => getComputedStyle(node).outlineStyle), 'solid');
      await page.locator('#reset').focus();
      await page.keyboard.press('Enter');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'method');
      await visible(page, '#results', false);
      assert.equal(await page.locator('#method').inputValue(), '');
      assert.doesNotMatch(await page.locator('#material').innerText(), /Arbeidsminnet holder/);
      assert.equal(await page.locator('#generate').isDisabled(), true);
      await page.locator('#method').selectOption('memory-basics-v1');
      await page.locator('#generate').focus();
      await page.keyboard.press('Enter');
      await page.locator('#results').waitFor({state: 'visible'});
      await page.locator('#tab-summary').focus();
      await page.keyboard.press('ArrowRight');
      await page.keyboard.press('ArrowRight');
      await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'content');
      await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'reveal');
      await page.keyboard.press('Enter');
      await visible(page, '#answer');
    });

    await check('failed network preserves source/settings and explicit retry succeeds', async () => {
      await page.locator('#edit-material').click();
      await page.route('**/api/v1/demo/generate', route => route.abort('failed'));
      await page.locator('#generate').click();
      await page.locator('#state-notice').waitFor({state: 'visible'});
      await visible(page, '#results', false);
      await visible(page, '#material-body');
      assert.equal(await page.locator('#method').inputValue(), 'memory-basics-v1');
      assert.match(await page.locator('#material').innerText(), /Arbeidsminnet holder/);
      assert.equal(await page.locator('#language').innerText(), 'Norsk (fast)');
      await page.unroute('**/api/v1/demo/generate');
      await page.locator('#retry').click();
      await page.locator('#results').waitFor({state: 'visible'});
      await visible(page, '#state-notice', false);
      await page.locator('#tab-flashcards').click();
      assert.match(await page.locator('#content').innerText(), /Kort 1 av 3/);
      await visible(page, '#answer', false);
    });

    await check('non-OK and malformed successful responses never fabricate success', async () => {
      const semanticMutations = [
        bundle => { bundle.source.id = 'wrong-source'; },
        bundle => { bundle.settings.language = 'en'; },
        bundle => { bundle.quiz[0].references[0].sourceUnitId = 'nonexistent'; },
        bundle => { bundle.quiz[0].references[0].label = 'Avsnitt 99'; },
        bundle => { bundle.quiz = []; bundle.insufficiency.quiz = ''; },
        bundle => { bundle.quiz = []; bundle.insufficiency.quiz = '   '; },
      ];
      const responses = [{status: 503, body: '{}'}, {status: 200, body: '{broken'}, {status: 200, body: '{}'}, ...semanticMutations.map(mutate => {
        const bundle = structuredClone(validBundle);
        mutate(bundle);
        return {status: 200, body: JSON.stringify(bundle)};
      })];
      for (const payload of responses) {
        if (await page.locator('#edit-material').isVisible()) await page.locator('#edit-material').click();
        await page.route('**/api/v1/demo/generate', route => route.fulfill({contentType: 'application/json', ...payload}));
        await page.locator('#generate').click();
        await page.locator('#state-notice').waitFor({state: 'visible'});
        await visible(page, '#results', false);
        await visible(page, '#material-body');
        await page.unroute('**/api/v1/demo/generate');
      }
    });

    await check('stalled generation times out at 15 seconds, retains source and retries', async () => {
      let pendingRoute;
      await page.route('**/api/v1/demo/generate', route => { pendingRoute = route; });
      const started = Date.now();
      await page.locator('#generate').click();
      // Previous error notices are cleared synchronously by the new request.
      await visible(page, '#state-notice', false);
      await page.locator('#state-notice').waitFor({state: 'visible', timeout: 20000});
      assert(Date.now() - started >= 14000, 'generation timeout should use the production 15 second bound');
      assert.equal(await page.locator('#generate').isDisabled(), false);
      assert.equal(await page.locator('#retry').isDisabled(), false);
      assert.equal(await page.locator('#method').inputValue(), 'memory-basics-v1');
      assert.match(await page.locator('#material').innerText(), /Arbeidsminnet holder/);
      await visible(page, '#material-body');
      await visible(page, '#results', false);
      await pendingRoute.abort();
      await page.unroute('**/api/v1/demo/generate');
      await page.locator('#retry').click();
      await page.locator('#results').waitFor({state: 'visible'});
      await page.locator('#edit-material').click();
    });

    await check('busy prevents duplicate submissions and reset ignores uncancellable late success', async () => {
      await page.evaluate(() => { window.ignoreGenerationAbort = true; });
      let release;
      const held = new Promise(resolve => { release = resolve; });
      let entered;
      const intercepted = new Promise(resolve => { entered = resolve; });
      await page.route('**/api/v1/demo/generate', async route => { entered(); await held; await route.fulfill({json: validBundle}); });
      const before = generationCalls;
      await page.locator('#generate').click();
      await intercepted;
      assert.equal(await page.locator('#generate').isDisabled(), true);
      await page.locator('#generate').evaluate(button => { button.click(); button.click(); });
      assert.equal(generationCalls, before + 1);
      await page.locator('#reset').click();
      release();
      await page.waitForResponse('**/api/v1/demo/generate');
      await page.waitForTimeout(150);
      await visible(page, '#results', false);
      await visible(page, '#material-body');
      assert.equal(await page.locator('#method').inputValue(), '');
      assert.match(await page.locator('#status').innerText(), /Ny økt/);
      await page.unroute('**/api/v1/demo/generate');
      await page.evaluate(() => { window.ignoreGenerationAbort = false; });
      await page.locator('#method').selectOption('memory-basics-v1');
      await generate(page);
    });

    await check('320px, 390px, 480px and 200% layout zoom remain usable without overflow', async () => {
      for (const width of [320, 390, 480]) {
        await page.setViewportSize({width, height: 900});
        await noOverflow(page);
        await page.locator('#edit-material').click();
        await noOverflow(page);
        await generate(page);
        await page.locator('#tab-quiz').click();
        await page.locator('#reveal').click();
        await noOverflow(page);
      }
      await page.setViewportSize({width: 1280, height: 1000});
      await page.evaluate(() => { document.documentElement.style.zoom = '200%'; });
      await noOverflow(page);
      await page.locator('#edit-material').click();
      await noOverflow(page);
      await generate(page);
      await page.locator('#tab-flashcards').click();
      await page.locator('#reveal').click();
      await noOverflow(page);
      await fs.mkdir(path.join(root, 'test-results'), {recursive: true});
      await page.screenshot({path: path.join(root, 'test-results/demo-200-percent.png'), fullPage: true});
      await page.evaluate(() => { document.documentElement.style.zoom = ''; });
      await page.screenshot({path: path.join(root, 'test-results/demo-desktop.png'), fullPage: true});
    });
    assert.deepEqual(errors, [], 'browser JavaScript errors');
    console.log(`${checks} browser scenarios passed; ${generationCalls} generation requests observed.`);
  } finally {
    if (browser) await browser.close();
    if (server?.pid) {
      server.kill();
      await new Promise(resolve => server.exitCode !== null ? resolve() : server.once('exit', resolve));
    }
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
