# Fuldt lys (rengøring) — hvad scenariet dækker

Status 18-10-2026. Hører sammen med [ihc-gennemgang-status-lys-i-stue.md](ihc-gennemgang-status-lys-i-stue.md).

## Hvad der var galt

Scenariet `Fuldt lys (Sætter al lys til fuld)` (`_0x11fc4a`, output fra
*Scenarie funktion Stor Stue*) havde 10 medlemmer:

| Lampe | Før |
|---|---|
| Røde lamper over sofa, standerlampe, pladespiller, klaver, pige | 100 % |
| Køkken PH-lamper + Køkken (relæ) | 100 % |
| Spisekarnap over bord, over Morten Nielsen | 100 % |
| LED under overskabe | 100 % |
| Spisekarnap "Væg mod sø" | **98 %** |
| Gangen | **ikke med** |
| Verner | **30 %** |

Gangen fik 35 % fra PIR-blokkens `Højt niveau` og trappede selv ned til
10 % (Mellem) efter efterløbet. Verner er en Hue-lampe og kan derfor
ikke være med i en IHC-scene — han styres fra Home Assistant.

De fire dæmperudgange uden scener (Luxo over vindue, Højre/Venstre for
vindue mod sø, Ved udgang til Nøddehaven) har **nul forbindelser** på
selve dæmpeudgangen. Det er tryktangenter hvor dæmperdelen ikke er i
brug — ingen glemt lampe.

## Hvad der blev lavet (TIB27_148_fuldt_lys_gang.vis)

- `Væg mod sø` rettet 98 → 100 %.
- Ny scene i gangblokken: **`Fuldt lys (100 %)`** (`_0x84894a`) →
  gangdæmperen "I det Magiske skab" på 100 %, rampe 1000 ms.
- Nyt internt flag **`Fuldt lys aktivt`** (`_0x848c0a`).
- `Sæt Ganglys i forhold til lys i stue`: flaget ryddes forrest i
  programmet; i grenen "hverken TV eller Nat" skelnes nu på
  `Status Lys i Stue = Fuldt Lys` → flag ON, `Fremkald Fuldt lys (100 %)`,
  `Lysdæmper status := Høj`, efterløbet standses og nulstilles.
  Alle andre scenarier kører den normale optrapning til 35 %.
- `PIR aktiveres`: mens flaget er ON holdes 100 % — en PIR-udløsning
  dæmper ikke ned til `Højt niveau`.
- `Efterløb starter`: spærret mens flaget er ON, så intet trapper ned.

Hvorfor ikke bare lægge gangen ind i stuens Fuldt lys-scene: gangblokkens
vagthund (`Status`) slukker lampen igen, hvis `Lysdæmper status` siger
Slukket mens `Lys niveau > 4` — og `Sæt Ganglys …` ville samtidig kalde
`Højt niveau`. De to ville kappes om dæmperen.

Verifikation: 11510 elementer, ingen dublet-id'er, alle 436 link-par og
232 scenarie-par gensidige, ingen døde referencer, CRLF bevaret, 11
ændrede områder i diff mod v147.

## Home Assistant (lavet og genindlæst 17-10-2026)

- Ny automation **`hue_ihc_verner_fuldt_lys`**: `sensor.stue_scenarie_status`
  → `Fuldt Lys` sætter `light.stue` (Verner) på 100 %. Forlades scenariet
  igen, går han tilbage til 30 % — undtagen ved skift til `TV` eller
  `Slukket`, som har deres egne automationer.
- `hue_ihc_verner_tv`: tv_fra-skabelonen udvidet, så den ikke sætter 30 %
  når scenariet skifter til `Fuldt Lys` (ellers kappedes de to).
- Backup: `/homeassistant/automations.yaml.bak-20261017`. 39 → 40
  automationer. Genindlæst med `automation.reload` — ingen genstart.

## Hue-entiteterne — rettelse af en tidligere fejlantagelse

`light.stue` er **ikke** en pære. Det er en Hue-**rumgruppe** ved navn
"Stue" (model `Room`), og den indeholder præcis én lampe:
`light.verner_panton` (model `Color temperature light`). De to er altså
ikke dubletter — begge skal blive, og automationerne styrer med rette
gruppen. Det bekræfter også at 100 %-automationen kun rammer Verner.

`light.extended_color_light_1` og `light.extended_color_light_1_2` er de
to Le Klint-pærer i Bjørneværelset ("Le Klint Bjørn 1" og "2") — aktive
og i brug. De har bare auto-genererede entity-id'er; dér er rettelsen at
omdøbe, ikke slette. **Står stadig åben.**

## Entitets-oprydning — gennemført 18-10-2026

Udgangspunkt: 1977 registrerede entiteter, 919 deaktiverede (HA's egne
diagnostiske entiteter, normalt). **86 var "Not provided"** — registret
havde dem, men integrationen leverede dem ikke længere — og ingen af dem
var nævnt i automationer, scripts, scener eller dashboards:

- **85 fra UniFi**: 52 rx/tx-båndbreddesensorer og 25 device_trackere for
  gamle klienter, 6 blokeringskontakter (`switch.hannibal_s_22`,
  `switch.kristoffer_s_tab_s10_fe`, `switch.lba_le_njan`,
  `switch.lene_bjerres_galaxy_s10_lite`, `switch.tib27_tv_net`,
  `switch.usw_1_magiske_skab`), `button.iw_hd_restart`, `update.iw_hd`
- **1 fra Roborock**: `select.zucker_mop_mode`

HA's eget "Not provided"-filter gav præcis de samme 86, uafhængigt af min
egen optælling. Jan fjernede dem fra Indstillinger → Enheder & tjenester
→ Entiteter. Efterkontrol samme sted: filteret giver nu **0 entiteter**.

De tre `light.light_*` i Bryggers ("Le Klint Lampe 1" og "2" + en
TRADFRI Driver 30W, alle via Matter) blev bevidst **ikke** rørt:
Matter-integrationen kører, og 15 af dens enheder er offline. De kommer
igen af sig selv hvis enhederne tændes. Skal de væk permanent, er det
enhederne der skal fjernes fra Matter — ikke entiteterne.

Ingen `tradfri`-entiteter tilbage overhovedet.
