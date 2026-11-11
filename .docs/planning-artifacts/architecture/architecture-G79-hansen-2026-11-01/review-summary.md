# Arkitektur — kontroll og status

**Status: Klar for implementeringsplanlegging, 11.11.2026.** Brukervalg og delegerte tekniske beslutninger er samkjørt med PRD, DESIGN og EXPERIENCE. Dette er en dokumentkontroll, ikke akseptanse av live-appen.

## Utført kontroll

- BMAD-linteren finner ingen mekaniske avvik i arkitekturspinen; se `reviews/lint-final.json`.
- Uavhengig krav-/rubrikkgjennomgang kontrollerte invariantsregler og PRD/UX-dekning. Den presiserte første Lagre: behold nåværende gyldige kort-/quizplasseringer; ved lagring av en ny erstatningsgenerering tilbakestilles fremdriften. Den foreldede arkitekturhandoffen er erstattet.
- Uavhengig teknologigjennomgang kontrollerte offisielle FastAPI-/pypdf-versjoner og Supabase Auth/PKCE/RLS/RPC/Storage-støtte. Prosjektets backend-styrte økt skiller seg eksplisitt fra Supabases nettleser-SDK/SSR-mønster. Parallelle PKCE-forsøk må ha isolerte verifikatorer.
- Uavhengig adversariell gjennomgang fant tre livssyklusuklarheter. AD-3/AD-6/AD-8 krever nå ubetinget lokal utlogging ved leverandørfeil, digest-bundne idempotente Lagre/Slett-operasjoner med sikker svarrepetisjon og full sporing av gamle/provisoriske filer til sletting er ferdig. Uavklarte opplastingsutfall kan ikke gi falsk slettesuksess.
- Struktur- og språkgjennomgang av studentforklaringen førte til tydeligere skille mellom vedtatte regler og kandidater, færre datogjentakelser og et konkret navn på FastAPI-serverens ansvar.
- Målrettede etterkontroller er dokumentert i de respektive sluttrapportene. Historiske rapporter fra tidligere omfang beholdes, men er ikke bevis for denne leveransen.

## Gjeldende grunnlag

- [Teknisk arkitektur](ARCHITECTURE-SPINE.md)
- [Forklaring for student og sensor](architecture-explained.md)
- [Forsknings-/kildenotater](research-notes.md)
- [Krav-/rubrikkrapport](reviews/review-final-rubric.md)
- [Teknologirapport](reviews/review-final-tech.md)
- [Adversariell rapport](reviews/review-final-adversarial.md)
- [Struktur-/språkrapport](reviews/review-final-editorial.md)

## Milepæler som gjenstår

PDF-kandidaten må bestå det avtalte tekstuttrekkseksperimentet. KI-leverandør/modell/API/budsjett og hosting/region/e-post/kvoter må velges før sine integrasjons- og oppsettsoppgaver. Live sikkerhets-/lagringsfunksjoner må bestå tobruker-, restart-, feil-, samtidighets- og fil-livssyklustester før private data aksepteres. Nettleser-, zoom- og skjermleserkontroll gjenstår før appakseptanse. Demoarbeidet kan starte uten disse eksterne tjenestene; det er ingen påstand om ferdig autentisering, varig lagring eller ekte KI.
