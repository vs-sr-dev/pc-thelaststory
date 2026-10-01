# This port and wiikit

This port takes [wiikit](https://github.com/vs-sr-dev/wiikit) as a
submodule at `wiikit/`, like the six ports before it.

## What this port used as it is (session 1)

`wiikit.disc`, `dol`, `ppc`, `rso` (to read the `.sel`), discovery and the
recompiler, and the whole runtime: threads, interrupts, IOS, GX and the
renderer, AX, the Classic Controller on SDL gamepads.

## What it gave wiikit (session 1: `ae77320`)

| Change | Layer | Why it is not game knowledge |
|---|---|---|
| **FIFO breakpoints stop the GP**: what the CPU writes past an enabled breakpoint is held, with its FIFO address, until the breakpoint is moved or cleared (or the GP's reading disabled while it moves); the CP's read pointer and read-write distance report what is held | 5 | any game that paces itself on the GP with `GXEnableBreakPt`; before, a breakpoint was reached at once and the GP ran past it, so a draw-sync token written after it arrived before the game had let the GP past the frame |
| the PI's FIFO base, end and write pointer in 32-byte units | 5 | the SDK's FIFO end is base + size - 4: the pipe wrapped 4 bytes into a burst, and every burst after the first wrap was 4 bytes off the addresses the game computes (a breakpoint was never reached) |
| `WPADGetInfo` hooked, `WPADGetInfoAsync` answered for a channel with a controller (full battery, its LED, the extension attached), its callback called at the next delivery | 5 | `WPADGetInfo` sleeps on the channel's control block, which a WPAD never started does not have |
| `WPADSetAutoSleepTime`, `WPADResetAutoSleepTimeCount` hooked as nothing | 5 | the SDKs of 2010 on put an unused Remote to sleep; the reset writes the time into the channel's control block |

Checked on the six other ports before it went in: Victorious self-test
15/15 and to its Auditions episode; Dragon Quest Swords to its Adventure
Logs; Conduit 2, Arc Rise Fantasia and Monster Hunter Tri to their titles;
Mega Man X: Command Mission to its opening scenes: the same screens as
before. Each was bumped to `ae77320` with a local commit.
