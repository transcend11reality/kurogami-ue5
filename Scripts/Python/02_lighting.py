"""Task A4: dusk lighting rig for the Brickell showpiece.

Spawns: one Directional Light (the dusk sun/moon), a Sky Atmosphere, a real-time-captured Sky
Light, Exponential Height Fog with Volumetric Fog enabled, an unbound Post Process Volume with
Lumen GI + reflections explicitly forced on, and a handful of KG_neon_* Rect Lights for accent.

Reads sun pitch/yaw/temperature and the brand palette from build_config.json. Those fields are
null placeholders until task A2 fills them in from the production plan's brand palette, so this
script falls back to documented dusk defaults (logged clearly) when a config value is missing,
the same graceful-degradation pattern as 01_blockout.py.

Everything is tagged KG_lighting_* / KG_neon_* and that set is cleared first (idempotent).

Run inside the editor:
    UnrealEditor-Cmd Kurogami.uproject -run=pythonscript -script="Scripts/Python/02_lighting.py" -unattended -nosplash

Dry-run (no engine, prints the plan and exits):
    python3 Scripts/Python/02_lighting.py --plan
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

LIGHT_TAG = "KG_lighting_"
NEON_TAG = "KG_neon_"

# Dusk defaults, used only when build_config.json's sun/palette fields are still the null
# placeholders from task A1 (task A2 fills them in from the production plan's brand palette).
DEFAULT_SUN = {"pitch_deg": -8.0, "yaw_deg": 200.0, "temperature_kelvin": 3200.0, "intensity_lux": 2.5}
# Neon signage reads as accent color, not the dark brand base (obsidian/navy/teal); pick these
# three palette keys by name, not "however many values happen to be first in the palette dict".
NEON_ACCENT_PALETTE_KEYS = ["cyan", "gold", "violet"]
DEFAULT_NEON_COLORS = ["#7FE9FF", "#F0C24A", "#8B5CF6"]  # cyan, gold, violet accents

# Brickell dusk neon accent placements: (label_suffix, location_cm, intensity_candela)
NEON_PLACEMENTS = [
    ("skyline_a", (300.0, 400.0, 4000.0), 5000.0),
    ("skyline_b", (900.0, 200.0, 6000.0), 5000.0),
    ("street_level", (100.0, 100.0, 500.0), 3000.0),
]


def hex_to_linear_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return (r, g, b)


def resolve_sun(config):
    sun = config.get("sun", {})
    resolved = {}
    used_default = False
    for key, default_value in DEFAULT_SUN.items():
        value = sun.get(key)
        if value is None:
            resolved[key] = default_value
            used_default = True
        else:
            resolved[key] = value
    if used_default:
        kg.log_warning(
            "build_config.json sun.* is not fully populated yet (task A2 fills it from the "
            "production plan); using documented dusk defaults: %s" % DEFAULT_SUN
        )
    return resolved


def resolve_neon_colors(config):
    palette = config.get("palette", {})
    colors = [palette[key] for key in NEON_ACCENT_PALETTE_KEYS if palette.get(key)]
    if len(colors) < len(NEON_ACCENT_PALETTE_KEYS):
        kg.log_warning(
            "build_config.json palette is missing one or more of %s (task A2 fills these in); "
            "using documented default accent colors: %s" % (NEON_ACCENT_PALETTE_KEYS, DEFAULT_NEON_COLORS)
        )
        colors = DEFAULT_NEON_COLORS
    return colors


def build_plan(config):
    sun = resolve_sun(config)
    neon_colors = resolve_neon_colors(config)
    plan = {
        "directional_light": {
            "label": LIGHT_TAG + "sun",
            "rotation": (sun["pitch_deg"], sun["yaw_deg"], 0.0),
            "temperature_kelvin": sun["temperature_kelvin"],
            "intensity_lux": sun["intensity_lux"],
        },
        "sky_atmosphere": {"label": LIGHT_TAG + "sky_atmosphere"},
        "sky_light": {"label": LIGHT_TAG + "sky_light"},
        "height_fog": {"label": LIGHT_TAG + "height_fog", "volumetric": True},
        "post_process": {"label": LIGHT_TAG + "post_process", "unbound": True,
                          "auto_exposure_bias": 0.5, "bloom_intensity": 0.6},
        "neon_lights": [],
    }
    for i, (suffix, location, intensity) in enumerate(NEON_PLACEMENTS):
        color = neon_colors[i % len(neon_colors)]
        plan["neon_lights"].append({
            "label": "%s%s" % (NEON_TAG, suffix),
            "location": location,
            "intensity_candela": intensity,
            "color_hex": color,
        })
    return plan


def apply_plan(plan):
    import unreal  # only reached inside the editor; guarded module import happens in ue_common

    kg.clear_tagged_actors(LIGHT_TAG)
    kg.clear_tagged_actors(NEON_TAG)

    # Directional light (the dusk sun).
    dl_plan = plan["directional_light"]
    sun_actor = kg.spawn_tagged_actor(unreal.DirectionalLight, dl_plan["label"], (0.0, 0.0, 0.0), dl_plan["rotation"])
    light_component = sun_actor.light_component
    light_component.set_editor_property("intensity", dl_plan["intensity_lux"])
    light_component.set_editor_property("use_temperature", True)
    light_component.set_editor_property("temperature", dl_plan["temperature_kelvin"])

    # Sky atmosphere (physically based sky).
    kg.spawn_tagged_actor(unreal.SkyAtmosphere, plan["sky_atmosphere"]["label"], (0.0, 0.0, 0.0))

    # Sky light, real-time captured so it reflects the atmosphere/scene without a manual recapture.
    sky_light_actor = kg.spawn_tagged_actor(unreal.SkyLight, plan["sky_light"]["label"], (0.0, 0.0, 0.0))
    sky_light_actor.light_component.set_editor_property("real_time_capture", True)

    # Exponential height fog with volumetric fog on for depth and god rays.
    fog_actor = kg.spawn_tagged_actor(unreal.ExponentialHeightFog, plan["height_fog"]["label"], (0.0, 0.0, 0.0))
    fog_component = fog_actor.component
    fog_component.set_editor_property("enable_volumetric_fog", True)

    # Unbound post-process volume forcing Lumen GI + reflections explicitly on, per CLAUDE.md.
    pp_plan = plan["post_process"]
    pp_actor = kg.spawn_tagged_actor(unreal.PostProcessVolume, pp_plan["label"], (0.0, 0.0, 0.0))
    pp_actor.set_editor_property("unbound", True)
    settings = pp_actor.settings
    settings.set_editor_property("override_auto_exposure_bias", True)
    settings.set_editor_property("auto_exposure_bias", pp_plan["auto_exposure_bias"])
    settings.set_editor_property("override_bloom_intensity", True)
    settings.set_editor_property("bloom_intensity", pp_plan["bloom_intensity"])
    settings.set_editor_property("override_dynamic_global_illumination_method", True)
    settings.set_editor_property("dynamic_global_illumination_method", unreal.DynamicGlobalIlluminationMethod.LUMEN)
    settings.set_editor_property("override_reflection_method", True)
    settings.set_editor_property("reflection_method", unreal.ReflectionMethod.LUMEN)
    pp_actor.set_editor_property("settings", settings)

    # Neon accent rect lights.
    for neon in plan["neon_lights"]:
        actor = kg.spawn_tagged_actor(unreal.RectLight, neon["label"], neon["location"])
        component = actor.light_component
        component.set_editor_property("intensity", neon["intensity_candela"])
        r, g, b = hex_to_linear_rgb(neon["color_hex"])
        component.set_editor_property("light_color", unreal.Color(int(r * 255), int(g * 255), int(b * 255), 255))


def main():
    config = kg.load_config()
    plan = build_plan(config)

    if kg.is_dry_run():
        kg.log("lighting plan:")
        kg.log("  directional_light: %s" % plan["directional_light"])
        kg.log("  sky_atmosphere: %s" % plan["sky_atmosphere"])
        kg.log("  sky_light: %s" % plan["sky_light"])
        kg.log("  height_fog: %s" % plan["height_fog"])
        kg.log("  post_process: %s" % plan["post_process"])
        for neon in plan["neon_lights"]:
            kg.log("  neon_light: %s" % neon)
        return

    apply_plan(plan)
    kg.log("lighting: rig applied (%d neon light(s))" % len(plan["neon_lights"]))


if __name__ == "__main__":
    main()
