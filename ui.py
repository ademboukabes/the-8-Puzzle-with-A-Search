import pygame

from astar import astar
from puzzle import (
    GOAL,
    get_neighbors,
    is_solvable,
    manhattan_distance,
    misplaced_tiles,
    shuffle_board,
)

# Dimensions & Géométrie
WIDTH = 840
HEIGHT = 560
TILE_SIZE = 92
GAP = 8
BOARD_X = 50
BOARD_Y = 130

# Couleurs modernes
BACKGROUND = (244, 246, 250)
PANEL_BG = (255, 255, 255)
CARD_BG = (238, 242, 248)
TILE_COLOR = (222, 234, 252)
TILE_BORDER = (185, 205, 235)
GOAL_COLOR = (205, 242, 218)
GOAL_BORDER = (150, 215, 175)
EMPTY_COLOR = (226, 230, 238)
TEXT_COLOR = (30, 41, 59)
TEXT_MUTED = (100, 116, 139)
ACCENT_COLOR = (37, 99, 235)
ACCENT_GREEN = (22, 163, 74)
ACCENT_ORANGE = (217, 119, 6)
SHADOW_COLOR = (210, 215, 225)


def get_tile_rect(row, col):
    x = BOARD_X + col * (TILE_SIZE + GAP)
    y = BOARD_Y + row * (TILE_SIZE + GAP)
    return pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)


def tile_at(position):
    x, y = position
    for row in range(3):
        for col in range(3):
            rect = get_tile_rect(row, col)
            if rect.collidepoint(x, y):
                return row * 3 + col
    return None


def move_tile(state, index):
    """Échange la tuile cliquée avec la case vide si elles sont adjacentes."""
    if index is None or state[index] == 0:
        return state
    for neighbor in get_neighbors(state):
        if neighbor[index] == 0:
            return neighbor
    return state


def print_terminal_summary(start, path, exploration, h_name, h_func):
    """Affiche un compte-rendu clair et détaillé dans la console pour l'enseignant."""
    print("\n" + "=" * 55)
    print("        USTHB - FIA : RECHERCHE DE CHEMIN A*")
    print("=" * 55)
    print(f"Heuristique utilisée : {h_name.upper()}")
    print(f"Nombre total de nœuds explorés (CLOSED) : {len(exploration)}")
    if path:
        print(f"Longueur du chemin solution optimal : {len(path) - 1} coups")
        print("-" * 55)
        print("Étapes du chemin solution :")
        for step_i, state in enumerate(path):
            g = step_i
            h = h_func(state)
            f = g + h
            tag = (
                "Départ (Config. finale définie)"
                if step_i == 0
                else (
                    "Objectif atteint (Figure 1)"
                    if step_i == len(path) - 1
                    else f"Étape {step_i}"
                )
            )
            print(f"\n[{tag}] - g(n)={g}, h(n)={h}, f(n)={f}")
            for r in range(3):
                row_vals = state[r * 3 : r * 3 + 3]
                print("   " + " ".join("_" if t == 0 else str(t) for t in row_vals))
    print("=" * 55 + "\n")


def draw_board(screen, font, state, dragged_index=None, drag_offset=(0, 0)):
    is_goal = state == GOAL

    # Dessin de l'arrière-plan du plateau
    board_rect = pygame.Rect(
        BOARD_X - 10,
        BOARD_Y - 10,
        3 * TILE_SIZE + 2 * GAP + 20,
        3 * TILE_SIZE + 2 * GAP + 20,
    )
    pygame.draw.rect(screen, CARD_BG, board_rect, border_radius=16)

    # Dessin des tuiles non déplacées
    for index, tile in enumerate(state):
        if index == dragged_index:
            continue

        row = index // 3
        col = index % 3
        rect = get_tile_rect(row, col)

        if tile == 0:
            pygame.draw.rect(screen, EMPTY_COLOR, rect, border_radius=12)
        else:
            bg_col = GOAL_COLOR if is_goal else TILE_COLOR
            border_col = GOAL_BORDER if is_goal else TILE_BORDER
            pygame.draw.rect(screen, bg_col, rect, border_radius=12)
            pygame.draw.rect(screen, border_col, rect, width=2, border_radius=12)

            text = font.render(str(tile), True, TEXT_COLOR)
            screen.blit(text, text.get_rect(center=rect.center))

    # Dessin de la tuile en cours de glissement (drag & drop)
    if dragged_index is not None and state[dragged_index] != 0:
        orig_row = dragged_index // 3
        orig_col = dragged_index % 3
        orig_rect = get_tile_rect(orig_row, orig_col)
        drag_rect = orig_rect.move(drag_offset[0], drag_offset[1])

        # Ombre
        shadow_rect = drag_rect.move(4, 4)
        pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect, border_radius=12)

        # Tuile surélevée
        pygame.draw.rect(screen, (240, 245, 255), drag_rect, border_radius=12)
        pygame.draw.rect(screen, ACCENT_COLOR, drag_rect, width=2, border_radius=12)
        text = font.render(str(state[dragged_index]), True, TEXT_COLOR)
        screen.blit(text, text.get_rect(center=drag_rect.center))


def run_ui():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Taquin 3x3 - Recherche A* (FIA USTHB)")
    clock = pygame.time.Clock()

    title_font = pygame.font.Font(None, 34)
    font = pygame.font.Font(None, 44)
    header_font = pygame.font.Font(None, 24)
    info_font = pygame.font.Font(None, 22)
    small_font = pygame.font.Font(None, 19)

    # État initial conforme Figure 1
    current = GOAL
    path = None
    exploration = []
    mode = "manual"  # "manual", "solution", "exploration"
    index = 0
    message = "Glissez ou cliquez sur une tuile pour définir la configuration finale."

    # Heuristique : "manhattan" ou "misplaced"
    heuristic_name = "manhattan"

    # Drag and Drop
    dragged_tile = None
    drag_start_pos = (0, 0)
    drag_offset = (0, 0)

    # Lecture automatique (Auto-play)
    autoplay = False
    last_step_time = 0
    step_delay = 350  # millisecondes entre deux pas

    running = True

    while running:
        current_time = pygame.time.get_ticks()

        # Gestion de l'avancement automatique (Auto-play)
        if autoplay and current_time - last_step_time >= step_delay:
            last_step_time = current_time
            if mode == "solution" and path is not None:
                if index < len(path) - 1:
                    index += 1
                    current = path[index]
                else:
                    autoplay = False
                    message = "Objectif atteint !"
            elif mode == "exploration" and exploration:
                if index < len(exploration) - 1:
                    index += 1
                    current = exploration[index]["state"]
                else:
                    autoplay = False
                    message = "Fin de l'exploration."

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # R : Réinitialiser à l'état initial
                elif event.key == pygame.K_r:
                    current = GOAL
                    path = None
                    exploration = []
                    mode = "manual"
                    index = 0
                    autoplay = False
                    message = "Plateau réinitialisé à l'état initial (Figure 1)."

                # M : Mélanger aléatoirement (Shuffle)
                elif event.key == pygame.K_m:
                    current = shuffle_board(GOAL, moves=25)
                    path = None
                    exploration = []
                    mode = "manual"
                    index = 0
                    autoplay = False
                    message = "Plateau mélangé avec 25 coups aléatoires légaux."

                # H : Basculer d'heuristique (Manhattan / Mal placées)
                elif event.key == pygame.K_h:
                    if heuristic_name == "manhattan":
                        heuristic_name = "misplaced"
                    else:
                        heuristic_name = "manhattan"
                    path = None
                    exploration = []
                    mode = "manual"
                    index = 0
                    autoplay = False
                    message = f"Heuristique active : {heuristic_name.upper()}."

                # S : Lancer la recherche A*
                elif event.key == pygame.K_s:
                    autoplay = False
                    if not is_solvable(current):
                        path = None
                        exploration = []
                        mode = "manual"
                        message = "Configuration impossible à résoudre (parité d'inversions différente)."
                    elif current == GOAL:
                        path = [current]
                        exploration = []
                        mode = "manual"
                        message = "Le plateau est déjà dans l'état initial (Figure 1)."
                    else:
                        h_func = (
                            manhattan_distance
                            if heuristic_name == "manhattan"
                            else misplaced_tiles
                        )
                        path, exploration = astar(current, heuristic=h_func)
                        print_terminal_summary(
                            current, path, exploration, heuristic_name, h_func
                        )

                        if path is None:
                            mode = "manual"
                            message = "Aucun chemin trouvé."
                        else:
                            mode = "solution"
                            index = 0
                            current = path[0]
                            message = (
                                f"A* réussi : {len(path) - 1} coups, "
                                f"{len(exploration)} états explorés. Appuyez sur Espace pour jouer."
                            )

                # P : Basculer vers le chemin Solution
                elif event.key == pygame.K_p and path is not None:
                    mode = "solution"
                    index = 0
                    current = path[0]
                    message = f"Affichage du chemin solution (Longueur : {len(path) - 1} coups)."

                # E : Basculer vers l'Exploration
                elif event.key == pygame.K_e and exploration:
                    mode = "exploration"
                    index = 0
                    current = exploration[0]["state"]
                    message = f"Affichage de l'exploration ({len(exploration)} nœuds extraits de OPEN)."

                # ESPACE : Play / Pause Auto-play
                elif event.key == pygame.K_SPACE:
                    if mode in ("solution", "exploration") and (path or exploration):
                        autoplay = not autoplay
                        message = "Auto-play en cours..." if autoplay else "Auto-play en pause."

                # N : Étape suivante (Next)
                elif event.key == pygame.K_n:
                    autoplay = False
                    if mode == "solution" and path is not None:
                        if index < len(path) - 1:
                            index += 1
                            current = path[index]
                        else:
                            message = "Objectif atteint !"
                    elif mode == "exploration" and exploration:
                        if index < len(exploration) - 1:
                            index += 1
                            current = exploration[index]["state"]
                        else:
                            message = "Dernier état exploré atteint."

                # B : Étape précédente (Back)
                elif event.key == pygame.K_b:
                    autoplay = False
                    if mode == "solution" and path is not None:
                        if index > 0:
                            index -= 1
                            current = path[index]
                    elif mode == "exploration" and exploration:
                        if index > 0:
                            index -= 1
                            current = exploration[index]["state"]

            # Interaction Souris (Clic et Glisser-Déposer)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if mode == "manual":
                    clicked = tile_at(event.pos)
                    if clicked is not None and current[clicked] != 0:
                        dragged_tile = clicked
                        drag_start_pos = event.pos
                        drag_offset = (0, 0)

            elif event.type == pygame.MOUSEMOTION:
                if dragged_tile is not None:
                    drag_offset = (
                        event.pos[0] - drag_start_pos[0],
                        event.pos[1] - drag_start_pos[1],
                    )

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragged_tile is not None and mode == "manual":
                    dest_tile = tile_at(event.pos)
                    zero_idx = current.index(0)
                    dist = (drag_offset[0] ** 2 + drag_offset[1] ** 2) ** 0.5

                    # Déplacement valide si relâché sur la case vide ou si simple clic
                    should_move = False
                    if dist < 10 or dest_tile == zero_idx:
                        should_move = True
                    else:
                        # Direction du glissement vers la case vide
                        zero_row, zero_col = zero_idx // 3, zero_idx % 3
                        drag_row, drag_col = dragged_tile // 3, dragged_tile % 3
                        if abs(zero_row - drag_row) + abs(zero_col - drag_col) == 1:
                            should_move = True

                    if should_move:
                        new_state = move_tile(current, dragged_tile)
                        if new_state != current:
                            current = new_state
                            path = None
                            exploration = []
                            h_val = (
                                manhattan_distance(current)
                                if heuristic_name == "manhattan"
                                else misplaced_tiles(current)
                            )
                            message = f"Configuration modifiée. Heuristique h = {h_val}"

                dragged_tile = None
                drag_offset = (0, 0)

        # Affichage
        screen.fill(BACKGROUND)

        # Titre et Sous-titre
        title_surf = title_font.render("Taquin 3x3 - Recherche A*", True, TEXT_COLOR)
        screen.blit(title_surf, (BOARD_X - 10, 30))

        subtitle_surf = small_font.render(
            "Fondements de l'IA (USTHB) - Pr. Slimane LARABI", True, TEXT_MUTED
        )
        screen.blit(subtitle_surf, (BOARD_X - 10, 68))

        # Plateau
        draw_board(screen, font, current, dragged_tile, drag_offset)

        # Panneau Latéral
        panel_x = 420
        panel_y = 30
        panel_w = 380
        panel_h = 495

        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(screen, PANEL_BG, panel_rect, border_radius=16)
        pygame.draw.rect(screen, CARD_BG, panel_rect, width=2, border_radius=16)

        # En-tête : Badge du Mode
        mode_titles = {
            "manual": ("MODE MANUEL", TEXT_COLOR, CARD_BG),
            "solution": ("CHEMIN SOLUTION", (255, 255, 255), ACCENT_GREEN),
            "exploration": ("EXPLORATION DES NŒUDS", (255, 255, 255), ACCENT_ORANGE),
        }
        mode_label, badge_fg, badge_bg = mode_titles[mode]
        badge_rect = pygame.Rect(panel_x + 20, panel_y + 18, 220, 30)
        pygame.draw.rect(screen, badge_bg, badge_rect, border_radius=8)
        badge_text = header_font.render(mode_label, True, badge_fg)
        screen.blit(badge_text, badge_text.get_rect(center=badge_rect.center))

        if autoplay:
            play_badge = small_font.render("▶ AUTO-PLAY", True, ACCENT_COLOR)
            screen.blit(play_badge, (panel_x + 250, panel_y + 24))

        # Bloc Scores & États
        scores_y = panel_y + 65
        h_label = "Manhattan (h2)" if heuristic_name == "manhattan" else "Mal placées (h1)"

        if mode == "solution" and path is not None:
            cur_h = (
                manhattan_distance(current)
                if heuristic_name == "manhattan"
                else misplaced_tiles(current)
            )
            lines = [
                f"Étape : {index} / {len(path) - 1} coups",
                f"Coût g(n) : {index}",
                f"Heuristique h(n) : {cur_h}",
                f"Score f(n) = g + h : {index + cur_h}",
                f"Heuristique choisie : {h_label}",
            ]
        elif mode == "exploration" and exploration:
            item = exploration[index]
            lines = [
                f"Nœud exploré : {index + 1} / {len(exploration)}",
                f"Coût g(n) : {item['g']}",
                f"Heuristique h(n) : {item['h']}",
                f"Score f(n) = g + h : {item['f']}",
                f"Heuristique choisie : {h_label}",
            ]
        else:
            cur_h = (
                manhattan_distance(current)
                if heuristic_name == "manhattan"
                else misplaced_tiles(current)
            )
            solv = "Oui" if is_solvable(current) else "Non"
            lines = [
                f"Heuristique active : {h_label}",
                f"Valeur h(actuel) : {cur_h}",
                f"Configuration soluble : {solv}",
                f"États explorés au dernier run : {len(exploration)}",
            ]

        # Boîte de score
        score_box = pygame.Rect(panel_x + 20, scores_y, panel_w - 40, 115)
        pygame.draw.rect(screen, CARD_BG, score_box, border_radius=10)
        for i, line in enumerate(lines):
            line_surf = info_font.render(line, True, TEXT_COLOR)
            screen.blit(line_surf, (panel_x + 32, scores_y + 12 + i * 20))

        # Commandes
        cmd_y = scores_y + 130
        screen.blit(
            header_font.render("Commandes & Raccourcis", True, TEXT_COLOR),
            (panel_x + 20, cmd_y),
        )

        commands = [
            ("Clic / Glisser", "Déplacer une tuile vers le vide"),
            ("M", "Mélanger aléatoirement (25 coups légaux)"),
            ("H", "Changer d'heuristique (Manhattan / Mal placées)"),
            ("S", "Lancer la recherche A*"),
            ("P", "Afficher directement le chemin Solution"),
            ("E", "Afficher l'Exploration pas-à-pas"),
            ("N / B", "Étape suivante / précédente"),
            ("Espace", "Lecture automatique (Play / Pause)"),
            ("R", "Réinitialiser à l'état initial (Figure 1)"),
            ("Échap", "Quitter"),
        ]

        for i, (k, desc) in enumerate(commands):
            ky = cmd_y + 26 + i * 23
            k_surf = small_font.render(k, True, ACCENT_COLOR)
            desc_surf = small_font.render(desc, True, TEXT_MUTED)
            screen.blit(k_surf, (panel_x + 22, ky))
            screen.blit(desc_surf, (panel_x + 130, ky))

        # Barre de notification / message en bas à gauche
        msg_rect = pygame.Rect(BOARD_X - 10, 485, 3 * TILE_SIZE + 2 * GAP + 20, 42)
        pygame.draw.rect(screen, CARD_BG, msg_rect, border_radius=10)
        msg_surf = small_font.render(message[:65], True, TEXT_COLOR)
        screen.blit(msg_surf, (BOARD_X + 5, 498))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
