from math import isqrt

import z3


def solve(grid):
    """Solve an N x N Sudoku. `grid` is a list of N rows of N ints (0 = empty).

    Returns the solved grid as a list of lists, or None if unsolvable.
    """
    n = len(grid)
    k = isqrt(n)
    if k * k != n:
        raise ValueError(f"grid size {n} is not a perfect square")
    if any(len(row) != n for row in grid):
        raise ValueError("grid must be square (N rows of N columns)")

    # One integer variable per cell, each constrained to 1..N.
    cells = [[z3.Int(f"c_{r}_{c}") for c in range(n)] for r in range(n)]

    s = z3.Solver()

    for r in range(n):
        for c in range(n):
            s.add(cells[r][c] >= 1, cells[r][c] <= n)

    # Rows and columns must each contain distinct values.
    for i in range(n):
        s.add(z3.Distinct(cells[i]))               # row i
        s.add(z3.Distinct([cells[r][i] for r in range(n)]))  # column i

    # Each k x k box must contain distinct values.
    for br in range(0, n, k):
        for bc in range(0, n, k):
            box = [cells[br + dr][bc + dc] for dr in range(k) for dc in range(k)]
            s.add(z3.Distinct(box))

    # Pin the given clues. This is the only part of the spec that is specific to the given example.
    for r in range(n):
        for c in range(n):
            if grid[r][c] != 0:
                s.add(cells[r][c] == grid[r][c])

    if s.check() != z3.sat:
        return None

    m = s.model()
    return [[m[cells[r][c]].as_long() for c in range(n)] for r in range(n)]


def format_grid(grid):
        """Render a grid as a string with box separators."""
        n = len(grid)
        k = isqrt(n)
        width = len(str(n))
        lines = []
        for r in range(n):
            if r > 0 and r % k == 0:
                lines.append("")
            cells = []
            for c in range(n):
                sep = "  " if c > 0 and c % k == 0 else " "
                cells.append((sep if c > 0 else "") + str(grid[r][c]).rjust(width))
            lines.append("".join(cells))
        return "\n".join(lines)


if __name__ == "__main__":
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]

    solution = solve(puzzle)
    if solution is None:
        print("No solution.")
    else:
        print(format_grid(solution))
