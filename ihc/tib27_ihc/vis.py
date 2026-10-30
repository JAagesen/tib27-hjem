"""Read and write IHC Visual 3 project files (.vis) without disturbing them.

The format is XML in ISO-8859-1 with CRLF line endings and an internal DTD.
IHC Visual is picky, so the rule here is: the raw bytes are the truth. We parse
a tree for *reading*, but every change is made as text surgery on the raw file
and written back byte-for-byte, never by re-serialising the tree (ElementTree
would add DTD default attributes, reorder quoting and drop the CRLFs).

Ids look like ``_0x<counter><type>``: the last two hex digits are the element
type, the rest is a project-wide counter. ``utcs_project/@last_unique_id`` is
the highest counter handed out so far.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

ENCODING = "iso-8859-1"

# Type byte -> element kind. Collected from real projects; not exhaustive.
TYPES: dict[int, str] = {
    0x0A: "flag", 0x0B: "integer", 0x0C: "counter", 0x0D: "time",
    0x0F: "enum", 0x10: "timer", 0x11: "input", 0x12: "output",
    0x13: "light_level", 0x17: "timertime", 0x1D: "light_indication",
    0x1E: "program_simple", 0x1F: "program_sub",
    0x23: "inputs", 0x24: "outputs", 0x25: "settings", 0x26: "programs",
    0x28: "functionblock", 0x29: "internalsettings",
    0x2C: "link_to_resource", 0x2D: "link_from_resource",
    0x47: "enum_definition", 0x48: "enum_value",
    0x4A: "resource_scene", 0x4B: "scene_link", 0x4C: "scene_dimmer",
    0x5A: "dataline_input", 0x5C: "airlink_input",
    0x64: "events", 0x65: "conditions", 0x66: "actions",
    0xC8: "event", 0xC9: "condition", 0xCA: "action",
}
TYPE_BY_NAME = {v: k for k, v in TYPES.items()}

# Method codes used by event/condition/action. Names as IHC Visual shows them.
METHODS: dict[str, str] = {
    "_0xa": "%P = ON / Fremkald %P",
    "_0x14": "%P = OFF",
    "_0x19": "%P = Initialværdi",
    "_0x1e": "%P = %S",
    "_0x23": "Kip %P",
    "_0x28": "%P <> %S",
    "_0x32": "%P > %S",
    "_0x3c": "%P < %S",
    "_0x46": "%P >= %S",
    "_0x96": "%P bliver ændret",
    "_0xbe": "Aktiver nedtælling med initialværdi",
    "_0xc8": "Aktiver optælling",
    "_0xd2": "Aktiver nedtælling på %P",
    "_0xdc": "Stands tælling på %P",
}

# Attributes that hold a reference to another element's id. ``typedef`` and
# ``inivalue`` are references only on resource_enum; elsewhere ``inivalue`` is a
# literal (``on``, ``off``, ``95`` ...).
REF_ATTRS = ("link", "link1", "link2")
ENUM_REF_ATTRS = ("typedef", "inivalue")


def ref_attrs(tag: str) -> tuple[str, ...]:
    return REF_ATTRS + ENUM_REF_ATTRS if tag == "resource_enum" else REF_ATTRS

_ID_RE = re.compile(r"^_0x([0-9a-fA-F]+)$")


def parse_id(id_: str) -> tuple[int, int]:
    """``'_0x84a628'`` -> ``(0x84a6, 0x28)`` (counter, type)."""
    m = _ID_RE.match(id_ or "")
    if not m or len(m.group(1)) < 3:
        raise ValueError(f"not an element id: {id_!r}")
    h = m.group(1)
    return int(h[:-2], 16), int(h[-2:], 16)


def make_id(counter: int, type_: int | str) -> str:
    t = TYPE_BY_NAME[type_] if isinstance(type_, str) else type_
    return f"_0x{counter:x}{t:02x}"


def parse_counter(value: str) -> int:
    """``last_unique_id`` is a bare counter written as ``_0x<hex>``."""
    m = _ID_RE.match(value or "")
    if not m:
        raise ValueError(f"not a counter: {value!r}")
    return int(m.group(1), 16)


@dataclass
class VisFile:
    path: Path | None
    raw: bytes
    _root: ET.Element | None = field(default=None, repr=False)
    _index: dict[str, ET.Element] | None = field(default=None, repr=False)
    _parents: dict[ET.Element, ET.Element] | None = field(default=None, repr=False)

    # ---------- loading ----------
    @classmethod
    def load(cls, path: str | Path) -> "VisFile":
        p = Path(path)
        return cls(p, p.read_bytes())

    @classmethod
    def from_text(cls, text: str) -> "VisFile":
        return cls(None, text.encode(ENCODING))

    @property
    def text(self) -> str:
        return self.raw.decode(ENCODING)

    @property
    def root(self) -> ET.Element:
        if self._root is None:
            self._root = ET.fromstring(self.raw)
        return self._root

    def invalidate(self) -> None:
        self._root = self._index = self._parents = None

    # ---------- lookups ----------
    @property
    def index(self) -> dict[str, ET.Element]:
        """id -> element. Duplicate ids keep the first; see verify for dupes."""
        if self._index is None:
            idx: dict[str, ET.Element] = {}
            for e in self.root.iter():
                i = e.get("id")
                if i and i not in idx:
                    idx[i] = e
            self._index = idx
        return self._index

    @property
    def parents(self) -> dict[ET.Element, ET.Element]:
        if self._parents is None:
            self._parents = {c: p for p in self.root.iter() for c in p}
        return self._parents

    def get(self, id_: str) -> ET.Element | None:
        return self.index.get(id_)

    def parent(self, e: ET.Element) -> ET.Element | None:
        return self.parents.get(e)

    def functionblock(self, name: str) -> ET.Element:
        hits = [e for e in self.root.iter("functionblock") if e.get("name") == name]
        if not hits:
            near = sorted({e.get("name", "") for e in self.root.iter("functionblock")
                           if name.lower() in e.get("name", "").lower()})
            hint = f" Mente du: {', '.join(near[:5])}?" if near else ""
            raise KeyError(f"Ingen funktionsblok hedder {name!r}.{hint}")
        if len(hits) > 1:
            raise KeyError(f"{len(hits)} funktionsblokke hedder {name!r}; brug id")
        return hits[0]

    @property
    def last_unique_id(self) -> int:
        return parse_counter(self.root.get("last_unique_id", ""))

    # ---------- writing ----------
    def save(self, path: str | Path | None = None) -> Path:
        out = Path(path) if path else self.path
        if out is None:
            raise ValueError("no path to save to")
        out.write_bytes(self.raw)
        return out

    def replace_once(self, old: str, new: str) -> None:
        """Text surgery on the raw file. ``old`` must occur exactly once.

        Use ``\\r\\n`` in ``old``/``new`` where the file has line breaks.
        """
        t = self.text
        n = t.count(old)
        if n != 1:
            raise ValueError(f"anchor found {n} times, expected exactly 1: {old[:80]!r}")
        self.raw = t.replace(old, new).encode(ENCODING)
        self.invalidate()


class IdAllocator:
    """Hands out new ids above ``last_unique_id`` and updates the header.

    >>> alloc = IdAllocator(vis); fb = alloc.next("functionblock")
    ... # build XML text with the ids, insert it with vis.replace_once(...)
    >>> alloc.commit()   # writes the new last_unique_id into the file
    """

    def __init__(self, vis: VisFile):
        self.vis = vis
        self.start = vis.last_unique_id
        self.counter = self.start

    def next(self, type_: int | str) -> str:
        self.counter += 1
        return make_id(self.counter, type_)

    def commit(self) -> None:
        if self.counter == self.start:
            return
        old = f'last_unique_id="_0x{self.start:x}"'
        new = f'last_unique_id="_0x{self.counter:x}"'
        self.vis.replace_once(old, new)
        self.start = self.counter
