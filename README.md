# StudyBuddy – G79-hansen

Gruppeprosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng).

StudyBuddy gjør kursmateriale om til sammendrag, begreper, flashcards og quiz
med kildehenvisninger. Prosjektet bruker Python/FastAPI og HTML/CSS/JavaScript.

**Leveransestatus 21.11.2026:** Lokal kjørbarhet, eksisterende kjernefunksjoner og
Supabase-lagring prioriteres. Det valgfrie offentlige tillegget ble aktivert
20.11; mobiltilgang er brukerbekreftet. Manuell kryptert appbackup med isolert
databaseimport og filkontroll er dokumentert. Videre driftsautomatisering utsettes.
Utprøvingen gjelder ikke-sensitivt testmateriale. Mål: fungerende kjerne 1.12,
innleveringsklar applikasjon, README og rapport 8.12, fast innlevering 15.12.2026.
Se [avtalt avgrensning](.docs/implementation-artifacts/leveranseavgrensning-2026-11-19.md)
og [senere publisering og åpne kontroller](.docs/implementation-artifacts/hosting-acceptance.md).

## Start demoen uten nøkler

Demoen bruker **faste eksempeldata og ferdige svar**. Den viser studieflyten,
men genererer ikke nye svar fra egne dokumenter. Ingen API-nøkler, kontoer,
Supabase-oppsett, Node.js eller betalte tjenester trengs for å kjøre demoen.

Installer [uv](https://docs.astral.sh/uv/getting-started/installation/).
Hent repoet med Git, eller last ned og pakk ut en ZIP-kopi:

```powershell
git clone https://github.com/IBE160-2026/G79-hansen.git
cd G79-hansen
```

Åpne en terminal i prosjektmappen (der `pyproject.toml` ligger), og kjør:

```powershell
uv sync --locked
uv run --no-env-file uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Åpne [http://127.0.0.1:8000](http://127.0.0.1:8000). `uv` bruker Python 3.13.7 fra `.python-version` og kan installere denne hvis den mangler. Python-avhengighetene er låst i `uv.lock`. Første oppsett krever internettilgang; selve demoen kjører lokalt uten nettverkstjenester. Stopp serveren med Ctrl+C.

Kjør demoen fra en terminal uten eksporterte appvariabler. `--no-env-file`
hindrer innlesing av lokal `.env`; eventuelle miljøvariabler i terminalen har
fortsatt virkning. Live-innlogging/generering/lagring er separat konfigurasjon.

Hvis port 8000 allerede er i bruk, la den prosessen stå og velg en ledig port:

```powershell
uv run --no-env-file uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Åpne da `http://127.0.0.1:8001`. Oppstartsloggen viser hvilken adresse som brukes.

## Prøv studieflyten

1. Les det faste eksempelet «Hukommelse og aktiv gjenhenting» og trykk **Lag læringsmateriale**.
2. Bytt mellom Sammendrag, Begreper, Flashcards og Quiz. Svar og kildehenvisning vises sammen når du trykker Vis svar / Vis fasit.
3. Bruk Forrige/Neste. Kort og quiz beholder hver sin posisjon og hvilke svar du har vist når du bytter fane.
4. Vis/rediger åpner materialet uten å endre fremdriften. Ny økt tømmer arbeidsflaten; velg eksempelet på nytt for å starte igjen.

## Demo og live-funksjoner

| Modus | Tilgjengelig |
| --- | --- |
| Demo uten nøkler | Fast eksempel, fire læringsdeler, kildehenvisninger og øving. Tilstanden finnes i nettleserminnet og forsvinner ved omlasting. |
| Separat konfigurert live-modus | Egen tekst/tekstfil/PDF, modellgenerering, innlogging, Mine dokumenter, lagring, fremdrift og sletting. Krever Supabase og serverens modellnøkkel/budsjett. |

PDF-støtten gjelder tekstbaserte PDF-er og krever Windows-isolasjonen i live-modus;
OCR og tolkning av figurer/tabeller inngår ikke. Modellens svar må kontrolleres
mot kildehenvisningene. Full sluttakseptanse og videre driftsautomatisering gjenstår.

## Publisert skoleutprøving

[Åpne StudyBuddy](https://fredriklaptop.tail55f8dd.ts.net:10000/account).
Offentlig HTTPS ble aktivert 20.11.2026 kl. 17:07; studenten bekreftet mobiltilgang
kl. 17:11. Dette er daterte kontrollresultater. Appen kjører på prosjektets
Windows-PC og trenger at PC, app og internett er tilgjengelige. Etter PC-omstart
må appen startes manuelt. Den lokale demoen ovenfor er tilgjengelig som alternativ.

Selvregistrering med e-postbekreftelse er brukerbekreftet. Åpne bekreftelseslenken
i samme nettleser/profil som registreringen startet i, innen ti minutter.
Registrering og glemt passord deler grensen på to e-postreservasjoner totalt
og to per mottaker per rullerende time. En bekreftet vanlig testkonto er valgt
som reserve for sensor; innloggingsopplysninger overleveres privat ved innlevering.
Bruk bare ikke-sensitivt testmateriale som du har lov til å dele.

[Kort tilgangs- og testveiledning for sensor](.docs/implementation-artifacts/assessor-access.md)
samler innlogging, lokal demo ved driftsavbrudd og hovedflyten.

Toveis fremdrift mellom PC og mobil, uavhengig utlogging og ny innlogging med
bevart materiale/fremdrift etter appomstart er brukerbekreftet 21.11.
Resterende eierisolasjon mellom ulike kontoer og privat kontooverlevering gjenstår.
Se [publisering og akseptansegrenser](.docs/implementation-artifacts/hosting-acceptance.md)
og [dokumentert backup med gjenopprettingsgrenser](.docs/implementation-artifacts/backup-local-4-1.md).

## Leserute for sensor

Etter demoen ovenfor kan utviklingsprosessen følges i denne rekkefølgen:

1. **Fra idé til valgt omfang.** [Product brief](.docs/planning-artifacts/briefs/brief-G79-hansen-2026-09-26/brief.md)
   beskriver studiebehovet; [PRD](.docs/planning-artifacts/prds/prd-G79-hansen-2026-09-26/prd.md)
   gir brukerreise, prioriteringer og testbare krav. Studenten ba om å redusere
   omfanget. [Beslutningen19.11](.docs/implementation-artifacts/leveranseavgrensning-2026-11-19.md)
   prioriterte eksisterende kjerne og lokal kjørbarhet. Offentlig skoleutprøving
   ble senere godkjent og aktivert [20.11](.docs/implementation-artifacts/hosting-acceptance.md);
   videre driftsautomatisering er fortsatt utsatt. [PRD-oppfølgingen](.docs/implementation-artifacts/prd-feedback-followup-2026-11-19.md)
   viser hvordan faglærerens kritikk ble behandlet.

2. **Et konkret eksempel på kontroll og retting av KI-assistert kode.**
   [Brukskontrollen19.11, funn B1](.docs/implementation-artifacts/usability-check-2026-11-19.md)
   avdekket at status fortsatt beskrev flashcard2 etter bytte til Quiz1.
   Studenten ba «rett denne». Commit `2494ce9` oppdaterte `announceSection()` i
   [app.js](app/static/app.js); [nettlesertesten](tests/browser-demo.cjs)
   kontrollerer riktig status, fokus, bevarte posisjoner/svar og ingen ekstra
   generering ved fanebytte. De13 scenariene bestod19.11.

3. **Følg ett krav til kode og tester.** PRD-kravene om kildebaserte læringsdeler
   er konkretisert i [Story2.5](.docs/implementation-artifacts/spec-2-5-generate-all-learning-parts-from-the-source.md).
   Les deretter [genereringstjenesten](app/services/generation.py),
   [Python-testene](tests/test_generation.py) og
   [akseptansenotatet](.docs/implementation-artifacts/generation-acceptance.md).
   Notatet skiller syntetiske tester fra tidligere ekte modellkall og åpne grenser.

4. **Sammenhold automatiske og manuelle resultater.**
   [Live-tekstflyten19.11](.docs/implementation-artifacts/live-walkthrough-2026-11-19.md)
   dokumenterer studentens bekreftelser fra kildevisning til lagring, gjenåpning,
   fremdrift, sletting av nytt testmateriale og utlogging, med ett modellkall.
   [Narrator-kontrollen](.docs/implementation-artifacts/screen-reader-check-2026-11-19.md)
   gjelder den faste demoen. Disse avgrensede kontrollene dekker ikke full
   PDF-/feilflyt, tilgjengelighet eller fysisk filretensjon. Testkommandoene står
   under **Verifisering** i de tekniske detaljene nedenfor; resultatene er datert
   evidens, ikke en ny test av siste innleveringsversjon.

Videre dokumentasjon:

- [Leveransesjekkliste og gjenværende arbeid](.docs/implementation-artifacts/delivery-checklist-2026-11-19.md)
- [Leveransen mot sensorveiledningens sju kriterier](.docs/implementation-artifacts/sensor-guidance-check-2026-11-19.md)
- [Refleksjonsnotater som grunnlag for studentens rapport](.reflection-doc/refleksjonsnotater.md)
- [Krav og avgrensning](.docs/planning-artifacts/prds/prd-G79-hansen-2026-09-26/prd.md)

<details>
<summary>Teknisk dokumentasjon, valgfritt live-oppsett og tidligere kontrollresultater</summary>

Detaljene under trengs ikke for å starte den nøkkelfrie demoen. Live-oppsett
bruker egne nøkler og tjenester; ikke kopier gruppens hemmeligheter til Git.

## Windows hosted launcher (Story 4.1, acceptance in progress)

`scripts/start-hosted.ps1` runs the one-process application behind the separately
approved HTTPS proxy. Hosted startup and public activation were performed on
20 November; see the dated [acceptance record](.docs/implementation-artifacts/hosting-acceptance.md).
Startup and proxy activation are separate operator actions. The launcher never
activates Funnel, changes Tailscale/Supabase,
stops another process or initializes state. Existing local/demo commands above
remain available.

For hosted configuration, use the ignored `.env.hosted` separately from the
local HTTP `.env`, using [.env.hosted.example](.env.hosted.example). Set the exact
HTTPS origin, including the StudyBuddy proxy port `10000`, with no path
or trailing slash, and `AUTH_ALLOW_LOOPBACK_HTTP=false`. Keep real configuration
and credentials outside Git. Ambient process environment variables take precedence
over dotenv values, so check the effective environment deliberately. An optional
`-EnvFile 'literal path'` selects a different file; relative paths are resolved
from the repository root, regardless of the caller's directory.
The bounded UTF-8 dotenv reader accepts only the documented application variable
names and supports `NAME=value`, optional `export`, comments
and single/double quotes around literal values. It performs no interpolation or
escape expansion; use literal Windows paths. Malformed lines and duplicate names
reject the entire file before loading any value.

```powershell
.\scripts\start-hosted.ps1 -Check
# Operator startup only when port 8000 is available; leave a running app intact:
.\scripts\start-hosted.ps1
```

Check mode validates configuration and existing state without importing the app,
starting a server or making provider calls. It briefly binds loopback port 8000
without listening, then closes it; an occupied port rejects startup without
affecting its owner. Startup fixes `127.0.0.1:8000`, one worker, no reload, proxy
headers trusted only from `127.0.0.1`, no access log and five-second keepalive.
It stays in the foreground; Ctrl+C stops that process. A restart invalidates
in-memory sessions and requires fresh login. The availability probe cannot reserve
the port across startup; a later bind conflict also fails without stopping anyone.

Enabled generation needs an existing valid budget and a non-placeholder API key.
A valid blocked/exhausted budget stays unchanged and generation remains denied
by its existing runtime gate; login and saved material remain reachable.
Enabled Save needs the existing backend capability,
Paris (`eu-west-3`), matching project reference/URL and a legacy public anon S3
key. These are local structural checks, not live provider/key verification.
Preserve budget, blocked markers, capability, email journal and sidecars across
restarts; the launcher never creates, repairs, resets or unblocks them. State
paths must identify distinct regular files. A configured email journal must pass
read-only schema/clock inspection with no SQLite sidecars present; uncertain
state rejects preflight. Empty `AUTH_EMAIL_ADMISSION_PATH` explicitly disables
signup/recovery email and prints a safe notice; password login remains available.

The wrapper uses the installed uv environment with `--offline --no-sync --locked`;
it performs no setup or downloads. It suppresses native dotenv/exception stderr
and filters stdout to fixed safe messages. A nonzero exit reports a category
such as `configuration-invalid`, `state-invalid`, `email-state-invalid`,
`port-busy` or generic `launch-failed`, with no paths, values or raw exceptions.
Consult the local example and persistent-state preparation records to resolve
the category. See [uv run flags](https://docs.astral.sh/uv/reference/cli/#uv-run)
and [Uvicorn settings](https://uvicorn.dev/settings/).

## Local prepared-export backup component (Story 4.1)

`scripts/backup-studybuddy.ps1` packs explicitly prepared database, Storage and
local-state copies into authenticated encrypted bundles, rotates recognized files
at seven days, and extracts only into a new quarantine directory. The default
encrypted root is `C:\StudyBuddy-Backup`; prepare private ACLs before use. The
complete plaintext bundle is limited to 64 MiB and exists only in memory while
packing. Each fresh Fernet key is protected with Windows DPAPI CurrentUser,
normally binding recovery to the same account/profile/PC.

**Documented result, 20 November:** a manually triggered encrypted application
backup was created and refreshed at16:10. A real isolated PostgreSQL17.11 import
and checks of all five included Storage files passed. The refreshed copy includes
four Auth users and the email journal. The student selected manual triggering;
daily export is not installed. The seven-day archive expiry task was installed
on19 November and runs when its Windows operator/session is available.

Database authentication with an explicit project CA was verified on19 November.
The ordinary connection checker still uses system roots; repeatable explicit CA
configuration remains open. Do not repeat credential capture or replace existing
state as setup. See [the source contract, dated evidence and recovery limits](.docs/implementation-artifacts/backup-local-4-1.md).

The shipped component packages **prepared exports**; the one-off live export and
restore helpers are not a shipped routine exporter. Full Supabase platform/role
recovery, restored live Auth/Storage access, post-snapshot deletion reconciliation
and monotonic budget/journal reconciliation remain open. Never replace current
state with quarantined older copies. Expiry cannot run while the PC is off;
same-PC risk is accepted through submission on15 December2026.

## API og avgrensning for demoen

- `GET /health` returnerer `{"status":"ok","mode":"demo"}`.
- `GET /api/v1/demo/fixture` gir den synlige kilden og de faste innstillingene.
- `POST /api/v1/demo/generate` tar nøyaktig `{"schemaVersion":"1.0","fixtureId":"memory-basics-v1"}` og returnerer alle fire deler samlet. Hver del har stabile element- og kilde-ID-er; hver generering får en ny `generationId`.
- [API-dokumentasjon](http://127.0.0.1:8000/docs) viser kontraktene. Ukjent eksempel, versjon, egne kildefelt, innstillinger og andre ekstra felt gir forståelig HTTP 422 uten behandling eller lagring.

Studiedemoen bruker faste syntetiske eksempeldata på norsk med kort sammendrag. Ingen AI-modell behandler demoteksten. Egen tekst, tekstfil/PDF og språk-/detaljvalg er tilgjengelig i det private arbeidsområdet `/workspace`, med separat aktivert modellkonfigurasjon. Eksplisitt privat Lagre er implementert med separat konfigurasjon og er deaktivert som standard; Mine dokumenter og løpende fremdriftssynkronisering er implementert i live-modus. Den aktive demotilstanden finnes bare i minnet på den åpne siden og forsvinner ved omlasting. Feil gir eksplisitt prøv-igjen; demoen bytter aldri til et falskt vellykket svar.

Demoen trenger ingen konfigurasjon og gjør ingen Supabase-kall. `/account` tilbyr norsk registrering og innlogging når Supabase er uttrykkelig aktivert og riktig konfigurert; ellers viser siden at innlogging er utilgjengelig. Bare eksplisitte offentlige UI-filer serveres; repositoryfiler og dokumentasjon er ikke statisk tilgjengelige. Den historiske UX-prototypen ligger uendret under `.docs/planning-artifacts/ux-designs/`.

## Konto og Supabase (Story 2.1)

Følg [oppsett og akseptanse for autentisering](.docs/implementation-artifacts/auth-setup.md):
organisasjonen **Study Buddy** på **Free**, prosjektet **studybuddy-test** i
**Paris (`eu-west-3`)**, med e-postbekreftelse. Studenten godkjente Paris
14.11.2026 som en endring fra opprinnelig Frankfurt-plan. De første kontrollene
brukte autoriserte teamtestere. To testkontoer bestod 20 HTTP-kontroller,
18 ekstra kontroller av øktlevetid/omstart/fornyelse og 24 nettleserkontroller.
Tidsgrenser var forkortet bare i en egen testserver; fornyelse brukte ekte
Supabase-tokens med instrumentert lokal utløpsmetadata. Senere ble
selvregistrering/e-postbekreftelse via HTTPS og vanlig passordinnlogging
brukerbekreftet 20.11; se [hostingplanen](.docs/implementation-artifacts/hosting-plan-4-1.md).
Negative bekreftelseslenketester og malinspeksjon står fortsatt åpne før
endelig Story 2.1-akseptanse.

Serveren leser `AUTH_ENABLED=true`, `APP_ORIGIN`, `SUPABASE_URL` og `SUPABASE_PUBLISHABLE_KEY` fra prosessmiljøet. `.env.example` er kun dokumentasjon og lastes ikke automatisk. Bruk bare publishable/anon-nøkkel, aldri service_role/secret-nøkkel. Lokal HTTP krever også `AUTH_ALLOW_LOOPBACK_HTTP=true` og loopback-adresse. Andre oppsett krever HTTPS. Manglende/ugyldig konfigurasjon stenger autentiseringen uten å påvirke demoen.

Den lokale ignorerte `.env` kan lastes eksplisitt med `uv run --env-file .env uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1`. Åpne deretter `http://127.0.0.1:8000/account`. Dette aktiverer den konfigurerte innloggingen; vanlig demooppstart laster fortsatt ingen `.env`.

Kjør med **én prosess / én worker**. Tokens og PKCE-forsøk finnes bare i begrenset serverminne; nettleseren får tilfeldige HttpOnly-cookies. Bekreftelsen må åpnes innen ti minutter i nettleseren/profilen der registreringen startet. Økten utløper etter 30 minutter uten aktivitet, senest etter 12 timer, og ved serverrestart. Standarddemoen forblir tilgjengelig uten konto. Lokal utlogging, midlertidig kildekontroll og KI-generering av alle fire læringsdeler er implementert; eksplisitt privat lagring er implementert i Story 3.1 med separat aktivering. Den avgrensede offentlige skoleutprøvingen ble separat godkjent og aktivert 20.11.

**Glemt passord (Story 2.2)** sender en generell kvittering og bruker en egen PKCE-lenke som må åpnes i samme nettleser/profil innen ti minutter. Lenken gir bare tilgang til skjemaet for nytt passord; den logger deg ikke inn. Et innsendt endringsforsøk bruker opp denne tilgangen før leverandørkallet. Etterpå må du logge inn på vanlig måte. Ved tidsavbrudd kan passordet allerede være endret: prøv innlogging eller be om en ny lenke. Innlogging og gjenoppretting deler maksimalt 1 000 lokale økter; registrering og gjenoppretting deler maksimalt 1 000 ventende forsøk og fire per nettleser. Reell e-post og passordendring krever uttrykkelig testerautorisasjon og er ikke utført av implementasjonstestene. Se [oppsettet](.docs/implementation-artifacts/auth-setup.md) for den ekstra redirect-oppføringen og åpne akseptansepunkter.

Email dispatch requires `AUTH_EMAIL_ADMISSION_PATH`, a dedicated server-only
SQLite journal. It was configured and enabled in the hosted app on20 November;
signup mail and HTTPS confirmation were user-confirmed that day. Password login
and the fixed demo remain available without email dispatch. For a **new independent
installation only**, initialize new state offline, then configure the same path:

```powershell
uv run --locked python -m scripts.email_admission init .auth-email-admission.sqlite3
```

Initialization refuses existing state or SQLite sidecars. The ignored
`.auth-email-admission*` files must stay private; for another path, ignore its
journal and `-journal`, `-wal`, `-shm` sidecars too. HTTP requests never initialize,
upgrade or reset state. Signup and password recovery share fixed rolling-hour limits of
two reservations globally and two per stripped, casefolded recipient across all
browsers. The journal stores only a locally generated secret, keyed recipient
digests, timestamps and schema metadata. Atomic durable reservations precede
provider calls; failed or uncertain calls retain their reservation across restart
until the rolling window expires. Preserve state and sidecars; do not delete,
replace or reinitialize them to restore capacity.

Existing version1 journals require an explicit offline upgrade to version2.
Stop only the checked StudyBuddy worker, retain the existing journal and sidecars,
and run against its configured path (never use `init` on an existing installation):

```powershell
uv run --locked python -m scripts.email_admission upgrade .auth-email-admission.sqlite3
```

The upgrade uses an exclusive transaction and preserves every existing digest,
reservation timestamp, journal secret and last-seen clock, including expired rows.
Existing reservations still count; this command grants no refund. A valid version2
journal is reported as already current without changing it. Invalid, locked,
unwritable or sidecar-bearing state fails closed and must be investigated without
deleting or repairing history. Verify with hosted `-Check`, then restart through
the hosted launcher. An older application rejects version2: recover forward with
compatible code; never restore an older journal to regain capacity. Same-address
provider cooldowns remain separate from these local limits.

Missing, invalid, locked or unwritable state and clock rollback refuse dispatch
with a generic error. These app-local limits do not count provider sends made
by other tools or projects. The rolling window uses reservation time; actual
provider dispatch may occur later. The [hosting plan](.docs/implementation-artifacts/hosting-plan-4-1.md)
records the actual email setup and chosen assessor reserve account; private
credential handover and remaining negative-link acceptance are still open.
Focused offline checks: `uv run --locked pytest -q tests/test_email_admission.py tests/test_auth.py tests/test_hosted_startup.py`.

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
Story 2.3 introduced no document persistence; explicit Save is added in Story 3.1 below.
Review corrections passed 243 Python tests (one
unchanged optional PDF skip), 33 auth-browser scenarios and 11 demo scenarios.
A separate real-Supabase run passed 25 checks of logout, same-account isolation,
refresh and restart; restricted grants/deadline metadata and revoke failure were
instrumented locally. See [precise acceptance limits](.docs/implementation-artifacts/auth-setup.md#story-23-review-completion--2026-11-15).
Remaining email/recovery-link acceptance is kept separate.

## Eget materiale (Story 2.4)

Åpne `/workspace` etter vanlig innlogging for å kontrollere innlimt tekst,
UTF-8-tekstfil eller tekstbasert PDF. Forhåndsvisningen viser avsnitt eller
opprinnelige fysiske sider og forklarer delvis PDF-dekning. Grensene er
30 000 Unicode-kodepunkter, 40 PDF-sider og 10 MiB per fil; overskridelse
avviser hele kilden. PDF krever den kontrollerte Windows-isolasjonen.

Materialet behandles midlertidig. Endret kilde/innstilling forkaster gammel
forhåndsvisning, og utlogging/utløp/ny innlogging tømmer privat innhold.
KI-generering er tilgjengelig som beskrevet nedenfor; eksplisitt privat lagring krever oppsettet for Story 3.1. Den faste demoen på `/` beholdes.
Kjør `node tests/browser-sources.cjs` for kildeflyten, i tillegg til de øvrige
testene. Se [API, testkommandoer og akseptansegrenser](.docs/implementation-artifacts/source-acceptance.md).

## Medlemmer

- Fredrik Fladmark Hansen

## Private learning generation (Story 2.5)

`/workspace` now has **Lag læringsmateriale**.
The action checks the current source when necessary, then requests summary,
concepts, flashcards and quiz together. The optional source preview remains
available. Unsaved results and selected files exist only in page memory.
Explicit private Save is implemented in Story 3.1 below and disabled by default
in a new installation; My documents, reopening and progress synchronization are
implemented in Stories 3.2/3.3 below. Editing material/settings, reset,
session changes and page exit clear the private result. Technical errors retain
the draft/file/settings and offer explicit retry. Practice navigation and reveal
controls do not call the model.

The fixed demo remains credential-free. Private generation is disabled by
default and has no demo fallback. Enable only after the approved model/data/cost
setup by putting `MODEL_ENABLED=true`, `OPENAI_API_KEY` and `MODEL_BUDGET_PATH`
in the server process environment (see `.env.example`). The application does not
automatically read `.env`. Use only nonsensitive material you are permitted to
send to OpenAI globally. Requests use `gpt-6-luna`, Standard, reasoning `none`,
`store:false` and explicit cache mode without breakpoints. No training opt-in
is enabled; ordinary provider abuse retention is normally up to 30 days, with
exceptions. This is separate from the application's transient storage boundary.

Initialize the content-free local USD 5 lifetime budget ledger **once**, after
approval; never reset or delete an existing ledger to restore allowance:

```powershell
uv run python -m scripts.model_budget init .model-budget.json
uv run python -m scripts.model_budget status .model-budget.json
```

Each dispatch durably reserves USD 0.05 before any network write. Missing,
corrupt, locked, blocked or exhausted ledgers refuse dispatch. Uncertain calls
keep their reservation across restart. This ledger covers this app only, not
other clients using the credential, provider prices, tax or purchases. No
purchase, account, funding or hosted setting is automated.

Unexpected reported usage durably creates a content-free `.blocked` sidecar,
even when another instance owns the ledger lock. Preserve that marker and the
ledger; neither may be removed or reset to restore allowance. All four approved
automated live smoke calls have been executed; their allowance is exhausted.
See the acceptance record for the unchanged historical measurements. Review
corrections use synthetic transports only.

Generation admits one request per session and two globally without a queue or
retry. Its 60-second server deadline includes body/preflight/validation;
extraction is a separately bounded phase. The browser waits at most 70 seconds
after extraction. Provider request/response envelopes are capped at 256 KiB,
output at 8,000 tokens and the private generation protocol at 2 MiB. Unsolicited
compressed provider responses are rejected before decompression. A cancelled
browser wait cannot guarantee the provider stopped billing.

Signed source proofs bind the exact accepted source/settings/coverage/file
hash. Signed generation receipts bind canonical source/settings/bundle hashes
to the current owner, a non-authorizing session binding and ordered workspace
command. Source text, generated content, receipts, credentials and source hashes
are never persisted in the budget ledger. Workspace authority stores metadata
only (at most eight workspaces per session), uses the auth-then-workspace mutex
order and is removed when access ends. Signature validity alone cannot authorize
a superseded result. Story 3.1 coordinates admission with invalidation using an
owned asynchronous workspace gate; no authentication/global lock spans network IO.

Run `uv run --group pdf-experiment pytest`, `node tests/browser-sources.cjs`,
`node tests/browser-auth.cjs`, `node tests/browser-demo.cjs` and `git diff --check`.
The opt-in `scripts.generation_smoke` runner makes at most four automated
synthetic calls over the same ledger's lifetime, including failed calls; it
never initializes the ledger, retries or prints source/output/credentials.
See [the generation acceptance record](.docs/implementation-artifacts/generation-acceptance.md)
for executed checks and the separate Story 2.6 quality/hosting gates.

## Controlled content evaluation (Story 2.6)

The [registered corpus and semantic rubric](.docs/implementation-artifacts/content-evaluation.md)
define three original synthetic documents and two negative cases. The runner
accepts only cases A–E. Default preflight uses production extraction and request
validation offline; it never reads model configuration or budget/grant files:

```powershell
uv run --group pdf-experiment python -m scripts.content_evaluation
uv run --group pdf-experiment pytest tests/test_content_evaluation.py tests/test_generation.py -q
uv run --group pdf-experiment python -m scripts.content_evaluation --register
```

Registration atomically publishes a complete fingerprinted directory beneath
`.docs/implementation-artifacts/content-evaluation-evidence/`, containing fixed
source units, settings, fifteen concept/location expectations, code/prompt hashes,
exact visible PDF lines, the immutable acceptance-rubric hash and a readable
ordinary-font `source-c.pdf`. Mutable status/results are excluded from that rubric
hash. Registration stages both files in an owned temporary directory, flushes
them, and publishes without replacing an existing registration. A failed staging
attempt cleans only its own temporary directory and can be retried offline.
Render and inspect all five physical pages and compare those lines before inference; pages
2 and 4 must be blank. Commit/fingerprint this registration before any live case.
A changed implementation requires a new matching registration, while the frozen
corpus fingerprint remains separately traceable.

After the recorded approval, initialize the separate eight-attempt grant **once**.
This exclusively creates the fixed ignored `.model-budget-evaluation-2-6.json`;
it cannot reset an existing file. The existing global USD 5 ledger must already
exist. A live run additionally requires the same process model configuration as
generation; use the existing approved configuration, with no credentials in
command arguments. Execute one explicitly selected case per invocation:

```powershell
uv run python -m scripts.content_evaluation --initialize-grant
uv run --env-file .env --group pdf-experiment python -m scripts.content_evaluation --live --case A
uv run --env-file .env --group pdf-experiment python -m scripts.content_evaluation --live --case A --phase recheck
```

The final command is only for an approved, needed recheck. There are eight total
attempts across restarts, including failed or uncertain attempts. Each consumes
the evaluation grant durably before reserving USD 0.05 in the existing global
ledger. No reservation is refunded, no retry is automatic, and a concurrent
runner fails immediately. An existing destination evidence file is rejected
under the grant lock before either allowance is consumed or a provider attempt
starts. The original four-smoke counter stays unchanged and
cannot be reused. Each attempt writes a new synthetic evidence file; numeric
errors omit provider messages and raw envelopes. JSON evidence is fully flushed
to an owned temporary file, then atomically published without replacement, using
Windows write-through or POSIX directory synchronization. Registration/PDF reads
are bounded before allocation. Error codes are 1 configuration,
2 grant/lock, 3 global reservation, 4 provider/usage, 5 output structure/reference
identity, 6 evidence persistence, 7 registration, 8 case selection, 9 deadline,
10 internal/other safe stop, and 11 explicit cancellation. Attempt evidence records
`globalReservationCompleted` and `providerAttemptStarted` booleans. These describe
local completion/start phases only; neither proves upstream receipt or billing.
For deadline code 9 they distinguish a stop before the provider attempt from a
deadline during that attempt. Failed/uncertain dispatch and cancellation retain
all consumed allowances. The five historical outputs/assessments keep their
original metadata and registration; these added fields apply to future attempts.

Structural validation establishes reference identity only. Audit every returned
item for factual support and substantive reference correctness; score each
registered concept semantically, retaining unsupported claims, wrong references
and omissions separately. Preserve initial failures and link fixes, regressions
and rechecks. Offline integrity tests validate historical observation hashes,
complete item/reference enumeration, exact excerpts and coverage identity links;
they establish traceability and do not judge semantic correctness.
A shared instruction change needs final evidence for all five
cases. Exhausted allowance or unresolved failures leave acceptance incomplete.
Passing this controlled corpus establishes its observed synthetic results only;
arbitrary course documents, complex PDF reading order/OCR, deployed isolation,
screen-reader assessment and earlier real-email gates remain separate.

## Explicit private Save (Story 3.1)

Storage verification update, 17 November 2026: authenticated REST downloads can
cache a successful internal read by user JWT and bypass later backend/lifecycle
checks. Original-file verification now uses uncached S3 session-token reads with
the same user JWT, owner RLS and backend capability. It requires
`SUPABASE_S3_REGION`, `SUPABASE_S3_KEY_ID` (project reference) and
`SUPABASE_S3_ANON_KEY` (legacy public anon key; never a privileged S3/service key).
The new read-policy migration must be approved and applied before activation.
See the current status at the top of the Save acceptance record.
The existing test setup was approved and activated on 17 November: 32 synthetic
hosted checks and 30 normal-server checks passed without real model calls. The
local app is available at `http://127.0.0.1:8000/workspace`; fresh login is required.

After generating material, **Lagre** saves the validated source, settings, four
learning sections, optional original file and the independent current flashcard
and quiz positions. The optional title accepts 160 Unicode code points. Save
makes no model call. Navigating practice does not save again; progress sync is
Story 3.3. Edits keep the saved document as the explicit replacement target;
**Ny økt** detaches that target without deleting data. Revision conflicts offer
**Hent lagret versjon** or **Lagre som nytt** and preserve the unsaved draft.

Save is disabled by default. It requires the migration, private bucket policies,
an administrator-installed verifier hash, `SAVE_ENABLED=true`, and the ignored
server capability file named by `SAVE_BACKEND_KEY_PATH`. The application never
loads `.env` automatically and uses user JWTs, never a service key, for ordinary
document/Storage work. The migration and exact hosted approval boundary are in
[the Save acceptance record](.docs/implementation-artifacts/save-acceptance.md).
No hosted migration/configuration is authorized by local implementation approval.

After approval, `uv run python -m scripts.save_backend_key` exclusively creates
the ignored `.save-backend-key` file with restricted permissions. It refuses an
existing/unignored destination and prints only `keyId` and the SHA-256 verifier.
Install only that verifier in `studybuddy.backend_verifiers` as administration.
Never put the raw capability in SQL, arguments, browser code or logs. Key rotation
changes current backend authorization without changing admitted operation IDs.

An immutable operation is durably admitted before any upload. Exact retries
return the recorded outcome before checking an old receipt/revision. A pending
panel after fresh login identifies pending same-owner operations by title and
admission/expiry times. Exact recovery lasts seven days using the stored snapshot
and matching original bytes when needed. Confirmed completed outcomes remain
discoverable for seven days after completion, including a lost successful reply.
At expiry, upload/commit is rejected exactly. A minute-by-minute administrator
database job erases overdue staging/title independently of owner login; physical
staging purge follows the next successful bounded maintenance batch. Scheduler
failure or backlog delays erasure and fails retention acceptance. Operators must
check `cron.job`, `cron.job_run_details` and
`studybuddy.expiry_maintenance_health`; see the acceptance record for health SQL.
`uv run python -m scripts.save_cleanup` asks for a fresh user JWT using a hidden
prompt, validates that identity, expires owner staging and retries registered
cleanup; it does not use or create accounts. Registered uncertain writes stay
discoverable. Object-free terminal operations report `cleanup_complete` and leave
content-free tombstones; registered file cleanup remains pending without physical
provider quiescence evidence. Ready Save and cleanup status are separate. Database
erasure does not establish removal from backups or physical blob storage; those
remain separate real-file acceptance gates.

Run `uv run pytest`, `node tests/browser-documents.cjs` and the three existing
browser suites. Injected-port tests exercise application lifecycle/failures;
`supabase/tests/save_protocol.test.sql` and the isolated local provider runner
exercise actual transactions/RLS/Storage. Their exact executed evidence and
remaining hosted/real-file/provider retention gates belong in the acceptance record.

**Mine dokumenter** lists only your ready saved documents, fifty per page, with
title, save date and the independently saved card/quiz positions. Listing and
returning preserve the active draft. Opening asks before replacing unsaved work,
restores the exact saved source/settings/four sections with answers hidden, and
makes no model call or generation receipt. Editing then uses normal extraction.
**Last ned originalfil** verifies the saved original's size and SHA-256 through
an authenticated, uncached user-JWT S3 read and returns an attachment. The browser
receives neither object keys nor signed URLs. Downloaded files remain on the
device after logout. New session clears only the workspace.

Mine dokumenter is active in the existing test setup after local and hosted
verification on 17 November 2026. Log in again after the local server restart.
Run `uv run pytest tests/test_library.py tests/test_documents.py
tests/test_save_acceptance_tools.py -q`, `node tests/browser-library.cjs`, and
the existing Save browser suite. Real local checks use
`SAVE_TEST_WSL_DISTRO=SUREUbuntu` with
`uv run python tests/library_provider_acceptance.py` and
`supabase/tests/library_protocol.test.sql`. See
[library acceptance](.docs/implementation-artifacts/library-acceptance.md) for
executed results and remaining release/retention limits.

Saved practice navigation now synchronizes the independent card/quiz positions.
Only acknowledged progress is guaranteed after leaving. A stale view reports
**Fremdriften er endret på en annen enhet** and requires **Hent siste fremdrift**;
fetching hides answers. An uncertain write retries its exact mutation once, then
offers explicit retry/refetch. Editing or generating new material requires an
explicit content Save before progress sync resumes. Opening a newer saved
generation requires reopening the document. No inference occurs during sync.

Focused checks: `uv run --locked pytest tests/test_progress.py -q`,
`node tests/browser-progress.cjs`, `supabase/tests/progress_protocol.test.sql`, and
the isolated local `tests/progress_provider_acceptance.py` runner with
`SAVE_TEST_WSL_DISTRO=SUREUbuntu`. See
[progress acceptance](.docs/implementation-artifacts/progress-acceptance.md)
for exact executed results and remaining integration limits.

Story 3.4 adds **Slett** in Mine dokumenter: a named confirmation includes
the source, learning material and progress; **Avbryt** changes nothing. Confirmed
deletion closes access immediately, clears the active saved workspace and only
reports success after verified object cleanup and transactional data removal.
Failures remain under pending deletions with **Prøv sletting igjen**, including
after fresh login. Unknown upload attempts stay tracked until reconciled.

The reviewed deletion migration was approved and applied to the existing test
project as `20261118172916` on18 November2026. The ordinary local app on port8000
is restarted; log in again to use deletion. Focused checks are `uv run pytest tests/test_deletion.py -q`,
`node tests/browser-deletion.cjs`, `supabase/tests/deletion_protocol.test.sql` and
`SAVE_TEST_WSL_DISTRO=SUREUbuntu uv run python tests/deletion_provider_acceptance.py`.
See [deletion acceptance](.docs/implementation-artifacts/deletion-acceptance.md)
for executed evidence, seven-day content-free retry retention and the remaining
backup/physical-retention gates before real files.


Local backup retention was **installed on19 November2026**. Preview its configuration with
`./scripts/install-backup-retention.ps1 -Plan`. The task is already installed on
the project PC; installation on a new host must use its authorized Windows operator.
The installer refuses an existing `StudyBuddy-Backup-Rotation` task and query
errors. The hidden limited task rotates recognized seven-day archives at03:00
local and at same-user logon, with catchup when available. It requires that user
to be logged on, does not wake the PC and cannot delete files while powered off.
This schedules expiry only; the student selected manually triggered backups.
Real hosted startup now completes expiry before app import, or refuses startup;
`--check` stays read-only. An actual rotation run completed with Task Scheduler
result0 on19 November. Database authentication and the20 November backup/import
results are documented in [the backup record](.docs/implementation-artifacts/backup-local-4-1.md).

The private ignored `.env.hosted` was used for HTTPS startup on20 November,
with existing model/save state and the subsequently enabled email journal.
Its ACL is restricted to the actual operator, SYSTEM and Administrators.
Public access on port10000 was activated at17:07 and mobile access was
user-confirmed at17:11. Operator startup must preserve existing state, use
the same Windows profile and avoid conflicting ambient app variables.
On21 November the student confirmed physical two-way PC/mobile progress,
independent logout and fresh login/reopening after a controlled app restart.
Remaining cross-owner acceptance and private assessor handover remain open;
see [the hosting record](.docs/implementation-artifacts/hosting-acceptance.md).

</details>
