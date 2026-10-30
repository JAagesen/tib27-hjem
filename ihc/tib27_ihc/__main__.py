"""Command line: ``python -m tib27_ihc <verify|dump|diff|blocks> ...``"""
from __future__ import annotations

import argparse
import sys

from .diff import describe, diff
from .dump import dump_block
from .verify import ERROR, WARN, summary, verify
from .vis import VisFile


def cmd_verify(a: argparse.Namespace) -> int:
    vis = VisFile.load(a.file)
    findings = verify(vis)
    try:
        s = summary(vis)
        print("  ".join(f"{k}={('_0x%x' % v) if k == 'last_unique_id' else v}" for k, v in s.items()))
    except Exception:  # unparsable file: findings say why
        pass
    for f in findings:
        print(f)
    errors = sum(f.level == ERROR for f in findings)
    warns = sum(f.level == WARN for f in findings)
    print(f"\n{'IKKE KLAR' if errors else 'KLAR'} til upload: {errors} fejl, {warns} advarsler")
    return 1 if errors else 0


def cmd_dump(a: argparse.Namespace) -> int:
    print(dump_block(VisFile.load(a.file), a.block))
    return 0


def cmd_diff(a: argparse.Namespace) -> int:
    old, new = VisFile.load(a.old), VisFile.load(a.new)
    print(describe(new, diff(old, new)))
    return 0


def cmd_blocks(a: argparse.Namespace) -> int:
    vis = VisFile.load(a.file)
    for fb in vis.root.iter("functionblock"):
        name = fb.get("name", "")
        if a.grep and a.grep.lower() not in name.lower():
            continue
        print(f"{fb.get('id'):12} {name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="tib27-ihc", description="Værktøjer til IHC Visual .vis-filer")
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verify", help="tjek en fil før upload")
    v.add_argument("file")
    v.set_defaults(fn=cmd_verify)
    d = sub.add_parser("dump", help="vis en funktionsblok som tekst")
    d.add_argument("file")
    d.add_argument("block", help="navn eller id på funktionsblokken")
    d.set_defaults(fn=cmd_dump)
    df = sub.add_parser("diff", help="hvad er ændret mellem to versioner")
    df.add_argument("old")
    df.add_argument("new")
    df.set_defaults(fn=cmd_diff)
    b = sub.add_parser("blocks", help="list funktionsblokke")
    b.add_argument("file")
    b.add_argument("--grep", default="")
    b.set_defaults(fn=cmd_blocks)
    a = p.parse_args(argv)
    try:
        return a.fn(a)
    except (KeyError, ValueError, FileNotFoundError) as exc:
        print(f"fejl: {exc.args[0] if exc.args else exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
