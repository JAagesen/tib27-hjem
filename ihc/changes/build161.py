"""v160 (dump fra controlleren) -> v161: hurtigt natlys i gangen.

Om natten tænder PIR'en med scenen "Lavt niveau" (5 %). Med 5000 ms rampe
er lampen mørk det meste af vejen, fordi LED'erne først lyser omkring 4-5 %,
så natlyset føles flere sekunder forsinket (Jan, 17-11-2026).
Rampen på Lavt niveau sættes til 500 ms. Alt andet uændret.

Kør:  python ihc/changes/build161.py IND.vis UD.vis
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
    assert 'ramptime_ms="5000"' in el and 'dimming_value="5"' in el, el
    v.replace_once(el, re.sub(r'\bramptime_ms="5000"', 'ramptime_ms="500"', el))
    v.save(dst)
    print(f"skrevet {dst}: Lavt niveau rampe 5000 -> 500 ms")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
