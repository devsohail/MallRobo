"""TSP solvers: Held-Karp (exact) and Nearest-Neighbor + 2-opt (heuristic).

Pure Python — no framework imports.
"""


def held_karp(dist: list[list[int]]) -> tuple[int, list[int]]:
    """Exact TSP solution using Held-Karp dynamic programming.

    Finds the minimum cost tour starting and ending at node 0,
    visiting all other nodes exactly once.

    Args:
        dist: distance matrix where dist[i][j] = cost from node i to node j.
              Node 0 is the start/end.

    Returns:
        (total_cost, visit_order) where visit_order is the sequence of node
        indices (excluding the return to 0).

    Time: O(2^k * k^2), Space: O(2^k * k) where k = len(dist) - 1.
    """
    n = len(dist)
    if n <= 1:
        return (0, [0])

    # dp[mask][i] = min cost to reach node i having visited the set 'mask' of nodes
    # mask is a bitmask over nodes 1..n-1 (node 0 is the start, not in the mask)
    k = n - 1  # number of nodes to visit (excluding start)
    INF = float("inf")
    size = 1 << k
    dp: list[list[float]] = [[INF] * k for _ in range(size)]
    parent: list[list[int]] = [[-1] * k for _ in range(size)]

    # Base case: go directly from node 0 to each node i
    for i in range(k):
        dp[1 << i][i] = dist[0][i + 1]

    # Fill DP
    for mask in range(1, size):
        for last in range(k):
            if not (mask & (1 << last)):
                continue
            if dp[mask][last] == INF:
                continue
            for nxt in range(k):
                if mask & (1 << nxt):
                    continue
                new_mask = mask | (1 << nxt)
                new_cost = dp[mask][last] + dist[last + 1][nxt + 1]
                if new_cost < dp[new_mask][nxt]:
                    dp[new_mask][nxt] = new_cost
                    parent[new_mask][nxt] = last

    # Find the optimal last node (completing the tour back to 0)
    full_mask = size - 1
    best_cost = INF
    best_last = -1
    for last in range(k):
        cost = dp[full_mask][last] + dist[last + 1][0]
        if cost < best_cost:
            best_cost = cost
            best_last = last

    # Reconstruct the visit order
    order: list[int] = []
    mask = full_mask
    current = best_last
    while current != -1:
        order.append(current + 1)  # convert back to original node index
        prev = parent[mask][current]
        mask ^= (1 << current)
        current = prev

    order.reverse()
    return (int(best_cost), order)


def nearest_neighbor_2opt(dist: list[list[int]]) -> tuple[int, list[int]]:
    """Heuristic TSP: nearest-neighbor construction + 2-opt improvement.

    Args:
        dist: distance matrix, node 0 is start/end.

    Returns:
        (total_cost, visit_order) — order excludes the return to 0.

    Time: O(k^2 * iterations), Space: O(k^2).
    """
    n = len(dist)
    if n <= 1:
        return (0, [0])

    # Nearest-neighbor construction starting from node 0
    visited = {0}
    tour = [0]
    current = 0
    for _ in range(n - 1):
        best_next = -1
        best_dist = float("inf")
        for j in range(n):
            if j not in visited and dist[current][j] < best_dist:
                best_dist = dist[current][j]
                best_next = j
        tour.append(best_next)
        visited.add(best_next)
        current = best_next

    # 2-opt improvement
    improved = True
    while improved:
        improved = False
        for i in range(1, len(tour) - 1):
            for j in range(i + 1, len(tour)):
                # Cost of current edges
                if j == len(tour) - 1:
                    # Edge from tour[j] back to 0
                    old = dist[tour[i - 1]][tour[i]] + dist[tour[j]][0]
                    new = dist[tour[i - 1]][tour[j]] + dist[tour[i]][0]
                else:
                    old = (
                        dist[tour[i - 1]][tour[i]] + dist[tour[j]][tour[j + 1]]
                    )
                    new = (
                        dist[tour[i - 1]][tour[j]] + dist[tour[i]][tour[j + 1]]
                    )
                if new < old:
                    tour[i : j + 1] = tour[i : j + 1][::-1]
                    improved = True

    # Calculate total cost including return to start
    total = sum(dist[tour[i]][tour[i + 1]] for i in range(len(tour) - 1))
    total += dist[tour[-1]][0]

    return (total, tour[1:])  # exclude start node from visit_order
