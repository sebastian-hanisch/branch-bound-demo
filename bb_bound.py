"""Upper-bound functions for Branch & Bound on 0/1-knapsack.

Both bounds take the same signature so the solver can swap them freely to
demonstrate how bound tightness alone changes pruning effectiveness. Both
are valid (never underestimate the best achievable completion) - that is
what makes pruning on them safe.
"""


def ratio_order(instance):
    """Item indices sorted by value/weight descending - the order both the
    branching and the LP-relaxation bound use, so the bound is tightest
    exactly where the algorithm is about to make its next decision."""
    return sorted(range(instance.n_items), key=lambda i: instance.values[i] / instance.weights[i], reverse=True)


def lp_relaxation_bound(instance, order, depth, remaining_capacity, current_value):
    """Fractional knapsack over the still-undecided items (in ratio order):
    take whole items while they fit, then a fraction of the next one. This
    is the classical, tight Dantzig bound for 0/1-knapsack B&B."""
    bound = current_value
    capacity = remaining_capacity
    for idx in order[depth:]:
        w, v = instance.weights[idx], instance.values[idx]
        if w <= capacity:
            capacity -= w
            bound += v
        else:
            bound += v * (capacity / w)
            break
    return bound


def weak_bound(instance, order, depth, remaining_capacity, current_value):
    """Ignores weight entirely: current value plus the value of every
    remaining item, as if capacity were infinite. Always valid, but far
    looser than the LP bound - deliberately weak, to show how much pruning
    depends on bound quality rather than just on the algorithm itself."""
    return current_value + sum(instance.values[idx] for idx in order[depth:])
