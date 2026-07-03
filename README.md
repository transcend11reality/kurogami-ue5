# Kurogami UE5

Unreal Engine 5 rebuild of the Kurogami world, starting with a single cinematic showpiece
environment delivered in-browser (pre-rendered video first, interactive Pixel Streaming later).
See `docs/UE5_SHOWPIECE_PLAN.md` for the full production plan.

---

## Read this first: what runs where

**GitHub Codespaces cannot run Unreal Engine.** Codespaces are headless Linux containers with
no GPU. The UE5 editor and Pixel Streaming both require a GPU (and a display). So this repo is
split by what each environment can actually do:

| Task | Where it runs |
|------|---------------|
| Edit C++ source, config, docs, web layer | Codespaces or local (no GPU needed) |
| Run the Pixel Streaming web + signalling layer | Codespaces or local (Node, see `web/`) |
| CI (lint, hygiene, web build) | GitHub Actions (no GPU) |
| Open/edit the UE editor, build lighting, author Blueprints | **GPU machine only** (your RTX workstation or a cloud GPU VM) |
| Cook/package the build | **GPU machine only** |
| Host the interactive stream | **GPU machine / cloud GPU** (or a managed Pixel Streaming provider) |

If you try to open the UE project in a Codespace it will not work. Use a GPU machine for the
engine, and Codespaces for everything around it.

---

## Prerequisites

- A **GPU machine** for the Unreal work: Windows + a recent NVIDIA RTX GPU (3080/4070 or better),
  32 to 64 GB RAM, fast NVMe, hundreds of GB free. Or a **cloud GPU VM** (AWS g5, Azure NV-series,
  GCP) if you do not have local hardware.
- **Unreal Engine 5.4 or 5.5** (via the Epic Games Launcher).
- **Git LFS** installed (UE content is large binary assets; this repo tracks them via LFS).
- **Node 20+** for the web layer (already provided in the Codespace devcontainer).

---

## Start here (step by step)

### 1. On your GPU machine: create the UE project into this repo
1. Clone this repo locally.
2. Install Git LFS once: `git lfs install`.
3. In the Epic Games Launcher, create a new UE 5.4/5.5 project (Blank, with Starter Content off).
   Create it INTO this repo folder so the generated files (`*.uproject`, `Config/`, `Source/`,
   `Content/`) live alongside the files already here. Name it `Kurogami`.
4. In the editor, enable the **Pixel Streaming** plugin (Edit > Plugins), then restart.
5. Merge the settings in `Config/DefaultEngine.ini.additions.txt` into your project's
   `Config/DefaultEngine.ini` (do not overwrite; append/merge the sections).
6. Confirm the project opens and Nanite/Lumen are on (they are UE5 defaults).

### 2. Commit and push
    git add .
    git commit -m "UE5 project + repo scaffold"
    git push
Large assets go through Git LFS automatically (see `.gitattributes`).

### 3. In Codespaces: work on the web + docs (no GPU needed)
- Open the repo in a Codespace.
- The devcontainer installs Node. Run the local player:
      cd web && npm start
  then open the forwarded port (8080). This serves `web/public/player.html`, the two-tier
  browser player: a pre-rendered cinematic video for everyone, plus a slot for the interactive
  Pixel Streaming stream when it is live.
- Edit docs and C++ source here freely; compile happens on the GPU machine.

### 4. Deliver the showpiece
- **Pre-rendered cinematic (do this first):** on the GPU machine, author a camera move in
  Sequencer and render with Movie Render Queue to a 4K MP4. Put the MP4 at
  `web/public/cinematic.mp4` (LFS) or on a CDN, and point `player.html` at it. This is a
  photoreal in-browser showpiece that runs everywhere and costs almost nothing to serve.
- **Interactive Pixel Streaming (later):** package the UE app on the GPU machine / cloud GPU,
  run Epic's Pixel Streaming signalling server (see `web/README.md`) or use a managed provider
  (Arcware, Vagon, Eagle 3D Streaming), and wire `player.html` to it. Remember: one GPU per
  concurrent interactive viewer, so gate access and autoscale to zero (see the plan, section 6).

---

## Boundaries (carry over from the whole project, unchanged)
- Scores/rewards stay cosmetic. No minting, tokens, real-money trading, or real-ownership
  representation anywhere in the experience.
- Educational content stays accurate and honest.
- Anything regulated stays gated pending counsel.
- Use only assets you have the right to use. Keep watches/jets/brands as original designs or
  clear homages under your own brand, never as trademarked reproductions. Photoreal makes
  passing-off easier to do by accident, so hold this line harder.

## Layout
    README.md                         this file
    .gitignore                        Unreal-aware ignores
    .gitattributes                    Git LFS for UE binary assets
    .devcontainer/                    Codespaces (Node) for the web layer
    .github/workflows/ci.yml          non-GPU CI (web build + hygiene)
    Config/DefaultEngine.ini.additions.txt   settings to merge into your UE project
    docs/UE5_SHOWPIECE_PLAN.md        the production plan
    web/                              Pixel Streaming web player + signalling notes (runs in Codespaces)
    (UE-generated on the GPU machine: Kurogami.uproject, Source/, Content/, Config/ ...)
