from bb_bound import lp_relaxation_bound, weak_bound
from bb_bruteforce import solve_bruteforce
from bb_evaluation import compute_stats
from bb_scenario import KnapsackInstance, generate_instance
from bb_solver import solve


def test_matches_hand_computed_tiny_instance():
    # Weights [2,3,4,5], values [3,4,5,6], capacity 5. By hand: only {item0,item1}
    # (weight 5, value 7) and {item3} alone (weight 5, value 6) fit exactly at
    # capacity; every other feasible subset is worse. Optimum: value 7.
    instance = KnapsackInstance(weights=(2, 3, 4, 5), values=(3, 4, 5, 6), capacity=5, correlation=0.0)
    result = solve(instance, lp_relaxation_bound)
    assert result.best_value == 7
    assert result.best_selection == (True, True, False, False)
    weight = sum(w for w, take in zip(instance.weights, result.best_selection) if take)
    assert weight <= instance.capacity


def test_matches_bruteforce_across_random_small_instances():
    for seed in range(30):
        instance = generate_instance(n_items=10, capacity_fraction=0.5, correlation=seed % 5 / 4, seed=seed)
        true_best, _ = solve_bruteforce(instance)
        strong = solve(instance, lp_relaxation_bound)
        weak = solve(instance, weak_bound)
        assert strong.best_value == true_best, f"strong bound mismatch, seed={seed}"
        assert weak.best_value == true_best, f"weak bound mismatch, seed={seed}"
        weight = sum(w for w, take in zip(instance.weights, strong.best_selection) if take)
        assert weight <= instance.capacity


def test_pruned_bound_nodes_never_exceed_the_final_best_value():
    for seed in range(10):
        instance = generate_instance(n_items=10, capacity_fraction=0.5, correlation=0.4, seed=seed)
        result = solve(instance, lp_relaxation_bound)
        for node in result.nodes:
            if node.status == "prune_bound":
                assert node.bound <= result.best_value


def test_incumbent_history_is_nondecreasing_and_ends_at_best_value():
    instance = generate_instance(n_items=10, capacity_fraction=0.5, correlation=0.2, seed=5)
    result = solve(instance, lp_relaxation_bound)
    values = [v for _, v in result.incumbent_history]
    assert values == sorted(values)
    assert values[-1] == result.best_value


def test_strong_bound_explores_no_more_nodes_in_total_than_weak_bound():
    total_strong = total_weak = 0
    for seed in range(20):
        instance = generate_instance(n_items=9, capacity_fraction=0.5, correlation=0.3, seed=seed)
        strong = solve(instance, lp_relaxation_bound)
        weak = solve(instance, weak_bound)
        total_strong += compute_stats(strong, instance)["nodes_explored"]
        total_weak += compute_stats(weak, instance)["nodes_explored"]
    assert total_strong <= total_weak


def test_max_nodes_cap_is_honored_and_flagged_as_truncated():
    instance = generate_instance(n_items=20, capacity_fraction=0.5, correlation=0.95, seed=1)
    result = solve(instance, weak_bound, max_nodes=50)
    assert len(result.nodes) <= 50 + 2  # small slack: the cap is checked before pairs of children
    assert result.truncated
