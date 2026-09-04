"""Summary statistics derived from a Branch & Bound SolveResult."""

from collections import Counter

from bb_bound import lp_relaxation_bound, weak_bound
from bb_solver import solve


def compute_stats(result, instance):
    counts = Counter(node.status for node in result.nodes)
    full_tree_nodes = 2 ** (instance.n_items + 1) - 1
    nodes_explored = len(result.nodes)
    return {
        "nodes_explored": nodes_explored,
        "full_tree_nodes": full_tree_nodes,
        "fraction_of_tree_explored": nodes_explored / full_tree_nodes,
        "pruned_bound": counts["prune_bound"],
        "pruned_infeasible": counts["prune_infeasible"],
        "branch_nodes": counts["branch"] + counts["root"],
        "leaves_evaluated": counts["leaf_new_best"] + counts["leaf_not_best"],
        "best_value": result.best_value,
        "truncated": result.truncated,
    }


def stats_up_to_step(result, step):
    """Same counts as compute_stats, but only over nodes visited so far
    (id <= step) - drives the live metrics row during step-through/auto-play."""
    counts = Counter(node.status for node in result.nodes if node.id <= step)
    current_best = 0
    for nid, v in result.incumbent_history:
        if nid <= step:
            current_best = v
    return {
        "nodes_so_far": counts.total(),
        "pruned_bound": counts["prune_bound"],
        "pruned_infeasible": counts["prune_infeasible"],
        "current_best": current_best,
    }


def bound_comparison(instance, max_nodes):
    """Solves the same instance with the strong (LP relaxation) and the
    weak (ignore-weight) bound, for the front-and-center 'does bound
    quality matter?' section - both must reach the same best_value."""
    strong_result = solve(instance, lp_relaxation_bound, max_nodes=max_nodes)
    weak_result = solve(instance, weak_bound, max_nodes=max_nodes)
    return {
        "strong": strong_result,
        "weak": weak_result,
        "strong_stats": compute_stats(strong_result, instance),
        "weak_stats": compute_stats(weak_result, instance),
    }
