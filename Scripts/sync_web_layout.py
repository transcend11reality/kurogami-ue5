"""Sync the web game's embedded layout data from Content/Data/brickell_layout.json.

Makes brickell_layout.json the single source of truth for both the UE5 blockout and the low-poly
web game (Scripts/Python/source/brickell-city.html), so "Brickell City Centre" sits at the exact
same place in both. Converts UE centimeters back to the web game's original meter-scale units
(divide by 100) and maps UE's Y axis back to the web game's Z axis (see brickell_layout.json's
own _source note for the original x100/axis-remap decision this reverses).

Only syncs the 7 real named landmarks (matching NAME_MAP below), not brickell_layout.json's two
"annex" satellite towers: those are intentionally NOT independent landmarks in the web game, they
are a special-cased pair of decorative buildings rendered at a relative offset from Brickell City
Centre inside buildLandmarks(), with no label or interaction prompt of their own. Syncing them as
LM entries would incorrectly give them a floating name label and an "examine" prompt they were
never meant to have.

Replaces the content between the <!-- KUROGAMI_LAYOUT_DATA_START --> / _END markers in the target
HTML file; the JS reads that embedded JSON at load time instead of a second hardcoded copy of the
same numbers.

Usage:
    python3 Scripts/sync_web_layout.py [--target /path/to/brickell-city.html]
"""
import argparse
import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_LAYOUT_PATH = os.path.join(REPO_ROOT, "Content", "Data", "brickell_layout.json")
DEFAULT_TARGET_PATH = os.path.join(REPO_ROOT, "Scripts", "Python", "source", "brickell-city.html")

START_MARKER = "<!-- KUROGAMI_LAYOUT_DATA_START -->"
END_MARKER = "<!-- KUROGAMI_LAYOUT_DATA_END -->"

# Only these 7 are real named landmarks in the web game; brickell_city_centre_annex_a/b are
# intentionally excluded (see module docstring).
NAME_MAP = {
    "brickell_city_centre": "Brickell City Centre",
    "mary_brickell_village": "Mary Brickell Village",
    "four_seasons_miami": "Four Seasons Miami",
    "dua_miami": "Dua Miami",
    "brickell_metrorail": "Brickell Metrorail",
    "simpson_park": "Simpson Park",
    "brickell_ave_bridge": "Brickell Ave Bridge",
}


def build_web_scale_landmarks(layout):
    result = []
    for b in layout.get("buildings", []):
        if b["id"] not in NAME_MAP:
            continue
        result.append({
            "name": NAME_MAP[b["id"]], "x": b["x"] / 100.0, "z": b["y"] / 100.0,
            "h": b["height"] / 100.0, "kind": b["kind"], "note": b["note"],
        })
    for b in layout.get("landmarks_without_geometry", []):
        if b["id"] not in NAME_MAP:
            continue
        result.append({
            "name": NAME_MAP[b["id"]], "x": b["x"] / 100.0, "z": b["y"] / 100.0,
            "h": 0, "kind": b["kind"], "note": b["note"],
        })
    return result


def build_web_scale_roads(layout):
    xs = sorted(set(
        r["polyline"][0][0] / 100.0 for r in layout.get("roads", []) if r["id"].startswith("ns_")
    ))
    return xs


def sync(layout_path, target_path):
    with open(layout_path, "r") as f:
        layout = json.load(f)

    landmarks = build_web_scale_landmarks(layout)
    roads = build_web_scale_roads(layout)

    if len(landmarks) != len(NAME_MAP):
        missing = set(NAME_MAP) - {
            k for k, v in NAME_MAP.items()
            if any(l["name"] == v for l in landmarks)
        }
        raise SystemExit("sync_web_layout: missing expected landmark(s) in layout JSON: %s" % missing)

    payload = json.dumps({"landmarks": landmarks, "roads": roads}, indent=2)
    block = "%s\n<script id=\"kurogami-layout-data\" type=\"application/json\">\n%s\n</script>\n%s" % (
        START_MARKER, payload, END_MARKER
    )

    with open(target_path, "r") as f:
        html = f.read()

    if START_MARKER not in html or END_MARKER not in html:
        raise SystemExit(
            "sync_web_layout: markers not found in %s; run this after the one-time JS refactor "
            "that adds the KUROGAMI_LAYOUT_DATA markers and reads from them" % target_path
        )

    start = html.index(START_MARKER)
    end = html.index(END_MARKER) + len(END_MARKER)
    new_html = html[:start] + block + html[end:]

    with open(target_path, "w") as f:
        f.write(new_html)

    print("sync_web_layout: synced %d landmark(s), %d road(s) into %s" % (
        len(landmarks), len(roads), target_path
    ))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layout", default=DEFAULT_LAYOUT_PATH)
    parser.add_argument("--target", default=DEFAULT_TARGET_PATH)
    args = parser.parse_args()
    sync(args.layout, args.target)


if __name__ == "__main__":
    main()
