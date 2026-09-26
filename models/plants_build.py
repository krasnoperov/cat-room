"""Deterministic, texture-free houseplants. Blender Z up; -Y faces the room.

Run: blender -b --factory-startup -P models/plants_build.py
Optionally append -- --plant monstera (or lemon / pothos).
All meshes are baked, closed surfaces; the only nodes are the growth contract.
"""
import argparse
import math
import random
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

ROOT = Path(__file__).resolve().parent
TAU = math.tau


def color(hex_rgb):
    rgb = [int(hex_rgb[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in rgb) + (1,)


def mix(a, b, t):
    return tuple(x * (1 - t) + y * t for x, y in zip(a, b))


GREEN = [color(h) for h in ('507D37', '648E3D', '416D36')]
VEIN = color('94AD51')
STEM = color('638242')
GOLD = color('D7CE55')
CREAM = color('EED9AC')
SOIL = color('60402C')


class Mesh:
    """Accumulate parts directly into one growable object, with no helper nodes."""
    def __init__(self):
        self.v, self.f, self.c = [], [], []

    def vert(self, p, c):
        self.v.append(tuple(p))
        self.c.append(c)
        return len(self.v) - 1

    def face(self, *indices):
        self.f.append(indices)

    def object(self, name, origin=(0, 0, 0)):
        origin = Vector(origin)
        me = bpy.data.meshes.new(name)
        me.from_pydata([Vector(v) - origin for v in self.v], [], self.f)
        me.update()
        attr = me.color_attributes.new(name='Col', type='FLOAT_COLOR', domain='POINT')
        me.color_attributes.active_color = attr
        for datum, c in zip(attr.data, self.c):
            datum.color = c
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-7)
        bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1e-8)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me)
        bm.free()
        for p in me.polygons:
            p.use_smooth = True
        o = bpy.data.objects.new(name, me)
        bpy.context.collection.objects.link(o)
        o.location = origin
        me.materials.append(bpy.data.materials['PlantPalette'])
        return o

    def tube(self, points, radii, c, sides=7):
        pts = [Vector(p) for p in points]
        start = len(self.v)
        for i, p in enumerate(pts):
            tangent = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
            u = tangent.cross(Vector((0, 1, 0)))
            if u.length < .1:
                u = tangent.cross(Vector((1, 0, 0)))
            u.normalize()
            v = tangent.cross(u).normalized()
            radius = radii[i] if isinstance(radii, list) else radii
            for j in range(sides):
                a = TAU * j / sides
                self.vert(p + radius * (u * math.cos(a) + v * math.sin(a)), c)
        for i in range(len(pts) - 1):
            for j in range(sides):
                a = start + i * sides + j
                b = start + i * sides + (j + 1) % sides
                self.face(a, b, b + sides, a + sides)
        self.face(*[start + j for j in reversed(range(sides))])
        self.face(*[start + (len(pts) - 1) * sides + j for j in range(sides)])

    def ellipsoid(self, centre, radii, c, rings=8, sides=12, axis=None):
        centre = Vector(centre)
        rotation = Vector((0, 0, 1)).rotation_difference(Vector(axis).normalized()) if axis else None
        start = len(self.v)
        # Unique poles keep meshes manifold and avoid zero-area triangles.
        def point(p):
            p = Vector(p)
            return centre + (rotation @ p if rotation else p)
        bottom = self.vert(point((0, 0, -radii[2])), c)
        for i in range(1, rings):
            lat = -math.pi / 2 + math.pi * i / rings
            for j in range(sides):
                a = TAU * j / sides
                p = (radii[0] * math.cos(lat) * math.cos(a), radii[1] * math.cos(lat) * math.sin(a), radii[2] * math.sin(lat))
                self.vert(point(p), mix(c, color('FFF0BD'), .10 * max(0, math.cos(a + 1)) * math.cos(lat)))
        top = self.vert(point((0, 0, radii[2])), c)
        for j in range(sides):
            nj = (j + 1) % sides
            self.face(bottom, start + 1 + nj, start + 1 + j)
            for i in range(rings - 2):
                a = start + 1 + i * sides
                self.face(a + j, a + nj, a + sides + nj, a + sides + j)
            a = start + 1 + (rings - 2) * sides
            self.face(a + j, a + nj, top)


def bezier(a, b, c, d, steps=14):
    a, b, c, d = map(Vector, (a, b, c, d))
    return [a * (1 - t) ** 3 + 3 * b * t * (1 - t) ** 2 + 3 * c * t * t * (1 - t) + d * t ** 3
            for t in [i / steps for i in range(steps + 1)]]


def inside(p, poly):
    x, y = p
    hit = False
    for a, b in zip(poly, poly[1:] + poly[:1]):
        if (a[1] > y) != (b[1] > y) and x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]:
            hit = not hit
    return hit


def leaf(mesh, base, direction, normal, length, width, shade, kind='oval', seed=0):
    """Triangulated curved blades, with boundary-constrained real fenestrations."""
    base, d, n = Vector(base), Vector(direction).normalized(), Vector(normal).normalized()
    u = d.cross(n).normalized()
    n = u.cross(d).normalized()
    def surface(x, t, lift=0):
        return base + u * (x * width) + d * (t * length) + n * (length * (.11 * math.sin(math.pi * t) - .17 * t * t) + width * .27 * x * x + lift)

    outline = []
    count = 120 if kind == 'monstera' else (12 if kind == 'oval' else 20)
    for side in (1, -1):
        seq = range(count + 1) if side == 1 else range(count - 1, 0, -1)
        for i in seq:
            t = i / count
            w = math.sin(math.pi * t) ** (.48 if kind != 'oval' else .70) * (.68 - .26 * t)
            y = t - (.36 * math.sin(math.pi * t) ** .48 * (1 - t) ** 2 if kind != 'oval' else 0)
            if kind == 'monstera':
                w *= 1 + .045 * side * math.sin(seed * 1.6 + t * 5)
                splits = (.29, .48, .65, .80) if seed < 6 else ((.38, .65) if seed == 6 else (.43,))
                for k, pos in enumerate(splits):
                    offset = .008 * math.sin(seed * 2 + k)
                    cut = (.65 + .06 * math.sin(seed + k)) * math.exp(-((t - pos - side * .012 - offset) / .020) ** 2)
                    w *= 1 - cut
                    y -= .13 * cut
            outline.append((side * w, y))
    if kind == 'monstera':
        # Round each cut's root and each finger, keeping the cuts open.
        rounded = []
        for a, b in zip(outline, outline[1:] + outline[:1]):
            rounded.extend([(a[0] * .75 + b[0] * .25, a[1] * .75 + b[1] * .25),
                            (a[0] * .25 + b[0] * .75, a[1] * .25 + b[1] * .75)])
        outline = rounded
    holes = []
    if kind == 'monstera':
        hole_positions = [(-1, .20), (1, .31), (-1, .49)] if seed < 6 else [(1, .27)]
        for side, y in hole_positions:
            holes.append([(side * .105 + .023 * math.cos(a), y + .038 * math.sin(a)) for a in [TAU * j / 12 for j in range(12)]])
    coords, edges = [], []
    for loop in [outline] + holes:
        start = len(coords)
        coords.extend(Vector(p) for p in loop)
        edges.extend((start + i, start + (i + 1) % len(loop)) for i in range(len(loop)))
    rows = 10 if kind == 'monstera' else (4 if kind == 'oval' else 7)
    for j in range(1, rows):
        t = j / rows
        for i in (range(-1, 2) if kind == 'oval' else range(-4, 5)):
            p = (i * (.22 if kind == 'oval' else .1), t)
            if inside(p, outline) and not any(inside(p, h) for h in holes):
                coords.append(Vector(p))
    verts, _, faces, _, _, _ = delaunay_2d_cdt(coords, edges, [], 0, 1e-7, False)
    faces = [f for f in faces if inside(sum((verts[i] for i in f), Vector((0, 0))) / 3, outline)
             and not any(inside(sum((verts[i] for i in f), Vector((0, 0))) / 3, h) for h in holes)]
    used = sorted({i for f in faces for i in f})
    ids = {}
    for i in used:
        x, t = verts[i]
        highlight = math.exp(-((x + .23) / .14) ** 2 - ((t - .28) / .29) ** 2)
        c = mix(shade, color('ACC266'), .42 * highlight + .10 * max(0, -x * 2))
        if kind == 'pothos':
            streak = abs(x - .10 * math.sin(t * 8 + seed)) < .07 + .05 * math.sin(t * 13 + seed)
            if streak or (x > .15 and .22 < t < .48):
                c = mix(c, GOLD, .88)
        ids[i] = (mesh.vert(surface(x, t, .0006), c), mesh.vert(surface(x, t, -.0006), mix(c, GREEN[2], .14)))
    boundary = {}
    for f in faces:
        mesh.face(*[ids[i][0] for i in f])
        mesh.face(*[ids[i][1] for i in reversed(f)])
        for a, b in zip(f, f[1:] + f[:1]):
            key = tuple(sorted((a, b)))
            boundary[key] = boundary.get(key, 0) + 1
    for (a, b), count in boundary.items():
        if count == 1:
            mesh.face(ids[a][0], ids[b][0], ids[b][1], ids[a][1])
    radius = .0013 if kind == 'monstera' else .00055
    vein_ts = (0, .3, .65, .93) if kind == 'oval' else (0, .15, .35, .55, .75, .93)
    mesh.tube([surface(0, t, .001) for t in vein_ts], radius, VEIN, 4 if kind == 'oval' else 5)
    if kind == 'monstera':
        for t in (.12, .32, .50, .68):
            for side in (-1, 1):
                mesh.tube([surface(0, t, .001), surface(side * .17, t + .035, .001), surface(side * .29, t + .085, .001)], .00065, mix(VEIN, shade, .4), 5)


def pot(width, height, terracotta=False):
    m = Mesh()
    r = width / 2
    profile = [(0, 0), (.66, 0), (.71, .018), (.74, .07), (.79, .13), (.91, .74), (.94, .80),
               (.98, .81), (1, .84), (1, .94), (.98, .98), (.94, 1), (.89, .98), (.88, .94), (.87, .86),
               (.83, .83), (.70, .12), (0, .12)]
    if not terracotta:
        profile = [(0, 0), (.60, 0), (.67, .018), (.69, .04), (.69, .07), (.77, .10),
                   (.84, .18), (.93, .36), (.98, .60), (1, .83), (.995, .92), (.98, .97),
                   (.95, 1), (.90, 1), (.87, .97), (.87, .92), (.88, .86), (.85, .78), (.66, .16), (0, .16)]
    base = color('C97545') if terracotta else CREAM
    sides = 48
    for j, (rr, z) in enumerate(profile):
        for i in range(sides):
            a = TAU * i / sides
            c = mix(base, color('FFEAC1'), .09 * max(0, math.cos(a + 2)))
            if j in (2, 3, 6):
                c = mix(c, color('8E552F') if terracotta else color('B59B76'), .16)
            if not terracotta:
                angle = math.atan2(math.sin(a + 2.15), math.cos(a + 2.15))
                shine = math.exp(-(angle / .20) ** 4 - ((z - .54) / .25) ** 4)
                c = mix(c, color('FFF4D8'), .68 * shine)
            m.vert((r * rr * math.cos(a), r * rr * math.sin(a), z * height), c)
    for j in range(len(profile) - 1):
        for i in range(sides):
            a, b = j * sides + i, j * sides + (i + 1) % sides
            m.face(a, b, b + sides, a + sides)
    m.ellipsoid((0, 0, height * .865), (r * .855, r * .855, .012), SOIL, 6, 40)
    rng = random.Random(81)
    for _ in range(18):
        a, rr = rng.uniform(0, TAU), r * math.sqrt(rng.uniform(.05, .60))
        m.ellipsoid((rr * math.cos(a), rr * math.sin(a), height * .88), (.009, .007, .004), color('795039'), 4, 7)
    m.object('pot')


def monstera():
    pot(.34, .30, True)
    # First four leaves span the whole silhouette, even at the juvenile stage.
    specs = [(-.22, -.03, .68, -.35, -.55, -.65, .29, .29),
             (.18, .04, .86, .45, -.40, -.60, .32, .33),
             (-.05, .08, .97, -.20, -.68, -.56, .33, .35),
             (.24, -.05, .61, .55, -.50, -.60, .28, .28),
             (-.20, .11, .80, -.65, .22, -.48, .27, .29),
             (.06, .17, .81, .30, .60, -.42, .28, .29),
             (-.13, -.10, .49, -.20, -.65, -.63, .21, .22),
             (.12, -.12, .52, .60, -.40, -.59, .22, .23)]
    for i, (x, y, z, dx, dy, dz, length, width) in enumerate(specs):
        m = Mesh()
        start = (x * .10, y * .10, .266)
        end = (x, y, z)
        m.tube(bezier(start, (x * .35, y * .4, .49), (x * .85, y * .85, z + .045), end), [.006 - .002 * j / 14 for j in range(15)], STEM)
        leaf(m, end, (dx, dy, dz), (x * 2.5, -1 if i < 4 or i > 5 else .8, .7), length, width, GREEN[i % 3], 'monstera', i)
        m.object('leaf' + str(i), start)
    m = Mesh()
    start = (.015, -.04, .266)
    m.tube(bezier(start, (.025, -.08, .46), (.07, -.10, .57), (.07, -.105, .65)), .004, STEM)
    # Open spiral blade, tapered at both ends, rather than a capsule bud.
    start_v = len(m.v)
    rows, cols = 14, 12
    for back in (False, True):
        for j in range(rows + 1):
            t = j / rows
            r = .0015 + .016 * math.sin(math.pi * t) ** .7
            for i in range(cols + 1):
                a = i / cols * math.pi * (1.85 - .85 * t) + .5
                rr = r + (-.0005 if back else .0005)
                m.vert((.07 + .020 * t + rr * math.cos(a), -.105 + rr * math.sin(a), .63 + .16 * t), color('96AC52') if i > 2 else color('B8C56B'))
    layer = (rows + 1) * (cols + 1)
    for j in range(rows):
        for i in range(cols):
            a = start_v + j * (cols + 1) + i
            b = a + cols + 1
            m.face(a, a + 1, b + 1, b)
            m.face(a + layer, b + layer, b + 1 + layer, a + 1 + layer)
    for j in range(rows):
        for i in (0, cols):
            a = start_v + j * (cols + 1) + i
            b = a + cols + 1
            m.face(a, b, b + layer, a + layer)
    for j in (0, rows):
        for i in range(cols):
            a = start_v + j * (cols + 1) + i
            m.face(a, a + 1, a + 1 + layer, a + layer)
    m.object('leaf8', start)


def lemon():
    pot(.28, .26)
    rng = random.Random(112)
    trunk, crown = Mesh(), Mesh()
    trunk.tube(bezier((0, 0, .22), (-.011, 0, .40), (.014, 0, .60), (.008, 0, .82)), [.018 - .011 * j / 14 for j in range(15)], color('89603E'), 10)
    centre = Vector((0, 0, .77))
    for k in range(11):
        a = k * 2.39996
        end = centre + Vector((.17 * math.cos(a), .17 * math.sin(a), .13 * math.sin(k * 1.8)))
        trunk.tube(bezier((0, 0, .46 + k * .019), (0, 0, .65), end * .7 + centre * .3, end, 7), [.008 * (1 - j / 9) for j in range(8)], color('89603E'), 6)
    trunk.object('trunk', (0, 0, .224))
    for i in range(128):
        a = i * 2.399963
        z = 1 - 2 * (i + .5) / 128
        r = math.sqrt(1 - z * z)
        outward = Vector((r * math.cos(a), r * math.sin(a), z))
        base = centre + Vector((outward.x * .16, outward.y * .15, outward.z * .13))
        twist = rng.uniform(-.85, .85)
        direction = Vector((math.cos(a + twist) * .7, math.sin(a + twist) * .7, .16 + .65 * z + rng.uniform(-.2, .2))).normalized()
        leaf(crown, base, direction, outward, rng.uniform(.105, .14), rng.uniform(.079, .100), GREEN[i % 3])
    # Blossoms on the front and outer foliage, joined to the crown.
    for p in [(-.17, -.185, .84), (.08, -.20, .90), (.205, -.10, .74), (-.075, -.21, .67)]:
        for j in range(5):
            a = TAU * j / 5
            centre_p = Vector(p) + Vector((math.cos(a) * .009, -.003, math.sin(a) * .009))
            crown.ellipsoid(centre_p, (.005, .0035, .011), color('FFF1CB'), 6, 8, (math.cos(a), 0, math.sin(a)))
        crown.ellipsoid(p, (.005, .005, .005), color('EAC454'), 6, 8)
    crown.object('crown', (0, 0, .57))
    for i, p in enumerate([(-.16, -.195, .79), (.16, -.18, .75), (-.075, -.205, .64), (.08, -.19, .60), (.225, .035, .70), (-.175, .08, .65)]):
        m = Mesh()
        m.ellipsoid(p, (.035, .033, .046), color('F2CE46'), 10, 14, (.15 * math.sin(i), .12, 1))
        m.ellipsoid(Vector(p) + Vector((0, 0, -.044)), (.009, .009, .009), color('EAC13C'), 6, 10)
        m.tube([Vector(p) + Vector((0, 0, .042)), Vector(p) + Vector((.004, .003, .067))], .002, STEM, 6)
        m.object('lemon' + str(i), p)


def pothos():
    pot(.15, .12)
    for k in range(4):
        x = (-.080, -.027, .030, .087)[k]
        count = (12, 11, 10, 11)[k]
        depth = (.54, .47, .41, .53)[k]
        def vine(t):
            if t < .23:
                u = t / .23
                return Vector((x * (.35 + .65 * u) + .012 * math.sin(u * math.pi + k), .018 - .138 * u, .105 + .049 * math.sin(u * math.pi) - .11 * u * u))
            u = (t - .23) / .77
            return Vector((x * (1 + .28 * u) - .012 * math.sin(k) + .022 * (math.sin(u * 8 + k) - math.sin(k)), -.12 - .025 * math.sin(u * math.pi / 2), -.005 - depth * u))
        times = [0, .025, .12, .22] + [.22 + .78 * j / (count - 3) for j in range(1, count - 2)]
        previous = vine(0)
        for i in range(count):
            t = times[i + 1]
            attach = vine(t)
            stem = Mesh()
            stem.tube([vine(times[i] + (t - times[i]) * j / 5) for j in range(6)], .0022 * (1 - .5 * t), STEM, 6)
            stem.object(f'vine{k}_seg{i:02}', previous)
            m = Mesh()
            side = (-1 if (i + k) % 2 else 1)
            tip = attach + Vector((side * .013, -.009, .010))
            m.tube([attach, (attach + tip) / 2, tip], .0015, STEM, 5)
            direction = (side * .65, -.18, -.8) if t > .25 else (side * .5, -.3, .9)
            if i == 0:
                direction = (math.cos(k * 2.4) * .7, math.sin(k * 2.4) * .5, .9)
            normal_x = (-.9, .6 * math.sin(i * 1.7), -.6 * math.sin(i * 1.7), 1.1)[k]
            leaf(m, tip, direction, (normal_x, -1, .25), .105 * (1 - .42 * t), .089 * (1 - .42 * t), GREEN[(k + i) % 3], 'pothos', k * 13 + i)
            m.object(f'vine{k}_leaf{i:02}', attach)
            previous = attach


def export(name):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mat = bpy.data.materials.new('PlantPalette')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    vc = mat.node_tree.nodes.new('ShaderNodeVertexColor')
    vc.layer_name = 'Col'
    mat.node_tree.links.new(vc.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = .63
    globals()[name]()
    objects = list(bpy.context.scene.objects)
    tris = 0
    for o in objects:
        o.data.calc_loop_triangles()
        tris += len(o.data.loop_triangles)
    print(f'{name}: {tris} triangles; objects: ' + ', '.join(sorted(o.name for o in objects)), flush=True)
    assert tris < 30000, f'{name} exceeds triangle budget: {tris}'
    bpy.ops.export_scene.gltf(filepath=str(ROOT / (name + '.glb')), export_format='GLB',
                             export_animations=False, export_skins=False, export_apply=True,
                             export_vertex_color='ACTIVE')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plant', choices=['monstera', 'lemon', 'pothos'])
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    for plant in [args.plant] if args.plant else ['monstera', 'lemon', 'pothos']:
        export(plant)
