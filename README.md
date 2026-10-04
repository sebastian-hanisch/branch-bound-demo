# Branch & Bound am Rucksackproblem – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-branch-bound-demo.streamlit.app/)**

Erstes Stück der "Konzepte"-Reihe für die Website "Sebastian Hanisch – Operations Research
und Machine Learning": anders als die Fall-Demos im Portfolio (ein Anwendungsfall, mehrere
Verfahren im Vergleich) zeigt diese Demo **ein** Verfahren – Branch & Bound – und lässt
stattdessen das **Beispiel** wachsen. Vehikel-Problem ist das klassische 0/1-Rucksackproblem,
bewusst gewählt, weil es der einfachste Lehrfall für Branch & Bound ist und die LP-Relaxierung
als Bound trivial zu berechnen und zu erklären ist.

Die Konzepte-Reihe ist kein linearer Pfad, sondern mehrere unabhängige Linien: diese Demo
ist der Startpunkt der **Exakte-Suche-Linie**. Sie steht bewusst neben, nicht vor, der
**Clustering-Linie** ([k-Means](../kmeans-demo) → ... → [HDBSCAN](../hdbscan-demo)) – die
Linien bauen nicht aufeinander auf.

Zweites Stück der Exakte-Suche-Linie ist [dynamic-programming-demo](../dynamic-programming-demo)
– bewusst als **Kontrast**, nicht als Fix: dasselbe Rucksackproblem, aber Tabellierung
überlappender Teilprobleme statt Suchbaum + Schranken, mit einer eigenen, andersartigen
Schwäche (pseudopolynomiale Abhängigkeit von der Kapazität statt vom Suchbaum). Drittes
Stück ist [cutting-planes-demo](../cutting-planes-demo) (Schnittebenen, ein Vorläufer, kein
Kontrast). Diese beiden Vorläufer **konvergieren** im vierten Stück,
[branch-cut-demo](../branch-cut-demo): Branch & Cut kombiniert das Verzweigen aus dieser
Demo mit den Schnitten aus cutting-planes-demo – dieselbe Rolle wie HDBSCAN in der
Clustering-Linie, nur für die Exakte-Suche-Linie. Fünftes Stück ist
[constraint-programming-demo](../constraint-programming-demo) – ein **unabhängiger
Zweig** ab dieser Demo (keine Fortsetzung/Kontrast/Konvergenz): Constraint-Propagation
statt LP-Schranken-Vergleich, dieselbe Rolle wie gmm-demo/spectral-demo als unabhängige
Zweige ab kmeans-demo in der Clustering-Linie.

## Warum diese Demo anders aufgebaut ist

Die Fall-Demos im Portfolio beantworten "welches Verfahren löst diesen einen Fall am besten?".
Diese Demo (wie die übrigen Stücke der "Konzepte"-Reihe) beantwortet stattdessen "wie verhält
sich EIN Verfahren, wenn das Beispiel komplexer wird?" – bei 3–4 Paketen passt der komplette
Suchbaum aufs Bild und ist Knoten für Knoten durchklickbar, bei 20 Paketen macht erst gutes
Pruning den Baum überhaupt bezwingbar.
Genau dieser Kontrast ist der Punkt, nicht ein Methodenvergleich.

Zwei unabhängige Regler steuern, wie schwer die Instanz für Branch & Bound tatsächlich ist:

- **Anzahl Pakete** – steuert die reine Baumgröße (2ⁿ mögliche Ja/Nein-Kombinationen).
- **Korrelation Wert/Gewicht** – 0: Wert unabhängig vom Gewicht. 1: Wert = Gewicht plus Rauschen
  (±8): fast alle Pakete haben ein ähnliches Wert/Gewicht-Verhältnis. Das entspricht eher den
  „weakly correlated"-Instanzen aus Pisingers Katalog (2005) als den „strongly correlated"
  (Wert = Gewicht + Konstante), die in der Literatur als schwer für Branch & Bound gelten. Gemessen
  (20 Pakete, Limit 50 %, 40 Seeds): der Faktor schwache/starke Bound liegt im Median bei etwa 240 für
  Korrelation 0 und bei etwa 640 für 0.95, die starke Bound braucht in beiden Fällen im Median rund
  90 Knoten – die Korrelation schwächt die LP-Bound in dieser Demo also nicht; nur einzelne Seeds
  (z. B. Seed 3: 591 gegen 159) zeigen einen kleineren Vorteil.

Zusätzlich ein Umschalter zwischen einer **starken** Bound (LP-Relaxierung, fraktionales
Rucksackproblem) und einer bewusst **schwachen** Bound (ignoriert das Gewicht komplett) –
beide mathematisch gültig, aber unterschiedlich scharf. Das zeigt direkt, dass Pruning-Erfolg
an der Bound-Qualität hängt, nicht am Algorithmus selbst.

## Suchbaum-Visualisierung

Die Knoten-IDs werden in Tiefensuche-Reihenfolge vergeben ("aufgenommen" vor "ausgelassen", je Ebene ein
Paket in Wert/Gewicht-Reihenfolge) – ein Animationsschritt ist damit exakt ein besuchter
Knoten, in der tatsächlichen Suchreihenfolge des Algorithmus, nicht künstlich nachgebaut. Das
Baum-Layout wird einmal über die vollständige (gerenderte) Knotenmenge berechnet, damit
Positionen beim Abspielen nicht springen – nur welche Knoten/Kanten sichtbar sind, ändert sich
pro Schritt.

Ein zweites, live mitwachsendes Diagramm zeigt den bisher besten gefundenen Wert gegen die
Anzahl besuchter Knoten, mit einer gestrichelten Linie beim bewiesenen Optimum – macht
sichtbar, wie schnell (oder langsam) sich ein guter Kandidat findet, nicht nur, dass der
Algorithmus am Ende das richtige Ergebnis liefert.

## Sicherheitsgrenzen

Anders als bei den übrigen Demos, wo nur die *Lösung* eines exakten Lösers an ein Zeitlimit
stößt, könnte hier die *Visualisierung* selbst bei zu vielen Knoten einfrieren. Zwei getrennte
Grenzen fangen das ab:

- `MAX_NODES_EXPLORED` (200.000): harter Abbruch der Suche selbst, mit ehrlicher
  "abgebrochen, beste bislang gefundene Lösung"-Kennzeichnung (siehe
  [tests/test_solver.py](tests/test_solver.py)).
- `MAX_NODES_RENDERED` (800): die Baum-*Grafik* zeigt höchstens diese vielen Knoten, auch wenn
  mehr besucht wurden – alle Live-Kennzahlen (Gesamtzahl, gestutzt, bester Fund) bleiben davon
  unberührt und zeigen weiterhin den vollständigen, korrekten Lauf.

## Verifikation

Kein Vergleich gegen einen zweiten Solver möglich (Branch & Bound IST hier der exakte Löser)
– stattdessen drei unabhängige Prüfungen:

- **Brute-Force-Cross-Check**: für kleine Zufallsinstanzen (n=10, 30 Seeds, beide Bounds)
  muss der gefundene Optimalwert exakt mit vollständiger Enumeration übereinstimmen.
- **Bound-Gültigkeit**: für zufällige Teillösungen wird per Enumeration aller Vervollständigungen
  geprüft, dass keine Bound (stark oder schwach) den wahren maximal erreichbaren Wert je
  unterschätzt – die Voraussetzung dafür, dass Pruning überhaupt sicher ist.
- **Handgerechnete Kleinstinstanz**: 4 Pakete, Optimum von Hand nachgerechnet (Wert 7).

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Hauptablauf: Presets, Einstellungen, Suchbaum-Animation, Bound-Vergleich, Formulierungs-Expander |
| `bb_constants.py` | Defaults, Regler-Grenzen, Sicherheitsgrenzen, `PRESETS` |
| `bb_presets.py` | `SettingSpec`/`SETTING_SPECS`, Permalink-Logik, Presets, Zufalls-Seed-Button |
| `bb_scenario.py` | Zufällige Rucksack-Instanzen mit einstellbarer Wert/Gewicht-Korrelation |
| `bb_bound.py` | LP-Relaxierungs-Bound (stark) und Wertsummen-Bound (schwach) |
| `bb_solver.py` | Tiefensuche-Branch-and-Bound mit vollständigem Knoten-Protokoll |
| `bb_bruteforce.py` | Unabhängige Referenzlösung (vollständige Enumeration) für Tests |
| `bb_evaluation.py` | Kennzahlen aus einem Suchlauf, Bound-Vergleich |
| `bb_visualization.py` | Suchbaum- und Konvergenz-Diagramm (Plotly) |
| `tests/` | Bound-Gültigkeit, Brute-Force-Cross-Check, Prune-Invariante, Sicherheitsgrenzen |

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Exakte Suche erklärt: Rucksack und Cutting Stock](https://sebastianhanisch.net/konzepte-exakte-suche.html).
