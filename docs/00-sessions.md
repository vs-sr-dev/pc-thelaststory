# Session log

## Session 1 — from the disc to the first cave

Goal: set the port up on wiikit, recompile, boot. It went past that: the
game runs from the strap screen through the title and the menu into its
first chapter, at a steady 30 frames a second.

Results:

* **The disc and its code** (`03-executable.md`): SLSP01, build 2350 of
  November 2011, the RVL SDK of August 2010. The disc was already extracted
  by the reverse engineering project
  ([wii-thelaststory-re](https://github.com/vs-sr-dev/wii-thelaststory-re)),
  in the same layout as `wiikit.disc`'s. Stripped; 899 names, of which 54 by
  hand with their evidence. No RSO module is loaded at run time: the
  executable is recompiled alone, 18 382 units, at the first try.
* **The third frame.** The game stopped after three frames: its engine
  paces itself on the GP with a FIFO breakpoint at the end of each frame
  and a draw-sync token after it, and flips the XFB only when the token is
  one past the last. wiikit's GP never stopped at a breakpoint, so the next
  frame's token overtook the one the flip waited for. wiikit now models
  the breakpoint (the GP stops there, what follows is held). Then a second
  stop after 51 frames: the PI wrapped its FIFO 4 bytes into a burst (the
  SDK's FIFO end is base + size - 4), and no burst after the first wrap
  fell on a breakpoint's address again. The PI's pointers are now in
  32-byte units, as on the console.
* **The Remote.** "Communications with the Wii Remote have been
  interrupted": the game learns of controllers only from KPAD's connect
  callback. It plays with the Classic Controller (`tools/tls.cpp`); wiikit
  calls the callbacks for such a game. Two more WPAD functions after New
  Game (`WPADGetInfo`, the Remote's auto-sleep), now in wiikit.
* **It runs**, with a scripted A every few seconds: the strap screen, the
  title, the menu, New Game, Chapter 1 (Reptids' Cave), Zael in the cave
  and the first tutorial, at 30 frames a second throughout (10 060 frames
  in 340 seconds); up to 52 million GX draws, merged into 4.8 million GL
  draws.
* **Played.** The user played into the cave and found two faults, both
  fixed the same session. The bodies were black and see-through: the
  equipment's textures are composed by the GP and compressed to CMPR by the
  CPU from an EFB copy in RAM, which wiikit never wrote (now it does, where
  the port asks: `03-executable.md`). And the game froze a little after the
  player took control: a busy frame filled the FIFO behind the breakpoint,
  and wiikit raised no overflow (now it does). Then: "it plays like a
  dream", the sound clean but for a blink at an autosave.
* **The sound** has gaps while the game loads (the AI interrupt not taken
  for 20-30 ms while the main thread works), none on the title; in game
  the user hears only that blink at an autosave.

wiikit's changes of this session were checked on the six other ports
(`10-wiikit.md`).

## Session 2 — the sound's gaps and the stalls

Goal: the frame rate. A message from a player who had found the port came
first, and with it the sound: the user heard it stutter. The session went
there, and stayed.

Results:

* **The engine's clock** (for later): the effects advance by the frames
  the engine hands them, 1.0 at every frame, never measured time
  (`atnEff_Advance`, `03-executable.md`). The world steps by frames: 60
  frames a second means half a step each, not a lifted cap.
* **The gaps in the tutorial's window**, ten a second: NW4R's AI callback
  enables interrupts once it has had AX mix; wiikit, catching up a late
  block, started the next one right there, inside the callback, which the
  SDK's AI handler then skipped: no frame for that block, and 50 ms of
  waiting for it. wiikit no longer starts a block while the game is in
  `__AIDHandler` (798 gaps in 190 s, then none).
* **A stall inside an interrupt**: the engine moves its FIFO breakpoint in a
  VI callback; the frame held behind it ended there, and wiikit waited for
  the renderer with interrupts off. It now hands such a frame over at the
  next point where interrupts are on.
* **The window behind another**: the sound grated (the user found it).
  Windows 11 throttles a process out of the foreground and may ignore its
  1 ms timer; wiikit now opts out of both.
* **A character coming in** stalled the game and its sound, 80-130 ms
  (the user's guess, "a spawn, an event", was right): its equipment's
  textures are composed by the GP mid-frame, each with a `GXDrawDone`,
  and wiikit's GP, always caught up, waited at the queued frame's
  breakpoint until the flip. The port now lets the CPU go on only once the
  frame ring is empty (`tools/tls.cpp`): 14 frames over 60 ms in two minutes,
  then 2; still 30 frames a second.
* **A lost wake-up in the engine**: its frame wait enables interrupts
  and then sleeps; a frame leaving the ring in between woke no one. Seen as
  a freeze after the third frame under load. The port wakes the ring's
  queue at every retrace.

`TLS_HITCH=1` reports frames over 60 ms and where the threads were. wiikit's
changes (`d9d14c0`) were checked on the seven other ports (`10-wiikit.md`).
Then the user played: "decidedly improved", one dip left of all the small
ones (scene changes still take a frame or two over 60 ms).

## Session 3 — played on, and the first sight of a scene

Goal: an issue on GitHub ("I want to see this going on!") asked for more.
The user played as far as the game went, with `TLS_HITCH=1` logging.

Results:

* **How far it goes**: from the strap screen through the Reptids' cave to
  Zael's mark (the Gathering) and the save after Syrenne's arrow, about a
  quarter of an hour of play, without a fault. The user: "a parte qualche hitch qua e là direi
  ottimo" (some hitches here and there, otherwise excellent).
* **The hitches were links.** Stalls of 100 ms to 2.7 s, where the camera
  turned or a scene came in: the GL programs for what came into view,
  linked when first drawn, 25-210 ms each on the user's driver. In 16
  minutes of play: 183 links, and 80 of the 137 frames over 60 ms had
  one; the two longest were 9 and 28 links in a row. The rest are the
  game's loads, under 150 ms but for seven. They felt worse than in
  session 2 for being new ground, and because the fog (wiikit `cbd441b`)
  made every program new code.
* **The shader list** (wiikit): each program the game draws with is listed
  by the GX registers that shape it (`build/shaderlist.txt`), and at the
  start those the cache lacks are generated again and linked in the
  background, on the driver's own threads. The port ships its list
  (`tools/shaderlist.txt`, `--shader-list`): a first run, or a run after
  a driver update, no longer links where it plays. Boot to the cave, the
  driver's cache defeated (`WIIKIT_SHADERSALT`): 88 links in play and 15
  frames over 60 ms (1.2 s, 1.6 s) without the list; with it, 86 of 88
  linked in the background in 1.4 s, 8 frames over 60 ms, the scene loads
  a run without links has too.
* **A freeze at the third frame** once at boot (the main thread in
  `DVDReadAsync`, taking an IPC interrupt), not seen again in six boots;
  the old binary did it once in October too. `TLS_HITCH` now reports
  the threads again every 2 s while a frame stays late, for the next time.

`WIIKIT_PERF=1` now reports each link over 20 ms. wiikit's change was
checked on the nine other ports (`10-wiikit.md`).
