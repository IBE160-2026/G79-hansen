# Konkret publiseringsforslag – 20.11.2026

**Status: separat godkjent med «ok» og aktivert20.11 kl.17:07.**
Se [aktivering og gjenstående akseptanse](hosting-acceptance.md).
Teksten nedenfor dokumenterer det konkrete forslaget som ble godkjent.
Forslaget gjelder avgrenset offentlig skoleutprøving med syntetisk eller annet
ikke-sensitivt testmateriale. Det avslutter ikke Story4.1 eller full releaseakseptanse.

## Dette blir tilgjengelig

- Inngang: **https://fredriklaptop.tail55f8dd.ts.net:10000/account**.
- Hele StudyBuddy HTTP-appen på `127.0.0.1:8000`, inkludert demo, konto,
  eget materiale og tilhørende API-er, får offentlig HTTPS-tilgang på port10000.
  Alle på internett kan nå inngangen og forsøke registrering; lenken er ikke en adgangskode.
- Privat lagring/bibliotek/fremdrift krever innlogging og eksisterende eierkontroll.
  Generering er aktiv innen eksisterende modellramme; ingen modellkall inngår i aktiveringen.
- Egenregistrering med e-postbekreftelse er prøvd. Eksisterende ordinære `+test1`-konto
  er valgt som reserve; adresse og eget StudyBuddy-passord overleveres privat av studenten.
  Sensor trenger ingen Tailscale-klient. Gmail-/SMTP-/Supabase-hemmeligheter deles ikke.

## Kontrollert kl.17:02–17:03

- Kun loopback8000 lytter, identifisert StudyBuddy-worker24992. Oppstartskontrollen
  validerte konfigurasjon, budsjett, signering og e-postjournal før forventet `port-busy`
  fra den kjørende appen; dette var ingen ny oppstart eller testkjøring.
- Eksakt HTTPS-origin, Secure cookies på, HTTP-loopback-unntak av.
  Vanlig TLS-validering og anonym auth-status200/available=true/no-store bestod.
  `/.env`, `/.env.hosted` og `/.git/config` ga404.
- Hosted-konfigurasjon og backupmappe har kun operatør/SYSTEM/Administrators i ACL.
- Serve10000 peker på8000 uten AllowFunnel.443→8765 (fotballdashboard) og
  8443→3000 (SURE) er fortsatt private. Noden har allerede Funnel-kapasitet for10000;
  forslaget omfatter ingen utvidelse av tailnet-policy.
- Supabase er ACTIVE_HEALTHY i Paris. Sikkerhetsrådgiveren ga ett varsel:
  lekket-passordbeskyttelse er av. Denne funksjonen krever Pro eller høyere;
  ingen oppgradering foreslås. [Leverandørforklaring](https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection).
- Modelljournal:11 forsøk, USD0,55 reservert av5, ikke blokkert.
  E-post: eksisterende varig fellesgrense2/time og1/mottaker/time, ingen reset.
- Siste krypterte appkopi er520630 byte, SHA256
  `3c2463c62803e4320f67b47250627f288cbef1bf7ad150b22e04fea0cb0cf0dd`.
  Tidligere faktisk isolert DB-import/fem filhashkontroller gjenbrukes.
  Prepared-mappen er borte.7-dagers rotasjonsjobb er Ready, siste resultat0,
  neste planlagte kjøring21.11 kl.03:00. Se [backup og avgrensninger](backup-local-4-1.md).

## Eksakt aktivering og tilbaketrekking – ikke kjørt

Etter godkjenning leses rutene på nytt. Bare10000 byttes til offentlig proxy:

```powershell
tailscale funnel --bg --https=10000 http://127.0.0.1:8000
```

Deretter kontrolleres at kun10000 har AllowFunnel, at backend fortsatt er8000,
og at443/8443 er bevart. Ved feil trekkes publiseringen tilbake på samme port:

```powershell
tailscale funnel --bg --https=10000 off
tailscale serve --bg --https=10000 http://127.0.0.1:8000
```

Ingen global reset, ruterportåpning, filserver, providerendring eller policyutvidelse.
Hvis verktøyet krever ny/bredere policytilgang, stoppes aktiveringen for avklaring.
Kommandoene er kontrollert mot installert hjelp og
[Tailscale-dokumentasjonen](https://tailscale.com/docs/reference/tailscale-cli/funnel).
Samme origin beholdes, så ingen nye Supabase-redirects trengs:

```text
Site URL: https://fredriklaptop.tail55f8dd.ts.net:10000/account
https://fredriklaptop.tail55f8dd.ts.net:10000/api/v1/auth/callback[?]state=*
https://fredriklaptop.tail55f8dd.ts.net:10000/api/v1/auth/recovery/callback[?]state=*
```

## Bruk og gjenstående akseptanse

PC, internett og app må kjøre; appen startes manuelt med eksisterende
`scripts/start-hosted.ps1 -EnvFile .env.hosted`. Funnel i bakgrunnen overlever
omstart, mens appen må startes igjen og brukerne logge inn på nytt.
Backup startes manuelt før vesentlige endringer;7-dagers utløpskontroll er automatisk.
Samme-PC-risiko er tidligere akseptert. Ingen ny hostingavgift eller nytt prosjekt.

Etter aktivering prøves først telefon med Wi-Fi/Tailscale av: HTTPS, eksisterende
testkonto, tomt bibliotek og utlogging, uten modellkall eller ny e-post.
Fysisk to-enhetsfremdrift, full isolasjons-/restartakseptanse og faktisk privat
overlevering til sensor står fortsatt åpne; tidligere syntetisk eierskapsevidens
erstatter ikke disse. Story4.1 blir ikke ferdig bare fordi lenken åpnes.

Gjenopprettingsmail er ikke live-prøvd. Full plattform-/rolle-/Auth-/Storage-service-
gjenoppretting og avstemming av slettinger/forbruk etter en eldre kopi er ikke bevist;
en eventuell restore skal holdes lukket til dette er avklart. Rutineeksportens CA-
oppsett og legacy fysisk filrest står fortsatt i issues. Disse grensene tillater
ingen påstand om full sikkerhets-/retensjonsakseptanse eller bruk av reelt privat
studiemateriale. Se [Epic4-grensene](epic-4-context.md) og
[sletteakseptanse](deletion-acceptance.md#remaining-gates-and-conservative-recovery).

Tilgang planlegges fram til innlevering15.12.2026. Manuell gjennomgang15.01.2027
foreslås for å avklare videre vurderingsbehov og stenging; ingen automatisk sletting
eller ny planlagt jobb opprettes. Det delte Supabase-prosjektet slettes ikke.
