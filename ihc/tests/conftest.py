import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tib27_ihc import VisFile  # noqa: E402

# A tiny but structurally complete project: one function block with an input
# linked to a product, an enum output, a scene pair, and one program.
# Counters run 0x10..0x24; last_unique_id = 0x24.
MINI = """<?xml version="1.0" encoding="ISO-8859-1"?>
<utcs_project version_major="3" version_minor="0" id1="_0x1" id2="_0x2" last_unique_id="_0x24">
<groups>
<group id="_0x1027" name="Stue">
<functionblock id="_0x1128" name="Billedlys følger" master_name="Test">
<inputs id="_0x1223">
<resource_input id="_0x1311" name="Skumring">
<link_to_resource id="_0x142c" link="_0x152d"/>
</resource_input>
<resource_enum id="_0x160f" name="Status" typedef="_0x1747" inivalue="_0x1848"/>
</inputs>
<outputs id="_0x1924">
<resource_scene id="_0x1a4a" name="Tænd billedlys">
<scene_link id="_0x1b4b" link="_0x1c4c"/>
</resource_scene>
</outputs>
<programs id="_0x1d26">
<program_simple id="_0x1e1e" name="Status ændres">
<events id="_0x1f64"><event id="_0x20c8" name="%P bliver ændret" link1="_0x160f" method="_0x96"/></events>
<conditions id="_0x2165"><condition id="_0x22c9" name="%P = ON" link1="_0x1311" method="_0xa"/></conditions>
<actions id="_0x2366" type="_0x2"><action id="_0x24ca" name="Fremkald %P" link1="_0x1a4a" method="_0xa"/></actions>
</program_simple>
</programs>
</functionblock>
</group>
</groups>
<products>
<dataline_input id="_0x0f5a" name="Skumring ude">
<link_from_resource id="_0x152d" link="_0x142c"/>
</dataline_input>
<dimmer id="_0x0e54" name="Billedbelysning">
<scenes id="_0x0d49">
<scene_dimmer id="_0x1c4c" dimming_value="45" ramptime_ms="2000" link="_0x1b4b"/>
</scenes>
</dimmer>
</products>
<typedefs>
<enum_definition id="_0x1747" name="Lysstatus">
<enum_value id="_0x1848" name="Slukket"/>
</enum_definition>
</typedefs>
</utcs_project>
"""


def make(text: str = MINI, crlf: bool = True) -> VisFile:
    if crlf:
        text = text.replace("\n", "\r\n")
    return VisFile.from_text(text)


@pytest.fixture
def mini() -> VisFile:
    return make()
