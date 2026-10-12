# TODO — session 3

The game plays from the strap screen into Chapter 1 at 30 frames a second
with the Classic Controller; since session 2 the sound holds through the
tutorial's window, behind other windows, and when characters come in
(`00-sessions.md`).

1. **The frame rate**, the goal of the port. The engine counts frames, not
   time: `atnEff_Advance` gets 1.0 at every frame (`03-executable.md`).
   Find where that 1.0 comes from (its caller 8023686C, up through
   800D28FC, 800D2500: the frame's update) and what else reads it: the
   characters, their `.motion` (30 frames a second, the reverse
   engineering project's doc 10), the camera, the physics. Then 60: the
   engine's VI callbacks act on every other retrace when `atnGfx`'s object
   has `+0xCC` set; clear it, hand half a step, and see what breaks.
   `TLS_HITCH=1` and `WIIKIT_PERF=1` measure.
2. **Play on.** The first battles (the Gathering, the crossbow, the
   commands), the cutscenes and their voices, Lazulis, saving and loading.
   `TLS_HITCH=1` while playing: any stall the user feels, with where the
   threads were. Two frames over 60 ms remain on the way into the cave:
   the scene being set up (the engine's own work, 8046Cxxx).
3. Fog: `gx: fog (not drawn), type 2` — the renderer has no fog yet;
   the game uses it (wiikit, layer 5).
4. The Remote and Nunchuk: the game also plays with them; wiikit has a
   Nunchuk since `57169a2` (Crystal Bearers). Only if the Classic falls
   short.

Build and run:

    sh build/rebuild.sh                     # recompile, ninja
    cd build/run1 && ../recomp-build/wiiboot ../extract --symbols ../recomp/symbols.tsv --nand ../nand --fonts ../fonts

`build/extract` is a junction to the reverse engineering project's
extraction. `build/fonts` holds the boot ROM's fonts and `dsp_coef.bin`
(copied from Monster Hunter Tri's build). Unattended: `WIIKIT_PAD="50:A
54:A ..."` presses the Classic's buttons too; A every 4 s from 50 s reaches
the cave in about a minute, the first tutorial in about four.
`WIIKIT_AUDIODBG=1` reports each audio block without its frame, with where
every guest thread was.
