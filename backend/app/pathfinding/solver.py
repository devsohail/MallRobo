"""High-level route solver that combines BFS + TSP.

Pure Python — no framework imports.
"""

from dataclasses import dataclass
from typing import TypeAlias

from app.pathfinding.bfs import bfs_distance_matrix, reconstruct_path
from app.pathfinding.tsp import held_karp, nearest_neighbor_2opt

Point: TypeAlias = tuple[int, int]

HELD_KARP_THRESHOLD = 12


class UnreachableProductError(Exception):
    """Raised when one or more products cannot be reached from the robot start."""

    def __init__(self, unreachable_points: list[Point]) -> None:
        self.unreachable_points = unreachable_points
        super().__init__(f"Unreachable points: {unreachable_points}")


@dataclass(frozen=True)
class RouteResult:
    visit_order: list[Point]
    cells: list[Point]
    total_seconds: int
    exact: bool


def compute_route(
    grid: set[Point],
    start: Point,
    product_locations: list[Point],
) -> RouteResult:
    """Compute the optimal robot route visiting all product locations.

    Args:
        grid: set of accessible (x, y) cells
        start: robot starting position
        product_locations: list of (x, y) positions to visit

    Returns:
        RouteResult with the ordered path, visit sequence, and timing.

    Raises:
        UnreachableProductError: if any product location is blocked or unreachable.
    """
    # Validate start
    if start not in grid:
        raise UnreachableProductError([start])

    # Empty cart
    if not product_locations:
        return RouteResult(
            visit_order=[],
            cells=[start],
            total_seconds=0,
            exact=True,
        )

    # Deduplicate waypoints while preserving association
    unique_waypoints: list[Point] = list(dict.fromkeys(product_locations))

    # Check all waypoints are on accessible cells
    unreachable = [wp for wp in unique_waypoints if wp not in grid]
    if unreachable:
        raise UnreachableProductError(unreachable)

    # Build waypoints list: start + unique product locations
    all_waypoints = [start] + unique_waypoints
    k = len(unique_waypoints)

    # Build distance matrix via BFS
    try:
        dist_matrix, parent_maps = bfs_distance_matrix(grid, all_waypoints)
    except ValueError:
        # Some waypoints are unreachable despite being on valid cells (isolated by obstacles)
        unreachable_isolated = []
        from app.pathfinding.bfs import bfs_from_source

        start_dists, _ = bfs_from_source(grid, start)
        for wp in unique_waypoints:
            if wp not in start_dists:
                unreachable_isolated.append(wp)
        raise UnreachableProductError(unreachable_isolated)

    # Solve TSP
    if k <= HELD_KARP_THRESHOLD:
        total_cost, visit_order_indices = held_karp(dist_matrix)
        exact = True
    else:
        total_cost, visit_order_indices = nearest_neighbor_2opt(dist_matrix)
        exact = False

    # Build the full route: start → wp1 → wp2 → ... → wpk → start
    visit_order = [all_waypoints[i] for i in visit_order_indices]
    full_path = _reconstruct_full_path(all_waypoints, visit_order_indices, parent_maps, start)

    return RouteResult(
        visit_order=visit_order,
        cells=full_path,
        total_seconds=len(full_path) - 1,
        exact=exact,
    )


def _reconstruct_full_path(
    all_waypoints: list[Point],
    visit_order_indices: list[int],
    parent_maps: list[dict[Point, Point]],
    start: Point,
) -> list[Point]:
    """Reconstruct the full cell-by-cell path from the TSP visit order."""
    # Build sequence: [0] + visit_order_indices + [0] (return to start)
    sequence = [0] + list(visit_order_indices) + [0]

    full_path: list[Point] = []
    for step in range(len(sequence) - 1):
        from_idx = sequence[step]
        to_idx = sequence[step + 1]
        from_point = all_waypoints[from_idx]
        to_point = all_waypoints[to_idx]

        segment = reconstruct_path(parent_maps[from_idx], from_point, to_point)

        if full_path:
            # Skip the first cell to avoid duplicating the junction point
            full_path.extend(segment[1:])
        else:
            full_path.extend(segment)

    return full_path
