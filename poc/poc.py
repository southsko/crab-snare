"""Cage retention proofs-of-concept. All fit the base as printed (same hub). Run:
"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" poc/poc.py
Each variant writes poc/Cage_<X>.stl (print upright) and goes into poc/CagePOC.FCStd with the deck."""
import os, math
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else "C:/Users/Joey/crab-snare/poc"
SRC = os.path.join(os.path.dirname(HERE), "build.py")
_src = open(SRC, encoding="utf-8").read()
_src = _src[:_src.rindex("\nmain()")]
exec(compile(_src, SRC, "exec"))

R = CAGE_RO
ZB = BODY_H                  # deck top / cage bottom
LOCK_ANGS = BAY_ANGLES       # slot start angles on the hub (cage drawn locked)


def rot(sh, ang):
    sh = sh.copy(); sh.rotate(V(0, 0, 0), V(0, 0, 1), ang); return sh


# ---------- A: silicone band hooks (band from hook to the base of a loop post) ----------
# J-hook in the r-z plane: 45 deg underside, upturned tip holds the band against an outward pull.
HOOK_ANGS = [75.0, 195.0, 315.0]   # 3-fold, same for every way the cage goes on; posts 90 and 230 sit
                                    # 15-35 deg CCW ahead, so the band pulls the cage the LOCK way
def hook(ang, width=4.0):
    u0 = R - 0.3
    pts = [(u0, ZB + 2.0), (u0 + 6.3, ZB + 8.3), (u0 + 6.3, ZB + 13.0), (u0 + 4.8, ZB + 13.0),
           (u0 + 4.8, ZB + 10.0), (u0, ZB + 7.5)]
    h = prism_xz(pts, -width / 2, width / 2)
    return rot(h, ang)

def cage_A():
    c = build_cage(skip_ribs=tuple(HOOK_ANGS))
    for a in HOOK_ANGS:
        c = c.fuse(hook(a))
    return c.removeSplitter()


# ---------- B: strap holes into the empty slot (reusable release zip tie, mono, or band) ----------
# Two holes side by side over each slot's entry channel, in the lug band (z 22.4-27.6 on the hub).
# Strap goes in one hole, along the empty slot, out the other. Turning the cage back to unlock drives
# the strap into the slot's end wall, so it can't come undone.
def cage_B():
    skip = tuple((a + 3.0) % 360 for a in LOCK_ANGS)       # rib at 15/135/255 sits over the holes
    c = build_cage(skip_ribs=skip)
    for a in LOCK_ANGS:
        for da in (3.5, 12.5):                               # inside the 15 deg entry, clear of its walls
            h = teardrop_cutter(R - CAGE_WALL - 1.0, CAGE_WALL + 2.0, 2.4, SLOT_Z0 + 0.8, SLOT_Z1 - 0.8 - 1.2)
            c = c.cut(rot(h, a + da))
    return c.removeSplitter()


# ---------- C: flex tab that snaps into the slot (no extra parts) ----------
# A tongue cut into the cage wall, free at the open bottom edge, with a square-sided nub on the inside.
# Twisting on, the nub rides the hub (tongue flexes out 1 mm) and drops into the slot at the end of the
# turn; turning back is blocked by the slot's end wall. To remove: lift the tab at the bottom, twist.
NUB_RIN = 28.3
def cage_C():
    skip = tuple((a + 3.0) % 360 for a in LOCK_ANGS)
    c = build_cage(skip_ribs=skip)
    ri = R - CAGE_WALL
    for a in LOCK_ANGS:
        mid = a + 4.0                                        # nub 2-6 deg into the slot: ~1 deg of play
        half_t = math.degrees(4.0 / R)                       # tongue 8 mm wide
        for s in (-1, 1):
            sl = teardrop_cutter(ri - 1.0, CAGE_WALL + 2.0, 1.0, ZB - 2.0, ZB + 14.0)
            c = c.cut(rot(sl, mid + s * (half_t + math.degrees(0.5 / R))))
        # nub: square sides, 45 deg top and bottom (prints upright, cams down over the hub chamfer)
        nz0, nz1 = SLOT_Z0 + 0.4, SLOT_Z1 - 0.8
        d = ri + 0.2 - NUB_RIN
        prof = [(ri + 0.2, nz0), (NUB_RIN, nz0 + d), (NUB_RIN, nz1 - d), (ri + 0.2, nz1)]
        w = 4.0
        nub = prism_xz(prof, -w / 2, w / 2)
        c = c.fuse(rot(nub, mid))
        # fingernail tab at the bottom of the tongue (sits on the bed when printing)
        tab = prism_xz([(R - 0.3, ZB), (R + 2.2, ZB), (R + 2.2, ZB + 1.0), (R - 0.3, ZB + 3.5)], -3.0, 3.0)
        c = c.fuse(rot(tab, mid))
    return c.removeSplitter()


if __name__ == "__main__" or True:
    body = build_body()
    tray, deck = split_body(body)
    doc = App.newDocument("CagePOC")
    o = doc.addObject("Part::Feature", "Deck"); o.Shape = deck
    o = doc.addObject("Part::Feature", "Tray"); o.Shape = tray
    for name, fn, dx in (("A_band_hooks", cage_A, 0.0), ("B_strap_holes", cage_B, 0.0), ("C_flex_tab", cage_C, 0.0)):
        cg = fn()
        print(name, "valid", cg.isValid(), "solids", len(cg.Solids),
              "overlap deck %.2f tray %.2f mm3" % (cg.common(deck).Volume, cg.common(tray).Volume),
              "bbox", [round(x, 1) for x in (cg.BoundBox.XLength, cg.BoundBox.YLength, cg.BoundBox.ZLength)])
        o = doc.addObject("Part::Feature", "Cage_" + name); o.Shape = cg
        pc = cg.copy(); pc.translate(V(0, 0, -pc.BoundBox.ZMin))
        stl(pc, os.path.join(HERE, "Cage_%s.stl" % name))
    doc.recompute()
    doc.saveAs(os.path.join(HERE, "CagePOC.FCStd"))
