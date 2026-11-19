# Fram til innlevering15.12.2026

Avtalt19.11: lokal leveranse først, eksisterende kjerne/Supabase beholdes,
offentlig lenke og videre hosting-/backupautomatisering utsettes.
Kjerne senest1.12; samlet applikasjon, README og rapport klar8.12; siste uke buffer.
Se [avgrensning](leveranseavgrensning-2026-11-19.md).

## Ferdig kontrollert

- [x] Avgrenset instrumentert tastatur-/visningskontroll19.11: fire kontrollpunkter
  observert med forventet resultat, desktop og390px visuelt inspisert, ingen
  eksterne sideforespørsler eller JavaScript-feil. Én misvisende statuslinje
  funnet ved fanebytte og deretter rettet med egen regresjon. Dette erstatter ikke manuell skjermleser-
  eller full tilgjengelighetskontroll. Se [resultat og funn](usability-check-2026-11-19.md).

- [x] README/ren oppstart19.11: kopi av versjonerte filer fra3484527, med
  oppdatert README, uten `.env`, nøkler, lokale journaler eller eksisterende
  `.venv`. `uv sync --locked` laget nytt miljø og installerte47 pakker.
  README-kommandoen med ledig port8001 startet demoen; side, demo-helsesjekk,
  fixture og alle fire læringsdeler bestod. Egen kontrollserver er avsluttet;
  original PID25940/port8000 ble ikke erstattet. Dette er Windows på samme PC
  med Python3.13.7/uv0.8.15 fra før og mulig gjenbruk av pakkebuffer, ikke bevis
  for nyinstallasjon av Python/uv på andre maskiner eller operativsystemer.
  Ingen ny full testpakke eller ekte modell-/provider-/e-postkall.
- [x] Nøkkelfri demo i separat midlertidig server:19.11 bestod alle11 scenarier i
  `tests/browser-demo.cjs`. Appvariabler og eventuell ekstern demo-adresse ble
  fjernet bare fra kontrollprosessens miljø. Ingen `.env` ble lastet av serveren.
  Faste eksempeldata, fire læringsdeler, svar/kildereferanser, uavhengig fremdrift,
  feil/nytt forsøk, tidsavbrudd, reset, tastatur og smal skjerm/200% layout inngikk.
  21 demoforespørsler, ingen ekte modell-/e-post-/providerkall. Serveren ble
  avsluttet av kontrollskriptet; eksisterende app på8000 ble ikke erstattet.
- [x] Tekst/PDF-generering, innholdsevaluering og Supabase-innlogging/lagring/
  bibliotek/fremdrift/sletting er implementert og har tidligere fokusert evidens.
  Dette er status, ikke en ny full akseptanse. Kilder: eksisterende
  [issues](../../.logs/fredrik/issues.md) og funksjonslogger; åpne begrensninger beholdes.

## Neste konkrete leveransearbeid

1. **Oppgavekrav:** Finn/sammenhold faktisk oppgavetekst og sensorveiledning med
   denne leveransen. Faglærertilbakemeldingen er ikke full vurderingsveiledning.
2. **README og oppsett:** Ren kopi/nytt virtuelt miljø og demooppstart er
   kontrollert på Windows. README har kort oppskrift, portalternativ og tydelig
   demo/live-skille; tekniske detaljer er sammenleggbare. Eventuell kontroll på
   en annen maskin er fortsatt egen leveransekontroll, ikke allerede bevist.
3. **Brukbarhet og gjenværende feil:** Gjør én samlet manuell hovedflyt, med
   tastatur/skjermleser og tydelige feilmeldinger. Gjenbruk eksisterende
   innholds-/tilgangsevidens; kjør bare nye tester for faktiske hull/endringer.
   Demo-statusfeilen fra19.11 er rettet; faktisk manuell skjermlesergjennomgang
   gjenstår. Oppsummer resterende live-innloggings-/PDF-/slettebegrensninger ærlig.
4. **Rapport og levering:** Fyll rapporten med studentens egne vurderinger, og
   bruk refleksjonsnotatene som faktagrunnlag. Sjekk kilder, oppstartsoppskrift,
   hemmeligheter/testdata og nødvendige innleveringsfiler i en samlet gjennomgang
   før8.12. Et [fakta-/arbeidsutkast](../../.reflection-doc/refleksjonsrapport-utkast.md)
   er laget19.11, med egne refleksjoner/korrekt studentinfo og sluttkontroll
   fortsatt åpne. Ingen nye funksjoner etter1.12.

## Utsatt, ikke ferdig

Offentlig HTTPS/Funnel, foreleserkonto/e-post, to-fysiske-enheter og komplett
automatisk DB+Storage-backup/isolert restore. Passordsjekken ble gjenopptatt og
bestod19.11 med lokalt kryptert passord og eksplisitt prosjekt-CA/verify-full;
dette er ikke komplett backup-/eksportakseptanse.
Eksisterende rotasjonsjobb og privat `.env.hosted` beholdes urørt. Ved senere
offentlig bruk/reelle private data gjelder tidligere sikkerhets-/tilgangs-/
backupporter og separat publiseringsgodkjenning. Ingen slik akseptanse hevdes.
