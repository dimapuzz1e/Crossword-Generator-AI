from crossword_abc import *

class CrosswordCustom(Crossword):
    def __init__(self, result_text, theme_entry, grid, llm_instance, word_sorter,exporter):
        self.words = []
        self.grid = grid
        self.result_text = result_text
        self.theme_entry = theme_entry
        self.llm_instance = llm_instance
        self.word_sorter = word_sorter 
        self.exporter = exporter

    def _get_theme_and_word_count(self):
        theme = self._validate_and_get_theme()
        words = self._validate_and_get_words()
        return theme, words
    
    def validate_words(self, words: list[str]) -> list[str]:
        invalid_words = self.llm_instance.validate_word_list(words)
        return invalid_words
    
    def _generate_prompt(self, theme, words):
        prompt = self.llm_instance.generate_custom_crossword_prompt(theme, words)
        if not prompt:
            raise ValueError("Failed to generate the crossword prompt.")
        return prompt

    def _validate_and_get_theme(self):
        theme = self.theme_entry.get().strip()
        if not theme:
            self._show_error("Please indicate the topic of the crossword puzzle!", suggest_clear=True)
            raise ValueError("Theme is missing.")
        if len(theme) < 3 or len(theme) > 20:
            self._show_error("The theme must be between 3 and 20 characters!", suggest_clear=True)
            raise ValueError("Theme length is incorrect.")
        if theme.isdigit():
            self._show_error("The theme cannot be just a number!", suggest_clear=True)
            raise ValueError("Theme cannot be just a number.")
        if re.match(r'([a-zA-Z])\1*$', theme):
            self._show_error("The theme cannot be made up of only one repeated letter (e.g., 'qqq').", 
                            suggest_clear=True)
            raise ValueError("Theme cannot consist of only one repeated letter.")
        if not self.llm_instance.validate_theme(theme):
            self._show_error("The theme is not meaningful or coherent!", suggest_clear=True)
            raise ValueError("Invalid theme: lacks meaning or coherence.")
        return theme

    def _validate_and_get_words(self):
        input_text = self.result_text.get(1.0, tk.END).strip()
        if CUSTOM_WELCOME in input_text:
            input_text = input_text.replace(CUSTOM_WELCOME, "").strip()
        if not input_text:
            self._show_error("Enter a list of words separated by commas to create a crossword puzzle.", 
                            suggest_clear=True)
            raise ValueError("Word list is empty.")
        words = [word.strip().upper() for word in input_text.split(",") if word.strip()]
        if not words:
            self._show_error("The word list is empty or incorrect. Try again.", suggest_clear=True)
            raise ValueError("No valid words found.")
        if len(words) > self.grid.grid_size:
            self._show_error(f"Too many words! The grid can only accommodate {self.grid.grid_size} words.",
                            suggest_clear=True)
            raise ValueError("Word count exceeds grid size.")
        
        invalid_words = self.validate_words(words)
        if invalid_words:
            self._show_error(f"The following words are invalid or meaningless: {', '.join(invalid_words)}",
                            suggest_clear=True)
            raise ValueError(f"Invalid words: {', '.join(invalid_words)}")
        return words

    def _generate_grid_and_clues(self, prompt, words):
        response = self.llm_instance.model.generate_content(prompt)
        if not response or not response.text:
            raise ValueError("The response from the model is blank or incorrect.")
        clues = eval(response.text)
        grid, word_positions = self.word_sorter.sort_and_place_words([word for word, _ in clues])
        if not grid:
            raise ValueError("Failed to place the words on the grid.")
        return clues, word_positions

    def _display_clues(self, clues, word_positions, clue_indices):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "The crossword puzzle has been created:\n\n")
        for word, question in clues:
            for placed_word, (start_row, start_col), direction in word_positions:
                if word == placed_word:
                    direction_str = DIRECTION_VERTICAL if direction == DIRECTION_VERTICAL else DIRECTION_HORIZONTAL
                    index = clue_indices[word]
                    self.result_text.insert(
                        tk.END, f"{index}. {question} ({direction_str}, {len(word)} letters)\n"
                    )
                    break

    def clear_data(self):
        self.words = []
        self.grid.clear_grid()
        self.grid.hidden_cells.clear()
        self.word_sorter = WordSorter(self.grid.grid_size, self.grid.cells)

    def generate_crossword(self):
        try:
            self.clear_data()
            theme, words = self._get_theme_and_word_count()
            self.result_text.insert(tk.END, "\nGenerating crossword...\n")
            self.result_text.update()
            prompt = self._generate_prompt(theme, words)
            clues, word_positions = self._generate_grid_and_clues(prompt, words)
            clue_indices = {word: i + 1 for i, (word, _) in enumerate(clues)}
            self._display_crossword(word_positions, clue_indices)
            self._display_clues(clues, word_positions, clue_indices)
            self.exporter.set_word_positions(word_positions, clue_indices)
        except Exception as e:
            print(f"Error creating a crossword puzzle: {str(e)}")

class CrosswordAuto(Crossword):
    def __init__(self, root):
        super().__init__(root)
        self.custom_mode_handler = CrosswordCustom(
            self.ui.parent.result_text, 
            self.ui.parent.theme_entry, 
            self.grid,
            self.llm_instance,
            self.word_sorter,
            self.exporter
        )
        self.ui.display_welcome_message(AUTO_MODE_TEXT)

    def _get_theme_and_word_count(self):
        theme = self._validate_and_get_theme()
        word_count = self._validate_and_get_word_count()
        return theme, word_count

    def _validate_and_get_theme(self):
        theme = self.ui.parent.theme_entry.get().strip()

        if not theme:
            self._show_error("Please indicate the topic of the crossword puzzle!", suggest_clear=True)
            raise ValueError("Theme is missing.")
        if len(theme) < 3 or len(theme) > 20:
            self._show_error("The theme must be between 3 and 20 characters!", suggest_clear=True)
            raise ValueError("Theme length is incorrect.")
        if theme.isdigit():
            self._show_error("The theme cannot be just a number!", suggest_clear=True)
            raise ValueError("Theme cannot be just a number.")
        if re.match(r'([a-zA-Z])\1*$', theme):
            self._show_error("The theme cannot be made up of only one repeated letter (e.g., 'qqq').", 
                            suggest_clear=True)
            raise ValueError("Theme cannot consist of only one repeated letter.")
        if not self.llm_instance.validate_theme(theme):
            self._show_error("The theme is not meaningful or coherent!", suggest_clear=True)
            raise ValueError("Invalid theme: lacks meaning or coherence.")
        return theme

    def _validate_and_get_word_count(self):
        word_count = self.ui.parent.word_count_entry.get()

        if not word_count.isdigit() or int(word_count) <= 0:
            self._show_error("Word count must be a positive integer!", suggest_clear=True)
            raise ValueError("Word count must be a positive integer.")
        word_count = int(word_count)
        if word_count > self.grid.grid_size:
            self._show_error("Word count cannot exceed the grid size!", suggest_clear=True)
            raise ValueError(f"Word count cannot exceed the grid size.")
        return word_count

    def _generate_grid_and_clues(self, theme, word_count):
        attempts = 3  
        for attempt in range(attempts):
            result = self.llm_instance.prompt_output(theme, word_count)
            clues = eval(result)
            if not clues or not isinstance(clues, list):
                continue  
            words = [word for word, _ in clues]
            if len(words) < word_count:
                if attempt == attempts - 1:
                    raise ValueError(f"Could not generate enough words for the theme after {attempts} attempts!")
                continue  
            if len(words) > word_count:
                words = words[:word_count]
                clues = clues[:word_count]
            word_sorter = WordSorter(self.grid.grid_size)
            grid, word_positions = word_sorter.sort_and_place_words(words)
            if grid:
                clue_indices = {word: idx for idx, (word, _) in enumerate(clues, 1)}
                return clues, word_positions, clue_indices
        raise ValueError("Failed to generate a valid crossword grid after multiple attempts.")

    def _display_clues(self, clues, word_positions, clue_indices):
        self.ui.parent.result_text.delete(1.0, tk.END)
        self.ui.display_message("The crossword puzzle has been created:\n\n")
        for i, (word, question) in enumerate(clues, start=1):
            for placed_word, (start_row, start_col), direction in word_positions:
                if word == placed_word:
                    direction_str = DIRECTION_VERTICAL if direction == DIRECTION_VERTICAL else DIRECTION_HORIZONTAL
                    index = clue_indices[word]  
                    self.ui.display_message(
                        f"{index}. {question} ({direction_str}, {len(word)} letters)"
                    )
                    break

    def generate_crossword(self):
        if self.ui.parent.mode_var.get() == CUSTOM_MODE_TEXT:
            self.custom_mode_handler.generate_crossword()
            self.is_generated = True
            self.is_solved = False
        else:
            try:
                theme, word_count = self._get_theme_and_word_count()
                self.ui.parent.result_text.insert(tk.END, "\nGenerating crossword...\n")
                self.ui.parent.result_text.update() 
                clues, word_positions, clue_indices = self._generate_grid_and_clues(theme, word_count)
                self._display_crossword(word_positions, clue_indices)
                self._display_clues(clues, word_positions, clue_indices)
                self.exporter.set_word_positions(word_positions, clue_indices)
                self.is_generated = True
                self.is_solved = False
            except Exception as e:
                print(f"Error creating a crossword puzzle: {str(e)}")