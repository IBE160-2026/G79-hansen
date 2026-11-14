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

### Videreføring kl. 23:43
Studenten godkjente den konkrete planen med «gjør det». Planen ble lest på nytt, frosset del låst og status satt til in-progress. Den tidligere dokumentbaselinen ble bevart. Sprinten viser 2.2 under arbeid og lar 2.1 stå åpen. Ett friskt implementeringsagentkontekst fulgte hele spesifikasjonen sekvensielt, etter build-steg 3.

Adapter, registre, API, UI og tester er implementert. Hovedagenten oppdaget at SDKens update_user kan fornye økten internt etter første eierkontroll; implementeringen validerer nå også den endelige SDK-økten før PUT, innen samme tidsbudsjett. Agentkontroll: 145 auth-tester; samlet 207 bestått/én forventet PDF-plattformskip/én eksisterende Starlette-advarsel; 20 auth-browser- og 11 demo-scenarier. Hovedagentens egen fullkjøring ga samme 207/én skip på 26,21 sekunder. JUnit-kontroll bekreftet alle 145 auth-tilfeller bestått og dekning av alle seks matriserader. Hovedagenten leste hele baselinediffen inkludert nye filer og inspiserte recovery ved 200 % visuelt. Den godkjente frosne blokken har uendret SHA-256 `6de3541322786d57b1d8dd61a580dcfb845cf328a984a44d214038b7370422cd`.

Tre uavhengige reviewlag ble startet før noen funn ble triagert. Kanttilfellelaget fant ingen nye funn; blindlaget ga ti funn, verifikasjonslaget to. Hvert funn er vurdert separat i spesifikasjonen før gruppering. En ignorert syntetisk probe reproduserte at en recovery-callback som venter på provider, kan erstatte en nyere innlogging. Syv små rettelsesgrupper er sendt til samme implementeringsagent: callback-rekkefølge, Unicode-lengde, kjente pre-admission-feil, navigasjon til innlogging/recovery, begge PKCE-forsøk i SDK-test, utløp under sluttvalidering og frigivelse av ventende plasser etter providerfeil. Foreløpige resultater over gjelder før disse sluttpatchene; endelig kjøring venter. To lave forbedringsforslag er avvist med begrunnelse. Felles email-throttling før offentlig drift er dokumentert som tidligere eksisterende hardening i deferred-work.md. Ingen betalt tjeneste eller ny hosted-innstilling ble innført.

Ingen ekte e-post eller passordmutasjon er utført. Planens godkjenning gir ikke i seg selv autorisasjon til å endre studentens passord. Spesifikasjonen står midlertidig in-review; faktisk hosted recovery og Story 2.1s bekreftelsesporter er fortsatt åpne.

### Ferdig implementering og review kl. 23:52
Alle syv rettelsesgrupper er implementert og kontrollert av hovedagenten. Siste egen fullkjøring: **213 bestått, én forventet PDF-plattformskip, én eksisterende Starlette-advarsel**, 26,89 sekunder. `test-results/recovery-parent-verification-final.xml` bekrefter **151 auth-tilfeller uten feil/skips**, inkludert tre callback/login-racer, to utløp under sluttvalidering og fem providerfeil uten lekkasje av ventende plasser før vellykket retry. Begge SDK-PKCE-forsøk fullføres med hver sin kode/verifier. Hovedagentens siste browser-auth ga **23 beståtte scenarier**; browser-demo ga **11 beståtte / 21 fixture-genereringer**. Dette er siste kjøring etter reviewpatchene, ikke eldre resultater.

Den opprinnelige syntetiske proben viser nå callback_set_cookie=false, newer_login_cookie_replaced=false, final_authenticated=true og final_recovery_available=false. Hovedagenten leste patchdiffen, oppdaterte den samlede tempdiffen inkludert ny deferred-work-fil og inspiserte oppdatert 200 %-skjermbilde med innloggingsknappen. Frosset blokk har samme hash som over. Diff-check bestod. Ingen kodeendring etter siste testkjøring.

Gammel eid server PID 48256 ble stoppet og stopp bekreftet. Ferdig lokalapp kjører med ignorert `.env`, én worker og ingen reload på http://127.0.0.1:8000/account, PID **35884**, verktøysesjon **37132**. Lesekontroller ga 200, available=true, authenticated=false, recoveryAvailable=false, no-store/no-referrer og nye recovery-/navigasjonskontroller. Ingen ekte e-post eller passord ble sendt/endret. Omstart krever ny vanlig innlogging.

BMAD-steg 5 er fulgt: implementeringsspec done, sprint 2.2 review og faktiske hosted-porter fortsatt åpne. Kode/tester/dokumentasjon er lagret lokalt i **5de0fadc1ba9859c7fccf606df66a6bf15b91ad9**, `feat: add password recovery with restricted sessions`, 15 filer. Ingen push, utrulling, hosted konfigurasjon, kontooppretting, reelt passordbytte eller betalt tjeneste. Loggen lagres separat. Neste produktsteg er hosted callback/template og uttrykkelig autorisert recovery-test, eventuelt videre arbeid uten å hevde full hosted-akseptanse.

### Åpne punkter
- Hosted recovery-akseptanse med uttrykkelig autorisert tester gjenstår: ekstra callback-allowlist/mal, ekte e-post, passordbytte/vanlig innlogging, replay/utløp/feil nettleser/overlapp og separat brukers tilgang. Implementering/review/sluttpatcher er ferdige; ikke be om ny plangodkjenning.
- Story 2.1s resterende hosted-e-postakseptanse beholdes i eksisterende punkt i issues.md; ikke krev nye administrative testbrukere eller merk storyen ferdig.
- Felles bounded recipient/request-throttling før offentlig drift står i deferred-work.md og eget issues-punkt.

## 2026-11-15 kl. 00:00 — Fredrik

### Oppgave
Studenten svarte «ok ta neste steg» på tilbudet om en kort gjennomgang av funksjonen. Fortsett med brukerorientert walkthrough, uten å anta autorisasjon til ekte e-post eller passordbytte.

### Plan
- Bruk BMAD walkthrough og eksisterende spec/commit som utgangspunkt; ikke spør om hvilken endring.
- Forklar forespørsel, begrenset lenke og nytt passord/vanlig innlogging. Hold ekte leverandørtest adskilt.

### Resultat
Walkthrough-skillen og customization-resolveren er lest/kjørt; ingen aktiverings-overrides finnes. Commit 5de0fadc1ba9859c7fccf606df66a6bf15b91ad9 og planens baseline er identifisert. Diffen fra baseline omfatter 17 filer inklusive planleggingslogger og tre nye offentlige HTTP-endepunkter. En leserekkefølge er generert i samtalen fra brukerflyt til grenser/leverandør. Orientering og den korte funksjonsgjennomgangen er klargjort. Lesekontroll av den eksisterende serveren ga status 200, available=true og recoveryAvailable-felt. Ingen ny testkjøring, kode-/konfigurasjonsendring, e-post, konto eller passordmutasjon; tidligere 213/én skip og 34 browser-scenarier er historisk sluttverifikasjon fra implementeringen. Brukerens egen inspeksjon eller akseptanse er ikke bekreftet.

### Åpne punkter
- Walkthroughens menneskelige vurdering og neste detail-pass/testing-steg gjenstår; dette er ikke et nytt godkjenningskrav for den allerede godkjente implementeringsplanen.
- De eksisterende hosted callback/template/e-post/passordportene og e-postgrenser før offentlig drift står fortsatt i issues.md. Avklar konkret tester før eventuell ekte e-post/passordendring.
