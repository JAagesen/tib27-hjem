# Lyset i Bjørneværelset tændte af sig selv på 0 % — 29-10-2026

## Symptom

Torsdag aften stod begge Le Klint-pærer i Bjørneværelset tændt på
**brightness 0 af 255 (0 %)** i varm rav-tone — et næsten usynligt skær.
Ingen havde tændt dem.

## Hvad der skete

Automatiseringen *"Når Nalle kommer hjem, tænd lyset i Bjørneværelset"*
(id `1736323342801`) udløste kl. 19:04:40 og igen 19:58:41.

Triggeren var `device_tracker.jan_s_cell_phone` fra `not_home` til
`Home`. Men ingen kom hjem — telefonen blinkede:

```
19:04:39  not_home
19:04:39  Home      ← samme sekund, automatiseringen fyrer
19:05:29  not_home
19:58:41  Home      ← fyrede igen
```

Trackeren skiftede tilstand 13 gange den dag. Ren GPS-jitter.

## To selvstændige årsager

### 1. Nøgen `light.turn_on` uden niveau

En Hue-pære vender tilbage til sit sidst huskede niveau når man ikke
angiver et. Niveauet lå i bund, så den tændte på 0 %.

Den mest sandsynlige kilde til bundniveauet er *"Bjoernevaerelset - Hue
regulering ned"*, som dæmpede i spring på `-16 %`. Fra de 80 % som
IHC-trykket tænder med er det præcis fem tryk til 0 — og HA's
trinregulering stopper ved 0 **uden at slukke pæren**.

### 2. To hjemmezoner

| Zone | Navn | Radius | Kilde |
|---|---|---|---|
| `zone.home` | TIB27 | 85 m | kernekonfiguration (den rigtige) |
| `zone.home_2` | `Home ` (med mellemrum til sidst) | 74,7 m | oprettet i UI'en, lagret under id `home` |

Samme punkt — 0,8 m fra hinanden — men dubletten var mindre. HA vælger
altid den **mindste** zone der dækker punktet, så telefonerne meldte
`Home ` i stedet for `home`. Det gav konstante falske tilstandsskift, og
seks automatiseringer var skrevet til at tage højde for begge stavemåder.

## Trackerne — hvad der faktisk er hvad

| Entitet | Integration | Enhed |
|---|---|---|
| `device_tracker.jan_s_s22` | UniFi (wifi) | Jans S22+ |
| `device_tracker.jan_s_cell_phone` | mobile_app (GPS) | **samme** S22+ |
| `device_tracker.sm_x906b` | mobile_app (GPS) | Samsung Tab S8 |
| `device_tracker.sealnb215` | UniFi (wifi) | SEAL-laptop |
| `device_tracker.jan_s_x1` | UniFi (wifi) | X1-laptop |
| `device_tracker.ella_tracker` | Tractive (GPS) | Ella — hunden |
| `device_tracker.mivs_s22` | UniFi (wifi) | Mivs S22+ |

Wifi-trackere melder **kun** `home`/`not_home`, aldrig et zonenavn.

`person.jan_bjerre_aagesen` samler X1, Tab S8, SEAL-laptop og
telefon-appen. **Den duer ikke som trigger for hjemkomst**: en person er
`home` så snart én enhed er hjemme, og laptop og tablet bliver tit
hjemme. Derfor lytter hjemkomst-automatiseringen på telefonens to trackere.

## Rettelserne

- **Automatiseringen** `1736323342801`: trigger på begge telefon-trackere,
  `not_home` → `home` holdt i 2 minutter; tænder på `brightness_pct: 80`
  med `transition: 1` (samme som IHC-trykket).
- **"Home Alone"** havde samme nøgne `light.turn_on` — rettet (se
  [ha-hjemkomst-lys-niveauer.md](ha-hjemkomst-lys-niveauer.md)).
- **"Bjoernevaerelset - Hue regulering ned"** (`hue_ihc_bjorn_ned`) har en
  bund på 10 % og kører kun når lyset er tændt.
- **Zonen** `zone.home_2` slettet. Seks automatiseringer fik `"Home "`
  erstattet med `home`.
- Pærerne blev slukket og tændt igen på 80 %, så det huskede niveau er rigtigt.

Fragmenterne fra før ændringen ligger i [backups/ha-backup-20261029.txt](backups/ha-backup-20261029.txt).

## Åbent

- **Natrisiko**: wifi-trackeren kan melde `not_home` hvis telefonen taber
  wifi i søvne og `home` igen når den vågner. Med Skumringsrelæet tændt
  går lyset så på 80 % om natten. To minutters hold dæmper det; en
  tidsbetingelse ville lukke det helt.
