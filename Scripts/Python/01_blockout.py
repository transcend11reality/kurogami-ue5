"""Task A3: level blockout for the Brickell dusk showpiece.

Reads Content/Data/brickell_layout.json (produced by task A2) and spawns simple grey blockout
geometry: one scaled cube per building, thin scaled cubes for road segments, and a scaled plane
for the bay. Everything is tagged KG_blockout_* and that set is cleared first, so re-running this
script rebuilds the blockout instead of duplicating it.

No materials here on purpose (task A5 handles those); this is deliberately grey-box.

Run inside the editor:
    UnrealEditor-Cmd Kurogami.uproject -run=pythonscript -script="Scripts/Python/01_blockout.py" -unattended -nosplash

Dry-run (no engine, prints the spawn plan and exits):
    python3 Scripts/Python/01_blockout.py --plan
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ue_common as kg

TAG = "KG_blockout_"

# Engine built-in primitive meshes used for grey-box geometry.
CUBE_ASSET = "/Engine/BasicShapes/Cube.Cube"
PLANE_ASSET = "/Engine/BasicShapes/Plane.Plane"

# unreal.BasicShapes cube/plane are 100x100x100 cm at scale (1,1,1); divide desired
# world-space size in cm by 100 to get the scale factor to pass to spawn_tagged_mesh_actor.
PRIMITIVE_SIZE_CM = 100.0


def load_layout():
    """Load Content/Data/brickell_layout.json. Returns an empty, well-shaped layout (with a
    warning logged) if the file does not exist yet, since task A2 is what produces it."""
    layout_path = kg.repo_path("Content", "Data", "brickell_layout.json")
    if not os.path.isfile(layout_path):
        kg.log_warning(
            "layout not found at %s (task A2 has not run yet); blockout will spawn 0 buildings, "
            "0 roads, no water, ground plane only" % layout_path
        )
        return {"buildings": [], "roads": [], "water": None}
    with open(layout_path, "r") as f:
        return json.load(f)


def plan_ground():
    return {"kind": "ground", "label": TAG + "ground", "size_cm": (200000.0, 200000.0)}


def plan_buildings(layout):
    plan = []
    for b in layout.get("buildings", []):
        footprint = b.get("footprint", {})
        width = float(footprint.get("width", 2000.0))
        depth = float(footprint.get("depth", 2000.0))
        height = float(b.get("height", 3000.0))
        plan.append({
            "kind": "building",
            "label": "%sbuilding_%s" % (TAG, b.get("id", "unknown")),
            "location": (float(b.get("x", 0.0)), float(b.get("y", 0.0)), height / 2.0),
            "size_cm": (width, depth, height),
        })
    return plan


def plan_roads(layout):
    plan = []
    for r in layout.get("roads", []):
        polyline = r.get("polyline", [])
        width = float(r.get("width", 800.0))
        for i in range(len(polyline) - 1):
            x0, y0 = polyline[i]
            x1, y1 = polyline[i + 1]
            mid_x, mid_y = (x0 + x1) / 2.0, (y0 + y1) / 2.0
            length = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
            plan.append({
                "kind": "road_segment",
                "label": "%sroad_%s_%d" % (TAG, r.get("id", "unknown"), i),
                "location": (mid_x, mid_y, 5.0),
                "size_cm": (max(length, 1.0), width, 10.0),
            })
    return plan


def plan_water(layout):
    water = layout.get("water")
    if not water or not water.get("polygon"):
        return None
    xs = [p[0] for p in water["polygon"]]
    ys = [p[1] for p in water["polygon"]]
    width = max(xs) - min(xs)
    depth = max(ys) - min(ys)
    return {
        "kind": "water",
        "label": TAG + "water",
        "location": ((max(xs) + min(xs)) / 2.0, (max(ys) + min(ys)) / 2.0, 0.0),
        "size_cm": (max(width, 1.0), max(depth, 1.0)),
    }


def build_plan(layout):
    plan = [plan_ground()]
    plan.extend(plan_buildings(layout))
    plan.extend(plan_roads(layout))
    water = plan_water(layout)
    if water:
        plan.append(water)
    return plan


def apply_plan(plan):
    kg.clear_tagged_actors(TAG)
    for item in plan:
        if item["kind"] in ("ground", "water"):
            sx, sy = item["size_cm"]
            scale = (sx / PRIMITIVE_SIZE_CM, sy / PRIMITIVE_SIZE_CM, 0.01)
            location = item.get("location", (0.0, 0.0, 0.0))
            kg.spawn_tagged_mesh_actor(PLANE_ASSET, item["label"], location, scale=scale)
        else:
            sx, sy, sz = item["size_cm"]
            scale = (sx / PRIMITIVE_SIZE_CM, sy / PRIMITIVE_SIZE_CM, sz / PRIMITIVE_SIZE_CM)
            kg.spawn_tagged_mesh_actor(CUBE_ASSET, item["label"], item["location"], scale=scale)


def summarize(plan):
    counts = {}
    for item in plan:
        counts[item["kind"]] = counts.get(item["kind"], 0) + 1
    return counts


def main():
    layout = load_layout()
    plan = build_plan(layout)
    counts = summarize(plan)
    kg.log("blockout plan: %s (total %d actor(s))" % (counts, len(plan)))

    if kg.is_dry_run():
        for item in plan:
            kg.log("  [plan] %s (%s)" % (item["label"], item["kind"]))
        return

    apply_plan(plan)
    kg.log("blockout: spawned %d actor(s)" % len(plan))


if __name__ == "__main__":
    main()
