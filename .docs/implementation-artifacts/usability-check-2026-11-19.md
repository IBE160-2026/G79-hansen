# Avgrenset brukskontroll – 19.11.2026

Instrumentert lokal nettlesergjennomgang og visuell inspeksjon av skjermbilder.
Dette er **ikke** en manuell skjermlesertest eller full tilgjengelighetsakseptanse.

Computer-use ble forsøkt, men meldte at nettlesertilgang manglet. Ingen
eksisterende Firefox-fane eller Supabase-side ble betjent. Kontrollserveren
brukte faste demodata, ledig loopbackport56690 og et miljø uten appnøkler.
Playwright/Chromium157.0.4341.60 var allerede installert. Ingen eksterne
forespørsler eller JavaScript-feil ble observert i kontrollkonteksten.

## Observerte resultater

| Kontroll | Observert |
| --- | --- |
| Tab til generering, Enter | Resultatene vises; fokus flyttes til synlig Vis/rediger-knapp. |
| Piltaster mellom læringsdeler | Fokus og valgt fane følger pilene. |
| Flashcard med tastatur | Synlig fokusmarkering, Enter viser svar med kilde; Neste gir kort2 med skjult svar. |
| Quiz ved390px bredde | Knapper/faner brytes over flere linjer, svar og kilde er lesbare, ingen horisontal overløp. |
| Ny økt med tastatur | Resultater tømmes, fokus går til eksempelvelger, ny valg/generering kan startes. |
| Visuell inspeksjon | Desktop og390px-skjermbilder gjennomgått; fokusramme, innhold og handlingsknapper er synlige. Ett misvisende statusfunn nedenfor. |

Fire samlede kontrollpunkter fullførte assert-kontrollene og skrev bevisfilen.
Den midlertidige kontrollharnessens etterarbeid hang og nådde90s-tidsgrensen;
hele prosessen skal derfor ikke omtales som en feilfri testkjøring. Separat
Windows-kontroll bekreftet ingen gjenværende kontrolllytter. Eksisterende
StudyBuddy PID25940 på8000 er bevart. Ingen bred testpakke ble kjørt om igjen.

## Funn B1 – gammel status ved bytte av fane

Etter Neste til flashcard2 og bytte til Quiz viser innholdet «Spørsmål1 av2»,
men den synlige `#status`-linjen viser fortsatt «Kort2 av3. Hva gjør
langtidsminnet?». Dette er synlig i390px-skjermbildet. `announceItem()` i
`app/static/app.js` oppdaterer status ved kortnavigering, mens faneklikk bare
bytter `active` og kaller `render()`.

**Åpent for retting:** Oppdater status konsekvent ved fanebytte slik at den
stemmer med aktiv læringsdel, uten ekstra genereringskall eller endring av
uavhengige posisjoner/svar. Verifiser kort2→quiz1 og tilbake med tastatur,
inkludert oppsummerings-/begrepsfaner. Skjermleserutfall er ikke observert.

## Liten tekstkorrigering utført

Demoens topptekst hevdet at lagring/Mine dokumenter «kommer senere». Den sier
nå korrekt at dette hører til separat konfigurert live-modus. Ingen
innlogging, generering, lagring eller nettverksregler ble endret.

## Lokal evidens og resterende grense

- [Desktop](../../test-results/walkthrough-desktop.png)
- [390px](../../test-results/walkthrough-mobile-390.png)
- [Kontrollpunkter](../../test-results/usability-walkthrough-proof.json)

Evidensfilene ligger lokalt i ignorert test-results og er ikke innleverte
vedlegg i seg selv. Testen dekker ikke faktisk skjermleser, full kontrastmåling,
andre nettlesere/enheter eller innlogget live-flyt. Tidligere11 automatiserte
demoscenarier/ren oppstartskopi er separat evidens. Ikke lukk disse åpne
akseptansepunktene på grunnlag av denne gjennomgangen.
