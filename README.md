# GRP → Blender reference toolkit

Small command-line helpers for reading a War Thunder GRP with an independently installed [Dagor Asset Explorer](https://github.com/quentin-dh/Dagor-Asset-Explorer), then importing reference geometry and the node hierarchy into Blender.

**Start here: [VT-5 walkthrough — English](docs/VT5_WALKTHROUGH.md).** It covers installation, resource listing, extraction, Blender inspection, and the separate CDK rebuild workflow.

## What this toolkit does

- Lists named resources in a GRP.
- Exports a selected model LOD and its matching skeleton/node tree to JSON.
- Imports geometry, UV coordinates and named Empty nodes into Blender, preserving rigid-object parent relationships and rest transforms.
- Optionally exports skinned objects as **static reference geometry**, with explicit `--freeze-skinned` consent.

It does **not** reconstruct skin weights, animation controllers, textures/material assignments, damage configuration, armour values or a complete playable vehicle. Nodes are Blender Empties, not a reconstructed deforming Armature. It is not a general-purpose GRP repacker.

## Files

- `extract_grp.py`: list / export CLI.
- `dae_bridge.py`: headless compatibility adapter for the external parser and a locally installed CDK DLL.
- `import_blender.py`: background Blender importer. It resets the scene; use the documented separate Blender process.
- `requirements.txt`: Python dependencies.
- `docs/VT5_WALKTHROUGH.md`: reproducible VT-5 example and rebuild boundaries.

## Tested scope

Windows x64, Python 3.11 and Blender 5.2.3. A clean upstream parser download plus this adapter extracted `vt_5_xray` with `vt_5_xray_skeleton`: **172 nodes / 68 meshes**, and saved a Blender file successfully. Counts depend on the game version. This is an extraction/import check, not a complete VT-5 recompile or in-game validation.

Game assets, extracted VT-5 files, purchased models, third-party parser source and CDK DLLs are not included. Install the parser and CDK separately. No upstream redistribution licence was found in the inspected source archive; this repository does not grant rights to that source or to game assets.

