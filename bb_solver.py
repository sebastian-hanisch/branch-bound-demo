"""Depth-first Branch & Bound for 0/1-knapsack that records every visited
node, in visit order, so the app can replay the search step by step.

Branching: one item per tree level, in ratio order (see bb_bound.ratio_order)
- "include" explored before "exclude", the standard order because it tends
to find a good incumbent early, which then prunes more of the "exclude"
side. Pruning reasons are recorded explicitly (infeasible vs. bound) so the
visualization can distinguish them.
"""

from dataclasses import dataclass

from bb_bound import ratio_order
from bb_constants import MAX_NODES_EXPLORED


@dataclass(frozen=True)
class Node:
    id: int
    parent_id: int
    depth: int
    item_index: int  # None for the root
    decision: bool  # True = included, False = excluded, None for the root
    weight: int
    value: int
    bound: float  # None for infeasible-pruned nodes (no bound computed)
    status: str  # root | branch | prune_bound | prune_infeasible | leaf_new_best | leaf_not_best


@dataclass(frozen=True)
class SolveResult:
    best_value: int
    best_selection: tuple
    nodes: tuple
    incumbent_history: tuple  # (node_id, value) pairs, in visit order
    truncated: bool
    order: tuple  # branching order used (item indices, ratio-descending)


def solve(instance, bound_fn, max_nodes=MAX_NODES_EXPLORED):
    order = ratio_order(instance)
    nodes = []
    incumbent_history = []
    best = {"value": 0, "selection": tuple(False for _ in range(instance.n_items))}
    truncated = {"flag": False}
    next_id = [0]

    def new_node(parent_id, depth, item_index, decision, weight, value, bound, status):
        node = Node(next_id[0], parent_id, depth, item_index, decision, weight, value, bound, status)
        next_id[0] += 1
        nodes.append(node)
        return node

    root_bound = bound_fn(instance, order, 0, instance.capacity, 0)
    root = new_node(None, 0, None, None, 0, 0, root_bound, "root")

    def explore(node, weight, value, decisions):
        depth = node.depth
        item = order[depth]
        w, v = instance.weights[item], instance.values[item]

        for decision in (True, False):
            if truncated["flag"] or len(nodes) >= max_nodes:
                truncated["flag"] = True
                return

            new_weight = weight + (w if decision else 0)
            new_value = value + (v if decision else 0)
            new_depth = depth + 1
            new_decisions = decisions + [(item, decision)]

            if decision and new_weight > instance.capacity:
                new_node(node.id, new_depth, item, decision, new_weight, new_value, None, "prune_infeasible")
                continue

            child_bound = bound_fn(instance, order, new_depth, instance.capacity - new_weight, new_value)

            if new_depth == instance.n_items:
                is_new_best = new_value > best["value"]
                status = "leaf_new_best" if is_new_best else "leaf_not_best"
                child = new_node(node.id, new_depth, item, decision, new_weight, new_value, child_bound, status)
                if is_new_best:
                    decision_map = dict(new_decisions)
                    best["value"] = new_value
                    best["selection"] = tuple(decision_map[i] for i in range(instance.n_items))
                    incumbent_history.append((child.id, new_value))
                continue

            if child_bound <= best["value"]:
                new_node(node.id, new_depth, item, decision, new_weight, new_value, child_bound, "prune_bound")
                continue

            child = new_node(node.id, new_depth, item, decision, new_weight, new_value, child_bound, "branch")
            explore(child, new_weight, new_value, new_decisions)

    explore(root, 0, 0, [])

    return SolveResult(
        best_value=best["value"],
        best_selection=best["selection"],
        nodes=tuple(nodes),
        incumbent_history=tuple(incumbent_history),
        truncated=truncated["flag"],
        order=tuple(order),
    )
