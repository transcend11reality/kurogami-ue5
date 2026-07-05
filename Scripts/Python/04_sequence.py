"""Task A6: Sequencer cinematic camera move for the Brickell showpiece.

Creates (or recreates, for idempotency) a Level Sequence at /Game/Cinematics/KG_Showpiece with one
CineCameraActor possessable, a keyframed 3D Transform track moving it through the vantage points in
build_config.json (establishing wide, hero push-ins, slow reveal), and a Camera Cuts track bound to
that camera spanning the whole sequence.

build_config.json's camera_vantage_points is an empty list until task A2 fills it in from the
production plan, so this script falls back to a documented default 3-point move (0s / 40s / 90s,
inside the plan's 60-120s target) when the config list is empty, same graceful-degradation pattern
as the other build scripts.

Scope note (honest, not overclaimed): only the camera's Transform (location/rotation) is keyframed
here, since that is the well-defined, confirmed part of the Sequencer scripting API. Focal length is
set once (from the first vantage point) as a static CineCameraComponent property, and depth of field
(aperture + focus distance) is likewise set once as a reasonable dusk-cinematic default. Per-keyframe
focal length racking and DoF timing are camera POLISH, reserved for the human pass in task B3
("Lighting + camera polish"), not fabricated here.

Idempotent: deletes and recreates the KG_Showpiece sequence asset on every run (task A6 itself calls
this out as the correct idempotency strategy for a sequence, unlike the level-actor tag-clearing used
by 01_blockout.py / 02_lighting.py).

Run inside the editor:
    UnrealEditor-Cmd Kurogami.uproject -run=pythonscript -script="Scripts/Python/04_sequence.py" -unattended -nosplash

Dry-run (no engine, prints the keyframe timeline and exits):
    python3 Scripts/Python/04_sequence.py --plan
"""
import os
import sys

try:
    _SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # __file__ is undefined when a script is run via exec(open(...).read()) in the
    # in-editor Python console, instead of as a real file (the -script= CLI flag or
    # standalone python3 both set __file__ correctly). Fall back to the project dir.
    import unreal
    _SCRIPT_DIR = os.path.join(unreal.Paths.project_dir(), "Scripts", "Python")
sys.path.insert(0, _SCRIPT_DIR)
import ue_common as kg

SEQUENCE_PACKAGE_PATH = "/Game/Cinematics"
SEQUENCE_NAME = "KG_Showpiece"
FRAME_RATE_FPS = 30

# Dusk cinematic defaults, used only when build_config.json's camera_vantage_points is still the
# empty-list placeholder from task A1 (task A2 fills it in from the production plan).
DEFAULT_VANTAGE_POINTS = [
    {"name": "establishing_wide", "time_sec": 0.0, "location": (-2000.0, -3000.0, 1200.0),
     "rotation": (-5.0, 45.0, 0.0), "focal_length_mm": 24.0},
    {"name": "hero_push_in", "time_sec": 40.0, "location": (500.0, 800.0, 2000.0),
     "rotation": (-10.0, 210.0, 0.0), "focal_length_mm": 50.0},
    {"name": "slow_reveal", "time_sec": 90.0, "location": (1500.0, 200.0, 800.0),
     "rotation": (0.0, 270.0, 0.0), "focal_length_mm": 35.0},
]

DOF_APERTURE_FSTOP = 2.8
DOF_FOCUS_DISTANCE_CM = 5000.0


def resolve_vantage_points(config):
    vantages = config.get("camera_vantage_points") or []
    if not vantages:
        kg.log_warning(
            "build_config.json camera_vantage_points is empty (task A2 fills it in from the "
            "production plan); using a documented default 3-point dusk move (0s/40s/90s)"
        )
        vantages = DEFAULT_VANTAGE_POINTS
    return vantages


def build_plan(config):
    vantages = resolve_vantage_points(config)
    duration_sec = vantages[-1]["time_sec"]
    return {
        "sequence_path": "%s/%s.%s" % (SEQUENCE_PACKAGE_PATH, SEQUENCE_NAME, SEQUENCE_NAME),
        "frame_rate_fps": FRAME_RATE_FPS,
        "duration_sec": duration_sec,
        "dof": {"aperture_fstop": DOF_APERTURE_FSTOP, "focus_distance_cm": DOF_FOCUS_DISTANCE_CM},
        "vantage_points": vantages,
    }


def apply_plan(plan):
    import unreal  # only reached inside the editor

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    full_path = plan["sequence_path"]

    if unreal.EditorAssetLibrary.does_asset_exist(full_path):
        unreal.EditorAssetLibrary.delete_asset(full_path)

    sequence = asset_tools.create_asset(
        SEQUENCE_NAME, SEQUENCE_PACKAGE_PATH, unreal.LevelSequence, unreal.LevelSequenceFactoryNew()
    )
    sequence.set_display_rate(unreal.FrameRate(plan["frame_rate_fps"], 1))
    total_frames = int(plan["duration_sec"] * plan["frame_rate_fps"])
    sequence.set_playback_start(0)
    sequence.set_playback_end(total_frames)

    first = plan["vantage_points"][0]
    camera_actor = kg.spawn_tagged_actor(
        unreal.CineCameraActor, "KG_sequence_camera", first["location"], first["rotation"]
    )
    camera_component = camera_actor.get_component_by_class(unreal.CineCameraComponent)
    camera_component.set_editor_property("current_focal_length", first["focal_length_mm"])
    camera_component.set_editor_property("current_aperture", plan["dof"]["aperture_fstop"])
    focus_settings = camera_component.focus_settings
    focus_settings.set_editor_property("manual_focus_distance", plan["dof"]["focus_distance_cm"])
    camera_component.set_editor_property("focus_settings", focus_settings)

    camera_binding = sequence.add_possessable(camera_actor)

    # Keyframe the camera move (location + rotation) across the vantage points.
    transform_track = camera_binding.add_track(unreal.MovieScene3DTransformTrack)
    transform_section = transform_track.add_section()
    transform_section.set_range_seconds(0.0, plan["duration_sec"])
    channels = {c.channel_name: c for c in transform_section.get_all_channels()}

    axis_map = {
        "Location.X": lambda v: v["location"][0], "Location.Y": lambda v: v["location"][1],
        "Location.Z": lambda v: v["location"][2], "Rotation.X": lambda v: v["rotation"][2],
        "Rotation.Y": lambda v: v["rotation"][0], "Rotation.Z": lambda v: v["rotation"][1],
    }
    for vantage in plan["vantage_points"]:
        frame = unreal.FrameNumber(int(vantage["time_sec"] * plan["frame_rate_fps"]))
        for channel_name, getter in axis_map.items():
            channel = channels.get(channel_name)
            if channel is not None:
                channel.add_key(time=frame, new_value=getter(vantage))

    # Camera cut track bound to the possessed camera, spanning the whole sequence.
    cut_track = sequence.add_track(unreal.MovieSceneCameraCutTrack)
    cut_section = cut_track.add_section()
    cut_section.set_range_seconds(0.0, plan["duration_sec"])
    binding_guid = unreal.MovieSceneBindingExtensions.get_id(camera_binding)
    binding_id = unreal.MovieSceneObjectBindingID()
    binding_id.set_editor_property("guid", binding_guid)
    cut_section.set_editor_property("camera_binding_id", binding_id)

    unreal.EditorAssetLibrary.save_loaded_asset(sequence)
    kg.log("sequence: %s created, %d vantage point(s), %.1fs" % (
        full_path, len(plan["vantage_points"]), plan["duration_sec"]
    ))


def main():
    config = kg.load_config()
    plan = build_plan(config)

    if kg.is_dry_run():
        kg.log("sequence plan: %s (%.1fs @ %d fps, DoF=%s)" % (
            plan["sequence_path"], plan["duration_sec"], plan["frame_rate_fps"], plan["dof"]
        ))
        for vantage in plan["vantage_points"]:
            kg.log("  [plan] t=%5.1fs  %-18s location=%s rotation=%s focal_length_mm=%s" % (
                vantage["time_sec"], vantage["name"], vantage["location"],
                vantage["rotation"], vantage["focal_length_mm"]
            ))
        return

    apply_plan(plan)


if __name__ == "__main__":
    main()
