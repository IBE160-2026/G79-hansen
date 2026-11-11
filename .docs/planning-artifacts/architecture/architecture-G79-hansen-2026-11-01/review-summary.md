# Arkitekturutkast – kontroll og status

**Status: Utkast til gjennomgang.** Dokumentet skiller mellom valg Fredrik har tatt og tekniske forslag som fortsatt må godkjennes.

## Kontroller utført

- Arkitekturspinen ble kjørt gjennom BMAD sin `lint_spine.py`; resultat: 0 funn.
- Uavhengige gjennomlesere kontrollerte kravkobling og tekniske kontrakter. De fant uklarheter i genereringskvittering, passordgjenoppretting, fil-livssyklus, opplastingsrekkefølge og samtidige endringer. Disse er presisert i utkastet.
- Målrettet etterkontroll fra krav- og teknologileserne bekreftet at deres høyt og middels prioriterte funn er lukket på dokumentnivå.
- Den siste målrettede etterkontrollen fra den adversarielle leseren kunne ikke fullføres. Første gjennomgang er bevart i `reviews/review-adversarial.md`; overlappende kontraktspresiseringer finnes i AD-3 og AD-6–AD-8. Dette er derfor ikke en uavhengig bekreftelse av alle de siste endringene.
- Lokal Markdown-/lenkekontroll og `git diff --check` bestod. Ingen backend, Supabase-policy, PDF-flyt, leverandørintegrasjon eller nettleseratferd er kjørt.

## Vedtatte valg

Python/FastAPI med vanlig HTML/CSS/JavaScript, Supabase Auth/Postgres/privat Storage, e-post og passord, eksplisitt lagring, privat innhold per bruker og tilgang til lagrede dokumenter fra flere enheter. Lokal demomodus skal fortsatt virke uten nøkler.

## Forslag som gjenstår

Blant annet BFF-økt/callback-detaljer, samtidighets- og lagringsprotokoller, gjenåpning med skjulte svar, pypdf, én Render-instans, grenser for filstørrelse og øktliv samt sikkerhets- og driftsdetaljer. Modellleverandør, API-nøkkel, hostingkostnad/region og opprettelse av skytjenester er ikke valgt eller utført.

Se [teknisk arkitektur](ARCHITECTURE-SPINE.md), [forklaring](architecture-explained.md), [kilder og avveininger](research-notes.md) og detaljrapportene i `reviews/`.
