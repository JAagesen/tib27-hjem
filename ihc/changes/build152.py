"""v151 -> v152: ganglyset slukket fra soveværelset.

Problem (1-11-2026):
  1. Slukkes gangen fra soveværelset, tænder den nogle gange igen af sig selv.
     Kort tryk på NAT spærrer PIR'en i 45 s. Når spærringen udløber, kører
     "PIR aktiveres" igen, og står PIR'en stadig på ON fra da man gik gennem
     gangen, tænder lyset.
  2. Om dagen slukker NAT-tasten med scenen "Sluk" (10 s rampe).

Rettelse — kun for de to NAT-taster i soveværelset (Mivs og Nalles 6-tast):
  * Ny indgang "Tryk NAT soveværelse"; de to soveværelses-links flyttes hertil.
    Gangens og hoveddørens NAT-taster er uændrede.
  * Tryk og hold deler tryktimer med de andre NAT-taster (samme regulering ned).
  * Kort tryk slukker med ny scene "Sluk straks (soveværelset)", 0 %, 200 ms —
    både lyst og mørkt. Natdrift sættes stadig, når det er mørkt.
  * Nyt flag "Vent på ny bevægelse": sættes ved sluk fra soveværelset, hvis PIR
    står på ON. "PIR aktiveres" kræver flaget OFF; flaget ryddes først når PIR
    går til OFF. En PIR der blot hænger fra turen gennem gangen kan derfor ikke
    tænde lyset igen — en ny bevægelse kan.

Kør:  python ihc/changes/build152.py IND.vis UD.vis
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tib27_ihc import IdAllocator, VisFile  # noqa: E402

N = "\r\n"

# Kendte id'er i v151
FB_PIR = "_0x32a528"
IN_TRYK_NAT = "_0x822611"
LINKS_SOVEVAERELSE = ("_0x822a2c", "_0x822c2c")       # Miv, Nalle (nederst højre)
T_TRYKTID_NAT = "_0x836310"
PIR = "_0x32ca11"
SKUMRING = "_0x32cb11"
NATDRIFT = "_0x32c911"
AFVENTER_NAT = "_0x82280a"
FLAG_MANUEL = "_0x32e80a"
T_SPAERRING_MANUEL = "_0x32de10"
T_EFTERLOEB = "_0x32d210"
TT_EFTERLOEB_DAG = "_0x32da17"
E_DAEMPER_STATUS = "_0x32d10f"
TYPEDEF_DAEMPER = "_0x2eec47"
V_SLUKKET = "_0x2eee48"
SC_MANUEL_REG = "_0x83604a"
SCENES_GANG = "_0x16949"


def build(src: str, dst: str) -> None:
    v = VisFile.load(src)
    assert v.last_unique_id == 0x84E3, f"forventede v151 (_0x84e3), fik _0x{v.last_unique_id:x}"
    a = IdAllocator(v)
    t = v.text

    # ---- 1. Ny indgang, og flyt soveværelsets to links over på den ----------
    in_sov = a.next("input")
    moved = []
    for lid in LINKS_SOVEVAERELSE:
        s = t.find(f'<link_to_resource id="{lid}"')
        s = t.rfind(N, 0, s) + 2
        e = t.find(N, s) + 2
        moved.append(t[s:e])
    for line in moved:
        v.replace_once(line, "")
    t = v.text
    i = t.find(f'<resource_input id="{IN_TRYK_NAT}"')
    end = t.find("</resource_input>", i) + len("</resource_input>") + 2   # + CRLF
    ind = " " * 15
    new_input = (f'{ind}<resource_input id="{in_sov}" name="Tryk NAT soveværelse" icon="_0x36" '
                 f'note="NAT-tasterne i soveværelset. Slukker gangen straks og venter på ny '
                 f'bevægelse, før PIR&apos;en må tænde igen.">{N}'
                 + "".join(moved) +
                 f"{ind}</resource_input>{N}")
    v.replace_once(t[i - 15:end], t[i - 15:end] + new_input)

    # ---- 2. Ny scene: Sluk straks ------------------------------------------
    sc, sl, sd = a.next("resource_scene"), a.next("scene_link"), a.next("scene_dimmer")
    anchor = '<resource_scene id="_0x84784a"'
    t = v.text
    s = t.rfind(N, 0, t.find(anchor)) + 2
    e = t.find("</resource_scene>", s) + len("</resource_scene>") + 2
    old = t[s:e]
    v.replace_once(old, old +
        f'{ind}<resource_scene id="{sc}" name="Sluk straks (soveværelset)" note="Som &quot;Sluk&quot;, '
        f'men næsten uden rampe (200 ms). Bruges kun af NAT-tasterne i soveværelset." hide_dialog="yes">{N}'
        f'{ind}   <scene_link id="{sl}" name="Scenarie link" icon="_0x47" link="{sd}"/>{N}'
        f'{ind}</resource_scene>{N}')
    dimmer_line = '                  <scene_dimmer id="_0x847a4c" name="Scenarie link" dimming_value="0" ramptime_ms="1000" link="_0x84794b"/>' + N
    v.replace_once(dimmer_line, dimmer_line +
        f'                  <scene_dimmer id="{sd}" name="Scenarie link" dimming_value="0" ramptime_ms="200" link="{sl}"/>{N}')

    # ---- 3. Nyt flag --------------------------------------------------------
    fl = a.next("flag")
    flag_anchor = v.text[v.text.rfind(N, 0, v.text.find('<resource_flag id="_0x848c0a"')) + 2:]
    flag_anchor = flag_anchor[:flag_anchor.find(N) + 2]
    v.replace_once(flag_anchor, flag_anchor +
        f'{ind}<resource_flag id="{fl}" name="Vent på ny bevægelse" icon="_0x33" note="Sat når gangen '
        f'slukkes fra soveværelset mens PIR står på ON. PIR&apos;en må ikke tænde lyset før den har været '
        f'OFF og ser ny bevægelse."/>{N}')

    # ---- 4. PIR aktiveres kræver flaget OFF ---------------------------------
    c = a.next("condition")
    last_cond = ('                           <condition id="_0x349dc9" name="%P = OFF" icon="_0x1a" '
                 'note="Betingelse at %P er OFF" link1="_0x32c711" method="_0x14"/>' + N)
    v.replace_once(last_cond, last_cond +
        f'                           <condition id="{c}" name="%P = OFF" icon="_0x1a" note="Ikke hvis '
        f'gangen er slukket fra soveværelset og PIR&apos;en endnu ikke har været i ro" link1="{fl}" method="_0x14"/>{N}')

    # ---- 5. Tryk-programmet starter også tryktiden for soveværelset ---------
    ev = a.next("event")
    ev_line = ('                        <event id="_0x8377c8" name="%P -&gt; ON" icon="_0xc" '
               'note="Starter program" link1="_0x822611" method="_0xa"/>' + N)
    v.replace_once(ev_line, ev_line +
        f'                        <event id="{ev}" name="%P -&gt; ON" icon="_0xc" note="NAT-tast i soveværelset" '
        f'link1="{in_sov}" method="_0xa"/>{N}')

    # ---- 6. Nye programmer ---------------------------------------------------
    P = "                  "     # program_simple indent (som "Tryk NAT slippes")
    ids = {k: a.next(tp) for k, tp in [
        ("p", "program_simple"), ("evs", "events"), ("ev", "event"), ("acts", "actions"),
        ("sub", "program_sub"), ("sc", "conditions"), ("scc", "condition"), ("tmr", "timer"),
        ("sa", "actions"),
        ("dsub", "program_sub"), ("dc", "conditions"), ("dcc", "condition"), ("da", "actions"),
        ("a_nat", "action"), ("a_afv", "action"), ("a_slk1", "action"), ("df", "actions"), ("a_slk2", "action"),
        ("psub", "program_sub"), ("pc", "conditions"), ("pcc", "condition"), ("pa", "actions"), ("a_flag", "action"),
        ("a_man", "action"), ("a_sp", "action"), ("a_ef", "action"), ("a_st", "action"), ("en", "enum"),
        ("fa", "actions"), ("a_stop", "action"), ("a_ef2", "action"), ("a_ef3", "action"),
        ("a_tt", "action"),
        ("q", "program_simple"), ("qevs", "events"), ("qev", "event"), ("qacts", "actions"), ("q_a", "action"),
    ]}
    I = ids
    release = f"""{P}<program_simple id="{I['p']}" name="Tryk NAT soveværelse slippes" icon="_0x7" note="Kort tryk i soveværelset slukker gangen straks. Står PIR&apos;en stadig på ON, venter den på ny bevægelse, før den må tænde igen. Langt tryk stopper blot reguleringen.">
{P}   <events id="{I['evs']}" name="Hændelser" icon="_0xb" note="Hændelser som starter program">
{P}      <event id="{I['ev']}" name="%P -&gt; OFF" icon="_0xc" note="Starter program" link1="{in_sov}" method="_0x14"/>
{P}   </events>
{P}   <actions id="{I['acts']}" name="Kommandoer" icon="_0x8" note="Kommandoer" type="_0x2">
{P}      <program_sub id="{I['sub']}" name="Kort tryk: sluk straks" icon="_0x7">
{P}         <conditions id="{I['sc']}" name="Betingelser" icon="_0x16" note="Gruppering af betingelser til logisk test">
{P}            <condition id="{I['scc']}" name="%P &gt;= %S" icon="_0x1a" note="Betingelse at %P er større end eller samme som %S" link1="{T_TRYKTID_NAT}" link2="{I['tmr']}" method="_0x46">
{P}               <resource_timer id="{I['tmr']}" name="Timer" icon="_0x43" hour="0" minute="0" second="0" millisecond="1"/>
{P}            </condition>
{P}         </conditions>
{P}         <actions id="{I['sa']}" name="Kommandoer ved betingelser sande" icon="_0x8" note="Gruppering af kommandoer som udføres når betingelser er sande" type="_0x1">
{P}            <program_sub id="{I['dsub']}" name="Natdrift når det er mørkt" icon="_0x7">
{P}               <conditions id="{I['dc']}" name="Betingelser" icon="_0x16" note="Gruppering af betingelser til logisk test">
{P}                  <condition id="{I['dcc']}" name="%P = ON" icon="_0x1a" note="Betingelse at %P er ON" link1="{SKUMRING}" method="_0xa"/>
{P}               </conditions>
{P}               <actions id="{I['da']}" name="Kommandoer ved betingelser sande" icon="_0x8" note="Gruppering af kommandoer som udføres når betingelser er sande" type="_0x1">
{P}                  <action id="{I['a_nat']}" name="%P = ON" icon="_0x9" note="Sætter natdrift" link1="{NATDRIFT}" method="_0xa"/>
{P}                  <action id="{I['a_afv']}" name="%P = OFF" icon="_0x9" note="Sætter %P" link1="{AFVENTER_NAT}" method="_0x14"/>
{P}                  <action id="{I['a_slk1']}" name="Fremkald %P" icon="_0x9" note="Slukker straks" link1="{sc}" method="_0xa"/>
{P}               </actions>
{P}               <actions id="{I['df']}" name="Kommandoer ved betingelser falske" icon="_0x8" note="Lyst ude: slukker også straks">
{P}                  <action id="{I['a_slk2']}" name="Fremkald %P" icon="_0x9" note="Slukker straks" link1="{sc}" method="_0xa"/>
{P}               </actions>
{P}            </program_sub>
{P}            <program_sub id="{I['psub']}" name="PIR står stadig på ON: vent på ny bevægelse" icon="_0x7">
{P}               <conditions id="{I['pc']}" name="Betingelser" icon="_0x16" note="Gruppering af betingelser til logisk test">
{P}                  <condition id="{I['pcc']}" name="%P = ON" icon="_0x1a" note="Betingelse at %P er ON" link1="{PIR}" method="_0xa"/>
{P}               </conditions>
{P}               <actions id="{I['pa']}" name="Kommandoer ved betingelser sande" icon="_0x8" note="Gruppering af kommandoer som udføres når betingelser er sande" type="_0x1">
{P}                  <action id="{I['a_flag']}" name="%P = ON" icon="_0x9" note="PIR&apos;en må først tænde igen efter at have været i ro" link1="{fl}" method="_0xa"/>
{P}               </actions>
{P}            </program_sub>
{P}            <action id="{I['a_man']}" name="%P = ON" icon="_0x9" note="Manuel slukning: spærrer PIR&apos;en kortvarigt" link1="{FLAG_MANUEL}" method="_0xa"/>
{P}            <action id="{I['a_sp']}" name="Aktiver nedtælling på %P med initial værdi" icon="_0x9" note="Efter nedtællingen frigives PIR&apos;en igen" link1="{T_SPAERRING_MANUEL}" method="_0xbe"/>
{P}            <action id="{I['a_ef']}" name="Stands tælling på %P" icon="_0x9" note="Standser efterløbet" link1="{T_EFTERLOEB}" method="_0xdc"/>
{P}            <action id="{I['a_st']}" name="%P = %S" icon="_0x9" note="Lampen er slukket" link1="{E_DAEMPER_STATUS}" link2="{I['en']}" method="_0x1e">
{P}               <resource_enum id="{I['en']}" name="Enumerator" typedef="{TYPEDEF_DAEMPER}" inivalue="{V_SLUKKET}" icon="_0x22"/>
{P}            </action>
{P}         </actions>
{P}         <actions id="{I['fa']}" name="Kommandoer ved betingelser falske" icon="_0x8" note="Gruppering af kommandoer som udføres når betingelser er falske" type="_0x0">
{P}            <action id="{I['a_stop']}" name="Stop regulering af %P" icon="_0x9" note="Stop regulering af lysniveauet for scenariet" link1="{SC_MANUEL_REG}" method="_0x46"/>
{P}            <action id="{I['a_ef2']}" name="%P = %S" icon="_0x9" note="Sætter %P til samme værdi som %S" link1="{T_EFTERLOEB}" link2="{TT_EFTERLOEB_DAG}" method="_0x1e"/>
{P}            <action id="{I['a_ef3']}" name="Aktiver nedtælling på %P" icon="_0x9" note="Aktiver nedtælling på %P" link1="{T_EFTERLOEB}" method="_0xd2"/>
{P}         </actions>
{P}      </program_sub>
{P}      <action id="{I['a_tt']}" name="Stands tælling på %P" icon="_0x9" note="Standser evt. igangværende optælling eller nedtælling på %P" link1="{T_TRYKTID_NAT}" method="_0xdc"/>
{P}   </actions>
{P}</program_simple>
{P}<program_simple id="{I['q']}" name="PIR i ro: frigiv efter sluk fra soveværelset" icon="_0x7" note="Når PIR&apos;en har været i ro, må næste bevægelse tænde lyset igen.">
{P}   <events id="{I['qevs']}" name="Hændelser" icon="_0xb" note="Hændelser som starter program">
{P}      <event id="{I['qev']}" name="%P -&gt; OFF" icon="_0xc" note="Starter program" link1="{PIR}" method="_0x14"/>
{P}   </events>
{P}   <actions id="{I['qacts']}" name="Kommandoer" icon="_0x8" note="Kommandoer" type="_0x2">
{P}      <action id="{I['q_a']}" name="%P = OFF" icon="_0x9" note="Sætter %P" link1="{fl}" method="_0x14"/>
{P}   </actions>
{P}</program_simple>
""".replace("\n", N)
    t = v.text
    i = t.find('<program_simple id="_0x83751e"')
    end = t.find("</program_simple>", i) + len("</program_simple>") + 2
    old = t[t.rfind(N, 0, i) + 2:end]
    v.replace_once(old, old + release)

    # Header
    a.commit()
    v.save(dst)
    print(f"skrevet {dst}  last_unique_id=_0x{v.last_unique_id:x}  (+{a.counter - 0x84E3} id'er)")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
