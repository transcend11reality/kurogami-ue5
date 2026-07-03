# Kurogami Brickell Dusk: Master Materials Recipe

Six master materials for the showpiece environment. Build these by hand in the Unreal material
editor (Content Browser > Add > Material, name exactly as given). `Scripts/Python/03_materials.py`
then creates a brand-tinted Material Instance Constant per master material and sets these same
parameter names automatically, once the master exists, so the PARAMETER NAMES below must match
exactly what the script expects.

Brand palette reference (fill the actual hex values into `Scripts/Python/build_config.json`'s
`palette` block as part of task A2; these are the production plan's named colors): obsidian, navy,
teal, gold, violet, crimson, cyan.

All six should be Lumen-compatible: default Shading Model (Default Lit) unless noted, no legacy
Screen Space Reflections dependency, since Lumen reflections are forced on in `02_lighting.py`'s
Post Process Volume.

---

## M_Glass

Lumen-reflective glass for tower facades.

- **Shading Model:** Default Lit. **Blend Mode:** Translucent.
- Graph: a `Fresnel` node feeds the alpha/opacity for a subtle edge highlight; a `VectorParameter`
  named `TintColor` multiplies a near-black base color (glass reads mostly through reflection, not
  albedo). A `ScalarParameter` named `Roughness` (default 0.05) drives the Roughness pin directly.
  A `ScalarParameter` named `Metallic` (default 0.0, glass is dielectric) and a `ScalarParameter`
  named `IOR` (default 1.52, standard architectural glass) feed a `Refraction` pin if using
  refraction, otherwise leave IOR informational for a future refractive pass.
- Enable **Lumen reflections** by leaving Two Sided off and using a reasonably high Roughness
  contrast so Lumen's reflection captures read the glass distinctly from concrete/metal neighbors.

## M_WetAsphalt

Reflective dark street surface.

- **Shading Model:** Default Lit. **Blend Mode:** Opaque.
- Graph: a base asphalt `Texture Sample` (Fab/Megascans asphalt scan, tiled via a `TexCoord` with a
  `Multiply` for tiling scale) multiplied by a `VectorParameter` named `TintColor` (default near-
  black, obsidian). A `ScalarParameter` named `PuddleAmount` (default 0.4) lerps between a high-
  Roughness dry asphalt Roughness value and a near-zero wet/puddle Roughness value using a noise
  or puddle mask texture, so the street reads wet and reflective under the neon per the plan's
  "wet reflective streets" hero look. A `ScalarParameter` named `Roughness` sets the dry baseline
  (default 0.15, already fairly glossy) and a fixed `Metallic` of 0.0.

## M_Metal

Brushed metal for structural and set-dressing elements.

- **Shading Model:** Default Lit. **Blend Mode:** Opaque.
- Graph: a brushed-metal normal map (Fab scan) into the Normal pin; a `VectorParameter` named
  `TintColor` (default navy) into Base Color; a `ScalarParameter` named `Roughness` (default 0.25)
  and `ScalarParameter` named `Metallic` (default 1.0, fully metallic) direct into their pins.

## M_Concrete

Building facades, sidewalks, structural mass.

- **Shading Model:** Default Lit. **Blend Mode:** Opaque.
- Graph: a concrete albedo + normal + roughness texture set (Fab scan) with a `VectorParameter`
  named `TintColor` (default obsidian, matching the deep navy/obsidian brand base) multiplying the
  albedo. `ScalarParameter` named `Roughness` (default 0.8, matte) and fixed `Metallic` of 0.0.

## M_NeonEmissive

Signage, accent strips, kanji signage per the brand.

- **Shading Model:** Default Lit (Unlit is acceptable if bloom alone should carry the look).
  **Blend Mode:** Opaque.
- Graph: a `VectorParameter` named `EmissiveColor` (no default; instances set gold/cyan/violet per
  `03_materials.py`) multiplied by a `ScalarParameter` named `EmissiveIntensity` (default 12.0,
  tuned against the Post Process Volume's Bloom Intensity of 0.6 from `02_lighting.py`, so the
  neon blooms convincingly without blowing out) feeding the Emissive Color pin. Base Color stays a
  near-black so the material reads as "off" until Emissive carries it, consistent with real neon
  signage.

## M_Water

Bay/harbor water for the Brickell waterfront.

- **Shading Model:** Default Lit. **Blend Mode:** Opaque (use the UE Water plugin's water body
  material system for the actual bay if using that plugin instead of this flat material; this
  recipe covers a simpler custom water material if not).
- Graph: a `VectorParameter` named `TintColor` (default teal) as the base color/absorption tint. A
  `ScalarParameter` named `Roughness` (default 0.02, near-mirror) for reflections. A
  `ScalarParameter` named `WaveAmount` (default 0.3) drives a `Panner`-fed normal map distortion for
  subtle animated ripples, keeping the scene "alive" per the production plan's set-dressing motion
  goal even before gameplay exists.

---

## What the script does once these exist

`Scripts/Python/03_materials.py` creates one Material Instance Constant per master material under
`/Game/Materials/Instances/` (two for M_NeonEmissive: gold and cyan variants), sets the scalar and
vector parameters above from `build_config.json`'s palette, and saves them. Run it after these six
masters exist; it logs a clear warning and skips any instance whose parent master is still missing,
so it is safe to run early and re-run as masters get added one at a time.
