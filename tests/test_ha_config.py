"""The real config must pass, and each house rule must actually bite."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import check_ha  # noqa: E402


def test_live_config_has_no_errors():
    errors = [f for f in check_ha.run() if f.level == "ERROR"]
    assert errors == [], "\n".join(map(str, errors))


@pytest.fixture
def cfg(tmp_path, monkeypatch):
    monkeypatch.setattr(check_ha, "CONFIG", tmp_path)

    def write(automations: str = "[]", configuration: str = "logger:\n  default: warning\n"):
        (tmp_path / "automations.yaml").write_text(automations, encoding="utf-8")
        (tmp_path / "configuration.yaml").write_text(configuration, encoding="utf-8")
    return write


def _msgs(level):
    return [f.message for f in check_ha.run() if f.level == level]


def test_luxo_may_never_be_switched_off(cfg):
    cfg("""
- id: '1'
  alias: sluk alt
  actions:
  - action: light.turn_off
    target: {entity_id: [light.kokken_3987805, light.kokken_3984477]}
""")
    assert any("Luxo" in m for m in _msgs("ERROR"))


def test_hue_without_level_warns_and_with_level_passes(cfg):
    cfg("""
- id: '1'
  alias: bar
  actions:
  - action: light.turn_on
    target: {entity_id: light.bjornevaerelse}
- id: '2'
  alias: med niveau
  actions:
  - action: light.turn_on
    target: {entity_id: light.bjornevaerelse}
    data: {brightness_pct: 80}
- id: '3'
  alias: ihc uden niveau er ok
  actions:
  - action: light.turn_on
    target: {entity_id: light.store_stue_942429}
""")
    warns = _msgs("WARN")
    assert len(warns) == 1 and "0 %" in warns[0]


def test_plaintext_password_is_an_error_even_in_a_comment(cfg):
    cfg(configuration="ihc:\n  - url: x\n    password: hunter2\n#   password: hunter3\n")
    assert len(_msgs("ERROR")) == 2


def test_secret_tag_passes(cfg):
    cfg(configuration="ihc:\n  - url: x\n    password: !secret ihc_password\n")
    assert _msgs("ERROR") == []


def test_duplicate_automation_id(cfg):
    cfg("- {id: '7', alias: a}\n- {id: '7', alias: b}\n")
    assert any("samme id" in m for m in _msgs("ERROR"))


def test_deleted_zone_name_warns(cfg):
    cfg("""
- id: '1'
  alias: gammel zone
  triggers:
  - trigger: state
    entity_id: device_tracker.x
    to: 'Home '
""")
    assert any("'Home '" in m for m in _msgs("WARN"))


def test_tracker_blip_rules(cfg):
    cfg("""
- id: '1'
  alias: forlader uden ventetid
  actions: [{action: light.turn_off}]
  triggers:
  - {trigger: state, entity_id: device_tracker.jan_s_s22, to: not_home}
- id: '2'
  alias: forlader med 3 min
  actions: [{action: light.turn_off}]
  triggers:
  - {trigger: state, entity_id: device_tracker.jan_s_s22, to: not_home, for: '00:03:00'}
- id: '3'
  alias: kommer hjem uden fravaerskrav
  actions: [{action: light.turn_on}]
  triggers:
  - {trigger: state, entity_id: person.miv, from: not_home, to: home}
- id: '4'
  alias: kommer hjem med fravaerskrav
  actions: [{action: light.turn_on}]
  triggers:
  - {trigger: state, entity_id: person.miv, from: not_home, to: home}
  conditions:
  - condition: template
    value_template: "{{ (trigger.to_state.last_changed - trigger.from_state.last_changed).total_seconds() >= 180 }}"
""")
    warns = [f.where for f in check_ha.run() if f.level == "WARN"]
    assert any("«forlader uden ventetid»" in w for w in warns)
    assert any("«kommer hjem uden fravaerskrav»" in w for w in warns)
    assert not any("«forlader med 3 min»" in w or "«kommer hjem med fravaerskrav»" in w for w in warns)


def test_automation_without_actions_is_ignored(cfg):
    cfg("""
- id: '1'
  alias: tom
  triggers:
  - {trigger: state, entity_id: device_tracker.x, to: not_home}
  actions: []
""")
    assert _msgs("WARN") == []
