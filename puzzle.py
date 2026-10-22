import random

# Configuration initiale selon le sujet (Figure 1, Pr. Larabi)
GOAL = (
    1, 2, 3,
    8, 0, 4,
    7, 6, 5,
)


def get_neighbors(state):
    """Retourne les états accessibles en un seul déplacement de la case vide."""
    neighbors = []
    zero_index = state.index(0)
    row = zero_index // 3
    col = zero_index % 3
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Haut, Bas, Gauche, Droite

    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_index = new_row * 3 + new_col
            new_state = list(state)
            new_state[zero_index], new_state[new_index] = (
                new_state[new_index],
                new_state[zero_index],
            )
            neighbors.append(tuple(new_state))
    return neighbors


def manhattan_distance(state):
    """Heuristique h2 : Somme des distances Manhattan des tuiles vers leur position cible (sans la case 0)."""
    distance = 0
    for index, tile in enumerate(state):
        if tile == 0:
            continue
        current_row, current_col = index // 3, index % 3
        goal_index = GOAL.index(tile)
        goal_row, goal_col = goal_index // 3, goal_index % 3
        distance += abs(current_row - goal_row) + abs(current_col - goal_col)
    return distance


def misplaced_tiles(state):
    """Heuristique h1 : Nombre de tuiles mal placées par rapport à la cible (sans la case 0)."""
    count = 0
    for tile, goal_tile in zip(state, GOAL):
        if tile != 0 and tile != goal_tile:
            count += 1
    return count


def inversion_count(state):
    """Compte le nombre d'inversions de la permutation, en ignorant la case vide 0."""
    tiles = [tile for tile in state if tile != 0]
    inversions = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversions += 1
    return inversions


def is_solvable(start):
    """
    Vérifie si la configuration peut atteindre l'objectif.
    Pour un damier 3x3, la parité du nombre d'inversions est un invariant de parité.
    """
    return inversion_count(start) % 2 == inversion_count(GOAL) % 2


def shuffle_board(state, moves=25):
    """Effectue une suite de déplacements aléatoires valides pour mélanger le taquin."""
    current = state
    prev = None
    for _ in range(moves):
        neighbors = get_neighbors(current)
        candidates = [n for n in neighbors if n != prev]
        chosen = random.choice(candidates if candidates else neighbors)
        prev = current
        current = chosen
    return current


def print_board(state):
    """Affiche le plateau 3x3 dans la console."""
    for row in range(3):
        values = state[row * 3 : row * 3 + 3]
        print(" ".join("_" if tile == 0 else str(tile) for tile in values))
    print()
