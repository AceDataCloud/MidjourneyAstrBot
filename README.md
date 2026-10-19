# Midjourney images for AstrBot

Generate one Midjourney image grid in an AstrBot conversation through your own Ace Data Cloud account. `midjourney_imagine` submits one job; `midjourney_get_task` queries the same task until the final grid is ready.

This independent **Midjourney integration is provided by Ace Data Cloud**; it is not an official plugin from the Midjourney publisher or the AstrBot team. Use your own Ace API key.

[简体中文指南](readme/README_zh_Hans.md) · [Imagine API](https://platform.acedata.cloud/documents/midjourney-imagine?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=midjourneyastrbot_readme_documents_midjourney_imagine) · [Tasks API](https://platform.acedata.cloud/documents/midjourney-tasks?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=midjourneyastrbot_readme_documents_midjourney_tasks) · [Current prices](https://platform.acedata.cloud/services/midjourney?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=midjourneyastrbot_readme_services_midjourney)

## 1. Find and install

Current upstream navigation is **Plugins → Plugins → Plugin Market / Installed**; older English versions may label the section Extensions. Search **Midjourney** and verify **Midjourney by Ace Data Cloud**, author **acedatacloud**, and the matching service icon.

**Publication status on 2026-10-19: not publicly listed in the official market.** The market search/install instructions above apply after publication. For the current preview, use the repository path below rather than waiting for a card that is not there.

Repository installation: **Plugins → Plugins → Installed → Install Plugin (+) → Install from URL**, with `https://github.com/AceDataCloud/MidjourneyAstrBot`. Source is already available. Confirm it is enabled and loaded. A repository/file installation is a separate path from official market installation.

**Access restriction:** the current Ace service catalog marks this service private/restricted. Installing the plugin does not grant service entitlement. Use an already entitled account or confirm eligibility first; do not send a paid trial request just to test access. This flag alone does not mean the service is retired.

## Configure your key

New account? Register and sign in first. If the Applications page has no General application yet, choose **Initialize General Application**, then continue with the key steps below.

In [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=midjourneyastrbot_readme_api_key), copy a generation API key from your General application or create a key that permits both `/midjourney/imagine` and `/midjourney/tasks`. Confirm your account has Midjourney access, then check the current price and balance before submitting. Paste the key into the plugin's **Ace Data Cloud generation API key with Midjourney access** setting. Do not add `Bearer ` or use a `platform-...` management token. AstrBot masks the field in WebUI but stores the original value in its data directory, which should be protected.

Select a chat model that supports tool calling. Allow both Midjourney tools in the conversation's profile and persona.

### Token screenshots: copy or create a dedicated key

[Register or sign in to Ace](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=midjourneyastrbot_readme_signup), then open **Applications → General application** and initialize it if absent. Use **1** to copy the selected key, or **2 Manage Keys → Create** for a dedicated key. If Allowed APIs is enabled, include `/midjourney/imagine` and `/midjourney/tasks`; check current entitlement, balance and prices before use.

![Copy an Ace key or open Manage Keys (redacted)](_assets/tutorial/get-api-key-en.png)

Use a name such as `AstrBot Midjourney` and set expiry/limits as needed. The screenshot’s `Dify tutorial` is an older example, not a required label.

![Create an optional dedicated API key (shared Ace page, not AstrBot)](_assets/tutorial/create-api-key-en.png)

Images were reused and checked on **2026-10-19**; original capture dates are unknown. Credentials, App ID and balance are redacted. This is the shared Ace Applications UI, not proof of AstrBot installation or a live service call. [Image sources and limits](_assets/tutorial/sources.json).

### Where to paste it in AstrBot

Open **Plugins → Plugins → Installed**, select the gear (**Plugin Configuration**) on **Midjourney by Ace Data Cloud**, paste the key into **Ace Data Cloud generation API key with Midjourney access** (stored field `api_key`), and save. Paste the key only, with no `Bearer ` prefix; never put it in model-provider settings or a chat prompt. UI masking does not encrypt the data-directory config. These are exact text steps; no fabricated settings image is used.

## Generate once, then query

Ask the bot:

> Use `midjourney_imagine` once to create a yellow paper boat on a cobalt blue background. Use version `8.1`. Show me the task ID.

The tool sends one asynchronous `POST /midjourney/imagine` request in fast mode, standard definition, and returns `status: submitted` with a task ID. That is not a finished grid. Keep the ID and ask:

> Use `midjourney_get_task` with the exact task ID `<task_id>`. Tell me its status and final grid image URL. Do not generate another image.

If pending, query the same ID later. Only `status: succeeded`, `success: true`, and a final HTTPS grid image URL indicate completion. The plugin never retries a paid submission automatically.

This first version supports the public version IDs `8.1`, `8`, `7`, `6.1`, `6`, and `5.2`. The default is `8.1` in fast mode without HD. Set the model with the `version` argument; inline flags that change model or billing (such as `--v`, `--q`, and `--sref`) are rejected. `split_images: true` also returns individual image URLs when the API provides them. Upscaling, variations, edits, blending, video, and other billing-impact controls are outside this first version. The current price depends on your selected version and options.

## Verify and troubleshoot

Match a returned trace ID in Ace Data Cloud usage when available. A finished task may include public `cost` amounts in Credits; confirm the live usage row before treating an estimate as a charge. Task lookup reads an existing job and does not submit another generation.

| Symptom | Check |
| --- | --- |
| Plugin fails to load | AstrBot version, **Failed to Load Plugins**, and **Data & Logs → Logs**. |
| Tools are missing | Plugin enabled, both tools allowed in the active profile and persona, chat model supports tool calling. |
| HTTP 401/403 | Key type, both allowed API paths, and account access. |
| Network error after submission | Inspect request history before generating again; a timeout may already have created a paid task. |
| Pending task | Query the same task ID later. |
| Failed task | Use the task or trace ID to inspect request history. |

The key goes only to `https://api.acedata.cloud`; redirects are rejected. The plugin exposes final image URLs and public cost fields to the model, without raw internal data. It uses Python's standard library and needs no runtime package installation.

## Validation and brand asset

On official AstrBot `v4.28.2`, an isolated editable installation registered both tools. ChatUI submitted one V8.1 fast standard-definition grid and queried the same task ID twice; the first lookup was pending and the second returned success, with no second generation. The final PNG returned HTTP 200, `image/png`, and decoded at 1024×1024. The exact generation trace matched one successful `/midjourney/imagine` usage row: 0.216 Credits original and deducted. See the [sanitized evidence](tests/e2e-results.json). Other versions and split output were validated structurally but not generated. This is a local editable installation; official Cloud review, market installation, and a first call from a market installation remain open.

`logo.png` is the unmodified 256×256 [current Midjourney service icon](https://cdn.acedata.cloud/wto43b.png), SHA-256 `6fe0ba60d32bd4f6da7ead89c0a3d8d318261ad08e02a619bd87a91d2218cb92`.
