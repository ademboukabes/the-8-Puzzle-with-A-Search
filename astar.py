import heapq
from itertools import count

from puzzle import GOAL, get_neighbors, manhattan_distance


def reconstruct_path(parent, current):
    """Reconstruit le chemin de la configuration de départ jusqu'à l'objectif."""
    path = [current]
    while current in parent:
        current = parent[current]
        path.append(current)
    path.reverse()
    return path


def astar(start, heuristic=manhattan_distance):
    """
    Algorithme A* conforme au formalisme enseigné en FIA (Pr. Larabi, USTHB) :
    - OPEN : file de priorité ordonnée par f(n) = g(n) + h(n)
    - CLOSED : ensemble des états déjà développés/explorés

    Retourne :
    - path : liste des états menant à l'objectif (None si pas de solution) ;
    - exploration : liste chronologique des nœuds extraits de OPEN avec leurs scores g, h, f.
    """
    if start == GOAL:
        return [start], []

    sequence = count()
    open_list = []
    closed_set = set()

    g_scores = {start: 0}
    parent = {}

    h_start = heuristic(start)
    # Tuple stocké dans OPEN : (f(n), sequence_id, state, g(n))
    heapq.heappush(open_list, (h_start, next(sequence), start, 0))
    exploration = []

    while open_list:
        f, _, current, saved_g = heapq.heappop(open_list)

        # Si l'état a déjà été développé, on l'ignore (fermé)
        if current in closed_set:
            continue
        closed_set.add(current)

        h_current = heuristic(current)
        exploration.append({
            "state": current,
            "g": saved_g,
            "h": h_current,
            "f": f,
        })

        # Test de but
        if current == GOAL:
            path = reconstruct_path(parent, current)
            return path, exploration

        # Expansion des successeurs
        for neighbor in get_neighbors(current):
            if neighbor in closed_set:
                continue

            tentative_g = saved_g + 1

            if tentative_g < g_scores.get(neighbor, float("inf")):
                parent[neighbor] = current
                g_scores[neighbor] = tentative_g
                h_neighbor = heuristic(neighbor)
                f_neighbor = tentative_g + h_neighbor
                heapq.heappush(
                    open_list,
                    (f_neighbor, next(sequence), neighbor, tentative_g),
                )

    return None, exploration
