"""Fixture-based idempotency test for Scripts/merge_config.py (task A8's Verify step).

Copies fixture_default_engine.ini to a temp file, which already has an unrelated key in the
[/Script/Engine.RendererSettings] section and a section the additions file does not mention, then
runs the merge twice. Asserts: the second run produces byte-identical output to the first (no
section or key gets duplicated by a repeat run), the pre-existing unrelated key and section survive
untouched, the additions' new keys are present, and a section whose additions content is entirely
commented out ([SystemSettings], see Config/DefaultEngine.ini.additions.txt) is never created since
it has zero real keys to contribute.

Usage: python3 Scripts/tests/test_merge_config.py
"""
import os
import shutil
import sys
import tempfile

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS_DIR = os.path.dirname(_THIS_DIR)
_REPO_ROOT = os.path.dirname(_SCRIPTS_DIR)

sys.path.insert(0, _SCRIPTS_DIR)
import merge_config

FIXTURE_PATH = os.path.join(_THIS_DIR, "fixture_default_engine.ini")
ADDITIONS_PATH = os.path.join(_REPO_ROOT, "Config", "DefaultEngine.ini.additions.txt")


def run():
    with tempfile.TemporaryDirectory() as tmp_dir:
        target = os.path.join(tmp_dir, "DefaultEngine.ini")
        shutil.copy(FIXTURE_PATH, target)

        merge_config.merge_config(ADDITIONS_PATH, target)
        with open(target, "r") as f:
            first_pass = f.read()

        merge_config.merge_config(ADDITIONS_PATH, target)
        with open(target, "r") as f:
            second_pass = f.read()

        assert first_pass == second_pass, "second merge run changed the file; not idempotent"
        assert first_pass.count("[/Script/Engine.RendererSettings]") == 1, "section header duplicated"
        assert first_pass.count("[SystemSettings]") == 0, (
            "SystemSettings has zero real keys in the additions file (all commented out); "
            "it must not be created"
        )
        assert "r.SomeOtherSetting=1" in first_pass, "pre-existing unrelated key was lost"
        assert "GameDefaultMap=/Game/Maps/Placeholder" in first_pass, "pre-existing section was lost"
        assert "r.DynamicGlobalIlluminationMethod=1" in first_pass, "new key was not merged in"
        assert "r.Nanite=1" in first_pass, "new key was not merged in"

    print("test_merge_config: PASS")


if __name__ == "__main__":
    try:
        run()
    except AssertionError as e:
        print("test_merge_config: FAIL - %s" % e)
        sys.exit(1)
