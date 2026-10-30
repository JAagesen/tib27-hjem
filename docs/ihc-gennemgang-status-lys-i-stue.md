# Gennemgang før scenarie 1: "Status Lys i Stue" skal følge dæmperne

Analyse af **TIB27_139**. Ingen ændringer lavet i projektfilen —
alt nedenfor er læst ud af filen med ElementTree og efterprøvet med betingelses-simulatoren.

---

## 1. Hvad er løgnen, helt præcist

Blokken **Scenarie funktion Stor Stue** har en udgang `Status Lys i Stue` (`_0x3b330f`,
enum: TV / Fuldt Lys / Dag / Nat / Slukket). Den skrives 8 steder — alle inde i blokken selv:

| Program | Sætter status til |
|---|---|
| `Dag` | Dag |
| `Nat` | Nat |
| `TV` | TV |
| `Fuldt lys` | Fuldt Lys |
| `Reguler op slippes` → «Kalder sidste niveau» | Dag |
| `Reguler op slippes` → «Kalder niveau oprettet i link» | Dag |
| `Touch slippes` → «Sluk» | Slukket |
| `Lysindikering OFF` | Slukket |

Asymmetrien er hele problemet:

```
Lysindikering OFF  (Lys indikering -> OFF)   ... sætter Status Lys i Stue := Slukket
Lysindikering ON   (Lys indikering -> ON)    ... sætter INGEN status
```

Lyset må altså godt slukke sig selv ud af statussen, men det kan ikke tænde sig ind i den.
`Lys indikering` er fælles for alle fem stuedæmpere (3 × Mobil stikkontakt, 2 × Lampeudtag),
så signalet betyder præcis "mindst én stuelampe er tændt" — det er et sandt signal.
Det er kun statussen der ikke følger med.

### De seks veje hvor status kommer til at lyve

| # | Udløser | Hyppighed | Skal rettes? |
|---|---|---|---|
| 1 | Kombi dimmer 4-tast, **nederst højre** → lampe over pladespiller (blok `Tænd/sluk lampe over pladespiller`) | dagligt | **ja** |
| 2 | Fjernbetjening **Tryk 7** → strikkelys, røde lamper på 100 % (blok `Tænder/Slukker Røde lamper over Sofa`) | ofte | **ja** |
| 3 | Langt tryk / touch-tænd i selve scenarieblokken (`Regulering ved langt tryk` «Scenarie op», `Touch slippes` «Kalder sidste niveau» / «Kalder niveau oprettet i link») — de sætter `Lys indikering := ON` men ingen status | ofte | **ja** |
| 4 | **Køkken-PIR'ens `Scenarie tænd`** tænder 4 stuelamper på 2–20 % om natten | hver nat | **NEJ — skal blive ved at lyve** |
| 5 | `Power ON` kalder `Fremkald Nat` (scenariet) uden at skrive status | ved strømsvigt | ja, men særskilt |
| 6 | HA / IHC-API / Captain Pi sætter en dæmper direkte | nu og da | **ja** |

Punkt 1–3 er fysiske kontakter der bruges hver dag. Det er dem der giver symptomet.

### Hvorfor gangen hænger på Mellem

Gangblokken bruger **to forskellige signaler** til samme spørgsmål:

* `Status Lys i Stue` (scenarie-enum) vælger **stigen** → `PIR funktion`
* `Lys i Stue` (dæmpernes `Lys indikering`) er **portvagt på nedtrapningen** i `Efterløb udløber`

Når de to er uenige, findes der ingen gren. Simuleret (status = Slukket, lamper tændt,
`PIR funktion = Trin høj/mellem/+ekstra efterløb`):

```
gang = Høj     -> Mellem Niveau, efterløb startet      (ser normalt ud)
gang = Mellem  -> *** ingen gren, ingen ny nedtælling ***
gang = Lav     -> *** ingen gren ***
```

Gangen står på Mellem for evigt, uden kørende timer.

Med sand status (= Dag, `PIR funktion = Trin høj/mellem`) rammer den
«Tænder lys på højt niveau og går til mellem uden sluk», som holder på Mellem **og
genstarter efterløbet** — altså et bevidst hold i stedet for et dødvande. Og når
stuelyset så slukkes, skifter status til Slukket, `Sæt Ganglys…` slår om til
`Trin høj/mellem/+ekstra efterløb`, og stigen kører Mellem → Lav → Sluk som den skal.

### Den omvendte løgn er også et dødvande

Hvis status siger Dag/TV/Nat mens lamperne er slukkede, har `Efterløb udløber`
**ingen gren i nogen kombination** (testet: 3 statusser × 3 gangniveauer = 9/9 dødvande).
Den tilstand kan nås efter et strømsvigt om dagen, hvor `Power ON` ikke skriver noget
og statussen er `backup="yes"` og derfor husker sin gamle værdi.

---

## 2. Hvem læser de tre statusser

| Udgang | Læses af |
|---|---|
| `Status Lys i Stue` `_0x3b330f` | Entre og Gang > `Styring af PIR i gang…`<br>Køkken > `PIR styring Køkken…`<br>Fælles > `Sluk kontrol (Køkken, Spisekarnap, Stue)` |
| `Status Lys i Spisekarnap` `_0x7d3f0f` | kun Køkken > `PIR styring Køkken…` |
| `Status Lys i Køkken` `_0x7d400f` | kun Køkken > `PIR styring Køkken…` |

Scenarie 1 rører **kun** `Status Lys i Stue`. Køkken- og spisekarnap-statusserne står
urørt, så de to blokke der henter dem andetsteds (`Styring af Lys i Køkken`,
`1.2.03.d. Trådløs dimmer (Spisekarnap)`) er helt uden for skudlinjen.

### Hvad ændrer sig i køkkenet

`PIR styring Køkken` bruger `Status Lys i Stue` fire steder — alle som krav om
`= Slukket` før PIR'en må tænde, plus programmet
`Styrer nedtælling af PIR tid, hvis lys tændes automatisk` der trigger på statusskift:

```
status ≠ Slukket  ->  Stands tælling på Efterløb, Efterløb := Initialværdi   (hold tændt)
alle tre Slukket  ->  Efterløb := 0                                          (sluk straks)
```

Simuleret, køkken-PIR udløses i mørke:

```
Status Lys i Stue = Slukket  ->  Udgang ON, Scenarie tænd        (tænder)
Status Lys i Stue = Dag      ->  ingen gren                      (tænder ikke)
Status Lys i Stue = TV       ->  ingen gren                      (tænder ikke)
Status Lys i Stue = Nat      ->  ingen gren                      (tænder ikke)
```

Det er blokkens egen hensigt — den hedder jo "…og når lys i Stue er slukket". I dag
*omgås* hensigten hver gang stuelyset tændes uden et scenarietryk. Scenarie 1 får
altså køkkenet til at opføre sig som designet. Det er en forbedring, men det er en
synlig adfærdsændring: tændt stuelys → ingen PIR-lys under overskabene.

### Sluk-vagthunden

`Sluk kontrol` trigger på **ethvert** skift af `Status Lys i Stue`: til Slukket starter
den kontrol-timeren, til alt andet **stopper den begge timere**. Ny skrivning til
statussen kan derfor afbryde en igangværende Sluk Alt-kontrol. Sandsynligheden er lav
(`Sluk alle` kører lamperne *ned*, så `Lys indikering` går OFF, ikke ON), men det er den
ene nye risiko scenarie 1 introducerer, og vagten "kun hvis status er Slukket" dækker
den ikke — under Sluk Alt-vinduet *er* status Slukket.

---

## 3. Den vigtigste konstatering: scenarie 1 i sin simple form er farlig

Køkken-PIR'ens `Scenarie tænd` tænder fire af de fem stuedæmpere:

| Dæmper | Niveau i `Scenarie tænd` |
|---|---|
| Lampeudtag (pladespiller) `_0xf8654` | 8 % |
| Mobil stikkontakt `_0xf6f54` | 2 % |
| Lampeudtag (klaver) `_0x191654` | 20 % |
| Mobil stikkontakt (pige) `_0x3cb054` | 20 % |

Det hæver `Lys indikering` → `Lysindikering ON` fyrer. Hvis det program skriver
`Status Lys i Stue := Dag`, sker følgende kl. 03 når man går ud i køkkenet (alle fire trin
simuleret):

1. Køkkenblokkens `Styrer nedtælling…` ser status ≠ Slukket → **stopper køkkenets efterløb**
   → køkkenlys og de fire stuelamper slukker aldrig af sig selv.
2. Gangens `Sæt dagdrift når stuelyset tændes` → **Natdrift := OFF, Afventer nat := OFF**.
3. Gangens `Sæt Ganglys i forhold til lys i stue` → `PIR funktion := Trin høj/mellem` og
   **`Fremkald Højt niveau` med det samme** — fuldt gangly kl. 03.
4. Næste PIR i gangen rammer «Højt niveau (Natdrift inaktiv)» → Høj igen.

Vagten "kun hvis status er Slukket" hjælper ikke: kl. 03 *er* status Slukket.
Niveauerne hjælper heller ikke — køkkenets natscenarie (2–20 %) overlapper både
TV (5–20 %) og Nat (2–19 %), så en lysniveau-tærskel kan ikke skille dem.

---

## 4. Forslaget — scenarie 1 med køkkenvagt

**Ændring A (kernen).** I `Lysindikering ON`, pak den nye skrivning i et underprogram:

```
IF   Status Lys i Stue  =  Slukket          (overskriver ikke TV / Nat / Fuldt Lys / Dag)
AND  Køkken-PIR Udgang  =  OFF              (køkkenets natscenarie tæller ikke som "lys i stuen")
THEN Status Lys i Stue := Dag
```

Kræver en ny indgang på `Scenarie funktion Stor Stue`, linket fra
`PIR styring Køkken…` > Output > `Udgang` (`_0x52f512`). Rækkefølgen passer: køkkenblokken
sætter `Udgang := ON` *før* `Fremkald Scenarie tænd`, så vagten er oppe inden dæmperne
melder tilbage.

Rækkefølge-risikoen ved scenarietasterne er nul: scenarieprogrammet (`TV`, `Nat`, …) kører
til ende — inklusive sin statusskrivning — før dæmpernes tilbagemelding behandles. Og selv
i omvendt rækkefølge ender værdien på scenariets egen, fordi den skrives sidst.

**Ændring B (anbefalet, lille).** `Power ON` kalder i dag `Fremkald Nat` uden status.
Lad begge grene skrive:

* natgrenen: `Status Lys i Stue := Nat`, Spisekarnap := Tændt, Køkken := Tændt (altså det
  `Nat`-programmet gør)
* daggrenen: `Status Lys i Stue := Slukket`

Så er statussen sand efter et strømsvigt, `Lysindikering ON` springer over (status ≠ Slukket),
og den omvendte løgn i afsnit 1 kan ikke længere nås.

**Ændring C (anbefalet).** `Sæt Ganglys i forhold til lys i stue` har en skævhed der først
bliver synlig når statussen begynder at sige sandheden. TV/Nat-grenen spørger om PIR'en:

```
TV / Nat   -> «Sætter lys i forhold til PIR»:  PIR ON -> Mellem,  PIR OFF -> Lav
Dag / Fuldt Lys -> ingen PIR-test:             Fremkald Højt niveau, altid
```

Dag-grenen tænder altså gangen på **Høj uden at spørge om nogen er der, og uden
skumringstest** — simuleret med `Skumring = OFF` midt på dagen: `Fremkald Højt niveau`.
I dag opdager man det sjældent, fordi statussen kun skifter når man trykker på en
scenarietast (og så står man typisk i stuen). Efter ændring A vil et tryk på
pladespiller-tasten eller strikkelyset kl. 12 tænde gangen på Høj med det samme.

Ønsket var *"gangen der skal gå på høj, når der tændes i stuen **og piren er aktiveret**"*.
Forslaget er derfor at give Dag-grenen samme PIR-test som TV/Nat-grenen har: sæt altid
`PIR funktion := Trin høj/mellem`, men tænd kun Høj hvis PIR'en er aktiv (eller gangen
allerede er tændt).

Ændring A og C hænger sammen: A uden C giver et nyt irritationsmoment om dagen.

### Hvad der ikke rettes af dette

* Køkken-PIR'en tænder fortsat fire stuelamper om natten. Hvis natlyset hellere *kun*
  skal være under overskabene, bliver vagten i ændring A unødvendig og hele rettelsen
  enklere. Det er et selvstændigt valg.
* Vagthunde-vinduet i `Sluk kontrol` (afsnit 2) står åbent. Kan lukkes med en kort
  blokeringstimer, hvis det er værd at bygge.

### Prøvetrykket inden upload

1. Backup af controlleren.
2. Åbn og tjek projektet i IHC Visual før upload.
3. Test i denne rækkefølge: pladespiller-tasten (dag) → gangen skal køre Høj → hold på
   Mellem; strikkelys → samme; TV-tast → Verner på 5 %, gang på Lav; **køkken kl. 03 →
   gangen skal *blive* i nat, og køkkenlyset skal slukke efter sit efterløb**; Sluk Alt →
   alt skal gå ud.

Punkt 4 er den der afgør om vagten virker.
