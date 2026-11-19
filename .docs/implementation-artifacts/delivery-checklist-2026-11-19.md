# Fram til innlevering15.12.2026

Avtalt19.11: lokal leveranse først, eksisterende kjerne/Supabase beholdes,
offentlig lenke og videre hosting-/backupautomatisering utsettes.
Kjerne senest1.12; samlet applikasjon, README og rapport klar8.12; siste uke buffer.
Se [avgrensning](leveranseavgrensning-2026-11-19.md).

## Ferdig kontrollert

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
2. **README og oppsett:** Gjør inngangen kort og tydelig. Kontroller oppsett fra
   ren kopi uten nøkler; dagens kontroll brukte installerte avhengigheter og
   beviser ikke nyinstallasjon. Skill fast demo fra valgfri live-konfigurasjon.
3. **Brukbarhet og gjenværende feil:** Gjør én samlet manuell hovedflyt, med
   tastatur/skjermleser og tydelige feilmeldinger. Gjenbruk eksisterende
   innholds-/tilgangsevidens; kjør bare nye tester for faktiske hull/endringer.
   Oppsummer resterende live-innloggings-/PDF-/slettebegrensninger ærlig.
4. **Rapport og levering:** Fyll rapporten med studentens egne vurderinger, og
   bruk refleksjonsnotatene som faktagrunnlag. Sjekk kilder, oppstartsoppskrift,
   hemmeligheter/testdata og nødvendige innleveringsfiler i en samlet gjennomgang
   før8.12. Ingen nye funksjoner etter1.12.

## Utsatt, ikke ferdig

Offentlig HTTPS/Funnel, foreleserkonto/e-post, to-fysiske-enheter og komplett
automatisk DB+Storage-backup/isolert restore. Passordsjekken venter fortsatt.
Eksisterende rotasjonsjobb og privat `.env.hosted` beholdes urørt. Ved senere
offentlig bruk/reelle private data gjelder tidligere sikkerhets-/tilgangs-/
backupporter og separat publiseringsgodkjenning. Ingen slik akseptanse hevdes.
