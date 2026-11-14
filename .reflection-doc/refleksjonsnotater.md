# Arbeidsnotater til refleksjonsrapporten

Opprettet: 01.11.2026. Sist oppdatert: 12.11.2026.

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

## 12.11.2026 – Neste oppgave konkretisert som PDF-eksperiment

**Dokumentert hendelse:** Studenten ba «fortsette på prosjekt study buddy». Assistenten leste siste logg og sprintstatus og konkretiserte neste planlagte oppgave, Story 1.2. En kontekstagent samlet relevante Epic 1-krav. Demoens status er fortsatt `review`; studentens godkjenning er ikke antatt.

**KI-forslag:** Et lokalt eksperiment med syntetiske PDF-er skal kontrollere opprinnelige sidenumre og grenser for sider, tegn, filstørrelse, tid og minne før PDF-opplasting integreres. 10 sekunder og 512 MiB er foreslåtte eksperimentgrenser, ikke målte resultater. pypdf-dokumentasjonen advarer om stor minnebruk; Python-modulen `resource` kan ikke brukes som en generell Windows-løsning. Kilder og akseptansekriterier finnes i [spesifikasjonen](../.docs/implementation-artifacts/spec-1-2-verify-physical-pdf-pages-before-integration.md).

**Kontroll og avgrensning:** `git diff --check` bestod. Ingen PDF-pakker installert, funksjon implementert eller funksjonstester kjørt i denne planleggingsøkten. Spesifikasjonen er `draft` ved BMADs godkjenningspunkt.

**Egen refleksjon (ubesvart):** Hvorfor må et PDF-eksperiment teste minnebruk i tillegg til filstørrelse og korrekte sidetall?

## 12.11.2026 – PDF-eksperiment implementert og kontrollert

**Studentens styring:** Studenten godkjente planen med «kjør». Det autoriserte lokal implementering og testing av Story 1.2, uten å godkjenne demoen på studentens vegne eller opprette skytjenester.

**Dokumentert resultat:** Et lokalt Python-verktøy bruker pypdf 7.0.1 i en egen Windows-prosess. Originale fysiske sidetall beholdes, blanke/bildesider oppgis, og grensene på 40 sider, 30 000 Unicode-kodepunkter og 10 MiB kontrolleres uten avkorting. Prosessen har en faktisk Windows-minnegrense på 512 MiB forpliktet minne og en tidsgrense på 10 sekunder. Kommandolinjeutdata viser metadata, ikke kildetekst eller filnavn. Verktøyet er et eksperiment og er ikke koblet til appens opplasting.

**KI-feil og retting:** Første kjøring viste at Windows' Python-miljø bruker en ekstra oppstartsprosess som kolliderte med grensen på én prosess. Oppstart via basisinterpreteren løste dette, mens biblioteket fortsatt lastes etter bekreftet isolasjon. Hovedagentens kontroll fant at én enkelt read-operasjon ikke håndterte strømmer som leverer data i små biter; lesingen ble rettet og testet mot omgåelse av bytegrensen.

**Uavhengig kontroll:** Tre KI-gjennomlesere vurderte endringen. Oppfølgingen la til et dekningsvarsel også på sider med både tekst og bilde, riktig feilkode ved isolasjonsfeil, målbare JUnit-egenskaper og en ekte PDF med lesbar side 1 og parserfeil på side 2. Denne feilen skal avvise hele dokumentet. Flere KI-vurderinger erstatter ikke studentens vurdering.

**Faktisk kontrollresultat:** Hovedagentens endelige kjøring ga 62 beståtte tester og én plattformspesifikk test hoppet over, med en eksisterende TestClient/httpx-advarsel. Testene omfatter den uendrede demoens API-kontrakter og PDF-eksperimentet. Låst installasjon, CLI-hjelp og diff-kontroll bestod. Komprimert stresstest ble stoppet innenfor ressursgrensene; dette er ikke bevis for korrekt uttrekk fra alle PDF-er.

**Begrensninger og spor:** Bare syntetiske PDF-er på denne Windows-maskinen er kontrollert. Typografi/leserekkefølge mot gjengitte sider, representative tillatte dokumenter og faktisk serverplattform må prøves før integrasjon. Se [rapporten](../.docs/implementation-artifacts/pdf-experiment.md) og [spesifikasjonens triage](../.docs/implementation-artifacts/spec-1-2-verify-physical-pdf-pages-before-integration.md). Ingen appfiler, kontoer eller eksterne tjenester ble endret.

**Egen refleksjon (ubesvart):** Hvorfor er en vellykket test med syntetiske filer utilstrekkelig til å hevde at alle forelesnings-PDF-er blir lest korrekt?

## 12.11.2026 – Innlogging planlagt og manglende Supabase-prosjekt avklart

**Studentens styring:** Studenten ba «kjøre neste steg» etter PDF-eksperimentet. På spørsmål om eksisterende Supabase-testprosjekt svarte studenten «Nei, det må opprettes». Dette dokumenterer manglende oppsett; gratisplan/konkret region er foreløpig foreslått, ikke opprettet eller godkjent.

**KI-bidrag:** Epic 2-kontekst, en [konkret innloggingsspesifikasjon](../.docs/implementation-artifacts/spec-2-1-sign-up-and-sign-in-securely.md) og [oppsettsveiledning](../.docs/implementation-artifacts/auth-setup.md) er utarbeidet. En egen kontekstagent samlet kravene, og en teknisk agent undersøkte stabil Supabase Python-SDK, isolert PKCE-lagring og sikker validering av identitet. Forslaget er et separat `studybuddy-test` på Free i konkret Frankfurt-region `eu-central-1`, med aktiverte e-postbekreftelser og begrensede testmottakere.

**Viktig kontrollfunn:** Offisiell dokumentasjon oppgir at standard SMTP bare sender til autoriserte teamadresser og for tiden er begrenset til to e-poster per time. Dette påvirker live-testing og er dokumentert, uten å foreslå at e-postbekreftelse deaktiveres. Stabil Python-SDK 2.34.1 ble valgt som teknisk utgangspunkt for senere installasjon, fremfor alfakode. Kildene er lenket i oppsettsveiledningen.

**Tilgang og avgrensning:** Forsøkt nettlesertilgang returnerte «The browser access host is unavailable»; kontroll av tilgjengelige flater viste heller ingen tilgjengelig native-pipe. Supabase-integrasjonen ble funnet i katalogen og foreslått, men var ikke installert/tilkoblet ved siste kontroll. Ingen konto, prosjekt, nøkkel, melding eller skytjeneste ble opprettet. Ingen appkode eller avhengigheter er endret, og nye innloggingstester er ikke kjørt. `git diff --check` bestod; spesifikasjonen står `draft` med oppsettsvalg til godkjenning.

**Egen refleksjon (ubesvart):** Hvorfor kan lokale tester med en simulert innloggingstjeneste ikke bevise at e-postbekreftelse og innlogging fungerer hos den faktiske leverandøren?

## 12.11.2026 – Innlogging implementert; kontrollpunkt før dagens avslutning

**Studentens styring:** Studenten svarte «godkjenner» til innloggingsplanen og Free/Frankfurt-oppsettet. Studenten opprettet deretter organisasjon/prosjekt manuelt, oppga prosjektadresse og publiserbar nøkkel, og sa at femtimerskvoten nesten var brukt opp og at dagen snart måtte avsluttes. Godkjenningen beholdes ved neste økt.

**Dokumentert implementering:** Supabase Python-SDK 2.34.1 er låst. Backend har validering av identitet, avgrensede minnebaserte økter, separate PKCE-forsøk, CSRF/Origin-vern, no-store og skjerming av kontrollverdier i logger. En norsk `/account`-side har konto/innlogging og feil-/bekreftelsestilstander. Demoen er beholdt uten krav om Supabase-konfigurasjon.

**Kontrollfunn og rettelser:** Hovedagenten fant at en ugyldig JSON-type i en legacy-nøkkel kunne gi feil fremfor avvist oppsett, at kodede callback-stier kunne omgå loggskjerming, og at null/ugyldige serversvar kunne gi fastlåst eller utrygg feilmelding. Dette ble rettet og testet. Nettlesertestene fant også behov for å rydde bort `#fragment` ved adresseendring uten sidelasting. En SDK-test brukte først feil form på signup-svaret; testdata ble korrigert mot det låste SDK-et.

**Faktisk verifikasjon:** Hovedagentens fulle kjøring ga **130 beståtte tester og én forventet plattformtest hoppet over**, med én eksisterende TestClient/httpx-advarsel, 47,18 sekunder. Implementeringsagenten kjørte 12 faktiske nettleserscenarier for konto og alle 11 demoscenarier; hovedagenten inspiserte skjermbilder for desktop og 200 % layoutzoom. SDK-testene bruker faktisk SDK med kontrollert HTTP-transport, ikke ekte kontoer.

**Supabase og lokale verdier:** Prosjektadressen og den publiserbare nøkkelen er bare lagt i ignorert `.env`; ingen databasesecret/service-role/passord er nødvendig eller lagt i repoet. En leseforespørsel til prosjektets offentlige Auth-innstillinger returnerte HTTP 200, e-post aktiv, e-postbekreftelse påkrevd og registrering tillatt. Det ble ikke opprettet konto eller sendt e-post i denne kontrollen.

**Avgrensning ved avslutning:** Studentens ønske om å runde av prioriteres. Story 2.1 står fortsatt `in-progress`: faktisk redirect-/maloppsett og registrering/e-postbekreftelse/innlogging i separate nettlesere samt den uavhengige kodegjennomgangen gjenstår. Ingen fullført sikkerhetsakseptanse er hevdet. Ingen videre funksjoner, betalte tjenester, publisering eller push ble startet. [Oppsett og neste kontroll](../.docs/implementation-artifacts/auth-setup.md) og [spesifikasjonen](../.docs/implementation-artifacts/spec-2-1-sign-up-and-sign-in-securely.md) er oppdatert.

**Egen refleksjon (ubesvart):** Hvordan skiller du mellom at en tjeneste svarer, at lokale tester består, og at hele den ekte innloggingsflyten er kontrollert?

## 13.11.2026 – Ekte innlogging gjort klar for manuell kontroll

**Studentens styring:** Studenten ba «kjør» etter at neste steg var forklart som Supabase-oppsett, faktisk registrering/bekreftelse/innlogging og uavhengig kodegjennomgang. Tidligere godkjenning ble beholdt.

**Observert kontroll:** Leverandørens offentlige Auth-innstillinger svarte igjen 200 med e-postbekreftelse påkrevd. Appen startet lokalt med ignorert `.env`, én prosess og uten reload. Kontosiden svarte 200; status viste tilgjengelig innlogging og ingen innlogget bruker. `no-store` og `no-referrer` var satt. Ingen konto ble opprettet eller e-post sendt i kontrollen. De 130 beståtte testene er fra 12. november, ikke en ny kjøring.

**Begrensning og neste brukertrinn:** Windows-verktøyet fikk ikke kontakt med native-pipen (`os error 2`), og ingen Supabase-administrasjon er tilkoblet. Studenten ble bedt om å lagre Site URL og callback-mønster i dashboardet. Denne endringen og ekte kontoflyt er foreløpig ubekreftet; Story 2.1 forblir under arbeid. Offisiell dokumentasjon for [returadresser](https://supabase.com/docs/guides/auth/redirect-urls) og [standard e-posttjeneste](https://supabase.com/docs/guides/auth/auth-smtp) ble kontrollert på nytt. Ingen erfaring eller godkjenning tilskrives studenten uten svar.

**Oppfølging samme dag:** Studenten svarte først «lagret» om returadressene og deretter «funka» på testen for registrering/e-postbekreftelse. Serveren viste én registrering med status 200 og én callback med 303. De undersøkte tilgangsoppføringene inneholdt ingen auth-querystrenger; bare tellinger ble skrevet ut ved kontrollen. Dette er et positivt første live-resultat, ikke full kontroll av isolasjon, avviste forsøk eller vanlig passordinnlogging. Studenten ble bedt om å teste innlogging i privat nettleservindu; resultatet er foreløpig ikke mottatt.

**Videre kontroll samme dag:** Studenten rapporterte «Skjema først, deretter innlogget» i privatvindu. Serveren viste login 200. Ved deretter bevisst feil passord rapporterte studenten den forventede trygge avvisningsmeldingen, og serveren viste login 401. Testene omfatter foreløpig én konto, ikke isolasjon mellom forskjellige brukere. Ingen testpassord eller rå kontrollverdier ble samlet inn.

**Tilgjengelige testere og videre avgrensning:** Studenten bekreftet at bare én konto er tilgjengelig. Test med to forskjellige ekte brukere er derfor ikke utført, og ingen ny bruker/invitasjon eller e-postleverandør ble opprettet. Ti HTTP-kontroller mot den kjørende appen bestod: isolert uautentisert cookie/CSRF-bootstrap, cookieflagg, personvernheadere, fravær av providertokens i bootstrap, avvisning av manglende/fremmed Origin, fremmed nettlesers CSRF, ugyldig skjema, ukjent callback og ukjent økt. Dette er ikke bevis for isolasjon av to autentiserte brukere. Studenten fikk en egen test for gjenbruk av den allerede brukte e-postlenken i privatvindu; resultat venter.

**Dagens avslutning:** Ved gjenbruk av bekreftelseslenken rapporterte studenten «kommer bare til innloggingssiden». Ingen ny innlogging ble rapportert; eksplisitt feilmelding og hvilken mekanisme som avviste forsøket er ikke verifisert. Studenten ba deretter om å avslutte for dagen. Lokal testserver ble stoppet, status og åpne tester lagret, og Story 2.1 forblir under arbeid. Testkontoen i Supabase beholdes; minneøktene i lokal backend skal ikke forventes å overleve. Ingen ny full offline-testkjøring eller appkodeendring i dag.

## 13.11.2026 – Gjenopptatt arbeid og foreløpig kodegjennomgang

**Studentens styring:** Etter dagsavslutningen ba studenten «vi fortsetter litt». Appen ble startet igjen, og studenten rapporterte «fikk logget inn». Dette bekrefter rapportert innlogging etter oppstart, men den gamle cookie-tilstanden før innlogging ble ikke separat dokumentert. Den tidligere godkjenningen ble beholdt.

**Uavhengige KI-kontroller:** Fire gjennomlesere vurderte kode, kanttilfeller, testgap og akseptanse. Alle funn fikk en egen vurdering før gruppering i tolv rettelser. En separat foreløpig gjennomgang ble gjennomført mens ekte akseptansetester står åpne, uten å hevde at Story 2.1 eller buildens formelle kontrolltrinn er fullført. Anonym kapasitetsbelastning på et fremtidig offentlig endepunkt ble vurdert som utenfor denne loopback-rettingen; dette innebærer ingen godkjenning av offentlig drift. Se [rapporten](../.docs/implementation-artifacts/auth-code-review-2026-11-13.md).

**Reproduserte feil og rettelser:** En ikke-ASCII-CSRF-verdi ga 500 uten no-store; samme probe gir nå 403 med no-store. En sen statusrespons kunne slette en nyere innlogging. Status endrer derfor ikke lenger økt-cookien; backend fjerner ugyldig autoritet og UI avviser, mens en ufarlig gammel tilfeldig verdi kan bli igjen. Andre rettelser gjelder nettverks-/innlesingsbudsjett, samtidig validering, levetid for nettleserbinding, skjema ved vindusbytte og trygge feilmeldinger.

**Feil funnet i KI-rettingen:** Oppfølgingskontrollen fant at avbrudd før køet arbeid fikk en tråd kunne etterlate en uavklart Future, og at testen for treg body bestod av feil grunn fordi passord manglet. Det ble rettet med selvstendig valideringsarbeid og komplett, forsinket testinput som må avbrytes. Hovedagenten fant også behov for å lukke den nye TLS-strømmen hvis håndtrykket returnerer etter budsjettet. Nye tester og oppfølgingsgjennomlesning kontrollerte dette. Tidsbudsjettet er kooperativt; det kan ikke tvangsavbryte systemets DNS/native operasjoner, og det hevdes ikke en hard veggklokkegrense.

**Faktisk sluttkontroll:** Hovedagentens samlede kjøring ga **155 beståtte tester, én forventet PDF-plattformtest hoppet over og én eksisterende advarsel**, 25,38 sekunder. Alle **93 innloggingstilfeller** bestod; **16 nettleserscenarier** og ti kontroller mot oppdatert konfigurert lokal server bestod. En ekstra gjennomleser kjørte avbruddsregresjonen med én bestått test. Låst installasjon/diff-kontroll bestod, og den godkjente frosne spesifikasjonen er uendret. Ingen ny konto/e-post/betalt tjeneste ble opprettet av testene. En ny manuell passordinnlogging etter selve rettelsene er bedt om, men ikke bekreftet ved dette kontrollpunktet. Test av to forskjellige autoriserte kontoer og øvrig hosted-akseptanse gjenstår.

**Manuell bekreftelse etter rettelsene:** Studenten svarte «Ja, jeg er logget inn» på den nye passordinnloggingen med eksisterende konto. Den nye serveren viste login 200; undersøkte tilgangsoppføringer hadde ingen auth-querystrenger. Dette bekrefter én ekte innlogging gjennom den korrigerte nettverksadapteren. Registrering/bekreftelse ble ikke gjentatt, og det er fortsatt ikke en test av to forskjellige brukere.

## 14.11.2026 – Minst mulig manuelt arbeid i to-konto-testen

**Studentens ønske:** Studenten ville fortsette testen dersom det krevde lite egeninnsats. Dette er en preferanse for automatisering, ikke bevis på en ekstra opprettet bruker eller tilkoblet administrasjon.

**Tilgangskontroll:** Ingen Supabase-administrasjonsverktøy er tilgjengelige. Katalogsøk viste at integrasjonen finnes, men ikke er installert/tilkoblet. Studenten ble bedt om å koble den til; ingen privilegerte nøkler eller passord ble etterspurt i chat. Docker-klienten finnes, men den lokale motoren svarer ikke; det ble ikke installert/startet en egen Supabase-stack. En slik lokal test ville uansett ikke bekrefte isolasjon på det godkjente skyløsningstestprosjektet.

**Faglig avgrensning:** Offisielle kilder for Auth Admin, administrativ brukeroppretting og SMTP ble kontrollert. En eventuell administrativt opprettet testbruker vil bare kunne gi evidens for de flytene som faktisk kjøres; den skal ikke omtales som verifisert e-postregistrering eller ubrukt lenkebinding. Ingen konto, invitasjon, e-post, innstillingsendring eller ny funksjonstest ble gjennomført i denne tilgangsavklaringen. Tidligere beståtte tester beholdes som historisk evidens.

## 14.11.2026 – Supabase-tilgang kontrollert i ny samtale

**Studentens styring:** «Fortsett Study Buddy der vi slapp.» Tidligere godkjenning og ønsket om minst mulig manuelt arbeid ble beholdt.

**Observert resultat:** Supabase-verktøyene er nå tilgjengelige og bekrefter organisasjonen Study Buddy, Free-planen og et aktivt studybuddy-test. En aggregert kontroll fant én bruker med bekreftet e-post, uten å hente personopplysninger eller legitimasjon. Faktisk region er `eu-west-3`, mens godkjent plan sier Frankfurt `eu-central-1`. Avviket er dokumentert og må avklares; ingen migrering eller omskriving av godkjenningen er utført.

**Verktøybegrensning og kontroll:** Integrasjonen har ingen Auth Admin-funksjon for brukeroppretting. Native-pipen feiler fortsatt med os error 2, og nettlesertilgangen er utilgjengelig. Studenten ble bedt om et kort manuelt dashboard-steg; ingen bekreftelse eller ny konto er antatt. Appen ble startet med eksisterende ignorert `.env` og én worker. Leverandørinnstillinger svarte 200 med påkrevd e-postbekreftelse, og ti nye HTTP-grensekontroller bestod. Dette verifiserer ikke isolasjon mellom to innloggede brukere; Story 2.1 er fortsatt under arbeid. Ingen ny full testsuite eller studentrefleksjon er hevdet.

**Kilder og vurdering:** [Oppdatert akseptansestatus](../.docs/implementation-artifacts/auth-setup.md). Sikkerhetsrådgiveren fant deaktivert kontroll av lekkede passord; [Supabases dokumentasjon](https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection) oppgir Pro-krav. Free-planen og eksisterende innstillinger ble beholdt.

**Neste konkrete steg:** Studenten svarte «Ja, jeg kan åpne Users». KI laget en ignorert lokal side med to tilfeldige testpassord og et HTTP-testprogram som bare skriver boolske kontrollresultater. Syntaks og lokal konfigurasjon er kontrollert. Studenten fikk veiledning for manuell oppretting av to administrative testbrukere; selve opprettingen og hosted-isolasjonstesten er ennå ikke bekreftet eller kjørt. Passord er ikke lagt i chat eller Git. Dette blir en test av konto-/øktisolasjon, ikke av registrering eller e-postlevering.

## 14.11.2026 – To opprettede testbrukere kontrollert

**Studentens bekreftelse:** «jeg har opprettet brukerene». Aggregert Supabase-kontroll viste nå tre brukere, alle med bekreftet e-post. Det stemmer med den opprinnelige kontoen og de to klargjorte testkontoene; ingen adresser, ID-er, passordhash eller tokens ble hentet.

**Kontroll og resultat:** Første testforsøk fullførte ingen kontroller fordi lokalserveren var stoppet. Etter oppstart med eksisterende ignorert konfigurasjon og én worker bestod **20 av 20 kontroller** mot ekte Supabase gjennom appen. Begge testbrukerne logget inn, beholdt separate identiteter ved vekslende forespørsler og fikk ulike øktcookies. Feil passord, fremmed CSRF, øktcookie uten riktig nettleserbinding og erstattet øktcookie ble avvist. Resultatet ble lagret uten legitimasjon i ignorert testfil. En uv-cachefeil i sandkassen ble løst ved godkjent eskalering.

**Faglig avgrensning:** Dette er HTTP-kontroll av autentisering og øktisolasjon for administrativt bekreftede testkontoer. Det dokumenterer ikke e-postregistrering, ubrukt bekreftelseslenke, nettleserlagring/UI, privat dokumentisolasjon, utløp eller refresh. Omstarten ble ikke testet med en bevart gammel innlogget cookie. Ingen appkode, global Auth-innstilling, konto eller abonnement ble endret av testprogrammet. Story 2.1 og regionavviket forblir åpne; studentens egen refleksjon er ikke lagt til av KI.

**Kilde:** [Akseptansestatus og reproduserbar kommando](../.docs/implementation-artifacts/auth-setup.md).

## 14.11.2026 – Øktlevetid, nettlesere og godkjent testregion

**Studentens beslutning:** Studenten ba «da går vi videre» og godkjente deretter «Ja, behold Paris for testprosjektet». Den eksisterende Free-instansen i eu-west-3 beholdes. Opprinnelig frosset spesifikasjon er bevart; en datert presisering dokumenterer endringen for testprosjektet. Dette er ikke en produksjonsbeslutning.

**Utførte kontroller:** En separat lokal HTTP-server med ekte Supabase-adapter bestod **18/18 kontroller**: kort inaktivitetsgrense, absolutt grense til tross for aktivitet, bevart gammel cookie avvist etter reell serveromstart, ny innlogging, ekte refresh med bevart identitet og avvisning av ugyldig refresh uten å avslutte den andre kontoen. Tidsgrensene ble forkortet i testoppsettet. For å fremprovosere refresh ble bare lokal utløpsmetadata forkortet; ekte provider-tokens og leverandørvalidering ble brukt. Dette er ikke observasjon av naturlig JWT-utløp eller 30 minutter/12 timer i faktisk ventetid. Loggkontrollen ble styrket til alle utstedte testtokens, og 18/18 bestod igjen; det er samme tilfeller, ikke 36 ulike tester.

**Ekte nettlesere:** **24/24 kontroller** bestod med to innloggede kontoer og et tredje uinnlogget miljø mot normalappen/hosted Supabase. Testen kontrollerte riktig identitet etter reload, cookieflagg, trygt feilpassord-svar/fokus/tømt passord, tom local/session storage, IndexedDB, Cache Storage og JavaScript-cookies, rene URL-er og fravær av provider-tokenfelter i API-svar. Ingen scriptfeil ble observert. Ikke en full manuell skjermleser- eller HTTPS-kontroll. Den vanlige serverens innstillinger ble beholdt; ekstra testservere ble stoppet.

**KI-feil og korrigering:** KI ba først om ny registrering med studentens eksisterende bekreftede adresse. Det ville ikke dokumentere en ny kontos bekreftelsesflyt. Instruksen ble trukket tilbake og erstattet med avklaring om en ubrukt, allerede autorisert teamadresse finnes. Studenten spurte «Skal jeg opprette en ny bruker»; svaret presiserte at flere administrative Supabase-brukere ikke trengs, og at eventuell e-posttest må gå gjennom appen med riktig adresse. Ingen ny registrering eller e-postlevering er antatt. Studentens egen refleksjon er ikke skrevet av KI.

**Kommunikasjon:** Studenten svarte «skjønner ikke» etter forklaringene om konto og teamadresse. KI presiserte at studenten ikke trenger opprette flere brukere eller gjøre noe nå. E-posttesten står fortsatt åpen; dette er ikke tolket som full akseptanse eller en uttalelse om andre adresser. De unødvendige og motstridende instruksene skapte mer manuelt arbeid enn ønsket.

**Status:** E-postlenkens resterende negative tilfeller og malinspeksjon står åpne; Story 2.1 forblir under arbeid. [Akseptansestatus](../.docs/implementation-artifacts/auth-setup.md) skiller nye resultater fra historiske tester og videre arbeid. Ingen appkode eller globale Auth-innstillinger ble endret.

## Mal for neste hendelse

### DD.MM.ÅÅÅÅ – Kort tittel

**Hendelse og mål:**

**KI-forslag/bidrag:**

**Studentens beslutning eller korrigering:**

**Kontroll og observert resultat:**

**Dokumentasjon/commit/prompt:**

**Relevant del av rapportmalen:**

**Studentens egen refleksjon:**
