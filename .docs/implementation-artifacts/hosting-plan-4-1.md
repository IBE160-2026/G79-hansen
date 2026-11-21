# Hostingplan – Story 4.1

## Sensortilgang – klargjøring21.11

[Kort sensorveiledning](assessor-access.md) samler den publiserte URL-en,
innlogging/e-postgrenser, lokal demo ved driftsavbrudd og en avgrenset prøve.
Den inneholder ingen innloggingsopplysninger. Eksisterende reservekonto er
fortsatt valgt; privat overlevering gjenstår. Praktisk kontroll mellom kontoen
som eier Synk-testen og en annen eksisterende konto pågår.
De daterte forslags-/aktiveringsnotatene nedenfor er historikk.

## Offentlig aktivering20.11 kl.17:07 – separat godkjent

Studenten svarte «ok» på det konkrete publiseringsforslaget. Funnel10000 er nå
aktiv mot8000. Kun denne vert/port har AllowFunnel=true; TCP-/Web-rutene er
identiske før/etter, og443/8765 samt8443/3000 forblir private. Ingen omstart,
provider-/redirect-/policyendring, e-post eller modellkall.
HTTPS konto/arbeidsflate/auth-status svarte200 og hemmelige filstier404.
[Akseptansenotatet](hosting-acceptance.md) skiller vertsmaskinkontrollen fra
telefonens mobilnettkontroll, som studenten bekreftet med «fungerer» kl.17:11.
Toveis fysisk PC/mobil-fremdrift, uavhengig utlogging og ny innlogging/
gjenåpning med bevart fremdrift etter appomstart er brukerbekreftet21.11.
Resterende eierisolasjon mellom ulike kontoer og privat kontooverlevering
gjenstår. Status er avstemt21.11 mot de daterte resultatene;
tidligere seksjoner nedenfor er historikk. Story4.1 og de avtalte
test-/retensjonsgrensene består.

## Sluttkontroll20.11 kl.17:03 – konkret forslag klart for separat godkjenning

[Publiseringsforslaget](hosting-publication-proposal-2026-11-20.md) angir eksakt
offentlig URL, hele appflaten, bare port10000, uendrede redirects, kontotilgang,
aktivering/tilbaketrekking og kontroll etter aktivering. Kun-lesende kontroll fant
gyldig lokal konfigurasjon/tilstand, normal TLS og404 på hemmelige filstier,
uendret kryptert kopi, fungerende rotasjonsjobb og private ruter. Supabase er
ACTIVE_HEALTHY i Paris; eneste sikkerhetsvarsel gjelder betalt lekket-passordvern.
Eksisterende fysisk-retensjons-/full-restore-/endelig akseptansegrenser består;
forslaget er avgrenset til offentlig skoleutprøving med testmateriale.
Ingen app-/provider-/ruteendring, tester, e-post eller modellkall ble utført.
Funnel er fortsatt av. Brukeren må godkjenne dette konkrete forslaget separat.

## Sensortilgang20.11 kl.16:15 – eksisterende testkonto valgt som reserve

Studenten valgte først en annen reservekonto senere, men presiserte deretter
«eller vi kan bruke den kontoen du foreslo». Siste valg gjelder: den nye
`+test1`-kontoen brukes som ferdig reservekonto, i tillegg til selvregistrering.
Kun-lesende kontroll fant nøyaktig én slik bekreftet bruker med ordinær
`authenticated`-rolle og0 lagrede dokumenter. Kontoen er med i den oppdaterte
krypterte kopien; ingen ny konto, rolle, passordendring eller e-post trengs nå.

Studenten beholder den konkrete testadressen og kontoens eget StudyBuddy-passord
privat og overleverer disse til faglærer/sensor sammen med oppgaven i en privat
kanal. Ingen passord eller innloggingsvedlegg legges i repoet. Google-app-passordet
brukes bare av e-postsenderen og inngår ikke i sensorens innlogging.
Selve overleveringen er ikke utført; mottaker/innleveringskanal avklares ved behov.

**Utkast til tilgangstekst etter separat publiseringsgodkjenning:**

> StudyBuddy: https://fredriklaptop.tail55f8dd.ts.net:10000/account
> Du kan opprette egen konto og bekrefte den via e-post. En ferdig testkonto
> leveres også privat som reserve. Bruk bare eget, ikke-sensitivt testmateriale.
> Den lokale demoen og oppstartsinstruksen finnes i README dersom nettsiden er
> utilgjengelig. Nettutgaven avhenger av at studentens PC og app kjører.

Dette er et lokalt utkast, ikke en sendt melding eller offentlig lenke.
Funnel er fortsatt av. Tilgangsopplegget er konkretisert; tidligere åpne
sikkerhets-/akseptanseporter må avstemmes før det endelige publiseringsforslaget.

## Backup oppdatert20.11 kl.16:10

Ny kryptert appkopi på520630 byte er opprettet og kontrollert:
`C:\StudyBuddy-Backup\studybuddy-20261120T150948Z-a98e54990bf74736b5a838856f33b1b2.sbb`.
Fersk databaseeksport og faktisk isolert import bekreftet4 Auth-brukere,
inkludert den nye bekreftede testkontoen. Alle fem gjenbrukte Storage-filer
matchet den gjenopprettede ferske databasens kontrollsummer. E-postjournalens
2 reservasjoner og eksisterende budsjett/signering er inkludert uten reset.
Ingen ukryptert stagingmappe ble opprettet. Den gamle kopien beholdes med
eksisterende7-dagers utløpskontroll. Se [backupresultat og grenser](backup-local-4-1.md).

StudyBuddy ble pauset kort og startet igjen med eksisterende launcher:
worker24992/hidden wrapper33016 på loopback8000. Privat HTTPS auth-status200
bestod, konfigurasjon/ruter og de tre tilstandsfilene er uendret. Ny innlogging
kreves etter omstarten. Ingen modellkall, e-post eller offentlig Funnel.
Praktisk reservekonto/overlevering og tidligere åpne akseptanseporter må fortsatt
avklares før et konkret publiseringsforslag og separat godkjenning.

## Registrering bekreftet20.11 kl.16:00 – e-post og HTTPS-retur fungerer

Etter korrigert Gmail-konto/app-passord og brukerbekreftet lagring i Supabase
rapporterte studenten mottatt bekreftelsesmail. Studenten bekreftet deretter
retur via lenken i samme PC-nettleser/profil og «Du er logget inn» på StudyBuddy.
Kun-lesende SQL-opptelling viste én ny Auth-bruker siste15min, én bekreftet,
én med +test1@gmail.com-suffiks. Ingen adresse/passord/token er hentet ut.
Studenten bekreftet også at utlogging og omlasting krever ny innlogging, og at
vanlig passordinnlogging med samme testadresse deretter fungerer. Dette er en
avgrenset faktisk brukskontroll, ikke ny full isolasjons-/sikkerhetsakseptanse.
Dette verifiserer denne manuelle aliasregistreringen, e-postbekreftelsen og
privat HTTPS/PKCE-retur; ikke alle e-postleverandører, passordgjenoppretting
eller offentlig tilgang. Den manuelle ut-/passordinnloggingen er brukerbekreftet.

Journalen er gyldig med2 reservasjoner; ingen kvote er økt eller nullstilt.
SMTP-avsenderen beholder vanlig Gmail-adresse. Aliaset er en egen vanlig
StudyBuddy-testkonto og gir ikke Supabase-prosjektrolle eller Gmail-tilgang.
Kryptert backup fra før opprettingen mangler både ny Auth-bruker og e-postjournal;
oppdatert manuelt startet backup må klargjøres før eventuell publisering.
Ingen modellkall eller offentlig Funnel er aktivert under kontrollen.

## SMTP-status15:49 – ny innlogging godtas av Google

Studenten oppga at nytt app-passord er opprettet på riktig Gmail-konto.
Én ny lokal AUTH-only-kontroll ga `accepted`, bekreftet av studenten og
statusfilen sist endret15:49:31. `email_sent=false`, `credentials_saved=false`.
Google godtar altså den nye kombinasjonen på PC-en. Dette beviser ikke at
Supabase har fått samme verdier eller at bekreftelsesmail/HTTPS-retur fungerer.
Neste manuelle steg er å lagre den samme Gmail-adressen som Sender email/Username
og det nye app-passordet direkte i Supabase Password. Ingen lokal omstart trengs.
Behold providergrense2/time. Ny registrering mot samme mottaker tidligst16:31;
journalens faktiske adgangstid er16:30:12 og kvoten er ikke endret/nullstilt.

## Ny registreringsprøve15:30 – SMTP-avvisning bekreftet lokalt15:40

Korrigert lokal kontroll15:40 ga `smtp_auth=rejected`, `smtp_status=535`,
`reason=bad_credentials`, `email_sent=false`, `credentials_saved=false`.
Google godtar altså ikke kombinasjonen som ble skrevet inn i kontrollvinduet.
Studenten skal velge riktig ny Gmail-konto i Google, opprette et nytt app-passord
og bruke samme adresse i kontrollen og Supabase. Ingen Google-kontopassord skal
endres eller deles. Korrigert innlegging/ny vellykket AUTH-prøve avventes.

Etter brukerbekreftet ny SMTP-innlegging og naturlig kvoteutløp ga ny manuell
registrering den generiske meldingen om utilgjengelig innlogging. Studenten
bekreftet at ingen e-post kom. Journalen har én ny reservasjon; ingen nullstilling.
Faktisk HTTPS auth-status svarer200/available=true. Prosjektet er ACTIVE_HEALTHY,
og0 nye Auth-brukere ble funnet siste15min ved kontroll15:31.
Nyeste loggutvalg hadde ingen Auth-feil fra dette forsøket; dette beviser ikke
at SMTP-innlogging er rettet eller at ingen request nådde leverandøren.
GET Auth-settings med vanlig TLS og samme transport som appen ga200 på under
ett sekund. Én avgrenset offline SDK-probe konstruerte signup/PKCE med
MockTransport, uten nettverkskall. Ingen av disse kontrollene sender e-post.

En lokal, interaktiv SMTP AUTH-kontroll er åpnet for studenten under test-results.
Den bruker smtp.gmail.com:587 med verifisert STARTTLS, maskert app-passord,
ingen SEND MAIL/DATA og ingen lagring av adresse/passord. Bare statuskode/resultat
lagres. Første statusfil viste uspesifikk forbindelsesfeil selv om studenten
rapporterte rejected. En separat SMTP/TLS-kontroll uten AUTH bestod. Hjelperen
ble rettet til én AUTH PLAIN uten mekanisme-retry og direkte close, slik at
avslutningsfeil ikke kan overskrive AUTH-resultatet. Ny brukerinnlesing ga
den presise535-statusen ovenfor. Appens server, produktkode og kvoter er uendret.

## Registreringsprøve20.11 – Google avviser SMTP-innlogging

Studenten autoriserte én manuell registrering og rapporterte deretter
«For mange pågående forsøk» og ingen mottatt e-post. Kun-lesende kontroll fant
én journalreservasjon fra13:56:08 lokal tid, med mottakergrense én/time.
Supabase-loggspørring for tidsrommet fra12:50UTC fant én Auth-feil500 /
unexpected_failure; server-side klassifisering av feilteksten ga
`smtp_bad_credentials` («Username and Password not accepted»).
Ingen rå loggtekst, adresser, passord, tokens eller IP-er ble hentet ut.
Kun-lesende opptelling fant0 nye Auth-brukere siste30 minutter.

Første SMTP-forsøk feilet altså ved avsenderinnlogging, mens senere forsøk kan
treffe den bevarte mottakerkvoten. Den generiske meldingen skiller ikke disse
årsakene. Studenten spurte om å endre grensen; anbefalingen er å rette Gmail-
brukernavn/app-passord først. Ingen kvote/journal er endret eller nullstilt.
Tidligste nye forsøk mot den samme mottakeren er etter14:56:09 lokal tid;
bruk14:57 som praktisk margin og bare etter korrigert SMTP-oppsett.
Ny app-passordinnlegging må skje direkte i dashboardet med riktig Google-konto.
Ingen ny utsending er utført av agenten.

## E-postklargjøring20.11 – SMTP lagret, journal aktiv privat

Studenten bekreftet «lagret» etter Gmail custom SMTP-oppsett og providergrense
på2 e-poster/time. Dette er brukerbekreftet; SMTP-levering er ikke prøvd og
faktisk avsenderadresse er ikke oppgitt. Passordet er ikke mottatt av agenten.
Eksisterende init-kommando opprettet
`C:\StudyBuddy-State\auth-email-admission.sqlite3` som normal operatør fredr.
Mappen har beskyttet ACL for operatøren, SYSTEM og Administrators.
Read-only `inspect_ready()` bestod,0 reservasjoner; ingen utsending/reservering.
Journalen må bevares og inkluderes som email_journal i neste manuelle backup;
kopien fra før opprettingen inneholder den ikke. Ikke gjenopprett eldre tom
kvotetilstand over senere reservasjoner.

Studenten bekreftet nå at Site URL
`https://fredriklaptop.tail55f8dd.ts.net:10000/account` og de to rettede
HTTPS-returmønstrene med `[?]` nedenfor er lagret. Faktisk e-postretur er ikke prøvd.
Kun `AUTH_EMAIL_ADMISSION_PATH` er endret i den private `.env.hosted` til
journalstien ovenfor. Eksisterende worker22936 ble identitetskontrollert og
erstattet via eksisterende launcher: ny worker25820, hidden wrapper32896,
fortsatt én worker/loopback8000. Preflight bestod etter portfrigivelse.
Faktisk privat HTTPS auth-status ga200/available/ikke innlogget, no-store og
Secure/HttpOnly/SameSite=Lax browser-cookie. Standard TLS-validering bestod.
Tailscale-konfigurasjonen er strukturelt uendret; ingen offentlig Funnel.
Budsjett, signeringsnøkkel og journal var byteuendret før/etter; ingen reservasjon,
utsending eller modellkall. Tilkoblingen aktiverer appens eksisterende e-postvern,
men beviser ikke SMTP-levering. Studenten er spurt om én manuell registreringsprøve
med den nye Gmail-adressen; passord skrives bare i nettleseren, ikke i chat.

## Sensortilgang20.11 – begge alternativer valgt

Studenten valgte både selvregistrering og en ferdig testkonto som reserve.
Registrering/bekreftelse finnes i appen; ingen ny autentiseringsplattform trengs.
Reservekontoen skal være en vanlig appkonto, uten prosjekt-/administratortilgang
i Supabase. Konto, e-postadresse og sikker overlevering av innlogging klargjøres
når de konkrete opplysningene foreligger. Ingen konto eller e-post er opprettet/sendt.

Kun-lesende Auth-settings20.11: e-postleverandør på, signup tillatt og
automatisk e-postbekreftelse av. Appens utsending er fortsatt deaktivert.
Disse offentlige flaggene viser ikke om custom SMTP er satt opp.
Supabases [standard-SMTP](https://supabase.com/docs/guides/auth/auth-smtp) sender
bare til teamadresser og er begrenset til to meldinger/time. En egnet sender må
derfor avklares før selvregistrering loves til sensorens vanlige e-postadresse.
Studenten bekreftet20.11 at «Enable custom SMTP» er deaktivert i dashboardet.
Tidligere vellykket registrering13.11 brukte egen autorisert teamadresse;
den testen dokumenterer ikke levering til sensorens vanlige adresse.

Gratis sender er undersøkt, men ikke valgt: [Brevo Free](https://help.brevo.com/hc/en-us/articles/208580669-FAQs-What-are-the-limits-of-the-Free-plan)
har300 utsendinger/dag. [Transaksjonsutsending krever separat aktivering](https://help.brevo.com/hc/en-us/articles/115000188150-Troubleshooting-Issues-with-Brevo-SMTP).
Brevo anbefaler [autentisert eget avsenderdomene](https://help.brevo.com/hc/en-us/articles/208836149-Create-a-new-sender-From-name-and-From-email);
gratis e-postdomener kan ikke autentiseres. Gratis tjeneste er derfor ikke
det samme som et ferdig, pålitelig oppsett uten eget domene. Studenten bekreftet
20.11 at eget domene ikke finnes. Ingen ny tjeneste, domene, nøkkel, konto eller
utsending er opprettet.

Neste avgrensede kandidat er eksisterende Gmail som avsender via
[`smtp.gmail.com`](https://developers.google.com/workspace/gmail/imap/imap-smtp),
med [totrinnsbekreftelse/app-passord](https://support.google.com/accounts/answer/185833?hl=no).
App-passord er ikke tilgjengelig for alle kontoer; dette må avklares før oppsett.
Supabases [Google-SMTP-eksempel](https://supabase.com/kb/troubleshooting/using-google-smtp-with-supabase-custom-smtp-ZZzU4Y)
er prøvd med Workspace og er ikke vår verifikasjon av en privat Gmail-konto.
Studenten er spurt om en egnet konto finnes og ønskes brukt; avsenderadressen
blir synlig for mottakerne. Ingen Gmail-/Supabase-innstillinger er endret, og
ingen e-post er sendt. Begge tilgangsmåter er fortsatt valgt inntil annet avtales.

Før aktivering av registreringsflyten: kontroller sender og mottakeradgang,
sett riktig HTTPS Site URL og snevre callback-regler, klargjør eksisterende
varige e-postvern og gjør en uttrykkelig autorisert e-post-/bekreftelsesprøve.
Behold bekreftelseskrav og tidligere nettleserbinding; ingen kvoter/journaler
nullstilles. Eksakte regler fra det eksisterende lokale oppsettet flyttes til
HTTPS-origin, med bare state-verdien som wildcard:

- `https://fredriklaptop.tail55f8dd.ts.net:10000/api/v1/auth/callback[?]state=*`
- `https://fredriklaptop.tail55f8dd.ts.net:10000/api/v1/auth/recovery/callback[?]state=*`

**Rettet20.11:** Studenten fikk «URL can't contain backslashes» i dashboardet
med agentens tidligere `\?`-instruks. Bruk `[?]` som bokstavelig spørsmålstegn
i [glob-syntaksen](https://github.com/gobwas/glob/blob/master/glob.go).
Begge strengene består lokal WHATWG URL-parsing uten bakstrek. Dashboardlagring
og faktisk returflyt er fortsatt ikke bekreftet; dette er ingen leveringsprøve.

Dette er klargjøringspunkter, ikke utførte providerendringer. Foreløpig privat
HTTPS/password-login beholdes, og offentlig Funnel krever fortsatt separat godkjenning.

**Tilgangspresisering20.11:** Del1-sensorveiledningen s.5 ber om testdata eller
testbrukere ved behov og tydelig README, men angir ikke om sensor skal få en
ferdig konto eller registrere seg selv. Studentens valg «egen foreleserkonto»
fastsetter ikke opprettingsmåten. Tidligere omtale av foreleserens e-post som
nødvendig neste steg var vår antakelse om forhåndsoppretting, ikke et oppgavekrav.
Begge tilgangsmåter er nå valgt som beskrevet ovenfor; selve klargjøringen
gjenstår. Hosted-e-post er fortsatt deaktivert, så
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
