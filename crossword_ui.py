from constants import *

class CrosswordUI:

    def __init__(self, parent):
        self.parent = parent
        self.parent.root.resizable(False, False)

    def create_main_frames(self):
        self.parent.main_frame = tk.Frame(self.parent.root)
        self.parent.main_frame.pack(fill=tk.BOTH, expand=True)

        self.parent.crossword_frame = tk.Frame(
            self.parent.main_frame, 
            bg=CROSSWORD_FRAME_BG, 
            width=CROSSWORD_FRAME_WIDTH, 
            height=CROSSWORD_FRAME_HEIGHT
        )
        self.parent.crossword_frame.grid(row=SECOND_ROW, column=FIRST_COLUMN, padx=PARENT_PADDING, pady=PARENT_PADDING, sticky=STICKY_NSEW)
        self.parent.crossword_frame.grid_propagate(False)

        self.parent.left_buttons_frame = tk.Frame(self.parent.main_frame)
        self.parent.left_buttons_frame.grid(row=FIRST_ROW, column=FIRST_COLUMN, padx=PARENT_PADDING, pady=PARENT_PADDING, sticky=STICKY_NW)

        self.parent.controls_frame = tk.Frame(self.parent.main_frame, width=CONTROLS_FRAME_WIDTH)
        self.parent.controls_frame.grid(row=FIRST_ROW, column=SECOND_COLUMN, rowspan=ROWSPAN, padx=PARENT_PADDING, pady=PARENT_PADDING, sticky=STICKY_N)
        self.parent.controls_frame.grid_propagate(False)

    def create_controls(self):
        self.parent.input_frame = tk.Frame(self.parent.controls_frame)
        self.parent.input_frame.pack()

        self.parent.theme_label = tk.Label(self.parent.input_frame, text="Topic:")
        self.parent.theme_label.grid(row=FIRST_ROW, column=FIRST_COLUMN, padx=ENTRY_PADDING)

        def validate_theme_input(event):
            char = event.char  
            current_text = self.parent.theme_entry.get()
            if event.keysym in ["BackSpace", "Delete"]:
                return True
            if char.isascii() and (char.isalpha() or char == ',' or char.isspace() or char.isdigit()):
                if '  ' in current_text + char:
                    return "break" 
                return True
            return "break"

        self.parent.theme_entry = tk.Entry(
            self.parent.input_frame
        )
        self.parent.theme_entry.grid(row=FIRST_ROW, column=SECOND_COLUMN, padx=ENTRY_PADDING)
        self.parent.theme_entry.bind("<KeyPress>", validate_theme_input)

        self.parent.word_count_label = tk.Label(self.parent.input_frame, text="Word Count:")
        self.parent.word_count_label.grid(row=FIRST_ROW, column=THIRD_COLUMN, padx=ENTRY_PADDING)

        def validate_number_input(value):
            if value == "":  
                return True
            if value.isdigit() and int(value) <= 99:  
                return True
            return False
        
        validate_number_command = self.parent.root.register(validate_number_input)

        self.parent.word_count_entry = tk.Spinbox(
            self.parent.input_frame,
            from_=WORD_COUNT_MIN,
            to=WORD_COUNT_MAX,
            width=WORD_COUNT_WIDTH,
            validate="key",
            validatecommand=(validate_number_command, "%P") 
        )
        self.parent.word_count_entry.grid(row=FIRST_ROW, column=FOURTH_COLUMN, padx=ENTRY_PADDING)
        
        self.parent.spacer_frame = tk.Frame(self.parent.controls_frame, height=SPACER_HEIGHT)
        self.parent.spacer_frame.pack()

        def validate_result_text_input(event):
            if self.parent.mode_var.get() == AUTO_MODE_TEXT:
                return "break" 
            char = event.char
            current_text = event.widget.get("1.0", "end-1c")
            if event.keysym in ["BackSpace", "Delete", "Return"]:
                return True
            if char.isascii() and (char.isalpha() or char == ',' or char.isspace()):
                if '  ' in current_text + char:
                    return "break"  
                return True
            return "break"

        self.parent.result_text = tk.Text(
            self.parent.controls_frame,
            height=RESULT_TEXT_HEIGHT,
            width=RESULT_TEXT_WIDTH
        )
        self.parent.result_text.pack(pady=(PADX, PADX_W))
        self.parent.result_text.bind("<KeyPress>", validate_result_text_input)

    def create_buttons(self):
        self.parent.zoom_in_button = tk.Button(
            self.parent.left_buttons_frame, text=PLUS, command=self.parent.increase_grid_size
        )
        self.parent.zoom_in_button.grid(row=FIRST_ROW, column=FIRST_COLUMN, padx=ZOOM_BUTTON_PADDING)

        self.parent.zoom_out_button = tk.Button(
            self.parent.left_buttons_frame, text=MINUS, command=self.parent.decrease_grid_size
        )
        self.parent.zoom_out_button.grid(row=FIRST_ROW, column=SECOND_COLUMN, padx=ZOOM_BUTTON_PADDING)

        self.parent.mode_var = tk.StringVar(value=AUTO_MODE_TEXT)

        self.parent.auto_radio = tk.Radiobutton(
            self.parent.left_buttons_frame, 
            text=AUTO_MODE_TEXT, 
            variable=self.parent.mode_var, 
            value=AUTO_MODE_TEXT,
            command=self.parent.toggle_mode
        )
        self.parent.auto_radio.grid(row=FIRST_ROW, column=THIRD_COLUMN, padx=RADIOBUTTON_PADDING)

        self.parent.custom_radio = tk.Radiobutton(
            self.parent.left_buttons_frame, 
            text=CUSTOM_MODE_TEXT, 
            variable=self.parent.mode_var, 
            value=CUSTOM_MODE_TEXT,
            command=self.parent.toggle_mode
        )
        self.parent.custom_radio.grid(row=FIRST_ROW, column=FOURTH_COLUMN, padx=RADIOBUTTON_PADDING)

        self.parent.grid_size_label = tk.Label(
            self.parent.left_buttons_frame,
            text=f"Grid size: {self.parent.grid_size}x{self.parent.grid_size}", 
            font=(FONT_NAME, LABEL_FONT)
        )
        self.parent.grid_size_label.grid(row=FIRST_ROW, column=FIFTH_COLUMN, padx=PADX)

        self.parent.max_words_label = tk.Label(
            self.parent.left_buttons_frame,
            text=f"Max words: {WORD_COUNT_MAX}", 
            font=(FONT_NAME, LABEL_FONT)
        )
        self.parent.max_words_label.grid(row=FIRST_ROW, column=SIX_COLUMN, padx=PADX)

        self.parent.buttons_frame = tk.Frame(self.parent.controls_frame, width=CONTROLS_FRAME_WIDTH)
        self.parent.buttons_frame.pack(fill=tk.X)

        self.parent.generate_button = tk.Button(
            self.parent.buttons_frame, 
            text=GENERATE_BUTTON_TEXT, 
            command=self.parent.generate_crossword, 
            height=BUTTON_HEIGHT
        )
        self.parent.generate_button.grid(row=FIRST_ROW, column=FIRST_COLUMN, sticky=STICKY_EW)

        self.parent.solve_button = tk.Button(
            self.parent.buttons_frame, 
            text=SOLVE_BUTTON_TEXT, 
            command=self.parent.solve_crossword, 
            height=BUTTON_HEIGHT
        )
        self.parent.solve_button.grid(row=FIRST_ROW, column=SECOND_COLUMN, sticky=STICKY_EW)

        self.parent.clear_button = tk.Button(
            self.parent.buttons_frame, 
            text=CLEAR_BUTTON_TEXT, 
            command=self.parent.clear_crossword, 
            height=BUTTON_HEIGHT
        )
        self.parent.clear_button.grid(row=SECOND_ROW, column=FIRST_COLUMN, sticky=STICKY_EW)

        self.parent.export_button = tk.Button(
            self.parent.buttons_frame, 
            text=EXPORT_BUTTON_TEXT, 
            command=self.parent.export_crossword, 
            height=BUTTON_HEIGHT
        )
        self.parent.export_button.grid(row=SECOND_ROW, column=SECOND_COLUMN, sticky=STICKY_EW)

        self.parent.buttons_frame.grid_columnconfigure(FIRST_ROW, weight=WEIGHT)
        self.parent.buttons_frame.grid_columnconfigure(SECOND_ROW, weight=WEIGHT)

    def display_message(self, message):
        self.parent.result_text.insert(tk.END, message + "\n")
        self.parent.result_text.see(tk.END)

    def display_welcome_message(self, mode):
        self.parent.result_text.delete(1.0, tk.END)
        if mode == CUSTOM_MODE_TEXT:
            message = CUSTOM_WELCOME
        else:
            message = AUTO_WELCOME
        self.display_message(message)