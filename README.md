# The 8-Puzzle Solver with A* Search

An optimal 8-Puzzle (*Taquin*) solver implemented in Python with an interactive Pygame visualization, powered by the **A\* search algorithm**.

Built as part of the *Foundations of Artificial Intelligence (FIA)* course at **USTHB** (Faculty of Computer Science, AI Engineering).

---

## 🎯 Goal Configuration

The solver is designed to reach the classic **spiral configuration** (centered blank tile):

```text
+---+---+---+
| 1 | 2 | 3 |
+---+---+---+
| 8 |   | 4 |
+---+---+---+
| 7 | 6 | 5 |
+---+---+---+
```

The user can drag or click tiles to set any configuration, and A* finds the optimal sequence of moves back to this target state.

---

## ✨ Features

- **Optimal A\* Search Engine**: Guarantees the shortest path using priority queue (`OPEN`) and explored set (`CLOSED`).
- **Two Heuristics Supported**:
  - **Manhattan Distance ($h_2$)**: Sum of grid distances to goal positions (admissible, consistent, and dominant).
  - **Misplaced Tiles ($h_1$)**: Number of tiles out of place.
  - Press `H` to toggle between heuristics and compare pruning efficiency in real time.
- **Mathematical Solvability Check**:
  - Automatically verifies permutation inversion parity (Johnson & Story, 1879) to ensure reachability before searching.
- **Interactive Pygame UI**:
  - **Mouse interaction**: Drag-and-drop tiles smoothly or simply click them.
  - **Dual view modes**:
    - **Solution Mode (`P`)**: Step through the shortest path to victory.
    - **Exploration Mode (`E`)**: Inspect the search tree node-by-node with live $g(n)$, $h(n)$, and $f(n)$ scores.
  - **Auto-Play (`Space`)**: Watch the solution animate automatically.
  - **Random Scramble (`M`)**: Generates guaranteed-solvable boards in one keystroke.
- **Detailed Console Trace**: Prints ASCII boards and step metrics to the terminal for easy logging.

---

## ⌨️ Controls & Shortcuts

| Key / Action | Description |
| :--- | :--- |
| **Mouse Click / Drag** | Move an adjacent tile into the blank space |
| **`M`** | Scramble board randomly (25 valid moves) |
| **`S`** | Run the A* algorithm |
| **`P`** | Switch to **Solution Mode** (direct path) |
| **`E`** | Switch to **Exploration Mode** (all evaluated states) |
| **`N`** | Next step (forward by 1) |
| **`B`** | Previous step (back by 1) |
| **`Space`** | Toggle **Auto-Play** (play / pause) |
| **`H`** | Toggle heuristic between **Manhattan** and **Misplaced Tiles** |
| **`R`** | Reset board to the initial spiral configuration |
| **`Esc`** | Exit the game |

---

## 🚀 Installation & Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/ademboukabes/the-8-Puzzle-with-A-Search.git
cd the-8-Puzzle-with-A-Search
```

### 2. Install dependencies
Make sure you have Python 3.10+ installed:
```bash
pip install -r requirements.txt
```
*(or `pip install pygame-ce`)*

### 3. Run the application
```bash
python3 main.py
```

---

## 📁 Project Structure

```text
├── astar.py          # A* search algorithm (OPEN/CLOSED lists, heuristic scoring)
├── puzzle.py         # Board representation, state transitions, heuristics, parity check
├── ui.py             # Pygame graphical user interface and event handling
├── main.py           # Application entry point
├── requirements.txt  # Python package dependencies
└── README.md         # Project documentation
```

---

## 🔬 Heuristic Comparison

On an identical 13-move scrambled board:

| Metric | Misplaced Tiles ($h_1$) | Manhattan Distance ($h_2$) |
| :--- | :---: | :---: |
| **Solution Length** | 13 moves | 13 moves |
| **Explored States** | 186 nodes | **59 nodes (68% fewer)** |
| **Search Time** | ~24 ms | **~8 ms (3× faster)** |

Since Manhattan distance dominates misplaced tiles ($h_2(n) \ge h_1(n)$), it drastically reduces the explored state space while guaranteeing optimality.

---

## 📜 References

* Johnson, Wm. Woolsey, and Story, William E. *"Notes on the '15' Puzzle"*, American Journal of Mathematics, Vol. 2, No. 4 (1879), pp. 397-404.
* Course: *Fondements de l'Intelligence Artificielle (FIA)*, USTHB, Prof. Slimane LARABI.

---

## 👤 Author

* **Adem Boukabes** ([@ademboukabes](https://github.com/ademboukabes))
