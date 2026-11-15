# Story 2.5 model decision and implementation status

**Current status, 15 November 2026:** the plan is approved, API readiness is
resolved and private generation is implemented, reviewed and verified offline.
The four approved synthetic live smoke calls have been executed; no further
automated inference is authorized by that allowance. The existing local ledger
must retain its counters/reservations. See [generation acceptance](generation-acceptance.md)
for actual measurements and the separate quality/platform gates.

## Historical proposal and approval record

The original comparison, initial missing-key observations and approval/readiness
updates below describe their respective points in the planning timeline. They
are preserved as decision evidence, not current setup instructions.

Checked on 15 November 2026. No inference request, key validation, account creation, purchase or hosted change was performed. The recommendation below is an engineering inference from official specifications, not a measured Study Buddy quality result.

**Approval update, 15 November:** The student accepted the plan and recommendations, then clarified “Trenger hjelp med oppsett”. Model, cost, data and bounds choices are now approved as recorded in the spec. API readiness remains outstanding; no new plan approval is required for this unchanged scope. The original comparison below is preserved as decision evidence.

**Readiness resolved, 15 November 12:14:** The student reports billing ready; the saved local key authorized GET `/v1/models/gpt-6-luna`, HTTP 200 and exact expected ID. No inference, secret output or billing mutation occurred. Local presence and model metadata access are verified; billing/credit availability remains student-reported until bounded live checks. Official Luna prices and explicit cache-mode behavior were rechecked unchanged. Continue the approved implementation; no repeat approval.

## Historical repository and integration evidence before implementation

The clean starting revision is `5737bbf45902f3621fc90ecb8ab62e09eecbf100`, following Story 2.4 code revision `c5b207ff8523c9b62668043f2ea69466e9e39ac7`. Cached Epic 2 context is newer than all planning artifacts. Source extraction is implemented; model adapters, workspace authority and save receipts are absent. `httpx` 0.28.1 is already locked transitively; declare it directly when implementing the HTTP adapter. No provider SDK needs to be introduced.

Available connected capabilities include existing Supabase and Sites tools, but no inference connector or app model credential. Existing Supabase access is already established and needs no reconnection. Chat tools cannot be treated as runtime credentials for the application. Only presence checks were performed for conventional OpenAI/Anthropic/Gemini key names in the ignored local `.env` and current process: none found. This says nothing about keys/accounts held elsewhere. No `.env` value was emitted or changed.

## Three suitable candidates

Standard direct-API text prices in USD per million tokens; no cache discounts, tools, Batch or priority processing assumed.

| Model | Input / output | Structure and technical limits | Quality and fit assessment |
| --- | --- | --- | --- |
| OpenAI GPT-6 Luna (`gpt-6-luna`) | $0.10 / $0.50 | Structured Outputs; 1,050,000 total context, 922,000 maximum input, 128,000 maximum output; reasoning can be `none` | Provider positions it for focused high-volume tasks. Best initial cost fit for one bounded source-to-schema transformation; Study Buddy grounding and Norwegian prose remain unmeasured. |
| Google Gemini 3.8 Flash (`gemini-3.8-flash`) | $0.75 / $3.75 through 31 December 2026; $1.50 / $7.50 from 1 January 2027 | Structured outputs; 1,048,576 input and 65,536 output; reasoning supports low/medium/high, not minimal | Provider positions it for complex enterprise/agent tasks. Credible alternative, but neither those claims nor multimodal breadth establish better study output. Thinking also consumes the paid output budget. |
| Anthropic Claude Sonnet 5.5 (`claude-sonnet-5-5`) | $2 / $10 | Structured JSON outputs; 1M context and 128K output; adaptive thinking and model-specific parameter restrictions | Provider describes content creation and a speed/intelligence balance. Useful quality challenger if evaluations fail, but no measured benefit here justifies its higher cost yet. |

Sources: [OpenAI model specification](https://developers.openai.com/api/docs/models/gpt-6-luna), [Google model specification](https://aistudio.google.com/docs/models/gemini-3.8-flash), [Google pricing](https://aistudio.google.com/docs/pricing#gemini-3.8-flash), [Anthropic specification](https://platform.claude.com/docs/en/models/sonnet-5-5/overview), [Anthropic structured output](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).

All exceed the application's source/output needs. Actual rate limits and access are project-specific and have not been verified. Luna requests above 272K input tokens have higher rates; the proposed local bound stays below that threshold. Native structured responses enforce supported schema structure, not factual truth or correct citation meaning. Refusal, incomplete output, semantic errors and unknown references still require whole-response rejection. See [OpenAI structured output guidance](https://developers.openai.com/api/docs/guides/structured-outputs).

## Data handling comparison

| Provider | Official default API handling | Consequence for this proposal |
| --- | --- | --- |
| OpenAI | No training unless opted in; abuse-monitoring content normally retained up to 30 days, with documented exceptions. Responses persist by default unless storage is disabled. ZDR requires approval. | Use `store:false`, foreground requests and no feedback/data-sharing opt-in. Global endpoint does not establish EU-only processing. |
| Google | Paid API prompts/responses are not used to improve products; safety logging lasts a limited period and processing/caching can occur wherever Google or agents operate. EEA terms extend paid data-use protections to unpaid services, while making API clients available in the EEA requires Paid Services. | Compare paid service for this Norwegian app; do not claim every free-tier request trains models. Neither paid status nor a European user proves EU-only processing or zero retention. |
| Anthropic | Commercial inputs/outputs are not used for training by default. API content is normally deleted within 30 days; policy/legal, feedback, agreed retention and other documented exceptions apply. | Ordinary API access is not a ZDR agreement or a location guarantee. Avoid Files API/feedback and verify project terms if selected. |

Sources: [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data), [Google API terms](https://aistudio.google.com/docs/terms), [Anthropic training policy](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training), [Anthropic retention](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data).

For Luna, propose `prompt_cache_options.mode:"explicit"` with **no breakpoints**: current documentation says this creates no prompt-cache writes. Do not substitute a short TTL or `store:false` for disabling caching. Without this control, provider KV cache retention can reach 24 hours. Validate this parameter locally and during the authorized smoke check; unsupported configuration fails closed. See [prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching).

Proposed permission covers nonsensitive, self-authored/public or otherwise permitted material. Send extracted text, compact unit keys and selected settings only; no original PDF/file, filename, email, account/session identifiers or receipt. App source/results remain transient until explicit Save in Epic 3; provider security retention is a separate boundary. If EU-only processing or ZDR is required, resolve eligibility/project configuration before integration; it cannot be inferred from the existing Free/Paris authentication project. [Regional processing documentation](https://developers.openai.com/api/docs/guides/data-residency).

## Recommendation and understandable cost

Start with **GPT-6 Luna, Standard processing, reasoning `none`**. Its low price, strict structure and controllable cache behavior suit the bounded task. Keep provider selection explicit: no automatic model upgrades or fallback. A failed quality evaluation triggers a new decision, not silent switching. Stable model ID and reported model identity are recorded as metadata; there is no dated Luna snapshot listed in the checked model reference.

These are estimates, not measured token counts or exchange-rate claims. A token is a model text unit; 30,000 characters do not imply a fixed token count. Prompt/schema and reference markup count too.

| Example including instructions/schema | GPT-6 Luna | Gemini 3.8 Flash, current price | Claude Sonnet 5.5 |
| --- | ---: | ---: | ---: |
| 10,000 input + 4,000 output tokens | $0.003 | $0.0225 | $0.060 |
| 20,000 input + 8,000 output tokens | $0.006 | $0.045 | $0.120 |
| 1,000 of the first example | $3 | $22.50 | $60 |

Calculation: `(input tokens × input price + output tokens × output price) / 1,000,000`. Google reasoning tokens are included in output in this example; hidden reasoning beyond it would raise cost. Taxes, currency conversion, purchases/minimum funding and unrelated project usage are excluded. No credits are assumed available or purchased.

**Proposed ceiling:** USD 5 total local testing/usage, not a monthly renewal. Before each dispatch persist a conservative USD 0.05 reservation; never refund an uncertain call or reset reservations on restart. This deliberately allows at most 100 attempts, even if the actual bill is far lower. Proposed maximum automated live verification is four self-authored synthetic calls; their combined reservation is $0.20. Story 2.6's larger evaluation is a later explicit step within any remaining approved allowance.

The proposed 256 KiB serialized provider-request bound plus a conservative 4,096-token protocol allowance gives at most 266,240 input tokens using UTF-8 byte count as the text-token upper bound, below the 272K price threshold. At the checked standard rates with 8,000 output tokens that is approximately $0.030624 before tax; the $0.05 reservation provides margin. Use compact source-unit keys, no tools, no cache writes and no hidden retry. Verify the bound against actual provider usage before wider use; unexpectedly higher usage disables further dispatch pending investigation. Documented prices must be rechecked before live activation and revised ceilings need renewed approval if they exceed the approved allowance.

An app ledger controls this app's dispatches, not another client's use of the same key/project or provider price changes. Use an appropriately isolated existing API credential; never claim a dashboard alert is a hard cap. The application refuses activation without a preinitialized budget ledger and agreed configuration. Missing/corrupt/exhausted state fails closed. No dashboard or funding changes are part of this proposal.

## Current approved configuration

The [implementation spec](spec-2-5-generate-all-learning-parts-from-the-source.md#readiness-gate)
records the resolved readiness gate and existing approval. The
[setup guide](model-setup-2-5.md) describes loading the existing ignored local
configuration and preserving the initialized ledger. No new approval, account,
funding or hosted change is implied. Prior auth/PDF approvals and historical test
evidence remain separate. General content fidelity evaluation belongs to Story 2.6.
