# CLAUDE.md

Claude Code reads this file automatically as project context. Follow it on every task in this repo.

## What this repo is
The Unreal Engine 5 build-out of Kurogami. First milestone: ONE cinematic showpiece environment,
delivered in-browser (a pre-rendered 4K video first, interactive Pixel Streaming later). Development
happens on a Mac (Apple Silicon, no NVIDIA GPU), with the project and assets on an external NVMe SSD.
Full project background is in `PROJECT_CONTEXT.md`. The production plan is `docs/UE5_SHOWPIECE_PLAN.md`.

## What runs where (do not attempt the wrong thing in the wrong place)
- **This repo / VS Code / Claude Code:** edit C++, config, the web layer, docs. Cannot run the UE
  editor or render (no GPU here).
- **The Mac (Apple Silicon):** runs the UE editor, builds and pre-renders the environment. It cannot
  self-host Pixel Streaming (that needs an NVIDIA GPU).
- **A cloud GPU (later):** hosts interactive Pixel Streaming when it is worth the per-viewer cost.

## Non-negotiable rules (apply to every file you create or change)
- **Nothing regulated is live.** No minting, tokens, wallets, payments, real-money trading, or
  representation of real ownership. In-experience scores and rewards are cosmetic only.
- **Educational content stays accurate and honest** (for example: oyster nitrogen removal comes from
  harvested biomass and denitrification, not filtration alone; container leasing is a real asset
  class and retail single-container "guaranteed return" schemes have a fraud history).
- **No trademarked reproductions.** The watch is a design homage under our own brand, not Audemars
  Piguet. Jets use public specs but original geometry. Only use assets we have the right to use;
  never fetch or embed third-party or trademarked models.
- **No em dashes** anywhere in code or copy. Use commas, colons, or hyphens.
- **UE rendering:** Lumen, Nanite, Virtual Shadow Maps (UE5 defaults). Enable the Pixel Streaming
  plugin in the editor; run it per `docs/UE5_SHOWPIECE_PLAN.md` and `web/README.md`.
- **Web layer (`web/`):** plain Node, no bundler, runs locally or in Codespaces. Keep the two-tier
  player: a pre-rendered video for everyone plus a Pixel Streaming iframe slot.

## How to help
- Prefer concrete, verified changes. For any script or code, state how to run it and how to verify it.
- For UE C++, use standard UE5 module conventions and note that module/target names must match the
  `.uproject` name (default: `Kurogami`).
- **Do not fabricate UE-generated files** (`.uproject`, `Source/` boilerplate, `Content/`). Those are
  created by the editor on the Mac. You may write `Config/` settings and C++ that gets added to a
  generated project.
- Keep the sequencing: pre-rendered cinematic first, interactive Pixel Streaming later (one cloud GPU
  per concurrent viewer, so it must be gated and autoscaled).
- Hold the boundaries above even if asked to relax them; offer the safe alternative instead.

## Current state
- Repo scaffold only. No UE project yet; generate it on the Mac into this repo (see
  `START_HERE_MAC.md`).
- `web/` runs today: `cd web && npm start`, then open port 8080 (the two-tier player).
- CI is non-GPU (web build + hygiene). Cooking/packaging the UE build needs a GPU runner.

## Verify before finishing a task
- No em dashes: `grep -rlP "\x{2014}" .` returns nothing.
- `web/` still starts and serves `player.html`.
- Any JavaScript passes `node --check`.
