# Kurogami UE5 Build Prompts (for a Claude build loop)

A dependency-ordered queue of focused, self-contained prompts to build the Milestone 1 showpiece
(one photoreal cinematic environment: Brickell skyline at dusk / Space-Sophia Nexus, delivered as a
pre-rendered 4K MP4 in the web player). Each prompt is scoped to one deliverable and states what to
do, the constraints, how to verify, and what to commit.

## How to use this

Two mechanisms:

1. **Driver loop (autonomous):** point a Claude session at the DRIVER PROMPT below. It picks the next
   unchecked task, does it, verifies it, commits it, checks the box, and continues until it hits a
   task tagged `[HUMAN GATE]`, where it stops and hands back to you.
2. **Manual:** copy any single task prompt into a session and run it on its own.

## The automation boundary (read once, it governs everything)

- Claude CANNOT run the Unreal editor, compile the project, or render. It writes the text that
  becomes the project: Python automation, config, data, shell scripts, docs, and the web layer.
- The `unreal` Python module only exists INSIDE the editor. Every Python script here must parse
  standalone (`python3 -m py_compile` clean) by guarding the `import unreal` so a missing module does
  not crash a syntax check. Claude verifies by compiling the file and checking the UE 5.4/5.5 Python
  API surface in docs, NOT by running it.
- Tasks tagged `[HUMAN GATE]` need you in the editor or Launcher. Claude stops there.
- Boundaries from `CLAUDE.md` apply to every file: cosmetic rewards only, honest educational content,
  no trademarked reproductions, no em dashes, Lumen + Nanite + Virtual Shadow Maps.

## Standing rules for every task

- Before writing any UE Python or C++, confirm the API against UE 5.4/5.5 docs (do not write engine
  APIs from memory; versions drift). Prefer the `unreal` Python API and `EditorAssetLibrary` /
  `EditorLevelLibrary` / `unreal.MoviePipeline*` families.
- Make scripts IDEMPOTENT: tag spawned actors/assets with a known prefix and clear that set before a
  rebuild, so re-running does not duplicate the world.
- Keep a `Scripts/Python/build_config.json` as the single source of truth for coordinates, palette,
  sun angle, camera vantage points. Scripts read from it; they do not hardcode.
- Verify what you can headlessly (py_compile, `node --check`, `grep` for em dashes), and for editor
  steps write the EXACT run command plus "what success looks like."
- One task = one commit. Message: `ue5: <task id> <short summary>`.

---

## DRIVER PROMPT (paste this to run the loop)

    Read docs/UE5_BUILD_PROMPTS.md. Find the first task whose checkbox is unchecked and that is NOT
    tagged [HUMAN GATE]. Do only that one task: implement it, verify it per its Verify section, commit
    it with message "ue5: <task id> <summary>", then edit this file to check its box. Then move to the
    next eligible task and repeat. If the next unchecked task is tagged [HUMAN GATE], STOP and tell me
    exactly what I need to do in the editor or Launcher, and what to run when I am done. Do not fabricate
    UE-generated files. Do not cross any boundary in CLAUDE.md. If a task is blocked by a missing
    dependency (for example the web build source or the .uproject), say so and stop rather than guessing.

---

## PHASE 0: Project creation

- [ ] **G0 [HUMAN GATE] Create the UE project.**
  In the Epic Games Launcher (installed to Bobo 1), create a new **Blueprint** project (Games >
  Blank, Starter Content OFF, Raytracing off, target Desktop) named exactly `Kurogami`, created INTO
  `/Volumes/Bobo 1/kurogami-ue5/` so `Kurogami.uproject`, `Content/`, `Config/`, `Saved/` land beside
  the existing files. Blueprint (not C++) is enough for a cinematic and avoids the Xcode toolchain;
  C++ gets added in Milestone 2. Then Edit > Plugins, enable **Python Editor Script Plugin**,
  **Editor Scripting Utilities**, **Movie Render Queue**, and **Movie Render Queue Additional Render
  Passes**; restart the editor. Success: the project opens, Nanite/Lumen are on, and the Output Log
  accepts `import unreal` in the Python console (Window > Output Log, then the cmd dropdown > Python).

## PHASE A: Scriptable scaffold (Claude can grind these)

- [x] **A1 Python automation framework.**
  Create `Scripts/Python/` with: `build_config.json` (empty-but-typed skeleton for coordinates,
  palette hex list, sun pitch/yaw/temperature, and an array of camera vantage points),
  `ue_common.py` (guarded `import unreal`, a logger, an idempotency helper that finds+deletes actors
  by a `KG_` name prefix, and a config loader), and `README.md` documenting the run command:
  `"/Volumes/Bobo 1/<UE>/Engine/Binaries/Mac/UnrealEditor-Cmd" "/Volumes/Bobo 1/kurogami-ue5/Kurogami.uproject" -run=pythonscript -script="Scripts/Python/<file>.py" -unattended -nosplash`.
  Verify: `python3 -m py_compile Scripts/Python/*.py` is clean; `build_config.json` parses with
  `python3 -c "import json;json.load(open('Scripts/Python/build_config.json'))"`.

- [ ] **A2 [HUMAN GATE dependency] Region layout data.**
  The Brickell landmark coordinates, road grid, and building footprints live in the web build file
  `brickell-city.html`, which is NOT in this repo. Either drop `brickell-city.html` into
  `Scripts/Python/source/`, or paste the coordinate/landmark block. Once present, extract it into
  `Content/Data/brickell_layout.json` (buildings: id, x, y, footprint, height, kind; roads: polylines;
  water: bay polygon) and fill the palette + sun angle in `build_config.json` from the brand palette
  in the plan. Verify: layout JSON parses and every building has all fields. If the source is absent,
  STOP and ask for it.

- [x] **A3 Level blockout script.**
  `Scripts/Python/01_blockout.py`: read the layout, spawn a ground plane, one Nanite box per building
  at its coordinate scaled to its height, the road grid as flat meshes, and the bay water plane. Tag
  everything `KG_blockout_*` and clear that set first (idempotent). No materials yet (default grey).
  Verify: py_compile clean; dry-run mode (`--plan` flag that prints the spawn list without importing
  unreal) lists the right count of actors from the layout.

- [x] **A4 Dusk lighting rig script.**
  `Scripts/Python/02_lighting.py`: Directional Light at the dusk pitch/yaw/temperature from config,
  Sky Atmosphere, Sky Light (captured), Exponential Height Fog with Volumetric Fog on, and a
  Post-Process Volume (unbound) setting exposure, moderate bloom, and explicit Lumen GI + reflections.
  A few `KG_neon_*` rect lights for accent. Idempotent by tag. Verify: py_compile clean; the dry-run
  prints each light with its key parameters.

- [x] **A5 Master materials recipe.**
  Material graph authoring via Python is verbose and brittle, so deliver TWO things:
  `Scripts/Python/03_materials.py` that creates material ASSETS and sets scalar/vector parameters
  where the API allows, AND `docs/MATERIALS_RECIPE.md` giving the exact node graph for M_Glass
  (Lumen-reflective), M_WetAsphalt, M_Metal, M_Concrete, M_NeonEmissive, M_Water, plus the brand-color
  instance values, so the human finishes any nodes Python cannot place. Verify: py_compile clean;
  recipe doc lists all six materials with parameters and no em dashes.

- [x] **A6 Sequencer cinematic script.**
  `Scripts/Python/04_sequence.py`: create a Level Sequence `KG_Showpiece`, add a Cine Camera Actor,
  keyframe a 60 to 120 second move through the vantage points in config (establishing wide, hero
  push-ins, slow reveal), add a Camera Cuts track bound to the camera, set DoF and a subtle shake.
  Idempotent (recreate the sequence asset). Verify: py_compile clean; dry-run prints the keyframe
  timeline (time, location, rotation, focal length) matching the config vantage count.

- [x] **A7 Movie Render Queue preset + render automation.**
  Create an MRQ preset config (4K, high anti-aliasing sample count, motion blur, Lumen; a
  Path Tracer variant noted as optional) that outputs an image sequence to `Saved/Render/`. Add
  `Scripts/render_cinematic.sh`: runs MRQ headless from the CLI against `KG_Showpiece`, then
  ffmpeg-encodes the frames to `web/public/cinematic.mp4` (H.264, web-faststart) and extracts a
  mid-timeline `web/public/poster.jpg`. Verify: `bash -n Scripts/render_cinematic.sh` clean; script
  checks for ffmpeg and the uproject and fails loudly if missing; it does NOT run the render itself
  (that is the human GPU step).

- [x] **A8 Config merge script.**
  `Scripts/merge_config.py`: idempotently merge the sections in `Config/DefaultEngine.ini.additions.txt`
  into the project `Config/DefaultEngine.ini` (create it if the project exists; append missing keys,
  never duplicate a section). Ensure the Python + MRQ plugins are enabled in `Kurogami.uproject`.
  Verify: py_compile clean; running it twice produces no second copy of any section (test against a
  fixture ini in `Scripts/tests/`).

- [ ] **A9 Asset license manifest.**
  `docs/ASSET_MANIFEST.md`: a table tracking every Fab/Megascans/original asset (name, source, license,
  date, where used) with the boundary reminder that watches/jets/brands stay original or clear homages,
  never trademarked reproductions. Seed it with headers and one example row. Verify: no em dashes;
  table renders.

- [ ] **A10 Web player wiring check.**
  Confirm `web/public/player.html` references `cinematic.mp4` and `poster.jpg`, start the server
  (`cd web && npm start`), and verify it serves player.html and 404s cleanly for the not-yet-rendered
  video. Add a short `web/public/README.md` noting the two files the render drops here. Verify:
  `node --check web/server.js`; server responds 200 on `/` and the player references both filenames.

## PHASE B: Human-in-editor build (Claude stops, you drive)

- [ ] **B1 [HUMAN GATE] Run the scaffold scripts in order.**
  Run A3, A4, A5, A6, A8 via the run command in `Scripts/Python/README.md` (or paste each into the
  editor Python console). After each, eyeball the viewport. Report anything that errored so Claude can
  fix the script. Success: the blockout, dusk lighting, materials, and a playable Sequencer camera all
  exist in the level.
- [ ] **B2 [HUMAN GATE] Megascans + art pass.** Replace hero blockout boxes with Fab/Megascans meshes
  and materials for the most-seen areas; log each asset in `docs/ASSET_MANIFEST.md`. Iterate to
  screenshot-worthy.
- [ ] **B3 [HUMAN GATE] Lighting + camera polish.** Tune the dusk mood, neon, and fog by eye; refine
  the camera move timing and DoF in Sequencer.
- [ ] **B4 [HUMAN GATE] Render.** Run `Scripts/render_cinematic.sh` (or MRQ in-editor), let it render,
  and confirm `web/public/cinematic.mp4` + `poster.jpg` appear. Commit them (Git LFS handles the mp4).
- [ ] **B5 [HUMAN GATE] Ship + QA.** Run the web player, watch the cinematic end to end on desktop and
  phone, confirm the boundaries read correctly (no trademarked repros on screen), and push.

## PHASE C: Milestone 2+ (deferred, prompts stubbed for later)

- [ ] **C1 DataTables from web build.** Translate `data/dialogue.json` and `data/quests.json` (from the
  module build) into UE DataTable CSVs, dialogue-tree and quest-chain schemas, cosmetic rewards only.
- [ ] **C2 C++ conversion + player controller.** Add a C++ module (matching the `Kurogami` name),
  Enhanced Input, third-person trailing camera per the web build feel.
- [ ] **C3 NPCs + interaction.** MetaHuman placement, proximity interaction, wire the honest
  educational NPCs (Scientist on oyster nitrogen, Analyst on container leasing + fraud warning).
- [ ] **C4 Game loops.** Oyster grow-harvest and container pack-ship as Blueprint actors, cosmetic
  score only.
- [ ] **C5 Pixel Streaming (only if a live interactive demo is needed).** Package, stand up one
  gated instance, autoscale to zero, keep the cinematic as the fallback.
