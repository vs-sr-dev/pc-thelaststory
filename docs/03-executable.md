# The executable

`sys/main.dol` of the European disc (SLSP01): build 2350 of 25 November
2011 (`files/revision.txt`), the RVL SDK of August 2010 (its libraries'
banners: `<< RVL_SDK - DVD release build: Aug 23 2010 ... >>`), NW4R's
sound library of June 2009. 7.4 MB of code in two text sections:

    T0  80004000-80006720   .init
    T1  800081C0-8072D2A0   .text
    bss 807C66C0 + 0xC2CF0

It is stripped, but not bare: its RTTI survived, 704 C++ class names with
their vtables (the reverse engineering project's
[doc 18](https://github.com/vs-sr-dev/wii-thelaststory-re/blob/main/docs/18-dol-classes.md)).
The engine calls itself LastWorld; its graphics layer's assertions name
`atn_graphics_device.cpp`.

## Recompiled

wiikit's discovery finds 18 382 units (1 868 161 instructions, no gaps),
321 switch tables sized from the code (one unresolved, at 80695B24, in
MSL's code: never reached so far). Recompiled and built at the first try.

## Names

The runtime needs the names of the SDK functions it replaces; nothing
else. `tools/names.py` puts them together, most trusted first:

| Source | Names | What |
|---|---|---|
| `tools/names-manual.tsv` | 62 | 50 functions the runtime hooks that the others miss, each with its evidence; twelve the port hooks or names, the engine's and the SDK's sound (below) |
| `files/LastWorld.sel` | 11 | the executable's exports: the Home Button menu's six, libc |
| the SDK's strings | 26 | a function that prints `Name()` names itself |
| Dolphin's `totaldb.dsy` | 808 | by signature (`tools/sigmatch.py`) |

The hand names were found with `tools/neighbors.py`: in one object file the
linker keeps the functions in order, so a function the signatures missed
sits at the same distance from a neighbour they found, in the symbolised
executable of another game of the same SDK (Victorious's ELF). Each was then
confirmed on its code. Two traps:

* Dolphin's database names `80660C50` `WPADSetSpeakerVolume`. It stores one
  byte to a global, not a channel's: it is `WPADSetAutoSleepTime`; the real
  `WPADSetSpeakerVolume` is `806631A0`.
* `WPADIsDpdEnabled` and `WPADGetDataFormat` (and `WPADIsSpeakerEnabled`)
  have the same shape (a getter on the channel's control block): the
  database names two of them `WPADIsDpdEnabled`. Order decides.

`WPADSetAutoSleepTime` and `WPADResetAutoSleepTimeCount` are not in
Victorious's SDK; they sit between `WPADDisconnect` and `WPADProbe`.

## No modules at run time

The disc has `LastWorld.sel` and `LastWorld_tools.rso`, an RSO module and
the executable's export table. The game never loads them: no `.sel` or
`.rso` name is in the executable, and the module imports the debug menu's
functions (`SetTask__17SequenceDebugMenu`, ...), which the `.sel` does not
export (the reverse engineering project's
[doc 06](https://github.com/vs-sr-dev/wii-thelaststory-re/blob/main/docs/06-debug-menu.md)).
`wiikit.recomp --rso` rightly refuses it. The port recompiles the
executable alone.

## The engine's frame pacing

The one thing of the engine the port had to read before it would run past
its third frame (`atn_graphics_device.cpp`, named by hand):

| Address | Name given | What it does |
|---|---|---|
| 80071AFC | `atnGfx_SwapFrame` | queues the frame in a ring of five (807C6F68): the FIFO write pointer at the end of its draws, its XFB, its draw-sync token; if no breakpoint is set, sets one there (`GXEnableBreakPt`); then the token, the copy to the XFB; then sleeps until at most one frame is queued |
| 80072BDC | `atnGfx_BreakPtCallback` | the GP has reached the frame's end: if the frame's XFB is not the one on screen, the frame leaves the ring and the breakpoint moves to the next one (or is cleared); if it is, it waits for the flip |
| 80072D74 | `atnGfx_PreRetrace` | at a retrace (every other one at 30 frames a second): when the PE token is one past the last seen, the other XFB goes on screen |
| 80072E08 | `atnGfx_PostRetrace` | after a flip, the frame that waited for it leaves the ring |

The GP is held at the end of each frame until its XFB is free: the engine
keeps the CPU at most a frame ahead of the GP and never draws into the
picture on screen. It depends on the console's FIFO breakpoint stopping
the GP, which wiikit did not model (`10-wiikit.md`).

`TLS_GFXTRACE=1` logs the ring at each of these four calls.

`atnGfx_SwapFrame` ends in a wait: interrupts off, then while more than one
frame is queued, interrupts on and `OSSleepThread` on the ring's queue
(807C6F60), which the breakpoint callback and the post-retrace wake when a
frame leaves. The CPU goes on a frame ahead, the GP held at that frame's
breakpoint until the picture before it has been on screen. Two things
follow on wiikit, whose GP keeps up with the CPU:

* the GP waits at the breakpoint through most of the next frame, and so
  does anything the CPU asks of it then: a `GXDrawDone` mid-frame waited
  for the flip (below, the equipment);
* the wait enables interrupts before it sleeps. wiikit delivers what is
  pending right there, and a frame that leaves the ring then wakes no one:
  if nothing is left to leave, the game sleeps for good.

The port waits on in `atnGfx_SwapFrame` until the ring is empty (asleep with
interrupts off, as the SDK means `OSSleepThread`), and wakes the ring's
queue at every post-retrace. The pace stays 30 frames a second; the CPU
starts each frame with the GP free. `TLS_AHEAD=1` keeps the engine's rule.

A frame of a busy scene is larger than the FIFO (512 KB here; a frame
recorded in a dungeon by the reverse engineering project is 555 KB). While
the GP waits at the breakpoint the CPU fills the FIFO, and on the console
the CP's overflow interrupt suspends the writing thread until the GP has
drained it. wiikit did not raise it: the CPU wrote on round the FIFO, a
breakpoint's address came round again in what was held, the GP stopped at
the wrong one, and the game froze once the player had control (`10-wiikit.md`).

## The equipment's textures

The characters' bodies wear textures made at load time (the reverse
engineering project found them in RAM and nowhere on the disc): the
dyed equipment.

| Address | Name given | What it does |
|---|---|---|
| 800D7278 | | composes the texture with the GP (`atn::TextureComposite`), `GXCopyTex` to RAM as RGBA8, waits for a draw-done |
| 800C0FBC | `atnTex_Unswizzle` | (data, format, w, h): GX tiles to rows, in place |
| 800D6E48 | `atnTex_CompressCopy` | (src, dst, w, h): ARGB to RGBA into `"UnswizzledTemp"`, then CMPR through `"DxtTemp"` |

The CPU reads an EFB copy. wiikit keeps EFB copies on the host GPU and
leaves RAM alone, so the bodies came out black and see-through (the
heads, plain textures from the disc, were right). The port's layer hooks
`atnTex_Unswizzle` and has wiikit write the copy into RAM first
(`gx_copy_to_ram`). Writing it any later, at the compression, puts tiles
where the game has already laid rows: the bodies came out in green and
black stripes.

The textures are made when a character comes in, each by
`atnTex_Composite` (800D7278), with a `GXDrawDone` (806140C0). With the
engine's frame wait, each draw-done waited for the flip: up to 33 ms a
texture, 80-130 ms a character, sound included. With the port's, 5 ms on
average.

## The clock

The effects advance by `atnEff_Advance` (8022D078): the frames handed to it,
times a speed (the object at `-0x6718(r13)`, +0x3A4), in steps of 1.0 with
the remainder carried; each step's length goes to `-0x7AE0(r13)`, which the
emitters integrate by (the reverse engineering project's doc 20). Its
caller hands it 1.0 at every frame: the engine counts frames, not time.

## The sound

NW4R's AI callback (805B6978, registered over AX's) calls AX's
(`__AXOutAiCallback`, 806098D0: mix a frame if the DSP is done, else mark
the deadline for `__AXDSPResumeCallback`, 80609990), then **enables
interrupts** (`OSEnableInterrupts`, 805F1EA0) for the rest of its work.
The SDK's `__AIDHandler` skips the callback while it runs. On the console
the next AI interrupt is 3 ms away; on wiikit, which caught up a late block
at once, it came inside that window, and the block had no frame (wiikit
now waits for the handler, `10-wiikit.md`).
