# Arbeidsnotater til refleksjonsrapporten

Opprettet: 01.11.2026. Sist oppdatert: 01.11.2026.

Dette er et løpende kildegrunnlag til [refleksjonsrapportmalen](reflection-report-template.md), ikke den ferdige rapporten. Notatene skiller mellom dokumenterte hendelser og spørsmål studenten må besvare med egne erfaringer. Tidligere arbeid er oppsummert i etterkant fra samtalen, prosjektfiler og Git-historikken; dette er ikke en fullstendig samtaleeksport.

## Slik vedlikeholdes notatet

- Legg til daterte hendelser når noe vesentlig skjer: beslutninger, KI-forslag, studentens korrigeringer, feil, tester og resultater.
- Beskriv hva som faktisk ble gjort, hvorfor og hvor dokumentasjonen finnes. Bruk commit-hash når den er kjent.
- Behold tidligere hendelser. Registrer endrede beslutninger som nye hendelser med begrunnelse.
- Ikke dikt opp tidsbesparelser, følelser, læringsutbytte, testresultater eller verktøybruk. Studentens egne refleksjoner merkes separat.
- Bevar originale prompter separat når mulig. Korte utdrag nedenfor erstatter ikke full samtalehistorikk. Ikke legg API-nøkler, private opplysninger eller kursmateriale uten avklart delingsrett i notatet.

## Status ved opprettelse

AI Study Buddy er et individuelt IBE160-prosjekt. Målet er å gjøre studentens tekst eller tekstbaserte PDF om til sammendrag, begreper, flashcards og quiz med kildehenvisninger. Omtrentlig innleveringsdato er 15. desember 2026, med ønsket ferdig kjerne rundt 1. desember.

Brief, PRD og UX er bearbeidet. En lokal klikkbar prototype bruker faste eksempeldata. Den har ingen backend, ekte KI-generering eller PDF-uttrekking. Arkitekturarbeidet er startet som arbeidsflyt, men teknologistakk, KI-leverandør og API-tilgang er ikke besluttet. Innlogging i Codex dokumenterer ikke at appen har API-tilgang.

## Dokumentasjon å vise til

| Kilde | Hva den kan underbygge |
| --- | --- |
| [Brief](../.docs/planning-artifacts/briefs/brief-G79-hansen-2026-09-26/brief.md) | Problem, målgruppe, avgrensninger og kvalitetsmål. |
| [Faglærerens tilbakemelding](../.docs/planning-artifacts/briefs/brief-G79-hansen-2026-09-26/tilbakemelding-product-brief.md) | Ekstern tilbakemelding og begrunnelse for revisjon. |
| [Utviklingsplan](../.docs/planning-artifacts/briefs/brief-G79-hansen-2026-09-26/development-plan.md) | Små utviklingstrinn, tidlig PDF-eksperiment og kontrollpunkter. |
| [PRD](../.docs/planning-artifacts/prds/prd-G79-hansen-2026-09-26/prd.md) | Krav og konkrete akseptansesjekker, FR-1–FR-9 og NFR-1–NFR-5. |
| [Arkitekturhandoff fra PRD](../.docs/planning-artifacts/prds/prd-G79-hansen-2026-09-26/addendum.md) | Tekniske valg som bevisst er utsatt. |
| [Visuell design](../.docs/planning-artifacts/ux-designs/ux-G79-hansen-2026-11-01/DESIGN.md) og [brukeropplevelse](../.docs/planning-artifacts/ux-designs/ux-G79-hansen-2026-11-01/EXPERIENCE.md) | Besluttet utseende, brukerflyt, tilstander og tilgjengelighet. |
| [Klikkbar prototype](../.docs/planning-artifacts/ux-designs/ux-G79-hansen-2026-11-01/.working/key-study.html) | Lokal demonstrasjon med faste eksempeldata. |
| [UX-kontrollrapport](../.docs/planning-artifacts/ux-designs/ux-G79-hansen-2026-11-01/validation-report.md) | Funn, rettinger og grensene for gjennomført kontroll. |
| [Sesjonslogger](../.logs/fredrik/) | Oppgaver, fremgangsmåte, resultater og åpne punkter. |

Beslutningsloggene `.memlog.md` i brief-, PRD- og UX-mappene gir mer detaljert historikk. Git viser hva som ble endret; loggene forklarer mer av hvorfor.

## 01.11.2026 – Revidering etter faglærerens tilbakemelding

**Hendelse:** Faglæreren beskrev briefen som et godt utgangspunkt med behov for justeringer. Hovedpunktene var et konkret problem og en primærbruker, ærlig differensiering fra vanlig chatbotbruk, begrunnede avgrensninger og én mulig utvidelse.

**KI-bidrag:** Assistenten sammenlignet briefen med tilbakemeldingen og oppdaterte brief, utviklingsplan og PRD etter studentens instruks.

**Studentens styring:** Studenten ba om at de fire foreslåtte forbedringspunktene skulle gjennomføres. Kjernen ble beholdt; automatisk rettet flervalgsquiz ble plassert som valgfri utvidelse etter at hovedkravene fungerer.

**Relevant i rapporten:** 2.2 Arbeidsmetodikk, 2.4 Planlegging, 4.2 Pålitelighet og 6.2 Validering av KI-forslag.

**Egen refleksjon – fylles ut av studenten:** Hvordan påvirket tilbakemeldingen forståelsen din av hva en god plan må inneholde? Var det enkelt å vurdere KI-ens forslag til avgrensning?

## 01.11.2026 – PRD gjennom konkrete avklaringer

**Hendelse:** Kravene ble avklart trinnvis. Studenten besluttet blant annet én aktiv inndatamåte, valgfritt fagfelt, norsk/kort som standard og én handling som lager alle fire læringsdelene. Svar skal være skjult til studenten ber om dem.

Studenten avklarte også at feil skal bevare materiale og innstillinger, at antall oppgaver skal følge kildegrunnlaget, og at utilstrekkelig materiale skal forklares fremfor å fylles med oppdiktet innhold.

**Konkret kontrollvalg:** Foreløpig maks 40 fysiske PDF-sider og 30 000 tegn, også for tekst hentet ut fra PDF. Overskridelser skal avvises uten automatisk kutting. Delvis lesbare PDF-er skal beholde opprinnelige sidenumre og oppgi hvilke sider som ikke kunne leses.

**KI-feil og retting:** Sluttkontrollen fant at formuleringene i NFR-2 og NFR-3 fortsatt var utdaterte forslag, selv om akseptansesjekkene beskrev de avklarte kravene. Formuleringene ble rettet før PRD-en ble ferdigstilt. Dette viser at en KI-oppsummering om at en endring er gjort må kontrolleres mot selve filen.

**Spor:** Commit `e0b56d0` – «Ferdigstill PRD for AI Study Buddy».

**Relevant i rapporten:** 3.3 KI-spesifikke utfordringer, 4.1/4.2 Kvalitet og pålitelighet, 6.1 Vedlikehold.

**Egen refleksjon:** Hvilke avklaringer tok du selv? Hva måtte du forstå for å avgjøre om kravene var riktige og realistiske?

## 01.11.2026 – Studenten styrte UX gjennom prototypen

**Hendelse:** Studenten valgte lys bakgrunn, mørk tekst, diskret blå aksent, tydelige overskrifter og god avstand. Materiale og innstillinger ble plassert over fire resultatfaner, med Sammendrag valgt etter generering.

Flashcards og quiz viser ett element om gangen, med teller, navigasjon og skjult svar/fasit. Fanebytte skal bevare plassering og viste svar. Kildehenvisningen vises sammen med svaret.

**Iterasjoner etter visuell gjennomgang:**

- Materialepanelet ble mer kompakt uten mindre tekst.
- Stor demoboks ble erstattet av diskret «Demo – eksempeldata» ved tittelen.
- «Generer» ble endret til «Lag læringsmateriale», med forklarende hjelpetekst.
- «Ny økt» fikk hjelpetekst om at materiale og resultater tømmes.
- Først skulle bare kildeteksten foldes sammen. Studenten endret dette til hele panelet etter vellykket generering, med «Vis/rediger» for å åpne igjen. Panelet skal være åpent før generering og ved feil.

**KI-bidrag:** Assistenten laget HTML/CSS/JavaScript-prototypen og oppdaterte den etter studentens beslutninger. Studenten ba uttrykkelig om faste eksempeldata, ingen backend/KI-integrasjon og ingen pakkeinstallasjon.

**Relevant i rapporten:** 2.4 Utvikling, 4.1 Effektivitet, 4.2 Kreativitet og 5.1 Ansvar.

**Egen refleksjon:** Var det lettere å oppdage behov når du kunne se og klikke i prototypen enn ved å lese kravene? Hvilke endringer kom fra din egen vurdering?

## 01.11.2026 – Kontroll av kravdekning og tilgjengelighet

**Hendelse:** Kravdekning og tilgjengelighet ble gjennomgått av separate KI-agenter, med etterfølgende rettinger. Flere KI-vurderinger er ikke en uavhengig menneskelig kvalitetssikring.

**Konkrete funn og løsninger:**

| Funn | Retting |
| --- | --- |
| Fokus kunne bli liggende på en skjult knapp når materialepanelet ble foldet sammen. | Fokus flyttes til synlig «Vis/rediger». |
| Åpning av hele panelet kunne etterlate kildeteksten skjult i en ekstra sammenfolding. | Kildeteksten åpnes når panelet utvides. |
| Kortnavigasjon flyttet fokus til motsatt knapp uten å kunngjøre nytt element. | Brukbar fokusplassering og kunngjøring av kort/spørsmål og plassering. |
| Overskriftsraden kunne bli for bred i et smalt vindu. | Raden kan brytes over flere linjer. |
| Feilmelding var ikke knyttet til det ugyldige feltet. | Feltet får ugyldig-status, kobling til feilmeldingen og fokus. |

**Gjennomførte kontroller:** JavaScript-syntaks, `git diff --check`, lokale dokumentlenker og beregnede kontrastforhold. Node-kontroller med en enkel DOM-stub kontrollerte blant annet oppstart, lasting/suksess, fokus, uavhengige faneplasseringer, viste svar, tilbakestilling og avvisning av tom/for lang tekst.

**Viktig begrensning:** DOM-stubben er ikke en ekte nettleser. Full tastatur-, zoom- og skjermlesertesting er ikke dokumentert som gjennomført. Kontrollene beviser heller ikke at en fremtidig KI-generering blir faglig korrekt.

**Tillegg etter studentens ønske:** Klikkbare eksempeltilstander for feil med «Prøv igjen», PDF med delvis/ingen lesbar tekst og utilstrekkelig materiale. Tilstandsvelgeren er tydelig adskilt fra produktgrensesnittet. Tilstandssjekkene ble utvidet og bestod.

**Spor:** Commit `74c660e` – «Ferdigstill UX for AI Study Buddy».

**Relevant i rapporten:** 3.1 Tekniske utfordringer, 4.2 Pålitelighet, 5.1 Kvalitetsansvar og 6.2 Beste praksis.

**Egen refleksjon:** Hvilke funn ville du oppdaget selv? Hva betyr det at en test består, og hva sier den ikke noe om?

## Prosess, personvern og verktøy – fakta å bygge videre på

- Arbeidet er individuelt. Ikke beskriv oppgavefordeling i en studentgruppe som om det har skjedd.
- Git/GitHub brukes til versjonering. BMAD brukes til planlegging og dokumentasjon, og Codex til KI-assistanse. Den lokale prototypen bruker HTML, CSS og JavaScript. Endelig appstakk er ennå ikke valgt.
- Lokale sesjonslogger og beslutningslogger gjør prosessen mer sporbar, men er ikke komplette originale promptlogger.
- Midlertidige økter uten lagret historikk/deling er valgt for første versjon. Faktisk sletting, logging og eventuell leverandørbehandling må kontrolleres i implementeringen.
- Prototypen bruker eksempeldata uten KI-kall. Ikke skriv at ekte kursmateriale allerede er analysert av et modell-API.
- Leverandør/modell, API-tilgang og budsjett gjenstår. Ikke oppgi en tjeneste eller kostnad som allerede brukt uten dokumentasjon.
- 01.11.2026: Studenten godkjente versjonering av det delte BMAD-oppsettet: 242 filer i `.agents/` og 20 i `_bmad/`. Personlige konfigurasjoner og genererte renderfiler holdes fortsatt utenfor Git. Dette bevarer rammeverk, maler og arbeidsflyter brukt i prosjektet. Git-kontrollen viste noen eksisterende mellomroms-/linjeskiftvarsler i installerte BMAD-filer; filene ble beholdt uendret.

## Korte originale promptutdrag fra denne samtalen

Disse er et utvalg, ikke alle utviklingssteg. Ta vare på hele relevante samtaler der det er mulig.

> Bruk key-study.html som lokal, klikkbar UX-prototype. Oppdater den etter hver avtalte BMAD-beslutning. Bruk eksempeldata uten backend eller AI-integrasjon. Endre bare relevante deler, ikke installer pakker, og oppsummer endringene kort.

> Legg hjelpeteksten «Ny økt tømmer materialet og resultatene.» ved «Ny økt». Behold knappen visuelt underordnet «Lag læringsmateriale».

> Ja. Lag klikkbare eksempeltilstander for feil med «Prøv igjen», PDF-varsler og utilstrekkelig materiale i eksisterende prototype. Bruk faste eksempeldata, uten backend. Hold tilstandsvelgeren tydelig adskilt fra selve produktgrensesnittet.

## Ta vare på dette i kommende arbeid

- Arkitektur: alternativer som vurderes, studentens valg og hva som verifiseres mot dokumentasjon.
- Implementering: faktiske feil, hvordan de ble oppdaget, KI-forslag som ble forkastet eller korrigert og resultater av kontroller.
- KI-integrasjon: faktisk leverandør/modell, hvilke data som sendes, kostnader og testfunn.
- Kildekvalitet: tre dokumenter, fem begreper valgt på forhånd per dokument, faktastøtte, henvisninger og dekning. Dette er planlagt, ikke gjennomført ennå.
- Studentens egen forståelse: noter fortløpende hva du kan forklare selv og hva du fortsatt trenger hjelp til.
- Ikke anslå timer spart uten egne målinger eller tydelig merking som subjektivt anslag.

## Mal for neste hendelse

### DD.MM.ÅÅÅÅ – Kort tittel

**Hendelse og mål:**

**KI-forslag/bidrag:**

**Studentens beslutning eller korrigering:**

**Kontroll og observert resultat:**

**Dokumentasjon/commit/prompt:**

**Relevant del av rapportmalen:**

**Studentens egen refleksjon:**
