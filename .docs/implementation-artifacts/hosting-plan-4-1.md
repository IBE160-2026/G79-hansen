# Hostingplan – Story 4.1

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

**Kontrollert nå:** Supabase-integrasjonen rapporterte `ACTIVE_HEALTHY`, Paris og Free. Tailscale er installert og status er Running/Online. Ingen Funnel-/HTTPS-/Auth-innstillinger er endret. Eksisterende `/health` gjenbrukes.

**Backup og sletting – forslag til godkjenning:** Daglig kryptert kopi av database **og separate Storage-filer**, samt før konfigurasjonsendringer. Oppbevar utenfor Git/synkroniserte mapper, på et separat eksisterende medium studenten angir, i maksimalt **7 dager**. Manglende medium eller mislykket kopi varsles; ingen bekreftet backup betyr at reelle private filer fortsatt venter. Supabase Free gir ikke inkludert automatisk gjenoppretting, og en databasekopi inneholder ikke Storage-filene. Gjenoppretting prøves isolert lokalt med syntetisk materiale før reelle filer; appen holdes stengt, senere slettinger påføres på nytt før åpning. Budsjettjournal og blokkering må aldri rulles tilbake til lavere forbruk; eksisterende signeringsnøkkel sikres separat. Ikke opprett nytt hosted-prosjekt for prøven.

Appens sletting rydder aktive data/filer og beholder innholdsfrie utfall i 7 dager. Usikre opplastinger beholder oppryddingsposter til sletting er bevist; eksisterende fysisk retensjonsport står åpen. Egne backupkopier utløper innen 7 dager; dette er ikke et løfte om fysisk sletting i leverandørens interne systemer. Foreslått gjennomgang **15.01.2027**: steng Funnel dersom vurderingen er ferdig, fjern tilhørende redirect og rydd autoriserte testdata/kopier. Det delte Supabase-testprosjektet slettes ikke automatisk.

**Før offentlig lenke:** Felles begrensning for signup/recovery, innholdsfrie logger, hemmeligheter utenfor repo, korrekt origin/CSRF/cookies, restart og faktisk PC/mobil-/to-konto-isolasjon må kontrolleres. Standard Supabase-e-post er begrenset til teamadresser og omtrent 2 meldinger/time; offentlig egenregistrering kan ikke loves. Foreleser må få en uttrykkelig avtalt egen testkonto eller et avklart gratis e-postløp. Ingen konto/e-post opprettes eller sendes nå. Credentialfri demo beholdes for vurdering ved driftsavbrudd; den erstatter ikke live-akseptanse.

**Gjenstående avklaring:** Godta PC/Funnel-opplegget og driftsavhengigheten; angi eksisterende backupmedium og godta 7 dagers retensjon/gjennomgangsdato; avklar forelesers testkonto. Deretter kan lokal klargjøring gjøres. Offentlig aktivering krever en konkret sluttgodkjenning etter kontrollene.

Kilder kontrollert 18.11.2026: [Funnel og begrensninger](https://tailscale.com/docs/features/tailscale-funnel), [Personal-pris](https://tailscale.com/pricing), [HTTPS/navnepublisering](https://tailscale.com/docs/how-to/set-up-https-certificates), [Supabase Free-kvoter og pausing](https://supabase.com/pricing), [backup](https://supabase.com/docs/guides/platform/backups), [standard SMTP](https://supabase.com/docs/guides/auth/auth-smtp). Free: 500 MB database, 1 GB filer, 5 GB utgående trafikk; kan pauses etter en uke uten aktivitet. Sjekk faktisk bruk før vurdering. Changelog lest; ingen relevant Python/backup-brytende endring identifisert.
