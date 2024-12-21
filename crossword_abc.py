from llm import *
from grid import *
from constants import *
from word_sorter import *
from crossword_ui import *
from crossword_export import *

class Crossword(ABC):
    def __init__(self, root):
        self.root = root
        self.llm_instance = LLM(MODEL)
        self.grid_size = DEFAULT_GRID_SIZE
        self.ui = CrosswordUI(self)
        self.ui.create_main_frames()
        self.ui.create_controls()
        self.ui.create_buttons()
        self.grid = Grid(self, self.ui.parent.crossword_frame, self.grid_size)
        self.exporter = CrosswordExport(self.grid, self.ui.parent.result_text, self.ui.parent.theme_entry)
        self.word_sorter = WordSorter(self.grid_size, self.grid.cells)
        self.is_generated = False
        self.is_solved = False

    @abstractmethod
    def _get_theme_and_word_count(self):
        pass

    @abstractmethod
    def _generate_grid_and_clues(self):
        pass

    @abstractmethod
    def _display_clues(self):
        pass

    @abstractmethod
    def generate_crossword(self):
        pass

    def increase_grid_size(self):
        self.grid.increase_grid_size()

    def decrease_grid_size(self):
        self.grid.decrease_grid_size()

    def _show_error(self, message, suggest_clear=False):
        full_message = message
        if suggest_clear:
            full_message += "\nPlease press 'Clear' to reset and try again."
        self.result_text.insert(tk.END, '\n'+full_message)
        self.result_text.update()

    def _display_crossword(self, word_positions, clue_indices):
        for cell_data in self.grid.cells.values():
            cell_data[WIDGET].config(bg=CROSSWORD_FRAME_BG, text="")

        self.grid.hidden_cells.clear()

        for (word, (start_row, start_col), direction) in word_positions:
            for i, char in enumerate(word):
                row = start_row + (i if direction == DIRECTION_VERTICAL else 0)
                col = start_col + (i if direction == DIRECTION_HORIZONTAL else 0)
                if (row, col) in self.grid.cells:
                    self.grid.cells[(row, col)][WIDGET].config(text="", fg=TEXT_COLOR, bg=INDEX_OUTLINE_COLOR)
                    self.grid.hidden_cells.append((row, col, char))

        self.grid.add_word_indices(word_positions, clue_indices)

    def solve_crossword(self):
        try:
            if not self.grid.hidden_cells:
                self.result_text.insert(tk.END, "\nThere are no hidden cells to reveal.")
                return
            for row, col, char in self.grid.hidden_cells:
                if (row, col) in self.grid.cells:
                    self.grid.cells[(row, col)][WIDGET].config(text=char, fg=TEXT_COLOR)
            self.grid.hidden_cells.clear()
            self.result_text.insert(tk.END, "\nThe crossword puzzle has been solved!")
            self.is_solved = True
        except Exception as e:
            self.result_text.insert(tk.END, f"\nError solving the crossword puzzle. {str(e)}\n")

    def clear_crossword(self):
        self.grid.clear_grid()
        self.ui.parent.result_text.delete(1.0, tk.END)
        self.ui.parent.theme_entry.delete(0, tk.END)
        self.ui.parent.word_count_entry.delete(0, tk.END)
        self.ui.parent.word_count_entry.insert(0, "1")
        current_mode = self.ui.parent.mode_var.get()
        self.ui.display_welcome_message(current_mode)
        self.is_generated = False 
        self.is_solved = False
    
    def toggle_mode(self):
        self.clear_crossword()
        mode = self.ui.parent.mode_var.get()
        if mode == CUSTOM_MODE_TEXT:
            self.ui.parent.word_count_label.grid_remove()
            self.ui.parent.word_count_entry.grid_remove()
        else:
            self.ui.parent.word_count_label.grid()
            self.ui.parent.word_count_entry.grid()
        self.ui.display_welcome_message(mode)
    
    def export_crossword(self):
        if not self.is_generated:
            self._show_error("The crossword puzzle must be generated before exporting.")
            return
        if not self.is_solved:
            self._show_error("The crossword puzzle must be solved before exporting.")
            return
        self.exporter.export_crossword()