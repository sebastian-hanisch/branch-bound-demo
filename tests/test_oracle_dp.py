"""Unabhängiges Orakel für Branch & Bound am Rucksack: Optimum per Kapazitäts-DP
(statt Suchbaum/Enumeration), jede angezeigte Knoten-Schranke gegen `linprog`
(LP-Relaxierung) bzw. gegen das echte beste Ende per DP, und die Knotenzahl gegen
eine eigene, regelgleiche Tiefensuche."""

import numpy as np
import pytest

from bb_bound import lp_relaxation_bound, weak_bound
from bb_scenario import generate_instance
from bb_solver import solve

scipy_opt = pytest.importorskip("scipy.optimize")


def _dp(weights, values, cap):
    best = [0] * (cap + 1)
    for w, v in zip(weights, values):
        for c in range(cap, w - 1, -1):
            best[c] = max(best[c], best[c - w] + v)
    return best[cap]


def _node_count(inst, strong):
    n = inst.n_items
    order = [-j for _, j in sorted(((inst.values[i] / inst.weights[i], -i) for i in range(n)), reverse=True)]

    def bound(depth, rem, cur):
        if not strong:
            return cur + sum(inst.values[i] for i in order[depth:])
        b, c = cur, rem
        for i in order[depth:]:
            if inst.weights[i] <= c:
                c -= inst.weights[i]
                b += inst.values[i]
            else:
                return b + inst.values[i] * c / inst.weights[i]
        return b

    state = {"cnt": 1, "best": 0}

    def rec(depth, wt, val):
        i = order[depth]
        for take in (1, 0):
            nw, nv = wt + take * inst.weights[i], val + take * inst.values[i]
            state["cnt"] += 1
            if nw > inst.capacity:
                continue
            if depth + 1 == n:
                state["best"] = max(state["best"], nv)
                continue
            if bound(depth + 1, inst.capacity - nw, nv) <= state["best"]:
                continue
            rec(depth + 1, nw, nv)

    rec(0, 0, 0)
    return state["cnt"], state["best"]


CASES = [(n, cap, corr, seed) for n in (1, 3, 6, 9, 12) for cap in (0.2, 0.5, 0.8) for corr in (0.0, 0.95) for seed in range(2)]


@pytest.mark.parametrize("n_items,cap,corr,seed", CASES)
def test_optimum_node_count_and_bounds_match_independent_oracles(n_items, cap, corr, seed):
    inst = generate_instance(n_items, cap, corr, seed)
    opt = _dp(inst.weights, inst.values, inst.capacity)
    for bound_fn, strong in ((lp_relaxation_bound, True), (weak_bound, False)):
        res = solve(inst, bound_fn)
        assert res.best_value == opt
        assert sum(v for v, t in zip(inst.values, res.best_selection) if t) == opt
        assert sum(w for w, t in zip(inst.weights, res.best_selection) if t) <= inst.capacity
        count, best = _node_count(inst, strong)
        assert (len(res.nodes), best) == (count, opt)
        order = list(res.order)
        for node in res.nodes:
            if node.bound is None:
                continue
            rem = inst.capacity - node.weight
            rest = [order[k] for k in range(node.depth, n_items)]
            completion = _dp([inst.weights[i] for i in rest], [inst.values[i] for i in rest], rem) if rest else 0
            assert node.bound >= node.value + completion - 1e-9  # Schranke gültig
            if strong and rest:
                w = np.array([inst.weights[i] for i in rest], dtype=float)
                v = np.array([inst.values[i] for i in rest], dtype=float)
                lp = scipy_opt.linprog(-v, A_ub=w[None, :], b_ub=[rem], bounds=(0, 1), method="highs")
                assert node.bound == pytest.approx(node.value - lp.fun, abs=1e-7)
