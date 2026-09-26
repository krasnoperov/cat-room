# Build the cat: one welded smooth body, vertex colours, eyes and nose,
# an armature with automatic weights, exported as a skinned GLB.
# Blender coordinates: X right, -Y forward (the cat looks toward -Y), Z up.
# The glTF exporter turns -Y into +Z, which is where the room expects the nose.
#
#   blender -b --factory-startup -P cat_build.py -- out.glb
import bpy, bmesh, math, sys
from mathutils import Vector

OUT = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else 'cat.glb'

bpy.ops.wm.read_factory_settings(use_empty=True)
print('Building volumes', flush=True)
scene = bpy.context.scene
col = scene.collection

# ---------------------------------------------------------------- body
# Explicit volumes keep the reference silhouette predictable; voxel union welds
# them into one surface before heat-weight binding.
parts = []
def ell(c, ext):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40, ring_count=24, radius=1, location=c)
    o = bpy.context.object
    o.scale = ext
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    parts.append(o)
    return o


def cap(a, b, r):
    a, b = Vector(a), Vector(b)
    o = ell((a+b)/2, (r, r, (b-a).length/2+r))
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = Vector((0,0,1)).rotation_difference((b-a).normalized())
    return o

# Short loaf torso and a low, generously rounded rump.
ell((0, .025, .127), (.082, .131, .083))
ell((0, .095, .125), (.085, .072, .077))
ell((0, -.073, .143), (.075, .065, .077))
ell((0, -.116, .133), (.061, .037, .061))
for x,z in [(-.045,.109),(-.028,.088),(0,.080),(.028,.088),(.045,.109)]:
    ell((x,-.126,z),(.019,.025,.027))
# Wide, low face: head itself is almost half the ear-to-floor height.
ell((0,-.111,.248),(.110,.082,.087))
ell((0,-.135,.218),(.111,.064,.053))
for s in (-1,1):
    for x,z,rx,rz in [(.105,.240,.031,.013),(.114,.218,.031,.015),(.103,.198,.027,.013)]:
        o=ell((s*x,-.117,z),(rx,.036,rz))
        o.rotation_euler.y=s*(.15 if z>.23 else .5)
# Cream muzzle is broad, shallow and continuous with the cheek pads.
ell((0,-.174,.210),(.080,.029,.032))
for s in (-1,1):
    ell((s*.022,-.190,.209),(.030,.018,.020))
# Straight stubby legs, cream mittens, and plump rear haunches.
for s in (-1,1):
    cap((s*.048,-.080,.118),(s*.048,-.080,.030),.033)
    ell((s*.048,-.091,.020),(.034,.039,.025))
    ell((s*.057,.095,.092),(.042,.056,.060))
    cap((s*.053,.092,.085),(s*.053,.092,.026),.025)
    ell((s*.053,.080,.020),(.030,.036,.022))
# Curved plume, broad at the rounded tip rather than a tube with a ball cap.
TAIL = [(0,.157,.132),(0,.199,.149),(0,.227,.179),(0,.236,.211),(.008,.248,.240),(.025,.266,.258)]
for i in range(5):
    a,b=Vector(TAIL[i]),Vector(TAIL[i+1])
    for j in range(5):
        t=(i+j/5)/5
        r=.023+.025*math.sin(t*math.pi/2)**2
        ell(a.lerp(b,j/5),(r,r,r))
ell(TAIL[-1],(.048,.046,.046))
for side in (-1,1):
    ell((side*.032,.240,.226),(.020,.025,.015))
    ell((.025+side*.034,.266,.260),(.018,.029,.022))

# Padded triangular ears with round tips. The closed front/back wedge is
# bevelled before union, preserving a broad base and an outward lean.
for side in (-1,1):
    outline=[(.033,.292),(.043,.317),(.099,.370),(.110,.368),(.122,.302),(.099,.280)]
    verts=[(side*x,y,z) for y in (-.134,-.104) for x,z in outline]
    verts.extend([(side*.081,-.144,.320),(side*.081,-.098,.320)])
    faces=[]
    for j in range(6):
        k=(j+1)%6
        faces.extend([(12,j,k),(13,k+6,j+6),(j,j+6,k+6,k)])
    mesh=bpy.data.meshes.new('EarVolume')
    mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new('EarVolume',mesh); col.objects.link(o)
    bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(mesh); bm.free()
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bevel=o.modifiers.new('Round ear edges','BEVEL');bevel.width=.007;bevel.segments=3
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    parts.append(o)

bpy.ops.object.select_all(action='DESELECT')
for o in parts: o.select_set(True)
body=parts[0]; bpy.context.view_layer.objects.active=body
print('Joining volumes', flush=True)
bpy.ops.object.join()
body.name='Cat'
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
rm=body.modifiers.new('Weld silhouette','REMESH'); rm.mode='VOXEL'; rm.voxel_size=.0018
sm=body.modifiers.new('Soft fur volumes','SMOOTH'); sm.factor=.9; sm.iterations=16
for m in list(body.modifiers):
    print('Applying',m.name, flush=True)
    bpy.ops.object.modifier_apply(modifier=m.name)
dc=body.modifiers.new('Export budget','DECIMATE'); dc.ratio=min(1.,17500/len(body.data.polygons))
bpy.ops.object.modifier_apply(modifier=dc.name)
# Floor-aligned paws, without changing the bone-space origin.
for v in body.data.vertices: v.co.z=max(0,v.co.z)
bpy.ops.object.shade_smooth()
me=body.data
print('cat faces',len(me.polygons),'verts',len(me.vertices))

# ---------------------------------------------------------------- colours
def rgba(hexcolour):
    # Blender / COLOR_0 store linear light, while the art palette is sRGB.
    rgb=[int(hexcolour[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)
GINGER = rgba('E8A45E')
CREAM = rgba('FFF0CA')
STRIPE = rgba('C17C43')
PINK = rgba('EB9C96')
BLUSH = rgba('EE927B')
MOUTH = rgba('79452F')
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


def softedge(distance, width=.003):
    return max(0.,min(1.,.5-distance/width))

vertex_samples=[(v.index,v.co.copy(),v.normal.copy()) for v in me.vertices]
for index,p,n in vertex_samples:
    c=GINGER
    dtail,tt=tail_param(p)
    on_tail=p.y>.156 and dtail<.053
    on_head=p.z>.177 and p.y<-.046 and not on_tail
    if on_tail:
        band=math.sin(tt*26+1.)
        c=mix(GINGER,STRIPE,softedge(.28-band,.23))
    elif p.z<.036:
        c=mix(GINGER,CREAM,softedge(p.z-.030,.008))
    elif on_head:
        # Broad cream lower face with a rounded rather than horizontal border.
        border=.237-.016*(abs(p.x)/.095)**2
        if p.y<-.143:
            c=mix(c,CREAM,softedge(p.z-border,.006))
        # Three tapered marks follow the forehead and stop above the eyes.
        if p.z>.266 and p.y<-.122:
            for mid,end,width in [(0,.268,.010),(-.033,.280,.007),(.033,.280,.007)]:
                taper=min(1.,max(0.,(p.z-end)/.033))**.45
                d=abs(p.x-mid)-width*taper
                c=mix(c,STRIPE,softedge(d,.007)*softedge(end-p.z,.008))
        brow=((abs(p.x)-.040)/.008)**2+((p.z-.280)/.006)**2
        if p.y<-.167: c=mix(c,CREAM,softedge(brow-.9,.35))
        # Pink stays inside a triangular ginger border, with a cream base tuft.
        x=abs(p.x); z=p.z
        ear_left=.050+.73*(z-.315)
        ear_right=.107-.18*(z-.315)
        if z>.308 and z<.354 and p.y<-.112:
            mask=softedge(max(ear_left-x,x-ear_right,.313-z,z-.354),.004)
            c=mix(c,PINK,mask)
        tuft=((x-.065)/.017)**2+((z-.311)/.009)**2
        if p.y<-.135: c=mix(c,CREAM,softedge(tuft-.85,.45))
        if p.y<-.173:
            blush=((abs(p.x)-.074)/.019)**2+((p.z-.223)/.012)**2
            c=mix(c,BLUSH,softedge(blush-.86,.34)*.9)
    else:
        bib=p.y<-.103 and abs(p.x)<.063 and p.z<.20
        belly=n.z<-.3 and p.z<.096
        if bib or belly: c=CREAM
        else:
            # Arched transverse bands with softly feathered painted edges.
            phase=p.y*68+1.1*math.cos(p.x*24)+.8*p.z/.15
            stripe=softedge(.56-math.sin(phase),.48)
            c=mix(c,STRIPE,stripe)
    attr.data[index].color=c

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
    bone(f'upperarm.{sd}', (x, -0.080, 0.12), (x, -0.080, 0.07), 'chest')
    bone(f'forearm.{sd}', (x, -0.080, 0.07), (x, -0.08, 0.022), f'upperarm.{sd}', True)
    bone(f'hand.{sd}', (x, -0.08, 0.022), (x, -0.108, 0.018), f'forearm.{sd}', True)
    x = s * 0.052
    bone(f'thigh.{sd}', (x, 0.092, 0.12), (x, 0.092, 0.07), 'pelvis')
    bone(f'shin.{sd}', (x, 0.092, 0.07), (x, 0.092, 0.022), f'thigh.{sd}', True)
    bone(f'foot.{sd}', (x, 0.092, 0.022), (x, 0.06, 0.018), f'shin.{sd}', True)
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
unweighted = sum(1 for v in me.vertices if sum(g.weight for g in v.groups) < 1e-6)
print('unweighted verts', unweighted)
assert unweighted == 0, 'Every body vertex must be bound'
assert len(me.polygons) < 45000, 'Body exceeds the face budget'

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


def sphere():
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=32,radius=1)

for side,sd in ((-1,'R'),(1,'L')):
    loc,nrm=surface((side*.049,-.4,.248),(0,1,0))
    eye=rigid(f'eye.{sd}',sphere,loc,nrm,.003,rgba('FFFFFF'),(.028,.031,.012))
    # A single coloured eye surface keeps iris and pupil together during blink.
    ec=eye.data.color_attributes.new(name='Col',type='BYTE_COLOR',domain='POINT')
    eye.data.color_attributes.active_color=ec
    for v in eye.data.vertices:
        x,y,z=v.co
        edge=(x*x+y*y)**.5
        c=mix(rgba('C58A43'),rgba('633126'),min(1.,max(0.,(y+.5)/1.2)))
        pupil=((x+.04)/.52)**2+((y-.28)/.62)**2
        c=mix(c,rgba('391F20'),softedge(pupil-1.,.18))
        c=mix(c,rgba('603426'),softedge(.88-edge,.04))
        ec.data[v.index].color=c
    mat=eye.data.materials[0]; vc=mat.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='Col'
    mat.node_tree.links.new(vc.outputs['Color'],mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    rotation=Vector((0,0,1)).rotation_difference(nrm)
    for number,offset,r in [(1,(-.007,.010,.009),.006),(2,(.008,-.011,.010),.0027)]:
        at=loc+rotation@Vector(offset)
        rigid(f'glint{number}.{sd}',lambda: bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,radius=1),at,nrm,0,rgba('FFFFFF'),(r,r,.002))
loc,nrm=surface((0,-.4,.217),(0,1,0))
nose=rigid('nose',lambda: bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=1),loc,nrm,-.001,rgba('E79391'),(.007,.005,.004))
# A softly triangular button nose, broad at the top.
for v in nose.data.vertices:
    v.co.x*=.72+.28*(v.co.y+1)/2

# Fine muzzle strokes join the body mesh with full head weights, so the
# only rigid attachments are the eyes, highlights and nose.
face_strokes = []
def stroke(name,points,radius,colour):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.bevel_depth=radius;curve.bevel_resolution=3
    sp=curve.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for bp,(x,z) in zip(sp.bezier_points,points):
        loc,nrm=surface((x,-.4,z),(0,1,0))
        bp.co=loc+nrm*.001;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,curve);col.objects.link(o)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target='MESH');o=bpy.context.object
    attr=o.data.color_attributes.new(name='Col',type='BYTE_COLOR',domain='POINT');o.data.color_attributes.active_color=attr
    for item in attr.data:item.color=colour
    o.data.materials.append(mat_fur)
    vg=o.vertex_groups.new(name='head');vg.add(list(range(len(o.data.vertices))),1.,'REPLACE')
    face_strokes.append(o)
    return o
mat_fur=body.data.materials[0]
stroke('muzzle.philtrum',[(0,.214),(0,.207),(0,.204)],.0009,MOUTH)
for side in (-1,1):
    stroke('muzzle.smile',[(0,.205),(side*.007,.200),(side*.014,.201),(side*.019,.205)],.001,MOUTH)

bpy.ops.object.select_all(action='DESELECT')
for o in face_strokes+[body]: o.select_set(True)
bpy.context.view_layer.objects.active=body
bpy.ops.object.join()
me=body.data
assert all(sum(g.weight for g in v.groups)>1e-6 for v in me.vertices)
me.calc_loop_triangles()
print('Final skinned triangles',len(me.loop_triangles))
assert len(me.loop_triangles)<45000

# ---------------------------------------------------------------- export
bpy.ops.object.select_all(action='SELECT')
kw = dict(filepath=OUT, export_format='GLB', use_selection=True, export_animations=False, export_skins=True, export_apply=False)
try:
    bpy.ops.export_scene.gltf(**kw, export_vertex_color='ACTIVE')
except TypeError:
    bpy.ops.export_scene.gltf(**kw, export_colors=True)
print('exported', OUT)
