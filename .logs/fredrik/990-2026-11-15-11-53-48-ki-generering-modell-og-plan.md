# KI-generering – modell og plan for Story 2.5

## 2026-11-15 kl. 11:53 — Fredrik

### Oppgave
Start en ny BMAD-build for Story 2.5 med modellavklaring og konkret implementeringsplan som første leveranse. Undersøk kode, dokumentasjon og tilgjengelige integrasjoner før spørsmål; sammenlign 2–3 aktuelle modeller fra oppdaterte offisielle kilder. Legg frem nye valg og plan før implementering eller modellkall. Tidligere godkjenninger, tester og begrensninger skal bevares.

### Plan
- Les CLAUDE.md, issues, [Story 2.4-loggen](991-2026-11-15-10-23-43-eget-kildemateriale.md), kildespesifikasjon/akseptanse, Epic 2-kontekst og Story 2.5. Følg ny BMAD build steg 1/2, med tidligere story som kontinuitet.
- Undersøk kilde-/økt-/UI-/læringskontrakter og integrasjoner uten app-/konto-/serverendringer. Sammenlign modellspesifikasjoner, pris, struktur, datahåndtering og grenser fra leverandørenes egne sider.
- Skriv [konkret draft-plan](../../.docs/implementation-artifacts/spec-2-5-generate-all-learning-parts-from-the-source.md), [modell-/kostnadssammenligning](../../.docs/implementation-artifacts/model-decision-2-5.md) og [genereringsprotokoll](../../.docs/implementation-artifacts/generation-protocol-2-5.md); legg frem fem åpne valg og be om ny godkjenning.

### Resultat
Arbeidskopien var ren ved oppstart. Baseline er **5737bbf45902f3621fc90ecb8ab62e09eecbf100**, etter kodecommit **c5b207ff8523c9b62668043f2ea69466e9e39ac7**. BMAD-build ble rendret nøyaktig én gang for denne nye oppgaven; workflow, steg 1, steg 2 og spec-mal ble lest. Cached Epic 2-kontekst er gyldig og nyere enn samtlige planleggingsfiler. Eksakt sprintnøkkel er `2-5-generate-all-learning-parts-from-the-source`. Specen står **draft**, route **dispatch**; sprint 2.5 forblir **backlog**.

To kun-lesende agenter undersøkte henholdsvis kilde-/økt-/kvitteringskontrakter og UI-/testmønstre etter steg 2s delegasjonsinstruks. De endret ingen filer og kjørte ingen tester. Kildeuttrekket mangler bevis som kan beskytte den kanoniske kilden mot endringer ved senere innsending til generering. Planen foreslår signert kildeakseptanse, flyktig metadata-/hashautoritet, ordnet ugyldiggjøring og signert 30-minutters genereringskvittering. Fremtidig Save må kontrollere gjeldende autoritet i tillegg til signatur. Ingen kildebevarende serverregister/database eller Save-endepunkt er planlagt i denne storyen.

Offisielle, oppdaterte sider for **GPT-6 Luna**, **Gemini 3.8 Flash** og **Claude Sonnet 5.5** ble kontrollert. Luna anbefales foreløpig på grunn av lav pris, strukturerte svar og eksplisitt cachemodus uten cachepunkter. Dette er et begrunnet KI-forslag, ikke en studentbeslutning eller målt norsk/kildefast kvalitet. Sammenligningen dokumenterer også Googles annonserte prisøkning fra 1. januar 2027 og EØS-unntaket i datavilkårene. Leverandørenes sikkerhets-/rettslige lagringsunntak er ikke omtalt som null lagring.

Eksempel med 10 000 input-/4 000 outputtokens gir **USD 0,003** for Luna, **USD 0,0225** for Gemini ved dagens pris og **USD 0,060** for Sonnet. Forslaget er **USD 5 samlet bruksramme**, **USD 0,05 konservativ reservasjon per forsøk**, ingen automatisk nullstilling/refusjon ved usikker kostnad/omstart og maksimalt fire automatiserte syntetiske livekontroller etter uttrykkelig godkjenning og tilgjengelig API. Avgifter/veksling og eventuell finansiering er skilt fra bruksanslaget. Ingen konto eller kreditt er opprettet eller kjøpt.

Tilgjengelige integrasjoner ga ingen inferens-/modelltilgang til appen. Forekomst av vanlige OpenAI-/Anthropic-/Gemini-nøkkelnavn ble kontrollert i eksisterende ignorert `.env` og prosessmiljø; ingen ble funnet. Ingen verdier ble skrevet ut. Dette avklarer lokal konfigurasjon, ikke om studenten har prosjekt/nøkkel et annet sted. Eksisterende Supabase-tilkobling/Free/Paris ble ikke gjenåpnet som nytt valg.

Spesifikasjonen er selvkontrollert og målt til **1594 tokens** med `tiktoken`/`o200k_base` som midlertidig uv-verktøyavhengighet. Appens avhengigheter/lockfil er uendret. En ren syntetisk størrelsesberegning ga 258 895 UTF-8-byte for 10 000 emojiavsnitt med lange kanoniske ID-er; den begrunner kompakte modellnøkler med serveroppløsning, ikke en ny funksjonstest. Planen angir 60 sekunders servergenereringsfrist etter autentisering/opptak, separat begrenset uttrekk og 70 sekunders nettleserventetid for genereringsfasen; 8 000 outputtokens og 256 KiB modellforespørsel/-respons er forslag som må godkjennes.

`git diff --check` bestod. Tidligere Story 2.3/2.4-spesifikasjoner, kildeakseptanse, sprintstatus, appkode, `.env.example`, `pyproject.toml` og `uv.lock` er identiske med baseline. Tidligere **306 bestått/én plattformskip og 19 kilde-/33 auth-/11 demoscenarier** er bevart som historisk evidens; ingen nye funksjonstester eller live-kvalitetsresultater er hevdet. Modellkall, nøkkelvalidering, serverrestart, passord-/konto-/e-posthandlinger, hosted-endringer, kostnader og deploy er ikke utført.

Plan-/sammenlignings-/protokolldokumentene og refleksjonsgrunnlaget er lagret lokalt i **829b0cc06667b2ab2b1a8e5a0c82a0acb0f0c266** (`docs(ai): propose story 2.5 model gate and generation plan`). Ingen push. Studentens egne refleksjoner eller godkjenning er ikke skrevet av KI.

**Oppfølging 15.11 kl. 12:01 – godkjenning og API-oppsett:** Studenten svarte «Godkjenn planen med forslagene. API-tilgang: har / trenger oppsett». Modell, kostnadsramme, datahåndtering og tids-/størrelsesgrenser ble registrert som godkjent; API-delen med begge alternativer ble ikke tolket som faktisk tilgang. Etter lokal forekomstkontroll uten verdier stilte KI ett spørsmål, og studenten svarte **«Trenger hjelp med oppsett»**. Samme konkrete plan skal ikke godkjennes på nytt.

Spesifikasjonen ble lest fra disk før beslutningene ble ført inn i godkjenningsblokken; baseline og draft/backlog beholdes fordi API-forutsetningen ennå ikke er etablert. Godkjent blokk, med markører og LF-normaliserte UTF-8-linjer, har SHA-256 **2b453bfa703d032fc54784412a7239b435ed4be9954e5f820f3e4fb563395301**. De fem spørsmålene er erstattet av beslutninger og en praktisk Readiness Gate; ingen appimplementering er startet.

Offisielle sider om OpenAI-prosjekter, nøkler, quickstart og forhåndsbetaling ble kontrollert. [Lokal oppsettsveiledning](../../.docs/implementation-artifacts/model-setup-2-5.md) skiller kjøp av kreditt fra godkjent appbruk: minimumskjøp USD 5, standardforslag USD 10 og automatisk påfyll på som standard ved oppsett. Studenten håndterer innlogging, eventuell betaling og nøkkeloppretting privat; KI har ikke opprettet konto/prosjekt, endret hosted-innstillinger eller kjøpt kreditt. Et tomt `OPENAI_API_KEY=`-felt ble lagt til i eksisterende ignorert `.env` etter ignore-/duplikatkontroll. Bare en kommentar og tomt felt er lagt til; tidligere auth-verdier er bevart, ingen verdier er vist og feltet aktiverer ikke nåværende app eller server.

Dokumentasjon/refleksjon er committet lokalt i **0ed527c44234b05b5484bec2c9762fe33910052f** (`docs(ai): record approved plan and prepare private API setup`). Specen er nå **1593 tokens**, `git diff --check` bestod. Ingen nye funksjonstester, nøkkelvalidering mot leverandøren, inferens, serverrestart eller kostnad er utført. Tidligere testresultater/godkjenninger og øvrige akseptanseporter er uendret. Ingen push.

### Åpne punkter
- Etabler API-tilgang med studentens private oppsett av prosjekt/nøkkel og eventuell fakturering. Nøkkelen legges i ignorert lokal `.env`, aldri chat. Bekreft deretter lokal konfigurasjon, billing og modelltilgang før implementering; draft/backlog består til denne forutsetningen er oppfylt. Modell/budsjett/data/grenser og selve planen er godkjent og skal ikke spørres om på nytt ved uendret omfang.
- Eksisterende representative PDF-/målplattform-, e-postlenke-/mal- og UX-/skjermleserporter består i issues.md. Ikke gjenta det vellykkede passordbyttet eller send nye e-poster/opprett kontoer automatisk.
