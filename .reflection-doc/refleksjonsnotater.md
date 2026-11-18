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

## 14.11.2026 – Neste oppgave konkretisert: Glemt passord

**Studentens styring:** «ok, da går vi videre». Den ekstra bekreftelses-e-posttesten står åpen. Studenten godkjente deretter «Ja, lagre og fortsett» for lagring av de fire ferdige dokumentoppdateringene fra testingen. De ble lagret lokalt i `32b1586bf6c1ebc3297205eefe538c1a3b176af9`.

**KI-bidrag og kontroll:** BMAD build ble brukt til å undersøke neste backloggoppgave og skrive [en konkret draft for Story 2.2](../.docs/implementation-artifacts/spec-2-2-recover-a-password-through-a-restricted-session.md). Én read-only-agent undersøkte gjenbrukspunkter etter skillens instruks. SDK-koden viste et viktig recovery-særtilfelle: lagret PKCE-verifier har `/PASSWORD_RECOVERY`-markør, mens utvekslingen må sende selve verifieren. Planen krever transporttest for dette og eierkontroll før passordmutasjon.

**Status og avgrensning:** Planen beskriver passordoppdateringsautoritet adskilt fra vanlig innlogging og gjenbruk av beskyttelsen mot at en sen respons overskriver en nyere login-cookie. Den er presentert til konkret godkjenning etter workflowens kontrollpunkt. Appkode er ikke endret, og ingen nye tester/e-poster/passordmutasjoner er utført. Dette er planlegging, ikke implementering eller godkjent akseptanse. Studentens egen refleksjon er ikke lagt til.

## 14.11.2026 – Glemt passord implementert og kontrollert

**Studentens godkjenning:** Etter forklaring av den konkrete planen svarte studenten «gjør det». Den frosne intensjonen i Story 2.2 ble låst; tidligere e-postakseptanse fra Story 2.1 forblir åpen. KI har ikke skrevet studentens egen refleksjon.

**Implementert:** Generisk forespørsel om gjenopprettingslenke, separat PKCE-formål/verifier/binding, begrenset engangsautoritet, passordoppdatering og vanlig innlogging etterpå. Kun syntetiske leverandørsvar brukes i implementasjonstestene. Ingen ekte e-post eller passordmutasjon ble utført.

**KI-feil og uavhengig kontroll:** Hovedagenten fant at SDKens update_user kunne fornye økten etter den første eierkontrollen. Identiteten kontrolleres nå også etter denne interne fornyelsen, før PUT. Tre uavhengige reviewlag leverte ti blindfunn, to verifikasjonsfunn og ingen ytterligere kanttilfellefunn. Alle funn fikk egen dom før gruppering. Syv små rettelser/testforbedringer ble gjennomført; to lave forslag ble avvist med begrunnelse, og tidligere eksisterende e-postkvote/throttling før offentlig drift ble utsatt eksplisitt. En syntetisk probe reproduserte at en forsinket recovery-callback kunne erstatte nyere innlogging; etter retting settes ingen gammel cookie og den nye innloggingen beholdes. UI fikk konsistente Unicode-grenser, riktige pre-admission-feil og synlig navigasjon til innlogging/recovery.

**Faktisk sluttkontroll:** Hovedagentens siste fulle kjøring ga **213 bestått, én forventet PDF-plattformskip og én eksisterende Starlette-advarsel**, 26,89 sekunder. JUnit inneholder **151 auth-tester uten feil/skips**, inkludert tre callback-racer, to utløp-under-validering og gjentatt feil/retry uten kapasitetslekkasje. **23 ekte nettleserscenarier for konto** med testleverandør og **11 demoscenarier** bestod. Hovedagenten leste full diff og patchdiff og inspiserte oppdatert 200 %-skjermbilde uten avkuttet innhold. Den frosne spesifikasjonsblokken er uendret. Ingen nye tester hevdes fra den etterfølgende dokumentredigeringen.

**Lokal drift og gjenstående akseptanse:** Normalappen ble startet på nytt med eksisterende ignorert `.env` og én worker; lesekontroller fant ny recovery-UI/status og personvernheadere. Omstarten krever ny vanlig innlogging. Implementeringsspesifikasjonen er done og sprintstoryen review. Ekstra hosted callback-allowlist, malinspeksjon, ekte gjenopprettingsmail og uttrykkelig autorisert passordendring gjenstår; dette er ikke full hosted-godkjenning. Free/Paris, ingen nye tabeller/betalte tjenester/utrulling og de eldre Story 2.1-portene er bevart. Se [oppsett og evidens](../.docs/implementation-artifacts/auth-setup.md).

## 15.11.2026 – Ekte passordbytte rapportert vellykket

**Studentens observasjon:** Etter rapportert lagring av recovery Redirect URL mottok studenten e-post med lenke for nytt passord. Studenten svarte deretter «resette passord fungerte» og presiserte «jeg prøvde å bytte passord, det fungerte». Dette er studentrapportert gjennomført ekte passordbytte; KI endret ikke passordet og ba ikke om å få det i chat.

**Supplerende kontroll:** Den kjørende konfigurerte serverens tilgangslogg viste én recovery-request 200, én recovery-callback 303, én passordoppdatering 200 og vanlig login 200 etter oppdateringsoppføringen. Bare trygge tellinger/boolske resultater ble skrevet ut. Hvilket passord som ble brukt ved innlogging ble ikke inspisert. Funksjonell callback er dermed underbygget, mens malinnhold og negative hosted-tilfeller fortsatt ikke er separat kontrollert. Ingen ny automatisk testkjøring er hevdet.

**Videre retning:** Studenten spurte «hva er neste steg». Neste planlagte utviklingsoppgave er Story 2.3, Logg ut og tydelig avslutning ved utløp/omstart. Det er en beskrivelse av backloggen, ikke godkjenning av en ny konkret implementeringsplan eller full akseptanse av alle gjenværende hosted-tester. Studentens egen refleksjon er ikke skrevet av KI.

## 15.11.2026 – Utlogging konkretisert før implementering

**Studentens styring:** «da fortsetter vi», etter forklaring av Story 2.3 som neste utviklingsoppgave. Tidligere positiv passordtest og de åpne hosted-portene ble beholdt som separate fakta.

**Undersøkelse og KI-forslag:** BMAD build og én read-only-agent ble brukt til å konkretisere utlogging og øktavslutning. SDK-koden viste at vanlig sign_out som standard kan logge ut alle økter og kan fornye tokens før revokering. Planen krever eksplisitt local scope med allerede beholdt bruker-JWT, lokal avslutning/cookie-sletting før best-effort providerarbeid og en grense for samtidige bakgrunnskall. En annen sentral beslutning er at passive statuskontroller ikke skal telle som aktivitet og dermed holde en ubrukt økt i live.

**Status:** [Planen for Story 2.3](../.docs/implementation-artifacts/spec-2-3-end-access-on-logout-expiry-and-restart.md) er draft og presentert til konkret godkjenning. Den legger opp til automatisk kontroll av samme konto i uavhengige nettlesere, utløp/omstart og sene svar. Ingen implementering eller nye testresultater er hevdet, og ingen faktisk bruker er logget ut av KI. Studentens egen refleksjon er ikke lagt til.

**Etterfølgende beslutning:** Studenten valgte «Godkjenn og fortsett med implementering». Frosset intensjon ble låst, og spec/sprint ble satt under arbeid. Én implementeringsagent fikk hele spesifikasjonen i frisk kontekst; senere review og hovedagentens verifikasjon skal skje før ferdigmelding. Pågående implementering er ikke registrert som ferdige tester eller hosted-kontroll.

**Kontroll og avslutning kl. 09:42:** Implementeringen legger til lokal utlogging, revisjonskontroll rundt sene innloggingsforsøk, ikke-forlengende status og synlig rydding ved utløp/omstart. Hovedagenten leste hele diffen og kjørte 239 beståtte tester/én uendret plattformskip, 177 auth-tilfeller, 28 auth-nettleserscenarier og 11 demo-scenarier. Godkjent blokk beholdt SHA-256 `0669a8ae87bcd57293b81ccc0cee6567e7795f60388dde9e08aa8946d82fc64e`. Tidlig kontroll oppdaget manglende revisjonsendring når utløp skjedde under validering, norske tekster med spørsmålstegn og for svake like-token-fixtures; implementeringsagenten rettet disse før hovedkontrollen.

**Fortsatt uferdig:** To uavhengige reviewrapporter foreligger, men funnene er ikke ferdig triagert/rettet. De gjelder blant annet retry ved mislykket utlogging, sene svar/cookies, gamle fanesignaler og en manglende test av leverandøravvisning samtidig med callback. Tredje review ble avbrutt da studenten ba «jeg vil avslutte denne sesjonen, commit». Dette overstyrte videre arbeid; spec/sprint blir review, ikke done. Ingen hosted-utlogging, nye e-poster, passordmutasjoner eller utrulling ble utført. Studentens egen refleksjon er ikke skrevet av KI.

**Parallelt arbeid:** Studenten ba om en oppgave til en annen sesjon. KI foreslo en kun-lesende kartlegging av Story 2.4/PDF-prototypen, uten filendringer, Git-operasjoner, serverstart eller Supabase-endringer for å unngå kollisjon i samme arbeidskopi.

## 15.11.2026 – Review og sluttkontroll av utlogging

**Studentens styring:** Studenten ba om å lese den lagrede konteksten og fortsette eksisterende BMAD build fra steg 4, uten ny planlegging/godkjenning. Implementeringen i `5222b95` og tidligere godkjenning ble beholdt. Studenten ba om fullføring, dokumentasjon/logg og lokal commit; tidligere vellykket passordbytte skulle ikke gjentas og nye e-poster ikke sendes automatisk.

**Uavhengig kontroll og bekreftede feil:** Det avbrutte edge-reviewet ble fullført og bekreftet de åtte app-/testfunnene B1–B8. B9 var allerede rettet i overleveringen; V1 var et dokumentert testgap. Hvert funn fikk egen vurdering før gruppering. En konkret probe viste at forsinkede logout-headere kunne slette en nyere innloggingscookie mens den nye serverautoriteten fortsatt levde. Cookies har nå egne øktgenerasjoner; bare innkommende generasjonsnavn slettes, og serverens aktive nettleserbinding avgjør hvilken autoritet som gjelder. Andre rettelser bevarer utloggingsintensjon gjennom retry, kontrollerer gamle fanesignaler mot serveren, trekker svartid fra visningens levetid, bevarer recovery-kontroller under passive kontroller, unngår felles trådkø ved revokering og rydder opp i sene avviste leverandøridentiteter. V1 har nye blokkerte callback-regresjoner. Oppfølgingsgjennomlesningen fant ingen ytterligere feil og kjørte ikke egne tester.

**Kontrollgrunnlag og grenser:** Hovedagentens fulle offline-kjøring ga 243 beståtte tester og én uendret valgfri PDF-plattformskip; alle 181 auth-tilfeller bestod. Auth-nettlesersuiten har 33 scenarier, og demoen 11 scenarier/21 genereringskall. De nye testene brukte syntetiske identiteter; skjermbildet ved 200 % ble inspisert. Den frosne godkjente blokken beholdt SHA-256 `0669a8ae87bcd57293b81ccc0cee6567e7795f60388dde9e08aa8946d82fc64e`. Testen for gammel fanetimer måtte få riktig rekkefølge: en ny BroadcastChannel i samme side leverer også til sidens app-lytter, og et slikt signal ville revalidere/fornye visningstimeren før den tilsiktede timerkontrollen. Timeren testes derfor før de eksplisitte signalene. Dette var en testoppsettfeil, ikke bevis på en ny produktfeil.

**Faktisk hosted-evidens:** En separat lokal nettleser-/HTTP-harness bestod 25 kontroller med eksisterende autoriserte testkonto og ekte Supabase-validering, lokal revokering og refresh. En annen nettleser på samme konto overlevde utlogging og gjennomførte ekte refresh. En reell testserverprosess ble startet på nytt med bevart cookie/åpen side; gammel autoritet ble avvist og ny innlogging fungerte. Recovery-grant og korte utløpsmetadata ble instrumentert lokalt med ekte leverandøridentitet; providerfeil ble injisert ved adaptergrensen. Dette beviser ikke ubrukt e-postlenke/PKCE, naturlig venting i 30 minutter/12 timer eller en reell Supabase-driftsstans. Ingen ny e-post, konto, passordmutasjon, innstillingsendring, kostnad eller utrulling ble utført.

**Lokal drift:** Prosesseierskap for gammel worker 35884 ble kontrollert før utskifting. Ny normalserver med ignorert `.env`, én worker og PID 11748 bestod ti kontroller, også ekte innlogging/utlogging og nye cookie-generasjoner. Den isolerte testserveren ble stoppet. Gjenstående lenke-/malakseptanse for Story 2.1/2.2 er fortsatt åpen. Studenten må logge inn igjen etter normalserverens omstart. Se [akseptanseevidens](../.docs/implementation-artifacts/auth-setup.md#story-23-review-completion--2026-11-15) og [triage](../.docs/implementation-artifacts/spec-2-3-end-access-on-logout-expiry-and-restart.md). Studentens egen refleksjon er ikke skrevet av KI.

## 15.11.2026 – Planlegging av eget kildemateriale (Story 2.4)

**Studentens styring:** Etter anbefaling om Story 2.4 svarte studenten «start med det». Det starter konkret planlegging av tekst-/fil-/PDF-inntak. Godkjenningen av Story 2.3 er ikke brukt som godkjenning av denne nye implementeringsplanen.

**Undersøkelse:** BMAD build ble rendret én gang for den nye oppgaven. Gyldig cached Epic 2-kontekst og ferdig Story 2.3 ble gjenbrukt. To kun-lesende agenter kartla henholdsvis PDF-isolasjon og UI/kontrakter; ingen tester ble kjørt av dem. Eksisterende PDF-probe har Windows Job Object-isolasjon, fysiske sidetall, dekning og grense-/oppryddingstester. Dette er tidligere syntetisk evidens, ikke akseptanse av vilkårlige PDF-er eller fremtidig hosting. [pypdf 7.0.1-dokumentasjonen](https://pypdf.readthedocs.io/en/7.0.1/user/extract-text.html) ble kontrollert om uttrekk og minnebruk; Python-dokumentasjonen ble kontrollert om streng UTF-8-/base64-dekoding.

**KI-forslag:** [Draft for Story 2.4](../.docs/implementation-artifacts/spec-2-4-validate-and-extract-the-active-source.md) beskriver egen innlogget kildeflate med forhåndsvisning, maks 30 000 kodepunkter/40 fysiske sider/10 MiB fil, begrenset body-/arbeidstid og kapasitetskontroll. Det gamle demoendepunktet skal aldri behandle privat materiale. Et ikke-autoriserende øktkjennetegn skal gjøre at gammelt materiale tømmes også ved ny innlogging i en annen fane på samme konto. KI-generering og lagring følger senere stories. Transportvalg og begrensninger er implementeringsvalg innenfor eksisterende krav; ingen åpne produktvalg krever spørsmål før den konkrete plangodkjenningen.

**Kontroll og KI-feil:** Spesifikasjonen ble selvkontrollert og forkortet fra 1733 til 1586 tokens målt med o200k-tokenisering. Ingen appkode, ny funksjonstest, serverstart, konto/e-post/passordmutasjon eller hosted-endring ble utført. Under lesing ble norske tegn oppdaget erstattet med spørsmålstegn i dokumentasjonen KI lagret ved forrige sluttføring; årsaken var tekst via PowerShells stdin-koding. Tegnene ble rettet uten endring av fakta, og nye norske tekster skrives direkte som UTF-8. Utdaterte sprintkommentarer/README ble også korrigert; Story 2.3 forblir review med done spec og sine presise hosted-begrensninger. Studentens egen refleksjon er ikke skrevet av KI.

**Status:** Story 2.4 er draft, sprintnøkkelen forblir backlog. Planen legges frem ved BMAD steg 2 CHECKPOINT 1 før implementering; tidligere testresultater er historiske og de eldre e-post-/lenkeportene forblir åpne.

## 15.11.2026 – Eget kildemateriale implementert og kontrollert

**Studentens styring:** Studenten godkjente den konkrete Story 2.4-planen med «godkjenn og fortsett». Specen ble lest fra disk på nytt, låst og satt under arbeid; opprinnelig baseline ble beholdt. Implementeringsagenten traff senere en bruksgrense etter å ha skrevet produksjonskode/UI og tester. Studenten svarte «fortsett», og hovedagenten fullførte selv uten ny planrunde eller godkjenning.

**Implementert:** Innlogget arbeidsflate for innlimt tekst, UTF-8-fil eller tekstbasert PDF med forhåndsvisning, studieinnstillinger og faktiske avsnitt/fysiske sider. Kildebytte/nullstilling og øktavslutning forkaster gammelt arbeid. `sessionViewId` er et ikke-autoriserende kjennetegn som avviser bruk av gamle utkast etter ny innlogging, også for samme konto. Materialet blir ikke lagret, og KI-generering følger Story 2.5. Den eksisterende demoen og konto-/recovery-flyten består.

**Uavhengig review og KI-feil:** Tre lag ga elleve blindfunn, to overlappende kanttilfellefunn og to dokumenterte testgap. Alle fikk egen dom før gruppering. Bekreftede rettelser gjelder minnepress fra vilkårlige JSON-objektgrafer, overlappende statuskontroller, sene autoritetssvar, begrenset utloggingsretry og bevart retry ved siderestaurering. Et 60 011-byte forsøk med 20 000 tomme objekter allokerte 1 513 276 byte før retting; nå avvises formen før objektene bygges, og parsing/klargjøring kjører i egne begrensede tråder. Testgapene gjaldt nøyaktig PDF-tekst gjennom API/UI og arbeidsflatens egen utlogging. Gamle dokumentasjonsformuleringer og et spørsmålstegn feilaktig endret under tegnopprydding ble korrigert uten å endre studentrefleksjoner. Et generelt forslag om ekstra shutdown-hook ble avvist fordi ingen lekkasje/unnsluppet prosess ble dokumentert, mens probe/deadline/opprydding allerede begrenser arbeidet. Ingen reviewfunn ble utsatt. Oppfølgingsgjennomlesningen fant ingen nye feil og kjørte ikke egne tester.

**Faktisk sluttkontroll:** Hovedagenten kjørte låst avhengighetssynk og full verifikasjon etter rettelsene: **306 beståtte Python-tester, én uendret valgfri PDF-plattformskip og én eksisterende Starlette-advarsel**, 77,74 sekunder. Alle **181 auth- og 63 kildetilfeller** bestod, inkludert ni faktiske isolerte PDF-integrasjonstilfeller. Ekte nettlesere med syntetisk identitetsadapter bestod **19 kilde-, 33 auth- og 11 demoscenarier**, 21 genereringskall i demo. 320 px/200 %-bilder ble inspisert uten overflyt. Begge godkjente specblokker er uendret; Story 2.4-hash er `bba17495533b217d96a9c382c43a59714338a307aec8b0df249d2ec10b7d6914`.

**Visuell kildekontroll og begrensning:** En selvforfattet PDF med ordinær synlig tekst på side 1 og 3 og blank side 2 ble gjengitt med Poppler og kontrollert visuelt side for side. API-et returnerte nøyaktig samme tekst, riktige fysiske plasseringer og blank side 2; worker/admission ble ryddet. Poppler ble brukt portabelt under ignorerte testfiler og ReportLab som midlertidig uv-verktøy, uten maskininstallasjon eller nye appavhengigheter utover den godkjente pypdf-pinnen. Dette er syntetisk/render-evidens på Windows, ikke godkjenning av vilkårlige pensum-PDF-er, OCR/leserekkefølge eller fremtidig hosting.

**Lokal drift og videre arbeid:** Prosesseierskap for gammel worker 11748 ble kontrollert før utskifting med worker 45744, én prosess med eksisterende ignorert `.env`. Åtte uinnloggede oppstarts-/sikkerhetskontroller bestod; ingen ekte konto-/e-post-/passordhandling ble kjørt i denne storyen. Studenten må logge inn igjen etter omstarten. Spesifikasjonen er done, sprint 2.4 er review, og [akseptansedokumentet](../.docs/implementation-artifacts/source-acceptance.md) skiller utførte kontroller fra åpne portene for representative PDF-er, målplattform og tidligere e-postlenker/maler. Ingen modellkall, lagring, hosted-innstilling, kostnad eller utrulling er utført. Studentens egen refleksjon er ikke skrevet av KI.

## 15.11.2026 – Modellavklaring og plan for ekte KI-generering

**Studentens styring:** «Første leveranse er modellavklaring og en konkret implementeringsplan, ikke live modellkall» og «Ikke anta at disse valgene allerede er godkjent». Studenten krevde undersøkelse av kode/integrasjoner før spørsmål, oppdaterte offisielle kilder, et forståelig kostnadsoverslag og konkret plangodkjenning før implementering. Tidligere auth-/PDF-godkjenninger og testresultater skulle bevares.

**Utført undersøkelse:** Ny BMAD-build ble rendret én gang. Hovedagenten leste tidligere logg, issues, Story 2.4-spesifikasjonen, kildeakseptansen, gyldig Epic 2-kontekst og Story 2.5. To kun-lesende agenter undersøkte henholdsvis kilde-/økt-/kvitteringskontrakter og UI/testmønstre etter build-steg 2s delegasjonsinstruks. De endret ingen filer og kjørte ingen tester. Kildeuttrekket har ennå ikke et bevis som beskytter kilden mot endring ved senere innsending til generering; planen foreslår signert kildebevis og en begrenset autoritetsoversikt med bare metadata/hashes. Fremtidig Save må kontrollere både signatur og gjeldende autoritet.

**KI-forslag, ikke studentbeslutning:** Offisielle sider for GPT-6 Luna, Gemini 3.8 Flash og Claude Sonnet 5.5 ble kontrollert. Luna anbefales foreløpig på grunn av pris, strukturerte svar og mulighet for eksplisitt cachemodus uten cachepunkter. Norsk tekstkvalitet og kildefasthet er ikke målt. Et regneeksempel med 10 000 inputtokens og 4 000 outputtokens gir USD 0,003 for Luna ved de kontrollerte prisene. Forslaget er totalt USD 5 i bruksramme, konservativ reservasjon USD 0,05 per forsøk, høyst fire automatiserte syntetiske livekontroller etter godkjenning, 60 sekunders serverfrist og 8 000 outputtokens. Globale API-vilkår, ingen treningsdeling og normalt inntil 30 dagers sikkerhetslogger må avklares; `store:false` alene betyr ikke null datalagring.

**API-tilgang og kontroll:** Kun forekomst av vanlige modellnøkkelnavn ble kontrollert i eksisterende ignorert `.env` og prosessmiljø; ingen ble funnet, og ingen verdier ble skrevet ut. Det beviser ikke at studenten mangler en konto eller nøkkel et annet sted. Tilgjengelige integrasjoner ga ingen modelltilgang til appen. Eksisterende Supabase-tilgang ble ikke åpnet som nytt spørsmål. Ingen inferenskall, kontovalidering, kjøp, endring av hosted-innstillinger, omstart, ny e-post, passordhandling eller utrulling er utført. Ingen nye funksjonstester er hevdet; tidligere 306 bestått/én skip og nettleserresultater er historisk baseline.

**Dokumentasjon og status:** [Draft-spesifikasjon](../.docs/implementation-artifacts/spec-2-5-generate-all-learning-parts-from-the-source.md), [modell-/kostnadssammenligning med kilder](../.docs/implementation-artifacts/model-decision-2-5.md) og [genereringsprotokoll](../.docs/implementation-artifacts/generation-protocol-2-5.md) er skrevet. De fem åpne spørsmålene gjelder modell, faktisk API-tilgang, kostnad/livekontroll, datahåndtering og tids-/størrelsesgrenser. Story 2.5 beholdes i backlog inntil porten er avklart; appkode er ikke endret. Studentens egen refleksjon eller godkjenning er ikke skrevet av KI.

## 15.11.2026 – Plangodkjenning og behov for API-oppsett

**Studentens beslutning:** Studenten svarte «Godkjenn planen med forslagene», men beholdt begge API-alternativene i den kopierte svarmalen. KI behandlet godkjenningen av modell, kostnadsramme, datavilkår og tids-/størrelsesgrenser som gyldig, men antok ikke at faktisk API-tilgang var på plass. På ett avklaringsspørsmål svarte studenten «Trenger hjelp med oppsett». Samme konkrete plan trenger dermed ikke ny godkjenning; API-oppsett er et utestående praktisk vilkår.

**KI-bidrag og kontroll:** Spesifikasjonen ble lest fra disk før godkjenningen ble registrert. Lokal kontroll av vanlige OpenAI-nøkkelnavn viste fortsatt ingen konfigurert nøkkel, uten å vise noen verdier. Offisielle oppsett-/prosjekt-/nøkkel-/betalingsinstruksjoner ble kontrollert. Veiledningen skiller minimumskjøp av kreditt på USD 5 fra appens bruksramme, og gjør oppmerksom på at automatisk påfyll er på som standard i betalingsoppsettet. Studenten håndterer innlogging, betaling og selve nøkkelen privat. Et tomt nøkkelfelt i ignorert `.env` klargjøres uten å endre auth-verdier eller aktivere modellkall.

**Status og avgrensning:** Planvalg er registrert i godkjenningsblokken, men spec/sprint står draft/backlog til API-tilgang er etablert. Ingen appimplementering, nøkkelvalidering mot leverandør, inferens, konto-/prosjektoppretting, kjøp, hosted-endring eller serverrestart er utført. Tidligere testbevis er historiske og uendret. Studentens egne refleksjoner er ikke skrevet av KI.

**Kontroll kl. 12:11:** Studenten rapporterte «nøkkelen er lagret og fakturering er klar». KI kontrollerte lokal konfigurasjon uten å vise verdier: riktig prosjektrot har én ignorert `.env`, med ett fortsatt tomt OPENAI_API_KEY-felt og ingen tilsvarende prosessvariabel. En ny kontroll etter ventetid viste samme resultat. Derfor ble ingen HTTP-forespørsel til OpenAI sendt, og faktisk modelltilgang er fortsatt ukontrollert. Dette er ikke en leverandøravvisning eller bevis på feil nøkkel/fakturering. Studenten ble bedt om å oppgi bare eventuell annen filsti eller lagre feltet i riktig fil. Godkjenningen beholdes; ingen ny finansiering eller plangodkjenning etterspørres.

## 15.11.2026 – Ekte KI-generering implementert og kontrollert

**Studentens styring og faktisk tilgang:** Etter «lagret» ble lokal nøkkel funnet og modellmetadata bekreftet uten inferens. Studenten ba «fortsett». Tidligere godkjent modell, USD 5-ramme, fire automatiserte livekontroller, datavilkår og tids-/størrelsesgrenser ble beholdt. KI ba ikke om ny betaling eller plangodkjenning og viste ingen hemmeligheter.

**Implementert:** Én handling trekker ut og genererer sammendrag, begreper, flashcards og quiz. Signert kildeakseptanse, ordnet metadata-/hashautoritet og genereringskvitteringer beskytter mot endret kilde, sene svar og avsluttet økt. Tekst, valgt fil og innstillinger beholdes ved teknisk feil. Budsjettreservasjoner er varige og innholdsfrie; demodata brukes aldri som reserve for modellsvikt. Save/database/hosting inngår ikke.

**KI-feil og uavhengig kontroll:** Et tidlig claims-utkast eksponerte rå øktidentifikator og ble rettet til ikke-autoriserende hashbinding før tester/live. En uventet 401 avdekket et eksisterende kanselleringsvindu etter vellykket auth-validering; deterministiske før-/etter-barrieretester dekker rettingen. Tre uavhengige reviewlag og én edge-oppfølging ga totalt tretten individuelle funn. Alle ble rettet, ingen utsatt. Bekreftede problemer omfattet manglende sjekk før utsending, anomalibruk under låsekonflikt/avvist svar, tidsfrist under treg opprydding og blokkerende budsjett-I/O, advarselskvote, UI-språk/kvalifikasjoner/Enter og for svak test av kildeenheter utover u1. Budsjett-I/O har nå to avgrensede arbeidere uten kø; autoritet kontrolleres på nytt etter venting. Ingen ny intensjon eller frosset godkjenning ble skrevet om.

**Faktisk kontroll:** Hovedagentens endelige fulle kjøring ga **422 bestått og én uendret plattformskip**, 90,163s, med **183 auth-, 63 kilde- og 114 genereringstester** uten skips. Sluttkontroll i nettleser: **28 kilde-/genererings-, 33 auth- og 11 demoscenarier**. Begge 320px/200%-bilder er inspisert. Låst avhengighetssynk og whitespace-kontroll bestod. Godkjent blokk beholdt SHA-256 `2b453bfa703d032fc54784412a7239b435ed4be9954e5f820f3e4fb563395301`; eldre kilde-/auth-akseptanse er bevart.

**Begrenset live-evidens og kostnad:** Eksakt fire godkjente, selvskrevne syntetiske kall bestod før reviewrettingene: norsk/kort, engelsk/detaljert, utilstrekkelig innhold og fysisk PDF med lesbare sider 1/3 og ulesbare 2/4. Estimert standardforbruk var **USD 0,0008135 før avgifter**, ikke faktura. Varig ledger har **USD 0,20 reservert**, fire forsøk og fire livekontroller; ingen nullstilling/refusjon eller flere automatiserte livekall. Sluttkontrollen etter review var offline, ikke en ny live-kvalitetsmåling. Full kildefasthet/språkkvalitet gjenstår i Story 2.6.

**Lokal drift og videre porter:** Normalserveren ble startet på nytt med samme ignorerte nøkkel/auth, eksplisitt modellaktivering og én worker (PID 30048). Ti uinnloggede oppstartskontroller bestod uten inferens eller budsjettendring; ny innlogging kreves. Første kontrollskript stoppet før HTTP på et feil navn på konfigurasjonsegenskapen; korrigert skript bestod. Spec er done, sprint review. Representative PDF-er, målplattform, eldre e-postlenke-/malporter og full skjermleserakseptanse er fortsatt åpne. Ingen konto, e-post, passord, hosted-innstilling, finansiering, deploy eller push ble utført. Se [akseptanseevidens](../.docs/implementation-artifacts/generation-acceptance.md) og [triage](../.docs/implementation-artifacts/spec-2-5-generate-all-learning-parts-from-the-source.md). Studentens egen refleksjon er ikke skrevet av KI.

## 15.11.2026 – Konkret kvalitetsplan for Story 2.6

**Studentens styring:** Studenten spurte om neste steg med 30 % igjen av femtimersgrensen og svarte «Start på det» etter anbefaling om en konkret kvalitetsplan. Dette er behandlet som start på planleggingen, ikke som ny kostnadsgodkjenning eller ferdig innholdsevaluering.

**KI-bidrag og undersøkelse:** En ny BMAD-build ble rendret én gang. Gyldig cached Epic 2-kontekst, ferdig Story 2.5, faktisk kode og tidligere akseptanseevidens ble lest. Én kun-lesende agent kartla gjenbruk/testgrenser etter planleggingsstegets instruks; ingen filer, tester eller nettverkskall ble utført av agenten. De fire tidligere livekontrollene er protokollevidens og kan ikke erstatte tre ulike dokumenter med fem forhåndsvalgte begreper hver.

**Konkret forslag:** KI skrev en [draft-spesifikasjon](../.docs/implementation-artifacts/spec-2-6-evaluate-generated-content-against-known-sources.md) og [forhåndsregistrert korpus/rubrikk](../.docs/implementation-artifacts/content-evaluation.md). Tre selvskrevne ufølsomme dokumenter gjelder et fiktivt bibliotek, en fiktiv laboratorieprosedyre og et fiktivt feltkurs; former er innlimt tekst, UTF-8-fil og PDF. Femten begreper/fysiske plasseringer er valgt før generering. Alle produserte elementer skal leses mot kilden, og kildefeil, referansefeil og utelatelser registreres separat. Konflikt i emnefelt og utilstrekkelig tegnsettingskilde har egne kontroller. KI forbereder materialet, slik at studenten ikke må finne/laste opp filer. Bare den ordinære lesbare PDF-en etter rendering/tekstsammenligning kan brukes som visuell kildeevidens.

**Kostnadsvalg er fortsatt et forslag:** Maksimalt åtte nye forsøk (fem grunnscenarier, tre mulige omtester), høyst USD 0,40 ekstra reservasjon innen eksisterende USD 5. En separat innholdsfri og varig evalueringskvote foreslås, mens den gamle firekallskvoten og global ledger bevares. Offisiell Luna-side ble kontrollert: USD 0,10/0,50 per million input/outputtokens. Åtte eksempelkall à 10 000/4 000 tokens gir USD 0,024 før avgifter; dette er regneeksempel, ikke faktisk forbruk. Ingen nye modellkall eller finansiering er autorisert/utført. Endres felles prompt, kreves nye sluttresultater for alle fem scenarier; utilstrekkelig kvote gir uferdig akseptanse, ikke automatisk økning.

**Kontroll og status:** Spesifikasjonen er 1527 tokens med `o200k_base`; whitespace-kontroll er utført, og kontekstens tidsstempel er nyere enn alle planleggingsfiler. Kode, avhengigheter, sprintstatus/backlog, `.env`, faktisk budsjett og normalserver er ikke endret. Ingen nye funksjonstester eller kvalitetsresultater er hevdet. Plan og ny evalueringsramme legges frem til samlet avklaring/godkjenning; spec forblir draft. Tidligere 422 bestått/én skip og 28/33/11 nettleserscenarier er historiske. Studentens egen refleksjon er ikke skrevet av KI.

## 15.11.2026 – Kvalitetsevaluering med fem kontrollerte modellkall

**Studentens beslutning:** Etter forklaring av fem grunnscenarier og opptil tre omtester svarte studenten «ok greit». Den konkrete planen og høyst åtte nye evalueringsforsøk/USD 0,40 ekstra reservasjon innen eksisterende USD 5 er dermed godkjent. Senere «fortsett» beholdt dette oppdraget. Gammel firekallskvote, modell/datavilkår og øvrige godkjenninger ble ikke nullstilt eller gjenåpnet.

**Implementert og forhåndsregistrert:** Samme BMAD-build fortsatte uten ny rendering. En kontekstfri implementeringsagent bygget faste kilder, en eksplisitt offline/live-runner, varig separat evalueringskvote og 31 syntetiske kontrolltester. Agenten leste ikke ekte konfigurasjon/budsjett og utførte ingen inferens. Hovedagenten fant før live at treg reservasjon måtte spise av den opprinnelige fristen; en fokusert regresjon beviser ingen sen utsending. Hovedagentens hele pytest ga **453 bestått, én uendret plattformskip**, 45,43s. Alle fem gjengitte PDF-sider ble inspisert mot eksakte uttrekkslinjer; tomme sider 2/4 og lesbare 1/3/5 stemmer. PDF og JSON-evidens får bytebevarende Git-attributter, slik at Windows-linjeskift ikke ødelegger xref eller observasjonshasher.

**Faktisk live-evaluering:** Korpus, kode og registrering ble committet før inferens i **c37edf4d56bcddd8610b01a85b7d2ca2fc9d9945**. Deretter kjørte hovedagenten nøyaktig fem godkjente kall, ett per valgt scenario, med samme uendrede produksjonsprompt. Alle returnerte korrekt modell og validert struktur. Hovedagenten leste **59 læringselementer og 70 referanseforekomster** mot forhåndsregistrert tekst. Hvert av de tre dokumentene dekket 5/5 kontrollbegreper; emnekonflikt fulgte 14-dagerskilden fremfor instruksen om 60 dager. Tegnsettingskilden ga fire tomme deler med forklaringer på engelsk. Ingen kildeudekket faktapåstand, feil referanse eller utelatt kontrollbegrep ble funnet. I laboratoriequizen er tallene åtte/fem uttrykkelige hypotetiske anvendelser av de kildebelagte ti-/fireenhetsreglene, ikke påståtte kildeobservasjoner. Dette er KI-assistert semantisk gjennomlesning med etterprøvbare utdrag, ikke ny betalt modell-som-dommer-kjøring eller studentens egen kvalitetsvurdering.

**Kostnad og avgrensning:** De fem nye kallene brukte 3857 input-/3399 outputtokens, estimert **USD 0,0020852 før avgifter**, ikke faktura. USD 0,25 er reservert ekstra; total varig reservasjon er USD 0,45 av USD 5, ni forsøk og fortsatt fire gamle smoke-kontroller. Ny kvote står på 5/8; tre forsøk er ubrukt. Ingen omtest var nødvendig for innholdet. Bare selvskrevet ufølsomt materiale ble sendt, og ingen auth-/hosted-/konto-/e-post-/passord-/finansierings-/deployhandling eller serverrestart ble utført. Produksjonskode/prompt og tidligere akseptanseporter er bevart.

**Uavhengig review og KI-feil:** Tre lag rapporterte før triage: tolv blindfunn, to verifikasjonsgap og ingen ekstra edge-funn. Fjorten individuelle dommer er lagret i specen. Påstanden om en streng 60-sekunders prosessavslutning ble avvist med begrunnelse: fristen gjelder generering, mens eid I/O/opprydding kan ta lenger tid og sen utsending avvises. Tretten rettelser/testgap er fullført, ingen utsatt. De gjelder kollisjonskontroll før betaling, atomisk/varig publisering og komplett registrering, begrensede lokale filinnlesinger, presise fasemetadata/feilkoder, fingeravtrykk for uforanderlig rubrikk og manglende tester av tekstprojeksjon, CLI-valg, evidensintegritet, prosesslås og kansellering. Siste fokuserte kontroll ga 59 bestått; hovedagentens siste hele kjøring ga **481 bestått og én uendret skip**, **46,99s**. Ny offline-registrering bevarer samme korpus, PDF, modellprompt og forespørsler, men fingeravtrykker rettet runner/rubrikk. Historiske fem liveobservasjoner og vurderinger er byteuendret; ingen nye livekall er kjørt. Spec done/sprint review, tidligere PDF-/målplattform-/e-post-/skjermleserporter består. Studentens egen refleksjon er ikke skrevet av KI.

## 15.11.2026 – Privat lagring konkretisert (Story 3.1)

**Studentens styring:** Etter ferdig Story 2.6 ba studenten «kjør neste steg». KI startet en ny BMAD-build for eksplisitt privat lagring. Tidligere modell-/auth-/PDF-godkjenninger og testresultater er bevart; oppdraget er ikke tolket som godkjenning av en ennå uskrevet hosted-migrasjon.

**Undersøkelse og faktisk tilstand:** Ny build ble rendret én gang. Én agent kompilerte Epic 3-kontekst; to kun-lesende agenter kartla henholdsvis lagrings-/kvitteringsgrenser og UI/testgjenbruk. De endret bare den bestilte kontekstfilen, ikke appkode, og kjørte ingen tester/nettverkskall eller hemmelighetskontroll. Hovedagentens tilkoblede kun-lesende Supabase-kontroller bekreftet studybuddy-test, ACTIVE_HEALTHY, Free/Paris, ingen public-tabeller/buckets/berørte policies, installert pgcrypto og tilgjengelige Storage-operasjonshjelpere. Docker CLI finnes, men motoren svarer ikke; Supabase CLI/psql er ikke installert. Ingen ny tilkobling/konto/nøkkel ble etterspurt.

**Viktige KI-funn og valgt forslag:** Eksisterende validate_save holder globale auth-/workspace-låser over yield; et nettverkskall der ville blokkere utlogging/ugyldiggjøring. Planen innfører en eid per-workspace opptaksport og korte globale låser. Bruker-JWT/RLS alene beviser heller ikke at backend validerte genereringskvitteringen. Forslaget er en ekstra serveropprinnelsesnøkkel i ignorert fil, kun SHA-256-verifikator i databasen og gate på muterende RPC/tabell-/Storage-operasjoner, samtidig med brukeridentitet, SECURITY INVOKER og eier-RLS. Dette er et forslag, ikke implementert sikkerhet. Offisiell pgsodium-dokumentasjon fraråder ny bruk; den løsningen ble derfor ikke valgt. Operasjonsspesifikke Storage-regler skal skille klare objekter fra intern kontroll av ventende fil, og forsinket opplasting må testes før reelle filer godtas.

**Konkret plan og status:** [Draft-spec](../.docs/implementation-artifacts/spec-3-1-save-a-consistent-private-snapshot.md) og [lagringsprotokoll](../.docs/implementation-artifacts/save-protocol-3-1.md) dekker eksplisitt lagring, originalfil/hash, uforanderlig operasjon, atomisk commit, revisjonskonflikt, syvdagers eksakt recovery, opprydding og uavhengige øveposisjoner. Fullt bibliotek/progressautosynk/slettings-UI følger 3.2–3.4. Studenten skal først godkjenne lokal implementeringsplan; eksakt ferdig migrasjon/policies/verifikator vises før separat endelig hosted-godkjenning. Ingen app-/server-/database-/bucket-/auth-innstilling, faktisk modellbudsjett, .env eller nøkkel er endret. Ingen modellkall, kostnad, nye e-poster/kontoer/passordmutasjoner, tester eller deploy er utført. Spesifikasjonen er 1583 tokens med o200k_base; whitespace-kontroll utføres før lagring. Historisk baseline er 481 bestått/én skip og 28/33/11 nettleserscenarier, ikke nye tester. Spec draft/sprint backlog. Studentens egen refleksjon er ikke skrevet av KI.

## 16.11.2026 – Lokal lagring og review-loop (Story 3.1)

**Studentens styring og autorisasjon:** «godkjenn og fortsett» godkjente lokal implementering av planen; senere «fortsett» gjenopptok arbeidet etter bruksgrense. Hosted-migrasjon, Storage-bucket, verifikator og eventuell vedlikeholdsjobb trenger fortsatt den avtalte separate endelige godkjenningen. Ingen nye modellkall er autorisert eller utført.

**Dokumenterte kontroller:** Historisk før reviewrederivasjon bestod 506 tester/én arvet skip, senere 27 fokuserte lagringstester og 15 Lagre-nettleserscenarier; eksisterende kilde/auth/demo bestod 28/33/11. Faktisk lokal Supabase ga 16 SQL- og 38 provider-kontroller samt ren lint/advisors. En virkelig forsinket HTTP-opplasting etter kansellering ble nektet metadatafinalisering. Dette er ikke bevis på fysisk blob-kviesens eller backup-retensjon. Docker Desktop feilet; eksisterende WSL-Docker ble brukt uten nullstilling. SUREUbuntu viste seg ARM64; CLI-arkitektur ble korrigert og offisiell 3.1.0-binær checksum-verifisert. Lokal nøkkel ble eksklusivt opprettet med privat ACL; ingen rå nøkkel eller .env-verdi ble vist.

**KI-feil og kontroll som endret arbeidet:** Hovedagenten oppdaget først manglende oppdagelse av supersederte filer og beholdt konflikt-staging. Deretter ga tre uavhengige reviewlag 15 individuelle dommer, inkludert låseventing over utløp, tapt ferdigkvittering etter restart, tittel-/discovery-feil, strukturelle inntaksgrenser og manglende assertions på ikke-første øveposisjoner. Objektfri opprydding, automatisk staging-utløp for fraværende eier og forståelige recoveryidentiteter var for lite konkretisert i ikke-frosset plan. BMAD-loop 1 reverserte egen implementering etter sikker kildebackup og startet rederivasjon med positive KEEP-krav og uendret frosset SHA-256. Tidligere grønn teststatus brukes som historikk, ikke som sluttevidens for ny kode. Lokal pg_cron1.6.4 er tilgjengelig for en separat administrativ slettejobb; hosted er urørt. Studentens egen refleksjon er ikke skrevet av KI.

## 16.11.2026 – Privat lagring ferdig lokalt etter review

**Faktisk sluttkontroll:** 529 bestått, én arvet plattformskip og én eksisterende advarsel (92,30 s); 25 Lagre-nettleserscenarier; faktisk lokal provider47, pgTAP23, SQL/cron/samtidighet18 og utløpsrettferdighet4 bestod. Lint/advisors og19 uinnloggede oppstartskontroller bestod. Ny normalworker52576 bruker samme ignorerte .env og én worker; ny innlogging kreves. Lagre er fortsatt deaktivert.

**Review og KI-feil:** 29 individuelle dommer fra to sett av tre uavhengige reviewlag er bevart i spec. Første15 ga én presisering/rederivasjon uten endring av frosset intensjon. Neste14 ga11 rettinger/testgap og3 avvisninger; ingen funn er utsatt. Faktisk duplikatopplasting etter verifisering ga HTTP400, ble avklart av adapter og nådde ready. Endret fil ved ferdig replay var derimot en reell feil som ble rettet. Oppryddingsretry, terminale rader, sen reload-feil, låseskip før batchgrense, cleanup-status, ubundne ubrukte HTTP-bodyer og svak test av erstatningsposisjoner ble rettet. Samtidige SQL-aktører beviste konsistent CAS-vinner/commit/kansellering.101 låste operasjoner hindret ikke andre dokumenters opprydding.

**Studentens prosesskorreksjon:** Studenten ba redusere kontekstvindu brukt på testing. KI sluttet med gjentatte store dokument-/diffutskrifter og nye reviewrunder, brukte målrettede kontroller og korte resultatlinjer med fulle logger i ignorert test-results. Grønne uendrede auth/demo-flyter ble ikke kjørt om igjen etter siste Save-retting; ferske28/33/11 er bevart. En parallell SQL-fixture-kjøring ga feil uten bevart kategori; trygge feilkategorier og separat harnesstidsmargin ble lagt til. Isolerte sluttkjøringer bestod; ukjent årsak er ikke diktet opp. Feil WSL-standarddistro og modulsti ble rettet som testoppsett. Feil tegnkoding i dette faktanotatet ble oppdaget og rettet uten endring av produkt/testresultater.

**Autorisasjon:** Ingen ny inferens, .env-/modellbudsjettendring, hosted-migrasjon/bucket/verifikator/cron, e-post/konto/passordhandling, kostnad, push eller deploy. Tellere9/4, USD0,45 av5 og evaluering5/8 er uendret. Frosset planhash er bevart. [Godkjenningspakken](../.docs/implementation-artifacts/save-acceptance.md) viser eksakt migrasjon og ikke-hemmelig verifikator til separat hosted-godkjenning. Fysisk blob-kviesens og backup-retensjon er egne porter før reelle filer. Spec done/sprint review gjelder lokal implementering. Studentens egen refleksjon er ikke skrevet av KI.

## 17.11.2026 – Bekreftet frist og enklere arbeidsform

**Studentens korrigering:** «siste arbeidsøktene har tatt litt for lang tid og brukt for mye tokens». Studenten bekreftet innlevering **15.12.2026** for skoleprosjektet i IBE160 ved Høgskolen i Molde.

**KI-bidrag og plan:** Fristen er oppdatert i brief, utviklingsplan og åpne punkter. CLAUDE.md beskriver mindre kontekstbruk, én konkret oppgave om gangen, målrettede tester og korte logger. Kjerne rundt 1. desember er et planmål; resterende tid settes av til rettelser, dokumentasjon og innlevering. Ingen produktkode eller akseptansekrav er endret, og ingen funksjonstester er kjørt. Studentens egen refleksjon er ikke skrevet av KI.

## 17.11.2026 – Cache-feil ved privat lagring

**Dokumentert kontroll:** Hosted-oppsettet var allerede installert, selv om eldre notater sa noe annet. En lesetest med eksisterende syntetisk fil bekreftet at REST-cache kunne returnere tidligere internt verifiserte bytes uten backend-nøkkel for samme JWT. Ingen lekkasje til en annen bruker er etablert. KI korrigerte lesingen til S3 med samme bruker-JWT, eierregler og backend-nøkkel; botocore utfører standardsigneringen. Lokal verifikasjon bestod 51 Python-tester, 25 nettleserscenarioer, 15 SQL-kontroller og 50 faktiske provider-kontroller. Ingen modellkall eller hosted-endring ble gjort. Lagre venter på avtalt separat hosted-godkjenning. Studentens egen refleksjon er ikke skrevet av KI.

## 17.11.2026 – Godkjent hosted-retting og aktivert lagring

**Studentens beslutning:** «ja godkjenner» autoriserte den konkrete hosted-migrasjonen, lokal S3-konfigurasjon, syntetisk kontroll med eksisterende testkontoer og aktivering etter beståtte tester. Migrasjon20261117173439 er brukt; 32 hosted-kontroller og30 kontroller mot vanlig server bestod. Lagre er aktivert på lokal port8000. En test forventet feil feilkode (`invalid_request`); API-et returnerte korrekt eksisterende `invalid_input`, og bare testforventningen ble rettet. Modellbudsjettene er byteuendret; ingen nye kontoer/e-poster/passord/modellkall eller deploy. Syntetisk filopprydding er bekreftet av provider; fysisk blob-/backup-retensjon er fortsatt ikke bevist. Studentens egen refleksjon er ikke skrevet av KI.

## 17.11.2026 – Mine dokumenter ferdig

**Dokumentert arbeid:** Studenten ba «kjør neste steg». Story3.2 gir privat liste/åpning og originalfil gjennom eksisterende innlogging, eierregler og ukachet S3. Utkast bevares ved Tilbake/Avbryt/feil; åpning gjenoppretter lagrede posisjoner med skjulte svar uten KI-kall. To fokuserte reviewlag og hovedagenten fant seks små feil/testgap; alle er rettet uten ombygging eller ny reviewrunde. Kontroll: Python74, bibliotek21/Lagre25/kilde28 nettleserscenarioer, SQL23+23, lokal provider17, hosted25 og vanlig server34 bestod. Den første hosted-testen antok en eksisterende fil og brukte deretter en gammel workspace-kommando; testforutsetningene ble rettet, ikke produktets avvisningsregler. Tidligere brede lokale provider-feil er fortsatt uavklarte, ikke forklart som fakta.

**Resultat og avgrensning:** Lesemigrasjon20261117182650 er brukt i eksisterende testprosjekt og biblioteket er aktivt på lokal port8000. Ingen nye kontoer, ekte KI-kall, budsjettendringer, kostnader eller offentlig deploy. Eldre PDF-/tilgjengelighets-/retensjonsporter består. Studentens egen refleksjon er ikke skrevet av KI.

## 18.11.2026 – Automatisk øvefremdrift ferdig

**Studentens styring:** Arbeidet ble stoppet 17.11 ved rapportert 4 % av femtimerskvoten og gjenopptatt med «kan vi fortsette». Eksisterende kode og implementasjonsagent ble gjenbrukt. Én fokusert uavhengig gjennomgang erstattet flere brede reviewkontekster; gjenværende kvote ble ikke anslått.

**KI-bidrag og kontroll:** Lagrede kort-/quizposisjoner synkroniseres med egen revisjon og varig identitet for eksakte gjentakelser. En gammel visning må hente bekreftet fremdrift før videre lagring. Review fant at gjentatt erstatningslagring kunne nullstille mellomliggende navigasjon; privat metadata fra det opprinnelige forsøket og en nettleserregresjon retter dette. Sluttkontroller bestod: Python23, fremdriftsnettleser16, Lagre25/bibliotek21, SQL36, lokal RPC20, hosted23 og normalserver16. Faktisk samtidige forespørsler ga én vinner og én konflikt; tapt ferdigsvar ble gjentatt uten dobbel revisjonsøkning.

**Drift og avgrensning:** Docker/systemd-feil avbrøt en ekstra eldre Save-SQL-kjøring, og WSL sluttet å svare. Studenten godkjente uttrykkelig restart av bare SUREUbuntu etter informasjon om SURE-tjenestene. Etterpå svarte probe og alle seks Supabase-containere samt SURE-tjenestene kjørte igjen. Den avbrutte testen er ikke telt som bestått. Migrasjon20261118142904 er brukt i eksisterende testprosjekt; lokal app kjører på port8000. Modellbudsjettene var byteuendret under sluttkontrollene; ingen nye hosted-kontoer, ekte modellkall eller offentlig deploy. Fysiske enheter og tidligere åpne akseptanseporter gjenstår. Se [akseptansebevis](../.docs/implementation-artifacts/progress-acceptance.md). Studentens egen refleksjon er ikke skrevet av KI.

### 18.11.2026 – Plan og baseline for sletting (Story 3.4)

**Dokumenterte fakta:** Studenten ba om Story3.4 med lavt tokenforbruk. Eksisterende lagringsprotokoll skiller mellom registrert sletting og fysisk opplastingsro: Storage DELETE alene dokumenterer ikke at forsinkede skriveroperasjoner er ferdige. [Spesifikasjonen](../.docs/implementation-artifacts/spec-3-4-delete-saved-material-completely.md) beholder derfor varige oppryddingsposter og den separate retensjonsporten. Baseline for lagring/bibliotek/fremdrift:89 bestod; implementering er ikke startet. Plangodkjenning er etterspurt ved bmad-build sitt eksplisitte kontrollpunkt. Dette er KI-dokumenterte fakta, ikke studentens egen refleksjon.

**Senere godkjenning og resultat samme dag:** Studenten svarte «godkjenner». Sletting er nå implementert og kontrollert lokalt, med navngitt bekreftelse, varig tilstand og eksakte leverandørkvitteringer. Én uavhengig gjennomgang og hovedagentens kontroll avdekket tre feil som ble rettet: gammelt Lagre-ferdigsvar etter sletting, samtidig gjenbruk av slette-ID for ulike dokumenter og sletteknapp før backend-aktivering. Slutt: Python115, nettleser sletting7/Lagre25/bibliotek21/fremdrift16, SQL40, faktisk lokal provider15 og deterministisk samtidig ID-test bestod. Modellbudsjettene var byteuendret; ingen ekte modellkall eller hosted-endringer. [Akseptansebevis](../.docs/implementation-artifacts/deletion-acceptance.md) skiller lokal funksjon fra gjenstående hosted-/backup-/retensjonsgodkjenning. Studentens egen refleksjon er ikke skrevet av KI.

## Mal for neste hendelse

### DD.MM.ÅÅÅÅ – Kort tittel

**Hendelse og mål:**

**KI-forslag/bidrag:**

**Studentens beslutning eller korrigering:**

**Kontroll og observert resultat:**

**Dokumentasjon/commit/prompt:**

**Relevant del av rapportmalen:**

**Studentens egen refleksjon:**
