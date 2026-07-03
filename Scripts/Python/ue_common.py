"""Shared helpers for Kurogami UE5 build scripts.

Import this from every numbered build script (01_blockout.py, 02_lighting.py, ...).
Works two ways:
  1. Inside the UE Editor's embedded Python interpreter, where the `unreal` module is real.
  2. Under plain `python3` outside the editor, for --plan/--dry-run verification with no engine
     running. `unreal` is unimportable there, so it is guarded and every call degrades to a
     logged no-op instead of raising.
"""
import json
import os
import sys

try:
    import unreal
    HAS_UNREAL = True
except ImportError:
    unreal = None
    HAS_UNREAL = False

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS_DIR))
CONFIG_PATH = os.path.join(_THIS_DIR, "build_config.json")


def repo_path(*parts):
    """Join path parts onto the repo root (the folder containing Kurogami.uproject)."""
    return os.path.join(REPO_ROOT, *parts)


def log(message):
    if HAS_UNREAL:
        unreal.log(message)
    else:
        print(message)


def log_warning(message):
    if HAS_UNREAL:
        unreal.log_warning(message)
    else:
        print("WARNING: " + message)


def load_config(path=CONFIG_PATH):
    with open(path, "r") as f:
        return json.load(f)


def is_dry_run(argv=None):
    """True when running outside the editor, or when --plan/--dry-run is passed explicitly."""
    argv = argv if argv is not None else sys.argv
    return (not HAS_UNREAL) or ("--plan" in argv) or ("--dry-run" in argv)


def clear_tagged_actors(prefix):
    """Delete every actor in the current level whose label starts with prefix.

    Call this before spawning a KG_* actor set so re-running a build script does not duplicate
    the world. No-op (logged) outside the editor.
    """
    if not HAS_UNREAL:
        log("clear_tagged_actors(%s): skipped, no unreal module (dry-run)" % prefix)
        return 0
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    removed = 0
    for actor in actor_subsystem.get_all_level_actors():
        if actor.get_actor_label().startswith(prefix):
            actor_subsystem.destroy_actor(actor)
            removed += 1
    log("clear_tagged_actors(%s): removed %d actor(s)" % (prefix, removed))
    return removed


def spawn_tagged_actor(actor_class, label, location, rotation=(0.0, 0.0, 0.0)):
    """Spawn an actor of actor_class (a Blueprint or native Class, e.g. unreal.DirectionalLight,
    unreal.CineCameraActor) at location/rotation and label it so clear_tagged_actors can find it
    later. location and rotation are 3-tuples. Returns the spawned actor, or None in dry-run mode.
    """
    if not HAS_UNREAL:
        log("spawn_tagged_actor(%s @ %s): skipped, no unreal module (dry-run)" % (label, location))
        return None
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    loc = unreal.Vector(location[0], location[1], location[2])
    rot = unreal.Rotator(rotation[0], rotation[1], rotation[2])
    actor = actor_subsystem.spawn_actor_from_class(actor_class, loc, rot)
    actor.set_actor_label(label, True)
    return actor


def spawn_tagged_mesh_actor(asset_path, label, location, rotation=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0)):
    """Load a StaticMesh (or other Factory/Archetype/Asset) at asset_path and spawn it as an actor
    with the mesh already assigned, via EditorActorSubsystem.spawn_actor_from_object. Use this for
    static meshes (asset_path like '/Engine/BasicShapes/Cube.Cube'); use spawn_tagged_actor for
    native/Blueprint actor classes instead. Returns the spawned actor, or None in dry-run mode.
    """
    if not HAS_UNREAL:
        log("spawn_tagged_mesh_actor(%s @ %s): skipped, no unreal module (dry-run)" % (label, location))
        return None
    obj = unreal.EditorAssetLibrary.load_asset(asset_path)
    if obj is None:
        log_warning("spawn_tagged_mesh_actor(%s): could not load asset %s" % (label, asset_path))
        return None
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    loc = unreal.Vector(location[0], location[1], location[2])
    rot = unreal.Rotator(rotation[0], rotation[1], rotation[2])
    actor = actor_subsystem.spawn_actor_from_object(obj, loc, rot)
    actor.set_actor_label(label, True)
    actor.set_actor_scale3d(unreal.Vector(scale[0], scale[1], scale[2]))
    return actor
