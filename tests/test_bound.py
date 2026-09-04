from itertools import product

import numpy as np
import pytest

from bb_bound import lp_relaxation_bound, ratio_order, weak_bound
from bb_scenario import KnapsackInstance, generate_instance


def _all_completions_max_value(instance, order, depth, fixed_decisions):
    """Brute-force best achievable total value from a partial state, by
    enumerating every completion of the still-undecided items - used to
    check that a bound never underestimates reality."""
    remaining = order[depth:]
    best = None
    for combo in product([False, True], repeat=len(remaining)):
        weight = sum(w for w, _ in fixed_decisions)
        value = sum(v for _, v in fixed_decisions)
        for idx, take in zip(remaining, combo):
            if take:
                weight += instance.weights[idx]
                value += instance.values[idx]
        if weight <= instance.capacity and (best is None or value > best):
            best = value
    return best


@pytest.mark.parametrize("bound_fn", [lp_relaxation_bound, weak_bound])
def test_bound_is_a_valid_upper_bound_on_random_partial_states(bound_fn):
    for seed in range(15):
        instance = generate_instance(n_items=8, capacity_fraction=0.5, correlation=0.3, seed=seed)
        order = ratio_order(instance)
        for depth in range(instance.n_items + 1):
            decided = order[:depth]
            rng = np.random.default_rng(seed * 100 + depth)
            decisions = [bool(rng.integers(0, 2)) for _ in decided]
            weight = sum(instance.weights[i] for i, take in zip(decided, decisions) if take)
            if weight > instance.capacity:
                continue
            value = sum(instance.values[i] for i, take in zip(decided, decisions) if take)
            fixed = [(instance.weights[i], instance.values[i]) for i, take in zip(decided, decisions) if take]
            bound = bound_fn(instance, order, depth, instance.capacity - weight, value)
            true_best = _all_completions_max_value(instance, order, depth, fixed)
            assert bound >= true_best - 1e-9


def test_weak_bound_is_never_tighter_than_the_lp_relaxation_bound():
    for seed in range(15):
        instance = generate_instance(n_items=10, capacity_fraction=0.5, correlation=0.3, seed=seed)
        order = ratio_order(instance)
        for depth in range(instance.n_items + 1):
            b_weak = weak_bound(instance, order, depth, instance.capacity, 0)
            b_strong = lp_relaxation_bound(instance, order, depth, instance.capacity, 0)
            assert b_weak >= b_strong - 1e-9


def test_lp_relaxation_bound_matches_hand_computed_value():
    instance = KnapsackInstance(weights=(2, 3, 4, 5), values=(3, 4, 5, 6), capacity=5, correlation=0.0)
    order = ratio_order(instance)  # ratios: 1.5, 1.333, 1.25, 1.2 -> already index order 0,1,2,3
    assert order == [0, 1, 2, 3]
    # From the root: take item 0 (w2) fully -> capacity left 3, take item 1 (w3) fully
    # -> capacity left 0, items 2/3 contribute 0. Bound = 3 + 4 = 7 (no fraction needed).
    bound = lp_relaxation_bound(instance, order, 0, instance.capacity, 0)
    assert bound == pytest.approx(7.0)
