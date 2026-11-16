"""v155 -> v156: minimum 10 % på gangens LED-dimmer (kanal 1).

Med minimum 5 % lyser LED'erne ikke på de lave scener (1 %): PIR i natdrift,
Nat, Lavt niveau, Nat nedtoning og Sluk Alt gav slukket lys. Ved 10 % lyser
de (testet af Jan 16-11-2026). Kombidimmeren klarede 5 %, LED-dimmeren ikke.

Kør:  python ihc/changes/build156.py IND.vis UD.vis
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tib27_ihc import VisFile  # noqa: E402

CHANNEL = "LED Dimmer Loftslys gang"


def build(src: str, dst: str) -> None:
    v = VisFile.load(src)
    ch = [c for c in v.root.iter("rs485_led_dimmer_channel") if c.get("name") == CHANNEL]
    assert len(ch) == 1
    mn = ch[0].find("dimmer_settings/dimmer_setting_minimum_value")
    assert mn.get("value") == "5", mn.get("value")
    t = v.text
    i = t.find(f'id="{mn.get("id")}"')
    s, e = t.rfind("<", 0, i), t.find(">", i) + 1
    old = t[s:e]
    v.replace_once(old, old.replace('value="5"', 'value="10"'))
    v.save(dst)
    print(f"skrevet {dst}: minimum 5 % -> 10 % på {CHANNEL}")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
