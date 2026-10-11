# Midjourney images for AstrBot

Generate one Midjourney image grid in an AstrBot conversation through your own Ace Data Cloud account. `midjourney_imagine` submits one job; `midjourney_get_task` queries the same task until the final grid is ready.

[简体中文指南](readme/README_zh_Hans.md) · [Imagine API](https://platform.acedata.cloud/documents/midjourney-imagine) · [Tasks API](https://platform.acedata.cloud/documents/midjourney-tasks) · [Current prices](https://platform.acedata.cloud/services/midjourney)

## Find and install

In AstrBot WebUI, open **Extensions → Plugins → AstrBot Plugin Market** and search **Midjourney**. Confirm the card says **Midjourney by Ace Data Cloud**, the author is **acedatacloud**, and the logo matches the [current service icon](https://cdn.acedata.cloud/wto43b.png). Install it, then check **Installed** for load errors.

The official AstrBot Cloud listing is pending. After the source release is merged, **Installed → Install (+) → Install from URL** with `https://github.com/AceDataCloud/MidjourneyAstrBot` can preview it. A URL installation does not prove market publication.

## Configure your key

In [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications), copy a generation API key from your General application or create a key that permits both `/midjourney/imagine` and `/midjourney/tasks`. Confirm your account has Midjourney access, then check the current price and balance before submitting. Paste the key into the plugin's **Ace Data Cloud generation API key with Midjourney access** setting. Do not add `Bearer ` or use a `platform-...` management token. AstrBot masks the field in WebUI but stores the original value in its data directory, which should be protected.

Select a chat model that supports tool calling. Allow both Midjourney tools in the conversation's profile and persona.

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
