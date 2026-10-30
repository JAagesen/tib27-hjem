# Projektfiler

Læg IHC Visual-projektfilerne her som `TIB27_<nr>_<kort_beskrivelse>.vis`,
fx `TIB27_151_spisekarnap_status.vis`.

- Brug den **originale** fil fra IHC Visual eller controlleren. En fil der
  har været åbnet og gemt i et almindeligt tekstprogram, sendt som tekst
  eller konverteret til UTF-8, har mistet æ/ø/å — `verify` melder det
  som `encoding`-fejl.
- `.gitattributes` gør `*.vis` binær for git, så CRLF aldrig konverteres.
- Commit den kørende version, *før* du ændrer i den. Så er git-historikken
  også din backup.

## Versioner

| Version | Hvad |
|---|---|
| 147 | Udgangspunkt 18-10-2026 |
| 148 | Fuldt lys (rengøring) når også gangen — [docs](../../docs/ihc-fuldt-lys-rengoering.md) |
| 149 | Billedlys over pigen følger spisekarnappen |
| 150 | … kun når det er mørkt |
| 151 | `Status Lys i Spisekarnap` følger lamperne; ikke under Fuldt lys — [docs](../../docs/ihc-billedlys-pige-spisekarnap.md) |
