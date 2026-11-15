"""Crab snare (sled style) - parametric build for FreeCAD 1.1.

Run headless:  "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" build.py
Outputs (next to this file): CrabSnare.FCStd, Body.stl, Cage.stl (print orientation), CrabSnare.step

Coordinates: mm, X = nose (tow direction), Z = up, body bottom at z=0.
California: max 6 loops per crab loop trap -> 6 posts.
Weight: flat disc sinkers with a wire eye slide in from the tail into a low tunnel, one behind
the other (e.g. 3 oz alone, or 2 oz + 3 oz). A zip tie goes down through the rear disc's eye
and around the tail lip, closing the mouth.
"""
import math, os
import FreeCAD as App
import Part
import Mesh, MeshPart
from FreeCAD import Vector as V

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------- parameters ----------------
BODY_A, BODY_B = 64.0, 58.0     # ellipse semi-axes (128 x 116 footprint)
TAIL_X = -57.0                  # tail squared off here: no knife-edge walls beside the weight mouth
TAIL_CHAMFER = 1.5
BODY_H = 20.0                   # body height
BOT_CHAMFER = 5.0               # 45 deg chamfer round the bottom (printable, skims)
TOP_FILLET = 3.0
NOSE_PLANE_X0 = 54.0            # 45 deg nose ramp: z = x - NOSE_PLANE_X0

HUB_R = 29.3                    # bayonet hub on top of the body
HUB_TOP = BODY_H + 11.0
CAGE_RO, CAGE_WALL = 32.5, 2.4   # cage bore 30.1 vs hub 29.3 -> 0.8 mm per side
CAGE_H = 56.0                   # deck to top of the roof
APEX_R, APEX_RIM = 3.0, 2.0     # 6 mm top vent, 2 mm flat rim round it
VENT_W, VENT_N = 5.0, 12        # side vents (teardrop: round bottom, 45 deg pointed top)
ROOF_VENT_N, ROOF_VENT_LEN = 6, 18.0

# disc sinkers (MEASURE YOURS and update these)
DISC_D = 42.0          # biggest disc diameter (the 3 oz)
DISC2_D = 36.0         # the second disc that goes in front (the 2 oz)
DISC_T = 11.0          # thickest disc
EYE_L = 9.0            # how far the wire eye sticks out past the disc
TUN_W = DISC_D + 2.0
TUN_Z0 = 4.0                                   # floor thickness (tail zip-tie slots go through it)
TUN_H = DISC_T + 1.5
TIE_X = -42.0                                  # zip tie goes through the rear disc's eye here
TUN_X1 = TIE_X + EYE_L / 2 + DISC_D + EYE_L + DISC2_D + 2.0   # front end of the tunnel
TIE_GATE_X = TIE_X - 10.0                      # 2nd slot: tie comes back up here, crossing the mouth (gate)
TAIL_PAD_H = 3.0                               # raised pad on the deck round the tail tie slots (45 deg sides)
TAIL_PAD_W = 22.0
MOUTH_CHAMFER = 1.5                            # small 45 deg lead-in on the channel mouth (keeps the walls thick)
TIE_SLOT = (2.2, 5.6)                          # zip-tie slot: thin x wide (fits a 4.8 mm tie)
TIE_CHAMFER = 0.8                              # 45 deg lead-in on every slot entry
TIE_GROOVE_D = 1.5
TUN_ROOF_CHAMFER = 0.0                         # roof corner chamfer (not needed now the body is split)

# two-piece body: TRAY (floor, walls, nose, tow eye) + DECK (roof plate, hub, loop posts).
# The 6 loop lines, the tail zip tie and one front zip tie clamp them; 4 pins locate them.
SPLIT_Z = TUN_Z0 + TUN_H                       # split exactly at the tunnel roof -> nothing to bridge
TAB_SPLIT_X = TUN_X1 + 1.5                     # tow eye forward of this belongs to the tray (clear of the channel)
NOTCH_CLR = 0.3                                # deck clearance round the tow eye
PIN_R, PIN_H, PIN_CLR = 2.5, 2.5, 0.2
PINS = [(20.0, 31.0), (20.0, -31.0), (-20.0, 31.0), (-20.0, -31.0)]
SIDE_TIES = False                              # side ties dropped: the 6 crimped loops clamp tray + deck
SIDE_TIE_X = 11.0                              # side ties: one per side in the solid wings beside the channel,
SIDE_TIE_Y = (38.0, 46.0)                      #   down/up enclosed slots at these |y|, tie runs across the wing
CAGE_CLEAR_R = 34.5                            # keep deck pads outside the cage + grip ribs

POST_ANGLES = [50.0, 90.0, 130.0, 230.0, 270.0, 310.0]   # where the posts sit (kept clear of the sinker channel)
POST_AIMS   = [20.0, 90.0, 160.0, 200.0, 270.0, 340.0]   # which way each post leans (plan view), front/rear
POST_TILTS  = [35.0, 25.0, 35.0, 35.0, 25.0, 35.0]       #   pairs aimed at the nose/tail corners for coverage
POST_R, POST_LEN, POST_TILT = 5.5, 20.0, 25.0   # tilt from vertical, leaning outward
POST_INSET = 0.86                                # post centres on ellipse scaled by this
HOLE_D, HOLE_SPACING = 2.3, 4.4                  # fits 80-100 lb mono or 0.065-0.080" trimmer line
CRIMP_R, CRIMP_D = 4.6, 3.5

# tow eye = upright fin with a sideways (Y) hole. The line wraps a round-fronted post (rounded in the
# print plane, so it's smooth and strong along the layers); hole is a teardrop (45 deg top, no bridge).
FIN_T = 10.0                    # fin thickness (Y); front is a full radius of FIN_T/2
FIN_FRONT = 68.0                # nose tip of the fin (x)
FIN_TOP = 32.0
FIN_BACK = 38.0                 # 45 deg ramp starts on the deck here
EYE_D = 7.0                     # line hole diameter
EYE_BAR = 5.0                   # solid post in front of the hole the line wraps round
EYE_Z = 24.0                    # hole centre height
EYE_HX = FIN_FRONT - EYE_BAR - EYE_D / 2

# bayonet
BAY_ANGLES = [12.0, 132.0, 252.0]
SLOT_RIN = 26.8
SLOT_ENTRY_SPAN, SLOT_TURN = 15.0, 25.0
SLOT_Z0, SLOT_Z1 = BODY_H + 2.4, BODY_H + 7.6
LUG_RIN, LUG_SPAN, LUG_Z0, LUG_Z1 = 27.6, 11.0, BODY_H + 3.2, BODY_H + 6.8   # underside chamfered 45 deg
DETENT_SPAN, DETENT_RIN = 2.0, 26.6       # bump on the hub, outer edge at 27.3


def prism_xz(pts, y0, y1):
    """Polygon given as (x, z) points, extruded along Y from y0 to y1."""
    w = Part.makePolygon([V(x, y0, z) for x, z in pts] + [V(pts[0][0], y0, pts[0][1])])
    return Part.Face(w).extrude(V(0, y1 - y0, 0))


def prism_yz(pts, x0, x1):
    """Polygon given as (y, z) points, extruded along X from x0 to x1."""
    w = Part.makePolygon([V(x0, y, z) for y, z in pts] + [V(x0, pts[0][0], pts[0][1])])
    return Part.Face(w).extrude(V(x1 - x0, 0, 0))


def tie_slot(cx, cy, sx, sy, z_bot, z_top, top=True, bottom=True):
    """Enclosed rectangular zip-tie slot with 45 deg lead-in chamfers at the ends."""
    c = Part.makeBox(sx, sy, z_top - z_bot + 0.02, V(cx - sx / 2, cy - sy / 2, z_bot - 0.01))
    ch = TIE_CHAMFER
    def rect(z, grow):
        return Part.makePolygon([V(cx - sx / 2 - grow, cy - sy / 2 - grow, z), V(cx + sx / 2 + grow, cy - sy / 2 - grow, z),
                                 V(cx + sx / 2 + grow, cy + sy / 2 + grow, z), V(cx - sx / 2 - grow, cy + sy / 2 + grow, z),
                                 V(cx - sx / 2 - grow, cy - sy / 2 - grow, z)])
    if top:
        c = c.fuse(Part.makeLoft([rect(z_top - ch, 0), rect(z_top + 0.01, ch + 0.01)], True, True))
    if bottom:
        c = c.fuse(Part.makeLoft([rect(z_bot - 0.01, ch + 0.01), rect(z_bot + ch, 0)], True, True))
    return c


def peaked_hole(r, z0, depth_straight):
    """Round pocket from below with a 45 deg conical roof (no bridge)."""
    return Part.makeCylinder(r, depth_straight + 0.01, V(0, 0, z0 - 0.01)).fuse(
        Part.makeCone(r, 0, r, V(0, 0, z0 + depth_straight)))


def ellipse_wire(a, b, z):
    return Part.Wire(Part.Ellipse(V(0, 0, z), a, b).toShape())


def sector(r_out, r_in, z0, z1, a0, span):
    h = z1 - z0
    s = Part.makeCylinder(r_out, h, V(0, 0, z0), V(0, 0, 1), span).cut(
        Part.makeCylinder(r_in, h, V(0, 0, z0), V(0, 0, 1), span))
    s.rotate(V(0, 0, 0), V(0, 0, 1), a0)
    return s


def nose_halfspace():
    """Solid below the plane z = x - X0 (for x > X0)."""
    b = Part.makeBox(200, 200, 200, V(0, -100, -200))
    b.rotate(V(0, 0, 0), V(0, 1, 0), -45)
    b.translate(V(NOSE_PLANE_X0, 0, 0))
    return b


def tunnel_shape():
    t = Part.makeBox(TUN_X1 + 80, TUN_W, TUN_H, V(-80, -TUN_W / 2, TUN_Z0))
    try:  # round the two front corners (discs are round anyway)
        edges = [e for e in t.Edges if e.BoundBox.XLength < 1e-6 and e.BoundBox.YLength < 1e-6
                 and abs(e.BoundBox.XMin - TUN_X1) < 1e-6]
        t = t.makeFillet(8.0, edges)
    except Exception as ex:
        print("tunnel fillet skipped:", ex)
    if TUN_ROOF_CHAMFER > 0:
     try:  # 45 deg chamfer on the roof corners: shorter bridge, still clears the rounded disc edges
        edges = [e for e in t.Edges if e.BoundBox.XLength > 50 and e.BoundBox.YLength < 1e-6
                 and abs(e.BoundBox.ZMin - (TUN_Z0 + TUN_H)) < 1e-6]
        t = t.makeChamfer(TUN_ROOF_CHAMFER, edges)
     except Exception as ex:
        print("tunnel roof chamfer skipped:", ex)
    # 45 deg side flare at the mouth so the discs slide in easily
    x_edge = TAIL_X                                                 # where the side walls end at the tail
    x_in, x_out = x_edge + MOUTH_CHAMFER, x_edge - 8.0
    flare = Part.makeLoft([
        Part.makePolygon([V(x_in, -TUN_W / 2, TUN_Z0), V(x_in, TUN_W / 2, TUN_Z0), V(x_in, TUN_W / 2, TUN_Z0 + TUN_H - TUN_ROOF_CHAMFER),
                          V(x_in, -TUN_W / 2, TUN_Z0 + TUN_H - TUN_ROOF_CHAMFER), V(x_in, -TUN_W / 2, TUN_Z0)]),
        Part.makePolygon([V(x_out, -TUN_W / 2 - (x_in - x_out), TUN_Z0), V(x_out, TUN_W / 2 + (x_in - x_out), TUN_Z0),
                          V(x_out, TUN_W / 2 + (x_in - x_out), TUN_Z0 + TUN_H - TUN_ROOF_CHAMFER),
                          V(x_out, -TUN_W / 2 - (x_in - x_out), TUN_Z0 + TUN_H - TUN_ROOF_CHAMFER), V(x_out, -TUN_W / 2 - (x_in - x_out), TUN_Z0)])], True, True)
    return t.fuse(flare)


def build_body():
    w0 = ellipse_wire(BODY_A - BOT_CHAMFER, BODY_B - BOT_CHAMFER, 0)
    w1 = ellipse_wire(BODY_A, BODY_B, BOT_CHAMFER)
    w2 = ellipse_wire(BODY_A, BODY_B, BODY_H)
    body = Part.makeLoft([w0, w1, w2], True, True)
    try:
        top_edges = [e for e in body.Edges if abs(e.BoundBox.ZMin - BODY_H) < 1e-6 and abs(e.BoundBox.ZMax - BODY_H) < 1e-6]
        body = body.makeFillet(TOP_FILLET, top_edges)
    except Exception as ex:
        print("top fillet skipped:", ex)

    hub = Part.makeCylinder(HUB_R, HUB_TOP - BODY_H + 1, V(0, 0, BODY_H - 1))
    try:  # lead-in chamfer so the cage drops on easily
        hub = hub.makeChamfer(1.0, [e for e in hub.Edges if abs(e.BoundBox.ZMin - HUB_TOP) < 1e-6])
    except Exception as ex:
        print("hub chamfer skipped:", ex)
    body = body.fuse(hub)

    # raised pads on the deck round the zip-tie slots (45 deg sides, clipped inside the top fillet and
    # clear of the cage) -> the deck is TAIL_PAD_H thicker wherever a tie pulls on it
    top_area = Part.Face(ellipse_wire(BODY_A - TOP_FILLET, BODY_B - TOP_FILLET, BODY_H - 1)).extrude(V(0, 0, 10))
    def deck_pad(x0, x1, y0, y1):
        def prect(z, g):
            return Part.makePolygon([V(x0 + g, y0 + g, z), V(x1 - g, y0 + g, z), V(x1 - g, y1 - g, z), V(x0 + g, y1 - g, z), V(x0 + g, y0 + g, z)])
        pad = Part.makeLoft([prect(BODY_H - 0.5, 0), prect(BODY_H + TAIL_PAD_H, TAIL_PAD_H)], True, True)
        return pad.common(top_area).cut(Part.makeCylinder(CAGE_CLEAR_R, 40, V(0, 0, 0)))
    body = body.fuse(deck_pad(TIE_GATE_X - 8.0, TIE_X + 8.0, -TAIL_PAD_W / 2, TAIL_PAD_W / 2))
    for sy in ((-1, 1) if SIDE_TIES else ()):
        ya, yb = sorted((sy * SIDE_TIE_Y[0], sy * SIDE_TIE_Y[1]))
        body = body.fuse(deck_pad(SIDE_TIE_X - 7.0, SIDE_TIE_X + 7.0, ya - 6.0, yb + 6.0))

    # tow eye fin (stadium in plan, 45 deg ramp at the back, top edges rounded)
    r = FIN_T / 2
    fin = Part.makeBox(FIN_FRONT - r - FIN_BACK, FIN_T, FIN_TOP, V(FIN_BACK, -r, 0))
    fin = fin.fuse(Part.makeCylinder(r, FIN_TOP, V(FIN_FRONT - r, 0, 0))).removeSplitter()
    ramp = Part.makeBox(300, 300, 300, V(0, -150, 0))
    ramp.rotate(V(0, 0, 0), V(0, 1, 0), -45)                 # region above z = x
    ramp.translate(V(FIN_BACK - BODY_H, 0, 0))               # -> above z = x - (FIN_BACK - BODY_H)
    fin = fin.cut(ramp)
    try:
        fin = fin.makeFillet(2.0, [e for e in fin.Edges if e.BoundBox.ZMin > BODY_H + 0.5])
    except Exception as ex:
        print("fin fillet skipped:", ex)
    body = body.fuse(fin)

    # loop posts: each loop = one piece of line, up one hole, down the other, crimped underneath
    posts, holes, sinks, crimps = [], [], [], []
    for ang, aim, tilt in zip(POST_ANGLES, POST_AIMS, POST_TILTS):
        th = math.radians(ang)
        px, py = BODY_A * POST_INSET * math.cos(th), BODY_B * POST_INSET * math.sin(th)
        ux, uy = math.cos(math.radians(aim)), math.sin(math.radians(aim))
        t = math.radians(tilt)
        d = V(math.sin(t) * ux, math.sin(t) * uy, math.cos(t))
        tang = V(-uy, ux, 0)
        base = V(px, py, BODY_H) - d * 7.0
        post = Part.makeCylinder(POST_R, POST_LEN, base, d)
        try:  # soften the post top so the line doesn't chafe
            tc = base + d * POST_LEN
            post = post.makeFillet(1.2, [e for e in post.Edges if e.Curve.__class__.__name__ == "Circle"
                                         and (e.Curve.Center - tc).Length < 1e-6])
        except Exception as ex:
            print("post fillet skipped:", ex)
        posts.append(post)
        top = base + d * POST_LEN
        mids = []
        for s in (-1, 1):
            p_top = top + tang * (s * HOLE_SPACING / 2)
            holes.append(Part.makeCylinder(HOLE_D / 2, 80, p_top + d * 1.0, d * -1))
            sinks.append(Part.makeCone(HOLE_D / 2, HOLE_D / 2 + 1.0, 1.01, p_top - d * 1.0, d))
            mids.append(p_top - d * (p_top.z / d.z))
        mid = (mids[0] + mids[1]) * 0.5
        cp = peaked_hole(CRIMP_R, 0, 2.0); cp.translate(V(mid.x, mid.y, 0))
        crimps.append(cp)
    for p in posts:
        body = body.fuse(p)

    body = body.cut(nose_halfspace())
    body = body.common(Part.makeBox(400, 400, 200, V(-200, -200, 0)))
    # square tail with a 45 deg chamfer on its top edge
    body = body.common(Part.makeBox(400, 400, 200, V(TAIL_X, -200, -1)))
    tc = Part.makeBox(300, 300, 300, V(0, -150, 0))
    tc.rotate(V(0, 0, 0), V(0, 1, 0), -45)                    # region above z = x
    tc.rotate(V(0, 0, 0), V(0, 0, 1), 180)                    # region above z = -x
    tc.translate(V(TAIL_X + TAIL_CHAMFER, 0, BODY_H))         # above z = BODY_H - (x - (TAIL_X + c))
    body = body.cut(tc.common(Part.makeBox(TAIL_CHAMFER + 1, 400, 30, V(TAIL_X - 1, -200, BODY_H - TAIL_CHAMFER))))

    # tow eye hole: teardrop along Y, 45 deg countersunk both faces
    er = EYE_D / 2
    eye = Part.makeCylinder(er, 40, V(EYE_HX, -20, EYE_Z), V(0, 1, 0))
    k = er / math.sqrt(2)
    eye = eye.fuse(prism_xz([(EYE_HX - k, EYE_Z + k), (EYE_HX, EYE_Z), (EYE_HX + k, EYE_Z + k), (EYE_HX, EYE_Z + er * math.sqrt(2))], -20, 20))
    for sy in (-1, 1):
        eye = eye.fuse(Part.makeCone(er + 1.5, er, 1.5, V(EYE_HX, sy * (FIN_T / 2 + 0.01), EYE_Z), V(0, -sy, 0)))
    body = body.cut(eye)

    # sinker tunnel, open at the tail
    tun = tunnel_shape()
    for i, c in enumerate(crimps):
        gap = c.distToShape(tun)[0]
        print("post %d crimp-to-tunnel wall %.1f mm" % (i, gap))
    for h in holes:
        if h.distToShape(tun)[0] < 0.5:
            print("WARNING loop hole breaks into tunnel")
    body = body.cut(tun)
    for fy in (SIDE_TIE_Y if SIDE_TIES else ()):
        sl = Part.makeBox(TIE_SLOT[1], TIE_SLOT[0], BODY_H, V(SIDE_TIE_X - TIE_SLOT[1] / 2, fy - TIE_SLOT[0] / 2, 0))
        vg = prism_xz([(SIDE_TIE_X - 4.0, 0), (SIDE_TIE_X + 4.0, 0), (SIDE_TIE_X, 4.0)], fy - 5, fy + 5)
        print("side tie slot y=%.0f: to channel %.1f mm, to crimp pockets %.1f mm (V-groove %.1f mm)" %
              (fy, sl.distToShape(tun)[0], min(sl.distToShape(c)[0] for c in crimps), min(vg.distToShape(c)[0] for c in crimps)))
    print("rear tail slot to tail face: %.1f mm" % (TIE_GATE_X - TIE_SLOT[0] / 2 - TAIL_X))
    xm = TAIL_X
    print("mouth side wall at the tail face: %.1f mm" % (BODY_B * math.sqrt(1 - (xm / BODY_A) ** 2) - TUN_W / 2))

    # tail zip tie: two enclosed slots straight through deck AND tray (like the front ones). Tie goes down
    # the first through the rear disc's eye and the floor, back up the second (crossing the mouth = gate),
    # and cinches in the groove on the deck. Clamps tray + deck, holds the disc, closes the mouth.
    pz = BODY_H + TAIL_PAD_H
    for tx in (TIE_X, TIE_GATE_X):
        body = body.cut(tie_slot(tx, 0, TIE_SLOT[0], TIE_SLOT[1], -0.01, pz, top=True, bottom=True))
    gx0, gx1 = TIE_GATE_X - TIE_SLOT[0] / 2, TIE_X + TIE_SLOT[0] / 2
    # (no groove on the pad: the tie sits on the full pad thickness)

    for h in holes + sinks + crimps:
        body = body.cut(h)

    # side zip ties (one per side, tie once): enclosed slots through deck pad + tray, tie recessed in a
    # groove on the pad and a 45 deg V-groove underneath, both closed at the ends
    fx, pz = SIDE_TIE_X, BODY_H + TAIL_PAD_H
    for sy in ((-1, 1) if SIDE_TIES else ()):
        ya, yb = sy * SIDE_TIE_Y[0], sy * SIDE_TIE_Y[1]
        for yy in (ya, yb):
            body = body.cut(tie_slot(fx, yy, TIE_SLOT[1], TIE_SLOT[0], -0.01, pz, top=True, bottom=True))
        y0, y1 = min(ya, yb) - TIE_SLOT[0] / 2, max(ya, yb) + TIE_SLOT[0] / 2
        # (no groove on the pad: the tie sits on the full pad thickness)
        body = body.cut(prism_xz([(fx - 4.0, -0.01), (fx + 4.0, -0.01), (fx, 4.0)], y0, y1))

    # bayonet L-slots in hub
    for a in BAY_ANGLES:
        body = body.cut(sector(HUB_R + 1, SLOT_RIN, SLOT_Z0, HUB_TOP + 1, a, SLOT_ENTRY_SPAN))
        body = body.cut(sector(HUB_R + 1, SLOT_RIN, SLOT_Z0, SLOT_Z1, a, SLOT_ENTRY_SPAN + SLOT_TURN))
        roof = sector(HUB_R + 1, SLOT_RIN, SLOT_Z1 - 0.01, SLOT_Z1 + 4, a, SLOT_ENTRY_SPAN + SLOT_TURN)
        roof = roof.cut(Part.makeCone(SLOT_RIN, SLOT_RIN + 4, 4, V(0, 0, SLOT_Z1)))   # 45 deg roof, no ledge
        body = body.cut(roof)
        bump_a = a + SLOT_ENTRY_SPAN + SLOT_TURN - LUG_SPAN - DETENT_SPAN - 1.0
        body = body.fuse(sector(SLOT_RIN + 0.5, DETENT_RIN, SLOT_Z0, SLOT_Z1, bump_a, DETENT_SPAN))
    return body.removeSplitter()


def split_body(body):
    below = Part.makeBox(400, 400, 200 + SPLIT_Z, V(-200, -200, -200))
    above = Part.makeBox(400, 400, 200, V(-200, -200, SPLIT_Z))
    keep = Part.makeBox(100, FIN_T, 100, V(TAB_SPLIT_X, -FIN_T / 2, SPLIT_Z))
    tray = body.common(below).fuse(body.common(keep))
    for x, y in PINS:
        pin = Part.makeCylinder(PIN_R, PIN_H + 0.01, V(x, y, SPLIT_Z - 0.01))
        try:
            pin = pin.makeChamfer(0.6, [e for e in pin.Edges if e.BoundBox.ZMin > SPLIT_Z + 1])
        except Exception as ex:
            print("pin chamfer skipped:", ex)
        tray = tray.fuse(pin)
    notch = Part.makeBox(100, FIN_T + 2 * NOTCH_CLR, 100, V(TAB_SPLIT_X - NOTCH_CLR, -FIN_T / 2 - NOTCH_CLR, SPLIT_Z - 1))
    deck = body.common(above).cut(notch)
    for x, y in PINS:
        sk = peaked_hole(PIN_R + PIN_CLR, SPLIT_Z, PIN_H - 0.6 + 0.3); sk.translate(V(x, y, 0))
        deck = deck.cut(sk)
    return tray.removeSplitter(), deck.removeSplitter()


def teardrop_cutter(x0, length, w, z_bot, z_top):
    """Radial slot cutter along +X: round bottom (prints fine), 45 deg pointed top (no bridge)."""
    c = Part.makeBox(length, w, z_top - z_bot, V(x0, -w / 2, z_bot))
    c = c.fuse(Part.makeCylinder(w / 2, length, V(x0, 0, z_bot), V(1, 0, 0)))
    sq = w / math.sqrt(2)
    d = Part.makeBox(length, sq, sq, V(x0, -sq / 2, -sq / 2))
    d.rotate(V(0, 0, 0), V(1, 0, 0), 45)
    d.translate(V(0, 0, z_top))
    return c.fuse(d)


def build_cage():
    """Prints upright (open end down) with no overhangs: 45 deg conical roof up to a small
    top vent, teardrop vents, 45 deg lug undersides."""
    R, w = CAGE_RO, CAGE_WALL
    z0, z1 = BODY_H, BODY_H + CAGE_H
    ri = R - w
    cone_h = R - (APEX_R + APEX_RIM)
    zw = z1 - cone_h                                   # where the wall turns into the roof
    outer = Part.makeCylinder(R, zw - z0, V(0, 0, z0)).fuse(
        Part.makeCone(R, APEX_R + APEX_RIM, cone_h, V(0, 0, zw)))
    k_in = R + zw - w * math.sqrt(2)                   # inner roof: r + z = k_in (parallel to the outer)
    zc = k_in - ri
    inner = Part.makeCylinder(ri, zc - z0 + 0.01, V(0, 0, z0 - 0.01)).fuse(
        Part.makeCone(ri, 0, ri, V(0, 0, zc)))
    cage = outer.cut(inner)
    cage = cage.cut(Part.makeCylinder(APEX_R, 20, V(0, 0, z1 - 10)))      # top vent
    # side vents on the straight wall
    vb, vt = HUB_TOP + 3 + VENT_W / 2, zw - 3 - VENT_W / 2
    for i in range(VENT_N):
        c = teardrop_cutter(ri - 2, 10, VENT_W, vb, vt)
        c.rotate(V(0, 0, 0), V(0, 0, 1), 360.0 / VENT_N * i)
        cage = cage.cut(c)
    # roof vents running down the 45 deg cone
    for i in range(ROOF_VENT_N):
        c = teardrop_cutter(5, 40, VENT_W, zw + 2 + VENT_W / 2, zw + ROOF_VENT_LEN)
        c.rotate(V(0, 0, 0), V(0, 0, 1), 360.0 / ROOF_VENT_N * i + 360.0 / VENT_N / 2)
        cage = cage.cut(c)
    for a in BAY_ANGLES:   # lugs shown in the locked position
        la = a + SLOT_ENTRY_SPAN + SLOT_TURN - LUG_SPAN - 0.5
        lug = sector(ri + 0.2, LUG_RIN, LUG_Z0, LUG_Z1 + 3, la, LUG_SPAN)
        lug = lug.cut(Part.makeCone(LUG_RIN, LUG_RIN + 3, 3, V(0, 0, LUG_Z1)))     # top slopes with the hub roof
        ch = ri + 0.2 - LUG_RIN
        lug = lug.cut(Part.makeCone(LUG_RIN + ch, LUG_RIN, ch, V(0, 0, LUG_Z0)))   # 45 deg underside
        cage = cage.fuse(lug)
    # grip ribs, tops beveled so they ramp into the wall (nothing to snag line or weed)
    rib_h, bevel = 12.0, 4.0
    limiter = Part.makeCylinder(R + 2, rib_h - bevel, V(0, 0, z0)).fuse(
        Part.makeCone(R + 1.0, R - 0.2, bevel, V(0, 0, z0 + rib_h - bevel)))
    for i in range(12):
        rib = Part.makeBox(1.2, 3.0, rib_h, V(R - 0.2, -1.5, z0))
        rib.rotate(V(0, 0, 0), V(0, 0, 1), 360.0 / 12 * i + 15)
        cage = cage.fuse(rib.common(limiter))
    bait = inner.common(Part.makeBox(200, 200, 200, V(-100, -100, HUB_TOP))).Volume / 1000
    print("cage: wall to z=%.0f, roof cone %.0f mm, bait space above hub ~%.0f cm3" % (zw - z0, cone_h, bait))
    return cage.removeSplitter()


def stl(shape, path):
    MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.03, AngularDeflection=0.25, Relative=False).write(path)


def main():
    body = build_body()
    tray, deck = split_body(body)
    cage = build_cage()
    for n, s in (("Tray", tray), ("Deck", deck), ("Cage", cage)):
        g = (s.Area * 1.2 + max(s.Volume - s.Area * 1.2, 0) * 0.15) / 1000 * 1.27
        print(n, "valid:", s.isValid(), "solids:", len(s.Solids), "vol cm3: %.1f" % (s.Volume / 1000),
              "bbox:", [round(x, 1) for x in (s.BoundBox.XLength, s.BoundBox.YLength, s.BoundBox.ZLength)],
              "est. PETG @3 walls/15%%: %.0f g" % g)
    print("tunnel: %.0f long x %.0f wide x %.1f tall, floor %.1f, roof %.1f" %
          (TUN_X1 - (-BODY_A), TUN_W, TUN_H, TUN_Z0, BODY_H - TUN_Z0 - TUN_H))
    print("overlap mm3: deck/cage %.2f  tray/cage %.2f  tray/deck %.2f" %
          (deck.common(cage).Volume, tray.common(cage).Volume, tray.common(deck).Volume))

    doc = App.newDocument("CrabSnare")
    objs = []
    for n, sh in (("Tray", tray), ("Deck", deck), ("Cage", cage)):
        o = doc.addObject("Part::Feature", n); o.Shape = sh; objs.append(o)
    doc.recompute()
    Part.export(objs, os.path.join(OUT, "CrabSnare.step"))
    stl(tray, os.path.join(OUT, "Tray.stl"))                 # prints as modelled, floor on the bed
    pd = deck.copy()
    pd.translate(V(0, 0, -pd.BoundBox.ZMin))               # prints with the split face on the bed
    stl(pd, os.path.join(OUT, "Deck.stl"))
    pc = cage.copy()
    pc.translate(V(0, 0, -pc.BoundBox.ZMin))      # print upright, open end on the bed
    stl(pc, os.path.join(OUT, "Cage.stl"))
    try:
        doc.saveAs(os.path.join(OUT, "CrabSnare.FCStd"))
    except Exception as ex:
        print("FCStd NOT saved (open in FreeCAD?):", ex)


main()
