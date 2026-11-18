# Sletting av lagret materiale – Story 3.4

## 2026-11-18 kl. 17:47 — Fredrik

### Oppgave
Studenten ba om å fortsette med Story 3.4 etter ferdig 3.3, med lite tokenbruk og hensyn til femtimersgrensen. Fristen er 15.12.2026, IBE160 ved Høgskolen i Molde.

### Plan
Gjenbruk [Epic3-kontekst](../../.docs/implementation-artifacts/epic-3-context.md), eksisterende lagringsprotokoll og [Story3.4-spesifikasjonen](../../.docs/implementation-artifacts/spec-3-4-delete-saved-material-completely.md). Navngitt bekreftelse, varig deleting-tilstand, trygg opprydding/gjentakelse og vern mot samtidige lagringer/opplastinger/fremdrift. Hold testene målrettede.

### Resultat
Plan/spec er skrevet med status draft; ingen implementering eller migrasjon er gjort. Baseline `uv run pytest tests/test_documents.py tests/test_library.py tests/test_progress.py -q`: **89 bestod**, eksisterende TestClient-advarsel. Baseline **b9f7158b86bc62b820de270edff6dbf131bbdd6b** på main var ren ved Git-kontroll med nødvendig tilgang; to tilsynelatende slettede evalueringsfiler var bare sandkassefeil og er ikke endret.

Eksisterende cleanup beholder med hensikt write_unknown/oppryddingsposter: HTTP200 fra Storage DELETE beviser ikke at en forsinket opplasting har sluttet å skrive. Spec viderefører dette vernet og separat fysisk backup-/retensjonsport. Ingen nye agenter, kontoer, ekte modellkall eller hosted-endringer. Bmad-build steg2 kontrollpunkt1 krever eksplisitt plangodkjenning; konkret spec er sendt til studenten med valg om å fortsette, stoppe etter godkjenning eller gjennomgå. Vent på svar før implementering; les spec fra disk ved godkjenning og gå til steg3 i eksisterende render-snapshot.

### Åpne punkter
- Story3.4: godkjenn konkret spec og gjennomfør implementering med lokale Python-/nettleser-/SQL-/provider-kontroller. Fysisk blob-/backup-retensjon og eldre porter i issues.md består.
