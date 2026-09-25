import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
for kind, size in [('BALL', None), ('ELLIPSOID', (1, 0.5, 0.5)), ('CAPSULE', (0.1, 1, 1))]:
    mb = bpy.data.metaballs.new(kind); mb.resolution = 0.003; mb.threshold = 0.6
    e = mb.elements.new(type=kind); e.radius = 0.1
    if size: e.size_x, e.size_y, e.size_z = size
    ob = bpy.data.objects.new(kind, mb); bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = ob.evaluated_get(dg).to_mesh()
    xs = [v.co.x for v in me.vertices]; zs = [v.co.z for v in me.vertices]
    print(kind, 'x extent', round(min(xs), 4), round(max(xs), 4), 'z', round(min(zs), 4), round(max(zs), 4), 'verts', len(me.vertices))
    bpy.data.objects.remove(ob)
