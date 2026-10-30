import pytest
from conftest import MINI, make

from tib27_ihc import IdAllocator, make_id, parse_id
from tib27_ihc.diff import diff
from tib27_ihc.dump import dump_block
from tib27_ihc.verify import ERROR, WARN, verify


def codes(findings, level=ERROR):
    return sorted(f.code for f in findings if f.level == level)


def test_ids_roundtrip():
    assert parse_id("_0x84a628") == (0x84A6, 0x28)
    assert make_id(0x84A6, "functionblock") == "_0x84a628"
    with pytest.raises(ValueError):
        parse_id("off")


def test_clean_file_has_no_findings(mini):
    assert verify(mini) == []


def test_save_is_byte_exact(mini, tmp_path):
    p = mini.save(tmp_path / "a.vis")
    assert p.read_bytes() == mini.raw
    assert b"\r\n" in p.read_bytes() and "æ".encode("iso-8859-1") in p.read_bytes()


def test_one_sided_link_is_an_error(mini):
    mini.replace_once('<link_from_resource id="_0x152d" link="_0x142c"/>',
                      '<link_from_resource id="_0x152d" link="_0x1311"/>')
    assert "link-pair" in codes(verify(mini))


def test_dead_reference_is_an_error(mini):
    mini.replace_once('link1="_0x1a4a"', 'link1="_0x9999ca"')
    assert "dead-ref" in codes(verify(mini))


def test_enum_inivalue_is_a_reference_but_input_inivalue_is_not():
    v = make(MINI.replace('<resource_input id="_0x1311" name="Skumring">',
                          '<resource_input id="_0x1311" name="Skumring" inivalue="off">'))
    assert verify(v) == []
    v.replace_once('inivalue="_0x1848"', 'inivalue="_0x7777"')
    assert codes(verify(v)) == ["dead-ref"]


def test_duplicate_id(mini):
    mini.replace_once('<enum_value id="_0x1848" name="Slukket"/>',
                      '<enum_value id="_0x1848" name="Slukket"/><enum_value id="_0x1848" name="Igen"/>')
    assert "duplicate-id" in codes(verify(mini))


def test_counter_above_last_unique_id(mini):
    mini.replace_once('last_unique_id="_0x24"', 'last_unique_id="_0x20"')
    assert "last-unique-id" in codes(verify(mini))


def test_broken_scene_pair_and_level(mini):
    mini.replace_once('dimming_value="45"', 'dimming_value="140"')
    assert "scene-level" in codes(verify(mini))
    mini.replace_once('ramptime_ms="2000" link="_0x1b4b"', 'ramptime_ms="2000" link="_0x1a4a"')
    assert "scene-pair" in codes(verify(mini))


def test_missing_operand(mini):
    mini.replace_once(' link1="_0x1311" method="_0xa"', ' method="_0xa"')
    assert "operand" in codes(verify(mini))


def test_lf_line_endings_warn_and_lf_only_fails():
    mixed = make()
    mixed.raw = mixed.raw.replace(b"</groups>\r\n", b"</groups>\n", 1)
    assert "line-endings" in codes(verify(mixed), WARN)
    assert "line-endings" in codes(verify(make(crlf=False)), ERROR)


def test_utf8_damage_is_caught():
    v = make()
    v.raw = v.raw.replace("ø".encode("iso-8859-1"), b"\xef\xbf\xbd")
    assert "encoding" in codes(verify(v))


def test_allocator_continues_counter_and_updates_header(mini):
    alloc = IdAllocator(mini)
    assert alloc.next("flag") == "_0x250a"
    assert alloc.next("action") == "_0x26ca"
    alloc.commit()
    assert 'last_unique_id="_0x26"' in mini.text
    assert mini.last_unique_id == 0x26


def test_replace_once_refuses_ambiguous_anchor(mini):
    with pytest.raises(ValueError):
        mini.replace_once('method="_0xa"', 'method="_0x14"')


def test_dump_reads_like_ihc_visual(mini):
    out = dump_block(mini, "Billedlys følger")
    assert "NÅR: Status bliver ændret" in out
    assert "- Skumring = ON" in out
    assert "- Fremkald Tænd billedlys" in out
    assert "Skumring  [input _0x1311]  ↔ Skumring ude" in out


def test_dump_unknown_block_suggests(mini):
    with pytest.raises(KeyError, match="Billedlys følger"):
        dump_block(mini, "Billedlys")


def test_diff_finds_only_the_edit(mini):
    new = make()
    new.replace_once('dimming_value="45"', 'dimming_value="50"')
    regions = diff(mini, new)
    assert len(regions) == 1 and regions[0].ids == ["_0x1c4c"]

