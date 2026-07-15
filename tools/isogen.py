# BEIT — isometric cutaway drawing generator
# 2:1 pixel isometric: a-axis -> (+2,+1)*q, b-axis -> (-2,+1)*q, z -> (0,-1)

class Scene:
    def __init__(self, ox, oy, q, ink, paper, system=False, zoff=0.0):
        self.ox, self.oy, self.q = ox, oy, q
        self.ink, self.paper, self.system = ink, paper, system
        self.zoff = zoff
        self.items = []  # (sortkey, svg)

    def P(self, a, b, z=0.0):
        return (self.ox + (a - b) * 2 * self.q, self.oy + (a + b) * self.q - (z + self.zoff))

    def _pts(self, pts):
        return ' '.join(f'{x:.1f} {y:.1f}' for x, y in pts)

    def _poly(self, pts):
        return 'M' + self._pts([pts[0]]) + ' L ' + ' L '.join(self._pts([p]) for p in pts[1:]) + ' Z'

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
        k = key if key is not None else (a1 + b1 + z0 * 0.01 + self.zoff * 0.001)
        top = [self.P(a0,b0,z0+h), self.P(a1,b0,z0+h), self.P(a1,b1,z0+h), self.P(a0,b1,z0+h)]
        fa  = [self.P(a1,b0,z0), self.P(a1,b1,z0), self.P(a1,b1,z0+h), self.P(a1,b0,z0+h)]
        fb  = [self.P(a0,b1,z0), self.P(a1,b1,z0), self.P(a1,b1,z0+h), self.P(a0,b1,z0+h)]
        d = self._poly(top) + ' ' + self._poly(fa) + ' ' + self._poly(fb)
        self.fill_stroke(k, d, w)

    def floor_ellipse(self, a, b, ra, rb, z=0, w=1.0, key=None):
        x, y = self.P(a, b, z)
        k = key if key is not None else (a + b + self.zoff*0.001)
        cls_s = ' class="hp" pathLength="1"' if self.system else ''
        self.items.append((k, f'<ellipse{cls_s} cx="{x:.1f}" cy="{y:.1f}" rx="{ra*2.2*self.q:.1f}" ry="{rb*1.1*self.q:.1f}" fill="{self.paper}" stroke="{self.ink}" stroke-width="{w}"/>'))

    def line(self, a0,b0,z0, a1,b1,z1, w=1.0, dash=None, op=None, key=None):
        p0, p1 = self.P(a0,b0,z0), self.P(a1,b1,z1)
        k = key if key is not None else max(a0+b0, a1+b1) + self.zoff*0.001
        self.stroke(k, f'M{p0[0]:.1f} {p0[1]:.1f} L{p1[0]:.1f} {p1[1]:.1f}', w, dash, op)

    # ---- furniture ----
    def bed(self, a, b, da, db, key=None):
        k = key if key is not None else a+da+b+db
        self.box(a, b, da, db, 0, 4, key=k)
        self.box(a+0.6, b+0.6, da-1.2, db-1.2, 4, 2, w=0.8, key=k+0.01)
        self.box(a+0.9, b+0.9, 2.0, db-1.8, 6, 1.4, w=0.8, key=k+0.02)
        self.line(a+da*0.55, b+0.6, 6.1, a+da*0.55, b+db-0.6, 6.1, w=0.7, key=k+0.03)

    def sofa(self, a, b, da, db, back='b0', key=None):
        k = key if key is not None else a+da+b+db
        self.box(a, b, da, db, 0, 4, key=k)
        if back == 'b0':
            self.box(a, b, da, 1.3, 4, 4.5, w=0.8, key=k+0.01)
            self.box(a, b, 1.3, db, 4, 3, w=0.8, key=k+0.02)
            self.box(a+da-1.3, b, 1.3, db, 4, 3, w=0.8, key=k+0.03)
        else:
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
        self.line(a, b, 0, a, b, h, w=0.8, key=k)
        self.floor_ellipse(a, b, r, r, z=h, w=1.0, key=k+0.01)

    def counter(self, a, b, da, db, key=None):
        k = key if key is not None else a+da+b+db
        self.box(a, b, da, db, 0, 9, key=k)
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
        self.line(a-2.6, b, 4, a-2.6, b, 10, w=0.8, key=k+0.02)

    def wc(self, a, b, facing='b', key=None):
        """Toilet at legible scale: cistern box against the wall + bowl ellipse."""
        k = key if key is not None else a+b+3
        if facing == 'b':   # bowl extends toward +b (viewer-left face)
            self.box(a, b, 2.4, 1.1, 0, 4.5, w=0.8, key=k)
            self.floor_ellipse(a+1.2, b+2.3, 1.1, 0.95, z=2.4, w=0.8, key=k+0.01)
            self.floor_ellipse(a+1.2, b+2.3, 0.7, 0.6, z=2.4, w=0.6, key=k+0.02)
        else:               # bowl extends toward +a
            self.box(a, b, 1.1, 2.4, 0, 4.5, w=0.8, key=k)
            self.floor_ellipse(a+2.3, b+1.2, 1.1, 0.95, z=2.4, w=0.8, key=k+0.01)
            self.floor_ellipse(a+2.3, b+1.2, 0.7, 0.6, z=2.4, w=0.6, key=k+0.02)

    def basin(self, a, b, key=None):
        """Vanity unit with basin bowl on top."""
        k = key if key is not None else a+b+3.5
        self.box(a, b, 2.6, 1.5, 0, 5.5, w=0.8, key=k)
        self.floor_ellipse(a+1.3, b+0.75, 0.8, 0.5, z=5.5, w=0.6, key=k+0.01)

    def shower(self, a, b, s=3.4, key=None):
        """Floor tray outline + drain + head riser."""
        k = key if key is not None else a+b+2.5
        self.stroke(k, self._poly([self.P(a,b,0.4),self.P(a+s,b,0.4),self.P(a+s,b+s,0.4),self.P(a,b+s,0.4)]), w=0.8)
        x, y = self.P(a+s/2, b+s/2, 0.4)
        self.items.append((k+0.01, f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{0.5*self.q:.1f}" fill="none" stroke="{self.ink}" stroke-width="0.6"/>'))
        self.line(a+0.5, b+0.5, 0, a+0.5, b+0.5, 9, w=0.8, key=k+0.02)
        self.line(a+0.5, b+0.5, 9, a+1.6, b+1.6, 8, w=0.8, key=k+0.03)

    def column(self, a, b, h, key=None):
        k = key if key is not None else a+b+0.5
        self.box(a-0.55, b-0.55, 1.1, 1.1, 0, h, w=0.8, key=k)

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

    def deck(self, a0, b0, da, db, step=1.6, key=None):
        k = key if key is not None else -1
        d = self._poly([self.P(a0,b0,0.6),self.P(a0+da,b0,0.6),self.P(a0+da,b0+db,0.6),self.P(a0,b0+db,0.6)])
        self.fill_stroke(k, d, w=1.0)
        n = int(da / step)
        for i in range(1, n+1):
            aa = a0 + i*step
            if aa >= a0+da: break
            self.line(aa, b0+0.3, 0.6, aa, b0+db-0.3, 0.6, w=0.6, op='0.8', key=k+0.001)

    def stair(self, a, b, run, width, z0, height, n=9, axis='b', key=None):
        """Ascending stack of step-boxes — simplified isometric stair convention."""
        k = key if key is not None else a+b+run+width+self.zoff*0.001
        step_run = run / n
        step_h = height / n
        for i in range(n):
            if axis == 'b':
                self.box(a, b + i*step_run, width, step_run, z0, (i+1)*step_h, w=0.7, key=k + i*0.001)
            else:
                self.box(a + i*step_run, b, step_run, width, z0, (i+1)*step_h, w=0.7, key=k + i*0.001)

    # walls: perimeter cut walls with openings. wall runs along a ('A') or b ('B')
    def wall_a(self, a0, a1, b, t, h, gaps=(), key=None):
        segs, cur = [], a0
        for (g0, g1, kind) in sorted(gaps):
            if g0 > cur: segs.append((cur, g0, 'wall'))
            segs.append((g0, g1, kind)); cur = g1
        if cur < a1: segs.append((cur, a1, 'wall'))
        for (s0, s1, kind) in segs:
            k = key if key is not None else (s1 + b + t + self.zoff*0.001)
            if kind == 'wall':
                self.box(s0, b, s1-s0, t, 0, h, key=k)
            elif kind == 'win':
                self.box(s0, b, s1-s0, t, 0, 7, w=0.8, key=k)

    def wall_b(self, b0, b1, a, t, h, gaps=(), key=None):
        segs, cur = [], b0
        for (g0, g1, kind) in sorted(gaps):
            if g0 > cur: segs.append((cur, g0, 'wall'))
            segs.append((g0, g1, kind)); cur = g1
        if cur < b1: segs.append((cur, b1, 'wall'))
        for (s0, s1, kind) in segs:
            k = key if key is not None else (a + s1 + t + self.zoff*0.001)
            if kind == 'wall':
                self.box(a, s0, t, s1-s0, 0, h, key=k)
            elif kind == 'win':
                self.box(a, s0, t, s1-s0, 0, 7, w=0.8, key=k)

    def render(self):
        self.items.sort(key=lambda it: it[0])
        return ''.join(svg for _, svg in self.items)


def sahel(ink, paper):
    s = Scene(ox=158, oy=42, q=2.35, ink=ink, paper=paper)
    A, B, WH, T = 44, 26, 15, 1.2
    x1, x2, x3 = 13, 19, 30   # bed|bath, bath|kitchen, kitchen|living
    y1 = 13                   # bedroom1 | bedroom2

    s.box(-0.8, -0.8, A+1.6, B+1.6, -6, 6, key=-10)
    s.deck(A+0.5, 3, 10, B-6, key=-5)

    # perimeter
    s.wall_a(0, A, 0, T, WH, gaps=((3,7,'win'),(17,21,'win'),(23,28,'win'),(35,40,'win')))
    s.wall_a(0, A, B-T, T, WH, gaps=((3,8,'win'),(15,18,'win'),(22,27,'win')))
    s.wall_b(0, B, 0, T, WH, gaps=((3,7,'win'),(17,21,'win')))
    s.wall_b(0, B, A-T, T, WH, gaps=((8,14,'door'),(16,22,'win')))
    # partitions
    s.wall_a(0, x1, y1, T, WH, gaps=((5,8,'door'),))
    s.wall_b(0, B, x1, T, WH, gaps=((4,7,'door'),(18,21,'door')))
    s.wall_b(0, B, x2, T, WH, gaps=((10,13,'door'),))
    s.wall_b(0, B, x3, T, WH, gaps=((11,15,'door'),))
    s.wall_a(x1+T, x2, 13, T, WH)   # bathroom | shower-WC split

    # bedroom 1
    s.bed(1.5, 1.5, 8, 6)
    s.wardrobe(1.5, 8.6, 3, 3.2)
    s.plant(10.6, 11, 0.85)
    # bedroom 2
    s.bed(1.5, 15, 8, 6)
    s.wardrobe(1.5, 22, 3, 3)
    s.plant(10.6, 24, 0.85)
    # bathroom (tub + basin) and separate shower + WC room
    s.tub(16, 4.6)
    s.basin(14, 10.2)
    s.shower(14.6, 14.8)
    s.wc(14, 21.3, facing='a')
    # kitchen / dining
    s.counter(20, 1.6, 8.5, 3.2)
    s.table(21.5, 9.5, 6, 3.4)
    for (ca, cb) in [(22.2,8.0),(25.3,8.0),(22.2,13.4),(25.3,13.4)]:
        s.chair(ca, cb)
    s.plant(27.4, 22, 0.9)
    # living
    s.sofa(32, 17, 10, 3.6, back='b0')
    s.box(34.5, 12, 4.2, 2.5, 0, 3, w=0.8)
    s.armchair(32.2, 10.8)
    s.plant(31.5, 2, 0.9)
    # deck furniture
    s.chair(A+3.5, 8.5)
    s.round_table(A+5.5, 11.5, r=1.8, h=6)
    s.plant(A+2.0, B-5.5, 0.9)
    return s.render()


def jabal(ink, paper):
    # Exploded two-storey axo: the complete first floor floats well above
    # the ground floor with dashed corner projection lines — the classic
    # drawing-set move. Nothing occludes anything; both plates read as
    # fully furnished cutaways. (A loft/slab hovering just above the cut
    # walls read as a lid parked on the ground floor.)
    A, B, T = 30, 20, 1.2
    WH = 12          # cutaway wall height, both storeys
    # zero screen overlap needs LIFT > plate screen height (A+B)*q + walls
    LIFT = 118       # air between the plates (z units == px)

    s = Scene(ox=178, oy=158, q=2.0, ink=ink, paper=paper)
    # stone plinth, coursed
    s.box(-0.8, -0.8, A+1.6, B+1.6, -9, 9, key=-20)
    for z in (-6, -3):
        s.line(A+0.8, -0.8, z, A+0.8, B+0.8, z, w=0.55, op='0.6', key=-19.9)
        s.line(-0.8, B+0.8, z, A+0.8, B+0.8, z, w=0.55, op='0.6', key=-19.9)
    s.deck(6, B+1.4, 15, 5.5, key=-15)
    plinth_svg = s.render()

    # ---- ground floor: living + hearth, kitchen/dining, WC, stair ----
    g = Scene(ox=s.ox, oy=s.oy, q=s.q, ink=ink, paper=paper)
    g.wall_b(0, B, 0, T, WH, gaps=((3,9,'win'),))
    g.wall_a(0, A, 0, T, WH, gaps=((3,9,'win'),(20,26,'win')))
    g.wall_b(0, B, A-T, T, WH, gaps=((4,9,'win'),(12,17,'win')))
    g.wall_a(0, A, B-T, T, WH, gaps=((5,10,'door'),(19,25,'win')))
    g.wall_b(0, B, 12, T, WH, gaps=((5,9,'door'),(14,17,'door')))   # kitchen wing | living
    g.wall_a(12+T, A-T, 7, T, WH, gaps=((13.5,16.5,'door'),))       # WC + stair | living

    # kitchen / dining (west wing)
    g.counter(1.6, 1.6, 7.5, 3.2)
    g.round_table(5.4, 9.5, r=1.9, h=6)
    g.chair(3.4, 8.0); g.chair(7.2, 11.2)
    g.plant(1.8, B-2.6, 0.85)
    # ground WC (real toilet + basin, its own room)
    g.wc(14, 1.6, facing='b')
    g.basin(18.5, 1.6)
    # stair up
    g.stair(23.5, 1.6, 4.8, 3.6, 0, WH, n=7, axis='b')
    # living + hearth (east/front)
    g.box(A-5.5, 8.5, 3.6, 2, 0, 11)
    g.stroke(400, g._poly([g.P(A-4.8,8.6,4),g.P(A-3.4,8.6,4),g.P(A-3.4,8.6,8),g.P(A-4.8,8.6,8)]), w=0.6)
    g.sofa(14, B-6.4, 9.5, 3.4, back='b0')
    g.armchair(25, B-7.2)
    g.plant(A-2.2, B-2.4, 0.85)
    ground_svg = g.render()

    # dashed corner projectors between the storeys
    p = Scene(ox=s.ox, oy=s.oy, q=s.q, ink=ink, paper=paper)
    for (ca, cb) in [(0,0),(A,0),(0,B),(A,B)]:
        p.line(ca, cb, WH+1, ca, cb, LIFT-1.5, w=0.6, dash='4 4', op='0.55', key=1000)
    proj_svg = p.render()

    # ---- first floor (floating): two bedrooms + full bathroom ----
    f = Scene(ox=s.ox, oy=s.oy, q=s.q, ink=ink, paper=paper, zoff=LIFT)
    f.box(-0.4, -0.4, A+0.8, B+0.8, -1.5, 1.5, w=0.8, key=-10)      # its slab
    f.wall_b(0, B, 0, T, WH, gaps=((3,9,'win'),))
    f.wall_a(0, A, 0, T, WH, gaps=((4,10,'win'),(20,26,'win')))
    f.wall_b(0, B, A-T, T, WH, gaps=((4,9,'win'),(12,17,'win')))
    f.wall_a(0, A, B-T, T, WH, gaps=((5,11,'win'),(19,24,'win')))
    f.wall_b(0, B, 12, T, WH, gaps=((8,12,'door'),))                # bed1 | hall+bed2
    f.wall_a(12+T, A-T, 9, T, WH, gaps=((14,17,'door'),))           # bathroom | bed2

    f.bed(2, 2, 8, 6)                                               # bedroom 1
    f.wardrobe(2, 9.4, 3, 3.2)
    f.plant(9.6, B-3, 0.8)
    f.bed(20, 12, 8, 6)                                             # bedroom 2
    f.wardrobe(A-4.4, B-3.4, 3, 3)
    # bathroom (tub + toilet + basin)
    f.tub(17, 3.4)
    f.wc(21.5, 1.6, facing='b')
    f.basin(25.5, 1.6)
    # stair void marked on the slab
    f.stroke(500, f._poly([f.P(23.5,1.6,0.3),f.P(28.3,1.6,0.3),f.P(28.3,5.2,0.3),f.P(23.5,5.2,0.3)]), w=0.6, dash='3 3', op='0.7')
    first_svg = f.render()

    return plinth_svg + ground_svg + proj_svg + first_svg


def wadi(ink, paper):
    s = Scene(ox=196, oy=26, q=2.05, ink=ink, paper=paper)
    A, B, WH, T = 42, 30, 15, 1.2
    cx0, cx1 = 11, 31     # courtyard a-range
    cy0, cy1 = 7, 23      # courtyard b-range  (20 x 16 -- much larger than before)

    s.box(-0.8, -0.8, A+1.6, B+1.6, -6, 6, key=-10)

    # perimeter — front door aligned with the entry path into the court
    s.wall_a(0, A, 0, T, WH, gaps=((3,9,'win'),(18,24,'win'),(33,39,'win')))
    s.wall_a(0, A, B-T, T, WH, gaps=((18.5,23,'door'),(3,8,'win'),(30,36,'win')))
    s.wall_b(0, B, 0, T, WH, gaps=((3,8,'win'),(16,21,'win')))
    s.wall_b(0, B, A-T, T, WH, gaps=((6,11,'win'),(22,27,'win')))

    # court ring: wide openings on the camera-facing sides, and the whole
    # south edge is an open COLONNADE — entry path runs straight in
    s.wall_b(0, B, cx0, T, WH, gaps=((9,13,'door'),(18,21,'door')))       # west rooms | court
    s.wall_b(0, B, cx1, T, WH, gaps=((11,17,'door'),))                    # east rooms | court (wide)
    s.wall_a(cx0, cx1, cy0, T, WH, gaps=((16,22,'door'),))                # kitchen | court (wide)
    s.wall_a(cx0, 17, cy1, T, WH)                                          # guest-WC room north wall
    for ca in (19.5, 23.5, 27.5):                                          # colonnade posts
        s.column(ca, cy1+0.6, WH, key=ca+cy1+2)
    # internal splits within the side bands
    s.wall_a(0, cx0, 15, T, WH, gaps=((3,6,'door'),))                     # bedroom1 | bedroom2 (west)
    s.wall_a(cx1, A-T, 20, T, WH, gaps=((33,37,'door'),))                 # living | bath (east)

    # west: two bedrooms
    s.bed(2, 2, 7.5, 6)
    s.wardrobe(2, 9.4, 3, 3.4)
    s.plant(8.6, 12.6, 0.8)
    s.bed(2, 17, 7.5, 6)
    s.wardrobe(2, 24.4, 3, 3.4)
    s.plant(8.6, 27, 0.8)

    # north: kitchen/dining
    s.counter(13, 1.6, 9, 3.2)
    s.table(24, 1.8, 5.5, 3.4)
    s.chair(25, 0.6); s.chair(27.6, 0.6)

    # east: living + full bathroom (tub, toilet, basin)
    s.sofa(33, 3, 8, 3.4, back='b0')
    s.box(35, 7.6, 4, 2.4, 0, 3, w=0.8)
    s.round_table(37.5, 14.5, r=2.0, h=6)
    s.chair(36.2, 13); s.chair(39.2, 16)
    s.plant(A-2.2, 2, 0.85)
    s.tub(35, 23.5)
    s.wc(38.5, 26.5, facing='b')
    s.basin(32.4, 26.8)

    # south: enclosed guest WC room (west of the entry path)
    s.wall_b(cy1, B, 17, T, WH, gaps=((25.5,28.5,'door'),))   # its east wall + door
    s.wc(12.6, cy1+1.4, facing='b')
    s.basin(14.6, B-2.9)
    s.plant(26.5, 27.4, 0.9)

    # entry path: paving from the front door through the colonnade into the court
    s.deck(18.5, cy1, 4.6, B-cy1-T, step=1.5, key=cx0+cy1+1)

    # courtyard: paved centre + trees + outdoor seating
    s.deck(cx0+T, cy0+T, (cx1-T)-(cx0+T), (cy1-T)-(cy0+T), step=1.5, key=cx0+cy0+2)
    s.plant((cx0+cx1)/2 - 3, (cy0+cy1)/2 - 1, 1.9, key=cx0+cx1+cy0+cy1)
    s.plant(cx0+3, cy1-3, 1.0, key=cx0+cy1+5)
    s.plant(cx1-3, cy0+3, 1.0, key=cx1+cy0+6)
    s.round_table((cx0+cx1)/2 + 5, (cy0+cy1)/2 + 2.5, r=1.6, h=5.5, key=500)
    s.chair((cx0+cx1)/2 + 4, (cy0+cy1)/2 + 5.5, key=501)
    s.chair((cx0+cx1)/2 + 7.5, (cy0+cy1)/2 + 4.5, key=502)
    return s.render()


def system_axo(ink, paper):
    def collect(build, zoff=0.0):
        sc = Scene(ox=200, oy=96, q=2.5, ink=ink, paper=paper, system=True, zoff=zoff)
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

out = {}
out['sahel'] = card_svg(sahel(INK_CARD, PAPER_CARD), 'SAHEL — coastal bungalow, furnished isometric cutaway', '15.0 M', 80, 320)
out['jabal'] = card_svg(jabal(INK_CARD, PAPER_CARD), 'JABAL — mountain house, two-storey furnished isometric cutaway', '9.6 M', 90, 310)
out['wadi']  = card_svg(wadi(INK_CARD, PAPER_CARD), 'WADI — courtyard house, furnished isometric cutaway', '18.4 M', 85, 315)
out['system'] = system_axo(INK_SYS, PAPER_SYS)

for k, v in out.items():
    print(k, len(v))

import json, os
open(os.path.join(os.path.dirname(__file__), 'svgs.json'), 'w', encoding='utf-8').write(json.dumps(out))
print('written')
