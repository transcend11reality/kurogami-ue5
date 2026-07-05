"""Task: procedural city fill for generic background buildings.

Reads Content/Data/brickell_layout.json's road grid and existing landmark buildings, then
deterministically fills the empty blocks between roads with grey-box filler buildings using a
fixed random seed, mirroring the original web build's buildBlocks() logic (buildings closer to
the district center are taller) without literally reproducing its per-page-load randomness, since
that data was never extractable (see Content/Data/brickell_layout.json's own _note field: the
original source scatters filler buildings randomly at load time, so there is no fixed list to
pull from). A fixed seed instead makes this fill deterministic and idempotent like every other
build script here, not truly random.

Skips any block that falls in the water, or that overlaps the clearance radius around an existing
named landmark building (so filler never collides with Four Seasons Miami, Brickell City Centre,
etc.).

Tagged KG_cityfill_* and idempotent (clears + respawns on every run), same pattern as
01_blockout.py. No materials here on purpose, same grey-box scope as the rest of Phase A; task B2
(the human art pass) is what replaces these with real Fab meshes.

Run inside the editor:
    UnrealEditor-Cmd Kurogami.uproject -run=pythonscript -script="Scripts/Python/05_city_fill.py" -unattended -nosplash

Dry-run (no engine, prints the spawn plan and exits):
    python3 Scripts/Python/05_city_fill.py --plan
"""
import json
import os
import random
import sys

try:
    _SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # __file__ is undefined when run via exec(open(...).read()) in the in-editor Python console.
    import unreal
    _SCRIPT_DIR = os.path.join(unreal.Paths.project_dir(), "Scripts", "Python")
sys.path.insert(0, _SCRIPT_DIR)
import ue_common as kg

TAG = "KG_cityfill_"
CUBE_ASSET = "/Engine/BasicShapes/Cube.Cube"
PRIMITIVE_SIZE_CM = 100.0

# Fixed seed so the fill is deterministic and idempotent across runs, unlike the original web
# build's true per-page-load randomness (which is exactly why this data could not just be
# extracted in task A2; see Content/Data/brickell_layout.json's _note field).
RANDOM_SEED = 20260704

WATER_X_CM = 19600.0  # matches Content/Data/brickell_layout.json's water polygon left edge
LANDMARK_CLEARANCE_CM = 4600.0  # skip a block within this distance of an existing named building
DISTRICT_CENTER_TALL_RADIUS_CM = 12000.0  # inside this radius, filler buildings run taller

GLASS_KINDS = ["glass", "glass2"]
MID_KINDS = ["concrete", "glass"]
LOW_KINDS = ["brick", "white"]


def load_layout():
    layout_path = kg.repo_path("Content", "Data", "brickell_layout.json")
    if not os.path.isfile(layout_path):
        kg.log_warning("layout not found at %s; city fill will spawn 0 buildings" % layout_path)
        return {"buildings": [], "roads": []}
    with open(layout_path, "r") as f:
        return json.load(f)


def road_positions(layout, prefix):
    """Extract the distinct fixed coordinate for each road matching id prefix ('ns_' or 'ew_'),
    reading the constant axis value from its polyline (x for ns_ roads, y for ew_ roads)."""
    positions = []
    for road in layout.get("roads", []):
        if not road["id"].startswith(prefix):
            continue
        (x0, y0), (x1, y1) = road["polyline"][0], road["polyline"][1]
        positions.append(x0 if prefix == "ns_" else y0)
    return sorted(set(positions))


def build_plan(layout):
    xs = road_positions(layout, "ns_")
    ys = road_positions(layout, "ew_")
    buildings = layout.get("buildings", [])
    rng = random.Random(RANDOM_SEED)

    plan = []
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cx = (xs[i] + xs[i + 1]) / 2.0
            cy = (ys[j] + ys[j + 1]) / 2.0

            if cx > WATER_X_CM:
                continue
            if any(
                abs(b["x"] - cx) < LANDMARK_CLEARANCE_CM and abs(b["y"] - cy) < LANDMARK_CLEARANCE_CM
                for b in buildings
            ):
                continue

            dist_from_center = (cx ** 2 + cy ** 2) ** 0.5
            count = 1 + (1 if rng.random() < 0.6 else 0)
            for k in range(count):
                width = 1500.0 + rng.random() * 1700.0
                depth = 1500.0 + rng.random() * 1700.0
                if dist_from_center < DISTRICT_CENTER_TALL_RADIUS_CM:
                    height = 4000.0 + rng.random() * 9000.0
                else:
                    height = 1800.0 + rng.random() * 4400.0
                kind = (
                    rng.choice(GLASS_KINDS) if height > 5800.0
                    else rng.choice(MID_KINDS) if height > 3200.0
                    else rng.choice(LOW_KINDS)
                )
                jitter_x = (rng.random() - 0.5) * 2000.0
                jitter_y = (rng.random() - 0.5) * 2000.0
                plan.append({
                    "label": "%sblock_%d_%d_%d" % (TAG, i, j, k),
                    "location": (cx + jitter_x, cy + jitter_y, height / 2.0),
                    "size_cm": (width, depth, height),
                    "kind": kind,
                })
    return plan


def apply_plan(plan):
    kg.clear_tagged_actors(TAG)
    for item in plan:
        sx, sy, sz = item["size_cm"]
        scale = (sx / PRIMITIVE_SIZE_CM, sy / PRIMITIVE_SIZE_CM, sz / PRIMITIVE_SIZE_CM)
        kg.spawn_tagged_mesh_actor(CUBE_ASSET, item["label"], item["location"], scale=scale)


def main():
    layout = load_layout()
    plan = build_plan(layout)
    kg.log("city fill plan: %d filler building(s)" % len(plan))

    if kg.is_dry_run():
        for item in plan[:10]:
            kg.log("  [plan] %s kind=%s size_cm=%s" % (item["label"], item["kind"], item["size_cm"]))
        if len(plan) > 10:
            kg.log("  ... and %d more" % (len(plan) - 10))
        return

    apply_plan(plan)
    kg.log("city fill: spawned %d actor(s)" % len(plan))


if __name__ == "__main__":
    main()
