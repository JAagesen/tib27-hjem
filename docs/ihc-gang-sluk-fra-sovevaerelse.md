# Ganglyset slukket fra soveværelset — v152, 1-11-2026

## Symptomer
1. Slukkes gangen fra soveværelset, tænder den nogle gange igen af sig selv.
2. Om dagen tager slukningen lang tid.

## Årsag
NAT-tasten (nederst højre) på begge 6-tast-tryk i soveværelset går til
PIR-blokkens indgang **Tryk NAT** — samme indgang som gangens og
hoveddørens NAT-tast.

1. Kort tryk spærrer PIR'en i **45 s** (`Spærring af PIR efter manuel sluk`).
   Når spærringen udløber, kører `PIR aktiveres` igen. Står PIR'en stadig på
   ON fra turen gennem gangen, tænder lyset. HA's historik viser netop sluk →
   tænd 45–50 s senere med PIR aktiv.
2. Om dagen bruges scenen `Sluk` (0 %, **10 s** rampe); kun i mørke `Sluk hurtigt` (1 s).

## Rettelse (kun soveværelset)
- Ny indgang **`Tryk NAT soveværelse`** (`_0x84e411`); linkene fra Mivs og
  Nalles NAT-tast er flyttet hertil. Gang og hoveddør er uændrede.
- Tryk og hold deler tryktimer med de andre NAT-taster, så langt tryk
  regulerer ned som før.
- Kort tryk slukker med ny scene **`Sluk straks (soveværelset)`**
  (`_0x84e54a`, 0 %, **200 ms**) både lyst og mørkt. Natdrift sættes stadig i mørke.
- Nyt flag **`Vent på ny bevægelse`** (`_0x84e80a`): sættes ved sluk fra
  soveværelset hvis PIR står på ON. `PIR aktiveres` kræver flaget OFF; nyt
  program `PIR i ro: frigiv …` rydder det, når PIR går til OFF. En PIR der
  blot hænger, kan ikke tænde igen — en ny bevægelse kan.

Rampetiden ændres i scenen `Sluk straks (soveværelset)` (0 ms = helt uden rampe).

## Verifikation
`verify`: KLAR. 11617 elementer (+45), 9 ændrede områder i diff mod v151,
CRLF bevaret, ingen erstattede tegn. `ihc/changes/build152.py` genskaber
filen byte for byte fra v151.

## Afprøvning efter upload
1. Om dagen: tryk kort NAT i soveværelset → gangen slukker straks.
2. Gå gennem gangen, ind i soveværelset, sluk med det samme → gangen må ikke
   tænde igen efter ~45 s.
3. Gå ud i gangen igen (efter PIR'en har været i ro) → lyset tænder.
4. NAT-tasten i gangen og ved hoveddøren: uændret (1 s / 10 s rampe).
