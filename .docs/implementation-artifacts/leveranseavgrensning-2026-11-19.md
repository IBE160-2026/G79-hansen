# Avtalt enklere skoleleveranse

19.11.2026. IBE160, Høgskolen i Molde. Frist15.12.2026.
**Valgt19.11.2026:** Studenten svarte «høres bra ut» og ba om å gå videre etter
forslaget om lokal leveranse først. Offentlig lenke er nå et valgfritt tillegg.
Eksisterende kjerne, innlogging og Supabase-lagring beholdes.

## Frist og arbeidsmål

Studenten presiserte19.11 at **hele oppgaven skal leveres15.12.2026**, og ønsker
at den er klar tidligere. Arbeidsmålene nedenfor gir én uke buffer:

| Senest | Arbeidsmål |
| --- | --- |
| 1. desember | Avtalt kjerneflyt ferdig og brukbar; ingen nye funksjoner etter dette. |
| 2.–7. desember | Nødvendige bruker-/tilgangskontroller, retting, README, refleksjonsrapport og øvrig innleveringsmateriale. |
| 8. desember | Samlet innleveringspakke klar og gjennomgått mot faktisk oppgavetekst. |
| 9.–14. desember | Buffer for feilretting og siste leveransekontroll. |
| 15. desember | Fast innleveringsfrist, ingen planlagt utvikling. |

Dette er styringsmål, ikke en påstand om at uferdige kontroller er bestått.
Offentlig hosting/to-fysiske-enheter og videre backup-/restoreautomatisering
utsettes som leveransekrav. De markeres ikke som ferdige. Sikkerhets- og
tilgangskontroll i eksisterende funksjoner beholdes; syntetiske data brukes.

## Grunnlag

Studenten opplever at særlig hosting/backup har blitt for omfattende og ber om
revurdering. [Faglærerens tilbakemelding](../planning-artifacts/briefs/brief-G79-hansen-2026-09-26/tilbakemelding-product-brief.md)
vektlegger gjennomførbarhet, begrunnet enkel arkitektur, kontroll av KI-resultater,
testing, dokumentert prosess og lokal kjørbarhet uten gruppens tjenester/nøkler.
Den opprinnelige tilbakemeldingen vurderte et mindre funksjonsomfang; innlogging
og lagring ble senere valgt som utvidelse. Den er ikke full oppgavetekst eller
sensorveiledning. Ingen garanti om vurdering/karakter utledes fra den.

Appserveren kjører lokalt. Lagrede dokumenter/fremdrift og originalfiler ligger
i Supabase Paris; lokal lagring nå gjelder blant annet budsjett, nøkler og
planlagt backup. Å flytte databasen til PC-en vil være en ny ombygging.

## Avtalt avgrensning

| Område | Valg | Konsekvens |
| --- | --- | --- |
| Fungerende kjerne | Behold tekst/PDF, kildehenvisninger, sammendrag, begreper, kort og quiz. | Bruk tiden på feil som påvirker studieflyten og dokumentert innholdskvalitet. |
| Innlogging og lagring | Behold implementert Supabase, Mine dokumenter, fremdrift og sletting. | Ingen databaseflytting eller ny plattform; bevar tilgangskontroll og hemmelighetshåndtering. |
| Sensorleveranse | Prioriter kjørbar lokal demo uten nøkler og tydelig separat beskrivelse av live-modus. | Sensor skal kunne demonstrere flyten selv om studentens PC/tjenester er utilgjengelige. |
| Offentlig lenke | Funnel-lenken er et valgfritt tillegg hvis tid og eksisterende kontroller tillater det. | Story4.1 er utsatt og ufullført; offentlig tilgang/to-fysiske-enheter er ikke påstått levert. |
| Backup/drift | Utsett videre eksport-/restoreautomatisering under arbeid med syntetiske testdata. Behold ferdige lokale komponenter uten mer utbygging nå. | Ingen påstand om komplett backup, produksjonsdrift eller fysisk retensjonsakseptanse. Full backup-/slettekontroll kreves før reelle private data/offentlig bruk. Passordsjekken venter. |
| Videre kvalitet | Prioriter README, enkel oppstart, sentrale brukerflyter/tilgang, tilgjengelighet og refleksjonsrapport. | Bruk eksisterende evidens; nye tester ved konkret behov, ingen ekstra modellkall uten behov. |
| Nye funksjoner | Ingen nye tillegg før kjernen og dokumentasjonen er ferdig. | Ikke legg til nye plattformer, betalingsløsninger eller avansert drift. |

## Avhengigheter og neste handling

Epic4/Story4.2 kan gjennomføres uten offentlig hosting. PRD og arkitektur har en
datert leveranseendring som avgrenser fysisk to-enhetsakseptanse, men bevarer
implementert persistens-/konfliktlogikk og eierkontroll. Neste konkrete arbeid
er nøkkelfri demooppstart og sentrale brukerflyter, deretter kort oversikt over
gjenværende leveransehull. Full oppgavetekst/sensorveiledning må fortsatt
kontrolleres før endelig innlevering.

Hvis offentlig lenke tas opp igjen, gjelder eksisterende sikkerhets-/backup-/
tilgangsporter og separat publiseringsgodkjenning fortsatt.

Dette notatet endrer ingen kode, data, kontoer, kjørende prosesser eller ruter.
Den installerte rotasjonsjobben beholdes; `.env.hosted` er kun klargjort lokalt.
