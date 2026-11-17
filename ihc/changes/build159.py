"""v158 -> v159: lavt niveau i gangen 10 % -> 5 % (Jan, 17-11-2026).

Kun scenen "Lavt niveau" (PIR-styringen) på gangens LED-dimmer. Nat, Nat
nedtoning og Sluk Alt bliver på 10 %.

Kør:  python ihc/changes/build159.py IND.vis UD.vis
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tib27_ihc import VisFile  # noqa: E402

LAVT = "_0x85294c"


def build(src: str, dst: str) -> None:
    v = VisFile.load(src)
    t = v.text
    i = t.find(f'id="{LAVT}"')
    s, e = t.rfind("<", 0, i), t.find(">", i) + 1
    el = t[s:e]
    assert 'dimming_value="10"' in el, el
    v.replace_once(el, re.sub(r'\bdimming_value="10"', 'dimming_value="5"', el))
    v.save(dst)
    print(f"skrevet {dst}: Lavt niveau 10 % -> 5 %")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
