"""Task A5 (script half): brand material INSTANCES for the Brickell showpiece.

Building a full material node graph via Python is verbose and brittle (MaterialEditingLibrary
node-by-node placement), so the master materials themselves (M_Glass, M_WetAsphalt, M_Metal,
M_Concrete, M_NeonEmissive, M_Water) are hand-built in the editor by a human per the node graph in
docs/MATERIALS_RECIPE.md (task B1/B2). What Python CAN do reliably is create a Material Instance
Constant per master material and set its brand-color/roughness/metallic/emissive parameters from
build_config.json's palette, which is exactly what this script does.

If a master material does not exist yet (the human has not built it per the recipe), this script
logs a warning and skips that one instance instead of failing the whole run, the same
graceful-degradation pattern as 01_blockout.py and 02_lighting.py.

Idempotent: re-running updates the existing instance's parameters in place rather than duplicating
it (material instances live in /Game/Materials/Instances/, not the level, so there is no KG_ actor
tag to clear; identity is the asset path itself).

Run inside the editor:
    UnrealEditor-Cmd Kurogami.uproject -run=pythonscript -script="Scripts/Python/03_materials.py" -unattended -nosplash

Dry-run (no engine, prints the plan and exits):
    python3 Scripts/Python/03_materials.py --plan
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ue_common as kg

INSTANCE_PACKAGE_PATH = "/Game/Materials/Instances"

# Six master materials from the recipe doc, each parameterized per the brand look. Palette keys
# reference build_config.json's palette dict; a literal default hex is used if that key is still
# a null placeholder (task A2 fills the palette in from the production plan).
DEFAULT_PALETTE = {
    "obsidian": "#0B0E14", "navy": "#111827", "teal": "#1FB6A8",
    "gold": "#F0C24A", "violet": "#8B5CF6", "crimson": "#DC2626", "cyan": "#7FE9FF",
}

MATERIAL_SPECS = [
    {
        "parent_path": "/Game/Materials/M_Glass.M_Glass",
        "instance_name": "MI_Glass_Brickell",
        "scalar": {"Roughness": 0.05, "Metallic": 0.0, "IOR": 1.52},
        "vector": {"TintColor": "cyan"},
    },
    {
        "parent_path": "/Game/Materials/M_WetAsphalt.M_WetAsphalt",
        "instance_name": "MI_WetAsphalt_Brickell",
        "scalar": {"Roughness": 0.15, "Metallic": 0.0, "PuddleAmount": 0.4},
        "vector": {"TintColor": "obsidian"},
    },
    {
        "parent_path": "/Game/Materials/M_Metal.M_Metal",
        "instance_name": "MI_Metal_Brickell",
        "scalar": {"Roughness": 0.25, "Metallic": 1.0},
        "vector": {"TintColor": "navy"},
    },
    {
        "parent_path": "/Game/Materials/M_Concrete.M_Concrete",
        "instance_name": "MI_Concrete_Brickell",
        "scalar": {"Roughness": 0.8, "Metallic": 0.0},
        "vector": {"TintColor": "obsidian"},
    },
    {
        "parent_path": "/Game/Materials/M_NeonEmissive.M_NeonEmissive",
        "instance_name": "MI_NeonEmissive_Gold",
        "scalar": {"EmissiveIntensity": 12.0},
        "vector": {"EmissiveColor": "gold"},
    },
    {
        "parent_path": "/Game/Materials/M_NeonEmissive.M_NeonEmissive",
        "instance_name": "MI_NeonEmissive_Cyan",
        "scalar": {"EmissiveIntensity": 12.0},
        "vector": {"EmissiveColor": "cyan"},
    },
    {
        "parent_path": "/Game/Materials/M_Water.M_Water",
        "instance_name": "MI_Water_Brickell",
        "scalar": {"Roughness": 0.02, "WaveAmount": 0.3},
        "vector": {"TintColor": "teal"},
    },
]


def hex_to_linear_color(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return (r, g, b, 1.0)


def resolve_palette(config):
    palette = config.get("palette", {})
    resolved = {}
    used_default = False
    for key, default_hex in DEFAULT_PALETTE.items():
        value = palette.get(key)
        if value is None:
            resolved[key] = default_hex
            used_default = True
        else:
            resolved[key] = value
    if used_default:
        kg.log_warning(
            "build_config.json palette is not fully populated yet (task A2 fills it in); "
            "using documented default brand hex values where missing"
        )
    return resolved


def build_plan(config):
    palette = resolve_palette(config)
    plan = []
    for spec in MATERIAL_SPECS:
        vector_params = {name: (palette_key, palette[palette_key]) for name, palette_key in spec["vector"].items()}
        plan.append({
            "parent_path": spec["parent_path"],
            "instance_path": "%s/%s.%s" % (INSTANCE_PACKAGE_PATH, spec["instance_name"], spec["instance_name"]),
            "instance_name": spec["instance_name"],
            "scalar": spec["scalar"],
            "vector": vector_params,
        })
    return plan


def apply_plan(plan):
    import unreal  # only reached inside the editor

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    created, updated, skipped = 0, 0, 0

    for item in plan:
        if not unreal.EditorAssetLibrary.does_asset_exist(item["parent_path"]):
            kg.log_warning(
                "skipping %s: parent material %s does not exist yet (build it in the editor per "
                "docs/MATERIALS_RECIPE.md, task B1/B2)" % (item["instance_name"], item["parent_path"])
            )
            skipped += 1
            continue

        parent = unreal.EditorAssetLibrary.load_asset(item["parent_path"])

        if unreal.EditorAssetLibrary.does_asset_exist(item["instance_path"]):
            instance = unreal.EditorAssetLibrary.load_asset(item["instance_path"])
            updated += 1
        else:
            factory = unreal.MaterialInstanceConstantFactoryNew()
            instance = asset_tools.create_asset(
                item["instance_name"], INSTANCE_PACKAGE_PATH, unreal.MaterialInstanceConstant, factory
            )
            created += 1

        unreal.MaterialEditingLibrary.set_material_instance_parent(instance, parent)
        for param_name, value in item["scalar"].items():
            unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(instance, param_name, value)
        for param_name, (palette_key, hex_value) in item["vector"].items():
            r, g, b, a = hex_to_linear_color(hex_value)
            unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
                instance, param_name, unreal.LinearColor(r, g, b, a)
            )
        unreal.EditorAssetLibrary.save_loaded_asset(instance)

    kg.log("materials: %d created, %d updated, %d skipped (missing parent)" % (created, updated, skipped))


def main():
    config = kg.load_config()
    plan = build_plan(config)

    if kg.is_dry_run():
        kg.log("materials plan (%d instance(s)):" % len(plan))
        for item in plan:
            kg.log("  %s <- %s | scalar=%s vector=%s" % (
                item["instance_name"], item["parent_path"], item["scalar"], item["vector"]
            ))
        return

    apply_plan(plan)


if __name__ == "__main__":
    main()
