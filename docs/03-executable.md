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
| `tools/names-manual.tsv` | 54 | 50 functions the runtime hooks that the others miss, each with its evidence; four of the engine's own (below) |
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
