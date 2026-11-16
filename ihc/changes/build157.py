"""v156 -> v157: synligt natlys på gangens LED-dimmer.

LED-dimmeren bruger ikke minimumsværdien som gulv for scenerne: en scene på
1 % giver 1 %, og ved det niveau lyser LED'erne ikke (de lyser fra ca. 10 %,
testet af Jan 16-11-2026). Derfor hæves selve scenerne på kanal 1:
  * Nat, Sluk Alt, Lavt niveau, Nat nedtoning: 1 % -> 10 %
  * Mellem Niveau: 10 % -> 20 %, så lav/mellem/høj stadig er tre trin
PIR-blokkens statuskontrol behandler natlys som "slukket" (niveau < 5 og > 4).
Tærsklerne flyttes til < 11 og > 10, så 10 % natlys behandles som før 1 %.
Rampetider og alle andre scener er uændrede. Gælder kun den nye dimmer.

Kør:  python ihc/changes/build157.py IND.vis UD.vis
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tib27_ihc import VisFile  # noqa: E402

SCENES = {"_0x851d4c": ("1", "10"), "_0x85234c": ("1", "10"), "_0x85294c": ("1", "10"),
          "_0x852f4c": ("1", "10"), "_0x852d4c": ("10", "20")}
THRESHOLDS = {"_0x35c413": ("4", "10"), "_0x35cf13": ("5", "11")}


def set_attr(v: VisFile, id_: str, attr: str, old: str, new: str) -> None:
    t = v.text
    i = t.find(f'id="{id_}"')
    assert i >= 0 and t.find(f'id="{id_}"', i + 1) < 0, id_
    s, e = t.rfind("<", 0, i), t.find(">", i) + 1
    el = t[s:e]
    assert re.search(rf'\b{attr}="{old}"', el), (id_, el)
    v.replace_once(el, re.sub(rf'\b{attr}="{old}"', f'{attr}="{new}"', el))


def build(src: str, dst: str) -> None:
    v = VisFile.load(src)
    for id_, (o, n) in SCENES.items():
        set_attr(v, id_, "dimming_value", o, n)
    for id_, (o, n) in THRESHOLDS.items():
        set_attr(v, id_, "inivalue", o, n)
    v.save(dst)
    print(f"skrevet {dst}: {len(SCENES)} scener og {len(THRESHOLDS)} tærskler ændret")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
