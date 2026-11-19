# Manuell skjermleserkontroll – 19.11.2026

**Status: gjennomført for punktene under, brukerbekreftet19.11.2026.**
Dette er en avgrenset kontroll av den faste demoen, ikke full WCAG-godkjenning.
En installert skjermleser eller automatisert DOM-test er ikke et bestått resultat.

## Oppsett

- Side: `http://127.0.0.1:8000/`, tydelig merket «Demo – eksempeldata».
- Hjelpemiddel: Windows Skjermleser/Narrator, installasjon bekreftet lokalt.
- Nettleser: Firefox160.0, versjon lest fra lokal kjørende prosess.
- Narrator-filversjon:10.0.26100.9949. Eksakt stemme ble ikke registrert.
- Gjennomføring: studenten betjener tastaturet og lytter. Agenten kan ikke
  høre opplesningen og registrerer bare det studenten faktisk rapporterer.
- Bare det faste eksempelet brukes; ingen modellkall, konto, passord eller
  eget dokument trengs. Eksisterende server/oppsett endres ikke.

## Kort gjennomgang

1. Åpne demoen i ny fane. Start/stopp Skjermleser med **Windows+Ctrl+Enter**.
   Hvis velkomstvinduet dekker siden, gå tilbake med **Alt+Tab**. Bekreft lyd
   og at du kan høre relevante elementer på siden. **Ctrl** stopper opplesning.
2. Bruk **Tab** til «Lag læringsmateriale» og **Enter**. Lytt etter tydelig
   knappetekst og bekreftelse/fokus når de fire læringsdelene er klare.
3. Gå med **Tab** til «Sammendrag». Ved behov slås skannemodus av med
   **Caps Lock+Mellomrom**; lytt til om den nå er av. Bruk **Pil høyre** via
   Begreper til Flashcards. Lytt etter valgt fane og gjeldende kort/spørsmål.
4. Bruk **Tab** videre til «Vis svar», og **Enter**. Les videre fra fokus med
   **Caps Lock+R**, eller bruk skannemodus/pil ned for tekstlesing. Bekreft at
   det avdekkede svaret og kildereferansen kan nås og leses. Skjulte svar skal
   ikke leses som synlig innhold før de avdekkes.
5. Gå til Quiz-fanen og lytt etter riktig aktiv del/spørsmål, deretter tilbake
   til Flashcards. Bruk «Ny økt» med tastatur og kontroller at ny valg av
   eksempel kan gjøres. Stopp Skjermleser med **Windows+Ctrl+Enter**.

Narrator-tasten er som standard Caps Lock eller Insert. Tastaturoppsett,
stemme og nettleser kan påvirke formuleringen; det er forståelig navn,
tilstand, fokus og tilgang til innhold som kontrolleres, ikke ordrett tale.

## Faktiske observasjoner

| Punkt | Resultat | Studentens observasjon |
| --- | --- | --- |
| Opplesning startet på riktig side | Bekreftet | Narrator-prosess/vindu ble observert; studenten bekreftet senere opplesning av demoens knapp og resultat/status. |
| Knapp/fokus og genereringsbekreftelse | Bekreftet innen spurt omfang | Studenten svarte «Ja, knapp og resultat/status ble lest opp» etter Tab til genereringsknapp og Enter. Spørsmålet tillot enten resultatstatus eller Vis/rediger; det er ikke en ordrett transkripsjon av alle hendelser. |
| Fanebytte og riktig kort/quiz-kontekst | Brukerbekreftet | «Ja, både fanebytte, svar og kilde fungerte»; senere «Ja, riktig spørsmål og ingen skjult fasit lest» ved Quiz. Ingen ordrett transkripsjon av alle ARIA-tilstander. |
| Avdekket svar/kilde og skjult quizfasit | Brukerbekreftet innen teststegene | Flashcards-svar/kilde kunne leses etter avdekking. På Quiz ble riktig spørsmål lest uten skjult fasit før Vis fasit. Skjult flashcard-svar før avdekking ble ikke spurt om separat. |
| Ny økt og eksempelvelger med tastatur | Brukerbekreftet | Studenten svarte «Ja, begge deler fungerte» på at resultater var borte og eksempelvelger ble tilgjengelig/lest etter Ny økt. Ny faktisk generering etter reset ble ikke kontrollert separat i denne lydtesten. |

Resultatene bygger på studentens eksplisitte svar under veiledet gjennomgang,
ikke agentens direkte lytting. Agenten har ikke gjort en lydregistrering.
Ingen demofeil ble rapportert i disse stegene. Innlogget arbeidsområde,
PDF-leserekkefølge, feilflyt, kontrast og andre nettlesere er egne grenser.
Den tidligere automatiserte kort2→quiz1-regresjonen er separat evidens; den
eksakte posisjonssekvensen er ikke hevdet som manuelt lydtestet her.

Oppstartsnotat: Studenten rapporterte først at både demo og Skjermleser ikke
åpnet. Kun-lesende kontroll fikk HTTP200 fra demoen og fant Narrator stoppet.
Etter manuell adresseinstruks ble et Firefox-vindu med demotittel observert.
Direkte start via Computer Use meldte først manglende målrettbart vindu;
ny vindus-/prosessobservasjon fant Narrator kjørende. Ingen nettleser- eller
sikkerhetsinnstilling ble endret og ingen utestående tillatelsesdialog godtatt.

Etter gjennomgangen spurte studenten hvordan Skjermleser slås av. Det ble
veiledet om Caps Lock+Esc eller Windows+Ctrl+Enter, og Ctrl for bare å stoppe
opplesning. Etter dette bekreftet prosesskontroll at Narrator ikke kjørte.
Dette er avslutningskontroll, ikke ekstra bevis for appens tilgjengelighet.

## Kilder kontrollert19.11

- [Microsoft: starte og stoppe Skjermleser](https://support.microsoft.com/en-us/accessibility/windows/narrator/chapter-1-introducing-narrator)
- [Microsoft: skannemodus og Narrator-tasten](https://support.microsoft.com/en-us/accessibility/windows/narrator/chapter-3-using-scan-mode)
- [Microsoft: lese tekst og stoppe opplesning](https://support.microsoft.com/en-us/accessibility/windows/narrator/chapter-4-reading-text)
- [Microsoft: standard hurtigtaster og avslutning](https://support.microsoft.com/en-us/accessibility/windows/narrator/appendix-b-narrator-keyboard-commands-and-touch-gestures)
