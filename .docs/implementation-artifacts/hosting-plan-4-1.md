# Hostingplan – Story 4.1

**Tilgangspresisering20.11:** Del1-sensorveiledningen s.5 ber om testdata eller
testbrukere ved behov og tydelig README, men angir ikke om sensor skal få en
ferdig konto eller registrere seg selv. Studentens valg «egen foreleserkonto»
fastsetter ikke opprettingsmåten. Tidligere omtale av foreleserens e-post som
nødvendig neste steg var vår antakelse om forhåndsoppretting, ikke et oppgavekrav.
Tilgangsmåten må avklares; ingen konto opprettes eller registreringsløsning endres
på grunnlag av denne presiseringen. Hosted-e-post er fortsatt deaktivert, så
selvregistrering er ikke klargjort for sensor nå.

## Privat HTTPS-kontroll20.11, kl.12:20

Etter studentens «gjør det» er faktisk hosted-oppstart og en egen **privat**
Serve-rute på10000 gjennomført. Worker22936 erstatter gammel25940 på loopback8000;
443/8765 og8443/3000 er bevart. Ingen offentlig Funnel-rute er aktivert.
TLS, anonym status/cookieflagg, feil HTTP-origin og avviste konfigurasjonsfiler
er kontrollert; budsjett/kapabilitet er byteuendret. Studenten bekreftet faktisk
innlogging, dokumentliste og utlogging etter omlasting på HTTPS-adressen.
Se [detaljert privat kontroll og stopp/omstart](hosting-local-preparation-4-1.md).
Foreleserens adresse/egen konto og separat offentlig godkjenning er fortsatt åpne.

## Oppdatert20.11.2026 – lokal klargjøring gjenopptatt

Studenten ønsker igjen faktisk tilgang fra telefon og sensorens PC via egen
Windows-PC/Funnel. Offentlig aktivering krever fortsatt separat godkjenning.
Studenten valgte **manuelt startet kryptert backup** fram til innlevering,
med eget ansvar for å starte kopien. Eksisterende7-dagers rotasjon beholdes;
daglig automatisk eksport bygges ikke videre nå. Kopien skal omfatte database
og Storage, og ha en kontrollert gjenopprettingsprøve før den regnes som klar.
Dette erstatter tidligere plan om daglig automatisk eksport.

Faktisk kontroll20.11:

- Hosted-preflight validerte konfigurasjon og tilstand, så avviste den opptatt
  port8000. Eksisterende StudyBuddy PID25940 på127.0.0.1:8000 er bevart.
  Ingen Windows-lytter ble funnet på10000; dette er ikke en rutekonfigurasjon.
- Effektive flagg fra separat hosted-fil: innlogging, generering og lagring på;
  Secure-cookies på, loopback-HTTP av, signup/recovery-e-post av.
  Ingen konfigurasjonsverdier eller nøkler ble skrevet ut.
- Supabase er `ACTIVE_HEALTHY` i Paris. Security-advisors rapporterte kun
  det tidligere kjente Auth-varselet om deaktivert lekket-passordvern.
  Storage har én privat bucket, ingen offentlige buckets og fem registrerte
  objekter. Dette er metadata, ikke en ny full sikkerhets-/retensjonsakseptanse.
- Før eksport hadde backupmappen to DPAPI-filer og et CA-sertifikat, ingen .sbb-kopi.
  Rotasjonsjobbens siste kjøring20.11 kl.05:30 ga resultat0; neste21.11 kl.03:00.
  Det beviser utløpsjobb, ikke opprettelse av sikkerhetskopi.
- Databasepassord/TLS ble allerede verifisert19.11 med prosjekt-CA.
  Gjenbrukbar standardhelper bruker fortsatt systemrøtter; vellykket tidligere
  kontroll brukte en eksplisitt CA-adapter.

Studenten valgte nedlasting av Storage-filene via dashboardet og bekreftet alle
fem i privat mottaksmappe. Én [faktisk kryptert appkopi og isolert import-/filprøve](backup-local-4-1.md)
er deretter fullført20.11. Ingen ny eksportnøkkel ble opprettet. Studenten
slettet den midlertidige Prepared-mappen manuelt etter policyavvist opprydding;
kontroll20.11 kl.12:11 bekreftet banen borte og arkivets SHA256 uendret.
Backupens begrensning til appdata og manglende
live gjenopprettings-/rolleakseptanse er dokumentert i resultatnotatet.
Foreleserkontoens e-post er fortsatt utsatt etter studentens ønske.
Før publisering gjenstår ferdig tilgang og samlet avstemming av de åpne portene;
deretter konkret aktiveringsforslag og separat godkjenning, fulgt av reell
mobil-/ekstern-PC-kontroll. Server, eksisterende ruter og providerinnstillinger
er ikke endret. Ingen modell-/e-postkall eller bred testsuite er kjørt;
den nødvendige faktiske backup-/importprøven ovenfor er gjennomført.

## Tidligere plan og kontroller18.–19.11

**Leveransevalg19.11.2026:** Lokal skoleleveranse prioriteres; offentlig lenke
og videre hosting-/backupautomatisering er valgfritt/utsatt. Tidligere plan og
evidens under beholdes som forberedelse, ikke krav om videre aktivering nå.
Se [avtalt avgrensning](leveranseavgrensning-2026-11-19.md) og
[leveransesjekkliste](delivery-checklist-2026-11-19.md).

18.11.2026. **Utkast, ingen publisering godkjent eller utført.** IBE160, Høgskolen i Molde; innlevering 15.12.2026.

Studenten ønsker gratis hosting på denne PC-en og en vanlig lenke som også foreleser kan åpne. Betalt Render er derfor tatt ut av forslaget.

| Punkt | Konkret forslag |
| --- | --- |
| Appserver | Denne Windows-PC-en, én FastAPI-prosess på loopback. Behold eksisterende Windows-isolasjon for PDF. |
| Tilgang | Tailscale **Funnel** foran bare appens port. Foreleser/mobil bruker vanlig nettleser, uten Tailscale-klient. Ingen portåpning i ruteren. Ikke eksponer repo, filsystem eller andre tjenester. |
| Region | App og budsjettfiler på studentens PC i Norge, forutsatt at PC-en står her. Eksisterende Supabase `studybuddy-test`, Free, **Paris/eu-west-3** beholdes. Tailscale har global formidling; ingen fast EU-region er valgt eller lovet for kontroll-/relétjenesten. |
| Kostnad | **0 kr i nye hostingabonnementer**: eksisterende PC/nett, Tailscale Personal og Supabase Free. Ingen betalt plan, domene, SMTP eller tillegg. Strøm/nett er eksisterende driftskostnader. Modell-API er separat og fortsatt under tidligere USD 5-ramme; ingen nye kall eller budsjettendring nå. |
| HTTPS | Gratis `https://<maskin>.<tailnet>.ts.net`. MagicDNS/HTTPS og Funnel må kontrolleres før aktivering. Velg ufølsomt maskinnavn: sertifikatets vertsnavn blir offentlig. Eksakt HTTPS-origin, Secure-cookies og avgrensede Supabase-callbacker må samstemme. |
| Tilgjengelighet | PC, internett og app må være på; hvilemodus/omstart gir avbrudd. Restart krever ny innlogging, lagrede data beholdes. Funnel er beta og har båndbreddegrenser. Avtal vurderingsperiode; ingen oppetidsgaranti. |

**Kontrollert nå:** Supabase-integrasjonen rapporterte `ACTIVE_HEALTHY`, Paris og Free. Tailscale er installert og status er Running/Online. Lokal mappe `C:\StudyBuddy-Backup` er opprettet; den inneholder foreløpig ingen backup. `tailscale funnel status --json` viser eksisterende HTTPS-ruter `fredriklaptop.tail55f8dd.ts.net:443` til `127.0.0.1:8765` og `:8443` til `127.0.0.1:3000`. Ingen rute peker på StudyBuddy port 8000. Disse eksisterende rutene ble ikke endret; eier/formål må identifiseres før eventuell endring av delingsoppsett. Auth-redirect er ikke inspisert. `/health` gjenbrukes.

**Backup og sletting – avklart forslag:** Dedikert mappe `C:\StudyBuddy-Backup` på denne PC-en, opprettet lokalt og utenfor Git. Studenten godtar at PC-en holder fram til innleveringen 15.12.2026; planen lover ikke beskyttelse ved diskfeil/tap av PC. Når backupjobb er implementert/godkjent: daglig kryptert kopi av database **og separate Storage-filer**, også før konfigurasjonsendringer; roter kopier etter maksimalt **7 dager**. Ingen ekstra tjeneste eller kjøp. Før reelle private filer brukes, skal backupen testes isolert med syntetisk materiale. Ved gjenoppretting holdes appen stengt; slettinger etter kopi påføres på nytt før åpning. Budsjettjournal og blokkering må aldri rulles tilbake til lavere forbruk; eksisterende signeringsnøkkel sikres separat. Supabase Free gir ikke inkludert automatisk gjenoppretting, og en databasekopi inneholder ikke Storage-filene. Ikke opprett nytt hosted-prosjekt for prøven.

Appens sletting rydder aktive data/filer og beholder innholdsfrie utfall i 7 dager. Usikre opplastinger beholder oppryddingsposter til sletting er bevist; eksisterende fysisk retensjonsport står åpen. Egne backupkopier utløper innen 7 dager; dette er ikke et løfte om fysisk sletting i leverandørens interne systemer. Foreslått gjennomgang **15.01.2027**: steng Funnel dersom vurderingen er ferdig, fjern tilhørende redirect og rydd autoriserte testdata/kopier. Det delte Supabase-testprosjektet slettes ikke automatisk.

**Før offentlig lenke:** Felles begrensning for signup/recovery, innholdsfrie logger, hemmeligheter utenfor repo, korrekt origin/CSRF/cookies, restart og faktisk PC/mobil-/to-konto-isolasjon må kontrolleres. Standard Supabase-e-post er begrenset til teamadresser og omtrent 2 meldinger/time; offentlig egenregistrering kan ikke loves. Foreleser må få en uttrykkelig avtalt egen testkonto eller et avklart gratis e-postløp. Ingen konto/e-post opprettes eller sendes nå. Credentialfri demo beholdes for vurdering ved driftsavbrudd; den erstatter ikke live-akseptanse.

**Oppdatert 18.11 kl. 20:19:** Kun-lesende inspeksjon avklarte at 443/8765 tilhører fotballdashboardet og 8443/3000 tilhører SURE. Både Serve- og Funnel-status viser **tailnet only**, ikke offentlig Funnel; tidligere omtale var upresis. Begge ruter bevares. Port 10000 er kandidat for separat StudyBuddy-HTTPS, med ny konfliktkontroll før eventuell aktivering. Se [lokal klargjøring og bevis](hosting-local-preparation-4-1.md).

**Gjenstående avklaring:** Brukeren har valgt PC, gratis offentlig tilgang for foreleser, samme-PC backupmappe fram til innlevering og **egen foreleserkonto; e-post avklares senere**. Ingen konto/e-post er opprettet eller sendt. Backupmappen er fortsatt tom; kryptert backup og 7-dagers rotasjon må implementeres og bevises. Foreslått oppryddingsgjennomgang 15.01.2027 er ikke bekreftet. Felles e-postvern er nå implementert lokalt (221 offline-tester); journal/oppsett er ikke initialisert i drift, og serveren er ikke restartet. Øvrige sikkerhetskontroller gjenstår. Offentlig aktivering krever konkret sluttgodkjenning først når kontrollene og tilgangen er klare.

Kilder kontrollert 18.11.2026: [Funnel og begrensninger](https://tailscale.com/docs/features/tailscale-funnel), [Personal-pris](https://tailscale.com/pricing), [HTTPS/navnepublisering](https://tailscale.com/docs/how-to/set-up-https-certificates), [Supabase Free-kvoter og pausing](https://supabase.com/pricing), [backup](https://supabase.com/docs/guides/platform/backups), [standard SMTP](https://supabase.com/docs/guides/auth/auth-smtp). Free: 500 MB database, 1 GB filer, 5 GB utgående trafikk; kan pauses etter en uke uten aktivitet. Sjekk faktisk bruk før vurdering. Changelog lest; ingen relevant Python/backup-brytende endring identifisert.

**Lokal oppstart klargjort:** `scripts/start-hosted.ps1` og separat `.env.hosted.example` er implementert/reviewet med99 fokuserte tester. Kontrollmodus validerer uten appstart eller tilstandsendring; faktisk start bruker én worker på127.0.0.1:8000, bare loopback som betrodd proxy og ingen access-logg. Gyldig brukt/blokkert modellbudsjett bevares; ny generering avvises fortsatt av eksisterende sperre. Ingen ekte `.env.hosted`, runtime-journal, nøkler eller serverprosess er endret/opprettet. Faktisk konfigurasjon/oppstart og backup gjenstår; dette er ikke publisering eller live-akseptanse. Se [oppstartsdeloppgaven](spec-4-1-local-hosted-startup.md).

**Lokal backupkomponent klargjort:** [Kryptert filpakking, rotasjon og karanteneutpakking](backup-local-4-1.md) er implementert/reviewet med 62 syntetiske kontroller, inkludert ekte Windows DPAPI/Fernet. Klarer eksplisitt klargjorte eksportpakker på maksimalt 64 MiB; erklærer aldri dette som verifisert komplett live-backup. 7-dagers sletting skjer ved kjøring, fra kopiens opprinnelige navnedato, også når ny pakking feiler. Ingen daglig jobb er satt opp. `C:\StudyBuddy-Backup` er fortsatt tom, men ACL er nå begrenset til operatøren, SYSTEM og administratorer. Studenten rapporterte 19.11 manuelt endret databasepassord. Lokal innlesing og autentiseringskontroll er klargjort, men brukeren har utsatt sjekken; ingen lagret credential eller faktisk tilkobling er bekreftet. Ekte DB+Storage-eksport, konsistent kopiering, planlagt kjøring, faktisk isolert databaseimport og budsjett-/sletterekonsiliering gjenstår før backup-gaten kan lukkes.

**Retensjon klargjort 19.11:** Installer med ren `-Plan`, begrenset skjult operatørjobb kl.03/ved innlogging og opprydding før hosted-appstart er implementert lokalt;75 fokuserte offline-tester bestod. Ingen jobb er registrert, ingen ekte backup er laget. Dette gjelder utløpte kopier; daglig eksport/oppretting av backup er fortsatt uferdig. Passordinnlesing/autentisering er uttrykkelig utsatt av brukeren.

**Installed19 November2026:** StudyBuddy-Backup-Rotation is now registered for the current operator. Actual run13:35 completed with Scheduler result0; next daily run20 November03:00 local. This is expiry only; password verification and full daily export remain pending. No public activation.

**Privat hosted-konfigurasjon 19.11:** Git-ignorert `.env.hosted` er klargjort for kandidatadressen på port10000 med eksisterende nøkler/budsjett og deaktivert signup/recovery-e-post. ACL/eier er fredr, SYSTEM og administratorer. Faktisk lokal kontroll validerte konfigurasjon/tilstand, men fullførte ikke fordi eksisterende StudyBuddy PID25940 bruker8000. Ingen omstart eller publisering; `.env`, budsjett og signeringsnøkkel er byteuendret. Passordsjekk, komplett backup/restore, foreleseradresse og offentlig godkjenning gjenstår.
