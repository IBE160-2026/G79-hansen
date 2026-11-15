# Eget kildemateriale – Story 2.4

## 2026-11-15 kl. 10:23 — Fredrik

### Oppgave
Studenten spurte hva som følger etter ferdigstilt Story 2.3. Neste backloggoppgave ble forklart som innlimt tekst, tekstfil og tekstbasert PDF, før KI-generering i Story 2.5. Studenten svarte «start med det» på tilbudet om å lage den konkrete planen for Story 2.4.

### Plan
- Følg ny BMAD build fra steg 1/2, gjenbruk Epic 2-kontekst og avsluttet Story 2.3. Se [forrige logg](992-2026-11-15-09-06-52-utlogging-og-oktavslutning.md).
- Undersøk eksisterende PDF-probe, kildekontrakter, demo-UI og autentisering uten appkode-/serverendringer.
- Skriv og selvkontroller [konkret spec](../../.docs/implementation-artifacts/spec-2-4-validate-and-extract-the-active-source.md), legg den frem ved steg 2 CHECKPOINT 1 og loggfør resultatet.

### Resultat
Arbeidskopien var ren ved oppstart. Baseline er **2fd75fb7eb22965a5288635dde21751ade10cfb0**. BMAD build ble rendret nøyaktig én gang for denne nye oppgaven; workflow, steg 1, steg 2 og spec-mal ble lest. Cached Epic 2-kontekst er gyldig og nyere enn alle planleggingsfilene. Ferdig Story 2.3 ble brukt som kontinuitet, uten å åpne dens plangodkjenning på nytt. Story 2.4s eksakte sprintnøkkel er `2-4-validate-and-extract-the-active-source`.

To kun-lesende agenter undersøkte PDF-isolasjon og UI/kontrakter etter steg 2s delegasjonsinstruks. Ingen filer, servere eller kontotilstander ble endret av dem. PDF-agenten leste tidligere JUnit-evidens (62 bestått/én skip); ingen ny kjøring ble hevdet. Eksisterende `Source`, `SourceUnit`, `Settings`, `probe_stream`, Windows Job Object og auth-/sekvensmønstre kan gjenbrukes. Dagens hovedside/demo er bevisst låst til eksempeldata; planen gir eget materiale en separat innlogget `/workspace`-flate. Offisiell pypdf 7.0.1-dokumentasjon og Python 3.13-dokumentasjon for base64/UTF-8 ble kontrollert.

Spesifikasjonen er **draft**, route **dispatch**, og sprint 2.4 forblir **backlog**. Planen beskriver ett aktivt tekst-/fil-/PDF-inntak med forhåndsvisning, bevarte studieinnstillinger, riktige avsnitt/fysiske sider og avvisning over 30 000 kodepunkter, 40 sider eller 10 MiB fil. Strengt JSON/base64-inntak unngår diskspooling; eget wire-/bodybudsjett og begrenset arbeid supplerer PDF-probens isolasjon. Et ikke-autoriserende `sessionViewId` skal hindre at eldre materiale følger med ved ny innlogging, også på samme konto. Privat kilde forblir flyktig. KI-generering, receipts/lagring, hosting og eksterne kontohandlinger inngår ikke.

Ingen uavklarte produktspørsmål gjenstår før den konkrete plangodkjenningen. Specen ble selvkontrollert og forkortet fra 1733 til **1586 tokens**, målt med `tiktoken`/`o200k_base` i en midlertidig uv-verktøyavhengighet; appens avhengigheter/lockfil er ikke endret. `git diff --check` bestod. Ingen ny funksjonstest, faktisk dokumentakseptanse eller implementering er hevdet. Windows-/syntetisk PDF-evidens er uttrykkelig avgrenset fra representative tillatte dokumenter og senere målplattform.

Under lesing ble tegnfeil i forrige sluttføringslogg/refleksjonsgrunnlag og enkelte overskrifter oppdaget: norske tegn hadde blitt spørsmålstegn ved tekst sendt gjennom PowerShells stdin-koding. Tegnene ble rettet med direkte UTF-8 uten endring av fakta. Utdaterte Story 2.3-kommentarer i sprintstatus og README ble også rettet; godkjent blokkhash for 2.3 er fortsatt `0669a8ae87bcd57293b81ccc0cee6567e7795f60388dde9e08aa8946d82fc64e`. Dette er dokumentasjonsrettinger, ikke nye testresultater eller endring av akseptansestatus.

Plan/refleksjon og øvrige dokumentasjonsrettinger er lagret lokalt i **177871779e3415e8cfa486552a0aa24dae879e4c** (`docs(sources): draft story 2.4 extraction plan`). Ingen push. Ingen appkode, serverrestart, Supabase-innstilling, ny konto/e-post, passordmutasjon, kostnad eller utrulling er utført. Studentens egne refleksjoner er ikke skrevet av KI.

### Åpne punkter
- Godkjenn eller juster den konkrete Story 2.4-planen før implementering; dette er ny plan, og tidligere Story 2.3-godkjenning er ikke brukt som erstatning. Ved godkjenning må specen leses fra disk på nytt før status endres.
- Eksisterende åpne PDF-integrasjons-/målplattform- og Story 2.1/2.2-lenke-/malporter beholdes i `issues.md`; ikke gjenta det vellykkede passordbyttet eller send nye e-poster automatisk.

## 2026-11-15 kl. 11:37 — Fredrik

### Oppgave
Studenten godkjente den konkrete planen med «godkjenn og fortsett». Etter at implementeringsagenten traff en bruksgrense, ba studenten «fortsett». Fullfør godkjent Story 2.4 med kode, tester, uavhengig review, dokumentasjon/logg og lokal commit; ingen ny planrunde.

### Plan
- Les [lagret spec](../../.docs/implementation-artifacts/spec-2-4-validate-and-extract-the-active-source.md) på nytt, lås godkjent blokk og følg eksisterende BMAD build fra steg 3.
- Implementer den beskyttede kildeflyten sekvensielt, bevar demo/auth og kontroller uttrekk mot gjengitte kjente PDF-sider.
- Verifiser oppgavene/matrisen, gjennomfør tre uavhengige reviewlag, rett bekreftede funn og gjenta full verifikasjon før sluttføring.

### Resultat
Specen var uendret ved ny disklesing; godkjenning ble registrert før ready-for-dev/in-progress. Opprinnelig baseline **2fd75fb7eb22965a5288635dde21751ade10cfb0** ble beholdt. Godkjent blokk fikk SHA-256 **bba17495533b217d96a9c382c43a59714338a307aec8b0df249d2ec10b7d6914**, som fortsatt er uendret. Ingen ny rendering eller plangodkjenning. Sprint ble synkronisert til in-progress, senere review.

Én implementeringsagent uten tidligere samtalekontekst fikk den eksakte full-spec-handoff fra steg 3 og skrev backend, UI og fokuserte tester/nettleserfixture. Den stoppet med faktisk bruksgrense før sluttrapport og dokumentasjon. Etter studentens «fortsett» tok hovedagenten over, leste de faktiske filene/diffen og fullførte dokumentasjon, verifikasjon og senere rettelser selv. Ingen feilfri/fullsjekket implementering ble antatt fra agentens mellomstatus.

Implementasjonen gir `/workspace`, tekst-/UTF-8-fil-/PDF-inntak, kanoniske kildeenheter, fysiske PDF-sider og tydelig delvis dekning, bevarte studieinnstillinger og trygg tømming/forkasting ved endret kilde, nullstilling, utløp, avvist autoritet, ny innlogging og pagehide. Status har et ikke-autoriserende `sessionViewId`; kopiert kjennetegn gir ingen tilgang. Strengt JSON/base64-inntak har egne byte-/body-/strukturgrenser uten diskspooling, og kapasitetsopptak før innlesing. Det er to forespørsler globalt/én per økt og én isolert PDF-worker globalt, med ressursopprydding som ikke frigis tidlig ved avbrutt HTTP-venter. Den låste pypdf 7.0.1 er nå runtime-avhengighet; eksisterende eksperimentkommandoer og begrensninger er bevart. Ingen kildebevarende serverregister/database, modellkall eller fabrikkert læringsresultat er lagt til.

Hovedagentens første kontroll ga 59 nye kildetester og 13 kildenettleserscenarier. Før uavhengig review bestod full suite med 302 tester/én uendret PDF-plattformskip, alle 181 auth-/59 kildetilfeller, og 13 kilde-/33 auth-/11 demoscenarier. Oppgavene og alle seks frosne matriserader ble kontrollert mot faktisk kjørte tester. Tidligere tester er tydelig skilt fra sluttkjøringen nedenfor.

Tre uavhengige reviewlag ble startet før noen rapport ble triagert. Blind-review ga elleve funn, edge-review to overlappende funn og verifikasjonsreview to pre-verifiserte testgap. Alle fikk egen dom i specen før gruppering. Bekreftede rettelser gjelder vilkårlige JSON-objektgrafer/eventloop-arbeid, overlappende statusobservasjoner som skjulte vellykket resultat, sen status etter avvisning, tidsbegrensning og bevart retry ved arbeidsflatens utlogging/restaurering, lokal tegnkontroll før paste-opplasting, direkte workspace-logout- og nøyaktig PDF-tekstregresjoner, samt dokumentasjon. En 60 011-byte JSON-probe med 20 000 tomme objekter allokerte 1 513 276 byte før retting; den formen avvises nå før objektene bygges, og parsing/klargjøring kjører i egne begrensede tråder. Et generelt forslag om ekstra shutdown-hook ble avvist: ingen unnsluppet/lekkende worker var dokumentert, og eksisterende body-deadline/Job Object/probe-finally begrenser og rydder arbeidet. Ingen reviewfunn ble utsatt, og ingen frosset intensjon ble endret. Én uavhengig oppfølgingsgjennomlesning fant ingen nye konkrete feil; den kjørte ikke egne tester.

**Siste faktiske parent-verifikasjon etter alle kodeendringer:**
- `uv sync --locked --group pdf-experiment`: bestått.
- `uv run --group pdf-experiment pytest --junitxml=test-results/source-parent-verification-final.xml`: **306 bestått, én uendret valgfri PDF-plattformskip, én eksisterende Starlette-advarsel**, 77,74 sekunder. JUnit: **181 auth- og 63 kildetilfeller uten feil/skips**, inkludert alle ni faktiske isolerte PDF-integrasjonstilfeller.
- `node tests/browser-sources.cjs`: **19 bestått**; `node tests/browser-auth.cjs`: **33 bestått**; `node tests/browser-demo.cjs`: **11 bestått / 21 genereringskall**.
- `git diff --check`: bestått. Begge godkjente blokker for Story 2.3/2.4 har uendrede SHA-256. Arbeidsflatens 320 px/200 %-bilder ble inspisert uten overflyt/avkuttet innhold.

**Visuell PDF-evidens:** Hovedagenten forfattet en enkel syntetisk tre-siders PDF med ordinær synlig tekst på side 1/3 og blank side 2. Alle Poppler-gjengitte sider ble visuelt inspisert; API-et returnerte nøyaktig samme tekst med fysiske plasseringer [1,3], totalPages=3 og unreadablePages=[2]. Opprydding og private headere bestod. Selve isolerte proben observerte workerReaped=true, peak committed memory 33 910 784 byte og 1,0708 sekunder. Poppler ble pakket ut portabelt under ignorerte testfiler etter SHA-256-kontroll, ReportLab brukt bare som midlertidig uv-verktøy. Dette er kontrollert syntetisk/render-evidens, ikke godkjenning av vilkårlige forelesnings-PDF-er eller målplattform. Detaljer i [kildeflytens akseptansedokument](../../.docs/implementation-artifacts/source-acceptance.md).

**Lokal drift:** Gammel worker **11748** ble kontrollert mot prosjektets virtualenv/uvicorn-kommando før stopp. Ny worker **45744** (launcher 45572) kjører én prosess på `127.0.0.1:8000` med eksisterende ignorert `.env`. **8/8 uinnloggede oppstarts-/sikkerhetskontroller** bestod: helse, arbeidsflate/private headere, ny JS, avvist ubeskyttet/kontoløs kildebehandling, konfigurert uinnlogget status og ingen eksponert `.env`. Ingen ekte konto-, e-post- eller passordhandling ble kjørt for denne storyen. De isolerte nettleserserverne er stoppet. Omstarten avslutter gamle lokale økter; studenten må logge inn igjen.

Ny kode-/dokumentcommit er **c5b207ff8523c9b62668043f2ea69466e9e39ac7** (`feat(sources): validate and preview authenticated study material`), 22 filer. Ingen push. Spec **done**, sprint **review** for avsluttende menneskelig/produktakseptanse. README, sluttevidens, sprintstatus og refleksjonsgrunnlag er oppdatert; issue om plangodkjenning er lukket. Tidligere tegnopprydding hadde utilsiktet endret ett spørsmålstegn i et refleksjonsspørsmål; dette er rettet uten å skrive studentens egen refleksjon. Ingen hosted-innstillinger, modell-/lagringsintegrasjon, kostnad eller utrulling er utført; Free/Paris og tidligere e-postporter er bevart.

### Åpne punkter
- Representativt tillatt pensummateriale, leserekkefølge/uttak mot gjengitte sider og faktisk fremtidig hosting/isolasjonsmiljø må fortsatt vurderes før bred PDF-/driftsakseptanse. Lokal Windows-integrasjon er nå kontrollert; eksisterende PDF-issue er oppdatert med denne forskjellen.
- Eldre Story 2.1/2.2-lenke-/malporter og UX-/skjermleserakseptanse består. Ikke gjenta det vellykkede passordbyttet eller send nye e-poster automatisk. Punktene står allerede i `issues.md`.
- Neste utviklingsoppgave er Story 2.5, ekte generering fra godkjent kilde. Modell/API, budsjett og datahåndtering må avklares før modellintegrasjon; dette er eksisterende live-arbeidspunkt i `issues.md`, ikke utført arbeid.
