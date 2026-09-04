"""Random 0/1-knapsack instance generation for the Branch & Bound demo."""

from dataclasses import dataclass

import numpy as np

from bb_constants import VALUE_BASE_RANGE, VALUE_NOISE_RANGE, WEIGHT_RANGE


@dataclass(frozen=True)
class KnapsackInstance:
    weights: tuple
    values: tuple
    capacity: int
    correlation: float

    @property
    def n_items(self):
        return len(self.weights)


def generate_instance(n_items, capacity_fraction, correlation, seed):
    """correlation=0: value independent of weight (easy for the LP bound to
    prune). correlation=1: value ~= weight (classic "strongly correlated"
    knapsack instance - notoriously hard to prune, even with the LP bound,
    because ratio-sorting no longer separates good items from bad ones)."""
    rng = np.random.default_rng(seed)
    weights = rng.integers(WEIGHT_RANGE[0], WEIGHT_RANGE[1] + 1, size=n_items)
    uncorrelated_value = rng.integers(VALUE_BASE_RANGE[0], VALUE_BASE_RANGE[1] + 1, size=n_items)
    noise = rng.integers(VALUE_NOISE_RANGE[0], VALUE_NOISE_RANGE[1] + 1, size=n_items)
    correlated_value = weights + noise
    values = np.round((1 - correlation) * uncorrelated_value + correlation * correlated_value)
    values = np.maximum(values, 1).astype(int)
    capacity = max(1, round(capacity_fraction * weights.sum()))
    return KnapsackInstance(
        weights=tuple(int(w) for w in weights),
        values=tuple(int(v) for v in values),
        capacity=int(capacity),
        correlation=correlation,
    )
