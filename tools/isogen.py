# BEIT — isometric cutaway drawing generator
# 2:1 pixel isometric: a-axis -> (+2,+1)*q, b-axis -> (-2,+1)*q, z -> (0,-1)
import math

class Scene:
    def __init__(self, ox, oy, q, ink, paper, system=False):
        self.ox, self.oy, self.q = ox, oy, q
        self.ink, self.paper, self.system = ink, paper, system
        self.items = []  # (sortkey, svg)

    def P(self, a, b, z=0.0):
        return (self.ox + (a - b) * 2 * self.q, self.oy + (a + b) * self.q - z)

    def _pts(self, pts):
        return ' '.join(f'{x:.1f} {y:.1f}' for x, y in pts)

    def _poly(self, pts):
        return 'M' + self._pts([pts[0]]) + ' L ' + ' L '.join(self._pts([p]) for p in pts[1:]) + ' Z'

    def add_raw(self, key, svg):
        self.items.append((key, svg))

    def fill_stroke(self, key, d, w=1.0, fill=None, dash=None, op=None):
        f = fill if fill else self.paper
        cls_f = ' class="axo-fill" opacity="0"' if self.system else ''
        cls_s = ' class="hp" pathLength="1"' if self.system else ''
        dash_a = f' stroke-dasharray="{dash}"' if dash else ''
        op_a = f' opacity="{op}"' if op else ''
        self.items.append((key, f'<path{cls_f} d="{d}" fill="{f}" stroke="none"/>'
                                f'<path{cls_s} d="{d}" fill="none" stroke="{self.ink}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"{dash_a}{op_a}/>'))

    def stroke(self, key, d, w=1.0, dash=None, op=None):
        cls_s = ' class="hp" pathLength="1"' if self.system else ''
        dash_a = f' stroke-dasharray="{dash}"' if dash else ''
        op_a = f' opacity="{op}"' if op else ''
        self.items.append((key, f'<path{cls_s} d="{d}" fill="none" stroke="{self.ink}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"{dash_a}{op_a}/>'))

    def box(self, a0, b0, da, db, z0, h, w=1.0, key=None):
        a1, b1 = a0 + da, b0 + db
        k = key if key is not None else (a1 + b1 + z0 * 0.01)
        top = [self.P(a0,b0,z0+h), self.P(a1,b0,z0+h), self.P(a1,b1,z0+h), self.P(a0,b1,z0+h)]
        fa  = [self.P(a1,b0,z0), self.P(a1,b1,z0), self.P(a1,b1,z0+h), self.P(a1,b0,z0+h)]
        fb  = [self.P(a0,b1,z0), self.P(a1,b1,z0), self.P(a1,b1,z0+h), self.P(a0,b1,z0+h)]
        d = self._poly(top) + ' ' + self._poly(fa) + ' ' + self._poly(fb)
        self.fill_stroke(k, d, w)

    def floor_ellipse(self, a, b, ra, rb, z=0, w=1.0, key=None):
        x, y = self.P(a, b, z)
        k = key if key is not None else (a + b)
        cls_s = ' class="hp" pathLength="1"' if self.system else ''
        self.items.append((k, f'<ellipse{cls_s} cx="{x:.1f}" cy="{y:.1f}" rx="{ra*2.2*self.q:.1f}" ry="{rb*1.1*self.q:.1f}" fill="{self.paper}" stroke="{self.ink}" stroke-width="{w}"/>'))

    def line(self, a0,b0,z0, a1,b1,z1, w=1.0, dash=None, op=None, key=None):
        p0, p1 = self.P(a0,b0,z0), self.P(a1,b1,z1)
        k = key if key is not None else max(a0+b0, a1+b1)
        self.stroke(k, f'M{p0[0]:.1f} {p0[1]:.1f} L{p1[0]:.1f} {p1[1]:.1f}', w, dash, op)

    # ---- furniture ----
    def bed(self, a, b, da, db, key=None):
        k = key if key is not None else a+da+b+db
        self.box(a, b, da, db, 0, 4, key=k)                       # base
        self.box(a+0.6, b+0.6, da-1.2, db-1.2, 4, 2, w=0.8, key=k+0.01)  # mattress
        self.box(a+0.9, b+0.9, 2.0, db-1.8, 6, 1.4, w=0.8, key=k+0.02)   # pillow
        # blanket fold line
        self.line(a+da*0.55, b+0.6, 6.1, a+da*0.55, b+db-0.6, 6.1, w=0.7, key=k+0.03)

    def sofa(self, a, b, da, db, back='b0', key=None):
        k = key if key is not None else a+da+b+db
        self.box(a, b, da, db, 0, 4, key=k)
        if back == 'b0':
            self.box(a, b, da, 1.3, 4, 4.5, w=0.8, key=k+0.01)
            self.box(a, b, 1.3, db, 4, 3, w=0.8, key=k+0.02)
            self.box(a+da-1.3, b, 1.3, db, 4, 3, w=0.8, key=k+0.03)
        else:  # back along a0
            self.box(a, b, 1.3, db, 4, 4.5, w=0.8, key=k+0.01)
            self.box(a, b, da, 1.3, 4, 3, w=0.8, key=k+0.02)
            self.box(a, b+db-1.3, da, 1.3, 4, 3, w=0.8, key=k+0.03)

    def armchair(self, a, b, key=None):
        k = key if key is not None else a+b+6
        self.box(a, b, 3.4, 3.4, 0, 4.5, key=k)
        self.box(a, b, 3.4, 1.1, 4.5, 4.5, w=0.8, key=k+0.01)

    def table(self, a, b, da, db, h=7, key=None):
        k = key if key is not None else a+da+b+db
        self.box(a, b, da, db, h-1.2, 1.2, key=k)
        for (xa, xb) in [(a+0.4,b+0.4),(a+da-0.6,b+0.4),(a+0.4,b+db-0.6),(a+da-0.6,b+db-0.6)]:
            self.line(xa, xb, 0, xa, xb, h-1.2, w=0.7, key=k-0.01)

    def chair(self, a, b, key=None):
        k = key if key is not None else a+b+4
        self.box(a, b, 1.8, 1.8, 0, 4, w=0.8, key=k)
        self.box(a, b, 0.5, 1.8, 4, 3.5, w=0.7, key=k+0.01)

    def round_table(self, a, b, r=2.6, h=7, key=None):
        k = key if key is not None else a+b+3
        x, y = self.P(a, b, 0)
        self.line(a, b, 0, a, b, h, w=0.8, key=k)
        self.floor_ellipse(a, b, r, r, z=h, w=1.0, key=k+0.01)

    def counter(self, a, b, da, db, key=None):
        k = key if key is not None else a+da+b+db
        self.box(a, b, da, db, 0, 9, key=k)
        # sink + hob on top
        self.stroke(k+0.01, self._poly([self.P(a+1.2,b+0.6,9),self.P(a+3.4,b+0.6,9),self.P(a+3.4,b+db-0.6,9),self.P(a+1.2,b+db-0.6,9)]), w=0.7)
        for i in range(2):
            x,y = self.P(a+da-2.2-i*1.8, b+db/2, 9)
            self.items.append((k+0.02, f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.0*self.q:.1f}" fill="none" stroke="{self.ink}" stroke-width="0.7"/>'))

    def wardrobe(self, a, b, da, db, key=None):
        k = key if key is not None else a+da+b+db
        self.box(a, b, da, db, 0, 11, key=k)
        n = max(2, int(da // 3))
        for i in range(1, n):
            aa = a + da * i / n
            self.line(aa, b+db, 0, aa, b+db, 11, w=0.7, key=k+0.01)

    def tub(self, a, b, key=None):
        k = key if key is not None else a+b+4
        self.floor_ellipse(a, b, 3.2, 1.9, z=4, w=1.0, key=k)
        self.floor_ellipse(a, b, 2.4, 1.3, z=4, w=0.7, key=k+0.01)
        # faucet
        self.line(a-2.6, b, 4, a-2.6, b, 10, w=0.8, key=k+0.02)

    def wc(self, a, b, key=None):
        k = key if key is not None else a+b+3
        self.box(a, b, 1.5, 1.3, 0, 4, w=0.8, key=k)
        self.floor_ellipse(a+2.2, b+0.7, 1.1, 0.9, z=3, w=0.8, key=k+0.01)

    def plant(self, a, b, s=1.0, key=None):
        k = key if key is not None else a+b+2
        x, y = self.P(a, b, 0)
        q = self.q * s
        leaves = (f'M{x:.1f} {y-3*q:.1f} q{-2.4*q:.1f} {-3.2*q:.1f} {-4.4*q:.1f} {-2.0*q:.1f}'
                  f'M{x:.1f} {y-3*q:.1f} q{2.4*q:.1f} {-3.4*q:.1f} {4.2*q:.1f} {-1.8*q:.1f}'
                  f'M{x:.1f} {y-3*q:.1f} q{0.4*q:.1f} {-4.4*q:.1f} {-1.2*q:.1f} {-5.6*q:.1f}'
                  f'M{x:.1f} {y-3*q:.1f} q{-0.6*q:.1f} {-3.6*q:.1f} {1.8*q:.1f} {-4.8*q:.1f}')
        pot = f'M{x-1.2*q:.1f} {y-3*q:.1f} L{x+1.2*q:.1f} {y-3*q:.1f} L{x+0.8*q:.1f} {y:.1f} L{x-0.8*q:.1f} {y:.1f} Z'
        self.fill_stroke(k, pot, w=0.8)
        self.stroke(k+0.01, leaves, w=0.8)

    def rug(self, a, b, da, db, key=None):
        k = key if key is not None else 0  # floor level, draw early
        self.stroke(k, self._poly([self.P(a,b,0.4),self.P(a+da,b,0.4),self.P(a+da,b+db,0.4),self.P(a,b+db,0.4)]), w=0.7, dash='3 3', op='0.7')

    def deck(self, a0, b0, da, db, step=1.6, key=None):
        k = key if key is not None else -1
        d = self._poly([self.P(a0,b0,0.6),self.P(a0+da,b0,0.6),self.P(a0+da,b0+db,0.6),self.P(a0,b0+db,0.6)])
        self.fill_stroke(k, d, w=1.0)
        n = int(da / step)
        for i in range(1, n+1):
            aa = a0 + i*step
            if aa >= a0+da: break
            self.line(aa, b0+0.3, 0.6, aa, b0+db-0.3, 0.6, w=0.6, op='0.8', key=k+0.001)

    # walls: perimeter cut walls with openings. wall runs along a ('A') or b ('B')
    def wall_a(self, a0, a1, b, t, h, gaps=(), key=None):
        segs, cur = [], a0
        for (g0, g1, kind) in sorted(gaps):
            if g0 > cur: segs.append((cur, g0, 'wall'))
            segs.append((g0, g1, kind)); cur = g1
        if cur < a1: segs.append((cur, a1, 'wall'))
        for (s0, s1, kind) in segs:
            k = key if key is not None else (s1 + b + t)
            if kind == 'wall':
                self.box(s0, b, s1-s0, t, 0, h, key=k)
            elif kind == 'win':
                self.box(s0, b, s1-s0, t, 0, 7, w=0.8, key=k)          # sill band
            # 'door' -> leave open

    def wall_b(self, b0, b1, a, t, h, gaps=(), key=None):
        segs, cur = [], b0
        for (g0, g1, kind) in sorted(gaps):
            if g0 > cur: segs.append((cur, g0, 'wall'))
            segs.append((g0, g1, kind)); cur = g1
        if cur < b1: segs.append((cur, b1, 'wall'))
        for (s0, s1, kind) in segs:
            k = key if key is not None else (a + s1 + t)
            if kind == 'wall':
                self.box(a, s0, t, s1-s0, 0, h, key=k)
            elif kind == 'win':
                self.box(a, s0, t, s1-s0, 0, 7, w=0.8, key=k)

    def render(self, group_only=False):
        self.items.sort(key=lambda it: it[0])
        return ''.join(svg for _, svg in self.items)


def sahel(ink, paper):
    s = Scene(ox=158, oy=42, q=2.35, ink=ink, paper=paper)
    A, B, WH, T = 44, 26, 15, 1.2
    # slab under everything
    s.box(-0.8, -0.8, A+1.6, B+1.6, -6, 6, key=-10)
    # deck toward viewer (a beyond A)
    s.deck(A+0.5, 3, 10, B-6, key=-5)
    # perimeter walls (cutaway height WH)
    s.wall_b(0, B, 0, T, WH, gaps=((4,10,'win'),(14,22,'win')), key=0.5)            # back-left long wall
    s.wall_a(0, A, 0, T, WH, gaps=((6,12,'win'),(20,26,'win'),(33,39,'win')), key=0.6)  # back-right long wall
    s.wall_b(0, B, A-T, T, WH, gaps=((6,12,'door'),(15,21,'win')))                  # front-right wall to deck
    s.wall_a(0, A, B-T, T, WH, gaps=((8,13,'win'),(26,30,'door'),(36,41,'win')))    # front-left wall
    # partitions
    s.wall_b(0, B, 28, T, WH, gaps=((10.5,14.5,'door'),))     # living | bedrooms
    s.wall_a(28+T, A-T, 12.5, T, WH, gaps=((30,33.5,'door'),))  # bed1 | bed2
    s.wall_b(0, 12.5, 20, T, WH, gaps=((3,6.5,'door'),))      # bath
    # living zone
    s.sofa(3, B-8.5, 10, 3.6, back='b0', key=None)
    s.box(6, B-13.5, 4.5, 2.6, 0, 3, w=0.8)                   # coffee table
    s.armchair(3.2, B-14.6)
    s.plant(1.6, B-3.2, 1.0)
    # dining + kitchen
    s.counter(15, 1.8, 10, 3.4)
    s.table(16.5, 8.5, 6.5, 3.6)
    for (ca, cb) in [(17.2,7.0),(20.5,7.0),(17.2,12.6),(20.5,12.6)]:
        s.chair(ca, cb)
    s.plant(26.5, 2.2, 0.9)
    # bath (a 20..28, b 0..12.5 corner)
    s.tub(24.5, 4.2)
    s.wc(21.5, 9.2)
    # bedrooms
    s.bed(31.5, 2.0, 8.5, 6.0)
    s.wardrobe(A-4.6, 8.6, 3.2, 3.6)
    s.bed(31.5, 15.5, 8.5, 6.0)
    s.plant(A-2.6, B-2.8, 0.9)
    # deck furniture
    s.chair(A+3.5, 8.5)
    s.round_table(A+5.5, 11.5, r=1.8, h=6)
    s.plant(A+2.0, B-5.5, 0.9)
    return s.render()


def jabal(ink, paper):
    s = Scene(ox=176, oy=44, q=2.35, ink=ink, paper=paper)
    A, B, WH, T = 36, 24, 15, 1.2
    # deep stone plinth with course lines
    s.box(-0.8, -0.8, A+1.6, B+1.6, -12, 12, key=-10)
    for z in (-8, -4):
        s.line(A+0.8, -0.8, z+12-12, A+0.8, B+0.8, z, w=0.6, op='0.6', key=-9.9)
        s.line(-0.8, B+0.8, z, A+0.8, B+0.8, z, w=0.6, op='0.6', key=-9.9)
    # terrace deck toward viewer
    s.deck(6, B+1.4, 16, 6, key=-5)
    # perimeter
    s.wall_b(0, B, 0, T, WH, gaps=((4,12,'win'),(15,21,'win')))
    s.wall_a(0, A, 0, T, WH, gaps=((6,12,'win'),(24,30,'win')))
    s.wall_b(0, B, A-T, T, WH, gaps=((5,11,'win'),(14,20,'win')))
    s.wall_a(0, A, B-T, T, WH, gaps=((8,14,'door'),(24,29,'win')))
    # partition living | sleeping
    s.wall_b(0, B, 21, T, WH, gaps=((9,13,'door'),))
    s.wall_a(21+T, A-T, 12, T, WH, gaps=((23,26.5,'door'),))
    # hearth against back wall
    s.box(9, 1.6, 4.5, 2.2, 0, 14)
    s.stroke(13.5, s._poly([s.P(10.2,1.7,5),s.P(12.2,1.7,5),s.P(12.2,1.7,10),s.P(10.2,1.7,10)]), w=0.7)
    # living furniture
    s.sofa(3, 14, 9.5, 3.6, back='b0')
    s.box(5.5, 9.2, 4.2, 2.5, 0, 2.6, w=0.8)
    s.armchair(12.5, 8.2)
    s.round_table(16.8, 4.6, r=2.2, h=6)
    s.chair(14.6, 3.2); s.chair(18.6, 6.8)
    s.plant(1.8, B-2.6, 1.0)
    s.plant(19.6, B-3.0, 0.9)
    # sleeping side
    s.bed(25, 2.2, 8, 6)
    s.wardrobe(A-4.4, 9.4, 3.0, 3.4)
    s.tub(26.5, 19.0)
    s.wc(31.5, 15.0)
    s.plant(A-2.6, B-2.8, 0.9)
    return s.render()


def wadi(ink, paper):
    s = Scene(ox=196, oy=30, q=2.15, ink=ink, paper=paper)
    A, B, WH, T = 42, 30, 15, 1.2
    C = (14, 10, 14, 10)  # court a0,b0,da,db
    ca0, cb0, cda, cdb = C
    s.box(-0.8, -0.8, A+1.6, B+1.6, -6, 6, key=-10)
    # perimeter
    s.wall_b(0, B, 0, T, WH, gaps=((4,9,'win'),(13,18,'win'),(22,27,'win')))
    s.wall_a(0, A, 0, T, WH, gaps=((5,10,'win'),(16,21,'win'),(28,33,'win')))
    s.wall_b(0, B, A-T, T, WH, gaps=((12,17,'door'),(21,26,'win')))
    s.wall_a(0, A, B-T, T, WH, gaps=((6,11,'win'),(18,23,'door'),(30,35,'win')))
    # court walls (low, with wide openings)
    s.wall_b(cb0, cb0+cdb, ca0, T, WH, gaps=((cb0+3, cb0+7, 'door'),))
    s.wall_b(cb0, cb0+cdb, ca0+cda-T, T, WH, gaps=((cb0+3, cb0+7, 'door'),))
    s.wall_a(ca0, ca0+cda, cb0, T, WH, gaps=((ca0+4, ca0+10, 'door'),))
    s.wall_a(ca0, ca0+cda, cb0+cdb-T, T, WH, gaps=((ca0+4, ca0+10, 'door'),))
    # court: paved stripes + tree
    s.deck(ca0+T, cb0+T, cda-2*T, cdb-2*T, step=1.4, key=ca0+cb0+2)
    s.plant(ca0+cda/2, cb0+cdb/2, 1.6, key=ca0+cda+cb0+cdb)
    s.plant(ca0+3, cb0+2.4, 0.8, key=ca0+cb0+4)
    # rooms around court
    s.sofa(30, 13, 9.5, 3.6, back='b0')       # living east
    s.box(32.5, 8.4, 4.2, 2.5, 0, 3, w=0.8)
    s.counter(2, 2, 9, 3.2)                    # kitchen north-west
    s.table(4, 8.5, 6, 3.4)
    for (ca_, cb_) in [(4.8,7.0),(7.6,7.0),(4.8,12.4),(7.6,12.4)]:
        s.chair(ca_, cb_)
    s.bed(3, 20, 8, 6)                         # bedroom west
    s.wardrobe(12.5, 25.5, 3.4, 3.4)
    s.bed(31, 21, 8, 6)                        # bedroom east
    s.tub(35, 4)                               # bath north-east
    s.wc(31, 3)
    s.plant(A-2.5, B-3, 1.0)
    s.plant(1.8, B-3, 0.9)
    return s.render()


def system_axo(ink, paper):
    # simplified furnished plate for the scroll choreography, grouped in layers:
    # base = slab + deck | wall-left / wall-right = partitions | roof-group = fit-out (lifts up)
    def collect(build):
        sc = Scene(ox=200, oy=96, q=2.5, ink=ink, paper=paper, system=True)
        build(sc)
        return sc.render()

    A, B, WH, T = 34, 22, 15, 1.2

    def base(sc):
        sc.box(-0.8, -0.8, A+1.6, B+1.6, -6, 6, key=-10)
        sc.deck(A+0.5, 3, 8, B-6, key=-5)

    def walls_left(sc):
        sc.wall_b(0, B, 0, T, WH, gaps=((4,9,'win'),(13,18,'win')))
        sc.wall_a(0, 18, 0, T, WH, gaps=((5,10,'win'),))
        sc.wall_a(0, 18, B-T, T, WH, gaps=((7,12,'win'),))
        sc.wall_b(0, B, 18, T, WH, gaps=((8.5,12.5,'door'),))

    def walls_right(sc):
        sc.wall_a(18, A, 0, T, WH, gaps=((22,27,'win'),))
        sc.wall_a(18, A, B-T, T, WH, gaps=((20,24,'door'),(27,31,'win')))
        sc.wall_b(0, B, A-T, T, WH, gaps=((5,10,'door'),(13,18,'win')))
        sc.wall_a(18+T, A-T, 11, T, WH, gaps=((26,29.5,'door'),))

    def fit(sc):
        sc.sofa(2.6, B-8, 8.5, 3.4, back='b0')
        sc.box(5, B-12.4, 4, 2.4, 0, 3, w=0.8)
        sc.counter(2.2, 1.8, 8, 3.2)
        sc.table(11.5, 5.5, 5, 3.2)
        sc.chair(12.4, 4.0); sc.chair(14.6, 4.0)
        sc.bed(21.5, 2.0, 7.5, 5.5)
        sc.bed(21.5, 14.0, 7.5, 5.5)
        sc.wardrobe(A-4.2, 8.0, 3.0, 3.2)
        sc.plant(1.6, B-2.6, 0.9)
        sc.plant(A-2.4, B-2.4, 0.9)
        sc.chair(A+2.8, 8.0)
        sc.round_table(A+4.6, 10.6, r=1.6, h=6)

    return (f'<g class="axo-base">{collect(base)}</g>'
            f'<g class="axo-wall-left">{collect(walls_left)}</g>'
            f'<g class="axo-wall-right">{collect(walls_right)}</g>'
            f'<g class="axo-roof">{collect(fit)}</g>')


INK_CARD, PAPER_CARD = '#2a251d', '#e9dfca'
INK_SYS, PAPER_SYS = '#f2efe9', '#070707'

def card_svg(body, label, dim_text, dim_x0, dim_x1):
    dims = (f'<g font-family="Barlow, sans-serif" font-size="9" fill="{INK_CARD}" opacity="0.65">'
            f'<path d="M{dim_x0} 282 H{dim_x1} M{dim_x0} 277 v10 M{dim_x1} 277 v10" stroke="{INK_CARD}" stroke-width="0.8" fill="none"/>'
            f'<text x="{(dim_x0+dim_x1)//2}" y="276" text-anchor="middle" letter-spacing="2">{dim_text}</text></g>')
    reg = f'<path d="M16 22 h10 M21 17 v10 M374 272 h10 M379 267 v10" stroke="{INK_CARD}" stroke-width="0.8" opacity="0.4" fill="none"/>'
    return (f'<svg viewBox="0 0 400 300" aria-label="{label}">{reg}{body}{dims}</svg>')

import io
out = {}
out['sahel'] = card_svg(sahel(INK_CARD, PAPER_CARD), 'SAHEL — coastal bungalow, furnished isometric cutaway', '15.0 M', 80, 320)
out['jabal'] = card_svg(jabal(INK_CARD, PAPER_CARD), 'JABAL — mountain house, furnished isometric cutaway', '9.6 M', 90, 310)
out['wadi']  = card_svg(wadi(INK_CARD, PAPER_CARD), 'WADI — courtyard house, furnished isometric cutaway', '18.4 M', 85, 315)
out['system'] = system_axo(INK_SYS, PAPER_SYS)

for k, v in out.items():
    print(k, len(v))

import json, os
open(os.path.join(os.path.dirname(__file__), 'svgs.json'), 'w', encoding='utf-8').write(json.dumps(out))
print('written')
