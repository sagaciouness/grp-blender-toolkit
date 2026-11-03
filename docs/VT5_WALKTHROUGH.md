I don't know if these translations are accurate。 Original text: ZHCN

### Scope

This is a **reference extraction workflow**, not a one-click conversion of a complete playable tank. The importer creates named Blender Empties with the node hierarchy and rest transforms, plus rigid meshes parented to their corresponding nodes. It does not restore a deforming Armature, skin weights, animation controllers, textures/material assignments, armour values or damage behaviour.

### Setup and extraction

1. Install Windows x64 Python 3.11, Blender and War Thunder CDK separately.
2. Download the [Dagor Asset Explorer source](https://github.com/quentin-dh/Dagor-Asset-Explorer). Locate its `src/dae` directory containing `parse` and `util`.
3. In PowerShell 7, copy the variable/setup block in section 1 above and replace the example paths. It creates a virtual environment, installs `requirements.txt` and creates an `output` folder. Keep using that same PowerShell session.
4. Run the command in section 2 (`--list`). The expected model/node pairs are:

| Model | Matching node tree |
| --- | --- |
| `vt_5` | `vt_5_skeleton` |
| `vt_5_xray` | `vt_5_xray_skeleton` |
| `vt_5_dmg` | `vt_5_dmg_skeleton` |

5. Run the command in section 3 to export `vt5_xray.json`. `--freeze-skinned` explicitly permits static reference export of skinned objects, such as crew. **No skin weights are recovered.** Without this option the exporter stops if it encounters a skinned object.
6. Run the background Blender command in section 4. The importer resets the scene, so do not run it inside an unsaved working scene. Open the resulting `vt5_xray.blend` afterward.

The tested VT-5 file produced **172 nodes and 68 meshes**. Game updates may change those numbers. The original game file is read-only in this workflow. A separate node-tree GRP can be supplied with `--skeleton-grp` when necessary.

### Inspecting and editing in Blender

- Node Empties retain source names; mesh objects normally end with `_mesh`.
- Use Frame Selected to inspect individual objects. Disable overlays if node arrows obscure the geometry.
- Y/Z conversion and triangle winding correction are already applied. Do not swap axes a second time.
- Rigid meshes follow their parent node. Test a node rotation and undo it before editing the reference pose.
- Objects marked `frozen_skin_reference = True` are static references, not restored animated skins.
- A grey model is expected: this helper preserves UV coordinates but does not recreate original textures, face material assignments or the complete normal/tangent data.
- For exterior extraction, use the command in section 5. The exterior command is provided as usage guidance; only the X-ray extraction/import path has been tested with this toolkit so far.

When using a reference in a custom vehicle, rebuild pivots, parent relationships and dimensions for that vehicle. Prepare exterior, damaged exterior, collision/damage and X-ray geometry separately. Imported `_mesh` names are for reference organization; adapt the final exported node names to the target resource definitions. Skinned animation requires separate rigging and weight work.

### Packing a new GRP

A GRP is not a ZIP containing a modified JSON or Blender file. Export the prepared model through the Dagor Blender exporter to `.dag`, then create the appropriate CDK resource definitions, skeleton, animation tree/character and materials. Compile that **configured CDK project** with `daBuild`; the command pattern is shown in section 7.

The command requires an existing valid `application.blk`, asset search paths and package/output settings. This toolkit does not supply a complete VT-5 rebuild project or official animation sources. Vehicle BLK files, weapons, localisation and a user mission must also be prepared separately for a playable custom vehicle.

References: [official asset documentation](https://gaijinentertainment.github.io/DagorEngine/assets/about-assets/about_assets.html), [Asset Viewer](https://gaijinentertainment.github.io/DagorEngine/dagor-tools/asset-viewer/index.html).

Successful compilation is not proof of correct in-game animation or armour behaviour. Read back the compiled nodes, inspect movement/materials and test the independent vehicle in a user mission.

### Troubleshooting and tested status

- Wrong resource name: run `--list` again and use the actual names.
- Missing node for a rigid mesh: verify the model/skeleton pair; do not silently ignore it.
- Missing DLL/exported function: check your own CDK installation/version. The bridge uses a named Oodle entry point, not guessed ordinal numbers.
- A startup `Failed to load daKernel-dev.dll` message followed by successful export is an upstream diagnostic caused by intentionally disabling ordinal-based binding. The bridge then loads the DLL by its named entry point. A traceback means failure.
- LZMA errors may require adapting the standard-library compatibility layer for that encoding. Do not accept an empty result as success.
- Parser failures after a game update may require upstream format updates.

On 2026-11-03, a fresh upstream source download and isolated Python environment successfully listed VT-5 resources, exported its X-ray model and saved it through Blender. This is **not** a skinning, full visual fidelity, repacking or in-game acceptance test.

No extracted VT-5 JSON/Blender files, game GRPs/textures, third-party parser source or CDK binaries are distributed with this toolkit. Install dependencies separately.
