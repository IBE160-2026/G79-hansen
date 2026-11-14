# Passordgjenoppretting

## 2026-11-14 kl. 15:39 — Fredrik

### Oppgave
Studenten ba «ok, da går vi videre». Den ekstra e-posttesten fra Story 2.1 står åpen; neste planlagte oppgave er Story 2.2, «Glemt passord». Studenten godkjente «Ja, lagre og fortsett» på lagring av fire dokumentoppdateringer og videre arbeid.

### Plan
- Følg rendret BMAD build, bruk eksisterende Epic 2-kontekst og implementert innlogging uten å erklære Story 2.1 ferdig.
- Undersøk kode og låst SDK, skriv en konkret spesifikasjon og presenter workflowens godkjenningspunkt før implementering.

### Resultat
De fire godkjente dokumentfilene er lagret i `32b1586bf6c1ebc3297205eefe538c1a3b176af9`: auth-setup, datert Paris-presisering i spesifikasjon, refleksjonsgrunnlag og README. Commiten inneholder bare disse filene; arbeidskopien var deretter ren. Ingen push.

BMAD build ble rendret én gang. Workflow/steg 1/steg 2/mal er lest fullt, med nødvendig eskalering ved sandkassens tilgangsavvisning. Epic 2-konteksten er nyere enn alle planleggingsfiler og ble gjenbrukt. Ingen tidligere ferdig Story 2 finnes; Story 2.1 er fortsatt in-progress. Skillens eksplisitte instruks om dype agentsøk ble fulgt med én read-only-agent; ingen implementeringsagent ble startet.

Ny konkret plan: `.docs/implementation-artifacts/spec-2-2-recover-a-password-through-a-restricted-session.md`, status draft, route dispatch, baseline lik dokumentcommiten over. Planen dekker generisk recovery-request, browser/purpose/verifier-bundet PKCE, separat begrenset autoritet, engangs passordoppdatering og vanlig innlogging etterpå. Eksisterende Origin/CSRF, body-/tids-/kapasitetsgrenser, cookie-/loggbeskyttelse og sen-respons-rettelser bevares. Samme opaque cookie skal referere til enten normal eller begrenset autoritet i adskilte registre; recovery kan aldri gi vanlig privat tilgang.

Installert SDK lagrer `verifier/PASSWORD_RECOVERY`, mens eksisterende adapter eksplisitt sender pending.verifier. Dette må håndteres og transporttestes. SDKens set_session kan fornye tokens; samme operasjonsbudsjett og eierkontroll før mutasjon kreves. Offisiell Supabase-dokumentasjon og lokal SDK-kode ble kontrollert. Planen ble forkortet og selvkontrollert; ingen åpne produktvalg krever et eget spørsmål før planens godkjenningspunkt. Diff-check bestod. Ingen appkode, appinnstilling, konto eller passord er endret, ingen e-post sendt og ingen nye funksjonstester kjørt.

Studenten er spurt om godkjenn og fortsett / godkjenn og stopp / gjennomgå planen først, etter BMAD steg 2 CHECKPOINT 1. Ingen svar på denne konkrete planen er antatt; status er fortsatt draft og implementering har ikke startet. Den tidligere godkjenningen gjaldt dokumentlagring/videreføring, ikke en spesifikasjon som ennå ikke var skrevet.

### Åpne punkter
- Godkjenning og deretter implementering/test av Story 2.2; speilet i issues.md. Ingen ekte testmail/passordmutasjon inngår automatisk i implementeringskontrollene.
- Story 2.1s resterende hosted-e-postakseptanse beholdes i eksisterende punkt i issues.md; ikke krev nye administrative testbrukere eller merk storyen ferdig.
