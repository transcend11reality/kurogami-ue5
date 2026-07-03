# Kurogami UE5 Python build scripts

Automation for the Milestone 1 showpiece (Brickell dusk cinematic). Every numbered script
(`01_blockout.py`, `02_lighting.py`, ...) imports `ue_common.py` and reads `build_config.json` as
its single source of truth for coordinates, palette, sun angle, and camera vantage points.

## Two ways to run a script

**1. Dry-run, no engine needed (verification only).** Runs under plain `python3` and prints what
it WOULD do without touching a level, since the `unreal` module does not exist outside the editor:

    python3 Scripts/Python/01_blockout.py --plan

**2. Inside the UE Editor (the real build step, human-run, see task B1):**

    "/Volumes/Bobo 1/<UE_INSTALL>/Engine/Binaries/Mac/UnrealEditor-Cmd" \
      "/Volumes/Bobo 1/kurogami-ue5/Kurogami.uproject" \
      -run=pythonscript -script="Scripts/Python/01_blockout.py" -unattended -nosplash

Replace `<UE_INSTALL>` with wherever the Epic Games Launcher installed the engine on Bobo 1.
You can also paste a script's contents directly into the in-editor Python console
(Window > Output Log, then the command-type dropdown > Python).

## Idempotency

Every script tags what it creates with a `KG_<script>_` actor label prefix and clears that exact
set first, so re-running a script rebuilds cleanly instead of duplicating actors in the level.
See `ue_common.clear_tagged_actors` / `spawn_tagged_actor`.

## Files

- `build_config.json` - coordinates, palette, sun angle, camera vantage points. Scripts read this;
  they never hardcode a number. Currently a typed skeleton with null/empty placeholders; task A2
  fills it in once the Brickell region source data is available.
- `ue_common.py` - shared logging, config loading, dry-run detection, and the idempotent
  spawn/clear actor helpers.
- `source/` - drop the web build's `brickell-city.html` here for task A2 to extract layout data
  from (not committed until provided).
