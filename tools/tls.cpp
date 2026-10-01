// The Last Story — the port's own layer over the wiikit runtime.
//
// Linked into wiiboot by tls.cmake; the functions it replaces are listed in
// tls-hooks.txt, which the recompiler takes with --hooks. What belongs here
// is what only this game needs.
#include "rt.h"
#include <cstdlib>

namespace {

// TLS_GFXTRACE=1: the engine's frame ring (atn_graphics_device.cpp) traced.
constexpr uint32_t kRing = 0x807C6F68;                 // 5 x {FIFO wptr, 0, XFB, token}, +0x50 write, +0x52 read
PPCFunc o_swap, o_bp, o_pre, o_post;
uint32_t traced = 0;

void ring(const char* what, PPCContext& c) {
    if (traced > 20000) return;
    traced++;
    uint32_t gd = ld32(c.r[13] - 0x67E0);
    rt_log("gfx: %-5s r3 %08X  ring w %u r %u  flags bp %u flip %u act %u  tok %u  xfb 78 %08X 7c %08X",
           what, c.r[3], ld16(kRing + 0x50), ld16(kRing + 0x52), ld8(c.r[13] - 0x67E7), ld8(c.r[13] - 0x67E6),
           ld8(c.r[13] - 0x67E8), ld16(c.r[13] - 0x67E4), gd ? ld32(gd + 0x78) : 0, gd ? ld32(gd + 0x7C) : 0);
}

// The equipment's textures (the bodies') are made at load time: the GP
// composes them (atn::TextureComposite), GXCopyTex puts them in RAM as
// RGBA8, and the CPU turns that copy's tiles into rows in place
// (atnTex_Unswizzle), merges an alpha mask and compresses it to CMPR
// (atnTex_CompressCopy). wiikit keeps EFB copies on the host GPU: the copy's
// bytes are written into RAM before the game first reads them, or the
// bodies come out black. (The mask is a texture from the disc: no copy.)
PPCFunc o_unswizzle;
void unswizzle(PPCContext& c) {                       // (data, format, w, h)
    gx_copy_to_ram(c.r[3] & 0x3FFFFFFF);
    o_unswizzle(c);
}

void install() {
    o_unswizzle = ppc_hook("atnTex_Unswizzle", unswizzle);
    // The game plays with the Classic Controller (or the Remote and Nunchuk,
    // which wiikit has no Nunchuk for); it learns of controllers from KPAD's
    // connect callback, which wiikit calls for a game of the Classic.
    wpad_set_classic(true);
    if (!std::getenv("TLS_GFXTRACE")) return;
    o_swap = ppc_hook("atnGfx_SwapFrame", [](PPCContext& c) { ring("swap", c); o_swap(c); ring("swap>", c); });
    o_bp = ppc_hook("atnGfx_BreakPtCallback", [](PPCContext& c) { ring("bp", c); o_bp(c); ring("bp>", c); });
    o_pre = ppc_hook("atnGfx_PreRetrace", [](PPCContext& c) { ring("pre", c); o_pre(c); });
    o_post = ppc_hook("atnGfx_PostRetrace", [](PPCContext& c) { ring("post", c); o_post(c); });
}

RtGameLayer layer("The Last Story", install);

}  // namespace
