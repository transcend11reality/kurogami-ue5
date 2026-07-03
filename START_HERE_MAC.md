# START HERE (Mac + external NVMe SSD + VS Code + Claude + Unreal)

An ordered checklist to stand up this project entirely on an external NVMe SSD, work in VS Code with
Claude, and set up Unreal for the environment build. Do the steps in order.

## 0. Reality check (so nothing surprises you)
- **Free path:** the UE editor and building/pre-rendering the environment are free on an Apple Silicon
  Mac. The only unavoidable recurring cost is interactive Pixel Streaming later (a cloud GPU per
  viewer). Defer it.
- **What runs where:** VS Code + Claude edit code/config/docs and the web layer. The Mac runs the UE
  editor. A cloud GPU (later) hosts the interactive stream. Claude cannot run the editor or render.
- **External drive caveat:** running everything off an external SSD works, but never unplug the drive
  while UE or VS Code has the project open, and keep good backups (push to GitHub).

## 1. Prepare the external NVMe SSD
1. Plug it into a **USB-C / Thunderbolt** port (not a slow adapter).
2. Open **Disk Utility**. Back up anything on the drive first, then **Erase** it as:
   - Format: **APFS** (do not use exFAT for a live project; it corrupts many-small-file workloads).
   - Scheme: GUID Partition Map.
3. Give it a clear name, for example `KUROGAMI`. It will mount at `/Volumes/KUROGAMI`.
4. Make a working folder: `/Volumes/KUROGAMI/kurogami-ue5/`.

## 2. Put this repo on the drive
1. Unzip this kit into `/Volumes/KUROGAMI/kurogami-ue5/` so `CLAUDE.md`, `README.md`, `web/`, `docs/`,
   and `Config/` sit at that folder's root.
2. This folder is your git repo and your VS Code workspace.

## 3. VS Code (open the repo from the drive)
1. Install **Visual Studio Code** (the app can live on your internal drive; it is small).
2. File > Open Folder > `/Volumes/KUROGAMI/kurogami-ue5/`.
3. Accept the recommended extensions when prompted (see `.vscode/extensions.json`).
4. Run the web player to confirm the drive workflow works:
   - Terminal > Run Task > **Serve web player** (or `cd web && npm start`), then open port 8080.

## 4. Claude in VS Code
1. Install **Claude Code** and its VS Code integration. Search "Claude Code" in the Extensions panel,
   or follow the current install steps at the official docs. (Install location does not matter; it
   operates on whatever folder is open.)
2. Open the repo folder as the workspace. Claude Code automatically reads **`CLAUDE.md`** at the root,
   which carries the project rules and context, so it will follow the boundaries without re-explaining.
3. Use Claude for: writing UE C++ and `Config/` settings, the web layer, docs, and CI. Not for running
   the editor or rendering (it cannot).

## 5. Unreal Engine (install to the external drive)
1. Install the **Epic Games Launcher**.
2. In the Launcher, before installing the engine, set the **install location to the external drive**
   (Launcher settings let you choose where engines install). Install **UE 5.4 or 5.5**.
3. Install **Git LFS** once: `git lfs install` (UE content is large binaries; this repo tracks them
   via `.gitattributes`).
4. In the Launcher, **create a new UE project** (Blank, Starter Content off) **into this repo folder**,
   named `Kurogami`. The generated `Kurogami.uproject`, `Source/`, `Content/`, and `Config/` will
   appear alongside the files already here.
5. Open the project, then **enable the Pixel Streaming plugin** (Edit > Plugins) and restart.
6. Merge `Config/DefaultEngine.ini.additions.txt` into the project's `Config/DefaultEngine.ini`
   (append the sections; do not overwrite the file).

## 6. First build loop (the showpiece, free on the Mac)
1. **Blockout** the chosen region (recommended: Space / Sophia Nexus, the Brickell skyline at dusk),
   using the web build as a layout reference. Lock 3 to 5 hero camera positions.
2. **Assets:** pull photoreal, UE-licensed assets from **Fab / Quixel Megascans** (free in UE). Keep
   them on the external drive with the project.
3. **Lighting + materials:** one directional light + sky atmosphere + Lumen; add neon/emissive and
   volumetric fog for mood. Master materials with instances.
4. **Cinematic:** author a 60 to 120 second camera move in **Sequencer**, then render with **Movie
   Render Queue** to a 4K MP4.
5. Put the MP4 at `web/public/cinematic.mp4` (and a `poster.jpg`). Run the web player. That video is
   your photoreal, in-browser showpiece, hostable for near nothing.

## 7. Back up (do this early and often)
- Create a GitHub repo and push: `git add . && git commit -m "init" && git push`. This gives you
  version history and a second copy that does not live only on the external drive.
- Large assets go through Git LFS automatically.

## 8. Cautions (external-drive specific)
- Format is **APFS**, not exFAT.
- Do not unplug the drive while UE or VS Code is open.
- Keep your Mac's internal drive at least ~10 percent free; UE still uses some temp space even when
  the project is external.
- If the engine feels sluggish running off the external, that is the known tradeoff of an all-external
  setup. It is workable; the alternative (a cloud GPU VM) is only needed once you reach interactive
  Pixel Streaming, which a Mac cannot self-host anyway.

## Where to read more
- `PROJECT_CONTEXT.md` - the whole project (web builds, module build, UE track, rules).
- `docs/UE5_SHOWPIECE_PLAN.md` - the full UE5 production plan and Pixel Streaming details.
- `README.md` - the what-runs-where matrix and repo layout.
- `web/README.md` - the two-tier browser player and streaming options.
