# Tilbakemelding på product brief

| | |
|---|---|
| **Gruppe** | G79 – G79-hansen |
| **Product brief** | `.docs/planning-artifacts/briefs/brief-G79-hansen-2026-09-26/brief.md` (commit `21b3b95`). `development-plan.md` i samme mappe og PRD-utkastet er lest som kontekst. |
| **Tilbakemelding fra** | Faglærer i IBE160 (utarbeidet med KI-støtte) |
| **Dato** | 2026-10-06 |

## Samlet vurdering

- **Godt utgangspunkt med justeringer.** Gruppen kan gå videre og innarbeide punktene under.

**Det som er bra:**

1. Realistisk og gjennomtenkt prioritering. Dere har valgt forslag 1, prioriterer gjennomførbarhet som én nybegynner, og bygger i små trinn: tekst til sammendrag først, deretter de andre læringsfunksjonene og PDF til slutt. Utviklingsplanen har en observerbar sjekk for hvert trinn.
2. Svært gode kvalitetsmål. Dere bruker tre dokumenter med fem sentrale begreper hver, identifisert *før* generering, krever at alt kontrollert innhold er støttet av kilden, og at minst fire av fem begreper er med. Det er konkret, etterprøvbart og løser problemet med å kontrollere KI-ens svar.
3. Tidlig PDF-eksperiment med en presis test (tre sider med tom midtside og en side som bare er bilde). Det viser at dere tar risikoen ved PDF-lesing på alvor.

**De viktigste endringene:**

1. **Briefen bør dekke malens deler.** Den mangler egne avsnitt for problemet (med en konkret student og situasjon), hva som skiller løsningen fra å lime tekst inn i en vanlig chatbot, hvem den er for, og visjon. «Students across subjects» er bredt. Beskriv én typisk bruker og brukssituasjon.
2. **Lukk de åpne spørsmålene selv i stedet for å vente.** Briefen har status «pending-assessment-criteria» og flere punkter som venter på faglærer. Sensorveiledningen for del 1 beskriver hva som vurderes. Prosjektforslaget knytter innlogging til at materiale «lagres eller deles». Midlertidige økter uten lagring er derfor et legitimt designvalg som dere kan ta og begrunne i briefen. Det samme gjelder tekstbaserte PDF-er uten tolkning av tabeller og figurer. Skriv valgene inn som beslutninger med begrunnelse.
3. **Vurder én avgrenset utvidelse for å løfte vanskelighetsgraden.** Forslag 1 er vurdert som enkelt, og dere har valgt bort poeng, flervalg og lagring. Det gir stor sjanse for å bli ferdig, men lite å vise utover kjernen. Når kjernen virker, kan for eksempel lagring av økter med innlogging eller automatisk retting av quiz være en tydelig utvidelse.

## Vanskelighetsgrad og gjennomførbarhet

### Vurdert vanskelighetsgrad

- **Enkel**

**Sammenlignbart med:** 1) AI Study Buddy (enkel). Det er dette forslaget dere har valgt, og v1 slik den er beskrevet holder seg innenfor det.

**Begrunnelse:**

| Faktor | Nivå (lav / middels / høy) | Kommentar |
|---|---|---|
| Domenelogikk – hvor mange og hvor kompliserte regler og beregninger må stemme? | lav | Få regler: detaljnivå, språk, avsnitts- og sidereferanser. Referansene som må bevare fysisk sidenummer er den mest krevende delen. |
| Datamodell – antall entiteter og relasjoner mellom dem | lav | Ett dokument per økt, uten lagret historikk. Ingen database er foreslått. |
| Brukere, roller og innlogging | lav | Ingen innlogging med midlertidige økter. Det må være et bevisst og begrunnet valg. |
| KI-funksjonalitet i appen, f.eks. kall til språkmodell, prompts i koden og håndtering av usikre svar | middels | Sammendrag, begreper, flashcards og quiz med kildehenvisninger. Kravet om at alt skal være støttet av kilden gjør promptarbeidet viktig. |
| Integrasjoner og eksterne tjenester, f.eks. API-er, betaling og e-post | lav | Ett skybasert LLM-API. |
| Sanntid, samtidighet eller flere brukere som påvirker hverandre | lav | Ingen. |
| Filhåndtering, f.eks. opplasting, PDF-lesing og eksport | middels | Opplasting av tekst og PDF med riktige sidereferanser. Det er planlagt et tidlig eksperiment, og det er riktig. |
| Sikkerhet og personvern | lav | Studentens eget kursmateriale sendes til en skytjeneste. Dere har allerede notert at dette må avklares før bruk. |

**Hva vanskelighetsgraden betyr for dere:**

- _Enkel:_ Et enkelt prosjekt gir stor sjanse for å bli ferdig. Vanskelighetsgraden inngår likevel i vurderingen, så for å nå helt opp må dere vise mer i gjennomføringen. Det betyr særlig et gjennomarbeidet design, grundig testing, en tydelig dokumentert prosess og en README som virker. Kvalitetsmålene og utviklingsloggen dere planlegger er et godt utgangspunkt for nettopp dette.

### Gjennomførbarhet med BMAD og Claude Code

Dere skal planlegge med BMAD (product brief → PRD → arkitektur → epics og stories) og implementere med Claude Code. Vurderingen under tar hensyn til at det må være tid til hele denne flyten, og til testing, retting og README til slutt.

| Spørsmål | Vurdering (OK / risiko / stor risiko) | Kommentar |
|---|---|---|
| **Tid og omfang** – kan v1 realistisk bli ferdig og stabil i løpet av semesteret, med tid til flere iterasjoner? | OK | Små trinn med sjekk for hvert, og to uker satt av til retting før fristen. Det er realistisk for én person. |
| **BMAD-flyten** – er briefen konkret nok til at PRD, arkitektur og stories kan lages uten store hull, og blir det overkommelig mange stories? | risiko | PRD-utkastet bygger godt på briefen, men flere beslutninger står åpne og venter på avklaring. Ta beslutningene, slik at PRD og arkitektur kan ferdigstilles. |
| **Egnet for Claude Code** – bruker løsningen en vanlig, godt dokumentert teknologistakk som Claude Code håndterer godt, eller krever den nisjeteknologi, spesialmaskinvare eller mye manuell konfigurasjon? | OK | Python og Streamlit med ett PDF-bibliotek og ett LLM-API er en enkel og godt dokumentert stakk. |
| **Kontroll på KI-ens arbeid** – kan gruppen selv avgjøre om koden gjør det riktige? Krever domenet kunnskap gruppen ikke har, f.eks. avanserte beregninger eller fagregler, så er det vanskelig å kvalitetssikre. | OK | Kvalitetsmålene med forhåndsidentifiserte begreper og kildesjekk gir en konkret måte å kontrollere KI-ens svar på. |
| **Testbarhet** – finnes det tydelige regler og forventede resultater som tester kan skrives mot? | OK | Tom input, feil i KI-kall, sidereferanser i PDF og begrepsdekning gir tydelige testtilfeller. |
| **Kjørbar for sensor** – kan appen kjøres lokalt etter README, uten gruppens nøkler, betalte kontoer eller egen infrastruktur? | risiko | Appen krever en LLM-nøkkel. Dere planlegger faste svar for grensesnittsjekker. Gjør dem til en dokumentert demomodus, og beskriv i README hvordan sensor bruker egen nøkkel. |
| **Avhengigheter og kostnader** – krever løsningen betalte API-er, f.eks. språkmodeller, og finnes det en plan for kostnad, testmodus eller mock-data? | risiko | Leverandør og budsjett er ikke valgt. Velg leverandør, sett en grense for dokumentstørrelse, og lagre eksempelsvar til testene. |

**Konklusjon om gjennomførbarhet:**

- **Gjennomførbart som beskrevet.**

**Forslag til justering av omfang eller vanskelighetsgrad:**

1. Behold v1 slik den er planlagt. Skriv i briefen en tydelig «hvis tid»-liste med én eller to utvidelser i prioritert rekkefølge, for eksempel lagrede økter med innlogging eller quiz med flervalg og automatisk retting.
2. Legg vekt på det sensor ser etter i et enkelt prosjekt: et gjennomarbeidet og tilgjengelig grensesnitt, de tre testdokumentene med dokumenterte resultater, og en utviklingslogg som viser hvor dere rettet KI-forslag.

## Hvorfor product brief er viktig for mappen

Product brief er utgangspunktet for PRD, arkitektur, stories og til slutt koden. Del 1 av mappen vurderes blant annet på om sensor kan følge en sporbar vei fra plan til ferdig app. Den vurderes også på om appen gjør det dere har beskrevet, om den er testet, om den er godt designet, og om den kan kjøres etter README. Et uklart, for stort eller for lite brief gjør alt dette vanskeligere senere. Det er mye enklere å rette nå enn sent i semesteret.

## 1. Gjennomgang av briefens deler

| Del av brief | Status | Kommentar |
|---|---|---|
| Executive Summary – er det klart hva appen er, og hvilket problem den løser? | Juster | «Purpose and agreed scope» handler mest om prosjektets rammer (én nybegynner, frist). Start med hva appen gjør for studenten. |
| The Problem – er problemet konkret, med reelle situasjoner og brukere? | Juster | Problemet er nevnt i én setning. Beskriv en konkret situasjon, for eksempel en student med 40 lysbilder før en prøve. |
| The Solution – beskriver løsningen brukeropplevelsen, ikke bare teknologi? | OK | «Proposed minimal implementation» beskriver én skjerm, ett dokument, kort/detaljert sammendrag og svar som vises ved behov. |
| What Makes This Different – er vurderingen ærlig og realistisk? | Endre | Mangler. Forklar ærlig hva appen gir utover å lime tekst inn i en chatbot, for eksempel kildehenvisninger og et fast format. |
| Who This Serves – er primærbrukerne tydelige, og vet vi hva de trenger? | Juster | «Students across subjects» er bredt. Beskriv én primærbruker og situasjonen deres. |
| Success Criteria – kan kriteriene faktisk sjekkes eller testes? | OK | «Agreed quality goals» er konkrete og etterprøvbare. |
| Scope – er det klart hva som er med i første versjon, og hva som ikke er det? | Juster | Det som er utsatt er tydelig, men flere valg er merket som forslag som venter på godkjenning. Gjør dem til beslutninger. |
| Vision – henger visjonen sammen med resten uten å blåse opp omfanget? | Juster | Mangler. Noen setninger om hva appen kan bli (for eksempel repetisjon over tid) gir retning uten å endre v1. |

## 2. Utgangspunkt for del 1 av mappen

Punktene følger kriteriene i sensorveiledningen for del 1. Vektene i parentes viser hvor mye hvert kriterium teller i del 1.

| Kriterium i del 1 | Hva briefen bør legge til rette for | Status | Kommentar |
|---|---|---|---|
| **1. Prosess og KI-styring** (30 %) | Brief som er presis nok til at PRD og stories kan bygges direkte på den, slik at krav kan spores fra brief til kode. | OK | Fem commits viser at briefen er bearbeidet og forenklet, og PRD-en har krav-ID-er som kan spores. Fortsett slik. |
| **2. Funksjonalitet og omfang** (20 %) | Realistisk omfang for gruppen og semesteret: en tydelig kjerneflyt som kan bli ferdig og stabil, og nok innhold til å vise reell funksjonalitet. | Juster | Kjerneflyten er tydelig og realistisk. Planlegg én utvidelse, slik at dere har mer å vise. |
| **3. Kvalitetssikring og testing** (15 %) | Suksesskriterier og funksjoner som er konkrete nok til å bli testtilfeller. | OK | Kvalitetsmålene og sjekkene i utviklingsplanen er gode testtilfeller. |
| **4. Design og brukeropplevelse** (10 %) | Tydelige brukere og brukssituasjoner som designet kan bygges rundt, gjerne med de viktigste skjermbildene eller flytene skissert. | Juster | Én skjerm er et godt valg. Skisser hvordan sammendrag, begreper, flashcards og quiz vises, og hvordan referansene ser ut. Med Streamlit må dere jobbe bevisst med design. |
| **5. Kodekvalitet og arkitektur** (10 %) | Teknologivalg som er begrunnet og ikke mer komplekse enn appen trenger. | OK | Ett prosjekt, ingen database, ingen vektorsøk. Bevisst enkel og begrunnet. |
| **6. README og kjørbarhet** (10 %) | Løsning som andre kan kjøre lokalt uten betalte kontoer, og uten tilgang til gruppens egne tjenester og nøkler. | Juster | Planlegg README med egen nøkkel via secrets-fil, en eksempelfil uten ekte nøkkel og en demomodus med faste svar. |
| **7. Ryddighet i repoet** (5 %) | En plan for hvor hemmeligheter, testdata og dokumentasjon skal ligge. | OK | Nøkler holdes utenfor Git, og dokumentasjonen ligger ryddig i `.docs/`. Legg testdokumentene i en egen mappe. |

## 3. Neste steg for gruppen

1. Legg til korte avsnitt for problem, primærbruker, differensiering og visjon i briefen, og endre status fra «pending-assessment-criteria».
2. Ta de åpne beslutningene selv og skriv begrunnelsen i briefen og PRD-en: midlertidige økter uten innlogging, kun tekstbaserte PDF-er, valg av LLM-leverandør.
3. Ferdigstill PRD-en, og start med trinn 1a–1c og PDF-eksperimentet slik utviklingsplanen beskriver.

Oppdater product brief i repoet når dere har gjort endringene, slik at historikken viser hvordan planen utviklet seg. Det er en del av prosessen sensor ser etter.
