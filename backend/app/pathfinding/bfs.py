"""BFS-based shortest path on an unweighted obstacle grid.

Pure Python — no framework imports.
"""

from collections import deque
from typing import TypeAlias

Point: TypeAlias = tuple[int, int]

# 4-directional movement
DIRECTIONS: list[Point] = [(0, 1), (0, -1), (1, 0), (-1, 0)]


def bfs_shortest_path(
    grid: set[Point],
    start: Point,
    goal: Point,
) -> tuple[int, list[Point]] | None:
    """Run BFS from start to goal on the accessible grid cells.

    Returns (distance, path) or None if unreachable.
    Path includes both start and goal.
    """
    if start == goal:
        return (0, [start])
    if start not in grid or goal not in grid:
        return None

    visited: set[Point] = {start}
    parent: dict[Point, Point] = {}
    queue: deque[Point] = deque([start])

    while queue:
        current = queue.popleft()
        for dx, dy in DIRECTIONS:
            neighbor = (current[0] + dx, current[1] + dy)
            if neighbor in grid and neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                if neighbor == goal:
                    return _reconstruct(parent, start, goal)
                queue.append(neighbor)

    return None


def _reconstruct(
    parent: dict[Point, Point], start: Point, goal: Point
) -> tuple[int, list[Point]]:
    path: list[Point] = []
    current = goal
    while current != start:
        path.append(current)
        current = parent[current]
    path.append(start)
    path.reverse()
    return (len(path) - 1, path)


def bfs_from_source(
    grid: set[Point],
    source: Point,
) -> tuple[dict[Point, int], dict[Point, Point]]:
    """Run BFS from a single source, returning distances and parent maps for all reachable cells."""
    dist: dict[Point, int] = {source: 0}
    parent: dict[Point, Point] = {}
    queue: deque[Point] = deque([source])

    while queue:
        current = queue.popleft()
        for dx, dy in DIRECTIONS:
            neighbor = (current[0] + dx, current[1] + dy)
            if neighbor in grid and neighbor not in dist:
                dist[neighbor] = dist[current] + 1
                parent[neighbor] = current
                queue.append(neighbor)

    return dist, parent


def reconstruct_path(
    parent: dict[Point, Point], source: Point, target: Point
) -> list[Point]:
    """Reconstruct the path from source to target using a parent map."""
    if source == target:
        return [source]
    path: list[Point] = []
    current = target
    while current != source:
        path.append(current)
        current = parent[current]
    path.append(source)
    path.reverse()
    return path


def bfs_distance_matrix(
    grid: set[Point],
    waypoints: list[Point],
) -> tuple[list[list[int]], list[dict[Point, Point]]]:
    """Build a distance matrix and parent maps for all waypoints.

    waypoints[0] is expected to be the start/robot position.
    Returns (distance_matrix, parent_maps) where:
    - distance_matrix[i][j] = shortest distance from waypoints[i] to waypoints[j]
    - parent_maps[i] = parent map from BFS rooted at waypoints[i]

    Raises ValueError if any waypoint pair is unreachable.
    """
    n = len(waypoints)
    dist_matrix: list[list[int]] = [[0] * n for _ in range(n)]
    parent_maps: list[dict[Point, Point]] = []

    for i in range(n):
        dists, parents = bfs_from_source(grid, waypoints[i])
        parent_maps.append(parents)
        for j in range(n):
            if i == j:
                continue
            if waypoints[j] not in dists:
                raise ValueError(
                    f"Waypoint {waypoints[j]} is unreachable from {waypoints[i]}"
                )
            dist_matrix[i][j] = dists[waypoints[j]]

    return dist_matrix, parent_maps
