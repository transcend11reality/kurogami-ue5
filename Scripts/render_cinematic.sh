#!/usr/bin/env bash
# Task A7/B4: headless Movie Render Queue render + ffmpeg encode for the Brickell showpiece.
#
# Renders the KG_Showpiece Level Sequence via the saved MoviePipelineQueue preset described in
# docs/MRQ_PRESET.md, then encodes the resulting image sequence into web/public/cinematic.mp4 and
# pulls a mid-timeline poster frame into web/public/poster.jpg.
#
# This is a HUMAN, GPU-machine step (task B4). It is not run automatically by the build loop; it
# only gets verified for syntax and guard-clause correctness (bash -n, and that it fails loudly
# instead of half-running when ffmpeg or the .uproject are missing).
#
# Required environment variables:
#   UE_EDITOR_CMD   Full path to UnrealEditor-Cmd on this machine, for example:
#                     export UE_EDITOR_CMD="/Volumes/Bobo 1/UE_5.5/Engine/Binaries/Mac/UnrealEditor-Cmd"
#
# Optional environment variables (sensible defaults shown):
#   MAP_PATH            Persistent level to load (default: /Game/Maps/L_Brickell_Dusk). Update this
#                        once the human names the actual map created in task G0.
#   MRQ_PRESET_PATH      Saved MoviePipelineQueue asset (default: /Game/Cinematics/KG_Showpiece_MRQ_Preset)
#   RENDER_OUTPUT_DIR    Where MRQ writes the image sequence (default: Saved/Render/KG_Showpiece)
#   RENDER_FRAMERATE     Encode framerate (default: 30)
#
# Usage:
#   export UE_EDITOR_CMD="/path/to/UnrealEditor-Cmd"
#   bash Scripts/render_cinematic.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
UPROJECT="$REPO_ROOT/Kurogami.uproject"

MAP_PATH="${MAP_PATH:-/Game/Maps/L_Brickell_Dusk}"
MRQ_PRESET_PATH="${MRQ_PRESET_PATH:-/Game/Cinematics/KG_Showpiece_MRQ_Preset}"
RENDER_OUTPUT_DIR="${RENDER_OUTPUT_DIR:-$REPO_ROOT/Saved/Render/KG_Showpiece}"
RENDER_FRAMERATE="${RENDER_FRAMERATE:-30}"

OUT_MP4="$REPO_ROOT/web/public/cinematic.mp4"
OUT_POSTER="$REPO_ROOT/web/public/poster.jpg"

fail() {
  echo "ERROR: $1" >&2
  exit 1
}

# --- Guard clauses: fail loudly instead of half-running. ---

if [ -z "${UE_EDITOR_CMD:-}" ]; then
  fail "UE_EDITOR_CMD is not set. Export it to the UnrealEditor-Cmd binary for your UE install, e.g.:
  export UE_EDITOR_CMD=\"/Volumes/Bobo 1/UE_5.5/Engine/Binaries/Mac/UnrealEditor-Cmd\""
fi

if [ ! -x "$UE_EDITOR_CMD" ]; then
  fail "UE_EDITOR_CMD ('$UE_EDITOR_CMD') does not exist or is not executable."
fi

if [ ! -f "$UPROJECT" ]; then
  fail "Kurogami.uproject not found at $UPROJECT. Complete task G0 (create the UE project into this
  repo via the Epic Games Launcher) before rendering."
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  fail "ffmpeg is not installed. Install it first, for example: brew install ffmpeg"
fi

if [ "$MAP_PATH" = "/Game/Maps/L_Brickell_Dusk" ]; then
  echo "NOTE: using the default MAP_PATH ($MAP_PATH). Set the MAP_PATH environment variable if the" \
       "actual level created in task G0 has a different name or location." >&2
fi

# --- Render (task B4, GPU machine only). ---

echo "Rendering $MRQ_PRESET_PATH (sequence KG_Showpiece, map $MAP_PATH) ..."
"$UE_EDITOR_CMD" "$UPROJECT" "$MAP_PATH" -game \
  -MoviePipelineConfig="$MRQ_PRESET_PATH" \
  -windowed -RenderOffscreen -Unattended -Log -StdOut -allowStdOutLogVerbosity

if [ ! -d "$RENDER_OUTPUT_DIR" ]; then
  fail "Render output directory $RENDER_OUTPUT_DIR was not created. Check the MRQ preset's Output
  Directory setting matches docs/MRQ_PRESET.md, and check the editor Output Log for render errors."
fi

# --- Encode the image sequence to a web-ready MP4. ---

mkdir -p "$(dirname "$OUT_MP4")"
echo "Encoding image sequence to $OUT_MP4 ..."
ffmpeg -y -framerate "$RENDER_FRAMERATE" \
  -i "$RENDER_OUTPUT_DIR/KG_Showpiece.%04d.png" \
  -c:v libx264 -pix_fmt yuv420p -movflags +faststart \
  "$OUT_MP4"

# --- Pull a mid-timeline poster frame. ---

DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUT_MP4")
MID_SEC=$(awk "BEGIN { printf \"%.2f\", $DURATION / 2 }")

echo "Extracting poster frame at ${MID_SEC}s to $OUT_POSTER ..."
ffmpeg -y -ss "$MID_SEC" -i "$OUT_MP4" -frames:v 1 "$OUT_POSTER"

echo "Done. $OUT_MP4 and $OUT_POSTER are ready for the web player (task B4 complete; see task B5)."
