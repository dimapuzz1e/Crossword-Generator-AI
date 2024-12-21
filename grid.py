from constants import *

class Grid:
    
    def __init__(self, parent, frame, grid_size):
        self.cells = {}
        self.frame = frame
        self.parent = parent
        self.cell_size = None
        self.index_labels = []
        self.hidden_cells = []
        self.grid_size = grid_size
        self.create_grid(grid_size)
        self.update_max_words()
        self.max_size_reached = False
        self.min_size_reached = False

    def create_grid(self, size):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.cells = {}
        self.cell_size = min(FIXED_WIDTH // size, FIXED_HEIGHT // size)
        frame_width = self.cell_size * size
        frame_height = self.cell_size * size
        self.frame.config(width=frame_width, height=frame_height)
        for i in range(size):
            self.frame.rowconfigure(i, weight=WEIGHT, minsize=self.cell_size)
            for j in range(size):
                self.frame.columnconfigure(j, weight=WEIGHT, minsize=self.cell_size)
                cell = tk.Label(
                    self.frame,
                    text="",
                    relief=FONT_STYLE_SOLID,
                    bg=DEFAULT_CELL_COLOR,
                    width=self.cell_size // 10,
                    height=self.cell_size // CELL_TO_MIN
                )
                cell.grid(row=i, column=j, sticky=STICKY_NSEW)
                self.cells[(i, j)] = {WIDGET: cell, SELECTED: False}

    def increase_grid_size(self):
        if self.grid_size < MAX_GRID_SIZE:
            self.parent.clear_crossword() 
            self.grid_size += GRID_SIZE_STEP
            self.create_grid(self.grid_size)
            self.update_max_words()
            self.parent.grid_size_label.config(text=f"Grid size: {self.grid_size}x{self.grid_size}")
            self.max_size_reached = False
        elif not self.max_size_reached:
            self.parent.ui.display_message("\nThe maximum grid size has been reached!")
            self.max_size_reached = True  

    def decrease_grid_size(self):
        if self.grid_size > MIN_GRID_SIZE:
            self.parent.clear_crossword() 
            self.grid_size -= GRID_SIZE_STEP
            self.create_grid(self.grid_size)
            self.update_max_words()
            self.parent.grid_size_label.config(text=f"Grid size: {self.grid_size}x{self.grid_size}")
            self.min_size_reached = False
        elif not self.min_size_reached:
            self.parent.ui.display_message("\nThe minimum grid size has been reached!")
            self.min_size_reached = True 

    def update_max_words(self):
        max_words = self.grid_size
        self.parent.max_words_label.config(text=f"Max words: {max_words}")
        self.parent.word_count_entry.config(to=max_words)

    def add_word_indices(self, word_positions, clue_indices=None):
        for index_label in self.index_labels:
            index_label.destroy()
        self.index_labels = []

        font_size = max(self.cell_size // 16, MIN_FONT_SIZE)
        bg_radius = self.cell_size // MIN_FONT_SIZE
        for i, (word, (start_row, start_col), direction) in enumerate(word_positions, start=1):
            index = clue_indices.get(word, i) if clue_indices else i 
            if (start_row, start_col) in self.cells:
                widget = self.cells[(start_row, start_col)][WIDGET]
                x = widget.winfo_x() + self.cell_size // CELL_TO_MIN
                y = widget.winfo_y() + self.cell_size // CELL_TO_MIN
                index_canvas = tk.Canvas(
                    self.frame,
                    width=bg_radius * RADIUS_TO_MIN,
                    height=bg_radius * RADIUS_TO_MIN,
                    bg=DEFAULT_CELL_COLOR,
                    highlightthickness=0
                )
                index_canvas.place(x=x, y=y)
                index_canvas.create_oval(
                    0, 0, bg_radius * RADIUS_TO_MIN, bg_radius * RADIUS_TO_MIN,
                    fill=INDEX_BG_COLOR, outline=INDEX_OUTLINE_COLOR
                )
                index_canvas.create_text(
                    bg_radius, bg_radius,
                    text=str(index),
                    fill=FONT_COLOR,
                    font=(FONT_NAME, font_size, FONT_STYLE)
                )
                self.index_labels.append(index_canvas)

    def clear_grid(self):
        for cell_data in self.cells.values():
            cell_data[WIDGET].config(bg=DEFAULT_CELL_COLOR, text="")
            cell_data[SELECTED] = False
        for index_label in self.index_labels:
            index_label.destroy()
        self.index_labels = []