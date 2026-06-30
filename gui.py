"""Tkinter GUI for the generalized Z3 Sudoku solver.

Enter clues on the board, press Solve, and Z3 fills the rest. The board size
is driven by the box dimension k (k x k boxes => N = k*k grid), so any
perfect-square Sudoku is reachable: k=2 -> 4x4, k=3 -> 9x9, k=4 -> 16x16, ...
"""

import tkinter as tk
from tkinter import messagebox

from solver import solve

GIVEN_COLOR = "#000000"   # clues the user typed
SOLVED_COLOR = "#1565c0"  # cells filled in by the solver


class SudokuGUI:
    def __init__(self, root, k=3):
        self.root = root
        self.root.title("Sudoku Solver")
        self.k = k
        self.n = k * k
        self.cells = []          # n x n grid of Entry widgets
        self.givens = set()      # (r, c) cells the user entered, for coloring

        self._build_controls()

        # Scrollable container so large boards stay usable.
        body = tk.Frame(root)
        body.grid(row=1, column=0, sticky="nsew")
        root.rowconfigure(1, weight=1)
        root.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(body, highlightthickness=0)
        vbar = tk.Scrollbar(body, orient="vertical", command=self.canvas.yview)
        hbar = tk.Scrollbar(body, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vbar.grid(row=0, column=1, sticky="ns")
        hbar.grid(row=1, column=0, sticky="ew")
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)

        self.board = tk.Frame(self.canvas, bg="#888888")
        self.canvas.create_window((0, 0), window=self.board, anchor="nw")
        self.board.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self._build_grid()

    def _build_controls(self):
        bar = tk.Frame(self.root)
        bar.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        tk.Label(bar, text="Box size k:").pack(side="left")
        self.k_var = tk.IntVar(value=self.k)
        tk.Spinbox(bar, from_=2, to=8, width=3, textvariable=self.k_var).pack(
            side="left", padx=(2, 8)
        )
        tk.Button(bar, text="Apply Size", command=self.apply_size).pack(side="left", padx=2)
        tk.Button(bar, text="Solve", command=self.solve_puzzle).pack(side="left", padx=2)
        tk.Button(bar, text="Reset", command=self.reset).pack(side="left", padx=2)

        self.status = tk.Label(bar, text="", fg="#555555")
        self.status.pack(side="left", padx=12)

    def _build_grid(self):
        for child in self.board.winfo_children():
            child.destroy()

        n, k = self.n, self.k
        self.cells = [[None] * n for _ in range(n)]
        self.givens.clear()
        vcmd = (self.root.register(self._validate), "%P")
        width = 2 if n <= 9 else len(str(n)) + 1

        for r in range(n):
            for c in range(n):
                # Wider gap on box boundaries draws the sub-grid lines.
                left = 4 if c % k == 0 and c != 0 else 1
                top = 4 if r % k == 0 and r != 0 else 1
                e = tk.Entry(
                    self.board, width=width, justify="center",
                    font=("Consolas", 16), relief="solid", borderwidth=1,
                    validate="key", validatecommand=vcmd,
                    disabledforeground=SOLVED_COLOR,
                )
                e.grid(row=r, column=c, padx=(left, 1), pady=(top, 1), ipady=4)
                self.cells[r][c] = e

        # Size the viewport to the board, capped so huge grids stay scrollable.
        self.board.update_idletasks()
        self.canvas.config(
            width=min(self.board.winfo_reqwidth(), 1100),
            height=min(self.board.winfo_reqheight(), 800),
        )

    def _validate(self, proposed):
        """Allow only empty or an integer in 1..N while typing."""
        if proposed == "":
            return True
        if not proposed.isdigit():
            return False
        return 1 <= int(proposed) <= self.n

    def _set_cell(self, r, c, text, color):
        """Programmatically set a cell's value (validation off during the edit)."""
        e = self.cells[r][c]
        e.config(validate="none", state="normal")
        e.delete(0, "end")
        if text:
            e.insert(0, text)
        e.config(fg=color, validate="key")

    def _read_grid(self):
        grid = []
        for r in range(self.n):
            row = []
            for c in range(self.n):
                txt = self.cells[r][c].get().strip()
                row.append(int(txt) if txt else 0)
            grid.append(row)
        return grid

    def apply_size(self):
        k = self.k_var.get()
        if k < 2:
            messagebox.showerror("Invalid size", "Box size k must be at least 2.")
            return
        self.k, self.n = k, k * k
        self._build_grid()
        self.status.config(text=f"{self.n}x{self.n} board ({k}x{k} boxes)")

    def reset(self):
        for r in range(self.n):
            for c in range(self.n):
                self._set_cell(r, c, "", GIVEN_COLOR)
        self.givens.clear()
        self.status.config(text="Cleared")

    def solve_puzzle(self):
        grid = self._read_grid()
        # Remember the user's clues so solver-filled cells render differently.
        self.givens = {(r, c) for r in range(self.n) for c in range(self.n) if grid[r][c]}

        self.status.config(text="Solving...")
        self.root.update_idletasks()

        try:
            solution = solve(grid)
        except ValueError as exc:
            self.status.config(text="")
            messagebox.showerror("Invalid grid", str(exc))
            return

        if solution is None:
            self.status.config(text="")
            messagebox.showinfo("No solution", "This puzzle has no solution.")
            return

        for r in range(self.n):
            for c in range(self.n):
                color = GIVEN_COLOR if (r, c) in self.givens else SOLVED_COLOR
                self._set_cell(r, c, str(solution[r][c]), color)
        self.status.config(text="Solved")


def main():
    root = tk.Tk()
    SudokuGUI(root, k=3)
    root.mainloop()


if __name__ == "__main__":
    main()
