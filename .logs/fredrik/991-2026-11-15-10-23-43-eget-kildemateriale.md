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
