# TODO — session 2

The game runs from the strap screen into Chapter 1 at 30 frames a second,
with the Classic Controller (session 1). Nobody has played it yet.

1. **Play it.** The cave, the first battles (the Gathering, the crossbow,
   the commands), the first cutscenes and their voices, Lazulis. Note what
   is wrong to the eye and the ear; F12 traces a frame's GX commands.
2. **The sound's gaps.** `WIIKIT_AUDIODBG=1` during loads: the AI
   interrupt raised, not acknowledged for 20-30 ms, the main thread in the
   engine's loading code (8020xxxx-8021xxxx) with interrupts enabled. Find
   what keeps it from taking them (a host-side wait inside a guest call, a
   loop the recompiler does not poll in). Monster Hunter Tri's open gaps
   may be the same.
3. **The frame rate.** The goal of the port: a rate the Wii never held.
   The engine runs at 30 (its VI callbacks act on every other retrace when
   `atnGfx`'s object has `+0xCC` set) and steps its world by a time step
   (the RE project found `r13-0x7AE0` = dt). First measure where the frame
   time goes in the heaviest places (Lazulis, big battles) with
   `WIIKIT_PERF=1` and `WIIKIT_PROFILE`; then see whether the engine can
   run at 60 with `+0xCC` cleared and its step halved, and what breaks
   (animation at 30 frames, `.motion`; effects; the camera).
4. Fog: `gx: fog (not drawn), type 2` — the renderer has no fog yet;
   the game uses it (wiikit, layer 5).
5. The Remote and Nunchuk: the game also plays with them; wiikit has no
   Nunchuk. Only if the Classic falls short.

Build and run:

    sh build/rebuild.sh                     # recompile, ninja
    cd build/run1 && ../recomp-build/wiiboot ../extract --symbols ../recomp/symbols.tsv --nand ../nand --fonts ../fonts

`build/extract` is a junction to the reverse engineering project's
extraction. `build/fonts` holds the boot ROM's fonts and `dsp_coef.bin`
(copied from Monster Hunter Tri's build). Unattended: `WIIKIT_PAD="50:A
54:A ..."` presses the Classic's buttons too; A every 4 s from 50 s reaches
the first tutorial in about 4 minutes.
