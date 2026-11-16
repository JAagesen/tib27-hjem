# Ny LED-dimmer i gangen — v153, 15-11-2026

Kombidimmeren i gangen ("Kombi dimmer 4 tast", I det Magiske skab) skiftes til en
**LK IHC LED Dimmer 2 kanaler** (RS485), samme type som den i det frostfri
(køkken / hyttehaven), men en ny enhed.

## Fase 1 — oprettet (v153)
Den nye dimmer ligger i "Entre og Gang" lige under kombidimmeren. Kanal 1,
"LED Dimmer Loftslys gang", har fået alt fra kombidimmerens dimmer-del:

- Indstillinger: min 5 %, max 100 %, fade op 5000 ms, fade ned 10000 ms,
  reguleringstid 10000 ms. (Load mode "rc" findes ikke på LED-dimmeren.)
- Alle 14 scenarier med samme niveau og rampe: Kombidimmer (dag&Nat) ×3,
  PIR-styringen i gangen ×10, Sluk Alt ×1. Hver scene har nu to scenarie-links,
  ét til hver dimmer.
- Lys niveau → PIR-styringens input "Lys niveau".
- Lys indikering → Kombidimmer-blokkens input "Lys indikering".

Kanal 2 er oprettet ledig. Serienummeret er tomt. `channel_id` er sat til
`_0x82`/`_0x83`, fordi frostfri-enheden bruger `_0x80`/`_0x81`.

Den gamle kombidimmer er urørt. Indtil den slettes, styres begge parallelt.

`verify`: KLAR. 18 ændrede områder i diff mod v152.
`ihc/changes/build153.py` genskaber filen fra v152.

## Fase 2 — når den nye er tilsluttet
1. Indtast serienummeret i IHC Visual (det står på enheden, "PL…").
2. Slet kombidimmeren. Dens scenarie-links og links forsvinder med den;
   den nye dimmers links bliver.
3. Kombidimmerens fire tryk forsvinder med den. Det er bevidst: de skal
   ikke erstattes, for gangen styres allerede fra rigeligt med andre tryk
   (Jan, 15-11-2026).

## Kombidimmeren ude af drift — v154, 16-11-2026
Kombidimmeren er ikke slettet, men alle dens forbindelser er fjernet: 14
scenarie-par, Lys niveau, Lys indikering og de fire tryk. Noten siger
"UDE AF DRIFT". Den nye LED-dimmer har stadig alle 14 scenarier og begge links.
Kombidimmer-blokkens input "Reguler scenarie op" har nu intet tryk. Det kom
kun fra kombidimmeren. De andre input har stadig deres øvrige tryk.

`verify`: KLAR. `ihc/changes/build154.py` genskaber filen fra v153.
Slettes kombidimmeren senere i IHC Visual, ændrer det intet funktionelt.
