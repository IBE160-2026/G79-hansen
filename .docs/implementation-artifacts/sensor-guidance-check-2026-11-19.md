# Leveransen mot sensorveiledningen – 19.11.2026

## Kilder og avgrensning

Studenten viste til `C:\IBE160\Oppgave`. Mappen inneholdt:

- `Sensorveiledning IBE160 - Del 1 applikasjon og prosess.pdf`, s.1–7.
  SHA256: `a0069856666a32e2e5c886fe1c46ade1d666a99bf800bc42b9e20113adc2e509`.
- `Skjermbilde 2026-11-19 180926.png`: oppgavealternativet «AI Study Buddy».

PDF-teksten er lest; skjermbildet er visuelt inspisert. Originalene ligger
utenfor repoet. Dette er en kildebasert avstemming mot eksisterende dokumentasjon,
ikke nye funksjonstester, full kode-/hemmelighetskontroll eller karaktersetting.
PDF-en utfyller en **overordnet sensorveiledning** som ikke lå i mappen.
Den bekrefter del1/applikasjon og prosess70% og refleksjonsrapport30%, men
gir ikke fullstendige form-/innleveringskrav for del2. Rapportmalens3000–5000
ord beholdes som malens forventning, ikke et nytt bekreftet krav fra denne PDF-en.

## Konsekvens for omfanget

Oppgavealternativet beskriver en enkel app som lager sammendrag, flashcards og
quiz fra PDF/tekst, med begreper og kilde-/sidereferanser. Innlogging kreves hvis
materiale lagres eller deles. LLM/konfidensialitet, detaljnivå, figurer/tabeller
og lokal behandling/skytjeneste er beslutningspunkter. Eksisterende valg og
begrensninger er beskrevet i [PRD](../planning-artifacts/prds/prd-G79-hansen-2026-09-26/prd.md).

Disse to kildene stiller ikke eksplisitt krav om offentlig hosting, Tailscale
eller automatisk full backup. Sensorveiledningen s.2 beskriver kloning og lokal
oppstart fra README i rent miljø, med veiledende15–20min innsats. Den avtalte
[lokale leveransen](leveranseavgrensning-2026-11-19.md) er derfor en rimelig
prioritering. Dette er vår tolkning av de tilgjengelige kildene; senere godkjente
løfter og eventuelle overordnede krav må også tas med.

**Fast demo er ikke hele appen.** Sensor vurderer kjerneflytene mot godkjent
proposal og README. Egne dokumenter, ekte generering og implementert privat
lagring må ha tydelig oppsett/tilgang og etterprøvbare resultater. Nøkkelfri demo
erstatter ikke denne funksjonaliteten eller beviser at live-kjerneflyten fungerer.

## De sju kriteriene i del1

Vektene under gjelder innenfor del1 og er veiledende. Evidensen er et startpunkt,
ikke en påstand om at alle kriterier er ferdig oppfylt.

| Kriterium | Vekt | Eksisterende grunnlag | Gjenstående leveransearbeid |
| --- | --- | --- | --- |
| Prosess og KI-styring | 30% | [Brief](../planning-artifacts/briefs/brief-G79-hansen-2026-09-26/brief.md), PRD, [arkitektur](../planning-artifacts/architecture/architecture-G79-hansen-2026-11-01/architecture-explained.md), Git-historikk og [beslutnings-/KI-notater](../../.reflection-doc/refleksjonsnotater.md). | Lag en kort leserute fra konkrete krav til kode, kontroll og studentens korrigeringer; kontroller samsvar med godkjent proposal. |
| Funksjonalitet og omfang | 20% | [Kilder/PDF](source-acceptance.md), [generering](generation-acceptance.md), [innholdskontroll](content-evaluation.md), [lagring](save-acceptance.md), [bibliotek](library-acceptance.md), [fremdrift](progress-acceptance.md) og [sletting](deletion-acceptance.md). | Én samlet manuell live-hovedflyt med syntetiske data; avklar sensorens praktiske tilgang uten å dele hemmeligheter i Git. Behold dokumenterte avgrensninger/åpne tilgangsporter. |
| Kvalitetssikring og testing | 15% | README har Python-/nettleserkommandoer; funksjonsnotatene skiller simulerte og reelle kontroller. Konkret statusfeil er rettet i `2494ce9`. | Sluttkontroll av relevante kommandoer og feilinput fra aktuell leveranseversjon. Gjenbruk eldre evidens med dato; ikke kall den en fersk full test. |
| Design og brukeropplevelse | 10% | [Instrumentert brukskontroll](usability-check-2026-11-19.md), [brukerbekreftet Narrator-demo](screen-reader-check-2026-11-19.md) og UX-planlegging. | Kontroller tydelige feil og tastatur i innlogget hovedflyt. Den avgrensede demoen er ikke full tilgjengelighetsakseptanse. |
| Kodekvalitet og arkitektur | 10% | Python/FastAPI, statiske klientfiler, låste avhengigheter, arkitektur og eksisterende gjennomganger. | Kort samsvarskontroll mellom faktisk struktur, konfigurasjon og dokumentasjon; beskriv Windows-begrensningen for PDF. Ingen ny arkitektur trengs for denne avstemmingen. |
| README og kjørbarhet | 10% | [README](../../README.md), ren Windows-kopi/nytt virtuelt miljø og nøkkelfri demooppstart19.11. | Endelig README-kontroll på innleveringsversjonen, særlig live-oppsett/testdata/tilgang. Tidligere kontroll var på samme PC, ikke ny maskin/annet OS. |
| Ryddighet i repoet | 5% | `.gitignore` skiller miljø, nøkler, testresultater og lokal tilstand. Dokumentasjon og kode har egne mapper. | Endelig kontroll av versjonerte filer og hemmeligheter også i historikken; ingen slik full kontroll er gjort i denne økten. Bevar relevant prosessevidens. |

## Kort prioritert restliste

1. Samlet manuell live-hovedflyt med tillatte syntetiske data og de eksisterende
   sikkerhetsgrensene; test nye hull fremfor å kjøre alle eldre tester om igjen nå.
2. Kort inngang til prosessevidens og en praktisk oppskrift for sensorens
   live-kontroll. En egen foreleserkonto er valgt; e-post er fortsatt uavklart.
3. Studentens egne refleksjoner og studentinfo, og avklaring av overordnet
   veiledning/del2/innleveringsformat før rapporten sluttføres.
4. Samlet sjekk av aktuell kode, README, tester og repo før arbeidsmålet8.12.
   Innleveringsfristen15.12.2026 er studentens bekreftede frist.

Ingen ny funksjon, offentlig lenke eller utvidet drift følger av denne avstemmingen.
