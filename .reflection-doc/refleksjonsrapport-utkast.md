# Refleksjonsrapport – StudyBuddy

**Arbeidsutkast19.11.2026, laget med KI-støtte. Ikke ferdig innleveringsrapport.**
Dette dokumentet samler dokumenterbare prosjektfakta etter rapportmalen.
Felt merket **Din refleksjon** skal fylles med studentens egne erfaringer og
vurderinger. Teksten påstår ikke hva studenten har lært, følt eller forstått.
Opplysninger og vurderingskrav må kontrolleres før innlevering15.12.2026.

## 1. Gruppeinformasjon

- Prosjekt/repo: G79-hansen – StudyBuddy.
- Emne: IBE160 Programmering med KI, Høgskolen i Molde.
- Student: Fredrik **[fyll inn korrekt navn og student-ID etter kravene]**.
- Endelig rapportdato: **[fyll inn]**.

## 2. Utviklingsprosessen

### 2.1 Prosjekt og mål

StudyBuddy skal gjøre kursmateriale om til sammendrag, forklarte begreper,
flashcards og quiz med kildehenvisninger. Tekst og tekstbaserte PDF-er støttes;
OCR og tolkning av figurer/tabeller er avgrenset bort. Henvisninger gjør at
brukeren kan kontrollere svarene, men er ingen garanti for korrekt innhold.

Det finnes to forskjellige bruksformer. Den lokale demoen bruker faste
eksempeldata/svar uten nøkler eller konto. Den separate live-modusen har
modellgenerering, Supabase-innlogging, privat bibliotek, lagring, fremdrift og
sletting. Demoen dokumenterer ikke at vilkårlige dokumenter kan behandles
uten modelltilgang. [README](../README.md) beskriver oppstart og grensene.

### 2.2 Arbeidsmetodikk

BMAD ble brukt til product brief, PRD, arkitektur og epics/stories.
KI-agenter bidro med planlegging, kode, tester, gjennomganger og dokumentasjon.
Studentens beslutninger og korrigeringer er lagret sammen med resultater i
[sesjonslogger](../.logs/fredrik/issues.md) og
[refleksjonsnotater](refleksjonsnotater.md). Git-historikken gir spor til
endringene. Dokumentert agentaktivitet er ikke i seg selv bevis for studentens
egen kontroll eller forståelse; det må forklares med konkrete eksempler.

**Din refleksjon:** Beskriv hvordan du valgte oppgaver og kontrollerte KI-ens
arbeid. Velg én faktisk instruksjon du ga, hva KI foreslo, og hva du selv
godtok eller korrigerte. Oppgi kilde til prompt/logg.

### 2.3 Teknologi og faser

Backend bruker Python3.13/FastAPI; grensesnittet bruker HTML, CSS og JavaScript.
Supabase Auth/Postgres/private Storage brukes i live-modus, med eksisterende
Free-prosjekt i Paris. Modellintegrasjonen bruker OpenAI. Avhengigheter er
låst med uv og package-lock. Node/Playwright brukes til nettleserkontroller,
men er ikke nødvendig for at sensor skal starte demoen.

Arbeidet gikk fra planlegging og fast demo til PDF-/modellgenerering,
innlogging og privat lagring/bibliotek/fremdrift/sletting. Hosting-/backuparbeid
tok etter hvert stor plass.19.11 ba studenten om mindre omfang. Den avtalte
[avgrensningen](../.docs/implementation-artifacts/leveranseavgrensning-2026-11-19.md)
prioriterer lokal skoleleveranse og beholder implementerte Supabase-funksjoner.
Offentlig lenke og videre driftsautomatisering er utsatt/valgfritt.
Arbeidsmål er kjerne1.12 og samlet pakke8.12; innleveringsfristen er15.12.

## 3. Utfordringer og løsninger

### 3.1 Kildebasert modellinnhold

Prosjektet må kontrollere både innhold og henvisninger. Evalueringen bruker
tre dokumenter og fem sentrale begreper per dokument, identifisert før
generering. Kontrollert innhold skal være støttet av kilden, og feilhenvisning,
manglende begreper og oppdiktet innhold vurderes separat. Dette er utvalgsbasert
evidens; resultatene kan ikke generaliseres til alle PDF-er eller fag.

**Din refleksjon:** Velg ett dokumentert kvalitetseksempel. Forklar hva du
kontrollerte selv, og om kildehenvisningene hjalp deg å oppdage feil.

### 3.2 Lagring og flere åpne visninger

Lagring krevde mer enn en lagringsknapp: kilden og resultatene må høre til
riktig bruker, fremdrift skal overleve gjenåpning, og en gammel fane må ikke
overskrive nyere fremdrift. Arkitekturen beskriver eierkontroll og håndtering
av foreldede oppdateringer. Eksisterende tester og logger inneholder evidens;
ingen full ny produksjonsakseptanse hevdes i dette utkastet.

**Din refleksjon:** Forklar med egne ord forskjellen på Ny økt, Lagre og
Slett. Beskriv hvilke deler av løsningen du kan forklare uten KI-hjelp.

### 3.3 Omfang og KI-feil

Studenten påpekte at hosting/backup var blitt for omfattende. Dette førte til
en enklere leveranseplan. Et konkret agentproblem var å forveksle Windows-
sandkassekontoen med den virkelige operatøren ved filtilgang; feilen ble
identifisert og rettet før nøkler ble skrevet. Et annet var at stopp av en
oppstartsprosess etterlot kontrollserveren, som deretter ble identifisert og
stoppet separat. Dette viser behovet for å kontrollere faktisk resultat,
ikke bare at en kommando ble kjørt.

**Din refleksjon:** Hvordan påvirket omfanget tiden og oversikten din? Hva
ville du avgrenset tidligere? Skill egen erfaring fra agentens beskrivelse.

## 4. Kritisk vurdering av KI

### 4.1 Fordeler

Loggene viser konkrete KI-bidrag til sammenhengende krav/kode, automatiserte
kontroller, dokumenterte feilkategorier og sporbare rettelser. Dette er
eksempler å vurdere, ikke en ferdig konklusjon om læring eller spart tid.

**Din refleksjon:** Hvilket bidrag var mest nyttig for deg, og hvorfor?
Bruk ett konkret før/etter-eksempel.

### 4.2 Begrensninger

Prosjektet inneholder også unødvendig omfattende driftsarbeid, feilaktige
antakelser om miljøet og tester som krevde korrigering. En kontroll kan
bestå i installert miljø uten å bevise ren oppstart. Derfor ble det laget en
separat kopi med nytt virtuelt miljø. Alle47 låste pakker ble installert, og
demooppstart/faste svar virket, men Python/uv og mulig pakkebuffer fantes
allerede på samme Windows-PC. Begrensningen ble dokumentert.

**Din refleksjon:** Når stolte du for mye eller for lite på KI? Hvordan
oppdaget du det, og hva gjorde du selv?

### 4.3 Med og uten KI; samlet vurdering

**Din refleksjon:** Hvilke deler ville du kunnet løse uten KI, og hvilke
ville krevd mer læring/tid? Unngå å oppgi tidsbesparelser du ikke har målt.
Forklar om KI samlet sett hjalp deg, og hva som begrunner vurderingen.

## 5. Etiske implikasjoner

### 5.1 Ansvar, eierskap og transparens

KI-bidrag dokumenteres i logger og dette utkastet. Det fritar ikke studenten
fra å kontrollere den innleverte teksten og koden. Bruk av eksternt materiale,
programvare og kilder må framgå etter emnets krav.

**Din refleksjon:** Hva mener du at du selv har ansvar for når KI skriver
kode eller tekst? Hvordan vil du gjøre egen innsats og KI-bidrag tydelige?

### 5.2 Læring, kompetanse og arbeidsliv

**Din refleksjon:** Hva har du faktisk lært, og hva trenger du mer øvelse i?
Hvordan tror du KI påvirker hvilke ferdigheter du ønsker å utvikle? Dette
skal være din begrunnede vurdering, ikke en faktapåstand om framtiden.

### 5.3 Datasikkerhet og personvern

Den nøkkelfrie demoen bruker syntetiske eksempeldata. Nylige oppstarts- og
brukskontroller gjorde ingen ekte modell-, e-post- eller providerkall.
Live-modus bruker eksterne tjenester og er separat konfigurert. Hemmeligheter
og lokale tilstandsfiler holdes utenfor Git. Offentlig drift, komplett
backup/restore og reelle private data har fortsatt åpne kontrollpunkter.

**Din refleksjon:** Beskriv hvilke data du selv har delt med KI-verktøy og
tjenester gjennom prosjektet, og hvordan du vurderte dette. Ikke anta at
demoens begrensninger beskriver all tidligere prosjektbruk.

## 6. Teknologiske implikasjoner

### 6.1 Kvalitet, vedlikehold og kontroll

Avgrensede lag for tjenester, adaptere og grensesnitt samt låste avhengigheter
gjør det mulig å undersøke deler av løsningen separat. Tester er likevel ikke
det samme som forståelse eller full dekning.19.11 fant visuell inspeksjon en
gammel statuslinje ved fanebytte til quiz, selv om fire instrumenterte
tastatur-/visningspunkter hadde bestått. Feilen ble deretter rettet med
regresjonskontroll av status, fokus og bevart øvingstilstand. Funn og grenser er dokumentert i
[brukskontrollen](../.docs/implementation-artifacts/usability-check-2026-11-19.md).

**Din refleksjon:** Hvor lett er det for deg å finne og endre riktig sted i
koden? Beskriv én feil du undersøkte, eller én kodebit du fortsatt ikke forstår.

### 6.2 Beste praksis og framtidig arbeid

**Din refleksjon:** Hvilke arbeidsregler ville du beholdt i neste prosjekt?
Forklar hva du vil gjøre enklere. Knytt anbefalingene til egne eksempler.

## 7. Konklusjon og læring

**Din refleksjon – fylles etter at du har skrevet delene over:**

1. Viktigste konkrete lærdom: **[din tekst]**.
2. Viktigste endring du ville gjort ved ny start: **[din tekst]**.
3. Viktigste råd til andre studenter: **[din tekst og begrunnelse]**.

Avslutt med din samlede vurdering av prosjektet og egen utvikling. Ikke
presenter utsatt hosting, åpen tilgjengelighetskontroll eller uferdig rapport
som ferdig. Rapportmalens forventede3000–5000 ord må sammenholdes med faktisk
oppgavetekst; dette kortere faktagrunnlaget oppfyller ikke lengdekravet alene.

## 8. Vedlegg og sporbarhet

- [Original rapportmal](reflection-report-template.md)
- [Refleksjonsnotater og studentens korrigeringer](refleksjonsnotater.md)
- [Oppgaver/status og tilhørende logger](../.logs/fredrik/issues.md)
- [Leveransesjekkliste](../.docs/implementation-artifacts/delivery-checklist-2026-11-19.md)
- [README med nøkkelfri oppstart](../README.md)
- [Faglærertilbakemelding](../.docs/planning-artifacts/briefs/brief-G79-hansen-2026-09-26/tilbakemelding-product-brief.md)

Før innlevering: kontroller kravene, faktapåstandene, lenkene og KI-merking;
fyll egne refleksjoner og korrekt studentinformasjon. Velg eventuelle
skjermbilder bevisst; filer i ignorert test-results er ikke automatisk del av
innleveringspakken.
