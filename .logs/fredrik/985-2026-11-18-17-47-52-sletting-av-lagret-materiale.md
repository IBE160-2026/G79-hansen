# Sletting av lagret materiale – Story 3.4

## 2026-11-18 kl. 18:24 — Fredrik

### Oppgave
Studenten ba om å fortsette med Story 3.4 etter ferdig 3.3, med lite tokenbruk og hensyn til femtimersgrensen. Fristen er 15.12.2026, IBE160 ved Høgskolen i Molde.

### Plan
Gjenbruk [Epic3-kontekst](../../.docs/implementation-artifacts/epic-3-context.md), eksisterende lagringsprotokoll og [Story3.4-spesifikasjonen](../../.docs/implementation-artifacts/spec-3-4-delete-saved-material-completely.md). Navngitt bekreftelse, varig deleting-tilstand, trygg opprydding/gjentakelse og vern mot samtidige lagringer/opplastinger/fremdrift. Hold testene målrettede.

### Resultat
Studenten godkjente konkret plan med «godkjenner». Lokal implementering/review er ferdig i **db8501f861bddd5381059c8ec8315c62c7d852b3**: navngitt bekreftelse/Avbryt, varig deleting og omprøving, eier-/livssyklusvern, eksakte opplastingsforsøk/Storage-kvitteringer og transaksjonell radopprydding med innholdsfrie syvdagers tombstones. Migrasjon **20261118165334** er CLI-opprettet og kjørt bare i isolert lokal testdatabase. Spec done/sprint review gjelder lokalt.

Slutt: **Python115, nettleser sletting7/Lagre25/bibliotek21/fremdrift16, pgTAP40, faktisk lokal provider15 og deterministisk samtidig ID-test bestod**. Hovedagenten kjørte Python115/Lagre25/bibliotek21/SQL40 etter reviewrettelser; fremdrift16/provider15 beholdes fra uendret tidligere kjøring. Én uavhengig review og hovedagentens diff-/matrisekontroll ga tre rettede funn: gammelt Lagre-ferdigsvar etter sletting, samtidig slette-ID på ulike dokumenter og sletteknapp før backend-aktivering. Ingen utsatte reviewfunn. [Detaljert akseptanse](../../.docs/implementation-artifacts/deletion-acceptance.md).

Modellbudsjettene var byteuendret. Ingen nye hosted-kontoer, ekte modellkall, e-poster/passordendringer, hosted-migrasjon, vanlig serverrestart, offentlig deploy eller push. Bare midlertidige syntetiske lokale testkontoer ble brukt/ryddet. Vanlig app beholder eldre backend; ny statisk UI holder Slett deaktivert når deletion-discovery mangler. Baseline89 og kodegrunnlag **b9f7158b86bc62b820de270edff6dbf131bbdd6b** er dokumentert; to tilsynelatende slettede evalueringsfiler var bare sandkassens tilgangsfeil og er ikke endret.

### Åpne punkter
- Story3.4 hosted-aktivering: godkjenn anvendelse av den konkrete migrasjonen i eksisterende studybuddy-test (Free/Paris), deretter lokal serverrestart og avgrensede kontroller med eksisterende syntetiske testdata. Den godkjente planen krever separat hosted-godkjenning.
- Eksisterende fysisk blob-/backup-retensjonsport består: eldre ukjente opplastinger og tapte remove-kvitteringer forblir ventende til uavhengig avklaring. Ikke hev full fysisk sletting eller full release-akseptanse; øvrige porter står fortsatt i issues.md.
