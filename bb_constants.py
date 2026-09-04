"""Defaults, slider bounds and presets for the Branch & Bound demo."""

DEFAULT_N_ITEMS = 6
DEFAULT_CAPACITY_FRACTION = 0.5
DEFAULT_CORRELATION = 0.0
DEFAULT_SEED = 7
DEFAULT_USE_STRONG_BOUND = True

N_ITEMS_MIN, N_ITEMS_MAX = 3, 22
CAPACITY_FRACTION_MIN, CAPACITY_FRACTION_MAX = 0.2, 0.8
CORRELATION_MIN, CORRELATION_MAX = 0.0, 1.0

# Hard safety limits so a bad slider combination (many items, weak bound,
# high correlation) can never freeze the app - the solve aborts with an
# honest "truncated" message instead of hanging.
MAX_NODES_EXPLORED = 200_000
MAX_NODES_RENDERED = 800

WEIGHT_RANGE = (5, 30)
VALUE_BASE_RANGE = (5, 30)
VALUE_NOISE_RANGE = (-8, 8)

PRESETS = {
    "Winziges Beispiel (Baum komplett sichtbar)": {
        "n_items": 4, "capacity_fraction": 0.5, "correlation": 0.0, "seed": 1,
    },
    "Mittlere Instanz (Pruning wird sichtbar)": {
        "n_items": 10, "capacity_fraction": 0.5, "correlation": 0.0, "seed": 7,
    },
    "Große, unkorrelierte Instanz (starke Bound glänzt)": {
        "n_items": 20, "capacity_fraction": 0.5, "correlation": 0.0, "seed": 3,
    },
    "Große, korrelierte Instanz (Bound-Vorteil schrumpft)": {
        "n_items": 20, "capacity_fraction": 0.5, "correlation": 0.95, "seed": 3,
    },
}
