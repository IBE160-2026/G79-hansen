'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const form = $('source-form'), controls = $('source-controls'), kind = $('source-kind');
  const text = $('source-text'), file = $('source-file'), subject = $('source-subject');
  const language = $('source-language'), detail = $('source-detail');
  const status = $('source-status'), error = $('source-error'), preview = $('source-preview');
  const retry = $('source-retry'), logout = $('source-logout'), signIn = $('source-sign-in');
  const channel = typeof BroadcastChannel === 'function' ? new BroadcastChannel('studybuddy-session') : null;
  const ended = 'Tilgangen er avsluttet. Logg inn på nytt.';
  const failed = 'Materialet kunne ikke behandles. Prøv igjen.';
  let csrf = null, view = null, revision = 0, sequence = 0, authSequence = 0;
  let active = null, authActive = null, lifetime = null, busy = false, logoutPending = false;
  let observation = null, logoutBusy = false, logoutController = null, logoutSequence = 0;
  const messages = {
    invalid_input: 'Velg én kilde og kontroller materialet før du prøver igjen.',
    invalid_text: 'Teksten må være gyldig UTF-8 uten binære kontrolltegn.',
    character_limit: 'Materialet kan ha høyst 30 000 tegn. Ingen del er godtatt.',
    byte_limit: 'Filen kan være høyst 10 MiB. Ingen del er godtatt.',
    wire_limit: 'Opplastingen er for stor. Ingen del er godtatt.',
    page_limit: 'PDF-en kan ha høyst 40 fysiske sider, også blanke sider og bildesider.',
    no_readable_text: 'Materialet har ingen lesbar tekst. OCR er ikke tilgjengelig.',
    encrypted_pdf: 'Krypterte PDF-er støttes ikke. Passord kan ikke oppgis.',
    invalid_pdf: 'PDF-en kunne ikke leses. Ingen del er godtatt.',
    isolation_unavailable: 'Sikker PDF-behandling er ikke tilgjengelig på denne serveren.',
    source_capacity: 'For mye materiale behandles nå. Vent litt og prøv igjen.',
    body_timeout: 'Opplastingen tok for lang tid. Prøv igjen.',
    request_rejected: 'Forespørselen ble avvist. Last siden på nytt og prøv igjen.',
    extraction_failed: failed,
  };
  function setBusy(value) {
    busy = value;
    $('check-source').disabled = value;
    form.setAttribute('aria-busy', String(value));
  }
  function clearPreview() {
    preview.hidden = true;
    $('source-units').replaceChildren();
    $('source-coverage').replaceChildren();
    $('source-count').textContent = '';
  }
  function invalidate() {
    ++revision; ++sequence;
    active?.abort(); active = null;
    clearPreview();
    error.hidden = true; retry.hidden = true;
    setBusy(false);
    if (view) status.textContent = 'Materialet er endret. Kontroller det på nytt.';
  }
  function showMethod() {
    $('source-paste-area').hidden = kind.value !== 'paste';
    $('source-file-area').hidden = kind.value === 'paste';
    file.accept = kind.value === 'pdf' ? '.pdf,application/pdf' : '.txt,text/plain';
  }
  function clearDraft() {
    invalidate();
    text.value = ''; file.value = ''; subject.value = '';
    kind.value = 'paste'; language.value = 'nb'; detail.value = 'short';
    showMethod();
  }
  function endAccess(message = ended) {
    ++authSequence;
    authActive?.abort(); authActive = null; observation = null;
    clearTimeout(lifetime);
    csrf = null; view = null;
    clearDraft();
    controls.disabled = true; form.hidden = true; logout.hidden = true;
    signIn.hidden = false;
    retry.hidden = !logoutPending;
    retry.disabled = logoutBusy;
    status.textContent = message;
  }
  function fail(message) {
    error.textContent = message;
    error.hidden = false; retry.hidden = false;
    error.focus();
  }
  function observe() {
    if (observation) return observation;
    const pending = observeSession();
    observation = pending;
    pending.finally(() => { if (observation === pending) observation = null; });
    return pending;
  }
  async function confirmAccess(id) {
    // An observation begun before extraction is not its final authority check.
    if (observation) await observation;
    if (id !== sequence) return false;
    return observe();
  }
  async function observeSession() {
    if (logoutPending) return false;
    const id = ++authSequence, started = performance.now();
    authActive?.abort();
    const controller = new AbortController(); authActive = controller;
    const timer = setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch('/api/v1/auth/status', {credentials: 'same-origin', cache: 'no-store', signal: controller.signal});
      const data = await response.json();
      if (id !== authSequence) return false;
      if (!response.ok || data.available !== true || data.authenticated !== true ||
          typeof data.csrfToken !== 'string' || !data.csrfToken ||
          typeof data.sessionViewId !== 'string' || !data.sessionViewId ||
          typeof data.expiresInSeconds !== 'number' || !Number.isFinite(data.expiresInSeconds) ||
          data.expiresInSeconds <= 0 || data.expiresInSeconds > 43200) {
        endAccess(data.available === false ? 'Innlogging er ikke tilgjengelig nå. Studiedemoen kan fortsatt brukes.' : ended);
        return false;
      }
      const seconds = data.expiresInSeconds - (performance.now() - started) / 1000;
      if (seconds <= 0) { endAccess(); return false; }
      const changed = view && view !== data.sessionViewId;
      if (changed) clearDraft();
      const initial = view === null;
      csrf = data.csrfToken; view = data.sessionViewId;
      clearTimeout(lifetime); lifetime = setTimeout(() => endAccess(), seconds * 1000);
      controls.disabled = false; form.hidden = false; logout.hidden = false; signIn.hidden = true;
      if (initial || changed) status.textContent = changed ? 'Ny innlogging. Velg materialet på nytt.' : 'Du er logget inn. Velg materialet du vil kontrollere.';
      return true;
    } catch {
      if (id === authSequence) {
        endAccess('Tilgangen kunne ikke bekreftes. Kontroller innloggingen på nytt.');
        retry.hidden = false;
      }
      return false;
    } finally {
      clearTimeout(timer);
      if (id === authSequence) authActive = null;
    }
  }
  function render(data) {
    if (!data || data.schemaVersion !== '1.0' || data.clientRevision !== revision ||
        !data.source || !Array.isArray(data.source.units) || !data.source.units.length ||
        !Number.isInteger(data.characterCount) || data.characterCount < 1 || data.characterCount > 30000 ||
        !Array.isArray(data.warnings) || !Array.isArray(data.unreadablePages)) throw new Error(failed);
    const units = document.createDocumentFragment();
    for (const unit of data.source.units) {
      if (!['paragraph', 'page'].includes(unit.kind) || !Number.isInteger(unit.location) || unit.location < 1 || typeof unit.text !== 'string') throw new Error(failed);
      const section = document.createElement('section'); section.className = 'source-unit';
      const heading = document.createElement('h3');
      heading.textContent = `${unit.kind === 'page' ? 'Side' : 'Avsnitt'} ${unit.location}`;
      const content = document.createElement('p'); content.className = 'canonical-text'; content.textContent = unit.text;
      section.append(heading, content); units.append(section);
    }
    const warnings = document.createDocumentFragment();
    for (const warning of data.warnings) {
      if (typeof warning !== 'string') throw new Error(failed);
      const p = document.createElement('p'); p.className = 'state-notice'; p.textContent = warning; warnings.append(p);
    }
    $('source-units').replaceChildren(units);
    $('source-coverage').replaceChildren(warnings);
    $('source-count').textContent = `${data.characterCount} tegn` + (data.totalPages ? ` · ${data.totalPages} fysiske sider` : ` · ${data.source.units.length} avsnitt`);
    preview.hidden = false;
    status.textContent = 'Materialet er kontrollert. Forhåndsvisningen viser kildeteksten. Generering kommer senere.';
    $('source-preview-heading').focus();
  }
  async function submit() {
    if (busy || !view || !csrf || logoutPending) return;
    clearPreview(); error.hidden = true; retry.hidden = true;
    const id = ++sequence, submittedView = view, submittedRevision = revision;
    const controller = new AbortController(); active = controller;
    const timer = setTimeout(() => controller.abort(), 20000);
    setBusy(true); status.textContent = 'Kontrollerer materialet …';
    try {
      const body = {schemaVersion: '1.0', kind: kind.value, settings: {language: language.value, detail: detail.value, subject: subject.value}, clientRevision: submittedRevision};
      if (kind.value === 'paste') {
        let count = 0;
        for (const char of text.value.replace(/\r\n?/g, '\n')) {
          if (++count > 30000) throw new Error(messages.character_limit);
        }
        body.text = text.value;
      }
      else {
        const selected = file.files[0];
        if (!selected) throw new Error(messages.invalid_input);
        if (selected.size > 10 * 1024 * 1024) throw new Error(messages.byte_limit);
        const bytes = new Uint8Array(await selected.arrayBuffer());
        if (id !== sequence || view !== submittedView) return;
        let binary = '';
        for (let offset = 0; offset < bytes.length; offset += 32768) binary += String.fromCharCode(...bytes.subarray(offset, offset + 32768));
        body.contentBase64 = btoa(binary);
      }
      const response = await fetch('/api/v1/sources/extract', {method: 'POST', credentials: 'same-origin', cache: 'no-store', signal: controller.signal,
        headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf, 'X-Session-View': submittedView}, body: JSON.stringify(body)});
      const data = await response.json();
      if (id !== sequence || view !== submittedView) return;
      if (response.status === 401) { endAccess(); return; }
      if (!response.ok) throw new Error(Object.hasOwn(messages, data.code) ? messages[data.code] : failed);
      // A delayed success must also survive authoritative browser observation.
      if (!await confirmAccess(id) || id !== sequence || view !== submittedView) return;
      render(data);
    } catch (failure) {
      if (id !== sequence || view !== submittedView) return;
      status.textContent = '';
      fail(failure.name === 'AbortError' ? 'Forespørselen tok for lang tid. Prøv igjen.' : (Object.values(messages).includes(failure.message) ? failure.message : failed));
    } finally {
      clearTimeout(timer);
      if (id === sequence) { active = null; setBusy(false); }
    }
  }
  for (const input of [text, file, subject, language, detail]) input.addEventListener(input === file || input.tagName === 'SELECT' ? 'change' : 'input', invalidate);
  kind.addEventListener('change', () => { invalidate(); text.value = ''; file.value = ''; showMethod(); });
  form.addEventListener('submit', event => { event.preventDefault(); submit(); });
  $('reset-source').addEventListener('click', () => { clearDraft(); status.textContent = 'Ny økt. Velg én kilde.'; text.focus(); });
  retry.addEventListener('click', () => logoutPending ? performLogout() : view ? submit() : observe());
  async function performLogout() {
    if (logoutBusy) return;
    const token = csrf;
    const id = ++logoutSequence, controller = new AbortController();
    logoutController = controller; logoutBusy = true; logoutPending = true;
    const timer = setTimeout(() => controller.abort(), 15000);
    endAccess('Logger ut …');
    try {
      let binding = token;
      if (!binding) {
        const response = await fetch('/api/v1/auth/status', {credentials: 'same-origin', cache: 'no-store', signal: controller.signal});
        const data = await response.json();
        if (!response.ok || data?.available !== true || typeof data.csrfToken !== 'string' || !data.csrfToken) throw new Error();
        binding = data.csrfToken;
      }
      if (id !== logoutSequence) return;
      const response = await fetch('/api/v1/auth/logout', {method: 'POST', credentials: 'same-origin', cache: 'no-store', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': binding}, body: '{}', signal: controller.signal});
      const data = await response.json();
      if (id !== logoutSequence) return;
      if (!response.ok || data?.authenticated !== false || data.recoveryAvailable !== false) throw new Error();
      logoutPending = false; channel?.postMessage('ended'); endAccess('Du er logget ut. Logg inn på nytt når du vil.');
    } catch {
      if (id === logoutSequence) fail('Utlogging kunne ikke bekreftes. Velg Prøv igjen for å logge ut.');
    } finally {
      clearTimeout(timer);
      if (id === logoutSequence) { logoutBusy = false; logoutController = null; retry.disabled = false; }
    }
  }
  logout.addEventListener('click', performLogout);
  channel?.addEventListener('message', event => { if (event.data === 'ended') observe(); });
  window.addEventListener('pagehide', () => {
    ++logoutSequence; logoutController?.abort(); logoutController = null; logoutBusy = false;
    endAccess();
  });
  window.addEventListener('pageshow', event => { if (event.persisted) observe(); });
  window.addEventListener('focus', observe);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) observe(); });
  setInterval(() => { if (!document.hidden) observe(); }, 30000);
  observe();
})();
