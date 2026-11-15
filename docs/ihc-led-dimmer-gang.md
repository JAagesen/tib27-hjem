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
3. **Kombidimmerens fire tryk forsvinder også.** De sender i dag til
   Kombidimmer-blokken (op/ned) og PIR-styringen (Tryk DAG / Tryk NAT).
   Skal de bevares, kræver det et nyt tryk, som kobles til de samme input.
