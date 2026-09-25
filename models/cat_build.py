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


import random
rnd = random.Random(7)
# plump body: a loaf with a round rump and a full chest
ell((0, 0.02, 0.13), (0.084, 0.125, 0.084))
ell((0, 0.085, 0.125), (0.08, 0.07, 0.082))
ell((0, -0.07, 0.14), (0.078, 0.07, 0.085))
# fluffy cream bib: a soft mass with tufts along its lower edge
ell((0, -0.1, 0.145), (0.062, 0.05, 0.07), 1.6)
for i in range(7):
    a = (i - 3) / 3
    ell((a * 0.045, -0.125 + abs(a) * 0.018, 0.085 + abs(a) * 0.02), (0.016, 0.014, 0.022), 2.4)
# head: big and round, sitting on the chest with no neck
ell((0, -0.105, 0.245), (0.094, 0.084, 0.082))
ell((0, -0.11, 0.285), (0.08, 0.07, 0.05))
# cheek ruff: round cheeks and tufts poking out sideways
for s in (-1, 1):
    ell((s * 0.07, -0.125, 0.215), (0.05, 0.045, 0.04), 1.8)
    for (dx, dz, sz) in ((0.105, 0.232, 0.019), (0.11, 0.206, 0.02), (0.098, 0.182, 0.017), (0.085, 0.255, 0.015)):
        ell((s * dx, -0.105, dz), (sz * 1.2, sz * 0.9, sz * 0.8), 2.6)
# muzzle and chin
ell((0, -0.18, 0.214), (0.043, 0.028, 0.03))
ell((0, -0.172, 0.196), (0.03, 0.022, 0.018))
# short stubby legs with round paws
for s in (-1, 1):
    cap((s * 0.046, -0.07, 0.1), (s * 0.046, -0.078, 0.028), 0.026)
    ell((s * 0.046, -0.088, 0.019), (0.03, 0.036, 0.02))
    ell((s * 0.056, 0.078, 0.1), (0.044, 0.062, 0.062))
    cap((s * 0.052, 0.086, 0.08), (s * 0.052, 0.086, 0.028), 0.025)
    ell((s * 0.052, 0.074, 0.019), (0.03, 0.036, 0.02))
# a thick fluffy tail that widens toward the tip, rest pose rising behind
TAIL = [(0, 0.175, 0.135), (0, 0.225, 0.165), (0, 0.262, 0.21), (0, 0.285, 0.262), (0, 0.296, 0.315), (0, 0.3, 0.36)]
steps = 45
for i in range(len(TAIL) - 1):
    a, b = Vector(TAIL[i]), Vector(TAIL[i + 1])
    n = steps // (len(TAIL) - 1)
    for k in range(n):
        t = (i + k / n) / (len(TAIL) - 1)
        c = a.lerp(b, k / n)
        ball = mb.elements.new(type='BALL')
        ball.co = c
        ball.radius = (0.019 + 0.014 * t * t) * K
        # fur tufts along the tail
        if k % 3 == 0 and t > 0.15:
            j = Vector((rnd.uniform(-1, 1), rnd.uniform(-0.3, 0.3), rnd.uniform(-1, 1))).normalized()
            tuft = mb.elements.new(type='BALL')
            tuft.co = c + j * (0.015 + 0.012 * t)
            tuft.radius = (0.008 + 0.005 * t) * K
            tuft.stiffness = 2.6
end = mb.elements.new(type='BALL'); end.co = Vector(TAIL[-1]) + Vector((0, 0.004, 0.01)); end.radius = 0.03 * K

bpy.context.view_layer.objects.active = body
body.select_set(True)
bpy.ops.object.convert(target='MESH')
body = bpy.context.view_layer.objects.active
body.name = 'Cat'

# ---------------------------------------------------------------- ears
ears = []
for s in (-1, 1):
    bpy.ops.mesh.primitive_cone_add(vertices=40, radius1=0.06, radius2=0.013, depth=0.074, location=(s * 0.066, -0.1, 0.356))
    ear = bpy.context.active_object
    ear.scale = (1, 0.48, 1)
    ear.rotation_euler = (math.radians(-6), math.radians(s * 30), math.radians(s * -4))
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
GINGER = (0.93, 0.62, 0.35, 1)
CREAM = (0.99, 0.93, 0.82, 1)
STRIPE = (0.84, 0.48, 0.23, 1)
PINK = (0.96, 0.66, 0.64, 1)
BLUSH = (0.97, 0.63, 0.55, 1)
MOUTH = (0.45, 0.27, 0.24, 1)
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


def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(4))


for v in me.vertices:
    p, n = v.co, v.normal
    c = GINGER
    dtail, tt = tail_param(p)
    on_tail = p.y > 0.16 and dtail < 0.055
    on_head = p.z > 0.17 and p.y < -0.03 and not on_tail
    if on_tail:
        c = STRIPE if math.sin(tt * 30 + 1.2) > 0.3 else GINGER
    elif p.z < 0.034:
        c = CREAM  # paws
    elif on_head:
        front = n.y < -0.35
        if p.z > 0.335 and n.y < -0.45 and abs(p.x) > 0.04:
            c = PINK  # inner ears
        elif front and p.z < 0.232 and abs(p.x) < 0.075:
            c = CREAM  # lower face, muzzle and chin
        elif p.z > 0.27 and n.y < 0.2 and abs(p.x) < 0.04 and math.cos(p.x * 150) > 0.62:
            c = STRIPE  # forehead stripes
        if front and 0.2 < p.z < 0.245:
            bl = ((abs(p.x) - 0.064) ** 2 / 0.018 ** 2 + (p.z - 0.222) ** 2 / 0.012 ** 2)
            if bl < 1:
                c = mix(c, BLUSH, 0.85 * (1 - bl))
    else:
        bib = p.y < -0.06 and n.y < -0.15 and abs(p.x) < 0.06 and p.z < 0.2
        belly = n.z < -0.4 and p.z < 0.12
        if bib or belly:
            c = CREAM
        elif n.z > -0.35 and p.z > 0.05 and math.sin(p.y * 70 + math.sin(p.x * 25) * 0.9) > 0.5:
            c = STRIPE  # soft bands across the back, flanks and legs
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
bone('pelvis', (0, 0.1, 0.13), (0, 0.02, 0.13), 'root')
bone('spine', (0, 0.02, 0.13), (0, -0.055, 0.14), 'pelvis', True)
bone('chest', (0, -0.055, 0.14), (0, -0.09, 0.18), 'spine', True)
bone('neck', (0, -0.09, 0.18), (0, -0.1, 0.205), 'chest', True)
bone('head', (0, -0.1, 0.205), (0, -0.115, 0.32), 'neck', True)
for s, sd in ((-1, 'R'), (1, 'L')):
    x = s * 0.046
    bone(f'upperarm.{sd}', (x, -0.068, 0.12), (x, -0.074, 0.07), 'chest')
    bone(f'forearm.{sd}', (x, -0.074, 0.07), (x, -0.08, 0.022), f'upperarm.{sd}', True)
    bone(f'hand.{sd}', (x, -0.08, 0.022), (x, -0.108, 0.018), f'forearm.{sd}', True)
    x = s * 0.052
    bone(f'thigh.{sd}', (x, 0.08, 0.12), (x, 0.076, 0.07), 'pelvis')
    bone(f'shin.{sd}', (x, 0.076, 0.07), (x, 0.086, 0.022), f'thigh.{sd}', True)
    bone(f'foot.{sd}', (x, 0.086, 0.022), (x, 0.06, 0.018), f'shin.{sd}', True)
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
    loc, nrm = surface((s * 0.05, -0.4, 0.25), (0, 1, 0))
    rigid(f'eye.{sd}', lambda: bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=1),
          loc, nrm, 0.004, (0.2, 0.1, 0.05, 1), (0.026, 0.03, 0.011))
    hl = surface((s * 0.043, -0.4, 0.262), (0, 1, 0))
    rigid(f'glint.{sd}', lambda: bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=1),
          hl[0], hl[1], -0.0075, (1, 1, 1, 1), (0.0085, 0.0085, 0.003))
    hl2 = surface((s * 0.057, -0.4, 0.24), (0, 1, 0))
    rigid(f'glint2.{sd}', lambda: bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6, radius=1),
          hl2[0], hl2[1], -0.0075, (1, 1, 1, 1), (0.0038, 0.0038, 0.0018))
loc, nrm = surface((0, -0.4, 0.218), (0, 1, 0.05))
rigid('nose', lambda: bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=1),
      loc, nrm, 0.001, (0.93, 0.55, 0.57, 1), (0.009, 0.0065, 0.005))

# ---------------------------------------------------------------- export
bpy.ops.object.select_all(action='SELECT')
kw = dict(filepath=OUT, export_format='GLB', use_selection=True, export_animations=False, export_skins=True, export_apply=False)
try:
    bpy.ops.export_scene.gltf(**kw, export_vertex_color='ACTIVE')
except TypeError:
    bpy.ops.export_scene.gltf(**kw, export_colors=True)
print('exported', OUT)
