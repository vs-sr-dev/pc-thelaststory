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

Then, the same session, after the user played it (`cf9adb9`; `3166862` names this port in wiikit's README):

| Change | Layer | Why it is not game knowledge |
|---|---|---|
| **an EFB copy into RAM on request** (`gx_copy_to_ram`): the renderer reads its copy back at the copy's native size, in the queue's order, and the runtime encodes it in the copy's texture format (I4, I8, IA4, IA8, RGB565, RGB5A3, RGBA8 in GX's tiles); `hw_run_locked` takes any callable | 5 | a game that reads an EFB copy on the CPU (to compress it, to save it); the port says where, as copying every copy back would stall the GPU every frame |
| **the CP's overflow and underflow**: the status register and the CP interrupt from what is held against the FIFO's watermarks (CP 0x28-0x2E) | 5 | with the GP held at a breakpoint, a frame larger than the FIFO filled it and the CPU wrote on round it; the SDK suspends the writer at the overflow and resumes it at the underflow |

Each was checked on the six other ports before it went in: Victorious
self-test 15/15 and to its Auditions episode; Dragon Quest Swords to its
Adventure Logs; Conduit 2, Arc Rise Fantasia and Monster Hunter Tri to their
titles; Mega Man X: Command Mission to its opening scenes: the same screens
as before. Each port was bumped to it.

## What it gave wiikit (session 2: `d9d14c0`)

| Change | Layer | Why it is not game knowledge |
|---|---|---|
| **no AI block while the game is in its AI interrupt**: `__AIDHandler` hooked (where the executable names it); a late block waits for it to return, and starts no sooner than half a block after the game took the last one's interrupt; the 50 ms a block may wait for its frame count from when it began to wait | 5 | NW4R's AI callback enables interrupts once it has had AX mix; a block started there is taken inside it, the SDK's handler skips the callback while it runs, and the block has no frame: a gap of 50 ms, ten a second where frames came late |
| **no wait for the renderer with interrupts off**: the record is kept and handed over at the next point where they are on (`ppc_poll`); a read-back still waits | 5 | a game that moves its FIFO breakpoint in a VI callback ends the held frame inside the handler; the wait there took no interrupt, the AI's included |
| **out of Windows' power throttling** (`SetProcessInformation`: execution speed, timer resolution) | 5 | out of the foreground Windows 11 may slow the process and ignore its 1 ms timer: the waits that take interrupts every millisecond took them every 15.6 ms, and the sound grated |
| `WIIKIT_AUDIODBG` reports every guest thread, the parked ones too (as `--watch` does) | 5 | where a block's frame was held up |

Checked on the seven other ports, old binaries against new, the sound on:
Victorious to its Auditions episode, Dragon Quest Swords to its Adventure
Logs, Conduit 2, Arc Rise Fantasia and Crystal Bearers to their titles,
Mega Man X: Command Mission to its opening scenes, Monster Hunter Tri
through its opening movie: the same screens; blocks without their frame 29
before, 4 after. Each port was bumped to it.

The rest of session 2 is the port's own (`tools/tls.cpp`): the engine's
frame wait to an empty ring, and the ring's queue woken at every retrace
(`03-executable.md`).
