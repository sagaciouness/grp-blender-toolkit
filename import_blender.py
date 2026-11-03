"""Run in background Blender: --python import_blender.py -- input.json output.blend"""
import json
import sys
from pathlib import Path
import bpy
from mathutils import Matrix


def main():
    args = sys.argv[sys.argv.index('--') + 1:]
    if len(args) != 2:
        raise ValueError('Expected input.json output.blend after --')
    data = json.loads(Path(args[0]).read_text(encoding='utf-8'))
    if data.get('format') != 'grp-reference-1':
        raise ValueError('Unsupported reference format')
    # Swapping Y/Z has negative determinant: reverse face winding as well.
    change = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'
    nodes = {}
    for item in data['nodes']:
        obj = bpy.data.objects.new(item['name'], None)
        bpy.context.scene.collection.objects.link(obj)
        obj.empty_display_type = 'ARROWS'
        obj.empty_display_size = .15
        nodes[item['name']] = obj
    for item in data['nodes']:
        if item['parent']:
            nodes[item['name']].parent = nodes[item['parent']]
    # Set rest matrices parent-first, irrespective of serialized node order.
    records = {n['name']: n for n in data['nodes']}
    done = set()
    def place(name):
        if name in done:
            return
        record = records[name]
        if record['parent']:
            place(record['parent'])
        nodes[name].matrix_world = change @ Matrix(record['world']) @ change
        bpy.context.view_layer.update()
        done.add(name)
    for name in nodes:
        place(name)
    for item in data['meshes']:
        mesh = bpy.data.meshes.new(item['name'] + '_geometry')
        mesh.from_pydata([(v[0], v[2], v[1]) for v in item['vertices']], [],
                         [list(reversed(f)) for f in item['faces']])
        mesh.update()
        uv = mesh.uv_layers.new(name='UVMap')
        for loop in mesh.loops:
            uv.data[loop.index].uv = item['uv'][loop.vertex_index]
        obj = bpy.data.objects.new(item['name'] + '_mesh', mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj['frozen_skin_reference'] = item['frozen_skin']
        if item['node']:
            obj.parent = nodes[item['node']]
            obj.matrix_parent_inverse = obj.parent.matrix_world.inverted()
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(Path(args[1]).resolve()))
    print('Imported nodes as Empties; no animation or skin weights have been reconstructed.')


if __name__ == '__main__':
    main()
