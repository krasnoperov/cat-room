"""Rebuild all room props: Blender -Y front, metres, no external textures.

Run from the project root:
  ~/opt/blender-5.2.2-linux-x64/blender -b --factory-startup -P models/props_build.py
Optional: -- box radio (build only the named props).
Animation anchors are real tiny meshes, preserved by the GLB exporter.
"""
import bpy
import bmesh
import math
import random
import sys
from pathlib import Path
from mathutils import Vector

OUT = Path(__file__).resolve().parent / 'props'
OUT.mkdir(exist_ok=True)
TAU = math.tau
rng = random.Random(1704)
MATS = {}


def material(name, color, roughness=.85, metallic=0):
    if name in MATS:
        return MATS[name]
    rgb = [int(color[i:i+2], 16)/255 for i in (0, 2, 4)]
    linear = tuple(v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb) + (1,)
    m = bpy.data.materials.new(name)
    m.diffuse_color = linear
    m.use_nodes = True
    bs = m.node_tree.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value = linear
    bs.inputs['Roughness'].default_value = roughness
    bs.inputs['Metallic'].default_value = metallic
    MATS[name] = m
    return m


WOOD = material('Honey walnut', 'AE7952')
LIGHTWOOD = material('Warm cut wood', 'CA9765')
DARK = material('Warm dark trim', '76503B')
GRAIN = material('Subtle wood grain', 'B78358')
CREAM = material('Buttercream linen', 'EBD7AD')
SEAM = material('Cushion piping', 'CEB38D')
BRASS = material('Aged brass', 'AE8D4E', .5, .3)
PINK = material('Dusty rose yarn', 'D89191')
PINKLIGHT = material('Yarn light strands', 'E6A6A0')
PINKDARK = material('Yarn shadow strands', 'C07A7C')
GREEN = material('Sage enamel', '7B9467', .55, .1)
GREENTRIM = material('Sage rolled edges', '59764F')
BLACK = material('Soft espresso', '45352C')


def active(o):
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o


def finish(o, mat, smooth=True):
    if mat:
        o.data.materials.append(mat)
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    return o


def mesh(verts, faces, mat, smooth=True):
    me = bpy.data.meshes.new('part')
    me.from_pydata(verts, [], faces)
    me.update()
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new('part', me)
    bpy.context.collection.objects.link(o)
    return finish(o, mat, smooth)


def bevel(o, width, segments=2):
    active(o)
    m = o.modifiers.new('Soft edges', 'BEVEL')
    m.width = width
    m.segments = segments
    bpy.ops.object.modifier_apply(modifier=m.name)
    m = o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    m.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=m.name)
    return o


def cube(c, size, mat, edge=.003):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(o, mat)
    return bevel(o, edge) if edge else o


def ell(c, radii, mat, seg=20, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=1, location=c)
    o = bpy.context.object
    o.scale = radii
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, mat)


def cylinder(a, b, radius, mat, vertices=24, edge=.001):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=(b-a).length, location=(a+b)/2)
    o = bpy.context.object
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = Vector((0,0,1)).rotation_difference((b-a).normalized())
    finish(o, mat)
    return bevel(o, edge) if edge else o


def tube(points, radius, mat, sides=6, closed=False):
    # Parallel transported frames avoid a twist at vertical tangents.
    pts = [Vector(p) for p in points]
    verts, faces = [], []
    previous = None
    for i, p in enumerate(pts):
        tangent = (pts[(i+1) % len(pts)]-pts[i-1]) if closed else (pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)])
        tangent.normalize()
        if previous is None:
            n = tangent.cross(Vector((0,0,1)))
            if n.length < .01:
                n = tangent.cross(Vector((0,1,0)))
        else:
            n = previous-tangent*previous.dot(tangent)
        n.normalize()
        previous = n
        b = tangent.cross(n).normalized()
        for j in range(sides):
            verts.append(p + radius*(math.cos(TAU*j/sides)*n+math.sin(TAU*j/sides)*b))
    for i in range(len(pts) if closed else len(pts)-1):
        k = (i+1) % len(pts)
        for j in range(sides):
            l = (j+1) % sides
            faces.append((i*sides+j, i*sides+l, k*sides+l, k*sides+j))
    if not closed:
        faces.extend([tuple(reversed(range(sides))), tuple((len(pts)-1)*sides+j for j in range(sides))])
    return mesh(verts, faces, mat)


def ring(c, rx, ry, radius, mat, n=32):
    return tube([(c[0]+rx*math.cos(TAU*i/n),c[1]+ry*math.sin(TAU*i/n),c[2]) for i in range(n)],radius,mat,closed=True)


def lathe(c, profile, mat, n=48):
    # Profile follows a closed section, allowing actual interior cavities.
    verts = [(c[0]+r*math.cos(TAU*i/n),c[1]+r*math.sin(TAU*i/n),c[2]+z) for r,z in profile for i in range(n)]
    faces = []
    for j in range(len(profile)-1):
        for i in range(n):
            k=(i+1)%n
            faces.append((j*n+i,j*n+k,(j+1)*n+k,(j+1)*n+i))
    o = mesh(verts,faces,mat)
    # Keep broad cylindrical walls smooth without blending their normals into
    # horizontal lips and bases (which produces diagonal toon shading).
    active(o)
    split=o.modifiers.new('Profile normal breaks','EDGE_SPLIT')
    split.split_angle=math.radians(48)
    bpy.ops.object.modifier_apply(modifier=split.name)
    weighted=o.modifiers.new('Broad surface normals','WEIGHTED_NORMAL')
    weighted.keep_sharp=True
    bpy.ops.object.modifier_apply(modifier=weighted.name)
    return o


def join(name, parts, origin=(0,0,0)):
    active(parts[0])
    for o in parts:
        o.select_set(True)
    bpy.ops.object.join()
    o = bpy.context.object
    o.name = name
    bpy.context.scene.cursor.location = origin
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    # Stable axes for local animation, including knob axes along -Y.
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return o


def anchor(name, at, mat=WOOD):
    return join(name,[ell(at,(.0004,)*3,mat,8,4)],at)


def beam(a,b,width,depth,mat=WOOD):
    a,b=Vector(a),Vector(b)
    o=cube((a+b)/2,(width,depth,(b-a).length),mat,min(width,depth)*.15)
    o.rotation_mode='QUATERNION'
    o.rotation_quaternion=Vector((0,0,1)).rotation_difference((b-a).normalized())
    return o


def build_box():
    card=material('Cardboard outer', 'C69669')
    inside=material('Cardboard inner', 'B7855D')
    edge=material('Cardboard fluting', '9F714F')
    p=[cube((0,0,.004),(.44,.34,.008),inside,.002)]
    for s in (-1,1):
        p.append(cube((s*.216,0,.103),(.008,.34,.20),card,.002))
        p.append(cube((0,s*.166,.103),(.432,.008,.20),inside,.002))
        # Flaps droop 14 degrees beyond the horizontal, hinges on wall tops.
        for along_x, length, width in [(True,.146,.336),(False,.132,.432)]:
            outward=Vector((s,0,0) if along_x else (0,s,0))
            hinge=Vector((s*.22,0,.201) if along_x else (0,s*.17,.201))
            end=hinge+outward*length+Vector((0,0,-.035))
            span=Vector((0,width/2,0) if along_x else (width/2,0,0))
            v=[hinge-span,hinge+span,end+span,end-span]
            verts=[tuple(vv+Vector((0,0,z))) for z in (-.002,.002) for vv in v]
            p.append(bevel(mesh(verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],card),.001,2))
            # Visible alternating corrugated fibres along the exposed flap edge.
            for j in range(35):
                a=end+span*(-.96+1.92*j/34)
                p.append(tube([a+Vector((0,0,-.0015)),a+outward*.0015,a+Vector((0,0,.0015))],.00065,edge,4))
    join('box',p)


def build_bowls():
    straw=material('Woven oat mat','CAA370')
    straw2=material('Basket weave highlights','D9B883')
    p=[ell((0,0,.007),(.20,.11,.007),straw,48,8)]
    for i in range(4):
        p.append(ring((0,0,.009),.194-i*.004,.104-i*.004,.002,straw2))
    for i in range(-13,14):
        x=i*.013
        y=.092*math.sqrt(max(0,1-(x/.185)**2))
        p.append(tube([(x+.0015*math.sin(j*math.pi/2),-y+2*y*j/8,.012) for j in range(9)],.00085,straw2,4))
    for i in range(-6,7):
        y=i*.013
        x=.184*math.sqrt(max(0,1-(y/.094)**2))
        p.append(tube([(-x+2*x*j/12,y,.0125+.0006*math.sin(j*math.pi/2)) for j in range(13)],.00085,straw2,4))
    join('mat',p)
    ceramic=material('Warm ivory ceramic','DBC5AE',.48)
    lip=material('Ceramic lip','F0DEBE',.45)
    for x,name in [(.099,'foodBowl'),(-.099,'waterBowl')]:
        profile = ([(0,0),(.065,0),(.071,.005),(.074,.013),(.063,.062),(.060,.066),(.055,.064),(.060,.016),(.052,.010),(0,.010)]
                   if name == 'foodBowl' else
                   [(0,0),(.048,0),(.056,.005),(.059,.013),(.068,.062),(.066,.066),(.062,.064),(.054,.016),(.048,.010),(0,.010)])
        p=[lathe((x,0,.013),profile,ceramic)]
        r=.0585 if name == 'foodBowl' else .0645
        p.append(ring((x,0,.077),r,r,.002,lip))
        r=.071 if name == 'foodBowl' else .057
        p.append(ring((x,0,.020),r,r,.002,SEAM))
        join(name,p)
    kibble=[material('Kibble toast','A9713E'),material('Kibble ochre','BE8749'),material('Kibble brown','95613A')]
    p=[ell((.099,0,.044),(.049,.049,.022),kibble[0],12,6)]
    for j in range(-4,5):
        for i in range(-4,5):
            x=.013*(i+.5*(j%2)); y=.0112*j
            r=math.hypot(x,y)
            if r >= .049:
                continue
            z=.058+.020*math.sqrt(1-(r/.054)**2)
            p.append(ell((.099+x+rng.uniform(-.0008,.0008),y+rng.uniform(-.0008,.0008),z),
                         (.0064,.0057,.0048),kibble[(i+j)%3],8,4))
    join('food',p,(.099,0,.023))
    water=material('Still blue water','94C3CE',.22)
    join('water',[cylinder((-.099,0,.023),(-.099,0,.056),.057,water,48,.0008)],(-.099,0,.023))


def build_cat_tree():
    rope=material('Natural sisal','CEAB7A')
    rope_high=material('Sisal raised cords','DEC193')
    p=[cylinder((0,0,0),(0,0,.046),.23,WOOD,64,.008),cylinder((0,0,.042),(0,0,.052),.222,LIGHTWOOD,64,.004)]
    for x,y,h,r in [(.077,.061,.81,.044),(-.105,-.070,.395,.040)]:
        p.append(cylinder((x,y,.050),(x,y,h),r,rope,32,.003))
        turns=round((h-.055)/.012)
        pts=[(x+(r+.001)*math.cos(TAU*t/10),y+(r+.001)*math.sin(TAU*t/10),.057+(h-.064)*t/(turns*10)) for t in range(turns*10+1)]
        p.append(tube(pts,.0035,rope_high,5))
    for x,y,z,r in [(-.105,-.070,.406,.151),(.077,.061,.826,.173)]:
        p.append(cylinder((x,y,z-.016),(x,y,z+.016),r,WOOD,48,.008))
        p.append(ring((x,y,z+.007),r-.001,r-.001,.004,LIGHTWOOD))
        p.append(ell((x,y,z+.024),(r-.014,r-.014,.021),CREAM,40,12))
        p.append(ring((x,y,z+.017),r-.014,r-.014,.0028,SEAM))
    # Padded top bed, with a real low entrance on its front side.
    n=56
    verts=[]
    for row in range(4):
        for i in range(n):
            a=TAU*i/n
            front=max(0,(-math.sin(a)-.25)/.75)
            z=.848 if row in (0,3) else .948-.068*front**5
            r=.172 if row<2 else .151
            verts.append((.077+r*math.cos(a),.061+r*math.sin(a),z))
    faces=[]
    for row in range(4):
        for i in range(n):
            j=(i+1)%n
            faces.append((row*n+i,row*n+j,((row+1)%4)*n+j,((row+1)%4)*n+i))
    p.append(bevel(mesh(verts,faces,LIGHTWOOD),.004,2))
    rim=[(.077+.162*math.cos(TAU*i/n),.061+.162*math.sin(TAU*i/n),.948-.068*max(0,(-math.sin(TAU*i/n)-.25)/.75)**5) for i in range(n)]
    p.append(tube(rim,.004,SEAM,6,True))
    join('tree',p)
    anchor('perch0',(-.105,-.070,.451),CREAM)
    anchor('perch1',(.077,.061,.871),CREAM)
    at=(.207,-.044,.830)
    p=[tube([at,(.207,-.044,.626)],.0015,DARK,6),ell((.207,-.044,.610),(.025,.025,.026),SEAM,16,10)]
    for i in range(18):
        a=TAU*i/18
        z=.610+.018*math.sin(i*2.4)
        r=math.sqrt(max(0,.025**2-(z-.610)**2))
        p.append(ell((.207+r*math.cos(a),-.044+r*math.sin(a),z),(.006,)*3,CREAM,8,6))
    join('toy',p,at)


def build_floor_lamp():
    p=[lathe((0,0,0),[(0,0),(.124,0),(.139,.009),(.139,.018),(.129,.029),(.074,.036),(0,.036)],BRASS)]
    p.append(cylinder((0,0,.025),(0,0,1.18),.009,BRASS,24,.002))
    p.append(cylinder((0,0,1.15),(0,0,1.22),.024,DARK,24,.002))
    for a in (0,TAU/3,TAU*2/3):
        p.append(tube([(0,0,1.245),(.18*math.cos(a),.18*math.sin(a),1.17)],.002,BRASS))
    # Pull chain ends below the shade, warm metal bead links.
    p.append(tube([(.061,0,1.20),(.061,0,1.029)],.0008,BRASS))
    for i in range(16):
        p.append(ell((.061,0,1.03+i*.010),(.0018,)*3,BRASS,8,4))
    p.append(ell((.061,0,1.018),(.006,.006,.009),BRASS,12,8))
    join('lamp',p)
    linen=material('Warm linen shade','E8CB91')
    thread=material('Linen weave','DFC08A')
    p=[lathe((0,0,0),[(.184,1.168),(.185,1.448),(.179,1.448),(.178,1.168),(.184,1.168)],linen,64)]
    p.extend([ring((0,0,z),.182,.182,.0035,LIGHTWOOD,64) for z in (1.170,1.445)])
    for i in range(72):
        a=TAU*i/72
        p.append(tube([(.1853*math.cos(a),.1853*math.sin(a),1.18),(.186*math.cos(a),.186*math.sin(a),1.437)],.00065,thread,4))
    join('shade',p)
    join('bulb',[ell((0,0,1.270),(.036,.036,.052),material('Warm bulb','FFF0C1',.4),24,16)])


def build_candle():
    amber=material('Amber jar','A56832',.25)
    amber.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=.15
    amber.node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value=1.45
    amberlip=material('Amber glass edge','C0823E',.24)
    p=[lathe((0,0,0),[(0,0),(.029,0),(.039,.006),(.040,.017),(.040,.078),(.035,.086),(.035,.096),(.030,.097),(.030,.088),(.034,.079),(.034,.016),(.028,.008),(0,.008)],amber)]
    for z in (.086,.093):
        p.append(ring((0,0,z),.035,.035,.0018,amberlip))
    label=material('Candle parchment label','D4B48D')
    verts=[]
    for z in (.020,.066):
        for i in range(17):
            a=-math.pi/2-.9+1.8*i/16
            verts.append((.0404*math.cos(a),.0404*math.sin(a),z))
    p.append(mesh(verts,[(i,i+1,i+18,i+17) for i in range(16)],label))
    join('jar',p)
    join('wax',[cylinder((0,0,.015),(0,0,.085),.030,material('Candle wax','F3D698'),40,.001)])
    join('wick',[tube([(0,0,.084),(0,0,.091),(.001,0,.096)],.001,BLACK)],(.001,0,.096))


def build_radio():
    p=[cube((0,0,.104),(.30,.13,.185),WOOD,.022)]
    # Raised front bezel and inset grille sit on the solid wooden chassis.
    p.append(cube((0,-.066,.111),(.274,.010,.161),DARK,.015))
    p.append(cube((0,-.073,.112),(.263,.007,.150),LIGHTWOOD,.011))
    grille=material('Speaker woven cloth','B79A72')
    p.append(cube((0,-.078,.139),(.240,.006,.086),grille,.006))
    thread=material('Speaker warm weave','C8AD83')
    thread2=material('Speaker shadow weave','9B7D59')
    for i in range(54):
        x=-.117+i*.0044
        p.append(tube([(x,-.0814,.100),(x,-.0814,.179)],.00065,thread,4))
    for i in range(19):
        z=.101+i*.00425
        p.append(tube([(-.117,-.0817,z),(.117,-.0817,z)],.00055,thread2,4))
    p.append(cube((0,-.077,.091),(.246,.009,.008),WOOD,.003))
    p.append(cube((0,-.078,.058),(.152,.009,.030),DARK,.004))
    for x in (-.105,.105):
        for y in (-.041,.041):
            p.append(cube((x,y,.008),(.035,.039,.016),DARK,.005))
    # Fine, restrained wood grain, also visible from behind.
    for i in range(7):
        y=-.045+i*.014
        p.append(tube([(-.119+j*.238/20,y+.002*math.sin(j*.5+i),.1972) for j in range(21)],.00055,GRAIN,4))
    for i in range(5):
        z=.053+i*.025
        p.append(tube([(-.122+j*.244/20,.0653,z+.002*math.sin(j*.45+i)) for j in range(21)],.0006,GRAIN,4))
    join('radio',p)
    dial=material('Amber tuning window','EDB76E')
    marks=material('Dial ink','AB6639')
    p=[cube((0,-.084,.058),(.139,.003,.021),dial,.002)]
    p.append(tube([(-.062,-.086,.057),(.062,-.086,.057)],.00055,marks,4))
    for i in range(11):
        x=-.059+i*.0118
        p.append(tube([(x,-.086,.054),(x,-.086,.062 if i%2==0 else .059)],.0005,marks,4))
    p.append(cube((.018,-.087,.058),(.0013,.001,.019),CREAM,.0002))
    join('dial',p)
    for x,name in [(.108,'knobL'),(-.108,'knobR')]:
        p=[cylinder((x,-.080,.058),(x,-.088,.058),.017,DARK,32),cylinder((x,-.086,.058),(x,-.100,.058),.0135,LIGHTWOOD,32,.002)]
        p.append(tube([(x,-.101,.064),(x,-.101,.069)],.0009,CREAM))
        join(name,p,(x,-.094,.058))


def build_yarn():
    from mathutils import Quaternion
    q=Quaternion(Vector((1,.4,0)).normalized(),.55)
    p=[ell((0,0,0),(.047,)*3,PINK,32,20)]
    # Closely wound bands form the base layer; the crossing front bundle sits
    # above it, so intersections read as layered yarn rather than spikes.
    for j in range(1,18):
        theta=math.pi*j/18
        pts=[q@Vector((.047*math.sin(theta)*math.cos(TAU*k/40),
                      .047*math.cos(theta),
                      .047*math.sin(theta)*math.sin(TAU*k/40))) for k in range(40)]
        p.append(tube(pts,.00135,PINKLIGHT,6,True))
    q2=Quaternion(Vector((0,1,0)),.65)
    for j in range(6):
        offset=(j-2.5)*.006
        rr=math.sqrt(.0495**2-offset**2)
        pts=[]
        for k in range(25):
            a=.18+(math.pi-.36)*k/24
            # The tips tuck beneath the base layer.
            r=rr-.004*abs(2*k/24-1)**8
            pts.append(q2@Vector((offset,-r*math.sin(a),r*math.cos(a))))
        p.append(tube(pts,.0018,PINKLIGHT,6))
    p.append(tube([(.022,-.035,-.026),(.037,-.034,-.030),(.048,-.018,-.031),(.045,.001,-.034)],.0018,PINKLIGHT,6))
    join('ball',p)


def build_watering_can():
    p=[lathe((-.045,0,0),[(0,0),(.065,0),(.071,.008),(.071,.099),(.066,.112),(.060,.113),(.060,.105),(.065,.097),(.064,.010),(0,.010)],GREEN)]
    for z,r in [(.009,.069),(.022,.071),(.089,.071),(.111,.064)]:
        p.append(ring((-.045,0,z),r,r,.0024,GREENTRIM))
    # Spout is a tapered, truly hollow pipe rising from the body.
    start=Vector((.012,0,.035)); end=Vector((.157,0,.141))
    d=(end-start).normalized(); q=Vector((0,0,1)).rotation_difference(d)
    sp=lathe((0,0,0),[(.018,0),(.009,(end-start).length),(.006,(end-start).length),(.014,0),(.018,0)],GREEN,32)
    sp.rotation_mode='QUATERNION'; sp.rotation_quaternion=q; sp.location=start; p.append(sp)
    rose=lathe((0,0,0),[(.009,-.016),(.030,0),(.030,.004),(.027,.007),(.025,.004),(.026,.001),(.007,-.012),(.006,-.016),(.009,-.016)],GREEN,32)
    rose.rotation_mode='QUATERNION'; rose.rotation_quaternion=q; rose.location=end; p.append(rose)
    # Perforated rose face: actual holes, boolean cut before joining.
    face=cylinder(end+d*.004,end+d*.008,.0265,GREENTRIM,32,.0005)
    active(face)
    for i in range(13):
        a=TAU*i/12; r=.017 if i<12 else 0
        at=end+q@Vector((r*math.cos(a),r*math.sin(a),.006))
        cutter=cylinder(at-d*.007,at+d*.007,.0017,None,8,0)
        active(face)
        mod=face.modifiers.new('Rose perforation','BOOLEAN'); mod.operation='DIFFERENCE'; mod.object=cutter
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter,do_unlink=True)
    p.append(face)
    # Arch over top and open side handle.
    pts=[(-.045,-.056*math.cos(math.pi*i/24),.101+.073*math.sin(math.pi*i/24)) for i in range(25)]
    p.append(tube(pts,.006,GREENTRIM,8))
    pts=[(-.105-.054*math.sin(math.pi*i/24),0,.096-.077*i/24) for i in range(25)]
    p.append(tube(pts,.006,GREEN,8))
    for part in p:
        part.location.x += .045
    join('can',p)
    anchor('spoutTip',end+d*.008+Vector((.045,0,0)),GREENTRIM)


def build_bird_feeder():
    # All coordinates measured downward from the hanging hook.
    p=[tube([(.011*math.cos(-.3+3.6*i/20),0,-.012+.011*math.sin(-.3+3.6*i/20)) for i in range(21)]+[(-.004,0,-.029),(0,0,-.036),(0,0,-.066)],.0018,BRASS,8)]
    p.append(cube((0,0,-.191),(.142,.107,.012),LIGHTWOOD,.003))
    p.append(cube((0,.040,-.140),(.112,.008,.094),WOOD,.002))
    # Corner posts leave the whole feeding face open.
    for x in (-.054,.054):
        for y in (-.039,.037):
            p.append(beam((x,y,-.184),(x,y,-.104),.008,.008,LIGHTWOOD))
    for s in (-1,1):
        o=cube((s*.037,0,-.091),(.086,.128,.009),LIGHTWOOD,.002)
        o.rotation_euler.y=s*.52
        p.append(o)
        for j in range(4):
            y=-.051+j*.034
            p.append(tube([(0,y,-.064),(s*.073,y,-.106)],.0006,GRAIN,4))
    for y in (-.050,.050):
        p.append(cube((0,y,-.178),(.137,.006,.014),WOOD,.001))
    for x in (-.068,.068):
        p.append(cube((x,0,-.178),(.006,.10,.014),WOOD,.001))
    p.append(cylinder((-.085,-.066,-.177),(.085,-.066,-.177),.004,LIGHTWOOD,16))
    for x in (-.048,.048):
        p.append(beam((x,-.040,-.186),(x,-.067,-.177),.005,.005,WOOD))
    seed=material('Golden seeds','D3A35C')
    for i in range(45):
        p.append(ell((rng.uniform(-.060,.060),rng.uniform(-.037,.037),-.182),(.0023,.0032,.0016),seed,8,4))
    join('feeder',p)
    anchor('perchL',(.045,-.066,-.1725))
    anchor('perchR',(-.045,-.066,-.1725))


def build_bird():
    brown=material('Sparrow chestnut','A7724C')
    cream=material('Sparrow warm belly','E7D3AE')
    feather=material('Sparrow feathers','87573E')
    p=[ell((0,.004,.029),(.025,.030,.026),brown,28,18)]
    p.append(ell((0,-.010,.027),(.023,.022,.024),cream,24,16))
    for x in (-.009,.009):
        p.append(cylinder((x,-.002,.012),(x,-.005,.003),.0016,BRASS,10,.0003))
        for dx in (-.003,0,.003):
            p.append(tube([(x,-.005,.002),(x+dx,-.013,.0014)],.0011,BRASS,5))
    for i in range(3):
        o=ell(((i-1)*.006,.034,.025),(.005,.019,.004),feather,12,8)
        o.rotation_euler.x=.28
        p.append(o)
    join('body',p)
    p=[ell((0,-.018,.052),(.021,.020,.020),brown,28,18)]
    p.append(ell((0,-.031,.046),(.018,.012,.012),cream,20,12))
    for s in (-1,1):
        p.append(ell((s*.015,-.033,.056),(.0042,.0030,.0045),BLACK,16,10))
        p.append(ell((s*.0145,-.0354,.0574),(.0011,.0008,.0011),CREAM,8,6))
        p.append(ell((s*.016,-.031,.045),(.0044,.003,.0036),feather,12,8))
    beak=material('Sparrow beak','77523A')
    p.append(bevel(mesh([(-.0045,-.040,.050),(.0045,-.040,.050),(0,-.040,.0435),(0,-.052,.047)],[(0,1,3),(1,2,3),(2,0,3),(0,2,1)],beak),.0005,2))
    join('head',p,(0,-.013,.040))
    for s,name in [(1,'wingL'),(-1,'wingR')]:
        p=[ell((s*.022,.009,.032),(.007,.023,.015),feather,20,12)]
        for i in range(3):
            o=ell((s*.027,.006+i*.008,.027-i*.001),(.0017,.008,.0035),LIGHTWOOD,12,8)
            o.rotation_euler.x=-.5
            p.append(o)
        join(name,p,(s*.020,-.006,.039))
    # Final bill-to-tail length is 8.5 cm; scale joint anchors with the meshes.
    for o in bpy.context.scene.objects:
        o.location *= .82
        for v in o.data.vertices:
            v.co *= .82



def build_wind_chime():
    p=[tube([(0,0,0),(-.004,0,-.010),(0,0,-.023),(.004,0,-.010),(0,0,0)],.0012,DARK,6)]
    for i in range(3):
        a=TAU*i/3
        p.append(tube([(0,0,-.022),(.047*math.cos(a),.047*math.sin(a),-.073)],.0008,DARK,5))
    p.append(cylinder((0,0,-.080),(0,0,-.072),.052,LIGHTWOOD,48,.002))
    p.append(ring((0,0,-.076),.052,.052,.0015,WOOD))
    join('top',p)
    pastels=['C8A1AD','CBB2C5','A4BEBC','D6B5B7','B5BFCB']
    for i,length in enumerate([.105,.080,.145,.120,.160]):
        a=TAU*i/5
        x,y=.037*math.cos(a),.037*math.sin(a)
        at=(x,y,-.080)
        mat=material('Chime pastel '+str(i),pastels[i],.4,.25)
        p=[tube([at,(x,y,-.102)],.00065,DARK,5)]
        p.append(lathe((x,y,-.102-length),[(.0037,0),(.0048,.001),(.0048,length),(.0033,length),(.0033,0),(.0037,0)],mat,20))
        join('tube'+str(i),p,at)
    p=[tube([(0,0,-.080),(0,0,-.258)],.0007,DARK,5),cylinder((0,0,-.158),(0,0,-.153),.022,WOOD,32,.001)]
    # Thin wooden teardrop sail below the clapper.
    outline=[(0,-.258),(.014,-.278),(.009,-.295),(0,-.300),(-.009,-.295),(-.014,-.278)]
    verts=[(x,y,z) for y in (-.0015,.0015) for x,z in outline]
    p.append(bevel(mesh(verts,[tuple(range(5,-1,-1)),tuple(range(6,12))]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)],LIGHTWOOD),.001,2))
    join('clapper',p,(0,0,-.080))


def build_easel():
    p=[]
    for s in (-1,1):
        p.append(beam((s*.245,-.09,.016),(s*.150,.065,1.075),.043,.037,LIGHTWOOD))
    p.append(beam((0,.305,.015),(0,.069,1.015),.043,.041,WOOD))
    p.append(beam((0,.065,.43),(0,.102,1.25),.038,.031,LIGHTWOOD))
    for z in (.24,.48):
        p.append(cube((0,-.020,z),(.398,.033,.039),WOOD,.004))
    # Canvas front is a dedicated flat UV-mapped surface facing -Y.
    p.append(cube((0,-.053,.504),(.575,.122,.029),LIGHTWOOD,.005))
    p.append(cube((0,-.112,.524),(.575,.019,.041),WOOD,.004))
    p.append(cube((0,-.057,1.136),(.12,.068,.033),WOOD,.004))
    p.append(cylinder((0,.073,1.19),(0,.065,1.19),.010,DARK,20,.001))
    for x in (-.175,.175):
        p.append(ell((x,-.040,.246),(.004,.002,.004),BRASS,8,6))
    # Palette with an actual thumb hole, plus raised paint dabs.
    palette=ell((.198,-.109,.550),(.075,.046,.007),LIGHTWOOD,32,10)
    cutter=cylinder((.174,-.097,.533),(.174,-.097,.568),.011,None,24,0)
    active(palette)
    mod=palette.modifiers.new('Thumb hole','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    p.append(palette)
    for x,y,color in [(.230,-.090,'B27E70'),(.238,-.118,'8BA18E'),(.211,-.137,'B5C8CF'),(.186,-.133,'D8B56F')]:
        p.append(ell((x,y,.557),(.011,.008,.0025),material('Palette '+color,color),12,8))
    join('easel',p)
    canvas=material('Blank warm canvas','EFE5D4')
    p=[cube((0,-.042,.831),(.508,.026,.608),WOOD,.005)]
    verts=[(-.25,-.0555,.535),(.25,-.0555,.535),(.25,-.0555,1.135),(-.25,-.0555,1.135)]
    front=mesh(verts,[(0,1,2,3)],canvas,False)
    uv=front.data.uv_layers.new(name='UVMap')
    # Conventional front-view mapping: lower left (0,0), upper right (1,1).
    for loop,xy in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):
        loop.uv=xy
    p.append(front)
    join('canvas',p)
    # Footprint is centred between the front feet and the rear tripod foot.
    objects=list(bpy.context.scene.objects)
    floor=min((o.matrix_world@v.co).z for o in objects for v in o.data.vertices)
    for o in objects:
        for v in o.data.vertices:
            v.co += Vector((0,-.105,-floor))


BUILDERS = {name: globals()['build_'+name] for name in (
    'box','bowls','cat_tree','floor_lamp','candle','radio','yarn',
    'watering_can','bird_feeder','bird','wind_chime','easel')}
EXPECTED = {
    'box': ['box'], 'bowls': ['mat','foodBowl','food','waterBowl','water'],
    'cat_tree': ['tree','perch0','perch1','toy'], 'floor_lamp': ['lamp','shade','bulb'],
    'candle': ['jar','wax','wick'], 'radio': ['radio','dial','knobL','knobR'],
    'yarn': ['ball'], 'watering_can': ['can','spoutTip'],
    'bird_feeder': ['feeder','perchL','perchR'], 'bird': ['body','head','wingL','wingR'],
    'wind_chime': ['top','tube0','tube1','tube2','tube3','tube4','clapper'],
    'easel': ['easel','canvas'],
}


def main():
    selected = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(BUILDERS)
    for name in selected:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        bpy.context.scene.cursor.location = (0,0,0)
        rng.seed(1704)
        BUILDERS[name]()
        objs=list(bpy.context.scene.objects)
        assert sorted(o.name for o in objs) == sorted(EXPECTED[name]), (name,[o.name for o in objs])
        count=0
        for o in objs:
            assert o.type == 'MESH' and not o.modifiers
            o.data.calc_loop_triangles()
            count+=len(o.data.loop_triangles)
        assert count < (20000 if name == 'cat_tree' else 12000), (name,count)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.export_scene.gltf(filepath=str(OUT/(name+'.glb')), export_format='GLB',
            use_selection=True, export_animations=False, export_skins=False, export_apply=True)
        print(f'PROP {name}: {count} triangles; objects: '+', '.join(o.name for o in objs),flush=True)


if __name__ == '__main__':
    main()
