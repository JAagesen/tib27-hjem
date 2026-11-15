"""v152 -> v153: ny IHC LED Dimmer 2 kanaler (RS485) til loftslyset i gangen.

Kombidimmeren i gangen ("Kombi dimmer 4 tast", _0x16054, "I det Magiske skab")
skal skiftes til en LK IHC LED Dimmer 2 kanaler — samme type som den i det
frostfri (køkken kanal 1 / hyttehaven kanal 2), men en ny enhed.

Fase 1 (denne fil): den nye dimmer oprettes og får ALT det, kombidimmerens
dimmer-del har. Den gamle bliver stående urørt, så begge reagerer parallelt,
indtil den nye er tilsluttet og den gamle slettes i IHC Visual.

Overført til kanal 1 på den nye dimmer:
  * dimmer-indstillinger: min 5 %, max 100 %, fade op 5000 ms, fade ned
    10000 ms, reguleringstid 10000 ms (load mode findes ikke på LED-dimmeren)
  * alle 14 scenarie-links med samme niveau og rampetid. Hver scene, der
    styrer kombidimmeren, får et ekstra scenarie-link til den nye dimmer:
      - Kombidimmer (dag&Nat): Regulering, Nat, Dag
      - Styring af PIR i gang …: Manuel regulering, Højt/Mellem/Lavt niveau,
        Sluk, Nat nedtoning (1 %), Højt niveau blødt, Sluk hurtigt (1 sek.),
        Sluk straks (soveværelset), Fuldt lys (100 %)
      - Fælles / Sluk Alt
  * Lys niveau  -> "Styring af PIR i gang …" / Input / Lys niveau
  * Lys indikering -> "Kombidimmer (dag&Nat)" / Input / Lys indikering

IKKE overført: kombidimmerens fire tryk. Bevidst — gangen har rigeligt med
andre tryk (Jan, 15-11-2026). De forsvinder, når den gamle slettes.

Kanal 2 oprettes ledig med skabelonens standardindstillinger.
Serienummer er tomt — udfyldes i IHC Visual, når enheden tilsluttes.

Kør:  python ihc/changes/build153.py IND.vis UD.vis
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tib27_ihc import IdAllocator, VisFile  # noqa: E402

N = "\r\n"
OLD = "_0x16054"
SCENES_OLD = "_0x16949"
LINK_TO_LEVEL = "_0x36632c"        # PIR-blok / Input / Lys niveau <- kombidimmer
LINK_TO_IND = "_0x22612c"          # Kombidimmer-blok / Input / Lys indikering <- kombidimmer
CHANNEL_IDS = ("_0x82", "_0x83")   # frostfri-enheden bruger _0x80/_0x81

# typebytes, som de står i den eksisterende LED-dimmer (_0x3d2758)
T = dict(product=0x58, flag=0x0A, channel=0x7B, inc=0x5F, dec=0x60, dim=0x5D, ind=0x1D,
         scenes=0x49, sd=0x4C, sl=0x4B, oc=0x7C, ov=0x7D, oh=0x7E, lf=0x7F, ds=0x6E,
         mn=0x71, mx=0x72, fu=0x6F, fd=0x70, rate=0x73, load=0x74, lfrom=0x2D, lto=0x2C)

ERRORS = [
    ("oc", "overcurrent", "Fejl - Overstrøm", "Kanal udgangen er overbelastet (kortsluttet udgang eller højere belastning end tilladt)"),
    ("ov", "overvoltage", "Fejl - Overspænding", "Der er højere spænding på kanal indgang end acceptabel for  korrekt funktion"),
    ("oh", "overheating", "Fejl - Overophedning", "Dimmerens temperatur overskrider den maksimalt tilladte temperatur (overbelastning, forkert installation)"),
    ("lf", "loadfailure", "Fejl - Belastnings fejl", "Belastning er frakoblet eller ikke i overenstemmelse med specifikationer"),
]


def line_with(t: str, needle: str) -> str:
    i = t.find(needle)
    assert i >= 0 and t.find(needle, i + 1) < 0, needle
    s = t.rfind(N, 0, i) + 2
    return t[s:t.find(N, i) + 2]


def build(src: str, dst: str) -> None:
    v = VisFile.load(src)
    assert v.last_unique_id == 0x8510, f"forventede v152 (_0x8510), fik _0x{v.last_unique_id:x}"
    a = IdAllocator(v)
    nid = lambda k: a.next(T[k])  # noqa: E731
    t = v.text

    # ---- kombidimmerens scener ----------------------------------------------
    s = t.find(f'<scenes id="{SCENES_OLD}"')
    e = t.find("</scenes>", s)
    old_scenes = re.findall(r'<scene_dimmer id="(_0x[0-9a-f]+)"([^>]*?) link="(_0x[0-9a-f]+)"/>', t[s:e])
    assert len(old_scenes) == 14, len(old_scenes)

    # ---- ny dimmer -----------------------------------------------------------
    I = " " * 9
    prod, sync = nid("product"), nid("flag")
    scene_lines, new_links = [], []
    ch_xml = []
    for n, (ch, cid) in enumerate(zip(("_0x0", "_0x1"), CHANNEL_IDS)):
        c = {k: nid(k) for k in ("channel", "inc", "dec", "dim", "ind", "scenes")}
        p = I + "   "
        q = p + "   "
        if n == 0:
            head = (f'{p}<rs485_led_dimmer_channel id="{c["channel"]}" product_identifier="_0x4410" '
                    f'name="LED Dimmer Loftslys gang" icon="_0x86" position="Gang" '
                    f'note="Loftslys i gang. Erstatter Kombi dimmer 4 tast (I det Magiske skab)" '
                    f'power_group="Gang Lys" channel="{ch}" channel_id="{cid}">')
            lf_lvl, lt_lvl, lf_ind, lt_ind = nid("lfrom"), nid("lto"), nid("lfrom"), nid("lto")
            new_links = [(LINK_TO_LEVEL, lt_lvl, lf_lvl), (LINK_TO_IND, lt_ind, lf_ind)]
            dim = (f'{q}<airlink_dimming id="{c["dim"]}" name="Lys niveau" address_channel="_0x1">{N}'
                   f'{q}   <link_from_resource id="{lf_lvl}" name="Følg Link" icon="_0x47" link="{lt_lvl}"/>{N}'
                   f'{q}</airlink_dimming>')
            ind = (f'{q}<light_indication id="{c["ind"]}" name="Lys indikering" note="&apos;On&apos; når lysdæmperen er tændt">{N}'
                   f'{q}   <link_from_resource id="{lf_ind}" name="Følg Link" icon="_0x47" link="{lt_ind}"/>{N}'
                   f'{q}</light_indication>')
            sds = []
            for old_sd, attrs, old_sl in old_scenes:
                sd, sl = nid("sd"), nid("sl")
                sds.append(f'{q}   <scene_dimmer id="{sd}"{attrs} link="{sl}"/>')
                scene_lines.append((old_sd, sd, sl))
            scenes = (f'{q}<scenes id="{c["scenes"]}" name="Scenarier/regulering" scene_resource="{c["dim"]}">{N}'
                      + N.join(sds) + f'{N}{q}</scenes>')
            settings = [("mn", 'value="5" maximum="100"'), ("mx", 'value="100" maximum="100"'),
                        ("fu", 'value="5000" minimum="200" maximum="60000"'),
                        ("fd", 'value="10000" minimum="200" maximum="60000"'),
                        ("rate", 'value="10000" minimum="2000" maximum="10000"')]
        else:
            head = (f'{p}<rs485_led_dimmer_channel id="{c["channel"]}" product_identifier="_0x4410" '
                    f'name="LED Dimmer gang (kanal 2, ledig)" icon="_0x86" channel="{ch}" channel_id="{cid}">')
            dim = f'{q}<airlink_dimming id="{c["dim"]}" name="Lys niveau" address_channel="_0x1"/>'
            ind = f'{q}<light_indication id="{c["ind"]}" name="Lys indikering" note="&apos;On&apos; når lysdæmperen er tændt"/>'
            scenes = f'{q}<scenes id="{c["scenes"]}" name="Scenarier/regulering" scene_resource="{c["dim"]}"/>'
            settings = [("mn", 'value="5" maximum="100"'), ("mx", 'value="100" maximum="100"'),
                        ("fu", 'value="700" minimum="200" maximum="60000"'),
                        ("fd", 'value="700" minimum="200" maximum="60000"'),
                        ("rate", 'value="5000" minimum="2000" maximum="10000"')]
        errs = [f'{q}<rs485_led_dimmer_error_state_{tag} id="{nid(k)}" name="{nm}" icon="_0x36" note="{note}"/>'
                for k, tag, nm, note in ERRORS]
        tagname = dict(mn="minimum_value", mx="maximum_value", fu="fade_rate_up", fd="fade_rate_down", rate="dimming_rate")
        ds = [f'{q}<dimmer_settings id="{nid("ds")}">']
        ds += [f'{q}   <dimmer_setting_{tagname[k]} id="{nid(k)}" {val}/>' for k, val in settings]
        ds += [f'{q}   <dimmer_setting_load_mode id="{nid("load")}"/>', f'{q}</dimmer_settings>']
        ch_xml.append(N.join([head,
            f'{q}<airlink_dimmer_increase id="{c["inc"]}" name="Tænd / Regulér op" address_channel="_0x1"/>',
            f'{q}<airlink_dimmer_decrease id="{c["dec"]}" name="Sluk / Regulér ned" address_channel="_0x1"/>',
            dim, ind, scenes, *errs, *ds, f'{p}</rs485_led_dimmer_channel>']))

    product = N.join([
        f'{I}<product_rs485_led_dimmer id="{prod}" product_identifier="_0x4409" name="IHC LED Dimmer 2 kanaler" '
        f'locked="yes" position="Gang" icon="_0x86" note="LK IHC RS485 produkter. Erstatter Kombi dimmer 4 tast i gangen" serialnumber="">',
        f'{I}   <resource_flag id="{sync}" name="Kanal synkronisering" icon="_0x33"/>',
        *ch_xml, f'{I}</product_rs485_led_dimmer>']) + N

    # indsæt lige efter kombidimmeren
    s = t.find(f'<product_airlink id="{OLD}"')
    e = t.find("</product_airlink>", s)
    e = t.find(N, e) + 2
    v.replace_once(t[s - 9:e], t[s - 9:e] + product)

    # ---- et ekstra scenarie-link i hver scene --------------------------------
    for old_sd, sd, sl in scene_lines:
        t = v.text
        m = re.search(rf'[ ]*<scene_link id="_0x[0-9a-f]+" name="Scenarie link" icon="_0x47" link="{old_sd}"/>\r\n', t)
        assert m and len(re.findall(rf'link="{old_sd}"', t)) == 1, old_sd
        ln = m.group(0)
        ind_ = ln[:len(ln) - len(ln.lstrip())]
        v.replace_once(ln, ln + f'{ind_}<scene_link id="{sl}" name="Scenarie link" icon="_0x47" link="{sd}"/>{N}')

    # ---- lys niveau og lys indikering -----------------------------------------
    for existing, lt, lf in new_links:
        ln = line_with(v.text, f'<link_to_resource id="{existing}"')
        ind_ = ln[:len(ln) - len(ln.lstrip())]
        v.replace_once(ln, ln + f'{ind_}<link_to_resource id="{lt}" name="Følg Link" icon="_0x4a" link="{lf}"/>{N}')

    a.commit()
    v.save(dst)
    print(f"skrevet {dst}  last_unique_id=_0x{v.last_unique_id:x}  (+{a.counter - 0x8510} id'er)")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
