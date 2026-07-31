"""Tests for the pathfinding package — pure Python, no DB needed."""

import itertools
import time

import pytest

from app.pathfinding.bfs import bfs_shortest_path, bfs_distance_matrix
from app.pathfinding.solver import (
    RouteResult,
    UnreachableProductError,
    compute_route,
)
from app.pathfinding.tsp import held_karp, nearest_neighbor_2opt

# ── Test Grid ──
# A simple 5x5 grid with some obstacles:
#  . . . . .    (y=0)
#  . X X . .    (y=1)
#  . X . . .    (y=2)
#  . . . X .    (y=3)
#  . . . . .    (y=4)
SIMPLE_GRID: set[tuple[int, int]] = set()
OBSTACLES = {(1, 1), (2, 1), (1, 2), (3, 3)}
for y in range(5):
    for x in range(5):
        if (x, y) not in OBSTACLES:
            SIMPLE_GRID.add((x, y))


# ── Larger grid matching seed data layout (14x9) ──
GRID_LAYOUT = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]
LARGE_GRID: set[tuple[int, int]] = set()
for y, row in enumerate(GRID_LAYOUT):
    for x, val in enumerate(row):
        if val == 1:
            LARGE_GRID.add((x, y))

ROBOT_START = (0, 0)


class TestBFS:
    def test_same_start_and_goal(self) -> None:
        result = bfs_shortest_path(SIMPLE_GRID, (0, 0), (0, 0))
        assert result is not None
        assert result == (0, [(0, 0)])

    def test_straight_line(self) -> None:
        result = bfs_shortest_path(SIMPLE_GRID, (0, 0), (4, 0))
        assert result is not None
        dist, path = result
        assert dist == 4
        assert path[0] == (0, 0)
        assert path[-1] == (4, 0)

    def test_around_obstacle(self) -> None:
        result = bfs_shortest_path(SIMPLE_GRID, (0, 0), (2, 2))
        assert result is not None
        dist, path = result
        # Must go around the obstacle block
        assert dist > 2  # Can't go directly

    def test_unreachable(self) -> None:
        # Create a grid with an isolated cell
        grid = {(0, 0), (1, 0), (5, 5)}
        result = bfs_shortest_path(grid, (0, 0), (5, 5))
        assert result is None

    def test_start_not_in_grid(self) -> None:
        result = bfs_shortest_path(SIMPLE_GRID, (99, 99), (0, 0))
        assert result is None


class TestHeldKarp:
    def test_single_node(self) -> None:
        dist = [[0]]
        cost, order = held_karp(dist)
        assert cost == 0
        assert order == [0]

    def test_two_nodes(self) -> None:
        dist = [[0, 5], [5, 0]]
        cost, order = held_karp(dist)
        assert cost == 10  # 0->1->0
        assert order == [1]

    def test_three_nodes_symmetric(self) -> None:
        dist = [
            [0, 1, 2],
            [1, 0, 1],
            [2, 1, 0],
        ]
        cost, order = held_karp(dist)
        # Optimal: 0->1->2->0 = 1+1+2=4 or 0->2->1->0 = 2+1+1=4
        assert cost == 4

    def test_optimality_brute_force(self) -> None:
        """Verify Held-Karp matches brute force for small instance."""
        dist = [
            [0, 3, 7, 2],
            [3, 0, 4, 6],
            [7, 4, 0, 5],
            [2, 6, 5, 0],
        ]
        cost_hk, _ = held_karp(dist)

        # Brute force
        nodes = list(range(1, 4))
        best = float("inf")
        for perm in itertools.permutations(nodes):
            c = dist[0][perm[0]]
            for i in range(len(perm) - 1):
                c += dist[perm[i]][perm[i + 1]]
            c += dist[perm[-1]][0]
            best = min(best, c)

        assert cost_hk == best


class TestNearestNeighbor2Opt:
    def test_two_nodes(self) -> None:
        dist = [[0, 5], [5, 0]]
        cost, order = nearest_neighbor_2opt(dist)
        assert cost == 10

    def test_reasonable_quality(self) -> None:
        """NN+2opt should be within 2x of optimal for small cases."""
        dist = [
            [0, 3, 7, 2],
            [3, 0, 4, 6],
            [7, 4, 0, 5],
            [2, 6, 5, 0],
        ]
        cost_hk, _ = held_karp(dist)
        cost_nn, _ = nearest_neighbor_2opt(dist)
        assert cost_nn <= cost_hk * 2


class TestComputeRoute:
    def test_empty_cart(self) -> None:
        result = compute_route(SIMPLE_GRID, (0, 0), [])
        assert result.total_seconds == 0
        assert result.cells == [(0, 0)]
        assert result.visit_order == []
        assert result.exact is True

    def test_single_product(self) -> None:
        result = compute_route(SIMPLE_GRID, (0, 0), [(4, 0)])
        assert result.total_seconds > 0
        assert result.cells[0] == (0, 0)
        assert result.cells[-1] == (0, 0)
        assert (4, 0) in result.cells
        assert result.exact is True

    def test_adjacent_product(self) -> None:
        result = compute_route(SIMPLE_GRID, (0, 0), [(1, 0)])
        assert result.total_seconds == 2  # go 1 step + return 1 step
        assert result.cells == [(0, 0), (1, 0), (0, 0)]

    def test_path_continuity(self) -> None:
        """Every consecutive pair in cells must be 4-adjacent."""
        result = compute_route(SIMPLE_GRID, (0, 0), [(4, 4), (0, 4)])
        for i in range(len(result.cells) - 1):
            a, b = result.cells[i], result.cells[i + 1]
            assert abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1, (
                f"Non-adjacent cells at step {i}: {a} -> {b}"
            )

    def test_all_waypoints_visited(self) -> None:
        waypoints = [(4, 0), (0, 4), (4, 4)]
        result = compute_route(SIMPLE_GRID, (0, 0), waypoints)
        for wp in waypoints:
            assert wp in result.cells

    def test_returns_to_start(self) -> None:
        result = compute_route(SIMPLE_GRID, (0, 0), [(4, 4)])
        assert result.cells[0] == (0, 0)
        assert result.cells[-1] == (0, 0)

    def test_unreachable_product(self) -> None:
        grid = {(0, 0), (1, 0)}  # small grid
        with pytest.raises(UnreachableProductError):
            compute_route(grid, (0, 0), [(5, 5)])

    def test_product_on_obstacle(self) -> None:
        with pytest.raises(UnreachableProductError):
            compute_route(SIMPLE_GRID, (0, 0), [(1, 1)])  # (1,1) is an obstacle

    def test_duplicate_locations_visited_once(self) -> None:
        result = compute_route(SIMPLE_GRID, (0, 0), [(4, 0), (4, 0)])
        # Should be same as single product at (4,0)
        result_single = compute_route(SIMPLE_GRID, (0, 0), [(4, 0)])
        assert result.total_seconds == result_single.total_seconds

    def test_optimality_vs_brute_force_k_le_6(self) -> None:
        """For k <= 6, verify the route matches brute-force optimum."""
        waypoints = [(4, 0), (0, 4), (4, 4)]
        result = compute_route(SIMPLE_GRID, (0, 0), waypoints)

        # Brute force: try all orderings
        best_cost = float("inf")
        all_points = [(0, 0)] + list(dict.fromkeys(waypoints))
        dist_matrix, _ = bfs_distance_matrix(SIMPLE_GRID, all_points)

        indices = list(range(1, len(all_points)))
        for perm in itertools.permutations(indices):
            cost = dist_matrix[0][perm[0]]
            for i in range(len(perm) - 1):
                cost += dist_matrix[perm[i]][perm[i + 1]]
            cost += dist_matrix[perm[-1]][0]
            best_cost = min(best_cost, cost)

        assert result.total_seconds == best_cost

    def test_large_grid_single_product(self) -> None:
        result = compute_route(LARGE_GRID, ROBOT_START, [(13, 0)])
        assert result.cells[0] == ROBOT_START
        assert result.cells[-1] == ROBOT_START
        assert (13, 0) in result.cells

    def test_performance_k12(self) -> None:
        """k=12 should complete in under 2 seconds on the large grid."""
        # Pick 12 distinct path cells
        waypoints = [
            (3, 0), (6, 0), (9, 0), (13, 0),
            (0, 3), (3, 3), (6, 3), (9, 3),
            (0, 6), (3, 6), (6, 6), (9, 6),
        ]
        start = time.time()
        result = compute_route(LARGE_GRID, ROBOT_START, waypoints)
        elapsed = time.time() - start
        assert elapsed < 2.0, f"k=12 took {elapsed:.2f}s (limit: 2s)"
        assert result.exact is True
        assert result.cells[0] == ROBOT_START
        assert result.cells[-1] == ROBOT_START
