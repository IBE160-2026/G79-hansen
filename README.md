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

Dette er Story 1.1: faste syntetiske eksempeldata på norsk med kort sammendrag. Ingen AI-modell behandler tekst. Egen tekst, tekstfil/PDF, språk-/detaljvalg, innlogging, Lagre, Mine dokumenter og varig fremdrift er senere arbeid. Den aktive tilstanden finnes bare i minnet på den åpne siden og forsvinner ved omlasting. Feil gir eksplisitt prøv-igjen; demoen bytter aldri til et falskt vellykket svar.

`.env.example` dokumenterer at demoen ikke trenger konfigurasjon. Å legge til nøkler aktiverer ingen livefunksjon. Live AI/Supabase, godkjente kostnader, sikker innlogging, lagring og utrulling må implementeres og testes i senere historier. Bare tre eksplisitte offentlige UI-filer serveres; repositoryfiler og dokumentasjon er ikke statisk tilgjengelige. Den historiske UX-prototypen ligger uendret under `.docs/planning-artifacts/ux-designs/`.

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
```

Testscriptet starter og stopper selv en lokal uvicorn-prosess på en ledig port. Hvis Playwright Chromium mangler, prøver det installert Microsoft Edge. Sett eventuelt `$env:DEMO_BROWSER_CHANNEL = "msedge"` for å velge Edge direkte. `DEMO_BASE_URL` kan peke mot en allerede kjørende lokal demo.

Nettlesertestene dekker alle fire deler, kildevisning, separate posisjoner og svar, tastatur/fokus, antall genereringskall, duplikatvern, reset med et forsinket svar som ignorerer kansellering, feil ved første innlasting, semantisk ugyldige svar og eksplisitt retry. Både innlasting og generering har et tidsavbrudd på 15 sekunder som testes med reell ventetid. De kontrollerer horisontal overløp ved 320/390/480 piksler og 200 % layoutzoom og legger skjermbilder i den ignorerte mappen `test-results/`. Dette er automatiserte nettlesersjekker; en full manuell skjermleser- og WCAG-vurdering er ikke gjennomført.

## Medlemmer

- Fredrik Fladmark Hansen
