# Build the cat: one smooth metaball body, vertex colours, eyes and nose,
# an armature with automatic weights, exported as a skinned GLB.
# Blender coordinates: X right, -Y forward (the cat looks toward -Y), Z up.
# The glTF exporter turns -Y into +Z, which is where the room expects the nose.
#
#   blender -b --factory-startup -P cat_build.py -- out.glb
import bpy, bmesh, math, sys
from mathutils import Vector, Quaternion, Matrix

OUT = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else 'cat.glb'
K = 1 / 0.574  # metaball radius for a visible radius of 1 (measured)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
col = scene.collection

# ---------------------------------------------------------------- body
mb = bpy.data.metaballs.new('CatBody')
mb.resolution = 0.0035
mb.render_resolution = 0.0035
mb.threshold = 0.6
body = bpy.data.objects.new('Cat', mb)
col.objects.link(body)


def ell(c, ext, stiff=2.0):
    e = mb.elements.new(type='ELLIPSOID')
    m = max(ext)
    e.co = Vector(c)
    e.radius = m * K
    e.size_x, e.size_y, e.size_z = ext[0] / m, ext[1] / m, ext[2] / m
    e.stiffness = stiff
    return e


def cap(a, b, r, stiff=2.0):
    a, b = Vector(a), Vector(b)
    e = mb.elements.new(type='CAPSULE')
    e.co = (a + b) / 2
    e.radius = r * K
    e.size_x = (b - a).length / 2
    e.rotation = Vector((1, 0, 0)).rotation_difference((b - a).normalized())
    e.stiffness = stiff
    return e


# torso: hips, belly, chest
ell((0, 0.085, 0.165), (0.068, 0.085, 0.07))
ell((0, 0.0, 0.158), (0.064, 0.1, 0.064))
ell((0, -0.085, 0.172), (0.064, 0.075, 0.074))
# chest fluff and neck
ell((0, -0.13, 0.17), (0.045, 0.035, 0.05), 1.6)
cap((0, -0.12, 0.2), (0, -0.175, 0.25), 0.042)
# head: skull, cheeks, muzzle, chin
ell((0, -0.2, 0.292), (0.078, 0.07, 0.068))
for s in (-1, 1):
    ell((s * 0.046, -0.224, 0.266), (0.04, 0.035, 0.034), 1.8)
ell((0, -0.264, 0.27), (0.03, 0.022, 0.022))
ell((0, -0.248, 0.252), (0.02, 0.018, 0.014))
# legs
for s in (-1, 1):
    cap((s * 0.04, -0.095, 0.15), (s * 0.04, -0.1, 0.03), 0.021)
    ell((s * 0.04, -0.11, 0.017), (0.024, 0.032, 0.016))
    ell((s * 0.046, 0.088, 0.128), (0.034, 0.052, 0.058))
    cap((s * 0.048, 0.1, 0.1), (s * 0.048, 0.1, 0.03), 0.019)
    ell((s * 0.048, 0.086, 0.017), (0.024, 0.032, 0.016))
# tail
TAIL = [(0, 0.16, 0.19), (0, 0.215, 0.2), (0, 0.27, 0.205), (0, 0.325, 0.205), (0, 0.38, 0.2), (0, 0.43, 0.195)]
# a dense chain of small balls makes a smooth tube; capsules bulge at their joints
steps = 40
for i in range(len(TAIL) - 1):
    a, b = Vector(TAIL[i]), Vector(TAIL[i + 1])
    for k in range(steps // (len(TAIL) - 1)):
        t = (i + k / (steps // (len(TAIL) - 1))) / (len(TAIL) - 1)
        ball = mb.elements.new(type='BALL')
        ball.co = a.lerp(b, k / (steps // (len(TAIL) - 1)))
        ball.radius = (0.0145 - 0.0035 * t) * K
        ball.stiffness = 2.0
end = mb.elements.new(type='BALL'); end.co = Vector(TAIL[-1]); end.radius = 0.0112 * K

bpy.context.view_layer.objects.active = body
body.select_set(True)
bpy.ops.object.convert(target='MESH')
body = bpy.context.view_layer.objects.active
body.name = 'Cat'

# ---------------------------------------------------------------- ears
ears = []
for s in (-1, 1):
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.037, radius2=0.005, depth=0.066, location=(s * 0.047, -0.19, 0.35))
    ear = bpy.context.active_object
    ear.scale = (1, 0.55, 1)
    ear.rotation_euler = (math.radians(-12), math.radians(s * 22), math.radians(s * -8))
    ears.append(ear)
bpy.ops.object.select_all(action='DESELECT')
for o in ears + [body]:
    o.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()

# fuse into one watertight surface, then soften the seams
rm = body.modifiers.new('Remesh', 'REMESH')
rm.mode = 'VOXEL'
rm.voxel_size = 0.0032
sm = body.modifiers.new('Smooth', 'SMOOTH')
sm.factor = 0.6
sm.iterations = 4
dc = body.modifiers.new('Decimate', 'DECIMATE')
dc.ratio = 0.45
for m in list(body.modifiers):
    bpy.ops.object.modifier_apply(modifier=m.name)
bpy.ops.object.shade_smooth()
me = body.data
print('cat faces', len(me.polygons), 'verts', len(me.vertices))

# ---------------------------------------------------------------- colours
GINGER = (0.93, 0.6, 0.32, 1)
CREAM = (0.98, 0.91, 0.81, 1)
STRIPE = (0.8, 0.44, 0.19, 1)
PINK = (0.95, 0.64, 0.63, 1)
attr = me.color_attributes.new(name='Col', type='BYTE_COLOR', domain='POINT')
me.color_attributes.active_color = attr
tail_len = sum((Vector(TAIL[i + 1]) - Vector(TAIL[i])).length for i in range(len(TAIL) - 1))


def tail_param(p):
    best, acc, t = 1e9, 0, None
    for i in range(len(TAIL) - 1):
        a, b = Vector(TAIL[i]), Vector(TAIL[i + 1])
        ab = b - a
        u = max(0, min(1, (p - a).dot(ab) / ab.length_squared))
        d = (a + ab * u - p).length
        if d < best:
            best, t = d, (acc + ab.length * u) / tail_len
        acc += ab.length
    return best, t


for v in me.vertices:
    p, n = v.co, v.normal
    c = GINGER
    dtail, tt = tail_param(p)
    on_tail = p.y > 0.17 and dtail < 0.03
    on_head = p.y < -0.16 and p.z > 0.22
    if on_tail:
        c = STRIPE if (math.sin(tt * 34) > 0.35 or tt > 0.88) else GINGER
    elif p.z < 0.03:
        c = CREAM  # paws
    elif on_head:
        if p.z > 0.338 and n.y < -0.3 and abs(p.x) > 0.028:
            c = PINK  # inner ears
        elif p.y < -0.244 and p.z < 0.279 and abs(p.x) < 0.052:
            c = CREAM  # muzzle and chin
        elif p.z > 0.3 and -0.255 < p.y < -0.19 and abs(p.x) < 0.034 and math.cos(p.x * 190) > 0.55:
            c = STRIPE  # the M on the forehead
        elif abs(p.x) > 0.055 and p.z < 0.28 and math.sin(p.z * 150) > 0.7:
            c = STRIPE  # cheek lines
    else:
        chest = p.y < -0.08 and p.z < 0.21 and abs(p.x) < 0.05 and n.y < -0.2
        belly = n.z < -0.45 and p.z < 0.16
        if chest or belly:
            c = CREAM
        elif n.z > -0.3 and p.z > 0.07 and math.sin(p.y * 78 + math.sin(p.x * 30) * 0.8) > 0.42:
            c = STRIPE  # bands across back and flanks, legs included
    attr.data[v.index].color = c

mat = bpy.data.materials.new('CatFur')
mat.use_nodes = True
bsdf = mat.node_tree.nodes['Principled BSDF']
vc = mat.node_tree.nodes.new('ShaderNodeVertexColor')
vc.layer_name = 'Col'
mat.node_tree.links.new(vc.outputs['Color'], bsdf.inputs['Base Color'])
bsdf.inputs['Roughness'].default_value = 0.9
me.materials.append(mat)

# ---------------------------------------------------------------- armature
arm_data = bpy.data.armatures.new('CatRig')
rig = bpy.data.objects.new('CatRig', arm_data)
col.objects.link(rig)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones


def bone(name, head, tail, parent=None, connect=False):
    b = eb.new(name)
    b.head, b.tail = Vector(head), Vector(tail)
    b.roll = 0
    if parent:
        b.parent = eb[parent]
        b.use_connect = connect
    return b


bone('root', (0, 0, 0), (0, -0.05, 0))
bone('pelvis', (0, 0.1, 0.168), (0, 0.02, 0.165), 'root')
bone('spine', (0, 0.02, 0.165), (0, -0.07, 0.172), 'pelvis', True)
bone('chest', (0, -0.07, 0.172), (0, -0.13, 0.2), 'spine', True)
bone('neck', (0, -0.13, 0.2), (0, -0.18, 0.255), 'chest', True)
bone('head', (0, -0.18, 0.255), (0, -0.23, 0.3), 'neck', True)
for s, sd in ((-1, 'R'), (1, 'L')):
    x = s * 0.04
    bone(f'upperarm.{sd}', (x, -0.09, 0.16), (x, -0.094, 0.09), 'chest')
    bone(f'forearm.{sd}', (x, -0.094, 0.09), (x, -0.1, 0.022), f'upperarm.{sd}', True)
    bone(f'hand.{sd}', (x, -0.1, 0.022), (x, -0.13, 0.016), f'forearm.{sd}', True)
    x = s * 0.048
    bone(f'thigh.{sd}', (x, 0.085, 0.16), (x, 0.075, 0.095), 'pelvis')
    bone(f'shin.{sd}', (x, 0.075, 0.095), (x, 0.1, 0.022), f'thigh.{sd}', True)
    bone(f'foot.{sd}', (x, 0.1, 0.022), (x, 0.07, 0.016), f'shin.{sd}', True)
prev = 'pelvis'
for i in range(len(TAIL) - 1):
    bone(f'tail{i}', TAIL[i], TAIL[i + 1], prev, i > 0)
    prev = f'tail{i}'
bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
unweighted = sum(1 for v in me.vertices if not v.groups)
print('unweighted verts', unweighted)

# ---------------------------------------------------------------- eyes and nose on the head bone
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
body_eval = body.evaluated_get(dg)


def surface(origin, direction):
    ok, loc, nrm, _ = body_eval.ray_cast(Vector(origin), Vector(direction).normalized())
    return (loc, nrm) if ok else (None, None)


def rigid(name, mesh_fn, loc, nrm, embed, color, scale):
    mesh_fn()
    o = bpy.context.active_object
    o.name = name
    o.location = loc - nrm * embed
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(nrm)
    o.scale = scale
    m = bpy.data.materials.new(name + 'Mat')
    m.use_nodes = True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = color
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    # parent to the head bone, keeping the world transform
    mw = o.matrix_world.copy()
    o.parent = rig
    o.parent_type = 'BONE'
    o.parent_bone = 'head'
    o.matrix_world = mw
    return o


for s, sd in ((-1, 'R'), (1, 'L')):
    loc, nrm = surface((s * 0.034, -0.4, 0.292), (s * -0.12, 1, 0))
    rigid(f'eye.{sd}', lambda: bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=1),
          loc, nrm, 0.002, (0.08, 0.05, 0.09, 1), (0.0145, 0.018, 0.007))
    hl = surface((s * 0.029, -0.4, 0.3), (s * -0.12, 1, 0))
    rigid(f'glint.{sd}', lambda: bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=1),
          hl[0], hl[1], -0.0045, (1, 1, 1, 1), (0.0045, 0.0045, 0.002))
loc, nrm = surface((0, -0.4, 0.279), (0, 1, 0.05))
rigid('nose', lambda: bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=1),
      loc, nrm, 0.001, (0.93, 0.55, 0.57, 1), (0.011, 0.008, 0.006))

# ---------------------------------------------------------------- export
bpy.ops.object.select_all(action='SELECT')
kw = dict(filepath=OUT, export_format='GLB', use_selection=True, export_animations=False, export_skins=True, export_apply=False)
try:
    bpy.ops.export_scene.gltf(**kw, export_vertex_color='ACTIVE')
except TypeError:
    bpy.ops.export_scene.gltf(**kw, export_colors=True)
print('exported', OUT)
