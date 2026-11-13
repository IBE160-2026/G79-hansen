'use strict';
(() => {
  const status = document.getElementById('account-status');
  const error = document.getElementById('account-error');
  const forms = document.getElementById('account-forms');
  const signedIn = document.getElementById('account-signed-in');
  const email = document.getElementById('account-email');
  const retry = document.getElementById('account-retry');
  let csrf = null, busy = false, sequence = 0, active = null;
  const initial = new URL(location.href);
  const outcome = initial.searchParams.get('confirmation');
  let confirmation = initial.hash || (initial.search &&
    (initial.searchParams.size !== 1 || !['success', 'invalid'].includes(outcome))) ? 'invalid' : outcome;
  if (initial.search || initial.hash) history.replaceState(null, '', '/account');
  const confirmationError = 'Bekreftelseslenken er ugyldig eller utløpt. Start registreringen på nytt og åpne e-posten i samme nettleser innen 10 minutter.';
  const unavailable = 'Innlogging er ikke tilgjengelig nå. Studiedemoen kan fortsatt brukes.';
  class AccountError extends Error {}

  function clearPasswords() {
    document.querySelectorAll('input[type=password]').forEach(input => { input.value = ''; });
  }
  function setBusy(value) {
    busy = value;
    document.querySelectorAll('form button').forEach(button => { button.disabled = value; });
    forms.setAttribute('aria-busy', String(value));
  }
  function fail(message) {
    error.textContent = message;
    error.hidden = false;
    error.focus();
  }
  function clearDisplay() {
    signedIn.hidden = true;
    email.textContent = '';
  }
  async function request(path, options, id) {
    const controller = new AbortController();
    active = controller;
    const timer = setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch(`/api/v1/auth/${path}`, {
        ...options, credentials: 'same-origin', cache: 'no-store', signal: controller.signal,
      });
      const data = await response.json();
      if (id !== sequence) return null;
      if (!data || typeof data !== 'object' || Array.isArray(data)) throw new AccountError(unavailable);
      if (!response.ok) {
        // Never render provider/server messages or arbitrary response strings.
        const messages = {
          invalid_credentials: 'Kunne ikke logge inn. Kontroller e-post, passord og bekreftelsen på e-post.',
          invalid_request: 'Kontroller e-post og passord og prøv igjen.',
          request_rejected: 'Forespørselen ble avvist. Last siden på nytt og prøv igjen.',
          auth_capacity: 'For mange pågående forsøk. Vent litt og prøv igjen.',
        };
        throw new AccountError(Object.hasOwn(messages, data.code) ? messages[data.code] : unavailable);
      }
      return data;
    } finally {
      clearTimeout(timer);
      if (id === sequence) active = null;
    }
  }
  function showIdentity(value) {
    if (value.authenticated !== true || typeof value.email !== 'string' || !value.email) throw new AccountError(unavailable);
    clearPasswords();
    forms.hidden = true;
    email.textContent = value.email;
    signedIn.hidden = false;
    status.textContent = 'Du er logget inn.';
  }
  async function bootstrap({background = false} = {}) {
    active?.abort();
    const id = ++sequence;
    const preserveDraft = background && !forms.hidden;
    const focused = preserveDraft ? document.activeElement : null;
    if (!preserveDraft) clearPasswords();
    clearDisplay();
    csrf = null;
    if (!preserveDraft) forms.hidden = true;
    retry.hidden = true;
    error.hidden = true;
    status.textContent = 'Kontrollerer innlogging …';
    setBusy(true);
    try {
      const data = await request('status', {}, id);
      if (!data) return;
      if (data.available !== true) {
        forms.hidden = true;
        status.textContent = unavailable;
        retry.hidden = false;
        return;
      }
      if (typeof data.csrfToken !== 'string' || !data.csrfToken || typeof data.authenticated !== 'boolean') throw new AccountError(unavailable);
      csrf = data.csrfToken;
      if (data.authenticated) showIdentity(data);
      else {
        forms.hidden = false;
        status.textContent = 'Du er ikke logget inn.';
      }
      const pendingConfirmation = confirmation;
      confirmation = null;
      if (pendingConfirmation === 'invalid') fail(confirmationError);
      else if (pendingConfirmation === 'success' && !data.authenticated) fail(confirmationError);
    } catch (failure) {
      if (id !== sequence) return;
      forms.hidden = true;
      status.textContent = '';
      fail(failure.name === 'AbortError' ? 'Forespørselen tok for lang tid. Prøv igjen.' : (failure instanceof AccountError ? failure.message : unavailable));
      retry.hidden = false;
    } finally {
      if (id === sequence) {
        setBusy(false);
        if (preserveDraft && !forms.hidden && error.hidden && focused?.isConnected) focused.focus();
      }
    }
  }
  for (const action of ['login', 'signup']) {
    document.getElementById(`${action}-form`).addEventListener('submit', async event => {
      event.preventDefault();
      if (busy || !csrf) return;
      const submittedEmail = document.getElementById(`${action}-email`).value.trim();
      // Serialize once and clear the field immediately, including on rejected requests.
      const body = JSON.stringify({email: submittedEmail, password: document.getElementById(`${action}-password`).value});
      clearPasswords();
      const id = ++sequence;
      setBusy(true);
      error.hidden = true;
      status.textContent = action === 'signup' ? 'Sender registreringen …' : 'Logger inn …';
      try {
        const data = await request(action, {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf}, body}, id);
        if (!data) return;
        if (action === 'login') {
          confirmation = null;
          showIdentity(data);
        }
        else {
          if (data.status !== 'check_email') throw new AccountError(unavailable);
          status.textContent = 'Hvis kontoen kan opprettes, får du en e-post. Åpne bekreftelsen i samme nettleser innen 10 minutter.';
        }
      } catch (failure) {
        if (id !== sequence) return;
        clearDisplay();
        status.textContent = '';
        fail(failure.name === 'AbortError' ? 'Forespørselen tok for lang tid. Prøv igjen.' : (failure instanceof AccountError ? failure.message : unavailable));
      } finally {
        if (id === sequence) setBusy(false);
      }
    });
  }
  retry.addEventListener('click', () => bootstrap());
  window.addEventListener('pagehide', () => {
    ++sequence;
    active?.abort();
    clearPasswords();
    clearDisplay();
    csrf = null;
  });
  window.addEventListener('pageshow', event => { if (event.persisted) bootstrap(); });
  window.addEventListener('hashchange', () => {
    confirmation = 'invalid';
    history.replaceState(null, '', '/account');
    bootstrap();
  });
  window.addEventListener('focus', () => { if (!busy) bootstrap({background: true}); });
  bootstrap();
})();
