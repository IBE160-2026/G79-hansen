# Slik er Study Buddy tenkt bygget

Status: arkitektur klar for implementeringsplanlegging, oppdatert 11.11.2026. Forklaring for studenten og sensor. Se [den tekniske kontrakten](ARCHITECTURE-SPINE.md) for regler som skal være felles når delene bygges.

## Det du har valgt

Appen bruker Python og FastAPI, med HTML, CSS og JavaScript i nettleseren. Supabase håndterer innlogging med e-post/passord, database og privat fillagring. Du skal kunne åpne ditt eget innhold fra flere enheter.

«Lag læringsmateriale» lager alle fire delene. «Lagre» beholder dokument, innstillinger og læringsmateriale. «Mine dokumenter» åpner eller sletter lagret innhold. Gjenåpning fortsetter på riktig flashcard og quizspørsmål. «Ny økt» starter en tom arbeidsflate uten å slette lagrede dokumenter.

Når dokumentet allerede er lagret, lagres plasseringen i flashcards og quiz automatisk og uavhengig av hverandre. Dokumentet, innstillingene og nytt læringsmateriale krever fortsatt «Lagre». Fremdrift i ulagret materiale blir bare i nettleserminnet. Ved gjenåpning gjenopptas riktig kort og quizspørsmål med svarene skjult. Under samme besøk beholdes viste svar ved fanebytte.

FastAPI-serveren håndterer innloggingstilstanden og oppbevarer den i minnet på én serverprosess i førsteversjonen. Serverrestart eller oppdatering krever ny innlogging. Lagrede dokumenter, læringsmateriale og synkronisert fremdrift beholdes i Supabase og kan åpnes etter innlogging. Flere enheter kan fortsatt være innlogget samtidig.

Du kan fortsette på en annen enhet fra sist bekreftede fremdrift. En utdatert fane får ikke overskrive nyere lagret fremdrift. Ved konflikt vises «Fremdriften er endret på en annen enhet», med «Hent siste fremdrift» før nye endringer kan lagres. Ved nettverksfeil vises at fremdriften ennå ikke er lagret; bare bekreftede oppdateringer kan gjenopptas på en annen enhet.

## Hvilken del gjør hva?

| Del | Ansvar |
| --- | --- |
| Nettleseren | Felter, faner, vis/skjul svar, kortnavigasjon og tilbakemeldinger. |
| FastAPI | Kontrollerer bruker/tilgang, validerer input, koordinerer PDF/KI og lagring. |
| Supabase Auth | Konto, innlogging, e-postbekreftelse, passordgjenoppretting og utlogging. |
| Supabase Postgres | Eierkobling, dokumentoversikt, lagret tekst/resultater og fremdrift. |
| Privat Supabase Storage | Opplastede dokumentfiler med tilgangsregler for riktig eier. |
| KI-adapter | Felles grensesnitt for faste demodata og senere ekte modellkall. |

Det er ikke nok å skjule andre brukeres dokumenter i grensesnittet. Server, database og fillagring må avvise uvedkommende forespørsler, også når noen endrer en dokument-ID manuelt.

## Eksempel på en vanlig bruk

1. Du logger inn og legger inn tekst eller en tekstbasert PDF.
2. FastAPI sjekker størrelse og henter ut tekst med avsnitts-/sidenumre.
3. Ett trykk bestiller sammendrag, begreper, flashcards og quiz. Ulesbare sider og utilstrekkelig kildegrunnlag forklares.
4. Du øver. Fanebytte koster ingen nye KI-kall.
5. Du trykker «Lagre». Først da opprettes varig lagring av materialet og resultatene.
6. På en annen enhet logger du inn på samme konto og åpner dokumentet. Det lagrede resultatet leses uten ny KI-generering.

## Tekniske valg

- **Fremdrift beskyttes med revisjonsnumre og låsing.** Gjentatte forespørsler får samme operasjons-ID, slik at et nettverksavbrudd ikke fører til at en gammel oppdatering overskriver en nyere.
- **Innlogging styres av serveren.** Førsteversjonen bruker én serverprosess, sikre informasjonskapsler og en kontroll av endringsforespørsler. Første tidsgrenser er 30 minutter uten aktivitet og 12 timer totalt. Utlogging gjelder enheten du bruker; andre enheter beholder innloggingen.

Passordgjenoppretting bruker en avgrenset innloggingstilstand som bare kan sette nytt passord. Løsningen krever at e-postlenken åpnes i samme nettleser som startet gjenopprettingen; ved utløp eller feil må en ny forespørsel startes. Vanlig innlogging på en annen enhet er fortsatt støttet.

Lagring og sletting berører både database og filer. Derfor får operasjonen en sporbar status før filene flyttes, og appen melder først «lagret» eller «slettet» når alle nødvendige steg er ferdige. Ved avbrudd skal operasjonen kunne prøves igjen uten duplikater eller feilaktig suksessmelding.

KI-leverandør og konkret modell er fortsatt åpne. Arkitekturen holder dette bak ett avgrenset grensesnitt, slik at demo, lagring og brukerflyt kan bygges først.

## Avklares før integrasjon og publisering

- **pypdf er kandidat** for tekstuttrekk, dersom det tidlige PDF-eksperimentet viser riktige fysiske sidenumre og forståelige begrensninger.
- **Render er kandidat** for hosting av FastAPI. Kostnader, region og tjenestegrenser sjekkes før opprettelse.

## Kontoer og oppsett

FastAPI er et Python-bibliotek og krever ingen konto. For skyløsningen trenger prosjekteieren en Supabase-konto og et prosjekt. Appbrukere oppretter konto gjennom Study Buddy og trenger ikke innlogging på Supabase-nettstedet. Hosting og den senere KI-leverandøren kan kreve egne kontoer.

Denne planen oppretter ingen kontoer eller betalte tjenester. Sensor skal fortsatt kunne kjøre en lokal demoversjon med faste eksempler uten eksterne nøkler. Live-modus krever konfigurerte tjenester og må dokumenteres separat i README.

## Hvordan kontrollere at det virker?

Test både normalflyt og avvisninger: to brukere, direkte forespørsler mot andres dokumenter/filer, utlogging, ugyldige gjenopprettingslenker, grenseverdier for input, delvis lesbar PDF og feil i KI/lagring/sletting. Sjekk at nytt innhold ikke lagres uten «Lagre», og at lagret materiale overlever serverrestart.

KI-kvaliteten kontrolleres med de tre avtalte testdokumentene og begreper valgt før generering. Gode kildehenvisninger og gyldig datastruktur garanterer ikke riktige faglige svar.

Den nåværende prototypen demonstrerer brukerflyten med eksempeldata. Den er ikke bevis for at backend, ekte autentisering, varig lagring eller KI allerede er implementert.

## Videre i BMAD

Arkitektur, krav og UX er nå samkjørt som implementeringsgrunnlag. Arbeidet deles i epics og stories, sprintplanen opprettes, og appen bygges fra demomodus til autentisering/lagring og ekte generering. PDF-biblioteket testes før PDF-integrasjonen; modell/API/budsjett og hostingoppsett avklares før sine milepæler. Behold tid til testing og feilretting før innlevering.
