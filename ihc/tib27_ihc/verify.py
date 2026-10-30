"""Structural checks for a .vis file — run before every upload to the controller.

Each check returns findings; ``ERROR`` means "do not upload", ``WARN`` means
"look at it". The checks are the ones that caught real mistakes while editing
TIB27 by hand: one-sided links, dangling references, a counter that would make
IHC Visual hand out an id that already exists, and line-ending damage.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass

from .vis import VisFile, parse_id, ref_attrs

ERROR, WARN, INFO = "ERROR", "WARN", "INFO"


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.level:5} {self.code:16} {self.message}"


def _label(e: ET.Element) -> str:
    n = e.get("name")
    return f"{e.tag} {e.get('id')}" + (f" «{n}»" if n else "")


def check_bytes(vis: VisFile) -> list[Finding]:
    out: list[Finding] = []
    crlf = vis.raw.count(b"\r\n")
    bare_lf = vis.raw.count(b"\n") - crlf
    if bare_lf:
        out.append(Finding(WARN, "line-endings",
                           f"{bare_lf} linjer slutter med LF i stedet for CRLF"))
    if crlf == 0 and bare_lf:
        out.append(Finding(ERROR, "line-endings", "filen har slet ingen CRLF — den er blevet konverteret"))
    if b"\xef\xbf\xbd" in vis.raw:
        n = vis.raw.count(b"\xef\xbf\xbd")
        out.append(Finding(ERROR, "encoding",
                           f"{n} tegn er erstattet med '�' — filen har været gennem en "
                           "UTF-8-konvertering, og æ/ø/å er tabt. Brug en original kopi."))
    head = vis.raw[:100].lower()
    if b"iso-8859-1" not in head:
        out.append(Finding(WARN, "encoding", "XML-erklæringen nævner ikke ISO-8859-1"))
    return out


def check_ids(vis: VisFile) -> list[Finding]:
    out: list[Finding] = []
    ids = [e.get("id") for e in vis.root.iter() if e.get("id")]
    for i, n in Counter(ids).items():
        if n > 1:
            out.append(Finding(ERROR, "duplicate-id", f"{i} findes {n} gange"))
    try:
        last = vis.last_unique_id
    except ValueError as exc:
        return out + [Finding(ERROR, "last-unique-id", str(exc))]
    top = 0
    bad = 0
    for i in ids:
        try:
            c, _ = parse_id(i)
        except ValueError:
            bad += 1
            continue
        top = max(top, c)
    if bad:
        out.append(Finding(WARN, "id-format", f"{bad} id'er har ikke formen _0x<tæller><type>"))
    if top > last:
        out.append(Finding(ERROR, "last-unique-id",
                           f"højeste tæller i brug er _0x{top:x}, men last_unique_id er _0x{last:x} — "
                           "IHC Visual vil uddele id'er der allerede findes"))
    return out


def check_references(vis: VisFile) -> list[Finding]:
    out: list[Finding] = []
    idx = vis.index
    for e in vis.root.iter():
        for a in ref_attrs(e.tag):
            ref = e.get(a)
            if ref and ref not in idx:
                out.append(Finding(ERROR, "dead-ref", f"{_label(e)}: {a}={ref} peger på ingenting"))
    return out


def check_links(vis: VisFile) -> list[Finding]:
    """link_to_resource <-> link_from_resource must point at each other."""
    out: list[Finding] = []
    idx = vis.index
    pairs = {"link_to_resource": "link_from_resource", "link_from_resource": "link_to_resource"}
    for tag, peer_tag in pairs.items():
        for e in vis.root.iter(tag):
            peer = idx.get(e.get("link", ""))
            if peer is None:
                continue  # reported by check_references
            if peer.tag != peer_tag:
                out.append(Finding(ERROR, "link-pair", f"{_label(e)} peger på {peer.tag}, ikke {peer_tag}"))
            elif peer.get("link") != e.get("id"):
                out.append(Finding(ERROR, "link-pair",
                                   f"{_label(e)} -> {peer.get('id')}, men den peger tilbage på {peer.get('link')}"))
    return out


def check_scenes(vis: VisFile) -> list[Finding]:
    """scene_link (under a resource_scene) <-> its member in the product's <scenes>."""
    out: list[Finding] = []
    idx = vis.index
    for e in vis.root.iter("scene_link"):
        member = idx.get(e.get("link", ""))
        if member is None:
            continue
        if member.get("link") != e.get("id"):
            out.append(Finding(ERROR, "scene-pair",
                               f"{_label(e)} -> {member.get('id')} ({member.tag}), som peger på {member.get('link')}"))
    for e in vis.root.iter("scene_dimmer"):
        sl = idx.get(e.get("link", ""))
        if sl is not None and sl.tag != "scene_link":
            out.append(Finding(ERROR, "scene-pair", f"{_label(e)} peger på {sl.tag}, ikke scene_link"))
        v = e.get("dimming_value")
        if v is not None and not (v.isdigit() and 0 <= int(v) <= 100):
            out.append(Finding(ERROR, "scene-level", f"{_label(e)} har dimming_value={v!r} (skal være 0–100)"))
    return out


def check_programs(vis: VisFile) -> list[Finding]:
    """Events/conditions/actions need the operand their method uses."""
    out: list[Finding] = []
    for tag in ("event", "condition", "action"):
        for e in vis.root.iter(tag):
            name = e.get("name", "")
            if "%P" in name and not e.get("link1"):
                out.append(Finding(ERROR, "operand", f"{_label(e)} bruger %P men mangler link1"))
            if "%S" in name and not e.get("link2"):
                out.append(Finding(ERROR, "operand", f"{_label(e)} bruger %S men mangler link2"))
    return out


ALL_CHECKS = (check_bytes, check_ids, check_references, check_links, check_scenes, check_programs)


def verify(vis: VisFile) -> list[Finding]:
    findings = check_bytes(vis)
    try:
        vis.root
    except ET.ParseError as exc:
        return findings + [Finding(ERROR, "xml", f"filen er ikke gyldig XML: {exc}")]
    for chk in ALL_CHECKS[1:]:
        findings.extend(chk(vis))
    return findings


def summary(vis: VisFile) -> dict[str, int]:
    r = vis.root
    return {
        "elementer": sum(1 for _ in r.iter()),
        "linkpar": sum(1 for _ in r.iter("link_to_resource")),
        "scenepar": sum(1 for _ in r.iter("scene_link")),
        "funktionsblokke": sum(1 for _ in r.iter("functionblock")),
        "last_unique_id": vis.last_unique_id,
    }
