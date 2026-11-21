# Fram til innlevering15.12.2026

Avtalt19.11: lokal leveranse først, eksisterende kjerne/Supabase beholdes.
Offentlig lenke var et valgfritt tillegg og ble senere godkjent/aktivert20.11;
videre driftsautomatisering utsettes. Status avstemt21.11 mot daterte resultater.
Kjerne senest1.12; samlet applikasjon, README og rapport klar8.12; siste uke buffer.
Se [avgrensning](leveranseavgrensning-2026-11-19.md).

**Tilgangsoppdatering20.11:** HTTPS-registrering/e-postbekreftelse,
utlogging og vanlig passordinnlogging er brukerbekreftet. Studenten har valgt
selvregistrering og den eksisterende bekreftede `+test1`-kontoen som reserve;
kontrollen fant0 lagrede dokumenter. Faktisk testadresse/StudyBuddy-passord
overleveres privat, uten passord i repoet. Oppdatert kryptert appbackup inkluderer
konto og e-postjournal. Offentlig Funnel10000 ble aktivert kl.17:07 og
mobiltilgang brukerbekreftet kl.17:11. Toveis fysisk fremdrift, uavhengig
utlogging og ny innlogging/bevart materiale etter appomstart er
brukerbekreftet21.11. Listekontroll mellom ulike kontoer er også brukerbekreftet;
privat kontooverlevering gjenstår;
se [publisering og kontrollgrenser](hosting-acceptance.md) og
[gjeldende plan og usendt tilgangstekst](hosting-plan-4-1.md).

## Ferdig kontrollert

- [x] Kort [sensorveiledning](assessor-access.md) klargjort21.11: offentlig
  URL, innlogging/e-postgrenser, lokal demo og en konkret hovedflyt. Ingen
  innloggingsopplysninger er skrevet eller sendt; privat reserveoverlevering
  gjenstår. Praktisk listekontroll mellom kontoer er brukerbekreftet nedenfor.

- [x] Praktisk listekontroll21.11: studenten rapporterte ny konto/innlogging,
  ingen dokumentoppføringer på den nye kontoen og fortsatt Synk-test på
  originalkontoen på PC. [Observasjoner og avgrensning](hosting-acceptance.md)
  skiller dette fra de tidligere direkte API-/databasekontrollene.

- [x] Toveis fysisk PC/mobil-prøve21.11: samme lagrede Synk-test ble åpnet
  på mobilen med kort2/Quiz1 fra PC. Etter endring på mobilen ble kort1 med
  skjult svar og fortsatt Quiz1 gjenfunnet på PC etter omlasting/gjenåpning.
  Uavhengig mobilutlogging lot PC-økten fortsette. Kontrollert appomstart
  krevde ny innlogging og bevarte dokumentet/kort1/Quiz1 med skjulte svar.
  [Brukerbekreftelser og grenser](hosting-acceptance.md). Dette gjelder samme
  konto på to enheter; kontroll mellom ulike kontoer er beskrevet separat over.

- [x] Avgrenset lokal PDF-kontroll21.11 med sensorveiledningen: 7 sider /
  15 614 tegn, gjengitte sider visuelt sammenholdt med uttak, 28 eksisterende
  nettleserscenarier og 3 ekstra PDF-/feil-/utloggingsscenarier bestod.
  [Resultater og grenser](pdf-acceptance-2026-11-21.md). Ingen ekte modell- eller
  Supabase-kall i den lokale prøven.
- [x] Veiledet PDF-hovedflyt21.11 med studentens Context engineering.pdf:
  1 side/2975 tegn lokalt visuelt kontrollert. Studenten bekrefter opplasting,
  fire læringsdeler, ett svar/Side1, lagring, gjenåpnet kort2/Quiz1 med skjulte
  svar, bortfall etter sletting og utlogging/ny innloggingsgrense. Ingen
  slettemelding ble observert; dette er åpent nedenfor. Budsjett11→12 forsøk /
  USD0,55→0,60 reservert, ublokkert, ingen ny automatisert smoke.
  [Resultater og presise grenser](pdf-acceptance-2026-11-21.md).

- [x] Offentlig skoleutprøving20.11: HTTPS-aktivering og mobilnettprøve er
  dokumentert i [akseptansenotatet](hosting-acceptance.md). Selvregistrering,
  e-postbekreftelse og ny passordinnlogging er brukerbekreftet; reservekonto
  er valgt for privat overlevering. Toveis fysisk fremdrift ble senere
  brukerbekreftet21.11 som beskrevet over.
- [x] Manuell kryptert appbackup20.11, oppdatert kl.16:10: ekte isolert
  PostgreSQL17.11-import og samsvar mellom database og fem inkluderte
  Storage-filer bestod. Konto/e-postjournal er med i oppdatert kopi.
  Manuell utløsning er valgt; installert sjudagersjobb roterer arkiver.
  [Backupresultater og grenser](backup-local-4-1.md) skiller dette fra full
  plattform-/rolle-/live-restore og avstemming av senere slettinger/budsjett.
- [x] Dokumentasjonsavstemming21.11: README, hostingplan, sprintstatus og
  leveranseoversikter skiller publisert skoleutprøving fra åpne sluttkontroller.
  Dette er dokumentarbeid med eksisterende evidens, uten ny live-/driftsprøve.

- [x] Veiledet manuell **tekstflyt i live-modus**19.11: innlogging/tomtilstand,
  tre syntetiske kildeavsnitt, én ekte generering, ett svar mot kildereferanse,
  privat lagring, kort2/quiz1 bevart ved gjenåpning med skjult svar, sletting av
  Fjord-testen og utlogging er brukerbekreftet. Journal10→11 forsøk og
  USD0,50→0,55 reservert av5; ingen ytterligere modellkall observert.
  [Resultater og avgrensninger](live-walkthrough-2026-11-19.md).
  Gammel123-oppføring er separat fjernet administrativt etter uttrykkelig
  instruks; teknisk filrest er fortsatt uavklart og bevart kryptert lokalt.
  Dette er ikke PDF-/full feilflyt-/full tilgjengelighets- eller fysisk
  retensjonsakseptanse.

- [x] Sensorveiledning del1 (s.1–7) og oppgavealternativet i studentens lokale
  mappe er lest19.11. [Krav, eksisterende evidens og prioritert restliste](sensor-guidance-check-2026-11-19.md).
  Del1 teller70%, refleksjonsrapport30%; offentlig hosting/automatisk backup
  er ikke eksplisitte krav i disse kildene. Overordnet veiledning og fullstendige
  del2-/innleveringskrav er fortsatt ikke kontrollert. Fast demo alene er ikke
  bevis for hele live-kjerneflyten.

- [x] Veiledet manuell Narrator-kontroll av den faste demoen19.11: studenten
  bekreftet knapp/resultat, tastaturfaner, avdekket svar/kilde, riktig quiz uten
  skjult fasit lest og Ny økt/eksempelvelger. Firefox160.0/Narrator10.0.26100.9949.
  [Brukerobservasjoner og eksakte grenser](screen-reader-check-2026-11-19.md).
  Dette er ikke full WCAG-/live-flyt-/alle-nettlesere-akseptanse.

- [x] PRD-tilbakemeldingen fra12.11 er fulgt opp19.11: prioritert omfang/fallback,
  tese/UJ-1/glossar, presise FR-3/4/8 og eksisterende modell-/kostnadsgrenser.
  Detaljerte sjekker er flyttet uendret til vedlegg. Alle12 FR-/5 NFR-ID-er
  beholdt,10 flyttede tekstblokker og lokale lenker kontrollert; én kildeavstemming
  uten gjenværende tapte krav. [Oppfølging og leveransehull](prd-feedback-followup-2026-11-19.md).

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

1. **Oppgavekrav:** Del1-veiledning og oppgavealternativ er sammenholdt med
   leveransen; følg den korte restlisten i kravoversikten. Overordnet veiledning
   og fullstendige rapport-/innleveringskrav gjenstår; formativ PRD-tilbakemelding
   erstatter ikke disse.
2. **README og oppsett:** Gjeldende publisering, e-post og manuell backup er
   avstemt21.11. Ren kopi/nytt virtuelt miljø og demooppstart er
   kontrollert på Windows. README har kort oppskrift, portalternativ og tydelig
   demo/live-skille; tekniske detaljer er sammenleggbare. Eventuell kontroll på
   en annen maskin er fortsatt egen leveransekontroll, ikke allerede bevist.
3. **Brukbarhet og gjenværende feil:** Gjør én samlet manuell hovedflyt, med
   tastatur/skjermleser og tydelige feilmeldinger. Gjenbruk eksisterende
   innholds-/tilgangsevidens; kjør bare nye tester for faktiske hull/endringer.
   [Kort live-gjennomgang](live-walkthrough-2026-11-19.md) er klargjort;
   innlogget tomtilstand, kildevisning med tre syntetiske avsnitt, én ekte
   generering og ett kontrollert svar/kilde med privat lagring er brukerbekreftet.
   Fremdrift/gjenåpning, sletting av Fjord-testen og utlogging er også bekreftet.
   Den gamle ventende appoppføringen ble fjernet etter uttrykkelig instruks;
   uavklart fysisk filrest beholdes i operatørjournal.
   Demo-statusfeilen og manuell skjermleserkontroll av demoen er fulgt opp.
   Innlogget arbeidsområde/PDF-/feilflyt og andre hjelpemiddel-/nettlesergrenser
   er ikke dekket av denne demotesten. Oppsummer resterende
   live-innloggings-/PDF-/slettebegrensninger ærlig.
4. **Rapport og levering:** Fyll rapporten med studentens egne vurderinger, og
   bruk refleksjonsnotatene som faktagrunnlag. Sjekk kilder, oppstartsoppskrift,
   hemmeligheter/testdata og nødvendige innleveringsfiler i en samlet gjennomgang
   før8.12. Et [fakta-/arbeidsutkast](../../.reflection-doc/refleksjonsrapport-utkast.md)
   er laget19.11, med egne refleksjoner/korrekt studentinfo og sluttkontroll
   fortsatt åpne. Ingen nye funksjoner etter1.12.

## Åpent og utsatt arbeid

- Privat overlevering av reservekonto til sensor. Praktisk listekontroll mellom
  ulike kontoer, toveis fysisk fremdrift, uavhengig utlogging og
  ny innlogging/gjenåpning etter appomstart er brukerbekreftet21.11.
- Flere representative PDF-/lysbildeoppsett, full feilflyt, tilgjengelighet i innlogget arbeidsområde
  og resterende negative e-postlenke-/malkontroller.
- Slettemeldingen ble ikke observert i brukerprøven, men studenten presiserte
  at den kan ha blitt oversett og ønsket å gå videre.7 lokale kontroller bestod;
  ingen bekreftet feil. Undersøk faktisk visning ved gjentakelse.
- Eldre fysisk filrest, gjentakbart eksplisitt CA-oppsett og full
  plattform-/rolle-/live-restore med avstemming av senere slettinger/budsjett.
- Videre driftsautomatisering er utsatt; manuell backup er valgt. Automatisk
  daglig eksport er ikke installert. Sjudagers arkivrotasjon er installert.
- Refleksjonsrapporten avventer studentens videre arbeid etter ønsket21.11;
  fullstendige rapport-/innleveringskrav og samlet leveransekontroll gjenstår.

Godkjent offentlig skoleutprøving gjelder ikke-sensitivt testmateriale.
Full sikkerhets-/produksjonsakseptanse for reelle private data hevdes ikke.
