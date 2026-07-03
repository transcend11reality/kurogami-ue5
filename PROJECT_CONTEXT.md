# Kurogami - Full Project Context (VS Code Handoff)

Drop this at the root of your working folder. It is the single source of truth for what this
project is, what has been built, the rules it follows, and how to continue in VS Code. It is
written so that you (or a fresh AI assistant with no memory of prior chats) can pick it up cold.

---

## 1. What Kurogami is

Kurogami is a dark, elite "Order of Shadows" themed venture around real-world-asset (RWA)
concepts (jets, watches, environmental credits, shipping/logistics), presented as an
interconnected set of browser 3D worlds plus a platform UI. Everything shipped so far is a
**demo / sandbox**: the data is illustrative and anything regulated (tokenization, staking,
real-money trading, real ownership) is intentionally NOT live.

There are two parallel codebases:
1. **The web build (shipped, working):** self-contained single-file HTML + Three.js worlds that
   run by drag-and-drop or static hosting.
2. **The module build (in progress):** the same worlds being rebuilt as a proper ES-module
   Three.js project so it can grow (this is the VS Code project going forward).

A separate track scopes an **Unreal Engine 5** version for photoreal quality (planning only).

---

## 2. Non-negotiable rules (apply to every file, every change)

These are the boundaries the whole project has been built to respect. Keep them.

- **Nothing regulated is live.** No minting, tokens, wallets, payments, real-money trading, or
  representation of real ownership anywhere in any experience. In-game scores/rewards are
  **cosmetic only** (points, in-session inventory, quest flags).
- **Honesty in educational content.** NPCs that teach real topics (the oyster-farm Scientist on
  nitrogen removal, the port Analyst on container leasing) must stay accurate, including the
  Analyst's warning about container-investment fraud. A prettier engine or new feature does not
  change the facts.
- **No trademarked reproductions.** The watch is a design homage to the Royal Oak **under our own
  brand**, not Audemars Piguet. Jets reference public specs but are original geometry. Do not
  fetch, embed, or ship third-party/trademarked 3D models. Only use assets you have the right to.
- **No em dashes** anywhere in code or copy. Use commas, colons, or hyphens.
- **Three.js constraints (web build):** single-file worlds load Three.js r128 from cdnjs; the
  module build uses r169 via import map. Never use `CapsuleGeometry` (r142+) or
  `OrbitControls` in r128; never use `localStorage`/`sessionStorage` in the browser builds.
- **Verify before shipping:** syntax-check JS, keep graceful WebGL/offline fallbacks, and (for the
  single-file site) rebuild the one deploy bundle after any change.

---

## 3. The web build (single-file worlds) - what exists

All of these are standalone HTML files that run over http (or file:// for the r128 ones):

- `index.html` - landing page ("Order of Shadows").
- `app.html` - the platform SPA: dashboard, Forge Index, Invest, Collateral, Markets,
  Tsukurukami codex, NEXUS ("explain and explore" educational console, deliberately NOT an
  advice engine), Account. Uses live crypto (CoinGecko) and RWA (DefiLlama) data read-only.
- `world.html` (source: `kurogami-tsukurukami.html`) - the walkable Three.js 3D world. This is the
  centerpiece. Eight regions with a hub, fast-travel map (M), deep-links (`#region`), NPCs with
  branching dialogue, quest chains, avatar tiers (T), and a trailing third-person camera.
  Regions: Olympus (hub), Jet Charter House, Space/Sophia Nexus (Brickell HQ), Tokyo Forge Hall,
  Longevity Sanctum, London Veil, **Chesapeake Oyster Farm**, **Port of Singapore**.
- `brickell-city.html` - stylized, walk-and-drive GTA-style slice of Brickell, Miami, grounded in
  real landmark coordinates. Procedural glass/concrete/brick facades with setbacks, real sun
  shadows, sky-reflecting glass, traffic lights, parked cars, pedestrians, day sky.
- `stores.html` (source: `kurogami-stores.html`) - two walkable showrooms: a watch boutique built
  like the inside of a giant Royal Oak (octagonal bezel, hex screws, tapisserie floor, sweeping
  hands, sapphire dome, display cases) and a jet showroom you walk aboard a Global 6000. Switch
  via tabs or `#watch` / `#jet`.
- `empty-leg.html` (source: `empty-leg-optimizer.html`) - a synthetic empty-leg flight optimizer.
- `current.html` (source: `living-current-app.html`) - the "Living Current" / NEXUS neuromorphic
  visualization SPA.
- `guide.html`, `neuron.html`, `order.html`, `portal.html` - concept/prospect pages.
- `prototypes/` - older concept pages (brand kit, catalog, deal, engine, floor, game, platform,
  prediction market, watch vault).
- `docs/` - PRDs, messaging kit, data-integration notes, and a Genesis mint config (metadata,
  guards, config) that is a **gated** artifact, not a live mint.

Two of the eight world regions are the "RWA game" pattern (fun loop + honest education +
cosmetic score), and they are the template for any future region:
- **Chesapeake Oyster Farm** (`#chesapeake`): grow oyster cages grey->gold, harvest ripe ones for
  a cosmetic "Shadow Credits" score, pollution mist clears to purification. The Scientist teaches
  that the nitrogen credit comes from harvested biomass + denitrification, not filtration alone.
- **Port of Singapore** (`#port`): pack/seal containers, ship the ready ones for a cosmetic
  "Manifest / TEU" score, congestion haze clears. The Analyst teaches container leasing as a real
  asset class, explains TEU, and honestly warns about retail container-investment fraud.

### Deploy bundle
`kurogami-site.zip` is the drag-to-Vercel bundle (root `index.html`, all the worlds, `prototypes/`,
`docs/`). It is rebuilt after any world change. `kurogami-vercel.zip` is a combined repo that also
nests the module build under `/app3d/` for a single GitHub->Vercel deploy.

---

## 4. The module build (this is the VS Code project going forward)

`kurogami-3d.zip` is the scaffold; `kurogami-3d-ported-verified.zip` is the version with two worlds
ported in and verified. Use the ported one as your working base.

**Structure:**
    kurogami-3d/
      index.html            import map (Three.js r169 from CDN), HUD, canvas
      css/style.css
      data/
        dialogue.json        NPC dialogue trees (cosmetic rewards only)
        quests.json          quest chains
      js/
        engine.js            renderer, scene, IBL environment, lights, loop
        controls.js          third-person controller (trailing camera, collision)
        vehicle.js           arcade driving mode (for Brickell)
        assets.js            GLTF + Draco loader with procedural fallback
        interact.js          proximity interaction + prompts
        dialogue.js          branching dialogue (cosmetic only; ignores any mint field)
        quests.js            quest chains + HUD
        main.js              entry point / tiny world router (#brickell vs boutiques)
        worlds/
          boutiques.js       watch + jet showrooms (full detail, GLTF-with-fallback)
          brickell.js        stylized Brickell city (walk + drive)
      assets/models/         drop licensed .glb here (currently only a README)

**How it runs:** it must be **served over http** (ES modules + fetch do not work from file://):
    cd kurogami-3d
    python3 -m http.server 8000     # then open http://localhost:8000
    # /#brickell , /#jet , /#watch select world/area

**Model ingestion status:** the watch and jet call `assets.load('assets/models/<file>.glb',
fallback)`. No `.glb` files exist yet, so they render **procedural fallbacks**. Drop licensed
`royal_oak.glb` / `global_6000.glb` (original or licensed, not trademarked reproductions) into
`assets/models/` and they load automatically. The loader only fetches the Draco decoder from a CDN,
nothing else external.

**Module build rules:** r169 APIs (`THREE.SRGBColorSpace`, `renderer.outputColorSpace`, not the old
`outputEncoding`/`sRGBEncoding`), no Capsule/localStorage, no em dashes, cosmetic rewards only.

`kurogami-port-kit.zip` contains this scaffold plus the original single-file source worlds plus
context-free PRDs (`PORT_STORES_PRD.md`, `PORT_BRICKELL_PRD.md`, `START_HERE.md`) describing how to
port the remaining single-file worlds into modules. Use these to port the other six regions
(Olympus, Jet, Space, Tokyo, Longevity, London, Chesapeake, Port) one at a time.

---

## 5. The Unreal Engine 5 track (planning + repo scaffold only)

Decisions on record: target is **photoreal, interactive in-browser via Pixel Streaming**, the team
builds it, first milestone is **one cinematic showpiece environment** (recommended: Space/Sophia
Nexus, the Brickell skyline at dusk). Dev hardware is **Macs (no NVIDIA GPU)**.

Key honest facts baked into the plan:
- UE5 is a **rebuild, not a port**. The design (regions, NPCs, quests, loops, boundaries) transfers;
  the Three.js code does not.
- **GitHub Codespaces cannot run UE5** (no GPU). Codespaces is for the repo, C++/config editing, the
  Pixel Streaming web layer, docs, and CI. The editor/cooking/streaming run on a GPU machine.
- On a **Mac (Apple Silicon)** you can run the UE5 editor and build + pre-render the environment for
  free. Macs cannot self-host Pixel Streaming (NVIDIA-only), but you do not need that yet.
- For a showpiece, ship a **pre-rendered cinematic** first (Movie Render Queue -> 4K MP4 -> host on
  the site, near-zero cost). Interactive Pixel Streaming is one cloud GPU per concurrent viewer, so
  defer it and gate it.

Files: `KUROGAMI_UE5_SHOWPIECE_PLAN.md` (full production plan) and `kurogami-ue5.zip` (a GitHub repo
scaffold: UE-aware `.gitignore`, Git LFS `.gitattributes`, a Node devcontainer, non-GPU CI, the plan
in `docs/`, and a runnable two-tier web player in `web/` - pre-rendered video plus a Pixel Streaming
iframe slot). The UE project files themselves must be generated by the editor on a Mac; they were
deliberately not fabricated.

---

## 6. How to continue in VS Code (recommended path)

1. **Unzip `kurogami-3d-ported-verified.zip`** into your working folder. This is the live module
   project.
2. Open the folder in VS Code. Recommended extensions: an HTTP server helper (or just use the
   Python one), and Prettier. No build tooling is required (import map, no bundler).
3. **Run it:** a terminal in VS Code, `python3 -m http.server 8000`, open `http://localhost:8000`.
   Test `/#brickell`, `/#jet`, `/#watch`.
4. **Next tasks, in order of value:**
   - Port the remaining single-file worlds into `js/worlds/` modules using the PRDs in
     `kurogami-port-kit.zip` (Olympus, Space, Tokyo, Longevity, London, and the two RWA-game
     regions Chesapeake + Port). Keep the world-module contract used by `boutiques.js`/`brickell.js`.
   - When you have licensed or original `.glb` models, drop them in `assets/models/` to replace the
     procedural watch/jet fallbacks.
   - Optionally move to a Vite build later for production (see `BUILD_GUIDE.md`).
5. **Deploy:** the single-file site deploys via `kurogami-site.zip` (drag to Vercel) or
   `kurogami-vercel.zip` (GitHub -> Vercel, both builds, module build under `/app3d/`). The module
   build must be served, not opened from file://.
6. **UE5 track (separate):** unzip `kurogami-ue5.zip`, push to GitHub, do the UE editor work on a
   Mac per `KUROGAMI_UE5_SHOWPIECE_PLAN.md`, and use the `web/` player for delivery.

---

## 7. File map (what to grab)

- **Work here:** `kurogami-3d-ported-verified.zip` (module project).
- **Port the rest with:** `kurogami-port-kit.zip` (scaffold + source worlds + PRDs).
- **Deploy the web site with:** `kurogami-site.zip` or `kurogami-vercel.zip`.
- **UE5:** `KUROGAMI_UE5_SHOWPIECE_PLAN.md` + `kurogami-ue5.zip`.
- **Single-file sources (reference/edit):** `kurogami-tsukurukami.html` (world), `brickell-city.html`,
  `kurogami-stores.html`, `app.html`, `index.html`, `empty-leg-optimizer.html`, and the rest.
- **Docs:** `BUILD_GUIDE.md` (module architecture + Vite path), `BRICKELL_MVP_PRD.md`,
  `DATA_INTEGRATION.md`, `kurogami-messaging-kit.md`.

---

## 8. The one strategic reminder

Everything shipped is a strong, honest **demo**. The real next unlock is not another region or a
prettier engine; it is (a) backend + persistence if you want progress/multiplayer to survive, and
(b) securities/environmental-markets/legal counsel before anything regulated (tokenization, credits,
real trading) is ever wired in. Build the experience freely; keep the regulated parts gated until the
legal groundwork exists. That posture is the reason this project stays defensible.
