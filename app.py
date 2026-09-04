"""
Branch & Bound am Rucksackproblem – interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Anders als die übrigen Demos im Portfolio (ein Anwendungsfall, mehrere Verfahren im
Vergleich) zeigt diese Demo EIN Verfahren - Branch & Bound - und lässt stattdessen das
Beispiel wachsen: von einer Instanz, deren kompletter Suchbaum aufs Bild passt, bis zu
einer, bei der Pruning über Minuten statt Millisekunden Rechenzeit entscheidet. Erstes
Stück der "Konzepte"-Reihe (siehe README für die Einordnung).

Lauffähig mit: streamlit run app.py
"""

import time

import streamlit as st

import bb_constants as C
from bb_bound import lp_relaxation_bound, weak_bound
from bb_evaluation import bound_comparison, compute_stats, stats_up_to_step
from bb_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sync_query_params,
)
from bb_scenario import generate_instance
from bb_solver import solve
from bb_visualization import build_incumbent_chart, build_tree_figure

st.set_page_config(page_title="Branch & Bound – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _compute_solve(n_items, capacity_fraction, correlation, seed, use_strong_bound):
    instance = generate_instance(n_items, capacity_fraction, correlation, seed)
    bound_fn = lp_relaxation_bound if use_strong_bound else weak_bound
    result = solve(instance, bound_fn)
    stats = compute_stats(result, instance)
    return instance, result, stats


@st.cache_data(show_spinner=False)
def _compute_bound_comparison(n_items, capacity_fraction, correlation, seed):
    instance = generate_instance(n_items, capacity_fraction, correlation, seed)
    return bound_comparison(instance, max_nodes=C.MAX_NODES_EXPLORED)


st.title("🌳 Branch & Bound am Rucksackproblem")
st.markdown(
    """
Ein Lieferwagen hat ein Gewichtslimit, mehrere Pakete stehen zur Auswahl - welche Auswahl
maximiert den Gesamtwert, ohne das Limit zu überschreiten? Das klassische **0/1-Rucksackproblem**
dient hier nur als Vehikel: im Mittelpunkt steht **Branch & Bound**, das Verfahren, das hinter
jedem "Exakt (OR-Tools)"-Vergleich im übrigen Portfolio unsichtbar mitläuft. Statt mehrere
Verfahren zu vergleichen, wächst hier das **Beispiel** - von einem Suchbaum, der komplett aufs
Bild passt, bis zu einem, bei dem nur gutes Pruning ihn überhaupt bezwingbar macht. Details im
Expander "Wie funktioniert Branch & Bound?" weiter unten, die formale Herleitung im Expander
"📐 Mathematische Formulierung".
"""
)

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
PRESET_HELP = {
    "Winziges Beispiel (Baum komplett sichtbar)": "4 Pakete - der komplette Suchbaum passt aufs Bild, jeder Knoten einzeln durchklickbar.",
    "Mittlere Instanz (Pruning wird sichtbar)": "10 Pakete - hier beginnt Pruning spürbar den Unterschied zu machen.",
    "Große, unkorrelierte Instanz (starke Bound glänzt)": "20 Pakete, Wert unabhängig vom Gewicht - die LP-Bound prunt hier fast den ganzen Baum weg.",
    "Große, korrelierte Instanz (Bound-Vorteil schrumpft)": "20 Pakete, Wert ≈ Gewicht - die LP-Bound hilft hier immer noch deutlich, aber spürbar weniger als bei unabhängigen Werten.",
}
preset_cols = st.columns(len(C.PRESETS))
for i, name in enumerate(C.PRESETS.keys()):
    with preset_cols[i]:
        st.button(name, use_container_width=True, on_click=apply_preset, args=(name,), help=PRESET_HELP[name])

st.caption(
    "🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, "
    "um ein Szenario zu teilen."
)

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    n_items = st.slider("Anzahl Pakete", *bounds("n_items_slider"), key="n_items_slider")
    capacity_fraction = st.slider(
        "Gewichtslimit (Anteil der Gesamtmenge)", *bounds("capacity_fraction_slider"), key="capacity_fraction_slider"
    )
    correlation = st.slider(
        "Korrelation Wert/Gewicht", *bounds("correlation_slider"), key="correlation_slider",
        help="0 = Wert unabhängig vom Gewicht (leicht zu prunen). 1 = wertvolle Pakete sind auch "
        "die schweren (klassische 'strongly correlated'-Instanz, notorisch schwer für Branch & Bound).",
    )
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)

    st.markdown("**Suchverhalten**")
    use_strong_bound = st.checkbox(
        "Starke Bound verwenden (LP-Relaxierung)",
        key="use_strong_bound_toggle",
        help="An: bricht ab, wenn die fraktionale (LP-)Lösung ab hier schon nicht mehr besser "
        "sein kann als der bisher beste Fund. Aus: bricht nur ab, wenn selbst alle restlichen "
        "Pakete gratis genommen nicht mehr helfen würden - eine gültige, aber sehr lockere "
        "Schranke, die kaum etwas abschneidet.",
    )

    st.button(
        "🎲 Neue Instanz generieren",
        use_container_width=True,
        on_click=randomize_seed,
        help="Würfelt einen neuen Zufalls-Seed für Paketgewichte und -werte.",
    )

sync_query_params(n_items, capacity_fraction, correlation, seed, use_strong_bound)

with st.spinner("Durchsuche den Baum..."):
    instance, result, stats = _compute_solve(int(n_items), capacity_fraction, correlation, int(seed), use_strong_bound)

if stats["truncated"]:
    st.error(
        f"⛔ Abgebrochen bei {C.MAX_NODES_EXPLORED:,} untersuchten Knoten, bevor der Baum "
        f"vollständig durchsucht war - das gezeigte Ergebnis ist die beste bislang gefundene, "
        f"nicht garantiert optimale Lösung. Reglereinstellungen (weniger Pakete, stärkere Bound, "
        f"geringere Korrelation) verringern die Baumgröße."
    )

max_step = len(result.nodes) - 1
if "bb_step" not in st.session_state or st.session_state.get("bb_step_owner") != (n_items, capacity_fraction, correlation, seed, use_strong_bound):
    st.session_state["bb_step"] = max_step
    st.session_state["bb_step_owner"] = (n_items, capacity_fraction, correlation, seed, use_strong_bound)

st.markdown("## 🎯 Der Suchbaum in Aktion")

render_note = (
    f" (zeigt die ersten {C.MAX_NODES_RENDERED:,} von {len(result.nodes):,} Knoten)"
    if len(result.nodes) > C.MAX_NODES_RENDERED
    else ""
)
st.caption(f"{len(result.nodes):,} Knoten insgesamt besucht{render_note}.")

step_col, play_col = st.columns([5, 1])
with step_col:
    step = st.slider("Schritt (Knoten)", 0, max_step, key="bb_step", help="Ein Schritt = ein besuchter Suchbaum-Knoten, in Besuchsreihenfolge.")
with play_col:
    auto_play = st.button("▶️ Abspielen", use_container_width=True)

tree_slot = st.empty()
gap_slot = st.empty()


def _render(current_step):
    tree_slot.plotly_chart(
        build_tree_figure(instance, result, current_step, C.MAX_NODES_RENDERED),
        use_container_width=True, key=f"tree_{current_step}",
    )
    gap_slot.plotly_chart(
        build_incumbent_chart(result, current_step, result.best_value),
        use_container_width=True, key=f"gap_{current_step}",
    )


if auto_play:
    n_frames = min(max_step + 1, 60)
    frame_skip = max(1, (max_step + 1) // n_frames)
    for s in list(range(0, max_step, frame_skip)) + [max_step]:
        _render(s)
        time.sleep(0.08)
    step = max_step
else:
    _render(step)

live = stats_up_to_step(result, step)
lm1, lm2, lm3, lm4 = st.columns(4)
lm1.metric("Besuchte Knoten (bisher)", f"{live['nodes_so_far']:,}")
lm2.metric("Gestutzt (Bound)", f"{live['pruned_bound']:,}")
lm3.metric("Gestutzt (zu schwer)", f"{live['pruned_infeasible']:,}")
lm4.metric("Bester Fund bisher", live["current_best"])

st.caption(
    f"Bewiesenes Optimum: **{result.best_value}** "
    f"({stats['fraction_of_tree_explored'] * 100:.2f}% des theoretischen 2^n-Baums tatsächlich besucht)."
)

st.markdown("---")

st.subheader("📐 Wie stark hilft eine gute Bound wirklich?")
st.markdown(
    """
Beide Bounds sind mathematisch gültig - keine unterschätzt jemals, was von einer Teillösung
aus noch erreichbar wäre, Pruning damit in beiden Fällen sicher. Der Unterschied liegt allein
in der **Schärfe**: eine lockere Bound schneidet seltener ab, selbst wenn das Ergebnis am Ende
exakt dasselbe ist. Live für Ihre aktuelle Instanz geprüft, nicht nur behauptet:
"""
)

cmp = _compute_bound_comparison(int(n_items), capacity_fraction, correlation, int(seed))
strong_nodes = cmp["strong_stats"]["nodes_explored"]
weak_nodes = cmp["weak_stats"]["nodes_explored"]
factor = weak_nodes / strong_nodes if strong_nodes else float("inf")

bc1, bc2, bc3 = st.columns(3)
bc1.metric("Starke Bound (LP-Relaxierung)", f"{strong_nodes:,} Knoten")
bc2.metric("Schwache Bound (nur Wertsumme)", f"{weak_nodes:,} Knoten", delta=f"{weak_nodes - strong_nodes:,} ggü. stark", delta_color="inverse")
bc3.metric("Beide finden denselben Optimalwert", cmp["strong"].best_value)

if factor >= 1.5:
    st.success(
        f"✅ Bei dieser Instanz durchsucht die schwache Bound **{factor:.1f}×** so viele Knoten "
        f"wie die starke - für dasselbe bewiesene Optimum. Der Unterschied liegt komplett in der "
        f"Bound-Schärfe, nicht im Algorithmus."
    )
else:
    st.info("Bei dieser (kleinen) Instanz ist der Unterschied noch nicht groß - mehr Pakete machen ihn deutlicher sichtbar.")

if correlation > 0.7:
    st.info(
        "ℹ️ Zum Vergleich: bei Korrelation 0 (Regler links) fällt dieser Faktor auf vergleichbaren "
        "Instanzen typischerweise deutlich größer aus. Sind Wert und Gewicht stark korreliert, "
        "haben fast alle Pakete ein ähnliches Wert/Gewicht-Verhältnis - dadurch bleibt selbst die "
        "scharfe LP-Bound an jedem Knoten näher am tatsächlich Erreichbaren dran, sie hilft also "
        "relativ gesehen weniger, auch wenn sie absolut meist noch klar überlegen bleibt."
    )

st.markdown("---")

with st.expander("Wie funktioniert Branch & Bound?"):
    st.markdown(
        """
Branch & Bound durchsucht systematisch alle 2ⁿ möglichen Ja/Nein-Entscheidungen (nehme
Paket $i$ mit oder nicht), ohne sie alle einzeln auszuprobieren - der Trick ist, ganze
Teilbäume überspringen zu können, ohne sie zu durchsuchen:

- **Branch (Verzweigen):** an jedem Knoten wird über GENAU EIN weiteres Paket entschieden -
  "rein" und "raus" werden zu zwei neuen Kind-Knoten.
- **Bound (Schranke):** für jeden Knoten wird eine **optimistische Obergrenze** berechnet -
  wie gut könnte die beste Vervollständigung von hier aus höchstens werden? Diese Demo bietet
  zwei Varianten: die scharfe **LP-Relaxierung** (bricht die Ganzzahligkeit auf, erlaubt
  Bruchteile eines Pakets) und eine bewusst **schwache** Variante (ignoriert das Gewicht
  komplett).
- **Prune (Stutzen):** ist die Obergrenze eines Knotens schon schlechter oder gleich gut wie
  der bisher beste GEFUNDENE, VOLLSTÄNDIGE Kandidat (der **Incumbent**), kann darunter
  garantiert nichts Besseres mehr stecken - der ganze Teilbaum wird übersprungen, ohne ihn
  einzeln durchzugehen.
- **Infeasible (Unzulässig):** ein Zweig, der das Gewichtslimit sofort überschreitet, wird
  ebenfalls sofort verworfen - unabhängig von der Bound.

Am Ende bleibt garantiert entweder ein **bewiesenes Optimum** (jeder Teilbaum wurde entweder
durchsucht oder nachweisbar zu Recht übersprungen) oder, bei sehr großen Instanzen, die beste
innerhalb der Rechenbudget-Grenze gefundene Lösung - diese Demo kennzeichnet diesen Fall
ehrlich als "abgebrochen", nie fälschlich als Optimum.

Die Reihenfolge, in der Pakete verzweigt werden (absteigend nach Wert/Gewicht-Verhältnis),
sowie "rein" vor "raus" sind bewusste, gängige Heuristiken - sie ändern nichts am gefundenen
Optimum, aber viel daran, wie schnell ein guter Incumbent gefunden wird und wie effektiv
dadurch früh geprunt werden kann.
        """
    )

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**0/1-Rucksackproblem:** gegeben $n$ Pakete mit Gewichten $w_i$ und Werten $v_i$ sowie ein
Gewichtslimit $W$, wähle eine Teilmenge, die den Gesamtwert maximiert, ohne $W$ zu überschreiten:

$$
\max \sum_{i=1}^n v_i x_i \quad \text{unter} \quad \sum_{i=1}^n w_i x_i \le W, \quad x_i \in \{0,1\}.
$$

NP-schwer (schwach NP-vollständig, pseudopolynomial lösbar per dynamischer Programmierung -
Branch & Bound wird hier bewusst statt DP gezeigt, weil sich der Suchbaum direkt visualisieren
lässt und dasselbe Prinzip auch auf Probleme ohne pseudopolynomiale DP-Lösung überträgt, z. B.
gemischt-ganzzahlige Modelle wie in den übrigen Demos dieses Portfolios).

**LP-Relaxierung** (starke Bound, an Knoten mit Teilentscheidung bis Index $k$, verbleibendem
Gewichtslimit $W'$ und bereits sicherem Wert $v'$): löst dieselbe Zielfunktion mit $x_i \in
[0,1]$ statt $\{0,1\}$ für die noch unentschiedenen Pakete $i > k$ in Wert/Gewicht-Reihenfolge
- das klassische Dantzig-Bound-Argument: die fraktionale Lösung ist immer mindestens so gut wie
jede ganzzahlige Vervollständigung, weil sie eine Restriktion (Ganzzahligkeit) fallen lässt.

$$
\text{Bound}_{\text{stark}} = v' + \max\Big\{\textstyle\sum_{i>k} v_i x_i : \sum_{i>k} w_i x_i \le W',\; x_i \in [0,1]\Big\}
$$

**Schwache Bound** (Vergleichsvariante): $\text{Bound}_{\text{schwach}} = v' + \sum_{i>k} v_i$
- ignoriert $W'$ komplett, ist damit immer $\ge \text{Bound}_{\text{stark}}$ und schneidet
entsprechend seltener ab (siehe Tests in [tests/test_bound.py](tests/test_bound.py), die
diese Ungleichung sowie die Gültigkeit beider Bounds gegen brute-force geprüfte
Referenzwerte verifizieren).

Implementiert in [bb_bound.py](bb_bound.py) (Bounds), [bb_solver.py](bb_solver.py)
(Tiefensuche mit Knoten-Protokoll) und [bb_bruteforce.py](bb_bruteforce.py) (unabhängige
Referenzlösung für kleine Instanzen).
        """
    )

st.markdown("---")

st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning. Interesse an einer maßgeschneiderten Lösung für "
    "Ihr Unternehmen? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html)"
)
