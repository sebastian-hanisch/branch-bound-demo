"""Exhaustive reference solver for 0/1-knapsack - independent of Branch &
Bound, used to verify the B&B implementation against ground truth. Only
practical for small n_items (exponential), which is exactly the regime
where B&B's own tree is still small enough to compare node-by-node."""

from itertools import product


def solve_bruteforce(instance):
    best_value = 0
    best_selection = tuple(False for _ in range(instance.n_items))
    for selection in product([False, True], repeat=instance.n_items):
        weight = sum(w for w, take in zip(instance.weights, selection) if take)
        if weight > instance.capacity:
            continue
        value = sum(v for v, take in zip(instance.values, selection) if take)
        if value > best_value:
            best_value = value
            best_selection = selection
    return best_value, best_selection
