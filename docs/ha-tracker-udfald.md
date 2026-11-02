# Et kort tracker-udfald slukkede hele huset — 2-11-2026

## Hvad der skete
Kl. 07:54 slukkede *"Når sidste mand forlader huset – sluk lyset hvis det er dag"*
alt lys (script `all_lights_off` = IHC Sluk alt). Jans wifi-tracker
(`device_tracker.jan_s_s22`) forsvandt og kom tilbage inden for samme minut.
Miv var gået 07:34, og det var lyst (Skumringsrelæ OFF siden 07:25), så alle
betingelser var opfyldt. GPS-trackeren og `person.jan_bjerre_aagesen` stod hele
tiden på `home`.

## Princip
Et udfald på en tracker må hverken tælle som *gået* eller *kommet hjem*.

| Situation | Regel |
|---|---|
| Gået | trigger `to: not_home` med `for: 3 min`, og betingelser `not_home` i mindst 3 min |
| Jan gået | både wifi (`jan_s_s22`) **og** GPS (`jan_s_cell_phone`) skal være `not_home` — begge er også triggere, så det fyrer når den sidste af dem er enig |
| Miv gået | kun wifi (`mivs_s22`) findes — 3 min ventetid |
| Kommet hjem | betingelse: væk i mindst 3 min før hjemkomsten |

```yaml
- condition: template
  value_template: >
    {{ trigger.from_state is not none and
       (trigger.to_state.last_changed - trigger.from_state.last_changed).total_seconds() >= 180 }}
```

Bemærk: den 29-10 fik Bjørneværelset-hjemkomst `for: 2 min` på `home`. Det
stopper **ikke** et udfald — telefonen står jo stabilt på `home` efter blinket.
Det er erstattet af fraværskravet ovenfor.

## Rettet
| Automatisering | Ændring |
|---|---|
| Når sidste mand forlader huset | 3 min på alle tre triggere, + GPS-trigger og -betingelse |
| Sluk lys i Bjørneværelset, når jeg forlader hjemmet | 3 min, wifi + GPS (og den døde `Home`-værdi er væk) |
| Lights out at 9 if no ones at home | 3 min på betingelserne, + GPS |
| Home Alone | 3 min på betingelserne, + GPS |
| Når vi begge kommer hjem og det er mørkt | 3 min på betingelserne, + wifi |
| When I come home turn on light in Bjørneværelse | fraværskrav i stedet for 2 min hold |
| Når vi kommer hjem og Ella ikke er hjemme | fraværskrav |

Ikke rørt: *Ella Away*, *Ella coming home*, *Når Miv kommer hjem* og *When Nalle
gets home* — de har ingen handlinger.

`tools/check_ha.py` advarer nu om tracker-triggere uden disse regler.
