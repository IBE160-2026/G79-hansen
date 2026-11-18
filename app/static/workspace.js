'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const form = $('source-form'), controls = $('source-controls'), kind = $('source-kind');
  const text = $('source-text'), file = $('source-file'), subject = $('source-subject');
  const language = $('source-language'), detail = $('source-detail');
  const status = $('source-status'), error = $('source-error'), preview = $('source-preview');
  const retry = $('source-retry'), logout = $('source-logout'), signIn = $('source-sign-in');
  const workspaceId = crypto.randomUUID();
  let commandSequence = 0, accepted = null, bundle = null, receipt = null, activeTab = 'summary';
  let positions = {flashcards: 0, quiz: 0}, revealed = {flashcards: new Set(), quiz: new Set()};
  let pendingInvalidation = null, invalidating = null, retryOperation = 'extract';
  const channel = typeof BroadcastChannel === 'function' ? new BroadcastChannel('studybuddy-session') : null;
  const ended = 'Tilgangen er avsluttet. Logg inn på nytt.';
  const failed = 'Materialet kunne ikke behandles. Prøv igjen.';
  let csrf = null, view = null, revision = 0, sequence = 0, authSequence = 0;
  let active = null, authActive = null, lifetime = null, busy = false, logoutPending = false;
  let observation = null, logoutBusy = false, logoutController = null, logoutSequence = 0;
  let saveAttempt = null, saveAttemptNavigation = null, savedTarget = null, saveBusy = false, saveEpoch = 0;
  let saveUncertain = false, discoveryEpoch = 0;
  let libraryOpen = false, libraryEpoch = 0, libraryCursor = null, libraryBusy = false, draftDirty = false;
  let replacement = null;
  const saveMessages = {
    library_unavailable: 'Dokumentene kunne ikke hentes. Materialet er beholdt. Prøv igjen.',
    document_unknown: 'Dokumentet er ikke tilgjengelig for kontoen. Materialet er beholdt.',
    file_unavailable: 'Originalfilen kunne ikke hentes eller kontrolleres. Prøv igjen.',
    save_unavailable: 'Lagring er ikke konfigurert. Materialet er beholdt.',
    save_pending: 'Lagringen er ikke bekreftet. Prøv samme lagring igjen.',
    save_conflict: 'Dokumentet er endret. Hent lagret versjon eller lagre som nytt.',
    save_expired: 'Lagringen er utløpt. Bare opprydding er tilgjengelig.',
    save_mismatch: 'Materialet eller filen samsvarer ikke med lagringen.',
    file_required: 'Velg samme originalfil for å fortsette.',
    save_capacity: 'En lagring pågår. Vent litt og prøv igjen.',
    invalid_proof: 'Lag læringsmaterialet på nytt før en ny lagring.',
    stale_workspace: 'Materialet er endret. Lag læringsmaterialet på nytt.',
    invalid_input: 'Kontroller tittelen og materialet før du prøver igjen.',
  };
  function saveControls() {
    $('save-document').disabled = saveBusy || libraryBusy || busy || !bundle || !receipt || savedTarget?.generationId === bundle?.generationId;
    $('save-title').disabled = saveBusy || libraryBusy || !!saveAttempt || !bundle || savedTarget?.generationId === bundle?.generationId;
    for (const id of ['save-again', 'save-reload', 'save-new']) $(id).disabled = saveBusy || libraryBusy;
  }
  async function documentRequest(path, body, submittedView, stillCurrent = () => true) {
    const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 70000);
    try {
      const response = await fetch('/api/v1/documents/' + path, {method: 'POST', credentials: 'same-origin', cache: 'no-store',
        signal: controller.signal, headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf, 'X-Session-View': submittedView}, body: JSON.stringify(body)});
      const data = await response.json();
      if (view !== submittedView || !stillCurrent()) return null;
      if (response.status === 401) { endAccess(); return null; }
      if (!response.ok) { const failure = new Error(saveMessages[data.code] || saveMessages.save_pending); failure.code = data.code; failure.saveDisabled = data.saveDisabled === true; throw failure; }
      return data;
    } finally { clearTimeout(timer); }
  }
  // Progress authority follows the active workspace, never library pagination.
  let progressEpoch = 0, progressState = null, practiceNavigation = 0;
  const progressRequests = new Set();
  const progressMessages = {
    progress_conflict: 'Fremdriften er endret på en annen enhet',
    progress_generation: 'Dokumentet har en ny versjon. Åpne det lagrede dokumentet på nytt.',
    progress_pending: 'Fremdriften er ikke bekreftet.',
    progress_mismatch: 'Fremdriftsoppdateringen ble avvist. Hent siste fremdrift.',
  };
  function progressNotice(message = '', recover = false, retryable = false) {
    $('progress-status').textContent = message;
    $('progress-fetch').hidden = !recover;
    $('progress-retry').hidden = !retryable;
    $('progress-fetch').disabled = !!progressState?.busy;
    $('progress-retry').disabled = !!progressState?.busy;
  }
  function clearProgress() {
    ++progressEpoch; progressState = null;
    for (const request of progressRequests) { clearTimeout(request.timer); request.controller.abort(); }
    progressRequests.clear(); progressNotice();
  }
  function fenceProgressForOpen() {
    const previous = progressState;
    clearProgress();
    if (previous) {
      progressState = {...previous, epoch:progressEpoch, busy:false, blocked:true, failure:'progress_pending', frozen:null, queued:null};
      progressNotice('Hent siste fremdrift før videre lagring.',true);
    }
  }
  function practicePositions() {
    return {flashcardId: bundle.flashcards[positions.flashcards]?.id || null, quizId: bundle.quiz[positions.quiz]?.id || null};
  }
  function samePositions(one, two) { return one?.flashcardId === two?.flashcardId && one?.quizId === two?.quizId; }
  function startProgress(progressRevision, acknowledged) {
    clearProgress();
    progressState = {epoch: progressEpoch, view, documentId: savedTarget.documentId, generationId: savedTarget.generationId,
      revision: progressRevision, acknowledged, queued: null, frozen: null, busy: false, blocked: false};
    progressNotice('Fremdriften er lagret.');
  }
  function progressCurrent(state) {
    return progressState === state && state.epoch === progressEpoch && view === state.view &&
      savedTarget?.documentId === state.documentId && savedTarget?.generationId === state.generationId && bundle?.generationId === state.generationId;
  }
  function validProgress(data, state) {
    return data?.schemaVersion === '1.0' && data.documentId === state.documentId && data.generationId === state.generationId &&
      Number.isSafeInteger(data.progressRevision) && data.progressRevision >= 1 && data.positions &&
      [['flashcards','flashcardId'],['quiz','quizId']].every(([section,key]) => bundle[section].length ?
        bundle[section].some(item => item.id === data.positions[key]) : data.positions[key] === null);
  }
  async function progressRequest(path, body, state) {
    const request = {controller: new AbortController(), timer: null};
    request.timer = setTimeout(() => { if (progressCurrent(state)) request.controller.abort(); }, 20000);
    progressRequests.add(request);
    try {
      const response = await fetch('/api/v1/progress/' + path, {method: 'POST', credentials: 'same-origin', cache: 'no-store',
        signal: request.controller.signal, headers: {'Content-Type':'application/json','X-CSRF-Token':csrf,'X-Session-View':state.view}, body: JSON.stringify(body)});
      if (!progressCurrent(state)) return null;
      if (response.status === 401) { endAccess(); return null; }
      const data = await response.json();
      if (!progressCurrent(state)) return null;
      if (!response.ok) { const failure = new Error(progressMessages[data.code] || progressMessages.progress_pending); failure.code = data.code; throw failure; }
      if (!validProgress(data,state)) throw new Error(progressMessages.progress_pending);
      return data;
    } finally { clearTimeout(request.timer); progressRequests.delete(request); }
  }
  function queueProgress() {
    const state = progressState;
    if (!state || !progressCurrent(state)) return;
    state.queued = practicePositions();
    if (!state.busy && !state.blocked && !state.frozen) sendProgress(state);
  }
  async function sendProgress(state) {
    if (!progressCurrent(state) || state.busy || state.blocked) return;
    if (!state.frozen) {
      if (!state.queued || samePositions(state.queued,state.acknowledged)) { state.queued = null; return; }
      state.frozen = {schemaVersion:'1.0',documentId:state.documentId,generationId:state.generationId,
        mutationId:crypto.randomUUID(),expectedProgressRevision:state.revision,positions:state.queued};
      state.queued = null;
    }
    state.busy = true; progressNotice('Lagrer fremdrift …');
    try {
      let data;
      // One automatic retry of the exact admitted request after uncertain transport.
      for (let attempt=0; attempt<2; attempt++) {
        try { data = await progressRequest('write',state.frozen,state); break; }
        catch (failure) {
          if (!progressCurrent(state)) return;
          if (attempt || (failure.code && !['progress_pending','save_capacity'].includes(failure.code))) throw failure;
        }
      }
      if (!data || !progressCurrent(state)) return;
      state.revision = data.progressRevision; state.acknowledged = data.positions; state.frozen = null;
      // Acknowledgement never jumps the visible position back during coalescing.
      progressNotice('Fremdriften er lagret.');
    } catch (failure) {
      if (!progressCurrent(state)) return;
      state.blocked = true;
      state.failure = failure.code || 'progress_pending';
      progressNotice(progressMessages[state.failure] || progressMessages.progress_pending, true,
        !['progress_conflict','progress_generation','progress_mismatch'].includes(state.failure));
    } finally {
      if (progressCurrent(state)) {
        state.busy = false;
        $('progress-fetch').disabled = false; $('progress-retry').disabled = false;
        if (!state.blocked && state.queued) sendProgress(state);
      }
    }
  }
  $('progress-retry').onclick = () => {
    const state = progressState;
    if (!state || !progressCurrent(state) || state.busy || !state.frozen || state.failure === 'progress_conflict') return;
    state.blocked = false; sendProgress(state);
  };
  $('progress-fetch').onclick = async () => {
    const state = progressState;
    if (!state || !progressCurrent(state) || state.busy) return;
    state.busy = true; progressNotice('Henter siste fremdrift …',true);
    try {
      const data = await progressRequest('read',{schemaVersion:'1.0',documentId:state.documentId,generationId:state.generationId},state);
      if (!data || !progressCurrent(state)) return;
      for (const [section,key] of [['flashcards','flashcardId'],['quiz','quizId']])
        positions[section] = Math.max(0,bundle[section].findIndex(item => item.id === data.positions[key]));
      revealed = {flashcards:new Set(),quiz:new Set()};
      state.revision = data.progressRevision; state.acknowledged = data.positions;
      state.frozen = null; state.queued = null; state.blocked = false; state.failure = null;
      renderLearning(); progressNotice('Siste fremdrift er hentet. Svarene er skjult.');
    } catch (failure) {
      if (!progressCurrent(state)) return;
      state.blocked = true;
      if (failure.code === 'progress_generation') state.failure = failure.code;
      progressNotice((progressMessages[state.failure] || progressMessages.progress_pending) + ' Siste fremdrift kunne ikke hentes.',true,
        !!state.frozen && !['progress_conflict','progress_generation','progress_mismatch'].includes(state.failure));
    } finally {
      if (progressCurrent(state)) { state.busy = false; $('progress-fetch').disabled = false; $('progress-retry').disabled = false; }
    }
  };
  async function discoverSaves(cursor = null, pageEpoch = null) {
    const submittedView = view;
    if (!submittedView) return;
    const epoch = cursor ? pageEpoch : ++discoveryEpoch;
    const current = () => view === submittedView && epoch === discoveryEpoch;
    if (!current()) return;
    try {
      const data = await documentRequest('pending', {schemaVersion: '1.0', cursor}, submittedView, current);
      if (!data || !current() || !Array.isArray(data.operations)) return;
      if (!cursor) { $('save-recovery-items').replaceChildren(); $('save-recovery').hidden = data.operations.length === 0; }
      for (const operation of data.operations) {
        const row = element('div', undefined, 'recovery-operation');
        row.dataset.operationId = operation.operationId;
        const expired = operation.cleanupOnly === true || operation.recoveryState === 'cleanup_only';
        const ready = operation.status === 'ready' && !expired;
        row.append(element('p', ready ? 'Lagret privat.' : expired ? 'Avsluttet lagring venter på opprydding.' : 'Lagring venter på bekreftelse.'));
        if (!expired && !ready && typeof operation.title === 'string') row.append(element('p', operation.title));
        for (const [key, label] of (ready || expired ? [['admittedAt', 'Startet']] : [['admittedAt', 'Startet'], ['expiresAt', 'Kan gjenopptas til']])) {
          const date = new Date(operation[key]);
          if (!Number.isNaN(date.getTime())) row.append(element('p', label + ': ' + date.toLocaleString('nb-NO')));
        }
        if (ready) { $('save-recovery-items').append(row); continue; }
        const resupply = element('input'); resupply.type = 'file'; resupply.accept = '.txt,.pdf,text/plain,application/pdf';
        resupply.id = 'recover-' + operation.operationId;
        if (operation.requiresFile && !expired) { const label = element('label', 'Samme originalfil'); label.htmlFor = resupply.id; row.append(label, resupply); }
        const action = element('button', expired ? 'Rydd opp' : 'Fortsett lagring'); action.type = 'button';
        action.onclick = async () => {
          if (!current()) return;
          action.disabled = true;
          try {
            const body = {schemaVersion: '1.0', operationId: operation.operationId};
            if (!expired) { body.digest = operation.digest; if (resupply.files[0]) body.contentBase64 = await encodeFile(resupply.files[0]); }
            const result = await documentRequest(expired ? 'cleanup' : 'retry', body, submittedView, current);
            if (!current() || !result) return;
            row.replaceChildren(element('p', result.status === 'ready' ? 'Lagret privat.' : result.status === 'cleanup_complete' ? 'Opprydding er fullført.' : 'Opprydding venter på bekreftelse.'));
            if (result.status === 'cleanup_pending') row.append(action);
          } catch (failure) {
            if (!current()) return;
            if (failure.code === 'save_expired' || failure.code === 'save_conflict') await discoverSaves();
            else row.append(element('p', failure.message || saveMessages.save_pending));
          }
          finally { if (current()) action.disabled = false; }
        };
        row.append(action); $('save-recovery-items').append(row);
      }
      if (data.nextCursor) {
        const more = element('button', 'Vis flere lagringer'); more.type = 'button';
        more.onclick = () => { if (current()) { more.remove(); discoverSaves(data.nextCursor, epoch); } };
        $('save-recovery-items').append(more);
      }
    } catch (failure) {
      if (!current()) return;
      if (failure.saveDisabled) {
        if (!cursor) { $('save-recovery-items').replaceChildren(); $('save-recovery').hidden = true; }
        return;
      }
      $('save-recovery').hidden = false;
      const notice = element('div', undefined, 'recovery-operation');
      notice.append(element('p', 'Tidligere lagringer kunne ikke hentes.'));
      const again = element('button', 'Prøv igjen'); again.type = 'button';
      again.onclick = () => { if (current()) { notice.remove(); discoverSaves(); } };
      notice.append(again);
      if (!cursor) $('save-recovery-items').replaceChildren();
      $('save-recovery-items').append(notice);
    }
  }
  async function encodeFile(selected) {
    if (selected.size > 10 * 1024 * 1024) throw new Error(messages.byte_limit);
    const bytes = new Uint8Array(await selected.arrayBuffer()); let binary = '';
    for (let offset = 0; offset < bytes.length; offset += 32768) binary += String.fromCharCode(...bytes.subarray(offset, offset + 32768));
    return btoa(binary);
  }
  async function saveDocument(asNew = false) {
    if (saveBusy || libraryBusy || !view || !bundle || !receipt) return;
    if (savedTarget?.generationId === bundle.generationId && !asNew) return;
    const submittedView = view, submittedRevision = revision, generation = bundle.generationId, epoch = saveEpoch;
    let firstDispatch = false;
    saveBusy = true; $('save-status').textContent = 'Lagrer privat …'; saveControls();
    try {
      if (!saveAttempt || asNew) {
        const navigation = practiceNavigation;
        const title = $('save-title').value;
        const effectiveTitle = title || bundle.source.title;
        if ([...effectiveTitle].length > 160) throw new Error('Tittelen kan ha høyst 160 tegn.');
        // Match Python Unicode whitespace and reject controls/lone surrogates;
        // astral characters count as one Unicode code point.
        if (!/[^\u0009-\u000d\u001c-\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]/u.test(effectiveTitle) ||
            [...effectiveTitle].some(char => char.codePointAt(0) < 32 || (char.codePointAt(0) >= 0xd800 && char.codePointAt(0) <= 0xdfff)))
          throw new Error('Tittelen må inneholde tekst uten kontrolltegn.');
        const frozen = {schemaVersion: '1.0', operationId: crypto.randomUUID(), documentId: asNew || !savedTarget ? crypto.randomUUID() : savedTarget.documentId,
          expectedRevision: asNew || !savedTarget ? null : savedTarget.revision, title: title || null,
          acceptance: accepted, bundle, receipt, positions: {flashcardId: bundle.flashcards[positions.flashcards]?.id || null, quizId: bundle.quiz[positions.quiz]?.id || null}};
        if (accepted.kind !== 'paste') {
          if (!file.files[0]) throw new Error(saveMessages.file_required);
          frozen.contentBase64 = await encodeFile(file.files[0]);
        }
        if (view !== submittedView || revision !== submittedRevision || epoch !== saveEpoch) return;
        saveAttempt = frozen; saveAttemptNavigation = navigation; saveUncertain = false;
      }
      firstDispatch = !saveUncertain; saveUncertain = true;
      const result = await documentRequest('save', saveAttempt, submittedView);
      if (!result || view !== submittedView || revision !== submittedRevision || bundle?.generationId !== generation || epoch !== saveEpoch) return;
      if (result.status !== 'ready') throw new Error(saveMessages.save_pending);
      savedTarget = {documentId: result.documentId, revision: result.revision, generationId: result.generationId};
      const initialPositions = saveAttempt.expectedRevision === null ? saveAttempt.positions :
        {flashcardId:bundle.flashcards[0]?.id || null,quizId:bundle.quiz[0]?.id || null};
      if (saveAttempt.expectedRevision !== null && saveAttemptNavigation === practiceNavigation) {
        positions = {flashcards:0,quiz:0}; revealed = {flashcards:new Set(),quiz:new Set()}; renderLearning();
      }
      startProgress(result.progressRevision || 1,initialPositions); queueProgress();
      saveAttempt = null; saveAttemptNavigation = null; $('save-status').textContent = 'Lagret privat. Øvingen beholdes ved denne lagringen.';
      draftDirty = false;
      for (const id of ['save-again', 'save-reload', 'save-new']) $(id).hidden = true;
      discoverSaves();
    } catch (failure) {
      if (view !== submittedView || epoch !== saveEpoch) return;
      $('save-status').textContent = failure.message || saveMessages.save_pending;
      if (failure.code === 'invalid_input' && firstDispatch) { saveAttempt = null; saveAttemptNavigation = null; saveUncertain = false; }
      $('save-again').hidden = !saveAttempt;
      $('save-reload').hidden = failure.code !== 'save_conflict' || !savedTarget;
      $('save-new').hidden = failure.code !== 'save_conflict';
    } finally {
      saveBusy = false; saveControls();
    }
  }
  $('save-document').onclick = () => saveDocument();
  $('save-again').onclick = () => saveDocument();
  $('save-new').onclick = () => saveDocument(true);
  $('save-reload').onclick = () => { if (savedTarget && !saveBusy) requestOpen(savedTarget.documentId, $('save-reload')); };
  function cancelReplacement() {
    const trigger = replacement?.trigger;
    replacement = null; $('document-replace').hidden = true;
    if (trigger?.isConnected) trigger.focus();
  }
  function leaveLibrary(focus = true) {
    ++libraryEpoch; libraryOpen = false; libraryBusy = false; libraryCursor = null;
    cancelReplacement(); $('library').hidden = true; $('workspace-active').hidden = false;
    $('library-items').replaceChildren(); $('library-status').textContent = '';
    saveControls();
    if (focus && view) $('document-library').focus();
  }
  async function listDocuments(cursor = null) {
    const submittedView = view, epoch = ++libraryEpoch;
    if (!submittedView || !libraryOpen) return;
    const current = () => libraryOpen && view === submittedView && epoch === libraryEpoch;
    libraryBusy = true; $('library').setAttribute('aria-busy', 'true');
    $('library-status').textContent = 'Henter dokumenter …';
    $('library-more').hidden = true; $('library-retry').hidden = true;
    try {
      const data = await documentRequest('library', {schemaVersion: '1.0', ...(cursor ? {cursor} : {})}, submittedView, current);
      if (!data || !current()) return;
      if (!Array.isArray(data.items) || data.items.length > 50) throw new Error(saveMessages.library_unavailable);
      if (!cursor) $('library-items').replaceChildren();
      for (const item of data.items) {
        const row = element('article', undefined, 'library-document');
        row.append(element('h3', item.title));
        const date = new Date(item.updatedAt);
        row.append(element('p', `Lagret: ${Number.isNaN(date.getTime()) ? 'ukjent dato' : date.toLocaleString('nb-NO')}`, 'source'));
        const progress = [];
        for (const [key, label] of [['flashcard', 'Kort'], ['quiz', 'Spørsmål']]) {
          const position = item.positions[key];
          progress.push(position ? `${label} ${position.ordinal} av ${position.total}` : `${label}: ingen`);
        }
        row.append(element('p', progress.join(' · '), 'source'));
        const actions = element('div', undefined, 'row actions'), open = element('button', 'Åpne');
        open.type = 'button'; open.onclick = () => requestOpen(item.documentId, open);
        actions.append(open);
        if (item.hasOriginalFile) {
          const download = element('button', 'Last ned originalfil'); download.type = 'button';
          download.onclick = () => downloadDocument(item.documentId, download); actions.append(download);
        }
        row.append(actions); $('library-items').append(row);
      }
      libraryCursor = data.nextCursor || null;
      $('library-more').hidden = !libraryCursor;
      $('library-status').textContent = $('library-items').children.length ? 'Dokumentene er klare.' : 'Du har ingen lagrede dokumenter. Velg Lagre etter at du har laget læringsmateriale. Tilbake beholder materialet ditt.';
    } catch (failure) {
      if (!current()) return;
      $('library-status').textContent = failure.message || saveMessages.library_unavailable;
      $('library-retry').hidden = false;
      // Retry the failed page, keeping earlier pages and the active draft.
      libraryCursor = cursor;
    } finally {
      if (current()) { libraryBusy = false; $('library').setAttribute('aria-busy', 'false'); }
    }
  }
  $('document-library').onclick = () => {
    if (!view || busy || saveBusy) return;
    libraryOpen = true; $('workspace-active').hidden = true; $('library').hidden = false;
    $('library-heading').focus(); listDocuments();
  };
  $('library-back').onclick = () => leaveLibrary();
  $('library-retry').onclick = () => { if (!libraryBusy) listDocuments(libraryCursor); };
  $('library-more').onclick = () => { if (!libraryBusy && libraryCursor) listDocuments(libraryCursor); };
  function requestOpen(documentId, trigger) {
    if (!view || libraryBusy || saveBusy || busy) return;
    if (draftDirty || saveAttempt || (bundle && savedTarget?.generationId !== bundle.generationId)) {
      replacement = {documentId, trigger}; $('document-replace').hidden = false; $('document-replace-heading').focus();
    } else openDocument(documentId);
  }
  $('document-replace-cancel').onclick = cancelReplacement;
  $('document-replace-confirm').onclick = () => {
    const candidate = replacement; replacement = null; $('document-replace').hidden = true;
    if (candidate) openDocument(candidate.documentId);
  };
  async function openDocument(documentId) {
    fenceProgressForOpen();
    const submittedView = view, epoch = ++libraryEpoch, submittedRevision = revision, submittedSequence = sequence, inLibrary = libraryOpen;
    const current = () => view === submittedView && epoch === libraryEpoch && revision === submittedRevision && sequence === submittedSequence && libraryOpen === inLibrary;
    const notice = inLibrary ? $('library-status') : $('save-status');
    libraryBusy = true; notice.textContent = 'Åpner lagret dokument …'; saveControls();
    try {
      const data = await documentRequest('reload', {schemaVersion: '1.0', documentId}, submittedView, current);
      if (!data || !current()) return;
      if (data.status !== 'ready' || data.documentId !== documentId || data.acceptance?.schemaVersion !== '1.0' ||
          !Number.isSafeInteger(data.progressRevision) || data.progressRevision < 1 ||
          !Number.isSafeInteger(data.revision) || data.revision < 1 || data.generationId !== data.bundle?.generationId ||
          !['paste', 'text-file', 'pdf'].includes(data.acceptance.kind) ||
          !Number.isInteger(data.acceptance.characterCount) || data.acceptance.characterCount < 1 || data.acceptance.characterCount > 30000 ||
          !Array.isArray(data.acceptance.source?.units) || !data.acceptance.source.units.length ||
          data.acceptance.source.units.some(unit => !['paragraph', 'page'].includes(unit.kind) || !Number.isInteger(unit.location) || unit.location < 1 || typeof unit.text !== 'string') ||
          !Array.isArray(data.acceptance.warnings) || data.acceptance.warnings.some(warning => typeof warning !== 'string') ||
          !Array.isArray(data.acceptance.unreadablePages) || !validateBundle(data.bundle, data.acceptance) ||
          !data.positions || typeof data.title !== 'string') throw new Error(saveMessages.library_unavailable);
      for (const [section, key] of [['flashcards', 'flashcardId'], ['quiz', 'quizId']]) {
        if (data.bundle[section].length ? !data.bundle[section].some(item => item.id === data.positions[key]) : data.positions[key] !== null)
          throw new Error(saveMessages.library_unavailable);
      }
      // Only a complete, current response may replace the active draft.
      invalidate(); bundle = data.bundle; receipt = null;
      kind.value = data.acceptance.kind; file.value = '';
      text.value = kind.value === 'paste' ? data.acceptance.source.units.map(unit => unit.text).join('\n\n') : '';
      language.value = bundle.settings.language; detail.value = bundle.settings.detail; subject.value = bundle.settings.subject;
      showMethod(); render({...data.acceptance, clientRevision: revision}); accepted = null;
      savedTarget = {documentId: data.documentId, revision: data.revision, generationId: data.generationId};
      $('save-title').value = data.title; saveAttempt = null; saveAttemptNavigation = null; draftDirty = false;
      startProgress(data.progressRevision,data.positions);
      for (const [section, key] of [['flashcards', 'flashcardId'], ['quiz', 'quizId']]) positions[section] = Math.max(0, bundle[section].findIndex(item => item.id === data.positions[key]));
      $('generation-warnings').replaceChildren(...bundle.warnings.map(warning => generated('p', warning, 'state-notice')));
      renderLearning(); $('results').hidden = false; leaveLibrary(false); materialOpen(false);
      $('save-status').textContent = 'Lagret versjon er hentet. Svarene er skjult.'; $('tab-summary').focus(); saveControls();
    } catch (failure) { if (current()) notice.textContent = failure.message || saveMessages.library_unavailable; }
    finally { if (epoch === libraryEpoch) libraryBusy = false; saveControls(); }
  }
  async function downloadDocument(documentId, button) {
    const submittedView = view, epoch = libraryEpoch, submittedRevision = revision;
    const current = () => libraryOpen && view === submittedView && epoch === libraryEpoch && revision === submittedRevision;
    const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 70000);
    button.disabled = true; $('library-status').textContent = 'Henter og kontrollerer originalfilen …';
    try {
      const response = await fetch('/api/v1/documents/file', {method: 'POST', credentials: 'same-origin', cache: 'no-store', signal: controller.signal,
        headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf, 'X-Session-View': submittedView}, body: JSON.stringify({schemaVersion: '1.0', documentId})});
      if (!current()) return;
      if (response.status === 401) { endAccess(); return; }
      if (!response.ok) throw new Error(saveMessages.file_unavailable);
      const blob = await response.blob();
      if (!current()) return;
      if (blob.size > 10 * 1024 * 1024 || !['text/plain', 'application/pdf'].includes(blob.type.split(';')[0])) throw new Error();
      const url = URL.createObjectURL(blob), link = document.createElement('a');
      link.href = url; link.download = blob.type.startsWith('application/pdf') ? 'original.pdf' : 'original.txt';
      document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
      $('library-status').textContent = 'Originalfilen er lastet ned. Nedlastede filer blir på enheten etter utlogging.';
    } catch { if (current()) $('library-status').textContent = saveMessages.file_unavailable; }
    finally { clearTimeout(timer); if (current()) button.disabled = false; }
  }
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
    generation_failed: 'Læringsmaterialet kunne ikke lages. Behold materialet og prøv igjen.',
    model_unavailable: 'Generering er ikke konfigurert. Materialet er beholdt.',
    budget_unavailable: 'Budsjettet er utilgjengelig eller brukt opp. Materialet er beholdt.',
    generation_timeout: 'Genereringen tok for lang tid. Prøv igjen eksplisitt.',
    generation_capacity: 'For mye materiale behandles nå. Vent litt og prøv igjen.',
    invalid_proof: 'Kildekontrollen er utløpt eller endret. Kontroller materialet på nytt.',
    stale_workspace: 'Materialet er endret. Kontroller det på nytt.',
    command_replayed: 'Denne handlingen er allerede registrert. Prøv igjen med en ny handling.',
    provider_input_limit: 'Materialet passer ikke innenfor genereringsgrensen. Ingen forespørsel er sendt.',
    workspace_capacity: 'For mange arbeidsområder er åpne. Logg ut og inn for en ny økt.',
  };
  function setBusy(value) {
    busy = value;
    $('check-source').disabled = value;
    $('generate').disabled = value;
    $('source-retry').disabled = value;
    $('results').setAttribute('aria-busy', String(value));
    form.setAttribute('aria-busy', String(value));
    saveControls();
    $('document-library').disabled = value;
  }
  function clearPreview() {
    preview.hidden = true;
    $('source-units').replaceChildren();
    $('source-coverage').replaceChildren();
    $('source-count').textContent = '';
  }
  function materialOpen(open) {
    $('material-body').hidden = !open;
    $('edit-material').hidden = !view || !bundle;
    $('edit-material').textContent = open ? 'Skjul materiale' : 'Vis/rediger';
    $('edit-material').setAttribute('aria-expanded', String(open));
  }
  function clearResults() {
    clearProgress();
    ++saveEpoch; saveAttempt = null; saveAttemptNavigation = null; saveUncertain = false; $('save-status').textContent = '';
    for (const id of ['save-again', 'save-reload', 'save-new']) $(id).hidden = true;
    bundle = null; receipt = null; activeTab = 'summary';
    positions = {flashcards: 0, quiz: 0}; revealed = {flashcards: new Set(), quiz: new Set()};
    $('results').hidden = true; $('content').replaceChildren(); $('generation-warnings').replaceChildren();
  }
  function command() {
    return {schemaVersion: '1.0', workspaceId, clientRevision: revision, commandSequence: ++commandSequence};
  }
  async function flushInvalidations() {
    if (invalidating) return invalidating;
    const run = async () => {
      while (pendingInvalidation && view && csrf) {
        const body = pendingInvalidation, submittedView = view;
        const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 5000);
        try {
          const response = await fetch('/api/v1/workspaces/invalidate', {method: 'POST', credentials: 'same-origin', cache: 'no-store', keepalive: true,
            signal: controller.signal, headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf, 'X-Session-View': submittedView}, body: JSON.stringify(body)});
          const data = await response.json();
          if (view !== submittedView) return;
          if (response.status === 401) { endAccess(); return; }
          if (!response.ok || data.commandSequence !== body.commandSequence || data.clientRevision !== body.clientRevision) throw new Error();
          if (pendingInvalidation === body) pendingInvalidation = null;
        } finally { clearTimeout(timer); }
      }
    };
    invalidating = run();
    try { await invalidating; } finally { invalidating = null; }
  }
  function invalidate() {
    ++libraryEpoch; libraryBusy = false; cancelReplacement(); draftDirty = true;
    ++revision; ++sequence;
    active?.abort(); active = null;
    accepted = null; clearResults(); materialOpen(true); clearPreview();
    if (view && csrf) {
      pendingInvalidation = command();
      queueMicrotask(() => flushInvalidations().catch(() => {
        if (view && pendingInvalidation) { status.textContent = 'Endringen kunne ikke bekreftes. Prøv igjen før generering.'; retry.hidden = false; }
      }));
    }
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
    savedTarget = null; $('save-title').value = '';
    invalidate();
    text.value = ''; file.value = ''; subject.value = '';
    kind.value = 'paste'; language.value = 'nb'; detail.value = 'short';
    showMethod();
    draftDirty = false;
  }
  function endAccess(message = ended) {
    if (view && csrf) {
      const body = {...command(), clientRevision: revision + 1};
      fetch('/api/v1/workspaces/invalidate', {method: 'POST', credentials: 'same-origin', cache: 'no-store', keepalive: true,
        headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf, 'X-Session-View': view}, body: JSON.stringify(body)}).catch(() => {});
    }
    ++authSequence;
    authActive?.abort(); authActive = null; observation = null;
    clearTimeout(lifetime);
    clearDraft();
    csrf = null; view = null; pendingInvalidation = null;
    ++discoveryEpoch;
    leaveLibrary(false); $('document-library').hidden = true;
    $('save-recovery-items').replaceChildren(); $('save-recovery').hidden = true;
    materialOpen(true); $('edit-material').hidden = true;
    controls.disabled = true; form.hidden = true; logout.hidden = true;
    signIn.hidden = false;
    retry.hidden = !logoutPending;
    retry.disabled = logoutBusy;
    status.textContent = message;
  }
  function fail(message) {
    materialOpen(true);
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
      if (changed) { clearDraft(); leaveLibrary(false); }
      const initial = view === null;
      csrf = data.csrfToken; view = data.sessionViewId;
      clearTimeout(lifetime); lifetime = setTimeout(() => endAccess(), seconds * 1000);
      controls.disabled = false; form.hidden = false; logout.hidden = false; signIn.hidden = true;
      $('document-library').hidden = false;
      if (initial || changed) status.textContent = changed ? 'Ny innlogging. Velg materialet på nytt.' : 'Du er logget inn. Velg materialet du vil kontrollere.';
      if (initial || changed) discoverSaves();
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
    status.textContent = 'Materialet er kontrollert. Forhåndsvisningen viser kildeteksten.';
    $('source-preview-heading').focus();
  }
  const names = {summary: 'Sammendrag', concepts: 'Begreper', flashcards: 'Flashcards', quiz: 'Quiz'};
  function element(tag, text, className) {
    const node = document.createElement(tag);
    node.lang = 'nb';
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  }
  function generated(tag, text, className) {
    const node = element(tag, text, className);
    node.lang = bundle.settings.language;
    return node;
  }
function references(items) {
  return element("p", "Kilde: " + items.map(reference => reference.label).join(", "), "reference");
}

function announceItem() {
  const index = positions[activeTab];
  status.replaceChildren(element('span', `${activeTab === "flashcards" ? "Kort" : "Spørsmål"} ${index + 1} av ${bundle[activeTab].length}. `),
    generated('span', bundle[activeTab][index].question));
}

function renderLearning() {
  for (const tab of document.querySelectorAll("[data-tab]")) {
    const selected = tab.dataset.tab === activeTab;
    tab.setAttribute("aria-selected", String(selected));
    tab.tabIndex = selected ? 0 : -1;
  }
  const content = $("content");
  content.setAttribute("aria-labelledby", `tab-${activeTab}`);
  content.replaceChildren(element("h2", names[activeTab]));
  const items = bundle[activeTab];
  const explanation = bundle.insufficiency[activeTab];
  if (explanation) content.append(generated('p', explanation, 'section-insufficiency'));
  if (!items.length) {
    if (!explanation) content.append(element("p", "Materialet gir ikke nok grunnlag for denne delen."));
    return;
  }
  if (activeTab === "summary" || activeTab === "concepts") {
    for (const item of items) {
      if (activeTab === "concepts") content.append(generated("h3", item.term));
      content.append(generated("p", item.text || item.explanation), references(item.references));
    }
    return;
  }
  const index = positions[activeTab];
  const item = items[index];
  const shown = revealed[activeTab].has(item.id);
  const reveal = element("button", activeTab === "flashcards" ? "Vis svar" : "Vis fasit");
  reveal.id = "reveal";
  reveal.type = "button";
  reveal.setAttribute("aria-expanded", String(shown));
  reveal.setAttribute("aria-controls", "answer");
  const answer = element("div", undefined, "answer");
  answer.id = "answer";
  answer.hidden = !shown;
  answer.append(element("strong", activeTab === "flashcards" ? "Svar" : "Fasit"), generated("p", item.answer), references(item.references));
  reveal.onclick = () => {
    revealed[activeTab].add(item.id);
    answer.hidden = false;
    reveal.setAttribute("aria-expanded", "true");
  };
  const navigation = element("div", undefined, "nav");
  for (const [id, label, delta] of [["previous", "Forrige", -1], ["next", "Neste", 1]]) {
    const button = element("button", label);
    button.type = "button";
    button.id = id;
    button.disabled = index + delta < 0 || index + delta >= items.length;
    button.onclick = () => {
      positions[activeTab] += delta;
      ++practiceNavigation;
      queueProgress();
      renderLearning();
      announceItem();
      ($(id).disabled ? $(id === "next" ? "previous" : "next") : $(id)).focus();
    };
    navigation.append(button);
  }
  content.append(element("p", `${activeTab === "flashcards" ? "Kort" : "Spørsmål"} ${index + 1} av ${items.length}`, "label"), generated("h3", item.question), reveal, answer, navigation);
}

function validateBundle(result, source = accepted) {
  if (!source?.source || !Array.isArray(source.source.units)) return false;
  if (!result || result.schemaVersion !== "1.0" || !result.generationId || result.source?.id !== source.source.id ||
      JSON.stringify(result.source) !== JSON.stringify(source.source) ||
      JSON.stringify(result.settings) !== JSON.stringify(source.settings) || !result.insufficiency || !Array.isArray(result.warnings) ||
      result.warnings.some(warning => typeof warning !== 'string')) return false;
  const units = new Map(source.source.units.map(unit => [unit.id, unit]));
  const ids = new Set();
  return Object.keys(names).every(section => Array.isArray(result[section]) &&
    (result[section].length > 0 || (typeof result.insufficiency[section] === "string" && result.insufficiency[section].trim().length > 0)) &&
    result[section].every(item => {
      if (!item.id || ids.has(item.id) || !Array.isArray(item.references) || !item.references.length) return false;
      ids.add(item.id);
      const fields = section === "summary" ? ["text"] : section === "concepts" ? ["term", "explanation"] : ["question", "answer"];
      return fields.every(field => typeof item[field] === "string" && item[field].length) && item.references.every(reference => {
        const unit = units.get(reference.sourceUnitId);
        return unit && reference.label === `${unit.kind === 'page' ? 'Side' : 'Avsnitt'} ${unit.location}`;
      });
    }));
}



  const tabs = Array.from(document.querySelectorAll('[data-tab]'));
  tabs.forEach((tab, index) => {
    tab.onclick = () => { if (bundle) { activeTab = tab.dataset.tab; renderLearning(); } };
    tab.onkeydown = event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      else if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = tabs.length - 1;
      else return;
      event.preventDefault(); tabs[next].click(); tabs[next].focus();
    };
  });
  async function submit(generateAfter = false) {
    if (busy || !view || !csrf || logoutPending) return;
    retryOperation = generateAfter ? 'generate' : 'extract';
    clearResults(); materialOpen(true); error.hidden = true; retry.hidden = true;
    const id = ++sequence, submittedView = view, submittedRevision = revision;
    const controller = new AbortController(); active = controller;
    const expire = () => {
      if (id !== sequence || view !== submittedView) return;
      invalidate();
      status.textContent = '';
      fail('Forespørselen tok for lang tid. Prøv igjen.');
    };
    let timer = setTimeout(expire, 20000);
    setBusy(true); status.textContent = 'Kontrollerer materialet …';
    try {
      await flushInvalidations();
      if (pendingInvalidation || id !== sequence || view !== submittedView) return;
      if (!accepted || !generateAfter) {
      accepted = null;
      clearPreview();
      const body = {...command(), kind: kind.value, settings: {language: language.value, detail: detail.value, subject: subject.value}};
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
      if (typeof data.sourceProof !== 'string' || !data.sourceProof) throw new Error(failed);
      accepted = data;
      }
      if (generateAfter) {
        clearTimeout(timer); timer = setTimeout(expire, 70000);
        status.textContent = 'Lager læringsmateriale …';
        const response = await fetch('/api/v1/generation', {method: 'POST', credentials: 'same-origin', cache: 'no-store', signal: controller.signal,
          headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf, 'X-Session-View': submittedView},
          body: JSON.stringify({...command(), acceptance: accepted})});
        const data = await response.json();
        if (id !== sequence || view !== submittedView) return;
        if (response.status === 401) { endAccess(); return; }
        if (!response.ok) {
          if (data.code === 'invalid_proof' || data.code === 'stale_workspace') accepted = null;
          throw new Error(Object.hasOwn(messages, data.code) ? messages[data.code] : failed);
        }
        if (!await confirmAccess(id) || id !== sequence || view !== submittedView) return;
        if (!validateBundle(data.bundle) || typeof data.receipt !== 'string' || !data.receipt ||
            data.clientRevision !== submittedRevision || data.commandSequence !== commandSequence) throw new Error(failed);
        bundle = data.bundle; receipt = data.receipt; renderLearning();
        $('generation-warnings').replaceChildren(...bundle.warnings.map((warning, index) => {
          const node = element('p', warning, 'state-notice');
          node.lang = index < accepted.warnings.length ? 'nb' : bundle.settings.language;
          return node;
        }));
        $('results').hidden = false; materialOpen(false); $('edit-material').focus();
        status.textContent = 'Alle fire læringsdeler er klare. Kontroller svarene mot kilden.';
      }
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
  form.addEventListener('submit', event => { event.preventDefault(); submit(true); });
  $('reset-source').addEventListener('click', () => { clearDraft(); status.textContent = 'Ny økt. Velg én kilde.'; text.focus(); });
  retry.addEventListener('click', () => logoutPending ? performLogout() : view ? submit(retryOperation === 'generate') : observe());
  $('check-source').addEventListener('click', () => submit(false));
  $('edit-material').addEventListener('click', () => {
    const open = $('material-body').hidden;
    materialOpen(open);
    if (open) kind.focus();
    else $('edit-material').focus();
  });
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
