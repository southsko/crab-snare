# Sled crab snare (Dungeness, beach/jetty casting, California 6-loop legal)

Rebuild everything: `"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" build.py`
(all sizes are parameters at the top of build.py)

| File | Print it |
|---|---|
| Tray.stl | floor down. Floor, side walls, sinker channel, nose ramp, tow eye, 4 locating pins |
| Deck.stl | flat (split face) down. Roof plate, bait hub, 6 loop posts |
| Cage.stl | upright, open end down. Bait cage |
| CrabSnare.FCStd / .step | assembled model |

**No supports and no bridges on any part.** Every downward-facing surface is 45 deg or steeper; this was checked on the exact CAD faces.
- Crimp pockets and pin sockets have cone roofs.
- The tail zip-tie slots are closed holes with 45 deg lead-in chamfers. The deck pad has no groove, so the plastic between the slots is the full 6.5 mm.
- The tow-eye hole is a teardrop (45 deg top).
- The twist-lock slot roofs slope at 45 deg, and the lug tops match. A pull on the cage pushes the lugs inward onto the hub, so they can't cam off.

## Sizes
- Body: 128 x 116 mm oval with a squared-off tail (121 mm long), 20 mm thick when assembled (4 mm floor).
  - The tail is cut flat with a 45 deg top chamfer, so the walls beside the weight mouth are 4.4 mm thick or more (no knife edges).
  - The deck has a 3 mm raised pad (45 deg sides) round the tail tie slots, so the deck there is 6.5 mm thick. The two tail slots are 10 mm apart (about 8 mm of solid plastic between them, through the 4 mm floor), with 3.9 mm of plastic behind the rear one.
  - Split at 16.5 mm: the tray is 16.5 mm tall plus the eye, and the deck is 3.5 mm plus the hub and posts.
  - 45 deg nose ramp and bottom chamfer.
- Tow eye: an upright fin, 10 mm thick, with a 7 mm sideways line hole (teardrop top, 45 deg countersinks on both faces).
  - The line wraps a 5 mm post with a fully round front. That post is rounded in the print plane, so it's smooth on the line and strong along the layers; it's good for well over 20 lb tugs.
  - The back of the fin ramps up from the deck at 45 deg, and the top edges are rounded.
  - It's one piece with the tray, so line pull never loads the seam.
- Sinker channel: 44 mm wide x 12.5 mm tall, open at the tail with a 1.5 mm chamfered mouth, about 94 mm long. Flat disc sinkers lie flat, one behind the other.
  - Sized for a 42 mm x 11 mm 3 oz disc plus a 36 mm 2 oz disc.
  - **These are estimates: measure yours** and set `DISC_D`, `DISC2_D`, `DISC_T`, `EYE_L`.
- Bait cage: 65 mm OD x 56 mm tall, about 74 cm3 of bait space.
  - Straight wall for 29 mm, then a 45 deg cone roof with a 6 mm vent at the tip.
  - 12 side vents and 6 roof vents, all teardrop shaped (round bottom, 45 deg pointed top).
  - Twist-lock, with 0.8 mm clearance all round (cage bore to hub, and lugs in their slots), so it goes on easily even in nylon. The small bump on the hub no longer touches the lugs, so there is no click. The lugs have 45 deg undersides, and the hub has a lead-in chamfer.
- 6 loop posts (California max), two 2.3 mm holes each, rounded tops, crimp recesses underneath the tray.
  - The middle pair leans 25 deg straight out to the sides.
  - The front and rear pairs lean 35 deg toward the nose and tail corners, so the loops cover all the way round.

## Print
- PETG or ASA, 3-4 walls, 15-25% gyroid.
- Estimated weights: tray ~67 g, deck ~54 g, cage ~29 g.

## Assembly
1. **Join tray + deck:** drop the deck onto the tray. The 4 pins locate it, and the notch fits around the tow eye.
2. **Loops (x6):** these also clamp the two halves together.
   - One piece of line per loop: 14" (36 cm) of 100 lb mono leader. 100 lb is the usual line for snare loops.
   - Go up one hole of a post, form a loop about 9-10 cm across, then down the other hole. The line runs through both the deck and the tray.
   - Crimp the two ends together underneath and pull the crimp up into its recess. Use aluminum double-barrel sleeves sized for 100 lb mono (for example AFW 4F8, 1.12 mm bore). If your line will not go in, use the next size up. Crimp with a proper crimping tool, not pliers.
   - 0.065-0.080" trimmer line also fits the holes.
3. **Sinkers:** slide them in from the tail, flat side down, eyes pointing back toward the tail.
   - 3 oz only: put it at the tail end, eye under the front tail slot.
   - 5 oz: push the 2 oz in first, then the 3 oz behind it.
4. **Tail zip tie:** two closed slots through the deck **and** the tray. Go down the front tail slot, through the rear disc's eye, out through the floor, back up the rear slot (that leg crosses the mouth), and cinch it on top of the deck pad. This clamps tray + deck, holds the disc and closes the mouth.
5. **Main line:** tie straight to the eye (it's round on the line), or use a swivel/snap.
6. **Bait:** fill the cage, push it down over the hub with the lugs lined up with the slots, and twist about 25 deg until it clicks.
