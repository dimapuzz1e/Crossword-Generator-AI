from constants import *

class WordSorter:
    
    def __init__(self, grid_size, cells=None):
        self.grid_size = grid_size
        self.grid = [["" for _ in range(grid_size)] for _ in range(grid_size)]
        self.word_positions = []
        self.cells = cells or {}

    def is_word_placeable(self, word, start_row, start_col, direction):
        delta_row = 1 if direction == DIRECTION_VERTICAL else 0
        delta_col = 1 if direction == DIRECTION_HORIZONTAL else 0
        len_word = len(word)
        for i in range(len_word):
            row = start_row + i * delta_row
            col = start_col + i * delta_col
            if not (0 <= row < self.grid_size and 0 <= col < self.grid_size):
                return False
            cell_char = self.grid[row][col]
            if cell_char not in ('', word[i]):
                return False
            adjacent_positions = []
            if direction == DIRECTION_HORIZONTAL:
                adjacent_positions.extend([
                    (row - 1, col),
                    (row + 1, col)
                ])
            else:
                adjacent_positions.extend([
                    (row, col - 1),
                    (row, col + 1)
                ])
            for adj_row, adj_col in adjacent_positions:
                if 0 <= adj_row < self.grid_size and 0 <= adj_col < self.grid_size:
                    adj_char = self.grid[adj_row][adj_col]
                    if adj_char != '':
                        if cell_char == '':
                            return False
        before_row = start_row - delta_row
        before_col = start_col - delta_col
        if 0 <= before_row < self.grid_size and 0 <= before_col < self.grid_size:
            if self.grid[before_row][before_col] != '':
                return False
        after_row = start_row + len_word * delta_row
        after_col = start_col + len_word * delta_col
        if 0 <= after_row < self.grid_size and 0 <= after_col < self.grid_size:
            if self.grid[after_row][after_col] != '':
                return False
        return True
    
    def add_word_to_grid(self, word, start_row, start_col, direction):
        for i, char in enumerate(word):
            row = start_row + (i if direction == DIRECTION_VERTICAL else 0)
            col = start_col + (i if direction == DIRECTION_HORIZONTAL else 0)
            self.grid[row][col] = char
        self.word_positions.append((word, (start_row, start_col), direction))

    def find_best_placement(self, word):
        best_score = -float('inf')
        best_position = None
        center = self.grid_size / 2.0
        positions = [(row, col) for row in range(self.grid_size) for col in range(self.grid_size)]
        positions.sort(key=lambda pos: ((pos[0] - center) ** 2 + (pos[1] - center) ** 2))
        for row, col in positions:
            for direction in [DIRECTION_HORIZONTAL, DIRECTION_VERTICAL]:
                if self.is_word_placeable(word, row, col, direction):
                    score = self.calculate_overlap_score(word, row, col, direction)
                    if score > best_score:
                        best_score = score
                        best_position = (row, col, direction)

        return best_position

    def calculate_overlap_score(self, word, start_row, start_col, direction):
        score = 0
        for i, char in enumerate(word):
            row = start_row + (i if direction == DIRECTION_VERTICAL else 0)
            col = start_col + (i if direction == DIRECTION_HORIZONTAL else 0)
            if self.grid[row][col] == char:
                score += 2
            elif self.grid[row][col] == '':
                score += 1
            else:
                return -1

        center = self.grid_size / 2.0
        word_center_row = start_row + (len(word) / 2.0 if direction == DIRECTION_VERTICAL else 0)
        word_center_col = start_col + (len(word) / 2.0 if direction == DIRECTION_HORIZONTAL else 0)
        distance = ((word_center_row - center) ** 2 + (word_center_col - center) ** 2) ** 0.5
        DISTANCE_WEIGHT = 0.1
        score -= distance * DISTANCE_WEIGHT
        return score

    def sort_and_place_words(self, words):
        center = self.grid_size // 2
        for word in sorted(words, key=len, reverse=True):
            if not self.word_positions:
                self.add_word_to_grid(word, center, center - len(word) // 2, DIRECTION_HORIZONTAL)
            else:
                best_position = self.find_best_placement(word)
                if best_position:
                    row, col, direction = best_position
                    self.add_word_to_grid(word, row, col, direction)
                else:
                    print(f"Could not place the word: {word}")
        return self.grid, self.word_positions