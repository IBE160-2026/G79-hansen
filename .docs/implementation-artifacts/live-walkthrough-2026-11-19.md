# Kort manuell live-gjennomgang – 19.11.2026

**Status: kildevisning, én ekte generering og privat lagring er brukerbekreftet;
kontroll av fremdrift/gjenåpning pågår.**
Dette er en plan og løpende resultatlogg, ikke en bestått kontroll.
Bruk eksisterende autorisert testkonto og bare kjent syntetisk materiale.
Ingen nye kontoer, e-poster, offentlige lenker eller brede testkjøringer inngår.

## Plan og resultater

| Steg | Handling og forventning | Observert resultat |
| --- | --- | --- |
| 1 | Åpne `http://127.0.0.1:8000/workspace`, logg inn og velg Mine dokumenter. Listen eller en forståelig tomtilstand vises. | Studenten gjenga innlogget status og forståelig tomtilstand. Separat vises én ufullført sletting med retry-knapp. Agenten har ikke observert nettleseren direkte. |
| 2 | Kontroller nytt syntetisk materiale, generer én gang, kontroller et svar/kilde og lagre som Fjord-test. | Tre kildeavsnitt, læringsdeler uten feil og ett korrekt svar/kilde med bekreftet privat lagring er brukerbekreftet. |
| 3 | Noter kort-/quizposisjon, flytt én posisjon der det finnes flere, og vent til fremdriften er bekreftet. | Ikke gjennomført. |
| 4 | Velg Ny økt og åpne samme dokument igjen. Bekreft gjenfunnet kort-/quizposisjon og skjulte svar; hent eventuelt siste fremdrift ved eksplisitt konflikt. | Ikke gjennomført. |
| 5 | Logg ut. Privat innhold skal forsvinne og privat arbeidsområde kreve innlogging. | Ikke gjennomført. |

Ingen private titler, passord, tokens eller privat dokumentinnhold skal i chat/logg.
Hvis listen er tom eller feiler, registrer det faktiske utfallet før neste steg.
Et eksisterende dokument slettes ikke som del av denne første gjennomgangen.

## Resten av hovedflyten

Kildevisning av innlimt tekst, én ekte generering og ny eksplisitt lagring er
brukerbekreftet nedenfor. Fremdrift/gjenåpning, utlogging, sletting av det nye
testdokumentet og PDF er ikke bekreftet i denne gjennomgangen. Tidligere
automatisert modell-smoke-ramme er brukt opp; den er ikke brukt som fullmakt
til nye automatiserte modellkall. Ingen ytterligere generering trengs for
gjenåpnings-/fremdriftskontrollen.

## Lokal klargjøring

Kl.18:18 svarte `/` og `/workspace` HTTP200. `/health` svarte200 med
`status=ok, mode=demo`. Feltet `mode` er statisk i dagens helserute og beviser
ikke at live-generering, innlogging eller lagring er aktivt/verifisert.
En første forespørsel mot `/api/health` ga404; eksisterende helserute er `/health`.
Ingen server ble startet eller restartet. Agenten har ikke logget inn eller
observert privat brukergrensesnitt i denne økten. Brukerobservasjon av første
steg viste ingen ferdiglagrede dokumenter. Derfor ble et nytt syntetisk
testgrunnlag brukt, som dokumentert nedenfor.

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
Studenten bekreftet «Ja, læringsdelene vises uten feil». Spørsmålet tillot også
tydelig forklaring på manglende innhold, så dette beviser ikke antall kort eller
at alle deler har fullstendig innhold. En etterfølgende lokal budsjettinspeksjon
viste11 forsøk og USD0,55 reservert, fortsatt ublokkert og fire tidligere
live-smokekontroller. Endringen er konsistent med ett nytt ordinært kall;
reservasjon er ikke det samme som faktisk fakturert pris. Agenten gjorde ingen
automatiserte modellkall. Ingen budsjettgrense eller nøkkel er endret;
inspeksjonskommandoen var `scripts.model_budget status`.

Neste spørsmål ber studenten kontrollere ett avdekket flashcardsvar mot
kildereferansen og lagre det nye materialet som «Fjord-test 19.11.2026».
Studenten bekreftet «Ja, svaret/kilden stemmer og lagringen bekreftes».
Dette gjelder ett svar/kildereferanse og meldingen om privat lagring; ikke full
innholdsevaluering eller direkte kontroll av database-/Storage-objekter.

Studenten er deretter bedt om å gå til flashcard2/quiz1, vise kortsvaret, vente
på «Fremdriften er lagret», velge Ny økt og åpne Fjord-testen fra Mine dokumenter.
Forventningen er gjenfunnet kort2/quiz1 og skjult svar. Utfall avventes.

Se [kravavstemming](sensor-guidance-check-2026-11-19.md) og
[leveransesjekkliste](delivery-checklist-2026-11-19.md).
