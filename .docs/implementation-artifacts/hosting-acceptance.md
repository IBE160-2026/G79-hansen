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

## 20.11.2026 kl.17:11 – brukerbekreftet mobilnettprøve

På instruksen om å bruke telefon med Wi-Fi/Tailscale av, eksisterende konto,
Mine dokumenter og utlogging svarte studenten «fungerer». Dette registreres som
brukerbekreftet ekstern tilgang i den forespurte mobilprøven. Ingen separat
instrumentering eller detaljert bekreftelse av hvert delsteg foreligger.

## 21.11.2026 – brukerbekreftet fremdrift på PC og mobil

Listen var tom etter forrige PDF-prøve. Studenten genererte den samme korte
Context engineering-PDF-en én gang og bekreftet lagring som
«Synk-test 21.11.2026». Eksisterende konto og vanlig appflyt ble brukt.

- **PC → mobil:** Studenten valgte flashcard2/Quiz1 på PC, ventet på
  fremdriftsbekreftelse og fulgte instruksen om samme konto via offentlig URL
  på telefon med Wi-Fi/Tailscale av. «ja» bekreftet de samme posisjonene ved
  åpning fra Mine dokumenter på mobilen.
- **Mobil → PC:** Studenten valgte flashcard1, viste svaret og ventet på
  fremdriftsbekreftelse på mobilen. «ja» bekreftet flashcard1 med skjult svar
  og fortsatt Quiz1 etter omlasting/gjenåpning på PC.
- **Uavhengig utlogging:** «ja» bekreftet at utlogging/omlasting på mobilen
  krevde ny innlogging der, mens PC etter omlasting fortsatt kunne åpne
  Synk-testen. Dette gjelder to økter for samme konto, ikke to forskjellige eiere.

Dette er veiledede brukerbekreftelser fra to fysiske enheter, ikke direkte
agentobservasjon eller instrumentert samtidighets-/offlinekonfliktprøve.
Journalen viser12→13 forsøk og USD0,60→0,65 reservert av5, fortsatt ublokkert;
smoke-telleren er4/uendret. Dette samsvarer med én nødvendig ordinær
brukergenerering for å opprette testmaterialet, ikke målt fakturert kostnad.
Agenten gjorde ingen modell-/providerkall eller konfigurasjonsendring i denne
fremdriftsprøven. Den etterfølgende omstarten er dokumentert separat nedenfor.

## 21.11.2026 kl.10:26 – kontrollert appomstart

Den ene loopbacklytteren på127.0.0.1:8000 og hosted-kommandoen ble
identitetskontrollert før stopp av worker24992. Eksisterende launcher ble
startet skjult med samme `.env.hosted` og én worker. Ny wrapper23368 /
worker17108 lytter på samme adresse/port. Ingen Tailscale-ruter, kontoer,
hosted-innstillinger eller appkode ble endret.

Første kontroll arvet8 appvariabler og ga configuration-invalid. Bare den
separate kontroll-/oppstartsprosessens arvede appvariabler ble fjernet;
`.env.hosted` var urørt. Deretter validerte preflight eksisterende konfigurasjon
og tilstand fram til forventet port-busy før den kontrollerte omstarten.

Før-/etterfingeravtrykk var like for konfigurasjon, modellbudsjett,
signeringsnøkkel, e-postjournal og kontrollerte blokk-/SQLite-sidecar-tilstander.
Journalen er fortsatt13 forsøk/USD0,65 reservert/ublokkert/smoke4. HTTPS med
normal TLS-validering ga200 på arbeidsområdet og anonym auth-status med
available=true/authenticated=false/no-store. Oppstartsloggene var tomme.
Ingen modellkall, e-post, nye kontoer, datagjenoppretting eller kvotenullstilling.

Etter omstart svarte studenten «ja» på at omlasting på PC krevde ny innlogging,
og at Synk-testen etter innlogging/gjenåpning fortsatt hadde flashcard1 og
Quiz1 med skjulte svar. Dette er brukerbekreftet vedvarende materiale/fremdrift
og avsluttet gammel økt etter den faktiske appomstarten. Den anonyme
HTTP-kontrollen over er separat og beviser ikke den private gjenåpningen.

## Gjenstående kontroll

- Resterende eierisolasjon mellom ulike kontoer og privat overlevering av
  reservekonto ved innlevering. Toveis fremdrift, uavhengig utlogging og
  innlogging/gjenåpning etter omstart er brukerbekreftet; Story4.1 er fortsatt åpen.
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
