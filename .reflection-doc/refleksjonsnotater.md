# Arbeidsnotater til refleksjonsrapporten

Opprettet: 01.11.2026. Sist oppdatert: 11.11.2026.

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

### 10.11.2026 – Samlet arkitekturutkast med kontroll

Studenten ba om et samlet utkast med forslag for valgene som gjenstår. Det ble laget en teknisk arkitekturkontrakt, en kort forklaring til student/sensor og et eget kildenotat. Vedtatte valg er markert separat fra foreslåtte mekanismer for innloggingstilstand, fremdrift, PDF og hosting. Utkastet innfører ikke faktisk backend eller eksterne tjenester.

En mekanisk arkitekturlinter ga null funn. Separate KI-agenter vurderte kravdekning, teknologikilder og om selvstendig bygde deler kunne følge dokumentet og likevel bli inkompatible. Funn gjaldt blant annet passordgjenopprettingens callback, koblingen mellom generering og senere eksplisitt lagring, databasetransaksjoner, filenes slettestatus og samtidige fremdriftsoppdateringer. Utkastet ble presisert med en felles callback-flyt, signert genereringskvittering, transaksjonsgrenser og sporbare filoperasjoner. Dette er dokumentkontroll, ikke verifisert implementering eller sikkerhetssertifisering.

Dokumentasjon: [arkitekturutkast](../.docs/planning-artifacts/architecture/architecture-G79-hansen-2026-11-01/ARCHITECTURE-SPINE.md), [enkel forklaring](../.docs/planning-artifacts/architecture/architecture-G79-hansen-2026-11-01/architecture-explained.md), [kilder](../.docs/planning-artifacts/architecture/architecture-G79-hansen-2026-11-01/research-notes.md).

**Egen refleksjon:** Hvilke tekniske valg kan du nå forklare selv? Hjalp den enkle forklaringen deg å forstå hvorfor innlogging og lagring krever mer enn en knapp i prototypen?

### 10.11.2026 – «Mine dokumenter» i prototypen

Studenten ba om å gå videre med dokumentoversikten. Prototypen viser flere lokalt lagrede eksempler med tittel, dato og fremdrift. «Åpne» henter riktig dokument og kort-/spørsmålsplassering. «Slett» viser en bekreftelse med dokumentnavn, avbryt og endelig sletting; sletting av aktivt dokument tømmer også arbeidsvisningen. Tekst som brukes i oversikten escapes, slik at dokumentnavn ikke tolkes som HTML. Node-kontroller for tom liste, flere dokumenter, gjenåpning, avbryt/slett og tømming av aktiv visning bestod. Fortsatt ingen backend, varig lagring eller faktisk tilgangskontroll.

### 10.11.2026 – E-post og passord valgt

Studenten godkjente «Opprett konto», «Logg inn», «Glemt passord» og «Logg ut» med Supabase Auth. Offisiell dokumentasjon for passordbasert innlogging ble kontrollert. Kravene beskriver også gyldig gjenopprettingsøkt, feil/utløpt lenke og generisk svar som ikke avslører om e-postadressen finnes. Prototypen demonstrerer handlingene med faste, skrivebeskyttede eksempelopplysninger. Den sender ingen e-post og oppretter ingen konto. Utlogging tømmer aktiv arbeidsflate og lokal eksempeltilstand. Node-tilstandssjekkene bestod; det er ikke en test av ekte autentisering.

### 10.11.2026 – Supabase valgt

Studenten godkjente Supabase til innlogging (Auth), database (Postgres) og privat fillagring (Storage). Formålet er å gjenbruke samme konto, innhold og fremdrift på flere enheter uten å bygge alle disse tjenestene selv. FastAPI og det eksisterende grensesnittet beholdes. Planen skiller nå mellom en hostet live-app og lokal demomodus for sensor. Kravene omfatter tester for samme bruker på en annen enhet og avvisning av andre brukere også ved direkte forespørsler til filer og data.

Valget er dokumentert, men ingen Supabase-konto/prosjekt, tabeller eller tilgangsregler er opprettet ennå. Innloggingsmetode, hosting, region, kostnadsrammer og detaljert datamodell gjenstår. At en tjeneste tilbyr tilgangsregler betyr ikke at appens data er beskyttet før reglene er konfigurert og testet.

### 10.11.2026 – Tilgang fra flere enheter

Studenten foretrekker å åpne eget lagret innhold fra flere enheter. Arkitekturen må derfor ha felles innlogging og lagring som ikke er bundet til én PC. Supabase Auth, Postgres og privat Storage ble undersøkt som et samlet forslag i offisiell dokumentasjon. Dette er ennå ikke et vedtatt leverandørvalg. Praktisk tilgang gjennom en vanlig nettadresse vil også kreve hosting av appen; lokal demomodus for sensor beholdes som eget krav. Ingen konto, skytjeneste, betalt abonnement eller publisering er opprettet ved denne avklaringen.

Kilder: [Supabase introduksjon](https://supabase.com/docs/guides/getting-started/the-supabase-way-to-build), [radbasert tilgang](https://supabase.com/docs/guides/database/postgres/row-level-security), [tilgang til lagrede filer](https://supabase.com/docs/guides/storage/security/access-control).

### 10.11.2026 – Fortsette der studenten slapp

Studenten valgte at gjenåpning av lagrede dokumenter skal gjenoppta samme flashcard og quizspørsmål. Fremdriften skal knyttes til riktig bruker og dokument. PRD-en har fått konkrete sjekker for gjenåpning, restart og at fremdrift ikke blandes mellom dokumenter/kontoer. Prototypen kan demonstrere gjenåpning av et lagret eksempel etter «Ny økt» med en separat prototypekontroll. Dette er fortsatt bare tilstand i nettleserminnet; varig lagring etter side-/serverrestart er et krav til den fremtidige appen. Tidspunkt for lagring av fremdrift og behandling av tidligere viste svar avklares videre i arkitekturen.

### 10.11.2026 – Studenten velger eksplisitt lagring

Studenten godkjente en «Lagre»-knapp fremfor automatisk lagring. Generering skal ikke i seg selv lagre innholdet permanent. Kilde, innstillinger og læringsmateriale lagres samlet når brukeren velger det; «Ny økt» tømmer arbeidsflaten uten å slette lagrede dokumenter. Krav og akseptansesjekker er oppdatert. Prototypen har en klikkbar demonstrasjon med fast eksempeltilstand, men ingen faktisk varig lagring eller innlogging ennå. Eksisterende tilstandssjekker bestod etter endringen.

### 10.11.2026 – Omfanget utvidet med innlogging og lagring

Studenten ønsket at opplastede dokumenter og læringsmateriale skulle beholdes mellom besøk, og ba om funksjonene etter å ha fått forklart ekstraarbeidet: innlogging, lagring, «Mine dokumenter», åpning, sletting og kontroll av at brukere ikke får tilgang til hverandres innhold. Dette overstyrer tidligere avgrensning til midlertidige økter uten database.

PRD-en ble åpnet igjen som utkast, FR-8 ble endret og FR-10–FR-12 lagt til. Brief, utviklingsplan og arkitekturgrunnlag ble samkjørt. UX ble markert som utkast for nye innloggings-/lagringsflater; den eksisterende prototypen demonstrerer fortsatt den tidligere arbeidsflaten. Tidligere godkjenninger og kontroller validerer ikke de nye funksjonene. Ingen innlogging eller lagring er implementert ennå.

«Ny økt» og «Slett dokument» har nå ulike betydninger: førstnevnte tømmer aktiv arbeidsflate, mens sistnevnte fjerner lagret materiale. Automatisk eller eksplisitt lagring og teknisk lagringsløsning gjenstår. CV-spesifikk behandling er ikke lagt til som eget bruksområde.

**Egen refleksjon:** Hvorfor ble lagring viktig for deg etter prototypen? Hvordan påvirker endringen gjennomførbarhet, testing og din forståelse av tilgangskontroll?

### 10.11.2026 – Teknologistakk valgt

Studenten godkjente Python + FastAPI med vanlig HTML/CSS/JavaScript. Begrunnelsen er å bygge videre på den gjennomgåtte prototypens utseende og oppførsel, i ett lokalt prosjekt uten database. Streamlit var alternativet med mer grensesnitt direkte i Python; FastAPI-alternativet krever mer kode mellom nettleser og backend. Beslutningen velger stakk, men innebærer ikke at backend er implementert eller pakker installert. Eksakte versjoner, PDF-bibliotek og KI-leverandør gjenstår.

**Egen refleksjon:** Hvordan vurderte du fordelen ved å beholde prototypen opp mot at løsningen bruker både Python og JavaScript?

### 01.11.2026 – Arkitekturarbeidet startet

Arbeidsformen er én beslutning om gangen, med kort teknisk arkitektur og enkel forklaring til student/sensor. Første valg er teknologistakk. Tidligere foreslått Python/Streamlit sammenlignes med Python/FastAPI som serverer HTML/CSS/JavaScript, siden en godkjent klikkbar prototype nå finnes. Streamlits øktmodell og faner og FastAPIs støtte for statiske filer ble kontrollert mot offisiell dokumentasjon. Ingen stakk er valgt, ingen pakker er installert og ingen backend er implementert på dette tidspunktet.

Kilder: [Streamlit Session State](https://docs.streamlit.io/develop/concepts/architecture/session-state), [Streamlit tabs](https://docs.streamlit.io/develop/api-reference/layout/st.tabs), [FastAPI Static Files](https://fastapi.tiangolo.com/tutorial/static-files/). Studentens valg og begrunnelse registreres når beslutningen tas.

- Arkitektur: alternativer som vurderes, studentens valg og hva som verifiseres mot dokumentasjon.
- Implementering: faktiske feil, hvordan de ble oppdaget, KI-forslag som ble forkastet eller korrigert og resultater av kontroller.
- KI-integrasjon: faktisk leverandør/modell, hvilke data som sendes, kostnader og testfunn.
- Kildekvalitet: tre dokumenter, fem begreper valgt på forhånd per dokument, faktastøtte, henvisninger og dekning. Dette er planlagt, ikke gjennomført ennå.
- Studentens egen forståelse: noter fortløpende hva du kan forklare selv og hva du fortsatt trenger hjelp til.
- Ikke anslå timer spart uten egne målinger eller tydelig merking som subjektivt anslag.

## Beslutninger og kontroll 11.11.2026

### 11.11.2026 – Første kjørbare demo og uavhengig kontroll

**Dokumentert resultat:** FastAPI serverer nå den faktiske studiedemoen og et API for et navngitt syntetisk eksempel. Sammendrag, begreper, flashcards og quiz hentes samlet fra backend. Skjulte svar/referanser, separate posisjoner, fanebytte, materialpanel, nullstilling og feilmeldinger er implementert. Egen tekst/PDF, KI, konto og varig lagring er fortsatt senere arbeid.

**Kontroll og rettelser:** 30 API-/kontrakttester bestod. Tre uavhengige kodelinser fant blant annet manglende tidsavbrudd og manglende dekning av feil ved første innlasting og komplette, men semantisk ugyldige svar. Etter retting bestod 11 nettleserscenarier i Edge, med virkelige 15-sekunders tidsavbrudd, ugyldige svar, retry og forsinkede svar etter reset. Kontrollen omfattet 320/390/480 piksler og 200 % layoutzoom; skjermbilder ble sett på. Dette erstatter ikke manuell skjermleser-/WCAG-kontroll. En upstream TestClient/httpx-advarsel er registrert, uten testfeil.

**Ytterligere arkitekturfunn:** Full-diff-kontrollen presiserte hvordan allerede opptatt eksplisitt lagring kan gjenopptas etter ny innlogging, og hvordan serveren opphever gamle signerte genereringskvitteringer. Dette er dokumentregler som må testes i senere live-oppgaver, ikke funksjoner denne demoen beviser.

**Kilder:** [Byggespesifikasjon og triage](../.docs/implementation-artifacts/spec-1-1-run-the-four-part-study-demo.md), [kvitteringsavklaring](../.docs/planning-artifacts/architecture/architecture-G79-hansen-2026-11-01/reviews/resolution-receipt-admission.md), [oppstart](../README.md).

**Egen refleksjon (ubesvart):** Hvorfor var vellykkede tester av normalflyten utilstrekkelig før oppstartsfeil og tidsavbrudd også ble testet?

### 11.11.2026 – Arkitektur ferdigstilt og første bygg planlagt

**Dokumentert hendelse:** Studenten ba «kjør disse punktene» etter anbefalingen om samlet arkitekturgjennomgang, utviklingsoppgaver, sprintplan og første kjørbare demo. Det gir grunnlag for å avgjøre rutinemessige tekniske forslag og fortsette uten nye delgodkjenninger, innenfor avtalt omfang.

**KI-bidrag og kontroll:** BMAD-arkitekturen og revidert PRD/UX er samkjørt og ferdigstilt som planleggingsgrunnlag. Uavhengig krav-/rubrikk-, teknologi- og adversariell gjennomgang avdekket blant annet forskjellen mellom første Lagre og erstatningslagring, lokal utlogging ved leverandørfeil og filsporing ved avbrutt sletting. Kravene er presisert og etterkontrollert. Arkitekturlinter: 0 funn; 22 relative lenker kontrollert. Dette er dokumentkontroller, ikke live sikkerhetstester.

**Resultat:** Fire epics med 14 konkrete stories og sprintstatus er opprettet. Story 1.1 er startet som lokal FastAPI-demo med faste eksempeldata. Ekte innlogging, varig lagring, PDF, modellvalg og publisering er fortsatt senere arbeid med egne kontrollpunkter. Den historiske utviklingsrekkefølgen er erstattet av den samlede backloggen, uten å fjerne kjernekravene.

**Kilder:** [Arkitekturkontroll](../.docs/planning-artifacts/architecture/architecture-G79-hansen-2026-11-01/review-summary.md), [epics](../.docs/planning-artifacts/epics.md), [implementeringsklarhet](../.docs/planning-artifacts/implementation-readiness.md).

**Egen refleksjon (ubesvart):** Hvilken verdi hadde kontrollen av avbrutt lagring/sletting før funksjonene ble kodet?

### 11.11.2026 – Fortsette på en annen enhet uten overskriving

**Dokumentert hendelse:** Studenten ønsket å fortsette på en annen enhet og svarte «ja» til at en utdatert fane ikke skal overskrive nyere fremdrift. KI foreslo meldingen «Fremdriften er endret på en annen enhet» med «Hent siste fremdrift», og synlig status når nettverksfeil hindrer lagring.

**Resultat:** Brukeroppførselen er vedtatt i AD-7, forklaring, PRD og EXPERIENCE. Akseptansesjekken beskriver to enheter, avvist utdatert oppdatering og nettverksfeil. Bare bekreftede oppdateringer garanteres på tvers av enheter. Teknisk revisjons-/låse-/retryprotokoll er fortsatt et forslag. Ingen kode eller skytjeneste endret.

**Egen refleksjon (ubesvart):** Hvorfor bør en gammel nettleserfane hente siste fremdrift før den lagrer videre?

### 11.11.2026 – Ny innlogging etter serverrestart valgt

**Dokumentert hendelse:** KI anbefalte midlertidig backend-styrt innloggingstilstand i serverminnet for førsteversjonen. Studenten svarte «kjør anbefalt løsning». Serverrestart eller oppdatering krever ny innlogging, mens lagrede dokumenter, læringsmateriale og synkronisert fremdrift beholdes i Supabase. Flere enheter kan være innlogget samtidig.

**Resultat:** Valget er registrert i beslutningsloggen, AD-3, studentforklaringen, PRD og EXPERIENCE. PRD beskriver kontroll av avvist gammel økt og gjenåpning etter ny innlogging. Valget gjelder øktens levetid; detaljer for sikkerhet, gjenoppretting og tidsgrenser er fortsatt forslag. Ingen backend implementert eller skytjeneste opprettet.

**Egen refleksjon (ubesvart):** Hva er forskjellen mellom at innloggingen forsvinner og at et lagret dokument slettes?

### 11.11.2026 – Skjulte svar ved gjenåpning valgt

**Dokumentert hendelse:** Studenten svarte «ja» til forslaget om at svarene skjules når et lagret dokument åpnes igjen, samtidig som riktig flashcard og quizspørsmål gjenopptas. Fanebytte under samme besøk beholder allerede viste svar.

**Resultat:** AD-7, studentforklaringen, PRD, EXPERIENCE og beslutningsloggen er oppdatert. Akseptansesjekken krever at begge svar er skjult ved gjenåpning og at plasseringene beholdes. Dette er dokumentert oppførsel for senere implementering; ingen kode endret.

**Egen refleksjon (ubesvart):** Hvordan kan skjulte svar støtte øving når du fortsetter på et lagret dokument?

### 11.11.2026 – Automatisk lagring av fremdrift valgt

**Dokumentert hendelse:** KI foreslo å lagre kort- og quizplassering automatisk når dokumentet allerede er lagret. Studenten svarte «jeg vil ha den ja». Dokument, innstillinger og nytt læringsmateriale krever fortsatt eksplisitt «Lagre»; fremdrift i ulagret materiale er bare i nettleserminnet.

**Resultat:** Valget er registrert i arkitekturens beslutningslogg og AD-7, studentforklaringen, PRD og EXPERIENCE. Dette er en krav-/arkitekturbeslutning, ikke implementert skylagring. Synkroniseringsmekanisme og synlighet av svar ved gjenåpning er fortsatt åpne forslag.

**Egen refleksjon (ubesvart):** Hvordan skiller du mellom å lagre læringsmaterialet og å huske hvor langt du har øvd?

## Mal for neste hendelse

### DD.MM.ÅÅÅÅ – Kort tittel

**Hendelse og mål:**

**KI-forslag/bidrag:**

**Studentens beslutning eller korrigering:**

**Kontroll og observert resultat:**

**Dokumentasjon/commit/prompt:**

**Relevant del av rapportmalen:**

**Studentens egen refleksjon:**
