# Billedlyset over pigen følger spisekarnappen

Lavet 18-10-2026 (v149/v150), fejlrettet 19-10-2026 i
`TIB27_151_spisekarnap_status.vis`.

## Ønsket

Tændes lyset i spisekarnappen, skal billedlyset over pigen i stuen tændes
med — men kun når det er mørkt udenfor. Slukkes spisekarnappen igen, skal
billedlyset **kun** slukke hvis der ikke er andet lys tændt i stuen;
ellers bliver det stående og slukkes som normalt sammen med resten af
stuen.

## Funktionsblokken

**`Billedlys over pigen følger spisekarnappen`** (`_0x84a628`), Store Stue.

**Input**

| Input | Kilde |
|---|---|
| `Status Lys i Spisekarnap` (`_0x84a80f`) | `_0x7d490f` i *1.2.03.d. Trådløs dimmer (Spisekarnap)* |
| `Status Lys i Stue` (`_0x84ab0f`) | `_0x3b330f` i *Scenarie funktion Stor Stue* |
| `Skumring` (`_0x84dc11`) | `dataline_input _0x3c7a5a` på *Udenfor det frostfri* |
| `Lys: Røde lamper` (`_0x84ae11`) | light_indication `_0xe621d` |
| `Lys: Standerlampe` (`_0x84b111`) | light_indication `_0xf731d` |
| `Lys: Pladespiller` (`_0x84b411`) | light_indication `_0xf8a1d` |
| `Lys: Klaver` (`_0x84b711`) | light_indication `_0x191a1d` |

**Output** — to scener, begge kun på kanalen `Billedbelysning pige`
(`_0x3cb054`, scenes `_0x3cb549`): `Tænd billedlys over pigen`
(`_0x84bb4a`, 45 % / 2000 ms) og `Sluk billedlys over pigen`
(`_0x84be4a`, 0 % / 3000 ms).

**Program** — udløst af at `Status Lys i Spisekarnap` skifter:

```
Spisekarnappen er tændt?
  JA  -> Mørkt ude, og stuen kører hverken TV, Nat eller Fuldt lys?
                                       -> Fremkald "Tænd billedlys"
  NEJ -> Røde, stander, pladespiller og klaver alle OFF?
                                       -> Fremkald "Sluk billedlys"
```

## Fejlen i v150 og rettelsen i v151

**Symptom (19-10):** slukker man stuen og tænder derefter kun
spisekarnappen, tænder billedlyset ikke. Det virker kun hvis man først
slukker spisekarnappen på dens egen tast og så tænder igen.

**Årsag:** `Status Lys i Spisekarnap` blev udelukkende sat af
spisekarnap-blokkens tastprogrammer. Et stue-scenarie slukker
spisekarnappens lamper direkte gennem scenen, uden at røre tasterne — så
status blev **hængende på Tændt** mens lamperne var slukkede. Næste tryk
på tænd-tasten satte status til Tændt igen, hvilket ikke er en
tilstandsændring, og blokkens udløser fyrede aldrig. Omvejen (sluk på
tasten, tænd igen) skabte netop de to ændringer der manglede.

**Rettelse 1** — i spisekarnap-blokkens program `Lysindikering OFF`
(`_0xb561e`) tilføjet `action _0x84e0ca`: `Status Lys i Spisekarnap :=
Slukket`. Nu følger status lamperne, uanset hvad der slukkede dem.

**Rettelse 2** — i billedlys-blokken tilføjet `condition _0x84e2c9`:
`Status Lys i Stue <> Fuldt Lys`, så rengøringsscenariets 100 % ikke kan
blive trukket ned til 45 %.

**Blast radius tjekket.** `Status Lys i Spisekarnap` læses også af
*PIR styring Køkken*:

- Tændebetingelserne kræver `= Slukket`. Den fastlåste "Tændt" kunne
  altså **blokere køkken-PIR'en helt**. Rettelsen gør den korrekt.
- `Styrer nedtælling af PIR tid` udløses på `= Tændt`, ikke på Slukket —
  uberørt, men dens betingelse bliver nu sand/falsk efter virkeligheden.
- `Sluk`-programmet udløses af statusændringen, men dets eneste
  ubetingede handlinger er at standse og nulstille køkkenets efterløb.
  Alt der faktisk slukker lys ligger bag køkkenets egen sluk-tast. Samme
  behandling som `Status Lys i Stue` og `Status Lys i Køkken` allerede
  gav.

## Øvrige valg

**Tasten, ikke lampen.** Blokken udløses stadig af status-enummet, som
kun *tændes* af tasterne. Det var med vilje: havde tændegrenen lyttet på
lampernes tilbagemelding, ville Dag, TV, Nat og Fuldt lys også udløse
den, og Fuldt lys-scenen ville komme i kapløb med de 45 %.

**Slukningen er ikke betinget af mørke.** Mørket gælder kun tændingen.

**Verner tæller ikke med** som "andet lys i stuen" — Hue-lampe uden
tilbagemelding til IHC.

## Verifikation

v151: 11572 elementer (+4 mod v150), ingen dublet-id'er, alle 450
link-par og 236 scenarie-par gensidige, ingen døde referencer, CRLF
bevaret. Diff mod v150: 4 ændrede områder.
