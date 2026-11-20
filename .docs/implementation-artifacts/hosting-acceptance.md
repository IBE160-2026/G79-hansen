# Offentlig hosting – aktivering og akseptanse

## 20.11.2026 kl.17:07 – aktivert etter separat godkjenning

Studenten svarte «ok» på det konkrete spørsmålet om offentlig tilgjengelighet
på vilkårene i [publiseringsforslaget](hosting-publication-proposal-2026-11-20.md).
Godkjenningen gjelder avgrenset skoleutprøving med ikke-sensitivt testmateriale.

**Aktiv URL:** https://fredriklaptop.tail55f8dd.ts.net:10000/account

Utført én gang:

```powershell
tailscale funnel --bg --https=10000 http://127.0.0.1:8000
```

CLI svarte «Available on the internet» og bekreftet bakgrunnskjøring.
Før-/etterkontroll av JSON viste identiske TCP- og Web-seksjoner; eneste
offentlige AllowFunnel-oppføring er verten på10000.443→8765 og8443→3000
er bevart og private. Ingen policyutvidelse eller Supabase-endring ble nødvendig.
Loopbackserveren på8000/worker24992 ble ikke restartet.

Etter aktivering: vanlig TLS-validering ga200 på `/account`, `/workspace` og
anonym `/api/v1/auth/status` (available=true, authenticated=false, no-store).
`/.env`, `/.env.hosted` og `/.git/config` ga404. Disse HTTP-kontrollene ble gjort
fra vertsmaskinen og beviser ikke alene tilgang fra mobilnett.
Ingen generering, e-post, nye kontoer eller endring av private data.

## Gjenstående kontroll

- Telefon via mobilnett med Wi-Fi/Tailscale av: eksisterende konto, Mine dokumenter,
  utlogging og krav om ny innlogging etter omlasting. Studenten er spurt; svar avventes.
- Full fysisk to-enhetsfremdrift, isolasjons-/restartakseptanse og privat
  overlevering av reservekonto ved innlevering. Story4.1 er fortsatt åpen.
- Eksisterende fysisk filrest, CA-rutine og full gjenoppretting/avstemming står
  fortsatt åpne. Reelt privat studiemateriale er utenfor godkjent utprøving.

## Tilbakeføring til privat tilgang

Ved feil eller ønske om stenging brukes bare StudyBuddy-porten:

```powershell
tailscale funnel --bg --https=10000 off
tailscale serve --bg --https=10000 http://127.0.0.1:8000
```

Dette er ikke kjørt. Ingen global reset. PC/app/internett må være tilgjengelig;
app må startes manuelt etter omstart. Manuell gjennomgang15.01.2027 inngår i
godkjent forslag, ingen påminnelsesjobb eller automatisk sletting er opprettet.
