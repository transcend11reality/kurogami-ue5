"""Task A8: idempotently merge Config/DefaultEngine.ini.additions.txt into the UE project's real
Config/DefaultEngine.ini, and make sure the Python/MRQ plugins are marked enabled in
Kurogami.uproject.

Pure text/JSON processing, no `unreal` module needed (this can run standalone with plain python3,
before or after the UE project exists).

Never duplicates a section or a key: if a section already exists in the target, only keys missing
from it are appended; if a section is entirely new, it is appended as a whole block at EOF. Running
this script any number of times converges to the same file (see Scripts/tests/ for the fixture-based
idempotency test backing task A8's Verify step).

If Kurogami.uproject does not exist yet (task G0 not done), the plugin-enabling step is skipped with
a clear log message rather than failing, since this script must also be runnable, and be verified,
before the UE project exists.

Usage:
    python3 Scripts/merge_config.py [--target /path/to/DefaultEngine.ini] [--uproject /path/to/Kurogami.uproject]

With no arguments, targets this repo's real Config/DefaultEngine.ini and Kurogami.uproject.
"""
import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ADDITIONS_PATH = os.path.join(REPO_ROOT, "Config", "DefaultEngine.ini.additions.txt")
DEFAULT_TARGET_PATH = os.path.join(REPO_ROOT, "Config", "DefaultEngine.ini")
DEFAULT_UPROJECT_PATH = os.path.join(REPO_ROOT, "Kurogami.uproject")

REQUIRED_PLUGINS = [
    "PythonScriptPlugin",
    "EditorScriptingUtilities",
    "MovieRenderPipeline",
    "MovieRenderPipelineAdditionalRenderPasses",
]


def parse_additions(path):
    """Parse an additions ini file into {section_header: {key: value}}, in file order, skipping
    comment-only and blank lines. A section with zero real key=value pairs is dropped entirely
    (for example a section that is currently only commented-out example keys)."""
    sections = {}
    current = None
    with open(path, "r") as f:
        for raw_line in f:
            stripped = raw_line.strip()
            if not stripped or stripped.startswith(";") or stripped.startswith("#"):
                continue
            if stripped.startswith("[") and stripped.endswith("]"):
                current = stripped
                sections.setdefault(current, {})
                continue
            if current is None or "=" not in stripped:
                continue
            key_part, _, rest = stripped.partition("=")
            key = key_part.strip()
            value = rest.split(";")[0].strip()  # drop a trailing inline "; comment"
            if key:
                sections[current][key] = value
    return {section: kv for section, kv in sections.items() if kv}


def scan_target_sections(lines):
    """Scan target ini lines into {section_header: {"header_line": i, "keys": {key: line_idx}}}."""
    scan = {}
    current = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current = stripped
            scan.setdefault(current, {"header_line": i, "keys": {}})
            continue
        if current and "=" in stripped and not stripped.startswith((";", "#")):
            key = stripped.split("=", 1)[0].strip()
            scan[current]["keys"][key] = i
    return scan


def merge_lines(lines, additions):
    """Apply one additions-section's missing keys per pass, rescanning after each pass so line
    index shifts from a prior insertion never go stale. Returns (lines, sections_created, keys_added)."""
    sections_created = 0
    keys_added = 0
    pending = dict(additions)

    while pending:
        section, kv = next(iter(pending.items()))
        del pending[section]

        scan = scan_target_sections(lines)
        if section not in scan:
            if lines and not lines[-1].endswith("\n"):
                lines[-1] = lines[-1] + "\n"
            if lines:
                lines.append("\n")
            lines.append(section + "\n")
            for key, value in kv.items():
                lines.append("%s=%s\n" % (key, value))
            sections_created += 1
            keys_added += len(kv)
            continue

        existing_keys = scan[section]["keys"]
        missing = {k: v for k, v in kv.items() if k not in existing_keys}
        if not missing:
            continue

        insert_at = (max(existing_keys.values()) + 1) if existing_keys else (scan[section]["header_line"] + 1)
        new_lines = ["%s=%s\n" % (k, v) for k, v in missing.items()]
        lines[insert_at:insert_at] = new_lines
        keys_added += len(missing)

    return lines, sections_created, keys_added


def merge_config(additions_path, target_path):
    additions = parse_additions(additions_path)
    lines = []
    if os.path.isfile(target_path):
        with open(target_path, "r") as f:
            lines = f.readlines()

    lines, sections_created, keys_added = merge_lines(lines, additions)

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w") as f:
        f.writelines(lines)

    print("merge_config: %s section(s) created, %s key(s) added into %s" % (
        sections_created, keys_added, target_path
    ))
    return sections_created, keys_added


def ensure_plugins_enabled(uproject_path):
    if not os.path.isfile(uproject_path):
        print("merge_config: %s not found (task G0 not done yet); skipping plugin check" % uproject_path)
        return 0

    with open(uproject_path, "r") as f:
        data = json.load(f)

    plugins = data.setdefault("Plugins", [])
    existing_names = {p.get("Name") for p in plugins}
    added = 0
    for name in REQUIRED_PLUGINS:
        if name in existing_names:
            for p in plugins:
                if p.get("Name") == name and not p.get("Enabled", False):
                    p["Enabled"] = True
                    added += 1
        else:
            plugins.append({"Name": name, "Enabled": True})
            added += 1

    if added:
        with open(uproject_path, "w") as f:
            json.dump(data, f, indent="\t")
            f.write("\n")
        print("merge_config: %d plugin entrie(s) added/enabled in %s" % (added, uproject_path))
    else:
        print("merge_config: all required plugins already enabled in %s" % uproject_path)
    return added


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--additions", default=DEFAULT_ADDITIONS_PATH)
    parser.add_argument("--target", default=DEFAULT_TARGET_PATH)
    parser.add_argument("--uproject", default=DEFAULT_UPROJECT_PATH)
    args = parser.parse_args()

    merge_config(args.additions, args.target)
    ensure_plugins_enabled(args.uproject)


if __name__ == "__main__":
    main()
