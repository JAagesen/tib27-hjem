"""Check the Home Assistant config in ha/config against the house rules.

    python tools/check_ha.py            # exit 1 on errors

ERROR = must be fixed before the config goes back into HA.
WARN  = works, but is a known trap.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "ha" / "config"

# --- house rules ----------------------------------------------------------
ALWAYS_ON = {
    "light.kokken_3984477": "Luxo Lampe i Køkken skal altid være tændt",
}
# Hue lights come back on at their last level when no level is given — which
# can be 0 %. Any turn_on of these must set a level.
HUE_LIGHTS = {
    "light.stue", "light.verner_panton", "light.lillestue", "light.sovevaerelse",
    "light.bjornevaerelse", "light.extended_color_light_1", "light.extended_color_light_1_2",
    "light.le_klint_1", "light.le_klint_2", "light.lille_lampe",
}
LEVEL_KEYS = {"brightness", "brightness_pct", "brightness_step", "brightness_step_pct"}
SECRET_KEY = re.compile(r"(password|passwd|token|api_key|apikey|secret|private_key|webhook_id)", re.I)


@dataclass
class Finding:
    level: str
    where: str
    message: str

    def __str__(self) -> str:
        return f"{self.level:5} {self.where}: {self.message}"


class Tagged(str):
    """Value of a YAML tag such as !secret or !include."""

    def __new__(cls, tag: str, value: str):
        s = super().__new__(cls, value)
        s.tag = tag
        return s


class Loader(yaml.SafeLoader):
    pass


def _tag(loader: Loader, node: yaml.Node) -> Tagged:
    return Tagged(node.tag, loader.construct_scalar(node))  # type: ignore[arg-type]


for t in ("!secret", "!include", "!include_dir_merge_named", "!include_dir_named",
          "!include_dir_list", "!include_dir_merge_list", "!env_var", "!input"):
    Loader.add_constructor(t, _tag)


def load(path: Path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=Loader)


def _walk(node, path=()):
    yield path, node
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _walk(v, path + (str(k),))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, path + (str(i),))


def _as_list(v) -> list:
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def _service_calls(node):
    """Every dict that calls a service (``action:`` or legacy ``service:``)."""
    for _, n in _walk(node):
        if isinstance(n, dict):
            svc = n.get("action") if isinstance(n.get("action"), str) else n.get("service")
            if isinstance(svc, str) and "." in svc:
                yield svc, n


def _targets(call: dict) -> set[str]:
    ents: set[str] = set()
    for src in (call.get("target") or {}, call.get("data") or {}, call):
        if isinstance(src, dict):
            ents.update(e for e in _as_list(src.get("entity_id")) if isinstance(e, str))
    return ents


def check_secrets() -> list[Finding]:
    out = []
    for f in sorted(CONFIG.glob("*.yaml")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            m = re.match(r"^\s*#?\s*-?\s*([\w-]+)\s*:\s*(.+?)\s*$", line)
            if not m or not SECRET_KEY.search(m.group(1)):
                continue
            value = m.group(2)
            if value.startswith("!secret") or value == "<fjernet>":
                continue
            out.append(Finding("ERROR", f"{f.name}:{n}", f"'{m.group(1)}' står i klartekst — brug !secret"))
    return out


def check_automations() -> list[Finding]:
    out: list[Finding] = []
    autos = load(CONFIG / "automations.yaml") or []
    seen: dict[str, str] = {}
    for a in autos:
        aid, alias = str(a.get("id")), a.get("alias", "?")
        where = f"automation {aid} «{alias}»"
        if aid in seen:
            out.append(Finding("ERROR", where, f"samme id som «{seen[aid]}»"))
        seen[aid] = alias

        for svc, call in _service_calls(a):
            ents = _targets(call)
            # Rule: the always-on lamps are never switched off.
            if svc in ("light.turn_off", "light.toggle", "homeassistant.turn_off"):
                for e in ents & ALWAYS_ON.keys():
                    out.append(Finding("ERROR", where, f"{svc} på {e} — {ALWAYS_ON[e]}"))
            # Rule: Hue lights get an explicit level when turned on.
            if svc == "light.turn_on" and ents & HUE_LIGHTS:
                data = call.get("data") or {}
                if not (LEVEL_KEYS & set(data)):
                    out.append(Finding("WARN", where,
                                       f"tænder {', '.join(sorted(ents & HUE_LIGHTS))} uden niveau — "
                                       "Hue-pæren arver sidste niveau, som kan være 0 %"))
        # Regression guard: the duplicate zone 'Home ' was deleted 29-10-2026.
        for p, v in _walk(a):
            if not (isinstance(v, str) and v in ("Home ", "Home") and p):
                continue
            key = p[-2] if p[-1].isdigit() and len(p) > 1 else p[-1]   # list item or scalar
            if key in ("state", "to", "from"):
                out.append(Finding("WARN", where, f"tilstanden {v!r} findes ikke længere — brug 'home'"))
    return out


def check_parse() -> list[Finding]:
    out = []
    for f in sorted(CONFIG.glob("*.yaml")):
        try:
            load(f)
        except yaml.YAMLError as exc:
            out.append(Finding("ERROR", f.name, f"ugyldig YAML: {exc}"))
    return out


def run() -> list[Finding]:
    findings = check_parse()
    if any(f.level == "ERROR" for f in findings):
        return findings
    return findings + check_secrets() + check_automations()


def main() -> int:
    findings = run()
    for f in findings:
        print(f)
    errors = sum(f.level == "ERROR" for f in findings)
    warns = sum(f.level == "WARN" for f in findings)
    print(f"\n{errors} fejl, {warns} advarsler")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
