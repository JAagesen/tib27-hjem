"""Render a function block as readable text, the way it reads in IHC Visual.

    ### Spisekarnappen tændes eller slukkes
      NÅR: Status Lys i Spisekarnap bliver ændret
      [Tænd billedlyset med]
        HVIS alle:
          - Skumring = ON
        SÅ:
          - Fremkald Tænd billedlys over pigen
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

from .vis import VisFile

RESOURCE_TAGS = ("resource_input", "resource_output", "resource_enum", "resource_flag",
                 "resource_integer", "resource_timer", "resource_counter", "resource_time",
                 "resource_timertime", "resource_light_level", "resource_scene")


def operand(vis: VisFile, ref: str | None) -> str:
    if not ref:
        return "?"
    e = vis.get(ref)
    if e is None:
        return f"<død ref {ref}>"
    # A local constant (resource_enum under a condition/action) shows its value.
    if e.tag == "resource_enum" and e.get("inivalue"):
        parent = vis.parent(e)
        if parent is not None and parent.tag in ("event", "condition", "action"):
            v = vis.get(e.get("inivalue", ""))
            return v.get("name", "?") if v is not None else "?"
    return e.get("name") or f"{e.tag} {ref}"


def statement(vis: VisFile, e: ET.Element) -> str:
    text = e.get("name") or e.get("method") or e.tag
    text = text.replace("%P", operand(vis, e.get("link1")))
    if "%S" in text:
        text = text.replace("%S", operand(vis, e.get("link2")))
    return text


def _render(vis: VisFile, e: ET.Element, depth: int, out: list[str]) -> None:
    pad = "  " * depth
    tag = e.tag
    if tag == "program_simple":
        out.append(f"{pad}### {e.get('name', '')}")
        for c in e:
            _render(vis, c, depth + 1, out)
    elif tag == "program_sub":
        out.append(f"{pad}[{e.get('name', '')}]")
        for c in e:
            _render(vis, c, depth + 1, out)
    elif tag == "events":
        for c in e:
            if c.tag == "event":
                out.append(f"{pad}NÅR: {statement(vis, c)}")
    elif tag == "conditions":
        items = [c for c in e if c.tag == "condition"]
        if items:
            out.append(f"{pad}HVIS {'en af' if e.get('type') == 'or' else 'alle'}:")
            out.extend(f"{pad}  - {statement(vis, c)}" for c in items)
    elif tag == "actions":
        label = {"_0x1": "SÅ:", "_0x0": "ELLERS:"}.get(e.get("type", ""), "UDFØR:")
        if len(e):
            out.append(f"{pad}{label}")
        for c in e:
            if c.tag == "action":
                out.append(f"{pad}  - {statement(vis, c)}")
            else:
                _render(vis, c, depth + 1, out)


def dump_block(vis: VisFile, name_or_id: str) -> str:
    fb = vis.get(name_or_id) if name_or_id.startswith("_0x") else vis.functionblock(name_or_id)
    if fb is None or fb.tag != "functionblock":
        raise KeyError(f"{name_or_id} er ikke en funktionsblok")
    out = [f"# {fb.get('name')}  ({fb.get('id')})"]
    if fb.get("master_name"):
        out.append(f"  skabelon: {fb.get('master_name')}")
    for section, title in (("inputs", "Indgange"), ("outputs", "Udgange"),
                           ("settings", "Indstillinger"), ("internalsettings", "Interne")):
        sec = fb.find(section)
        if sec is None:
            continue
        res = [r for r in sec if r.tag in RESOURCE_TAGS]
        if res:
            out.append(f"  {title}:")
            for r in res:
                links = [vis.get(l.get("link", "")) for l in r if l.tag in ("link_to_resource", "link_from_resource")]
                where = ", ".join(_owner(vis, p) for p in links if p is not None)
                out.append(f"    {r.get('name')}  [{r.tag.removeprefix('resource_')} {r.get('id')}]"
                           + (f"  ↔ {where}" if where else ""))
    progs = fb.find("programs")
    if progs is not None:
        out.append("")
        for p in progs:
            _render(vis, p, 1, out)
    return "\n".join(out)


def _owner(vis: VisFile, link: ET.Element) -> str:
    """Name of the resource that holds the other end of a link."""
    p = vis.parent(link)
    return p.get("name", p.tag) if p is not None else "?"
