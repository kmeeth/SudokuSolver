from math import isqrt

import z3


def solve(grid):
    """Solve an N x N Sudoku. `grid` is a list of N rows of N ints (0 = empty).

    Returns the solved grid as a list of lists, or None if unsolvable.

    Uses a boolean one-hot encoding: x[r][c][d] is true iff cell (r, c) holds
    digit d+1. Every rule becomes an "exactly one true" cardinality constraint,
    which Z3's SAT/pseudo-boolean core handles much faster than the integer
    Distinct encoding on hard or under-constrained puzzles.
    """
    n = len(grid)
    k = isqrt(n)
    if k * k != n:
        raise ValueError(f"grid size {n} is not a perfect square")
    if any(len(row) != n for row in grid):
        raise ValueError("grid must be square (N rows of N columns)")

    # x[r][c][d] is true iff cell (r, c) contains digit d+1.
    x = [[[z3.Bool(f"x_{r}_{c}_{d}") for d in range(n)]
          for c in range(n)] for r in range(n)]

    s = z3.Solver()

    def exactly_one(bools):
        return z3.PbEq([(b, 1) for b in bools], 1)

    # Each cell holds exactly one digit.
    for r in range(n):
        for c in range(n):
            s.add(exactly_one(x[r][c]))

    # Each digit appears exactly once per row, column, and k x k box.
    for d in range(n):
        for r in range(n):
            s.add(exactly_one([x[r][c][d] for c in range(n)]))
        for c in range(n):
            s.add(exactly_one([x[r][c][d] for r in range(n)]))
        for br in range(0, n, k):
            for bc in range(0, n, k):
                s.add(exactly_one(
                    [x[br + dr][bc + dc][d] for dr in range(k) for dc in range(k)]))

    # Pin the given clues.
    for r in range(n):
        for c in range(n):
            if grid[r][c] != 0:
                s.add(x[r][c][grid[r][c] - 1])

    if s.check() != z3.sat:
        return None

    m = s.model()
    return [[next(d + 1 for d in range(n) if z3.is_true(m[x[r][c][d]]))
             for c in range(n)] for r in range(n)]


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
