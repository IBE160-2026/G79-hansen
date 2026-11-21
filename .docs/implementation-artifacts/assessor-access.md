# StudyBuddy – tilgang og kort prøve for sensor

Oppdatert21.11.2026. Skoleutgave av G79-hansen i IBE160.

Leveransen skjer via GitHub. Start i [README](../../README.md) for kode,
lokal kjøring og prosessdokumentasjon. Nettappen har egen selvregistrering;
sensor kan opprette sin egen konto uten innloggingsopplysninger fra repoet.

## Åpne appen

[Åpne StudyBuddy](https://fredriklaptop.tail55f8dd.ts.net:10000/account)
i en vanlig nettleser på PC eller mobil. Tailscale er ikke nødvendig hos sensor.
Nettutgaven er avhengig av at studentens Windows-PC, internett og app kjører.
Etter PC-omstart må studenten starte appen manuelt.

Den lokale nøkkelfrie demoen kan brukes hvis nettutgaven er utilgjengelig.
Følg [oppstartsinstruksen i README](../../README.md#start-demoen-uten-nøkler).
Demoen viser faste eksempler; egne dokumenter behandles i den innloggede nettutgaven.

## Logg inn

Bruk skjemaet **Opprett konto** og bekreft den vanlige brukerkontoen via e-post.
Åpne lenken innen ti minutter i samme nettleser/profil som registreringen startet i.
Registrering og glemt passord deler en grense på to e-postforsøk totalt og to
per mottaker per rullerende time; forsøk kan telle også når utsending mislykkes.
Tidligere forsøk beholdes og teller fortsatt. Leverandørens egen ventetid for
samme adresse gjelder i tillegg; studenten utfører eventuelle nye e-postforsøk.

En eksisterende bekreftet vanlig testkonto er valgt som reserve.
Innloggingsopplysningene overleveres separat og privat av studenten.
Ingen konto- eller prosjektadministratorrolle hos Supabase er nødvendig.

## Prøv hovedflyten

1. Åpne **Eget materiale**. Velg innlimt tekst, tekstfil eller **PDF med tekst**.
   For PDF vises **Velg fil** når kildetypen er valgt. Bruk en kort kilde du
   har lov til å dele, uten sensitive opplysninger.
2. Velg **Kontroller materiale**. Kontroller teksten og avsnitts-/sidetallene.
   Maksimum er40 PDF-sider,30 000 uttatte tegn og10 MiB. Bilder, tabeller og
   figurer tolkes ikke; skannede dokumenter uten tekst støttes ikke.
3. Trykk **Lag læringsmateriale** én gang. Se Sammendrag, Begreper, Flashcards
   og Quiz. Vis ett svar og kontroller det mot kildehenvisningen.
4. Gi materialet en gjenkjennelig testtittel og velg **Lagre**. Flytt til et
   annet kort/spørsmål og vent på **Fremdriften er lagret**.
5. Velg **Vis/rediger → Ny økt**, deretter **Mine dokumenter**, og åpne testen.
   Posisjonen skal være bevart og svarene skjult. Gjenåpning krever ikke ny generering.
6. Slett eventuelt bare materialet du opprettet for prøven. Logg ut og last
   siden på nytt; privat innhold skal være borte og ny innlogging kreves.

Generering bruker serverens avgrensede testbudsjett. Modellens svar må
kontrolleres mot kilden. Se [dokumenterte resultater og åpne grenser](hosting-acceptance.md)
og [PDF-prøven](pdf-acceptance-2026-11-21.md).

## Overleveringsstatus

Selvregistrering og den valgte reservekontoen er dokumentert i
[tilgangsplanen](hosting-plan-4-1.md). Selvregistrering er hovedveien for
GitHub-innleveringen. Hvis reservekonto trengs, overleverer studenten dens
innloggingsopplysninger separat i en privat kanal. Disse legges ikke i README,
repoet, GitHub-issues eller andre repo-vedlegg. Denne veiledningen inneholder
ingen passord; ingen melding er sendt til sensor som del av klargjøringen.
