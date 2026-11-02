# Overdragelse — status 2-11-2026

Til næste samtale. Læs denne først.

## Kodeprojektet `tib27-hjem`
- GitHub: `JAagesen/tib27-hjem` (privat) — **oprettet, men tomt**. Intet er pushet endnu.
- Hele projektet ligger i den nyeste `tib27-hjem.zip` fra samtalen 30-10 → 2-11-2026:
  6 commits, den øverste hedder "Overdragelsesnote til næste samtale".
  Jan vedhæfter zip-filen i første besked. Første opgave: pak ud, tjek
  `git log` (6 commits), kør `pytest` (26 tests) og `python tools/check_ha.py`
  (0 fejl, 0 advarsler), og push `main` til `JAagesen/tib27-hjem`.
- Indhold: `ha/config/` (HA-konfiguration, hemmeligheder som `!secret`),
  `ihc/tib27_ihc/` (`tib27-ihc verify|dump|diff|blocks`), `ihc/project/`
  (v151, v152), `ihc/changes/build152.py`, `tools/check_ha.py`, `docs/`.

## Adgang til HA
- Kun gennem Claude in Chrome mod `http://homeassistant.local:8123`.
  `document.querySelector('home-assistant').hass` giver states og token
  (forny med `hass.auth.refreshAccessToken()` før POST — ellers 401).
- Filer læses via File editor-tilføjelsens API
  (`<ingress>/api/file?filename=/homeassistant/…`). Overførsel til
  containeren: vis teksten med `§` foran hver linje og `¤` for mellemrum,
  læs med `get_page_text`, kontrollér med FNV-1a-checksum.
- `configuration.yaml` har IHC-passwordet i klartekst og en udkommenteret
  UniFi-blok med routerens root-password. Gentag dem aldrig; filtrér dem
  i browseren før overførsel.

## IHC
- Projektfiler: `C:\Users\jan\OneDrive\IHC\Projekter\` på Jans pc (jans-x1).
- **v151 er IKKE uploadet til controlleren.** Hvad der kører, er ukendt —
  sandsynligvis v147 eller tidligere. v152 indeholder v148–v151 + gangrettelsen.
  Spørg Jan hvilken version der kører, før v152 uploades.
- Jans pc meldte "disk full" ved skrivning 1-11.
- Faste regler: backup før upload, `verify` skal sige KLAR, åbn i IHC
  Visual før upload. Markise-flagene `_0x80c90a`, `_0x80ca0a`, `_0x80cb0a`,
  `_0x80cc0a` må ikke ændres. Frostfri-stikket må aldrig slukkes. Sluk Alt
  når hele huset; Tænd Alt kun stue/køkken/spisekarnap.

## Rettet i denne samtale
| Dato | Hvad | Note |
|---|---|---|
| 29-10 | Dubletzone `Home ` slettet; Bjørneværelset tændte på 0 % | `ha-bjornevaerelset-zone-dublet.md` |
| 30-10 | Hjemkomst-lys: mørke-betingelse, kontakt-niveauer | `ha-hjemkomst-lys-niveauer.md` |
| 30-10 | Luxo Lampe i Køkken skal altid være tændt (fast regel) | `ha-hjemkomst-lys-niveauer.md` |
| 1-11 | Mammotion: refreshToken udløbet → Jan genkonfigurerede; Aliyun-transport fejler stadig, men data kommer | — |
| 1-11 | IHC v152: gangen slukkes straks fra soveværelset, tænder ikke igen | `ihc-gang-sluk-fra-sovevaerelse.md` |
| 2-11 | Tracker-udfald slukkede huset → 3 min-regel overalt | `ha-tracker-udfald.md` |
| 2-11 | Skumringslys omdøbt + Hue-niveauer; hjemkomst også med Ella | `ha-hjemkomst-lys-niveauer.md` |

## Åbent
- Push repoet (se øverst).
- Afklar hvilken IHC-version der kører; upload v152 efter backup.
- Flyt IHC-passwordet til `secrets.yaml`; fjern UniFi-blokken; Jan bør
  skifte routerens password.
- `stue_tryk_off_faelles` og `Sluk_Alt_Fælles` har samme IHC-id (1439068).
- Omdøb `light.extended_color_light_1` / `_1_2` (Le Klint i Bjørneværelset).
- Network-dashboardet: ét kort pr. UniFi-klient (Jans valg), ikke startet.
- Dashboards ligger ikke i repoet endnu.
- Mammotion: hold øje med om kommandoer fra HA virker uden Aliyun.
