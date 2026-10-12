# pc-thelaststory

Toward a native PC port of **The Last Story** (Wii, Mistwalker / AQ
Interactive, 2011; Europe 2012, North America 2012). The game was never
re-released: no remaster, no digital release. The goal is the game running
natively on PC, at a frame rate the Wii never held steady.

The route is static recompilation: the game's own PowerPC code, translated
to C++ and built for the PC, running on a replacement for the Wii's
hardware and system software. Nothing is emulated at the instruction
level, and nothing of the game is rewritten.

This repository documents the port and holds its own tools and layer. It is
the seventh port built on **[wiikit](https://github.com/vs-sr-dev/wiikit)**,
the game-agnostic Wii toolkit, taken here as a submodule at `wiikit/`. Where
this game needs something every Wii game would need, it goes into wiikit,
not here. The game's formats were reverse engineered earlier, in
[wii-thelaststory-re](https://github.com/vs-sr-dev/wii-thelaststory-re).

## Where it stands

After two sessions the game **boots and plays into its first chapter**:
the strap screen, the title, the menu, New Game, Chapter 1 (Reptids'
Cave), Zael in the cave and the first tutorial, at 16:9 and a steady 30
frames a second, with the Classic Controller (a gamepad), played by hand
through the first cave. Session 2 cleared the sound's gaps and the stalls
when characters come in. Fog is not drawn yet; 60 frames a second is
next. See [docs/00-sessions.md](docs/00-sessions.md) and the plan in
[docs/07-next-session.md](docs/07-next-session.md).

## BYOA — Bring Your Own Assets

This repository contains **documentation and tools only**. No game data, no
executables, no assets. You need your own original disc. The work is done on
the European release, SLSP01; the addresses in `tools/` and `docs/` are that
executable's.

## Layout

    docs/     the executable, the plan, the session log
    tools/    The Last Story-specific tools, the port's layer (tls.cpp)
    wiikit/   game-agnostic Wii toolkit (submodule: github.com/vs-sr-dev/wiikit)
    build/    (not in git) the disc, everything derived from it, the build

## Building

As for the other wiikit ports: Python 3.8+, CMake, Ninja, clang (MSYS2) and
SDL3; OpenGL 4.5 to run. From the root:

```sh
python -m wiikit.disc GAME.iso --extract build/extract
python tools/sigmatch.py build/extract/sys/main.dol --dsy <Dolphin>/Sys/totaldb.dsy \
    --out build/sig_guess.tsv
python tools/names.py build/extract/sys/main.dol          # -> build/names.tsv
python -m wiikit.recomp build/extract/sys/main.dol --out build/recomp \
    --symbols build/names.tsv --hooks tools/tls-hooks.txt
cmake -S build/recomp -B build/recomp-build -G Ninja -DCMAKE_CXX_COMPILER=clang++ \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS_RELEASE=-O1 -DWIIKIT_EXTRA=$PWD/tools/tls.cmake
ninja -C build/recomp-build
cd build/run1 && ../recomp-build/wiiboot ../extract --symbols ../recomp/symbols.tsv
```

`build/fonts` holds the boot ROM's fonts and `dsp_coef.bin` (Dolphin's
`Sys/GC` has free ones). The names need only Dolphin's `totaldb.dsy` (in
every Dolphin install's `Sys` folder) and `tools/names-manual.tsv`, every
function the runtime hooks that the database misses, each with its
evidence. `tools/look.py` is `wiikit.ppc` on the stripped DOL.

## Documentation

    00-sessions.md            progress log
    03-executable.md          the stripped DOL, its names, the engine's frame pacing
    07-next-session.md        the plan for the next session
    10-wiikit.md              how this port uses and grows wiikit

Playing: wiikit's Classic Controller mapping (the pad's buttons by
position; `build/keys.txt` for the keyboard). F11 fullscreen, F12 a GX
trace.

## Licence

MIT. This covers the documentation and tools in this repository only. It
says nothing about The Last Story, which remains the property of its rights
holders.
