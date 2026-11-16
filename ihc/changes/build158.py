"""v157 -> v158: højt niveau i gangen 35 % -> 55 %.

35 % er for svagt på LED-lampen. Alle scener på gangens LED-dimmer, der stod
på 35 %, hæves til 55 % (Jan, 16-11-2026). Rampetider uændrede.
  Højt niveau, Højt niveau blødt, Manuel regulering (PIR-styringen),
  Dag og Regulering (Kombidimmer-blokken).

Kør:  python ihc/changes/build158.py IND.vis UD.vis
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tib27_ihc import VisFile  # noqa: E402

CHANNEL = "LED Dimmer Loftslys gang"


def build(src: str, dst: str) -> None:
    v = VisFile.load(src)
    ch = [c for c in v.root.iter("rs485_led_dimmer_channel") if c.get("name") == CHANNEL][0]
    ids = [sd.get("id") for sd in ch.find("scenes").findall("scene_dimmer") if sd.get("dimming_value") == "35"]
    assert len(ids) == 5, ids
    for id_ in ids:
        t = v.text
        i = t.find(f'id="{id_}"')
        s, e = t.rfind("<", 0, i), t.find(">", i) + 1
        el = t[s:e]
        v.replace_once(el, re.sub(r'\bdimming_value="35"', 'dimming_value="55"', el))
    v.save(dst)
    print(f"skrevet {dst}: {len(ids)} scener 35 % -> 55 %")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
