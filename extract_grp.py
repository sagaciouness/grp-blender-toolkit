"""List GRP resources or export one model and its node tree to JSON."""
import argparse
import json
from pathlib import Path
from dae_bridge import load_parser


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('grp', type=Path)
    parser.add_argument('--dae-source', required=True, type=Path)
    parser.add_argument('--cdk-bin', required=True, type=Path)
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--model')
    parser.add_argument('--skeleton')
    parser.add_argument('--skeleton-grp', type=Path, help='If the node tree is in another GRP')
    parser.add_argument('--lod', type=int, default=0)
    parser.add_argument('--freeze-skinned', action='store_true', help='Explicitly export skinned objects as static reference meshes; weights are NOT recovered')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if not args.grp.is_file() or args.lod < 0:
        parser.error('Supply an existing GRP and a non-negative LOD')
    if not args.list and not all((args.model, args.skeleton, args.out)):
        parser.error('Export requires --model, --skeleton and --out; first use --list')
    Pack, Cache = load_parser(args.dae_source, args.cdk_bin)
    pack = Pack(str(args.grp))
    if args.list:
        for resource in pack.getPackedFiles():
            print(resource.name, type(resource).__name__)
        return
    skeleton_pack = Pack(str(args.skeleton_grp)) if args.skeleton_grp else pack
    skeleton = skeleton_pack.getResourceByName(args.skeleton)
    Cache.cacheAsset(skeleton)
    nodes = list(skeleton.getNodes())
    model = pack.getResourceByName(args.model).getModel(args.lod)
    meshes = []
    for obj in model:
        if not obj.faces:
            continue
        if obj.skinned and not args.freeze_skinned:
            raise ValueError(f'{obj.name} is skinned. This tool does not recover weights. Use --freeze-skinned only for a static reference.')
        node = skeleton.getNodeByName(obj.name)
        if node is None and not obj.skinned:
            raise ValueError(f'Rigid object {obj.name} has no matching node; check --skeleton')
        used = sorted({i for face in obj.faces for i in face})
        remap = {old: new for new, old in enumerate(used)}
        vertices = [model.getVertex(i, parentBone=None if obj.skinned else node) for i in used]
        meshes.append(dict(name=obj.name, node=None if obj.skinned else node.name,
                           frozen_skin=bool(obj.skinned), vertices=vertices,
                           faces=[[remap[i] for i in face] for face in obj.faces],
                           uv=[model.getUV(i)[:2] for i in used]))
    result = dict(format='grp-reference-1', coordinates='dagor-world-y-up', model=args.model,
                  nodes=[dict(name=n.name, parent=n.parent.name if n.parent else None,
                              world=n.wtm, local=n.tm) for n in nodes], meshes=meshes)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, separators=(',', ':')), encoding='utf-8')
    print(f'Exported {len(nodes)} nodes and {len(meshes)} meshes to {args.out}')


if __name__ == '__main__':
    main()
