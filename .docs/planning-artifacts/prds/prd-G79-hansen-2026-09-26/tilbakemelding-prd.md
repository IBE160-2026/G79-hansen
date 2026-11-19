# Tilbakemelding på PRD

| | |
|---|---|
| **Gruppe** | G79 – G79-hansen |
| **PRD vurdert** | `.docs/planning-artifacts/prds/prd-G79-hansen-2026-09-26/prd.md` (status `final`, sist endret 2026-11-11, commit 11e89f4). `addendum.md` i samme mappe er lest som kontekst. |
| **Dato** | 2026-11-12 |
| **Type** | Formativ tilbakemelding, ikke karakter |

## 1. Samlet inntrykk

PRD-en har uvanlig gode akseptansesjekker og ærlige avgrensninger, og kvalitetsmålene (NFR-1) fra briefen er videreført. Risikoen er omfanget og formen. Prosjektet har vokst fra «enkel» til innlogging, lagring, flerenhets-synkronisering og gjenopptakelse av fremdrift, mens PRD-en mangler en tydelig bruker, tese og glossar, og har blitt en tett tekst der krav, arkitektur og endringshistorikk er blandet.

## 2. Dette fungerer godt

1. **Testbare sjekker som kan bli testtilfeller direkte.** «Input-limit acceptance check» (30 000 tegn godtatt, 30 001 avvist; 40-siders PDF godtatt, 41 avvist) og PDF-sjekken («readable text on pages 1 and 3, a blank page 2 and an image-only page 4») er konkrete nok til å kodes uten tolkning.
2. **Kontroll av KI-resultatet er bygd inn.** NFR-1 («three documents, identifying five central concepts … before generation … at least four of five») har motmål: «coverage must never be improved by adding unsupported items». I tillegg skiller PRD-en «insufficient material» fra teknisk feil (NFR-2).
3. **Ærlig om hva som ikke er bestemt.** Tabellen «Deferred decisions» har eier og tidspunkt per beslutning, og «No paid service, public deployment, cloud resource or real private upload is authorized» (addendum). Demomodus uten nøkkel (NFR-4) løser kjørbarhet for sensor.

## 3. Oversikt per dimensjon

| Dimensjon | Vurdering | Kort begrunnelse |
|---|---|---|
| Beslutningsklarhet | god | Valg er datert og tatt («Explicit Save is selected»), åpne punkter har eier. Frist og leverandør er fortsatt uavklart. |
| Substans | god | Innholdet er prosjektspesifikt, ikke boilerplate. Det mangler en konkret bruker utover én setning. |
| Strategisk sammenheng | svak | Ingen uttalt tese. Innlogging/synk-funksjonene er lagt til uten at det vises hvordan de tjener kjernen (oversikt og øving). |
| Testbarhet | god | Sterke sjekker for inndata, grenser og feil. FR-3/FR-4 er vage, og sjekkene er spredt utover dokumentet. |
| Scope og avgrensning | god | Utelatelser er eksplisitte (OCR, eksport, flere dokumenter). Realismen for ett semester og én person er svak. |
| Brukbarhet for neste fase | svak | Ingen glossar-seksjon, ingen brukerreiser, krav og arkitekturdetaljer blandet. ID-ene er ryddige. |
| Formtilpasning | svak | Over-formalisert på auth/synk (kvitteringer, låsing), under-formalisert på visjon og bruker. |

## 4. Viktigste forbedringer

### 4.1 Omfanget er stort for ett semester og én person
- **Alvorlighet:** høy
- **Hvor:** «Login and workspace reset», FR-8 til FR-12, «Cross-device conflict and network acceptance check»
- **Problem og hvorfor det betyr noe:** Briefen ble vurdert som «enkel» og anbefalte *én* avgrenset utvidelse. PRD-en har nå konto med passordgjenoppretting, Supabase RLS, lagring, automatisk lagring av fremdrift, konfliktvarsler på tvers av enheter og to-brukertester, i tillegg til hele kjernen (tekst + PDF + live KI). Kjernen skal være ferdig «around 1 December». Det finnes ingen prioritert rekkefølge hvis tiden ikke strekker til, og «do not silently drop existing core quality goals» er ikke en plan.
- **Forslag:** Del kravene i tre nivåer og skriv det inn i PRD-en: **Må** (FR-1 til FR-7, FR-9, NFR-1 til NFR-4 med demomodus), **Bør** (FR-8, FR-10 til FR-12 med enkel innlogging og eksplisitt lagring), **Hvis tid** (automatisk fremdrift på tvers av enheter, konfliktvarsel «Hent siste fremdrift», EXT-1). Eksempel: «Hvis 1. desember passeres uten at kjernen består sjekkene, utsettes fremdriftssynk til v2.»

### 4.2 Mangler tydelig bruker, tese og glossar
- **Alvorlighet:** høy
- **Hvor:** «Goal and boundaries»; «Completion and terminology»
- **Problem og hvorfor det betyr noe:** Brukeren er én setning («a student preparing for a test with about 40 lecture slides», «not validated research»). Tilbakemeldingen på briefen ba om problem, primærbruker, forskjell fra en vanlig chatbot og visjon. Det er ikke løftet inn her. Uten dette har UX, stories og tester ingen felles forståelse av hvem som skal få hva ut av hva. Begrepene (source, session, workspace, saved document, generation) er definert i ett avsnitt til slutt, og «session» brukes både for innlogging og arbeidsflate.
- **Forslag:** Legg til (a) en tese på 2–3 setninger, for eksempel «Studenten får på minutter et kildefestet utgangspunkt for repetisjon som er raskere og mer etterprøvbart enn å lime tekst inn i en chatbot», (b) ett navngitt brukerscenario med inngang, steg og hva som viser at verdien er levert (UJ-1), og (c) en glossar med én linje per begrep, der «session» deles i «login session» og «workspace».

### 4.3 FR-3, FR-4 og FR-8 er ikke testbare eller er overlastet
- **Alvorlighet:** medium
- **Hvor:** FR-3 «Summary points accurately describe supplied material»; FR-4 «meets the agreed coverage target below»; FR-8
- **Problem og hvorfor det betyr noe:** «Accurately» kan ikke testes uten et mål. FR-8 samler seks-sju krav i ett avsnitt (opprettelse, innlogging, gjenoppretting, tilgangskontroll, utlogging, ikke avsløre kontoer), så én story kan ikke «bli ferdig» tydelig.
- **Forslag:** FR-3: «Hvert sammendragspunkt kan knyttes til minst én kildereferanse, og ingen punkt påstår noe som ikke står i kilden; kontrollert på de tre testdokumentene (NFR-1).» Del FR-8 i FR-8a opprett/logg inn/logg ut, FR-8b gjenoppretting av passord, FR-8c eierskap (to-brukertesten), hver med egne konsekvenser.

### 4.4 KI-kostnad og usikre svar mangler tall
- **Alvorlighet:** medium
- **Hvor:** «Deferred decisions» («API access/budget, request limits»); NFR-2
- **Problem og hvorfor det betyr noe:** Ingen øvre grense for kostnad eller antall kall, og PRD-en sier ikke hva appen gjør når modellen svarer med noe som ikke er kildestøttet (kun at kontrollen er manuell i NFR-1). Det gjør live-integrasjonen vanskelig å teste og kan gi uventet regning.
- **Forslag:** Sett en grense nå, for eksempel «maks 3 genereringer per bruker per time og et samlet testbudsjett på X kr; ved overskridelse vises meldingen …». Legg til et FR for atferd: «Et element uten kildereferanse vises ikke, og seksjonen forklarer at underlaget var for tynt.»

### 4.5 Arkitektur og endringslogg ligger i kravteksten
- **Alvorlighet:** medium
- **Hvor:** FR-10-avsnittet «Explicit Save is selected …»; «Scope revision – 2026-11-10»; «Save admission/recovery acceptance check» (henviser til AD-6, AD-8, som ikke er definert i PRD-en)
- **Problem og hvorfor det betyr noe:** Signerte kvitteringer, stagede operasjoner, 7-dagers gjenopptak og utløpstider er løsninger, ikke krav. De gjør PRD-en på ca. 3 400 ord tung å lese, og avsnittene har dato-merker («Confirmed 2026-11-11») som hører hjemme i en logg.
- **Forslag:** Flytt mekanismene til arkitekturdokumentet og behold kun det brukeren ser: «Hvis noen forsøker å lagre et resultat som er endret etter generering, avvises lagringen med en melding.» Samle akseptansesjekkene under hvert FR, og la «Scope revision» bli en kort endringslogg.

## 5. Mekaniske funn

- FR-1 til FR-12, NFR-1 til NFR-5 og EXT-1 er sammenhengende og unike. Det finnes ingen SM-ID-er (suksessmål ligger i NFR-1) og ingen UJ-ID-er, så krav kan ikke spores til brukerreiser.
- Begrepsdrift: «session» (innlogging, nytt arbeidsområde), «document», «source» og «material» brukes om hverandre.
- Henvisninger til AD-6, AD-7, AD-8 løses kun i et annet dokument. Ingen `[ASSUMPTION]`-merking; antakelser står som tekst («exact date unconfirmed»).

## 6. Før dere går videre

**Må avklares før videre UX/arkitektur/epics:** prioriteringsnivå per krav (4.1); tese, bruker og glossar (4.2); tall for KI-kostnad og kallgrense (4.4); faktisk frist.

**Kan vente:** valg av PDF-bibliotek, hosting og region, e-postoppsett og EXT-1.

**Oppfølging av briefen:** *delvis.* Kvalitetsmålene er beholdt, demomodus og README med egen nøkkel er med (NFR-4), og beslutningene er tatt. Problem, primærbruker, differensiering og visjon er ikke løftet inn. Dere har tatt utvidelsen «innlogging og lagring» som foreslått, men i et omfang som er langt større enn én avgrenset utvidelse.

## 7. Refleksjonsspørsmål

1. Hvilke deler av autentiserings- og synkkravene (kvitteringer, låsing, 7-dagers gjenopptak) foreslo KI, og hvilke ville dere selv ha valgt for en studentapp? Hva gjorde dere for å kontrollere at de trengs?
2. Hvis dere bare får tid til halvparten av FR-8 til FR-12, hvilken halvdel gir studenten mest verdi, og hvordan ville PRD-en vise det valget?

_Vurdert mot kvalitetsrubrikken i bmad-prd. Dette er veiledning, ikke sensur._
