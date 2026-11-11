"use strict";

const $ = id => document.getElementById(id);
const names = {summary: "Sammendrag", concepts: "Begreper", flashcards: "Flashcards", quiz: "Quiz"};
let fixture = null;
let bundle = null;
let active = "summary";
let positions = {flashcards: 0, quiz: 0};
let revealed = {flashcards: new Set(), quiz: new Set()};
let sequence = 0;
let controller = null;
let busy = false;
let retryOperation = "fixture";

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function setMaterialOpen(open) {
  const focusInside = $("material-body").contains(document.activeElement);
  $("material-body").hidden = !open;
  $("edit-material").hidden = open;
  $("edit-material").setAttribute("aria-expanded", String(open));
  if (!open && focusInside) $("edit-material").focus();
}

function clearNotice() { $("state-notice").hidden = true; }

function setBusy(value) {
  busy = value;
  $("generate").disabled = value || !fixture || !$("method").value;
  $("retry").disabled = value;
  $("results").setAttribute("aria-busy", String(value));
}

function invalidatePending() {
  sequence += 1;
  controller?.abort();
  controller = null;
  setBusy(false);
}

function clearResults() {
  bundle = null;
  active = "summary";
  positions = {flashcards: 0, quiz: 0};
  revealed = {flashcards: new Set(), quiz: new Set()};
  $("results").hidden = true;
  $("content").replaceChildren();
}

function renderSource() {
  $("material").replaceChildren();
  if (!$("method").value || !fixture) {
    $("material").append(element("p", "Velg det faste eksempelet for å fortsette.", "source"));
    return;
  }
  for (const unit of fixture.source.units) {
    const region = element("div", undefined, "source-unit");
    region.append(element("span", `Avsnitt ${unit.location}`, "label"), element("p", unit.text));
    $("material").append(region);
  }
}

function showError(operation) {
  retryOperation = operation;
  clearResults();
  setMaterialOpen(true);
  $("state-heading").textContent = operation === "fixture" ? "Kunne ikke hente eksempelet" : "Kunne ikke lage læringsmaterialet";
  $("state-message").textContent = "Forbindelsen eller svaret feilet. Materialet og innstillingene er beholdt. Prøv igjen.";
  $("state-notice").hidden = false;
  $("status").textContent = "Forespørselen feilet. Prøv igjen når forbindelsen er klar.";
  $("retry").focus();
}

function hasKeys(value, keys) {
  return value !== null && typeof value === "object" && !Array.isArray(value) &&
    Object.keys(value).length === keys.length && keys.every(key => Object.hasOwn(value, key));
}

function validateFixture(result) {
  if (!hasKeys(result, ["schemaVersion", "fixtureId", "source", "settings"]) ||
      result.schemaVersion !== "1.0" || result.fixtureId !== "memory-basics-v1") return false;
  const {source, settings} = result;
  return hasKeys(source, ["schemaVersion", "id", "title", "units"]) &&
    source.schemaVersion === "1.0" && source.id === result.fixtureId &&
    typeof source.title === "string" && source.title.trim().length > 0 &&
    Array.isArray(source.units) && source.units.length === 3 && source.units.every((unit, index) =>
      hasKeys(unit, ["id", "kind", "location", "text"]) && unit.id === `memory-p${index + 1}` &&
      unit.kind === "paragraph" && unit.location === index + 1 &&
      typeof unit.text === "string" && unit.text.trim().length > 0) &&
    hasKeys(settings, ["language", "detail", "subject"]) &&
    settings.language === "nb" && settings.detail === "short" && settings.subject === "";
}

async function loadFixture() {
  invalidatePending();
  const requestSequence = sequence;
  controller = new AbortController();
  setBusy(true);
  $("status").textContent = "Henter fast eksempel …";
  try {
    const response = await fetch("/api/v1/demo/fixture", {
      signal: AbortSignal.any([controller.signal, AbortSignal.timeout(15000)]),
    });
    if (!response.ok) throw new Error("fixture_request_failed");
    const result = await response.json();
    if (requestSequence !== sequence) return;
    if (!validateFixture(result)) throw new Error("invalid_fixture");
    fixture = result;
    $("method").disabled = false;
    $("method").value = fixture.fixtureId;
    renderSource();
    clearNotice();
    $("status").textContent = "Det faste eksempelet er klart. Lag læringsmateriale for å starte.";
  } catch (error) {
    if (requestSequence === sequence) showError("fixture");
  } finally {
    if (requestSequence === sequence) { controller = null; setBusy(false); }
  }
}

function references(items) {
  return element("p", "Kilde: " + items.map(reference => reference.label).join(", "), "reference");
}

function announceItem() {
  const index = positions[active];
  $("status").textContent = `${active === "flashcards" ? "Kort" : "Spørsmål"} ${index + 1} av ${bundle[active].length}. ${bundle[active][index].question}`;
}

function render() {
  for (const tab of document.querySelectorAll("[data-tab]")) {
    const selected = tab.dataset.tab === active;
    tab.setAttribute("aria-selected", String(selected));
    tab.tabIndex = selected ? 0 : -1;
  }
  const content = $("content");
  content.setAttribute("aria-labelledby", `tab-${active}`);
  content.replaceChildren(element("h2", names[active]));
  const items = bundle[active];
  if (!items.length) {
    content.append(element("p", bundle.insufficiency[active] || "Materialet gir ikke nok grunnlag for denne delen."));
    return;
  }
  if (active === "summary" || active === "concepts") {
    for (const item of items) {
      if (active === "concepts") content.append(element("h3", item.term));
      content.append(element("p", item.text || item.explanation), references(item.references));
    }
    return;
  }
  const index = positions[active];
  const item = items[index];
  const shown = revealed[active].has(item.id);
  const reveal = element("button", active === "flashcards" ? "Vis svar" : "Vis fasit");
  reveal.id = "reveal";
  reveal.type = "button";
  reveal.setAttribute("aria-expanded", String(shown));
  reveal.setAttribute("aria-controls", "answer");
  const answer = element("div", undefined, "answer");
  answer.id = "answer";
  answer.hidden = !shown;
  answer.append(element("strong", active === "flashcards" ? "Svar" : "Fasit"), element("p", item.answer), references(item.references));
  reveal.onclick = () => {
    revealed[active].add(item.id);
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
      positions[active] += delta;
      render();
      announceItem();
      ($(id).disabled ? $(id === "next" ? "previous" : "next") : $(id)).focus();
    };
    navigation.append(button);
  }
  content.append(element("p", `${active === "flashcards" ? "Kort" : "Spørsmål"} ${index + 1} av ${items.length}`, "label"), element("h3", item.question), reveal, answer, navigation);
}

function validateBundle(result) {
  if (result.schemaVersion !== "1.0" || !result.generationId || result.source?.id !== fixture.source.id ||
      JSON.stringify(result.source) !== JSON.stringify(fixture.source) ||
      JSON.stringify(result.settings) !== JSON.stringify(fixture.settings) || !result.insufficiency || !Array.isArray(result.warnings)) return false;
  const units = new Map(fixture.source.units.map(unit => [unit.id, unit]));
  const ids = new Set();
  return Object.keys(names).every(section => Array.isArray(result[section]) &&
    (result[section].length > 0 || (typeof result.insufficiency[section] === "string" && result.insufficiency[section].trim().length > 0)) &&
    result[section].every(item => {
      if (!item.id || ids.has(item.id) || !Array.isArray(item.references) || !item.references.length) return false;
      ids.add(item.id);
      const fields = section === "summary" ? ["text"] : section === "concepts" ? ["term", "explanation"] : ["question", "answer"];
      return fields.every(field => typeof item[field] === "string" && item[field].length) && item.references.every(reference => {
        const unit = units.get(reference.sourceUnitId);
        return unit && reference.label === `Avsnitt ${unit.location}`;
      });
    }));
}

async function generate() {
  if (busy) return;
  if (!fixture || !$("method").value) {
    $("status").textContent = "Velg det faste eksempelet for å fortsette.";
    $("method").focus();
    return;
  }
  invalidatePending();
  const requestSequence = sequence;
  controller = new AbortController();
  clearNotice();
  clearResults();
  setMaterialOpen(true);
  setBusy(true);
  $("status").textContent = "Lager læringsmateriale …";
  try {
    const response = await fetch("/api/v1/demo/generate", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({schemaVersion: "1.0", fixtureId: $("method").value}),
      signal: AbortSignal.any([controller.signal, AbortSignal.timeout(15000)]),
    });
    if (!response.ok) throw new Error("generation_failed");
    const result = await response.json();
    if (requestSequence !== sequence) return;
    if (!validateBundle(result)) throw new Error("invalid_bundle");
    bundle = result;
    render();
    $("results").hidden = false;
    setMaterialOpen(false);
    $("edit-material").focus();
    $("status").textContent = "Alle fire læringsdeler er klare med faste eksempeldata.";
  } catch (error) {
    if (requestSequence === sequence) showError("generate");
  } finally {
    if (requestSequence === sequence) { controller = null; setBusy(false); }
  }
}

$("edit-material").onclick = () => { setMaterialOpen(true); $("method").focus(); };
$("method").onchange = () => {
  invalidatePending();
  clearResults();
  clearNotice();
  renderSource();
  setMaterialOpen(true);
  $("status").textContent = $("method").value ? "Det faste eksempelet er valgt. Lag læringsmateriale for å starte." : "Velg det faste eksempelet for å fortsette.";
};
$("generate").onclick = generate;
$("retry").onclick = () => retryOperation === "fixture" ? loadFixture() : generate();
$("reset").onclick = () => {
  invalidatePending();
  clearResults();
  clearNotice();
  $("method").value = "";
  // If reset happened during initial fixture loading, allow an explicit reload.
  $("method").disabled = !fixture;
  renderSource();
  setMaterialOpen(true);
  setBusy(false);
  $("status").textContent = "Ny økt. Velg det faste eksempelet for å fortsette.";
  if (!fixture) {
    retryOperation = "fixture";
    $("state-heading").textContent = "Eksempelet er ikke lastet";
    $("state-message").textContent = "Trykk Prøv igjen for å hente det faste eksempelet.";
    $("state-notice").hidden = false;
    $("retry").focus();
  } else $("method").focus();
};

const tabs = Array.from(document.querySelectorAll("[data-tab]"));
tabs.forEach((tab, index) => {
  tab.onclick = () => { active = tab.dataset.tab; render(); };
  tab.onkeydown = event => {
    let next;
    if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
    else if (event.key === "ArrowLeft") next = (index + tabs.length - 1) % tabs.length;
    else if (event.key === "Home") next = 0;
    else if (event.key === "End") next = tabs.length - 1;
    else return;
    event.preventDefault();
    tabs[next].click();
    tabs[next].focus();
  };
});

loadFixture();
