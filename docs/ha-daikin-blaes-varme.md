# Daikin Stue: kun blæs over 24 °C, varme under 24 °C — 20-11-2026

## Før
To automationer med device-triggere:
- "Daiken Fan Only above 25" — kun blæs når temperaturen krydsede **over 26 °C**.
- "Set Heat on when below 24" — varme når den krydsede **under 25 °C**.

Grænserne passede ikke med 24 °C, og de reagerede kun i selve krydsningen,
så efter udfald (Daikin offline 19-11 kl. 14:48), HA-genstart eller hvis
den var slukket, kunne den hænge i "kun blæs".

## Nu
Én automation, `daikin_stue_blaes_varme_24`:
- Over 24 °C i 5 min og står på varme → kun blæs.
- Under 24 °C i 5 min og står på kun blæs → varme.
- Præcis 24 °C → ingen ændring (naturlig hysterese).
- Tjekker også ved HA-start, når Daikin kommer online, og hvert 15. min.
- Rører ikke køl eller sluk. Kræver "Daikin Stue Power" tændt.

De to gamle er **slået fra, ikke slettet**.

## Test 20-11-2026
- Ved 22 °C i varme: ingen ændring (korrekt).
- Sat manuelt til kun blæs kl. 10:04:40 → automationen satte varme kl. 10:05:00.
- Logikken simuleret: 25/varme → blæs, 24/varme → intet, 23/blæs → varme,
  24/blæs → intet, 26/køl → intet, 22/sluk → intet.
