# G79 — Gruppe123

Gruppeprosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng).

Repoet inneholder gruppens applikasjon og dokumentasjon av utvikling, testing og kvalitetssikring med KI.

## Kjør studiedemoen lokalt

Demoen er én FastAPI-applikasjon med vanlig HTML, CSS og JavaScript. Ingen API-nøkler, kontoer eller skytjenester er nødvendige. Installer [uv](https://docs.astral.sh/uv/getting-started/installation/) først. Kjør fra repoets rot:

```powershell
uv sync --locked
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Åpne [http://127.0.0.1:8000](http://127.0.0.1:8000). `uv` bruker Python 3.13.7 fra `.python-version` og kan installere denne hvis den mangler. Python-avhengighetene er låst i `uv.lock`. Første oppsett krever internettilgang; selve demoen kjører lokalt uten nettverkstjenester. Stopp serveren med Ctrl+C.

1. Les det faste eksempelet «Hukommelse og aktiv gjenhenting» og trykk **Lag læringsmateriale**.
2. Bytt mellom Sammendrag, Begreper, Flashcards og Quiz. Svar og kildehenvisning vises sammen når du trykker Vis svar / Vis fasit.
3. Bruk Forrige/Neste. Kort og quiz beholder hver sin posisjon og hvilke svar du har vist når du bytter fane.
4. Vis/rediger åpner materialet uten å endre fremdriften. Ny økt tømmer arbeidsflaten; velg eksempelet på nytt for å starte igjen.

## API og avgrensning

- `GET /health` returnerer `{"status":"ok","mode":"demo"}`.
- `GET /api/v1/demo/fixture` gir den synlige kilden og de faste innstillingene.
- `POST /api/v1/demo/generate` tar nøyaktig `{"schemaVersion":"1.0","fixtureId":"memory-basics-v1"}` og returnerer alle fire deler samlet. Hver del har stabile element- og kilde-ID-er; hver generering får en ny `generationId`.
- [API-dokumentasjon](http://127.0.0.1:8000/docs) viser kontraktene. Ukjent eksempel, versjon, egne kildefelt, innstillinger og andre ekstra felt gir forståelig HTTP 422 uten behandling eller lagring.

Studiedemoen bruker faste syntetiske eksempeldata på norsk med kort sammendrag. Ingen AI-modell behandler tekst. Egen tekst, tekstfil/PDF, språk-/detaljvalg, Lagre, Mine dokumenter og varig fremdrift er senere arbeid. Den aktive demotilstanden finnes bare i minnet på den åpne siden og forsvinner ved omlasting. Feil gir eksplisitt prøv-igjen; demoen bytter aldri til et falskt vellykket svar.

Demoen trenger ingen konfigurasjon og gjør ingen Supabase-kall. `/account` tilbyr norsk registrering og innlogging når Supabase er uttrykkelig aktivert og riktig konfigurert; ellers viser siden at innlogging er utilgjengelig. Bare eksplisitte offentlige UI-filer serveres; repositoryfiler og dokumentasjon er ikke statisk tilgjengelige. Den historiske UX-prototypen ligger uendret under `.docs/planning-artifacts/ux-designs/`.

## Konto og Supabase (Story 2.1)

Følg [oppsett og akseptanse for autentisering](.docs/implementation-artifacts/auth-setup.md): organisasjonen **Study Buddy** på **Free**, prosjektet **studybuddy-test** i **Paris (`eu-west-3`)**, med e-postbekreftelse og bare autoriserte teamtestere. Studenten godkjente Paris for det eksisterende testprosjektet 14.11.2026 som en endring fra opprinnelig Frankfurt-plan. Prosjekttilgang og aktiv e-postbekreftelse er kontrollert. Studenten rapporterer vellykket registrering/bekreftelse og separat privat innlogging. To administrative testkontoer bestod 20 HTTP-kontroller, 18 ekstra kontroller av øktlevetid/omstart/fornyelse og 24 kontroller i ekte nettlesere. Tidsgrenser var forkortet bare i en egen testserver; fornyelse brukte ekte Supabase-tokens med instrumentert lokal utløpsmetadata. Gjenværende hosted-tester av e-postbekreftelseslenker og malinspeksjon står åpne før endelig Story 2.1-akseptanse.

Serveren leser `AUTH_ENABLED=true`, `APP_ORIGIN`, `SUPABASE_URL` og `SUPABASE_PUBLISHABLE_KEY` fra prosessmiljøet. `.env.example` er kun dokumentasjon og lastes ikke automatisk. Bruk bare publishable/anon-nøkkel, aldri service_role/secret-nøkkel. Lokal HTTP krever også `AUTH_ALLOW_LOOPBACK_HTTP=true` og loopback-adresse. Andre oppsett krever HTTPS. Manglende/ugyldig konfigurasjon stenger autentiseringen uten å påvirke demoen.

Den lokale ignorerte `.env` kan lastes eksplisitt med `uv run --env-file .env uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1`. Åpne deretter `http://127.0.0.1:8000/account`. Dette aktiverer den konfigurerte innloggingen; vanlig demooppstart laster fortsatt ingen `.env`.

Kjør med **én prosess / én worker**. Tokens og PKCE-forsøk finnes bare i begrenset serverminne; nettleseren får tilfeldige HttpOnly-cookies. Bekreftelsen må åpnes innen ti minutter i nettleseren/profilen der registreringen startet. Økten utløper etter 30 minutter uten aktivitet, senest etter 12 timer, og ved serverrestart. Standarddemoen forblir tilgjengelig uten konto. Lokal utlogging er implementert i 2.3; private dokumenter, AI, lagring og utrulling inngår ikke her.

**Glemt passord (Story 2.2)** sender en generell kvittering og bruker en egen PKCE-lenke som må åpnes i samme nettleser/profil innen ti minutter. Lenken gir bare tilgang til skjemaet for nytt passord; den logger deg ikke inn. Et innsendt endringsforsøk bruker opp denne tilgangen før leverandørkallet. Etterpå må du logge inn på vanlig måte. Ved tidsavbrudd kan passordet allerede være endret: prøv innlogging eller be om en ny lenke. Innlogging og gjenoppretting deler maksimalt 1 000 lokale økter; registrering og gjenoppretting deler maksimalt 1 000 ventende forsøk og fire per nettleser. Reell e-post og passordendring krever uttrykkelig testerautorisasjon og er ikke utført av implementasjonstestene. Se [oppsettet](.docs/implementation-artifacts/auth-setup.md) for den ekstra redirect-oppføringen og åpne akseptansepunkter.

## Verifisering

API-/kontrakttester bruker den låste utviklingsgruppen som `uv sync --locked` installerer:

```powershell
uv run pytest
git diff --check
```

For nettlesertester trengs Node.js 22+ og npm. JavaScript-avhengighetene er låst i `package-lock.json`:

```powershell
npm ci
npx playwright install chromium
node tests/browser-demo.cjs
node tests/browser-auth.cjs
```

Testscriptet starter og stopper selv en lokal uvicorn-prosess på en ledig port. Hvis Playwright Chromium mangler, prøver det installert Microsoft Edge. Sett eventuelt `$env:DEMO_BROWSER_CHANNEL = "msedge"` for å velge Edge direkte. `DEMO_BASE_URL` kan peke mot en allerede kjørende lokal demo.

Kontotestene bruker en virkelig nettleser og en lokal server med en adapter som bare finnes i `tests/`. Python-testene kontrollerer også det låste Supabase-SDK-et mot syntetisk HTTP-transport. De dekker sikkerhetsmatrisen, uavhengige nettlesere og PKCE-forsøk, CSRF/Origin, provider-validering, refresh, kapasitets-/utløpsgrenser og trygg håndtering av feil/logging/lagring. Dette er offline verifisering; ekte e-post, bekreftelse og innlogging må gjennomføres separat før live akseptanse kan godkjennes.

Nettlesertestene dekker alle fire deler, kildevisning, separate posisjoner og svar, tastatur/fokus, antall genereringskall, duplikatvern, reset med et forsinket svar som ignorerer kansellering, feil ved første innlasting, semantisk ugyldige svar og eksplisitt retry. Både innlasting og generering har et tidsavbrudd på 15 sekunder som testes med reell ventetid. De kontrollerer horisontal overløp ved 320/390/480 piksler og 200 % layoutzoom og legger skjermbilder i den ignorerte mappen `test-results/`. Dette er automatiserte nettlesersjekker; en full manuell skjermleser- og WCAG-vurdering er ikke gjennomført.

## Lokalt PDF-eksperiment (Story 1.2)

PDF-proben krever Windows med tilgjengelig Job Object-isolasjon. Installer den valgfrie,
låste eksperimentgruppen og kjør fra repoets rot:

```powershell
uv sync --locked --group pdf-experiment
uv run --group pdf-experiment pytest
uv run --group pdf-experiment python scripts/pdf_probe.py --help
```

Lag en syntetisk PDF i den ignorerte testmappen og prøv CLI-en:

```powershell
New-Item -ItemType Directory -Force test-results | Out-Null
uv run --group pdf-experiment python tests/pdf_fixtures.py test-results/synthetic.pdf
uv run --group pdf-experiment python scripts/pdf_probe.py test-results/synthetic.pdf
```

JSON viser status, antall, opprinnelige sidenumre, dekningsvarsel og ressursmålinger.
Kildetekst, filnavn og parserfeil vises aldri. Avvisning gir exit-kode 1. Ved import
gir `scripts.pdf_probe.probe_pdf(path)` og `probe_stream(binary_stream)` også lesbare
kildeenheter i minnet; disse skal ikke logges. Enheten `pdf-page-3` viser fysisk side 3,
selv om side 2 er blank. Blanke sider og bildesider blir oppgitt som ulesbare.

Grensene er 40 fysiske sider, 30 000 Unicode-kodepunkter etter normalisering av
linjeskift, 10 MiB input, 10 sekunder arbeidertid og 512 MiB forpliktet arbeiderminne.
Overskridelser avvises uten avkorting eller delvis aksept. Manglende minneisolasjon
gir `isolation_unavailable`; Linux/macOS støttes foreløpig ikke. Eksperimenttestene
er valgfrie og hoppes over hvis gruppen ikke er installert; `uv run pytest` fortsetter
å kjøre demoens tester.

Se [målerapport og begrensninger](.docs/implementation-artifacts/pdf-experiment.md).
Bare syntetiske PDF-er er testet. Ingen OCR eller tolkning av bilder/tabeller inngår,
og krypterte dokumenter avvises. Dette er lokal gjennomførbarhetstesting;
applikasjonsintegrasjon tilhører Story 2.4. Målplattformen må verifiseres før hosting.
Story 1.1 venter fortsatt på studentens gjennomgang.

## Avslutning av tilgang (Story 2.3)

Story 2.3 adds browser-local **Logg ut** for normal and password-recovery access.
`POST /api/v1/auth/logout` requires the existing Origin/CSRF protection and an
empty JSON object. Local sessions, recovery grants and pending attempts end
atomically; the response deletes request-supplied session cookie generations before best-effort provider
revocation with explicit `local` scope. Provider failure never restores local
access or ends a different browser's session, including the same account.
Revocation admits at most 16 batches without a queue or retry, with one shared
ten-second cooperative deadline per batch and a separate worker limiter. User JWTs are sent directly to the
SDK logout endpoint; logout never refreshes tokens or uses a privileged key.

Status observation does not renew the 30-minute idle / 12-hour absolute maxima.
Normal and restricted status include bounded `expiresInSeconds`; the account
page clears its display at that deadline and checks status every 30 seconds
while visible, on focus and on page restoration. Restart requires fresh login.
Sibling tabs reconcile secret-free termination signals against server status;
old tab timers cannot end a newer login. Lifetime timing includes response delay,
and passive observations preserve forms/focus. Failed logout retains its intent
and retries the protected POST. Each opaque HttpOnly session cookie has its own
generation name, so delayed logout headers cannot delete a newer login cookie.
No private document endpoints or saved-data durability are introduced here;
durability belongs to Story 3.2. Review corrections pass 243 Python tests (one
unchanged optional PDF skip), 33 auth-browser scenarios and 11 demo scenarios.
A separate real-Supabase run passed 25 checks of logout, same-account isolation,
refresh and restart; restricted grants/deadline metadata and revoke failure were
instrumented locally. See [precise acceptance limits](.docs/implementation-artifacts/auth-setup.md#story-23-review-completion--2026-11-15).
Remaining email/recovery-link acceptance is kept separate.

## Medlemmer

- Fredrik Fladmark Hansen
