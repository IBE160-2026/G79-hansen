# Local API setup for Story 2.5

The plan was approved and API readiness resolved on 15 November 2026. Private
generation is implemented, reviewed and verified offline. The four authorized
live smoke calls have already run; no further automated inference is authorized
by that allowance. Preserve the existing ignored local key and initialized
budget ledger; do not recreate/reset them. No account, project, purchase or
hosted configuration is created automatically.

## Current local operation

The application reads `OPENAI_API_KEY`, `MODEL_ENABLED=true` and
`MODEL_BUDGET_PATH` from the server process environment. It does not load `.env`
automatically. Load the existing ignored file explicitly when starting the
single-worker server, as documented in README; keep all existing auth settings.
Generation stays disabled without explicit model configuration and a valid
preinitialized ledger. Never print the key or place it in chat/browser code.

Use `uv run python -m scripts.model_budget status .model-budget.json` to inspect
content-free counters. Keep the ledger and any `.blocked` sidecar unchanged;
missing/corrupt/blocked/exhausted state fails closed, uncertain calls are never
refunded and restart does not restore allowance. The four-call smoke counter is
exhausted. See [generation acceptance](generation-acceptance.md) for the executed
checks and separate quality/platform gates.

## Historical initial owner setup steps

The following instructions record the initial setup sequence before readiness
was resolved. They are not a request to create another key/account, buy credits
or repeat the live checks now.


1. Sign in with your existing account at [OpenAI Platform](https://platform.openai.com/). Select a project dedicated to Study Buddy, or create one yourself through the project selector if needed. Keep the approved Global processing choice; do not change unrelated projects. [Official project instructions](https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform).
2. Inspect [API billing](https://platform.openai.com/settings/organization/billing/overview). If no usable credit exists, new prepaid accounts currently have a minimum USD 5 purchase, while the default suggested purchase is USD 10. Check the actual amount and taxes yourself, and turn **Use auto-reload off** before confirming any purchase; it is enabled by default during setup. Buying credits is separate from the approved USD 5 application usage ceiling. The assistant does not purchase/fund anything. [Official billing instructions](https://help.openai.com/en/articles/8264644-setting-up-and-managing-prepaid-api-billing).
3. In the selected Study Buddy project, open [API keys](https://platform.openai.com/api-keys) and choose **Create new secret key**. Name it `Study Buddy local`. Use a project key, not an organization administration key. If configuring Restricted permissions, allow Responses creation and model-access reads. Save the secret privately: the complete value is only shown when created. [Official key instructions](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key).
4. Open the existing ignored project-root `.env` in your local editor and paste the key after the prepared `OPENAI_API_KEY=` field. Keep every existing auth setting unchanged. Save; never paste the key in chat or send a screenshot of it. Tell the assistant that local key setup and billing are ready, without disclosing payment details.

That initial sequence was completed before implementation: billing was
student-reported, the local key authorized the expected model metadata read, and
four bounded synthetic inference checks subsequently ran. Any future change to
funding, model/data policy or allowed usage requires a separate decision.

## Current configuration boundary

An empty `OPENAI_API_KEY=` placeholder does not enable inference. The implemented
runtime also requires explicit model enablement and the existing budget path;
`POST /api/v1/generation`, the live adapter and durable ledger are now present.
The ledger, rather than provider credits or dashboard alerts, controls this
application's dispatch reservations. Other clients using the credential and
provider billing delays remain outside that boundary. Preserve earlier auth/PDF
acceptance limits and the historical measurements in the acceptance record.
