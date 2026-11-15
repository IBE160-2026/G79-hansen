# Kildebasert kvalitet – Story 2.6

## 2026-11-15 kl. 17:50 — Fredrik

### Oppgave
Studenten spurte om neste steg med 30 % igjen av femtimersgrensen og svarte «Start på det» etter anbefaling om en konkret kvalitetsplan for Story 2.6. Undersøk og legg frem planen før implementering og nye modellkall.

### Plan
- Les CLAUDE.md, issues, [Story 2.5-loggen](990-2026-11-15-11-53-48-ki-generering-modell-og-plan.md), Story 2.6, gyldig Epic 2-kontekst og ferdig implementering/evidens.
- Bruk ny BMAD-build og én kun-lesende kodekartlegging. Velg kilder og kontrollpunkter før generering; avklar bare valg som faktisk trenger studenten.
- Lag [draft-spec](../../.docs/implementation-artifacts/spec-2-6-evaluate-generated-content-against-known-sources.md) og [konkret korpus/rubrikk](../../.docs/implementation-artifacts/content-evaluation.md), med samlet plan-/livekostnadsvalg før neste fase.

### Resultat
Arbeidskopien var ren, baseline **dec0683dca9888aa04fcb0635d6e10421c7d71e6** på main. BMAD-build ble rendret én gang for den nye storyen; workflow/steg 1/steg 2/spec-mal ble lest. Cached Epic 2-kontekst er nyere enn samtlige planleggingsfiler; ferdig Story 2.5 ble lastet som kontinuitet. Eksakt sprintnøkkel er `2-6-evaluate-generated-content-against-known-sources`. Story 2.6 forblir backlog, ny spec draft/dispatch.

Én kun-lesende agent undersøkte komponentgjenbruk og eksisterende testgrenser etter steg 2s delegasjonsinstruks. Den endret ingen filer og kjørte ingen tester/modell-/nettverkskall. Hovedagenten undersøkte ekstraksjon, modelladapter, budsjett, smokeskript og PDF-evidens. Tidligere vanntekster og innholdsfrie observasjoner etablerer ikke tre dokumenters faktiske kildefasthet eller semantiske dekning.

Tre originale ufølsomme syntetiske kilder er forhåndsregistrert: fiktivt studiebibliotek (innlimt norsk/kort), Lumen-laboratorium (UTF-8-fil, engelsk/detaljert) og Varde-feltkurs (PDF, norsk/detaljert). Fem begreper med nødvendige fakta/plasseringer er definert per dokument, totalt femten før modellkall. PDF-en skal bygges etter godkjenning med lesbare sider 1/3/5 og blanke 2/4, gjengis og sammenlignes mot faktisk tekstuttrekk. Dagens kodede PDF-prober alene kan ikke brukes som bevis på synlige glyfer. Studenten trenger ikke finne eller laste opp materiale.

Planen krever semantisk gjennomlesning av alle genererte elementer og alle kildehenvisninger, minst 4/5 begreper dekket per dokument, og separat registrering av kildeudekkede påstander, feil referanser og utelatelser. Misvisende emnefelt og lesbar tegnsetting uten fakta er egne scenarier. Syntetisk output kan bevares som uttrykkelig avgrenset testevidens uten nøkkel, raw providerbody, brukerkilde, autoriserende identitet, signert bevis eller kvittering. En promptendring krever sluttresultater for alle fem scenarier; manglende kvote betyr uferdig akseptanse.

Forslaget som venter godkjenning er **opptil åtte nye evalueringsforsøk**, fem første scenarier og høyst tre eksplisitte omtester. Hvert forsøk bruker varig ny evalueringskvote og eksisterende global USD 0,05-reservasjon før utsending. Høyst **USD 0,40 ekstra reservasjon innen eksisterende USD 5**, uten nullstilling av gammel global ledger eller brukt firekallskvote. Hvis ingen andre kall kommer til, ville samlet reservasjon være høyst USD 0,60. Separat evalueringskvote opprettes én gang først etter godkjenning; ingen slik fil er laget nå. Offisielle [Luna-priser](https://developers.openai.com/api/docs/models/gpt-6-luna) ble kontrollert: USD 0,10/0,50 per million input/outputtokens. Åtte regneeksempler à 10 000/4 000 tokens gir USD 0,024 før avgifter, ikke målt faktisk forbruk. Alternativet er bare offline forberedelse med liveakseptanse fortsatt åpen.

Spesifikasjonen er **1527 tokens**, målt med midlertidig uv/tiktoken/o200k_base uten avhengighetsendring. Første tellekommando hadde en ekstra parentes og stoppet lokalt; korrigert kommando ga den oppgitte tellingen. `git diff --cached --check` bestod. Plan/korpus/refleksjonsgrunnlag er lagret lokalt i **66a40ff78507cc90d0875b2bfbe081fa55ccc0d9** (`docs(ai): plan source fidelity evaluation for story 2.6`). Ingen push. Ingen nye funksjonstester, kvalitetspasseringer eller livekall hevdes; tidligere 422 bestått/én skip og 28/33/11 nettleserscenarier er historisk baseline. Appkode, sprintstatus, .env, faktisk budsjett og normalserver er uendret. Ingen e-post/konto/passord/hosted-endring, kjøp eller deploy. Studentens egen refleksjon er ikke skrevet av KI.

### Åpne punkter
- Avklar/godkjenn konkret plan og eventuell ny åtteforsøksramme før implementering/live. Godkjennes bare offline forberedelse, står live kvalitet fortsatt uverifisert og Story 2.6 kan ikke ferdigmeldes.
- Gjennomfør de tre dokumentene/to negative scenariene og nødvendige rettelser/omtester etter godkjenning; bevar tidligere ledger, kvote, feilresultater og akseptanseporter. Representative PDF-/målplattform-, e-postlenke-/mal- og UX-/skjermleserporter i issues.md består.
