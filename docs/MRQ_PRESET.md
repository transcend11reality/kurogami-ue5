# Movie Render Queue preset: KG_Showpiece_MRQ_Preset

Movie Render Queue configuration is authored through the editor's Render Movie Queue panel and saved
as a `MoviePipelineQueue` / `MoviePipelineMasterConfig` asset, not written by a script (building that
asset graph by hand in Python is exactly the kind of brittle, verbose automation the production plan
avoids). Build it once in the editor per this recipe, save it at `/Game/Cinematics/KG_Showpiece_MRQ_Preset`,
and `Scripts/render_cinematic.sh` (task A7) points the command-line render at that saved asset.

## Steps (Windows > Cinematics > Render Movie Queue in the editor, task B4)

1. Add job: the `KG_Showpiece` Level Sequence, current level.
2. **Output settings:**
   - Resolution: **3840x2160 (4K)**.
   - Output directory: `{project_dir}/Saved/Render/KG_Showpiece`.
   - Filename format: `{sequence_name}.{frame_number}`.
   - Output format: PNG (or EXR for grading headroom; PNG is simpler for the ffmpeg encode step).
3. **Anti-Aliasing settings:** Spatial samples 8, Temporal samples 1 (raise spatial samples for a
   cleaner final pass if render time allows).
4. **Deferred rendering (Lumen path, the default and fastest option):** leave the renderer on the
   standard Deferred path so Lumen GI/reflections from `02_lighting.py`'s Post Process Volume are
   used as-is. Enable Motion Blur in the Anti-Aliasing / Rendering settings for the camera move.
5. **Optional Path Tracer variant** (reference-quality, much slower, section 3 of the production
   plan): duplicate this preset as `KG_Showpiece_MRQ_Preset_PathTracer`, switch the renderer to the
   Path Tracer, and raise samples per pixel substantially (for example 256). Use this only if render
   time budget allows; the Lumen deferred preset is the one shipped by default.
6. Save the config as an asset via the queue panel's save button, at the path above.

## What the CLI render then does

`Scripts/render_cinematic.sh` invokes `UnrealEditor-Cmd` in `-game -Unattended` mode pointed at this
saved preset asset, which renders the image sequence to `Saved/Render/KG_Showpiece/`, then the script
ffmpeg-encodes that sequence into `web/public/cinematic.mp4` and pulls a poster frame into
`web/public/poster.jpg`. See the script's header comment for the exact command and required
environment variables.
