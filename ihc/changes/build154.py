"""v153 -> v154: kombidimmeren i gangen sat ud af drift, men ikke slettet.

Den nye LED-dimmer (v153) har overtaget alle scenarier og links. Her fjernes
alle kombidimmerens forbindelser, så den ikke gør noget:
  * de 14 scenarie-links (begge ender: scene_dimmer i produktet og
    scene_link i scenerne)
  * Lys niveau -> PIR-styringen, Lys indikering -> Kombidimmer-blokken
  * de fire tryk -> Kombidimmer-blokken (op/ned) og PIR-styringen (DAG/NAT)
Produktet, dets indstillinger og serienummer bliver stående, og noten
markerer det som ude af drift. Det kan slettes i IHC Visual senere.

Kør:  python ihc/changes/build154.py IND.vis UD.vis
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tib27_ihc import VisFile  # noqa: E402

N = "\r\n"
OLD = "_0x16054"


def drop_line(v: VisFile, needle: str) -> None:
    t = v.text
    i = t.find(needle)
    assert i >= 0 and t.find(needle, i + 1) < 0, needle
    s = t.rfind(N, 0, i) + 2
    v.replace_once(t[s:t.find(N, i) + 2], "")


def build(src: str, dst: str) -> None:
    v = VisFile.load(src)
    assert v.last_unique_id == 0x8554, f"forventede v153 (_0x8554), fik _0x{v.last_unique_id:x}"
    t = v.text
    s = t.find(f'<product_airlink id="{OLD}"')
    e = t.find("</product_airlink>", s)
    block = t[s:e]

    links = re.findall(r'<link_from_resource id="(_0x[0-9a-f]+)" [^>]*link="(_0x[0-9a-f]+)"/>', block)
    scenes = re.findall(r'<scene_dimmer id="(_0x[0-9a-f]+)"[^>]*link="(_0x[0-9a-f]+)"/>', block)
    assert len(links) == 6 and len(scenes) == 14, (len(links), len(scenes))

    for lf, lt in links:
        drop_line(v, f'<link_from_resource id="{lf}"')
        drop_line(v, f'<link_to_resource id="{lt}"')
    for sd, sl in scenes:
        drop_line(v, f'<scene_dimmer id="{sd}"')
        drop_line(v, f'<scene_link id="{sl}"')

    v.replace_once('note="Styring af Loftslys i gang" power_group="Gang Lys">',
                   'note="UDE AF DRIFT 16-11-2026: erstattet af IHC LED Dimmer 2 kanaler '
                   '(LED Dimmer Loftslys gang). Ingen links. Kan slettes." power_group="Gang Lys">')
    v.save(dst)
    print(f"skrevet {dst}: {len(links)} link-par og {len(scenes)} scenarie-par fjernet")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
