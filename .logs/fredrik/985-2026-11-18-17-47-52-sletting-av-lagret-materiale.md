# Sletting av lagret materiale – Story 3.4

## 2026-11-18 kl. 18:42 — Fredrik

### Oppgave
Studenten ba om å fortsette med Story 3.4 etter ferdig 3.3, med lite tokenbruk og hensyn til femtimersgrensen. Fristen er 15.12.2026, IBE160 ved Høgskolen i Molde.

### Plan
Gjenbruk [Epic3-kontekst](../../.docs/implementation-artifacts/epic-3-context.md), eksisterende lagringsprotokoll og [Story3.4-spesifikasjonen](../../.docs/implementation-artifacts/spec-3-4-delete-saved-material-completely.md). Navngitt bekreftelse, varig deleting-tilstand, trygg opprydding/gjentakelse og vern mot samtidige lagringer/opplastinger/fremdrift. Hold testene målrettede.

### Resultat
Studenten godkjente konkret plan med «godkjenner». Lokal implementering/review er ferdig i **db8501f861bddd5381059c8ec8315c62c7d852b3**: navngitt bekreftelse/Avbryt, varig deleting og omprøving, eier-/livssyklusvern, eksakte opplastingsforsøk/Storage-kvitteringer og transaksjonell radopprydding med innholdsfrie syvdagers tombstones. Migrasjon **20261118165334** er CLI-opprettet og kjørt bare i isolert lokal testdatabase. Spec done/sprint review gjelder lokalt.

Slutt: **Python115, nettleser sletting7/Lagre25/bibliotek21/fremdrift16, pgTAP40, faktisk lokal provider15 og deterministisk samtidig ID-test bestod**. Hovedagenten kjørte Python115/Lagre25/bibliotek21/SQL40 etter reviewrettelser; fremdrift16/provider15 beholdes fra uendret tidligere kjøring. Én uavhengig review og hovedagentens diff-/matrisekontroll ga tre rettede funn: gammelt Lagre-ferdigsvar etter sletting, samtidig slette-ID på ulike dokumenter og sletteknapp før backend-aktivering. Ingen utsatte reviewfunn. [Detaljert akseptanse](../../.docs/implementation-artifacts/deletion-acceptance.md).

Studenten godkjente deretter konkret hosted-aktivering med **«ja godkjenner»**. Den uendrede migrasjonen er anvendt som **20261118172916** i eksisterende studybuddy-test (Free/Paris); RLS/invoker/anonymesperrer/admin-cron ble kontrollert. Vanlig app er restartet på **http://127.0.0.1:8000/workspace**, worker**25940**, med samme ignorerte konfigurasjon. Ny innlogging kreves. Aktiveringsbevis er lokalt committet i **30ab7d9c6579baf82cdd10c15e1b83fc74b609a8**.

Aktivering: hosted**16**, normal sletting**22**, faktisk normalnettleser**6** og normal fremdrift**16** bestod. Eksisterende kontoer ble gjenbrukt; ny syntetisk fil og erstattet versjon ble lagret med injisert modell, satt ventende med simulert feil før Storage DELETE, og ferdigslettet gjennom vanlig server etter fersk innlogging. DB-etterkontroll: null dokument/innhold/bundle/fremdrift/progress-request/Save/objekt/opplastingsforsøk; to innholdsfrie Save-tombstones og slettetutfall beholdt. Eksisterende syntetisk bibliotekpost ble bare brukt til bekreftelse/Avbryt og er bevart. Første hosted-test antok feilaktig403 fremfor korrekt401; samme fil ble gjenbrukt etter testretting. Første nettleserprobe traff eksisterende429 ved oppstartsdiscovery; kontroll etter fullført discovery bestod. Produksjonsgrenser er uendret.

Modellbudsjettene var byteuendret under alle aktiveringskontroller. Ingen nye hosted-kontoer, ekte modellkall, e-poster/passordendringer, offentlig deploy eller push. Kun eksisterende advarsel om lekket-passord-vern i hosted security advisors; Auth-innstillinger uendret. Baseline89 og kodegrunnlag **b9f7158b86bc62b820de270edff6dbf131bbdd6b** er dokumentert; to tilsynelatende slettede evalueringsfiler var bare sandkassens tilgangsfeil og er ikke endret.

### Åpne punkter
- Neste avgrensede omfang er Epic4: offentlig hosting og kontroll fra to fysiske enheter. Eksisterende hosting-/release-port i issues.md gjelder; ingen offentlig utrulling er gjort.
- Eksisterende fysisk blob-/backup-retensjonsport består: eldre ukjente opplastinger og tapte remove-kvitteringer forblir ventende til uavhengig avklaring. Ikke hev full fysisk sletting eller full release-akseptanse; øvrige porter står fortsatt i issues.md.
