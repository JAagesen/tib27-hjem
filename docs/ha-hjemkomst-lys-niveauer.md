# Hjemkomst-lys: mørke-betingelse og kontakt-niveauer — 30-10-2026

Opfølgning på [ha-bjornevaerelset-zone-dublet.md](ha-bjornevaerelset-zone-dublet.md).

## Hvad der skete

Fredag 09:58 tændte hele stuen og køkkenet midt på formiddagen. Lyset var
slukket korrekt (08:49 af "sidste mand forlader huset", og begge
09:00-automatiseringer kørte). Det blev tændt igen af *"Når vi kommer
hjem og Ella ikke er hjemme"* (`1762441290061`) da Jans telefon kom på
wifi.

Den manglede en mørke-betingelse. Det var aldrig blevet opdaget, fordi
Jans halvdel af triggeren (`device_tracker.jan_s_s22`) stod til
`to: "Home "`. Wifi-trackere melder kun `home`/`not_home`, så den kunne
aldrig fyre — kun `person.miv` virkede. Zone-oprydningen 29-10 rettede
strengen og gjorde den levende.

## Princip: samme niveau som kontakten

| Lampe | Hvad kontakten gør | Hvad HA gør |
|---|---|---|
| IHC-lamper (stue, køkken, spisekarnap) | Kip-dimmere tænder på **sidste niveau** (står i funktionsblokkene) | `light.turn_on` uden niveau — HA's IHC-integration bruger også sidste niveau, og 0 bliver til 100 % |
| Verner Panton (Hue, `light.stue`) | IHC-trykket sætter **30 %**, eller 5 % i TV-scenariet | Samme skabelon: `{{ 5 if states('sensor.stue_scenarie_status') \| trim == 'TV' else 30 }}` |
| Bjørneværelset (Hue) | IHC-trykket sætter **80 %** | 80 % |

Faste tal på IHC-lamperne ville glide fra kontakten, så snart en lampe
blev reguleret med sin kontakt. Nul-fælden findes kun på Hue-pærerne —
derfor tjekker [`tools/check_ha.py`](../tools/check_ha.py) at Hue-lamper
altid tændes med et niveau.

## Ændringer

**"Når vi kommer hjem og Ella ikke er hjemme"** (`1762441290061`):
- Ny betingelse: `binary_sensor.faelles_3963482` (Skumringsrelæ) = `on`.
- Områderne `living_room` og `kokken` er erstattet af en eksplicit liste
  over de 11 IHC-lamper som faktisk tændte, plus Verner med kontaktens
  skabelon. `light.store_stue_1007453` (Kombi dimmer ved Nøddehaven) er
  taget ud — det er en tasteenhed, ikke en lampe, og IHC slukkede den
  igen efter 3 sekunder.

**"Home Alone"** (`1735596209433`): samme princip — IHC-lamperne uden
niveau, Verner med kontaktens skabelon.

## Fast regel

- **`light.kokken_3984477` (Luxo Lampe i Køkken) skal altid være
  tændt.** Den må aldrig med i en sluk-liste. `tools/check_ha.py` fejler,
  hvis en automatisering slukker den.

## Bemærket

- `light.taend_alt` ("Tænd alt lys i stuen") findes i HA, men bruges ikke
  af noget. Ikke brugt, fordi IHC-programmet skelner mellem kort og langt
  tryk og pulsvarigheden fra HA ikke er afprøvet. Scriptet
  `all_lights_off` viser mønsteret for Sluk alt: off → 100 ms → on →
  100 ms → off.
