# Kort manuell live-gjennomgang – 19.11.2026

**Status: startet; dokumentlisten er tom og viser én ventende sletting.**
Dette er en plan og løpende resultatlogg, ikke en bestått kontroll.
Bruk eksisterende autorisert testkonto og bare kjent syntetisk materiale.
Ingen nye kontoer, e-poster, offentlige lenker eller brede testkjøringer inngår.

## Første del uten modellkall

| Steg | Handling og forventning | Observert resultat |
| --- | --- | --- |
| 1 | Åpne `http://127.0.0.1:8000/workspace`, logg inn og velg Mine dokumenter. Listen eller en forståelig tomtilstand vises. | Studenten gjenga innlogget status og forståelig tomtilstand. Separat vises én ufullført sletting med retry-knapp. Agenten har ikke observert nettleseren direkte. |
| 2 | Åpne et kjent syntetisk testdokument. Kilde og læringsdeler gjenfinnes; svar er skjult til de avdekkes. Bruk tastatur til faner og svar/kildereferanse. | Ikke gjennomført. |
| 3 | Noter kort-/quizposisjon, flytt én posisjon der det finnes flere, og vent til fremdriften er bekreftet. | Ikke gjennomført. |
| 4 | Velg Ny økt og åpne samme dokument igjen. Bekreft gjenfunnet kort-/quizposisjon og skjulte svar; hent eventuelt siste fremdrift ved eksplisitt konflikt. | Ikke gjennomført. |
| 5 | Logg ut. Privat innhold skal forsvinne og privat arbeidsområde kreve innlogging. | Ikke gjennomført. |

Ingen titler, passord, tokens eller dokumentinnhold må gjengis i chat/logg.
Hvis listen er tom eller feiler, registrer det faktiske utfallet før neste steg.
Et eksisterende dokument slettes ikke som del av denne første gjennomgangen.

## Resten av hovedflyten

Ny kilde/PDF, ekte generering, ny eksplisitt lagring og sletting av et nytt,
avgrenset testdokument er **ikke dekket** av gjenåpning alene. Disse punktene
planlegges etter første observasjon og tidligere evidens, slik at eventuell
generering begrenses til et konkret nødvendig kall innen eksisterende budsjett
og autorisasjon. Tidligere automatisert modell-smoke-ramme er brukt opp;
den gjenbrukes ikke som fullmakt til nye automatiserte modellkall.

## Lokal klargjøring

Kl.18:18 svarte `/` og `/workspace` HTTP200. `/health` svarte200 med
`status=ok, mode=demo`. Feltet `mode` er statisk i dagens helserute og beviser
ikke at live-generering, innlogging eller lagring er aktivt/verifisert.
En første forespørsel mot `/api/health` ga404; eksisterende helserute er `/health`.
Ingen server ble startet eller restartet. Agenten har ikke logget inn eller
observert privat brukergrensesnitt i denne økten. Brukerobservasjon av første
steg er mottatt. Det viser ingen ferdiglagrede dokumenter å bruke til steg2–4.

## Observasjon og neste avklaring

Studentens svar viser at innlogget arbeidsområde og Mine dokumenter er
tilgjengelig, med tomtilstand og et element under ventende sletting. Dokumentets
tittel gjengis ikke her. Dette beviser ikke hvorfor slettingen er ufullført.
Koden viser at «Prøv sletting igjen» gjenbruker den eksisterende slettings-ID-en,
og bare viser fullført når serveren svarer `deleted`; øvrige utfall forblir åpne.
Studenten svarte «Jeg er usikker på hva det er» på spørsmålet om elementet
fortsatt skal slettes. Det lar vi stå; ingen retry eller sletting er utført.

Neste steg er kildekontroll uten modellkall: studenten er bedt om å lime inn
tre syntetiske avsnitt om studiegruppen Fjord og velge «Kontroller materiale».
Studenten bekreftet «Ja, teksten vises som tre avsnitt». Dette er brukerbekreftet
kildevisning, ikke direkte agentobservasjon eller en PDF-kontroll. Teksten er
laget for denne gjennomgangen og inneholder ingen private data.

Lokal budsjettinspeksjon viste10 forsøk, USD0,50 reservert av USD5,00,
USD0,05 reservasjon per kall, `blocked=false` og fire tidligere live-smokekontroller.
Studenten er deretter bedt om å trykke «Lag læringsmateriale» én gang på den
syntetiske teksten, informert om modellbruk/reservasjon og om å unngå retry ved
feil. Dette er et nødvendig manuelt genereringssteg, ikke ny automatisert smoke.
Genereringsresultat avventes. Ingen budsjettgrense, nøkkel eller journal er endret
av agenten; inspeksjonskommandoen var `scripts.model_budget status`.

Se [kravavstemming](sensor-guidance-check-2026-11-19.md) og
[leveransesjekkliste](delivery-checklist-2026-11-19.md).
