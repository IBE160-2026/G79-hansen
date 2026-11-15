# Local API setup for Story 2.5

Plan/recommendations approved on 15 November 2026. The student needs setup help. API access is not yet established; Story 2.5 remains draft/backlog. No account, project, purchase or hosted configuration is created automatically.

## Private owner steps

1. Sign in with your existing account at [OpenAI Platform](https://platform.openai.com/). Select a project dedicated to Study Buddy, or create one yourself through the project selector if needed. Keep the approved Global processing choice; do not change unrelated projects. [Official project instructions](https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform).
2. Inspect [API billing](https://platform.openai.com/settings/organization/billing/overview). If no usable credit exists, new prepaid accounts currently have a minimum USD 5 purchase, while the default suggested purchase is USD 10. Check the actual amount and taxes yourself, and turn **Use auto-reload off** before confirming any purchase; it is enabled by default during setup. Buying credits is separate from the approved USD 5 application usage ceiling. The assistant does not purchase/fund anything. [Official billing instructions](https://help.openai.com/en/articles/8264644-setting-up-and-managing-prepaid-api-billing).
3. In the selected Study Buddy project, open [API keys](https://platform.openai.com/api-keys) and choose **Create new secret key**. Name it `Study Buddy local`. Use a project key, not an organization administration key. If configuring Restricted permissions, allow Responses creation and model-access reads. Save the secret privately: the complete value is only shown when created. [Official key instructions](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key).
4. Open the existing ignored project-root `.env` in your local editor and paste the key after the prepared `OPENAI_API_KEY=` field. Keep every existing auth setting unchanged. Save; never paste the key in chat or send a screenshot of it. Tell the assistant that local key setup and billing are ready, without disclosing payment details.

The assistant can then check presence/ignore status without displaying credentials and establish the remaining access prerequisite. No manual server restart, SDK installation or test request is needed now; implementation, budget initialization and bounded verification follow the approved build sequence. Any request to fund more, change model/data policy or expand usage requires a new decision.

## What the local file change means

An empty `OPENAI_API_KEY=` placeholder is configuration preparation only. It neither enables inference nor changes the running server. The current application does not yet read this field. There is no generation endpoint, live adapter or budget ledger yet. Those are implementation tasks after readiness is established.

The planned local ledger, rather than the provider's credit balance or a dashboard alert, will enforce application dispatch reservations. Prepaid cutoff can be delayed; credits alone are not an instantaneous spending cap. Actual usage, model access and rate limits remain unverified until separately checked. Preserve all earlier auth/PDF acceptance limits.
