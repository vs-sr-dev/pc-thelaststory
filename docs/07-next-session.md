# TODO — session 4

The game plays from the strap screen to Zael's mark (the Gathering) and the
save after it, with the Classic Controller at 30 frames a second
(`00-sessions.md`). Programs no longer link where it plays if
`tools/shaderlist.txt` has them.

1. **Play on**, with `--shader-list ../../tools/shaderlist.txt` and
   `TLS_HITCH=1 WIIKIT_PERF=1`: Lazulis, the battles, the cutscenes and
   their voices, saving and loading. Each run adds what it sees to
   `build/shaderlist.txt`; bring it into the port's list (the command is
   at the head of `tools/shaderlist.txt`). The stretch from the cave's
   entrance to the Gathering is not listed yet (played before the list
   existed): a replay on a copy of the NAND would add it.
2. **The stalls left** are loads: the main thread reading the disc
   (`DVDReadAsync` from the scene's set-up, 8046Cxxx) or in its own work
   (`fn_8009BF3C`, from 800BDBC8) while IPC replies come in, 60-500 ms.
   How long does wiikit take to answer a disc read, and could it answer
   sooner?
3. **The freeze at the third frame**, rare (once in seven boots today,
   once in October): `TLS_HITCH` now reports the threads every 2 s while a
   frame stays late. Catch one and read where everything sleeps.
4. **The frame rate**: the engine counts frames, not time (`atnEff_Advance`
   gets 1.0 at every frame, `03-executable.md`). Find where that 1.0 comes
   from (its caller 8023686C, up through 800D28FC, 800D2500: the frame's
   update) and what else reads it: the characters, their `.motion`, the
   camera, the physics. Then 60: the engine's VI callbacks act on every
   other retrace when `atnGfx`'s object has `+0xCC` set; clear it, hand
   half a step, and see what breaks.
5. The Remote and Nunchuk: only if the Classic falls short.

Build and run:

    sh build/rebuild.sh                     # recompile, ninja
    cd build/run1 && ../recomp-build/wiiboot ../extract --symbols ../recomp/symbols.tsv         --nand ../nand --fonts ../fonts --shader-list ../../tools/shaderlist.txt

`build/extract` is a junction to the reverse engineering project's
extraction. `build/fonts` holds the boot ROM's fonts and `dsp_coef.bin`
(copied from Monster Hunter Tri's build). Unattended: `WIIKIT_PAD="50:A
54:A ..."` presses the Classic's buttons too; A every 4 s from 50 s reaches
the cave in about a minute, the first tutorial in about four.
`WIIKIT_AUDIODBG=1` reports each audio block without its frame, with where
every guest thread was. `WIIKIT_SHADERSALT=word` makes every program new to
the driver: a first run's links, to test the list.
