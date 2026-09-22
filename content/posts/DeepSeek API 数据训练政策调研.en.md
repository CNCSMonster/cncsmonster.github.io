+++
title = "Does DeepSeek Train on API Data? A Policy Investigation"
date = 2026-05-19T00:00:00+08:00
slug = "deepseek-api-data-training-policy"
[taxonomies]
    tags = ["DeepSeek", "API", "Privacy", "Data Training", "Research", "数据训练", "隐私", "调研"]
+++

> **Updated 2026-09-22**: rewritten. The original conclusion (keep sensitive data off the API) held up, but the reasoning had a gap — it read only the Open Platform Service Agreement and missed the training grant in the parent agreement. The three policy versions are byte-for-byte the same versions I checked in May, so the terms didn't change; the reading did. Quotes below are translated from the zh-CN originals (the controlling text for mainland accounts); all re-fetched on 2026-09-22.

---

## The Question

I call the DeepSeek API. Do my prompts and completions get used to train their models?

## The Answer

**"The Open Platform agreement says nothing about training" is true — but "won't train" does not follow from it.**

DeepSeek's data rules are **three agreements stacked on top of each other**. The training grant sits in clause 4.3 of the parent User Agreement, and clause 1.1 of that same agreement explicitly counts the API as a "Service". The real state of affairs for API traffic is **undisclosed**: DeepSeek neither commits to not training on API inputs/outputs, nor states whether it collects or retains them at all.

| What I use | What the terms say | Can I opt out? |
|-----------|-------------------|:--------------:|
| Web/App chat | ✅ Explicitly says inputs/outputs may be used for training (de-identified) | ✅ Turn off "数据用于优化体验" (Data used to optimize experience) |
| Open Platform API | ⚠️ Child agreement has no training clause, but parent clause 4.3 is not displaced; Privacy Policy never lists prompt content as collected | ❌ No toggle in the Open Platform console |

## The key point: the three agreements stack, they don't replace each other

**Open Platform Service Agreement** (updated 2026-04-22, effective 2026-04-29), opening paragraph:

> *"[It], **as a specific agreement referred to under, and a constituent part of, the DeepSeek User Agreement**, applies in particular to you, as an individual or enterprise developer, using the **application programming interface (API)** or other developer tools provided by this platform…"*

**DeepSeek User Agreement** (updated/effective 2025-09-05), preamble:

> *"When you use a particular feature of the Service, there may be a separate agreement for that feature… **Where this Agreement conflicts with a specific agreement, the specific agreement prevails. All of the foregoing terms and rules form an inseparable part of this Agreement.**"*

**→ A child agreement overrides the parent only where they conflict on the same point. Silence is not a conflict, so clause 4.3's training grant is not carved out for API traffic.** Judging what happens to API data from one document is not enough.

Division of labour across the three:

| Document | Version | What it says about training |
|----------|---------|----------------------------|
| User Agreement 1.1 + 4.3 | 2025-09-05 | 1.1 defines "Service" to include the API; 4.3 **grants** use of "inputs and corresponding outputs collected by the Service" for model training and service optimisation, plus a free non-exclusive licence |
| Open Platform Service Agreement | effective 2026-04-29 | **No** training grant; 4.2 keeps input rights with you and assigns outputs to you; 5.5 **routes** personal-information processing to the Privacy Policy |
| Privacy Policy | 2026-02-10 | Preamble scope **expressly includes the API**; §I.2 (chat) carries the training clause; §I.3 (Open Platform) lists only real-name identity, e-mail and payment records — **no prompt content** |

## Evidence

### 1: The parent agreement says training happens, and its service definition includes the API

**Source:** [DeepSeek User Agreement](https://cdn.deepseek.com/policies/zh-CN/deepseek-terms-of-use.html), clauses 1.1 and 4.3 (fetched 2026-09-22, version 2025-09-05)

> 1.1 *"Our products and services include … software development kits (SDKs) and **application programming interfaces (APIs)** for use by third-party websites and applications…"*
>
> 4.3 *"To provide you with a continuous, high-quality service, **on the premise of secure encryption processing and strict de-identification that cannot re-identify a specific individual, we may use the inputs and corresponding outputs collected by the Service for model training and service optimisation. On that premise, you grant DeepSeek a royalty-free, non-exclusive licence**… If you refuse to have your data used for model training, you may opt out in-product by turning off 'Data used to optimize experience'."*

### 2: The child agreement has no training grant — but it points personal-data handling at the Privacy Policy

**Source:** [Open Platform Service Agreement](https://cdn.deepseek.com/policies/zh-CN/deepseek-open-platform-terms-of-service.html) (fetched 2026-09-22, effective 2026-04-29)

- No training authorisation anywhere in the text (the "training other models, e.g. distillation" wording in 4.2 is a right **granted to you**, not to DeepSeek)
- 4.2 *"You retain any rights, title and interest you hold in the inputs you submit… We assign to you any rights, title and interest in the content of the outputs of this Service."*
- 5.5 *"We will collect and process personal information generated and provided by you, as a personal-information subject, when using the Open Platform services **in accordance with the DeepSeek Privacy Policy**."*
- **No** data-retention period, deletion mechanism, or logging terms

### 3: The Privacy Policy covers the API, but never mentions API prompt content

**Source:** [DeepSeek Privacy Policy](https://cdn.deepseek.com/policies/zh-CN/deepseek-privacy-policy.html) (fetched 2026-09-22, version 2026-02-10)

> Preamble *"Unless otherwise stated, this Privacy Policy applies to the DeepSeek web pages, applications, mini-programs, software development kits (SDKs) and **application programming interfaces (APIs)** for use by third-party websites and applications…"*
>
> §I.2 Chat *"On the premise of secure encryption processing and de-identification, we may use the inputs and corresponding outputs collected by the service for training the DeepSeek model and optimising the service."*
>
> §I.3 Open Platform: the collection list is only real-name identity data, bound e-mail address, and payment order/transaction records — closing with *"The collection and processing of the above personal information applies only to the DeepSeek Open Platform."*

**→ This is where the actual gap is.** DeepSeek neither discloses that it collects API prompt/completion content, nor that it doesn't. Inference requires the full prompt to reach the server; receiving is not the same as retaining, and the terms never say how long anything is retained. **"Not listed in the collection inventory" is a disclosure gap, not a guarantee that the data goes unused.**

### 4: Retention has only a statutory floor; the API docs site carries no privacy statement at all

- Privacy Policy §V.2: *"Comply with laws and regulations on information retention (e.g. the Cybersecurity Law requires… **network logs retained for no less than six months**)"*; after account deletion or data removal, *"we will delete or anonymise your personal information"*
- [api-docs.deepseek.com](https://api-docs.deepseek.com/zh-cn/): checked 2026-09-22 — the site contains **no** statement about data retention, logging, whether prompts/completions are stored, or training use
- The opt-out toggle "Data used to optimize experience" is documented (Privacy Policy §VI.2.1) at an App/Web path: avatar → Settings → Data management. There is no equivalent in the Open Platform console, and it is not stated whether an API-only account can exercise it

### 5: Cross-vendor comparison — an affirmative commitment is achievable, and DeepSeek hasn't made one

| Provider | Does the paid API **affirmatively commit** to no training? | Wording | Source |
|----------|:---:|---|------|
| OpenAI | ✅ | *"As of March 1, 2023, data sent to the OpenAI API is not used to train or improve OpenAI models (unless you explicitly opt in)."* Abuse-monitoring logs default to 30 days | [your-data](https://developers.openai.com/api/docs/guides/your-data) |
| Anthropic | ✅ | *"By default, we will not use your inputs or outputs from our commercial products (e.g. Claude for Work, **Anthropic API** …) to train our models."* | [privacy.claude.com](https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training) |
| Google Cloud Gemini | ✅ | *"Gemini doesn't use your prompts or its responses as data to train its models."* | [data-governance](https://docs.cloud.google.com/gemini/docs/discover/data-governance) |
| **DeepSeek** | ❌ No commitment, and the parent agreement keeps the grant | See evidence 1–3 | [Open Platform Service Agreement](https://cdn.deepseek.com/policies/zh-CN/deepseek-open-platform-terms-of-service.html) |

**→ The difference isn't just "DeepSeek wrote nothing while others wrote something": others wrote "we won't", DeepSeek's parent agreement wrote "we may".**

## What should I do

1. **Keep sensitive data off the DeepSeek API** — personal data of your users, trade secrets, plaintext proprietary code. Not because it certainly trains on you, but because it never promised it wouldn't and the parent agreement reserves the right
2. **Don't treat "the terms don't say so" as a green light** — that mistakes textual silence for a behavioural guarantee, and it only holds after you have checked whether a higher-level agreement does say so
3. **Switch providers if you need an affirmative commitment** — the three above give quotable, auditable text
4. **Local deployment is the only certainty** — DeepSeek releases model weights under the MIT License; local inference removes this entire chain of questions
5. **Re-check periodically** — reread all three agreements quarterly, watching for a new data clause in the Open Platform agreement or prompt content finally appearing in Privacy Policy §I.3. Contacts: <privacy@deepseek.com> / <api-service@deepseek.com>

## Currency

On 2026-09-22 I re-fetched all three agreements: the version numbers are **identical** to the original survey point (2026-05-19) — User Agreement 2025-09-05, Privacy Policy 2026-02-10, Open Platform Service Agreement effective 2026-04-29. Terms change without notice; these conclusions reflect the text as of that date.
