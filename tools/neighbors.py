"""Find SDK functions in the stripped DOL by their neighbours in a symbolised ELF.

Within one object file the linker keeps the functions in order, so a
function the signatures missed sits at the same distance from a neighbour
they found, as long as the functions between have the same sizes. For each
name asked, every neighbour within --reach functions in the ELF that the
signature pass found once in the DOL predicts an address; the predictions
are counted, and each is checked against the DOL's unit starts and sizes
(build/recomp/symbols.tsv, written by the recompiler).

This only proposes: a name goes into tools/names-manual.tsv with the
evidence that confirms it (its code, its callers, a string).

    python tools/neighbors.py --elf <pc-victorious>/build/extract/files/Oscar_wii_final_versioned.elf \\
        --sig build/sig_elf.tsv KPADRead KPADInit ...
"""
import argparse
import collections
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))  # wiikit/

from wiikit.dol import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("names", nargs="+")
    ap.add_argument("--elf", required=True)
    ap.add_argument("--sig", default=os.path.join(ROOT, "build", "sig_elf.tsv"))
    ap.add_argument("--units", default=os.path.join(ROOT, "build", "recomp", "symbols.tsv"))
    ap.add_argument("--reach", type=int, default=12)
    a = ap.parse_args()

    elf = sorted((f for f in Image(a.elf).functions() if f.size), key=lambda f: f.addr)
    index = {f.name: i for i, f in enumerate(elf)}
    by_name = collections.defaultdict(set)
    with open(a.sig) as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            by_name[p[2]].add(int(p[0], 16))
    found = {n: next(iter(s)) for n, s in by_name.items() if len(s) == 1}
    units = {}
    with open(a.units) as f:
        next(f)
        for line in f:
            p = line.split("\t")
            units[int(p[0], 16)] = (int(p[1]), p[5])

    for name in a.names:
        if name not in index:
            print(f"{name}: not in the ELF")
            continue
        i = index[name]
        t = elf[i]
        votes = collections.Counter()
        who = collections.defaultdict(list)
        for j in range(max(0, i - a.reach), min(len(elf), i + a.reach + 1)):
            if j == i or elf[j].name not in found:
                continue
            pred = found[elf[j].name] + (t.addr - elf[j].addr)
            votes[pred] += 1
            who[pred].append(f"{elf[j].name}{j - i:+d}")
        if not votes:
            print(f"{name} ({t.size:#x}): no neighbour found")
            continue
        out = []
        for pred, n in votes.most_common(3):
            u = units.get(pred)
            mark = f"unit {u[0]:#x} {u[1]}" if u else "NOT A UNIT"
            out.append(f"{pred:08X} x{n} [{mark}] ({', '.join(who[pred][:3])})")
        print(f"{name} ({t.size:#x}): " + " | ".join(out))


if __name__ == "__main__":
    main()
