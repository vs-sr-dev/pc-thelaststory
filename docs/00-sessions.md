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
* **The sound** has gaps while the game loads (the AI interrupt not taken
  for 20-30 ms while the main thread works), none on the title. Not yet
  listened to in game.

wiikit's changes of this session were checked on the six other ports
(`10-wiikit.md`).
