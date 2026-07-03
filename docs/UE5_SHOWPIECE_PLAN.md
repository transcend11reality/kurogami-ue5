# Kurogami UE5 Cinematic Showpiece + Pixel Streaming - Production Plan

Prepared for the team building the Unreal Engine 5 version. This is a production plan, not
a code port. Read it top to bottom before starting; it is written to be self-contained.

---

## 0. The honest reframe (read this first)

Moving from the browser (Three.js) build to Unreal Engine 5 is a **rebuild in a new medium**,
not an upgrade of existing files. Almost no code transfers. What transfers is the **design**:
the eight regions, the NPC characters and dialogue, the quest chains, the farming/shipping game
loops, the brand and lore, and the boundaries baked into all of it (cosmetic scores, honest
educational NPCs, gated tokenization). Treat the existing web build and its source files as the
**design bible and reference blockout**, not as something to convert.

Milestone 1 is deliberately narrow: **one photoreal cinematic environment, delivered in-browser.**
No gameplay systems yet. Get one region looking stunning and streamable first; layer game systems
in later milestones. This is the right order and it keeps the first deliverable achievable.

---

## 1. The cost-and-quality decision you must make up front

You chose "photoreal but in-browser." There are two ways to deliver that, and for a *cinematic
showpiece* they are not equal:

**A. Pre-rendered cinematic (Movie Render Queue -> video -> CDN).**
Render the environment offline at 4K/8K with Lumen or the Path Tracer, export a video, host it on
any CDN or your existing Vercel site. Highest possible fidelity (offline rendering beats real-time),
trivial to serve, near-zero ongoing cost, works on every device including phones. The catch: it is
not interactive; the viewer watches, they do not control the camera.

**B. Interactive Pixel Streaming (UE runs on a cloud GPU, streams video to the browser).**
The viewer moves through the space live. This is what you asked for. The catch: **each concurrent
interactive viewer needs a GPU-backed UE instance running in the cloud.** That is a real, ongoing,
per-viewer cost (see section 6). It shines for a controlled demo (an investor session, a booth, a
"request access" experience), and gets expensive fast for uncontrolled public traffic.

**Recommended sequence (do both, in this order):**
1. Build the environment once (sections 3 to 5).
2. Ship the **pre-rendered cinematic** immediately. It is your showpiece today, gorgeous and cheap.
3. Add the **Pixel Streaming interactive layer** (section 6) when you have a reason for viewers to
   drive the camera, and gate it (session limits, request-access, autoscale to zero) so the GPU bill
   is bounded.

This gives you the in-browser photoreal win now and the interactivity when it earns its cost.

---

## 2. Which region to build first

Pick one region as the showpiece. The best UE5 "sizzle" is where Lumen (real-time global
illumination and reflections), Nanite (film-density geometry), and volumetrics do the most work:

- **Space / Sophia Nexus (Brickell skyline at dusk)** - neon, wet reflective streets, glass towers,
  volumetric haze. The classic UE5 hero shot, and it is your flagship HQ. **Primary recommendation.**
- **Port of Singapore at night** - water reflections, volumetric fog, gantry cranes and container
  stacks as dense Nanite geometry, neon accents. Extremely cinematic, strong alternative.
- **Olympus hub at golden hour** - the flagship temple, warm rim light, marble and gold. On-brand
  and iconic, slightly less "wow" than neon+reflections but a strong signature image.

Recommendation: build **Space / Sophia Nexus (Brickell dusk)** as the showpiece. It is the most
UE5-flattering and the most central to the brand. Whatever you choose, use the existing web region
as the layout blockout so proportions and landmarks stay consistent.

---

## 3. Engine, tools, and hardware

- **Unreal Engine 5.4 or 5.5** (5.4+ has the mature Pixel Streaming 2 plugin).
- **Rendering:** Nanite (virtualized geometry, no manual LODs), Lumen (real-time GI + reflections),
  Virtual Shadow Maps. For the pre-rendered path, optionally the **Path Tracer** for reference-quality.
- **Assets:** **Fab** (formerly Quixel Megascans) - thousands of photoreal, UE-licensed scans free for
  use in UE. This is your main asset source and it sidesteps most licensing risk.
- **Cinematics:** **Sequencer** (camera work, timing) + **Movie Render Queue** (final frames/video).
- **NPCs (later milestones):** **MetaHuman** for photoreal characters; Control Rig + Sequencer for
  performance. Not needed for the environment showpiece.
- **Team for milestone 1:** one UE-capable environment/technical artist can carry the showpiece; a
  second generalist helps with the Pixel Streaming deployment. This is not a large team, but it is a
  different skill set than web dev (UE, Blueprints, materials, lighting, some DevOps for streaming).
- **Workstation:** Windows, a recent NVIDIA RTX GPU (RTX 3080/4070 or better), 32 to 64 GB RAM, fast
  NVMe. UE5 projects and Nanite assets are large; budget hundreds of GB of disk.

---

## 4. Environment build pipeline (the showpiece)

1. **Blockout.** Recreate the chosen region's layout as simple geometry, using the web build for
   proportions and landmark placement. Lock camera-worthy vantage points early.
2. **Hero geometry.** Bring in Fab/Megascans and custom meshes as Nanite. Buildings, cranes, docks,
   the temple, whatever the region needs. Nanite means you can use film-density meshes directly.
3. **Materials.** Master materials with instances: glass (with Lumen reflections), wet asphalt, brushed
   metal, concrete, water. Drive variation through material instance parameters, not new materials.
4. **Lighting.** One directional (sun/moon) + sky atmosphere + Lumen for bounce and reflections.
   Add local emissive/neon and a few area lights for the hero shots. Exponential height fog +
   volumetric fog for depth and god rays.
5. **Water and volumetrics.** UE Water plugin (or a custom material) for the bay/river/harbor; tune
   reflections and caustics. Volumetric clouds if skyline is visible.
6. **Set dressing and motion.** Populate with props; add subtle motion (drifting fog, water, blinking
   lights, a slow crane, distant traffic) so the scene feels alive even without gameplay.
7. **Optimization pass.** Even for cinematics, keep it running: check Nanite stats, shadow cost,
   translucency overdraw, and Lumen scene detail. For Pixel Streaming this matters a lot (section 6).

Keep the brand: deep navy/obsidian, teal, gold, violet, crimson, cyan; kanji signage; the "Order of
Shadows" restraint. Match the web build's palette so the two read as one world.

---

## 5. The pre-rendered cinematic (ship this first)

1. In **Sequencer**, author a 60 to 120 second camera move through the environment: establishing wide,
   a few hero push-ins on landmarks, a slow reveal. Add depth of field, subtle camera shake, timed
   light/fog changes.
2. Render with **Movie Render Queue** at 4K (or 8K), high sample counts, motion blur, Lumen or Path
   Tracer. Output an image sequence or ProRes, then encode to web-friendly H.264/H.265 MP4.
3. Host the MP4 on your CDN / existing site. This is a photoreal, in-browser showpiece that runs
   everywhere and costs almost nothing to serve. Add a poster frame and a tasteful play control.

This deliverable alone satisfies "photoreal in the browser" and gives you something to show while the
interactive layer is built.

---

## 6. Pixel Streaming (the interactive layer)

### How it works
Unreal runs on a **cloud machine with an NVIDIA GPU**, renders the scene, hardware-encodes the frames
(NVENC) to a video stream, and sends it over **WebRTC** to the viewer's browser. The browser sends
input (mouse/keyboard/touch) back. The viewer needs no install and no powerful device; the GPU work
happens in the cloud.

### Components you deploy
- **The packaged UE app** with the **Pixel Streaming plugin** enabled (Linux builds work and are cheaper
  to host).
- **Signalling + web server** from Epic's **Pixel Streaming Infrastructure** (open source): serves the
  player web page and brokers the WebRTC connection.
- **STUN/TURN** (e.g. coturn) for NAT traversal so connections succeed across networks.
- **A scaling layer** (matchmaker / orchestrator) if you want more than one concurrent viewer: it spins
  up one UE+GPU instance per session and routes viewers to a free one.

### The core cost fact
Interactive Pixel Streaming is roughly **one GPU instance per concurrent interactive viewer.** A cloud
GPU instance (AWS g4dn.xlarge with a T4, or g5.xlarge with an A10G; Azure NV-series; GCP equivalents)
runs roughly **$0.50 to $1.50 per hour**. So:
- 1 concurrent viewer ~ one GPU ~ ~$1/hr.
- 50 concurrent viewers ~ ~50 GPUs ~ ~$50/hr while live.
Encoding/quality and instance choice move these numbers, but the shape is linear in concurrency. Plan
for it. (A few viewers can share one instance via an SFU, but interactive camera control is effectively
per-viewer.)

### Two ways to run it
- **Managed Pixel Streaming provider** (Arcware, Vagon Streams, Eagle 3D Streaming, and similar). They
  host the GPUs, autoscaling, and the web player; you upload your packaged build and embed an iframe.
  Fastest path, less DevOps, you pay per streaming hour. **Recommended for a small team.**
- **Self-hosted on cloud GPUs** (AWS/Azure/GCP), containerized (Linux), with autoscaling via Kubernetes
  or Epic's scalable Pixel Streaming reference. More control, lower per-hour cost at scale, much more
  ops work. Choose this only if you have DevOps capacity.

### Keep the bill bounded
- **Autoscale to zero** when idle so you pay nothing between sessions.
- **Gate access:** "request a session" / scheduled demos / a queue, rather than an always-open public link.
- **Session timeouts** (for example 10 to 15 minutes) so instances free up.
- **Fallback to the pre-rendered video** when no GPU session is available or on mobile, so no viewer
  ever hits a dead end.

### Embedding in your existing site
The Pixel Streaming player is a web page you can host or iframe. Drop it into the current Kurogami site
(root or an `/experience/` route) with the pre-rendered MP4 as the graceful fallback. Same site, two
tiers: video for everyone, live stream for gated sessions.

---

## 7. Assets and licensing (the boundary that gets sharper in UE)

Photoreal UE needs real 3D assets, which raises the same IP line you have held throughout:

- **Prefer Fab/Megascans and original models.** They are licensed for UE use and cover most environment
  needs (architecture, materials, props, vegetation, vehicles-as-set-dressing).
- **Do not model real trademarked products as the genuine article** (the Royal Oak, a specific
  Bombardier jet, brand logos on containers). Keep watches/jets/brands as **original designs or clear
  homages under your own brand**, exactly as in the web build. Photoreal makes passing-off easier to do
  accidentally, so hold this line harder, not softer.
- Track licenses for every purchased/downloaded asset. Keep a manifest.

---

## 8. Boundaries that carry into UE (unchanged)

Everything that made the web build defensible carries over verbatim:
- Scores and rewards are **cosmetic**. No minting, no tokens, no real-money trading, no representation
  of real ownership anywhere in the experience.
- Educational NPCs (the Scientist, the Analyst) stay **accurate and honest**, including the container
  investment fraud warning. A prettier engine does not change the facts they teach.
- Anything regulated stays **gated** pending counsel. UE is a presentation upgrade, not a license to
  wire in the parts that were always off-limits.

Bake these into the design bible so no one "upgrades" them away during the rebuild.

---

## 9. Roadmap beyond the showpiece

Once the environment streams, layer systems in milestones, reusing the web build's design as spec:
1. **Player + controls.** Third-person character (UE Enhanced Input), the trailing camera feel from the
   web build. Or keep it on-rails/free-fly for a pure showpiece.
2. **NPCs.** MetaHumans for the region's characters; place them and add proximity interaction.
3. **Dialogue + quests, data-driven.** Mirror the JSON you already have: put dialogue trees and quest
   chains in **DataTables / Data Assets** so writers edit data, not Blueprints. This is a direct
   translation of `data/dialogue.json` and `data/quests.json` from the module build.
4. **Game loops.** Rebuild the oyster-grow-harvest and container-pack-ship loops as Blueprint actors
   with the same cosmetic-score, honest-education design.
5. **More regions.** Repeat the environment pipeline per region. Stream each as it is ready.

---

## 10. First two weeks (concrete starting actions)

1. Install UE 5.4/5.5; enable Nanite/Lumen; create the project. Enable the Pixel Streaming plugin.
2. Blockout the chosen region from the web build; lock 3 to 5 hero camera positions.
3. First lighting + material pass on the blockout so the mood reads immediately (this sells the look
   before assets are final).
4. Drop in Fab/Megascans hero assets for the most-seen areas; iterate to "screenshot-worthy."
5. Author a short Sequencer camera move; render a 4K test with Movie Render Queue; put the MP4 on the
   site behind a poster. **This is your first shippable showpiece.**
6. In parallel, stand up a **single** Pixel Streaming instance (start with a managed provider trial or
   one cloud GPU) and get the packaged build streaming to a browser for one viewer. Prove the pipeline
   before worrying about scale.

---

## 11. Honest risk + cost summary

- **Skills gap:** UE + materials + lighting + streaming DevOps is a different team than web. Budget
  ramp-up time or hire for it.
- **Asset cost/time:** photoreal means real art. Fab/Megascans covers a lot for free, but bespoke hero
  assets take time or money, and licensing must be tracked.
- **Streaming cost:** interactive Pixel Streaming is linear in concurrent viewers. Gate it, autoscale to
  zero, and keep the pre-rendered video as the mass-reach fallback.
- **Scope creep:** the whole point of milestone 1 is one environment, one cinematic. Do not add NPCs,
  gameplay, or a second region until the first is shipped and streaming.
- **The good news:** the design is done and proven. You are rebuilding a known thing in a prettier
  medium, which is far lower risk than designing from scratch. Lead with the pre-rendered cinematic and
  you will have something genuinely stunning in weeks, not months.
