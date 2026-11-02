# TIB27 — Home Assistant og IHC

Konfiguration, værktøjer og noter for husets styring: **IHC** (controller
192.168.27.53, projektfil `TIB27_*.vis`) og **Home Assistant**, der bygger
Hue, UniFi, Daikin, markise m.m. ovenpå.

```
ha/config/        Home Assistant-konfigurationen, som den ligger i /homeassistant
ihc/tib27_ihc/    Python-værktøjer til .vis-filen: verify, dump, diff, blocks
ihc/project/      Her lægges projektfilerne (TIB27_*.vis) — se ihc/project/README.md
tools/check_ha.py Tjekker HA-konfigurationen mod husets regler
docs/             Fejlfinding og beslutninger, én fil pr. sag
```

## Faste regler

Disse er skrevet ind i tjekkene, så de ikke kan glide i stilhed.

| Regel | Håndhæves af |
|---|---|
| **Luxo Lampe i Køkken** (`light.kokken_3984477`) skal altid være tændt | `check_ha.py` — fejl |
| **Køleskabsstikket (Frostfri)** må aldrig slukkes | manuelt — IHC-siden |
| **Sluk Alt** skal nå hele huset; **Tænd Alt** kun stue/køkken/spisekarnap | manuelt — IHC-siden |
| De fire **markise**-flag (`_0x80c90a`, `_0x80ca0a`, `_0x80cb0a`, `_0x80cc0a`) må ikke ændres | manuelt — IHC-siden |
| **Hue-lamper** tændes altid med et niveau (ellers kan de arve 0 %) | `check_ha.py` — advarsel |
| **Ingen hemmeligheder i repoet** — heller ikke i udkommenterede linjer | `check_ha.py` — fejl |
| Et **tracker-udfald** må ikke tælle som gået eller kommet hjem (3 min) | `check_ha.py` — advarsel |
| Før upload til controlleren: **backup**, `verify`, og åbn filen i IHC Visual | arbejdsgang nedenfor |

## Kom i gang

```bash
pip install -e '.[dev]'
pytest                       # 26 tests: IHC-værktøjer og HA-regler
python tools/check_ha.py     # tjek HA-konfigurationen
```

## Ændre IHC-projektet

```bash
tib27-ihc blocks  ihc/project/TIB27_151.vis --grep spisekarnap
tib27-ihc dump    ihc/project/TIB27_151.vis "Billedlys over pigen følger spisekarnappen"
# … rediger med VisFile.replace_once / IdAllocator, gem som ny version …
tib27-ihc verify  ihc/project/TIB27_152.vis          # skal sige KLAR
tib27-ihc diff    ihc/project/TIB27_151.vis ihc/project/TIB27_152.vis
```

1. Tag backup af controlleren.
2. Læg den kørende version i `ihc/project/` og commit den, *før* der ændres noget.
3. Lav ændringen som en ny version. Rør aldrig filen med et værktøj der
   gemmer XML'en om — `VisFile` laver tekstkirurgi og bevarer CRLF og
   ISO-8859-1 byte for byte.
4. `verify` skal sige **KLAR**. `diff` skal kun vise de områder du ville ændre.
5. Åbn filen i IHC Visual og tjek den, før den uploades.
6. Commit med en besked der siger *hvorfor*.

`verify` fanger: ensidede link-par, døde referencer, scene-par der ikke
peger på hinanden, dublet-id'er, en `last_unique_id` der er lavere end et
id i brug, manglende operander, LF i stedet for CRLF, og filer der har
været gennem en UTF-8-konvertering (æ/ø/å erstattet med `�`).

## Ændre Home Assistant

Filerne i `ha/config/` er et øjebliksbillede af `/homeassistant`. Ændringer
laves i HA og hentes så hjem igen — se [ha/README.md](ha/README.md).

## Hemmeligheder

`configuration.yaml` i repoet bruger `!secret ihc_password`. Selve
værdien hører hjemme i HA's `secrets.yaml`, som **aldrig** committes —
se [ha/secrets.yaml.example](ha/secrets.yaml.example).

## Åbne punkter

- Den kørende `configuration.yaml` i HA har stadig IHC-passwordet i
  klartekst, og en udkommenteret `device_tracker`-blok med routerens
  root-password. Begge bør flyttes til `secrets.yaml` / fjernes, og
  routerens password bør skiftes.
- IHC-binærsensoren `stue_tryk_off_faelles` og lyset `Sluk_Alt_Fælles`
  har samme IHC-id (1439068) i `configuration.yaml`.
- Le Klint-pærerne i Bjørneværelset hedder stadig
  `light.extended_color_light_1` / `_1_2` — bør omdøbes.
- v151 er ikke uploadet til controlleren. v152 indeholder derfor også v148–151.
