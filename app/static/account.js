'use strict';
(() => {
  const status = document.getElementById('account-status');
  const error = document.getElementById('account-error');
  const forms = document.getElementById('account-forms');
  const signedIn = document.getElementById('account-signed-in');
  const email = document.getElementById('account-email');
  const retry = document.getElementById('account-retry');
  const recovery = document.getElementById('account-recovery');
  let csrf = null, busy = false, sequence = 0, active = null, formsRequested = false;
  let deadlineTimer = null, hasAuthority = false;
  let logoutPending = false, observePending = false;
  const channel = typeof BroadcastChannel === 'function' ? new BroadcastChannel('studybuddy-session') : null;
  const endedMessage = 'Tilgangen er avsluttet. Logg inn på nytt.';
  function endAccess(message = endedMessage, {broadcast = false} = {}) {
    ++sequence;
    active?.abort();
    clearTimeout(deadlineTimer);
    hasAuthority = false;
    confirmation = null;
    formsRequested = false;
    clearPasswords();
    clearDisplay();
    setBusy(false);
    forms.hidden = logoutPending || !csrf;
    error.hidden = true;
    retry.hidden = !!csrf;
    status.textContent = message;
    if (broadcast) channel?.postMessage('ended');
  }
  function armLifetime(value, started) {
    const snapshot = value.expiresInSeconds;
    if (typeof snapshot !== 'number' || !Number.isFinite(snapshot) || snapshot <= 0 || snapshot > 43200) throw new AccountError(unavailable);
    const seconds = snapshot - (performance.now() - started) / 1000;
    clearTimeout(deadlineTimer);
    if (seconds <= 0) { endAccess(); return false; }
    hasAuthority = true;
    deadlineTimer = setTimeout(() => endAccess(), seconds * 1000);
    return true;
  }
  function observe() {
    if (logoutPending) return;
    if (busy) { observePending = true; return; }
    observePending = false;
    bootstrap({background: true});
  }
  channel?.addEventListener('message', event => { if (event.data === 'ended') observe(); });
  const initial = new URL(location.href);
  const outcomeKind = initial.searchParams.has('recovery') ? 'recovery' : 'confirmation';
  const outcome = initial.searchParams.get(outcomeKind);
  let confirmation = initial.hash || (initial.search &&
    (initial.searchParams.size !== 1 || !['success', 'invalid'].includes(outcome))) ? 'invalid' : outcome;
  if (initial.search || initial.hash) history.replaceState(null, '', '/account');
  const confirmationError = 'Bekreftelseslenken er ugyldig eller utløpt. Start registreringen på nytt og åpne e-posten i samme nettleser innen 10 minutter.';
  const recoveryError = 'Gjenopprettingslenken er ugyldig eller utløpt. Be om en ny lenke og åpne den i samme nettleser innen 10 minutter.';
  const recoveryFailed = 'Passordendringen kunne ikke bekreftes. Passordet kan være endret. Prøv å logge inn, eller be om en ny lenke.';
  const unavailable = 'Innlogging er ikke tilgjengelig nå. Studiedemoen kan fortsatt brukes.';
  class AccountError extends Error {
    constructor(message, code = null) {
      super(message);
      this.code = code;
    }
  }

  function clearPasswords() {
    document.querySelectorAll('input[type=password]').forEach(input => { input.value = ''; input.setCustomValidity(''); });
  }
  function setBusy(value) {
    busy = value;
    document.querySelectorAll('form button, [data-account-navigation]').forEach(button => { button.disabled = value; });
    forms.setAttribute('aria-busy', String(value));
    recovery.setAttribute('aria-busy', String(value));
    if (!value && observePending) queueMicrotask(observe);
  }
  function fail(message) {
    error.textContent = message;
    error.hidden = false;
    error.focus();
  }
  function clearDisplay() {
    signedIn.hidden = true;
    recovery.hidden = true;
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
          invalid_recovery: recoveryError,
          recovery_failed: recoveryFailed,
        };
        throw new AccountError(Object.hasOwn(messages, data.code) ? messages[data.code] : unavailable,
          typeof data.code === 'string' ? data.code : null);
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
    formsRequested = false;
    forms.hidden = true;
    recovery.hidden = true;
    email.textContent = value.email;
    signedIn.hidden = false;
    status.textContent = 'Du er logget inn.';
  }
  async function bootstrap({background = false} = {}) {
    if (logoutPending) return;
    active?.abort();
    const id = ++sequence;
    const started = performance.now();
    const hadRecovery = !recovery.hidden;
    const hadAuthority = hasAuthority;
    const preserveDraft = background && (!forms.hidden || hadRecovery);
    if (!preserveDraft) clearPasswords();
    if (!background) { clearDisplay(); csrf = null; }
    if (!preserveDraft) forms.hidden = true;
    retry.hidden = true;
    if (!background) {
      error.hidden = true;
      status.textContent = 'Kontrollerer innlogging …';
      setBusy(true);
    }
    try {
      const data = await request('status', {}, id);
      if (!data) return;
      if (data.available !== true) {
        endAccess(unavailable, {broadcast: hadAuthority});
        csrf = null;
        forms.hidden = true;
        status.textContent = unavailable;
        retry.hidden = false;
        return;
      }
      if (typeof data.csrfToken !== 'string' || !data.csrfToken || typeof data.authenticated !== 'boolean') throw new AccountError(unavailable);
      csrf = data.csrfToken;
      if (data.authenticated || data.recoveryAvailable === true) {
        if (!armLifetime(data, started)) return;
      }
      else {
        clearTimeout(deadlineTimer);
        hasAuthority = false;
        if (hadAuthority) {
          formsRequested = false;
        }
      }
      if (!data.authenticated && data.recoveryAvailable !== true) clearDisplay();
      if (formsRequested) {
        forms.hidden = false;
        status.textContent = data.authenticated ? 'Du er fortsatt logget inn. Du kan logge inn på nytt eller gjenopprette passord.' : 'Velg innlogging eller be om en ny gjenopprettingslenke.';
      } else if (data.authenticated) showIdentity(data);
      else if (data.recoveryAvailable === true) {
        forms.hidden = true;
        recovery.hidden = false;
        status.textContent = 'Du kan endre passordet. Du er ikke logget inn.';
      } else {
        if (hadRecovery || hadAuthority) clearPasswords();
        forms.hidden = false;
        status.textContent = hadAuthority ? endedMessage : 'Du er ikke logget inn.';
      }
      const pendingConfirmation = confirmation;
      confirmation = null;
      const linkError = outcomeKind === 'recovery' ? recoveryError : confirmationError;
      if (pendingConfirmation === 'invalid') fail(linkError);
      else if (pendingConfirmation === 'success' && !(outcomeKind === 'recovery' ? data.recoveryAvailable : data.authenticated)) fail(linkError);
    } catch (failure) {
      if (id !== sequence) return;
      endAccess(endedMessage, {broadcast: hadAuthority});
      csrf = null;
      forms.hidden = true;
      status.textContent = '';
      fail(failure.name === 'AbortError' ? 'Forespørselen tok for lang tid. Prøv igjen.' : (failure instanceof AccountError ? failure.message : unavailable));
      retry.hidden = false;
      setBusy(false);
    } finally {
      if (id === sequence) {
        setBusy(false);
      }
    }
  }
  document.getElementById('recovery-form').addEventListener('submit', async event => {
    event.preventDefault();
    if (busy || !csrf) return;
    const body = JSON.stringify({email: document.getElementById('recovery-email').value.trim()});
    const id = ++sequence;
    active?.abort();
    setBusy(true);
    error.hidden = true;
    status.textContent = 'Sender gjenopprettingslenken …';
    try {
      const data = await request('recovery/request', {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf}, body}, id);
      if (!data) return;
      if (data.status !== 'check_email') throw new AccountError(unavailable);
      status.textContent = 'Hvis kontoen finnes, får du en e-post. Åpne lenken i samme nettleser innen 10 minutter.';
    } catch (failure) {
      if (id !== sequence) return;
      status.textContent = '';
      fail(failure.name === 'AbortError' ? 'Forespørselen tok for lang tid. Prøv igjen.' : (failure instanceof AccountError ? failure.message : unavailable));
    } finally {
      if (id === sequence) setBusy(false);
    }
  });
  const newPassword = document.getElementById('recovery-password');
  const confirmPassword = document.getElementById('recovery-password-confirm');
  for (const input of [newPassword, confirmPassword]) input.addEventListener('input', () => {
    newPassword.setCustomValidity('');
    confirmPassword.setCustomValidity('');
  });
  document.getElementById('recovery-password-form').addEventListener('submit', async event => {
    event.preventDefault();
    if (busy || !csrf || recovery.hidden) return;
    // Native minlength/maxlength count UTF-16 units; the server counts code points.
    const length = [...newPassword.value].length;
    if (length < 8 || length > 1024) {
      newPassword.setCustomValidity('Bruk 8–1024 tegn i passordet.');
      newPassword.reportValidity();
      return;
    }
    if (newPassword.value !== confirmPassword.value) {
      confirmPassword.setCustomValidity('Passordene må være like.');
      confirmPassword.reportValidity();
      return;
    }
    const body = JSON.stringify({password: newPassword.value});
    clearPasswords();
    const id = ++sequence;
    active?.abort();
    setBusy(true);
    error.hidden = true;
    retry.hidden = true;
    status.textContent = 'Endrer passord …';
    try {
      const data = await request('recovery/password', {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf}, body}, id);
      if (!data) return;
      clearTimeout(deadlineTimer);
      hasAuthority = false;
      clearDisplay();
      forms.hidden = false;
      confirmation = null;
      channel?.postMessage('ended');
      if (data.status !== 'password_updated' || data.authenticated !== false) throw new AccountError(recoveryFailed);
      status.textContent = 'Passordet er endret. Logg inn med det nye passordet.';
      document.getElementById('login-email').focus();
    } catch (failure) {
      if (id !== sequence) return;
      confirmation = null;
      status.textContent = '';
      const correctable = {
        invalid_request: 'Kontroller passordet og prøv igjen. Bruk 8–1024 tegn. Passordet er ikke endret.',
        request_rejected: 'Forespørselen ble avvist. Velg Prøv igjen for å kontrollere tilgangen på nytt. Passordet er ikke endret.',
        auth_unavailable: 'Passordendring er ikke tilgjengelig nå. Passordet er ikke endret. Prøv igjen senere.',
      };
      if (failure instanceof AccountError && Object.hasOwn(correctable, failure.code)) {
        recovery.hidden = false;
        forms.hidden = true;
        retry.hidden = failure.code === 'invalid_request';
        fail(correctable[failure.code]);
      } else {
        clearDisplay();
        forms.hidden = false;
        fail(failure instanceof AccountError && failure.code === 'invalid_recovery' ? recoveryError : recoveryFailed);
      }
    } finally {
      if (id === sequence) setBusy(false);
    }
  });
  for (const button of document.querySelectorAll('[data-account-navigation]')) button.addEventListener('click', () => {
    if (busy || !csrf) return;
    ++sequence;
    active?.abort();
    formsRequested = true;
    confirmation = null;
    clearPasswords();
    clearDisplay();
    forms.hidden = false;
    error.hidden = true;
    retry.hidden = true;
    status.textContent = 'Velg innlogging eller be om en ny gjenopprettingslenke.';
    document.getElementById('login-email').focus();
  });
  for (const action of ['login', 'signup']) {
    document.getElementById(`${action}-form`).addEventListener('submit', async event => {
      event.preventDefault();
      if (busy || !csrf) return;
      const submittedEmail = document.getElementById(`${action}-email`).value.trim();
      // Serialize once and clear the field immediately, including on rejected requests.
      const body = JSON.stringify({email: submittedEmail, password: document.getElementById(`${action}-password`).value});
      clearPasswords();
      const id = ++sequence;
      active?.abort();
      if (action === 'login') clearTimeout(deadlineTimer);
      setBusy(true);
      error.hidden = true;
      status.textContent = action === 'signup' ? 'Sender registreringen …' : 'Logger inn …';
      try {
        const data = await request(action, {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf}, body}, id);
        if (!data) return;
        if (action === 'login') {
          confirmation = null;
          if (data.authenticated !== true || typeof data.email !== 'string' || !data.email) throw new AccountError(unavailable);
          formsRequested = false;
          observePending = false;
          await bootstrap({background: true});
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
  async function performLogout() {
    const refreshBinding = logoutPending || !csrf;
    logoutPending = true;
    endAccess('Logger ut …');
    const id = sequence;
    setBusy(true);
    try {
      if (refreshBinding) {
        const binding = await request('status', {}, id);
        if (!binding) return;
        if (binding.available !== true || typeof binding.csrfToken !== 'string' || !binding.csrfToken) throw new AccountError(unavailable);
        csrf = binding.csrfToken;
      }
      const data = await request('logout', {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf}, body: '{}'}, id);
      if (!data) return;
      if (data.authenticated !== false || data.recoveryAvailable !== false) throw new AccountError(unavailable);
      logoutPending = false;
      endAccess('Du er logget ut. Logg inn igjen når du vil.', {broadcast: true});
      document.getElementById('login-email').focus();
    } catch (failure) {
      if (id !== sequence) return;
      endAccess();
      fail('Utlogging kunne ikke bekreftes. Velg Prøv igjen for å logge ut.');
      retry.hidden = false;
    } finally {
      if (id === sequence) setBusy(false);
    }
  }
  for (const button of document.querySelectorAll('[data-account-logout]')) button.addEventListener('click', performLogout);
  retry.addEventListener('click', () => logoutPending ? performLogout() : bootstrap());
  window.addEventListener('pagehide', () => {
    csrf = null;
    endAccess();
  });
  window.addEventListener('pageshow', event => { if (event.persisted) logoutPending ? performLogout() : bootstrap(); });
  window.addEventListener('hashchange', () => {
    confirmation = 'invalid';
    history.replaceState(null, '', '/account');
    bootstrap();
  });
  window.addEventListener('focus', () => { if (!busy) bootstrap({background: true}); });
  document.addEventListener('visibilitychange', () => { if (!document.hidden && !busy) bootstrap({background: true}); });
  setInterval(() => { if (!document.hidden && !busy) bootstrap({background: true}); }, 30000);
  bootstrap();
})();
