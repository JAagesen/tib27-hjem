"""Compare two versions of a project and list what changed, region by region.

Used to prove that an edit touched only what it was meant to touch.
"""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass

from .vis import VisFile

_ID_ATTR = re.compile(r'\bid="(_0x[0-9a-fA-F]+)"')


@dataclass
class Region:
    kind: str           # insert | delete | replace
    old_lines: tuple[int, int]
    new_lines: tuple[int, int]
    ids: list[str]
    sample: list[str]


def diff(old: VisFile, new: VisFile, context: int = 0) -> list[Region]:
    a = old.text.split("\r\n")
    b = new.text.split("\r\n")
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    regions: list[Region] = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        changed = b[j1:j2] if op != "delete" else a[i1:i2]
        ids: list[str] = []
        for line in changed:
            ids.extend(_ID_ATTR.findall(line))
        regions.append(Region(op, (i1 + 1, i2), (j1 + 1, j2), ids,
                              [l.strip()[:140] for l in changed[:4]]))
    return regions


def describe(new: VisFile, regions: list[Region]) -> str:
    out = [f"{len(regions)} ændrede områder"]
    for n, r in enumerate(regions, 1):
        out.append(f"\n[{n}] {r.kind}: gammel linje {r.old_lines[0]}–{r.old_lines[1]}, "
                   f"ny linje {r.new_lines[0]}–{r.new_lines[1]}")
        for i in r.ids[:8]:
            e = new.get(i)
            out.append(f"    {i}  {e.tag if e is not None else '(slettet)'}"
                       + (f" «{e.get('name')}»" if e is not None and e.get("name") else ""))
        if len(r.ids) > 8:
            out.append(f"    … og {len(r.ids) - 8} mere")
        if not r.ids:
            out.extend(f"    | {s}" for s in r.sample)
    return "\n".join(out)
