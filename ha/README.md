# Home Assistant-konfigurationen

Øjebliksbillede af `/homeassistant` hentet 30-10-2026 (HA 2026.10.1).

| Fil | Indhold |
|---|---|
| `config/configuration.yaml` | Kerne, logger, recorder, IHC-ressourcer |
| `config/automations.yaml` | 40 automatiseringer |
| `config/scripts.yaml` | `heat_on_and_off`, `all_lights_off` (pulserer IHC Sluk alt) |
| `config/scenes.yaml` | Daikin-scenen "Temperatur" |
| `config/fjernet_taend_lys_naar_vi_kommer_hjem.yaml` | Arkiveret, ikke indlæst |

Ikke med: `secrets.yaml`, databasen, logfiler, `.storage/` (dashboards,
zoner, entitetsregister) og `custom_components/`.

## Hvordan filerne kom herind

Den eneste vej til HA er gennem browseren. Filerne blev hentet via File
editor-tilføjelsens API, passwords blev erstattet med `!secret` i
browseren *før* noget forlod HA, og hver fil blev kontrolleret mod en
FNV-1a-checksum beregnet i browseren — de er identiske med originalen,
bortset fra de to redigerede password-linjer.

## Sende en ændring tilbage

1. Ret i repoet og kør `python tools/check_ha.py` og `pytest`.
2. Tag en kopi af den fil der overskrives i HA (fx `automations.yaml.bak-ÅÅÅÅMMDD`).
3. Overfør filen med File editor, og sørg for at `ihc_password` findes i
   HA's `secrets.yaml`, før `configuration.yaml` fra repoet tages i brug.
4. `automation.reload` for automatiseringer; `configuration.yaml` kræver
   *Kontrollér konfiguration* og en genstart.

Automatiseringer kan også skrives direkte gennem
`POST /api/config/automation/config/<id>` — den skriver `automations.yaml`
og genindlæser kun den ene automatisering. Hent så filen hjem bagefter.
