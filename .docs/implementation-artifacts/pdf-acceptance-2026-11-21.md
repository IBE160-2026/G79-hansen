# PDF-kontroll og brukerbekreftet hovedflyt – 21.11.2026

## Omfang og status

Studenten ba om å gå videre med punkt3 fra mangelvurderingen: samlet sluttprøve
med representative PDF-er. Lokal kilde-/feilkontroll er gjennomført med den
tilgjengelige sensorveiledningen. Deretter oppga studenten `Context engineering.pdf`
og gjennomførte en veiledet vanlig appflyt fra opplasting til generering,
kildekontroll, lagring, gjenåpning, sletting og utlogging. Resultatene nedenfor
skiller agentens lokale kontroller fra studentens bekreftelser. Slettemeldingen
ble ikke observert i brukerprøven. Studenten presiserte senere at den kan ha
blitt oversett og ønsket å gå videre; dette behandles som en usikker observasjon.

Kilde: `C:\IBE160\Oppgave\Sensorveiledning IBE160 - Del 1 applikasjon og prosess.pdf`.
SHA256: `a0069856666a32e2e5c886fe1c46ade1d666a99bf800bc42b9e20113adc2e509`.
Kilden er ikke kopiert inn i repoet. Appkoden er uendret fra `a32bdc3`;
eksisterende dokumentendringer fra forrige oppgave er beholdt.

## Utførte kontroller

| Kontroll | Faktisk resultat |
| --- | --- |
| Appens kontrollerte Windows-PDF-uttak | Godtatt: 7 fysiske/lesbare sider, ingen ulesbare sider, 15 614 tegn. Job Object, 512 MiB og 10 sekunders grense var aktive. Første CLI-kjøring: 0,5307 s, topp 36 614 144 committed byte, worker avsluttet/innhentet. Målinger er denne kjøringens observasjoner. |
| Visuell kildekontroll | Alle 7 sider ble gjengitt lokalt med PDFium og visuelt inspisert. Tekstuttakets overskrifter, avsnitt, kriterier/vekter og siste sides karaktereksempel ble sammenholdt med sidene. Norske tegn var bevart; ingen U+FFFD i uttaket. |
| Eksisterende nettleserregresjon | `node tests/browser-sources.cjs`: 28 scenarier bestod, med syntetisk autentisering/modell. Inkluderer PDF-sidehull, innstilling/filbevaring, fokus, smal skjerm og genererings-/feilhåndtering. |
| Vanlig PDF gjennom app/API/grensesnitt | Separat lokal fixture med appens ekte PDF-adapter: HTTP200/no-store, Side1–7 og alt vist kildeinnhold likt med det kontrollerte uttaket. Fokus flyttet til kildeoverskriften; varsel om tekstdekning synlig. |
| Skadet PDF og nytt forsøk | HTTP422/invalid_pdf, synlig forståelig feil, ingen godtatt forhåndsvisning, valgt fil beholdt. Den gyldige PDF-en ble deretter godtatt igjen. |
| Utlogging og avgrensning | Utlogging krevde ny innlogging og tømte kildevisningen. Lokal fixture: 0 modellkall, 0 modellreservasjon, 0 eksterne nettleserforespørsler og 0 JavaScript-feil. |

De tre ekstra nettleserscenariene bestod. De brukte fake-auth i eksisterende
`tests/sources_browser_app.py`, en egen midlertidig server/ledig port og
separat syntetisk budsjett. Den vanlige appen ble ikke restartet eller endret;
ingen Supabase-, e-post-, ekte modell- eller privat lagringsoperasjon ble gjort.
Kontrollserverne er avsluttet.

## Context engineering – veiledet appflyt

Kilde: `C:\IBE160\Oppgave\Context engineering.pdf`, 71 994 byte.
SHA256: `e4340605de0f094f712244cb7082ab2215e6f78e4416768353781dae3de7bfa2`.
Lokal kontroll godtok 1 fysisk/lesbar side og 2 975 tegn uten sidehull.
Windows Job Object var aktivt, worker innhentet; første CLI-kjøring målte
0,2727 s og topp 35 278 848 committed byte. Gjengitt side ble visuelt inspisert
mot uttaket: overskrift, avsnittsrekkefølge, oppsummering, kilder og norske
tegn var bevart. Kilden er et kort dokument med enkel layout; bred PDF-dekning
kan ikke utledes fra denne ene prøven.

Computer Use kunne ikke kontrollere Firefox fordi URL-policyhåndheving ikke
støttes i Windows-nettleseren. Ingen innlogging eller live UI-handling ble
utført av agenten. Studenten gjennomførte derfor følgende i sin vanlige app:

| Steg | Brukerbekreftet resultat |
| --- | --- |
| Opplasting/kontroll | «teksten vises når jeg trykker kontreoller materiale». |
| Generering | «fungerer» etter instruks om én generering og kontroll av Sammendrag, Begreper, Flashcards og Quiz. Detaljert innhold/antall er ikke uavhengig inspisert. |
| Faglig kontroll | «ja» på at ett avdekket flashcardsvar støttes av PDF-en og refererer til Side1. Dette er ett kontrollert svar, ikke evaluering av alt generert innhold. |
| Lagring | «ja» på at materialet ble lagret med tittelen PDF-test Context engineering 21.11.2026 og at lagringsbekreftelse ble vist. |
| Gjenåpning/fremdrift | «ja» på flashcard2 og Quiz1 bevart med skjulte svar etter Ny økt og gjenåpning fra Mine dokumenter. |
| Sletting | «så ikke en bekreftelse, men ble slettet». Registreres som bortfall fra listen; synlig fullføringsmelding og fysisk leverandørsletting er ikke dermed bekreftet. |
| Utlogging/omlasting | «ja» på at privat innhold er borte og ny innlogging kreves. |

Budsjettjournalen ble inspisert før/etter: 11→12 forsøk og USD0,55→0,60
reservert av USD5, fortsatt ublokkert. Dette samsvarer med én ordinær generering;
reservasjon er ikke målt fakturert kostnad. Den automatiserte smoke-telleren
forble4. Ingen ekstra modellkall eller kvotenullstilling ble utført av agenten.

### Oppfølging av slettemeldingen

`app/static/workspace.js` setter `library-status` til fullføringsmelding og
flytter fokus til bibliotekoverskriften når serveren svarer `deleted`.
`node tests/browser-deletion.cjs` ble kjørt målrettet etter brukerobservasjonen:
alle7 syntetiske lokale nettleserkontroller bestod, inkludert synlig eksakt
fullføringsmelding, bortfall av testdata og fokus. Ingen feil er reprodusert
i denne lokale kjøringen, og ingen appkode er endret. Studenten presiserte
«mulig jeg bare overså den, vi kan gå videre». Ingen feil er bekreftet;
undersøk faktisk visning hvis observasjonen gjentar seg. Ikke gjenta sletting
av andre dokumenter som kontroll.

## Observerte begrensninger

- Uttaket plasserer PDF-ens bunntekst før sideinnholdet. Fysiske sidetall er
  bevart; dette er ikke en garanti om identisk visuell leserekkefølge.
- Tabelltekst fremkommer som løpende tekst. Kontrollen avdekket ingen feil
  i de inspiserte kriterie-/vektkoblingene, men strukturerte tabeller, figurer
  og OCR er fortsatt utenfor avtalt støtte. Andre oppsett må vurderes separat.
- Sensorveiledningen er et vanlig dokument med avsnitt og tabeller. Den lokale
  prøven alene verifiserer ikke faglig modellinnhold eller live-lagring.
  Den separate brukerprøven over dekker én kort PDF og ett kontrollert svar.
- Den ekstra PDF-prøven var lokal med syntetisk autentisering. Den erstatter
  ikke hosted-kontroll, ekte konto-/Storage-isolasjon eller fysisk to-enhetstest.

## Reproduksjon og lokal evidens

Fra repoet på Windows med eksisterende låste miljø:

```powershell
python scripts/pdf_probe.py 'C:\IBE160\Oppgave\Sensorveiledning IBE160 - Del 1 applikasjon og prosess.pdf'
node tests/browser-sources.cjs
```

Gjengitte sider, uttak, UI-skjermbilde, engangshjelper og resultat ligger lokalt
under ignorert `test-results/pdf-acceptance-2026-11-21/`. Engangshjelperen
`browser-real-pdf.cjs` tar den samme PDF-stien som argument og sammenligner
grensesnitt/API mot `sensor-extraction.json`; den er ikke en ny versjonert test.
PDFium/Pillow ble brukt i et separat uv-miljø kun til gjengivelse, uten endring
av prosjektets avhengigheter eller låsefiler.

## Gjenstående kontroll

- Ved gjentakelse: undersøk synlig slettemelding i faktisk appvisning. Den
  tidligere observasjonen er usikker; dokumentet er allerede fjernet.
- Breiere PDF-/lysbildeoppsett, full feilflyt, innlogget tilgjengelighet og
  full fysisk to-enhetskontroll har egne åpne punkter. Ingen full produksjons-
  eller fysisk filretensjonsakseptanse hevdes.
- Tidligere oppbrukt automatisert modell-smoke-ramme er ikke gjenåpnet.
  Brukerprøvens ordinære generering er separat dokumentert ovenfor.
