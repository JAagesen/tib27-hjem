"""v159 -> v160: Nat og Nat nedtoning i gangen 10 % -> 5 % (Jan, 17-11-2026).

Kør:  python ihc/changes/build160.py IND.vis UD.vis
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tib27_ihc import VisFile  # noqa: E402

SCENES = ("_0x851d4c", "_0x852f4c")   # Nat (Kombidimmer-blokken), Nat nedtoning (PIR-styringen)


def build(src: str, dst: str) -> None:
    v = VisFile.load(src)
    for id_ in SCENES:
        t = v.text
        i = t.find(f'id="{id_}"')
        s, e = t.rfind("<", 0, i), t.find(">", i) + 1
        el = t[s:e]
        assert 'dimming_value="10"' in el, el
        v.replace_once(el, re.sub(r'\bdimming_value="10"', 'dimming_value="5"', el))
    v.save(dst)
    print(f"skrevet {dst}: Nat og Nat nedtoning 10 % -> 5 %")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
