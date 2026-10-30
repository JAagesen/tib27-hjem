# Home Assistant kørte i knæ — recorder-oprydning 18-10-2026

## Symptomer

Søndag aften 18-10 var HA reelt uanvendelig: websocket afbrudt (frontenden
viste frosne data og "Loading…"), REST-API 7 sekunder om at svare, derefter
timeout efter 45 s. Terminal-tillægget rendererede sort, dashboardsider
timede ud, og kernen var genstartet af sig selv kort forinden.

Det blev først fejlagtigt tolket som problemer med ttyd og med
Lovelace-siderne. Det var HA selv.

## Målinger før

| | |
|---|---|
| RAM | 1886 MB, 421 MB ledig |
| Swap | 1023 MB, **533 MB i brug** |
| Load (1/5/15 min) | 0,10 / 0,24 / 0,26 — toppen var overstået |
| Oppetid host | 13 dage (ingen reboot) |
| Disk | 13,8 GB af 458 GB — ikke problemet |
| `home-assistant_v2.db` | **1,1 GB** |

## Årsag

Der var **ingen `recorder:`-sektion** i `configuration.yaml`. HA kørte
altså på standard: gem alt, i 10 dage. Med 973 entiteter — heraf 52
`*_rx`, 52 `*_tx` og 27 `*_uptime` fra UniFi, som opdaterer med få
sekunders mellemrum — voksede databasen til 1,1 GB. På en 2 GB-maskine
sender recorderens oprydning i en fil af den størrelse systemet i swap,
og så falder websocket ud og API'et kryber.

## Rettelsen

Indsat i `configuration.yaml` foran `ihc:`:

```yaml
recorder:
  purge_keep_days: 7
  commit_interval: 10
  exclude:
    entity_globs:
      - sensor.*_rx
      - sensor.*_tx
      - sensor.*_uptime
```

131 støjsendere holdes ude. Device trackers (82) og router-belastning
beholdes, så historikken på hvem der er hjemme er intakt.

## Resultat efter genstart

| | Før | Efter |
|---|---|---|
| API-svartid | 7000 ms | **18 ms** |
| Websocket | afbrudt | **forbundet** |
| IHC-entiteter | — | **85, 0 utilgængelige** |
| Swap i brug | 533 MB | 449 MB |

`recorder.purge` med `repack: true` blev accepteret (HTTP 200).
Pr. 30-10 er `home-assistant_v2.db` på 844 MB.

## IHC debug-logning slået fra — 19-10-2026

`logger:`-sektionen stod med fuld debug på IHC (`homeassistant.components.ihc`
og `ihcsdk` på `debug`). `ihcsdk: debug` logger hvert eneste IHC-telegram.
Det var en fejl, ikke noget der var sat med vilje. Sektionen er nu kun:

```yaml
logger:
  default: warning
```

Niveauet blev sat live uden genstart med `logger.set_level`. Skal debug
tilbage midlertidigt, så brug `logger.set_level` fra Udviklerværktøjer i
stedet for `configuration.yaml` — så forsvinder det igen ved næste genstart.

## Åbent

- **Gamle logfiler**: `home-assistant.log.old` (ca. 390 MB, nov. 2025),
  `.log.1` og `.log.fault`. Ren diskplads.

## Noter

- ttyd-sessionen hænger jævnligt og dropper tastetryk. Browserens
  `javascript_tool` mod HA-frontenden er en langt mere pålidelig vej:
  `document.querySelector('home-assistant').hass` giver både states og
  adgangstoken til REST-kald.
- Websocket-kald (`hass.callWS`) fejler med tallet `3`
  (ERR_CONNECTION_LOST) når HA er presset — et godt hurtigt sundhedstegn.
- zsh's url-quote-magic ødelægger `curl` med JSON og URL i samme linje.
  Brug Python i stedet.
