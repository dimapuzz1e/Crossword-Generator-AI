from constants import *

class CrosswordExport:
    def __init__(self, grid, result_text, theme_entry):
        self.grid = grid
        self.result_text = result_text
        self.theme_entry = theme_entry
        self.word_positions = []
        self.clue_indices = {}

    def set_word_positions(self, word_positions, clue_indices):
        self.word_positions = word_positions
        self.clue_indices = clue_indices

    def export_crossword(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".docx",
                filetypes=[("Word Document", "*.docx"), ("PDF File", "*.pdf")],
                title="Save Crossword As"
            )
            if not file_path:
                return
            theme = self.theme_entry.get()
            if not theme:
                theme = "Untitled Crossword"
            clues_text = self.result_text.get(1.0, tk.END).strip()
            if not clues_text:
                raise ValueError("\nThere are no clues to export.")
            questions = self._extract_questions(clues_text)
            if not questions:
                raise ValueError("\nNo valid questions found to export.")
            indices_to_answers = {int(index): word for word, index in self.clue_indices.items()}
            if file_path.endswith(".pdf"):
                self._export_to_pdf(file_path, theme, questions, indices_to_answers)
            elif file_path.endswith(".docx"):
                self._export_to_word(file_path, theme, questions, indices_to_answers)
            else:
                raise ValueError("\nUnsupported file format.")
            self.result_text.insert(tk.END, f"\nCrossword exported successfully to {file_path}")
        except Exception as e:
            self.result_text.insert(tk.END, f"\nError exporting crossword: {str(e)}\n")
            print(f"Error exporting crossword: {str(e)}")

    def _extract_questions(self, clues_text):
        pattern = r"^(\d+)\.\s(.+)\((horizontal|vertical),\s(\d+)\sletters\)$"
        questions = []
        for line in clues_text.strip().split("\n"):
            match = re.match(pattern, line.strip())
            if match:
                index = int(match.group(1))
                question_text = match.group(2).strip()
                direction = match.group(3)
                num_letters = int(match.group(4))
                questions.append((index, question_text, direction, num_letters))
        return questions

    def _export_to_pdf(self, file_path, theme, questions, indices_to_answers):
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, height - 20, theme)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, height - 40, "Questions:")
        c.setFont("Helvetica", 8)
        y_position = height - 60
        for index, question, direction, num_letters in questions:
            question_line = f"{index}. {question} ({direction}, {num_letters} letters)"
            c.drawString(100, y_position, question_line)
            y_position -= 10
            if y_position < 50:
                c.showPage()
                y_position = height - 50
        c.setFont("Helvetica-Bold", 12)
        y_position -= 20
        c.drawString(100, y_position, "Crossword Grid (Without Answers):")
        y_position -= 30
        self._draw_grid_to_pdf(c, y_position, with_answers=False)
        c.showPage()
        y_position = height - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, y_position, theme)
        y_position -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y_position, "Questions and Answers:")
        y_position -= 20
        c.setFont("Helvetica", 8)
        for index, question, direction, num_letters in questions:
            answer = indices_to_answers.get(index, '')
            qa_line = f"{index}. {question} ({direction}, {num_letters} letters) - {answer}"
            c.drawString(100, y_position, qa_line)
            y_position -= 10
            if y_position < 50:
                c.showPage()
                y_position = height - 50
        y_position -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y_position, "Crossword Grid (With Answers):")
        y_position -= 30
        self._draw_grid_to_pdf(c, y_position, with_answers=True)
        c.save()

    def _draw_grid_to_pdf(self, c, y_position, with_answers=False):
        max_row = max(r for r, c in self.grid.cells.keys()) + 1
        max_col = max(c for r, c in self.grid.cells.keys()) + 1
        cell_size = 20
        scale_factor = 1
        if max_row > 20 or max_col > 20:
            scale_factor = min(20 / max_row, 20 / max_col)
            cell_size *= scale_factor
        starting_positions = {}
        for word, (start_row, start_col), direction in self.word_positions:
            index = self.clue_indices.get(word, '')
            starting_positions[(start_row, start_col)] = index
        word_cells = set()
        for word, (start_row, start_col), direction in self.word_positions:
            for i in range(len(word)):
                row = start_row + (i if direction == DIRECTION_VERTICAL else 0)
                col = start_col + (i if direction == DIRECTION_HORIZONTAL else 0)
                word_cells.add((row, col))
        for row in range(max_row):
            for col in range(max_col):
                x = 100 + col * cell_size
                y = y_position - row * cell_size
                c.rect(x, y, cell_size, cell_size, stroke=1, fill=0)
                if (row, col) in word_cells:
                    char = self.grid.cells[(row, col)][WIDGET].cget("text") if with_answers else ""
                    if (row, col) in starting_positions and not with_answers:
                        index = starting_positions[(row, col)]
                        c.setFont("Helvetica", 6)
                        c.drawString(x + 2, y + cell_size - 7, str(index))
                        c.setFont("Helvetica", 10)
                    if char:
                        c.drawString(x + cell_size/3, y + cell_size/4, char)
                else:
                    c.setFillColor(colors.grey)
                    c.rect(x, y, cell_size, cell_size, fill=1)
                    c.setFillColor(colors.black)

    def _export_to_word(self, file_path, theme, questions, indices_to_answers):
        document = Document()
        document.add_heading(theme, level=1)
        document.add_heading("Questions", level=2)
        for index, question, direction, num_letters in questions:
            document.add_paragraph(f"{index}. {question} ({direction}, {num_letters} letters)")
        document.add_page_break()
        document.add_heading("Crossword Grid (Without Answers)", level=2)
        self._get_grid_as_table(document, with_answers=False)
        document.add_page_break()
        document.add_heading(theme, level=1)
        document.add_heading("Questions and Answers", level=2)
        for index, question, direction, num_letters in questions:
            answer = indices_to_answers.get(index, '')
            document.add_paragraph(f"{index}. {question} ({direction}, {num_letters} letters) - {answer}")
        document.add_page_break()
        document.add_heading("Crossword Grid (With Answers)", level=2)
        self._get_grid_as_table(document, with_answers=True)
        document.save(file_path)

    def _get_grid_as_table(self, document, with_answers=False):
        max_row = max(r for r, c in self.grid.cells.keys()) + 1
        max_col = max(c for r, c in self.grid.cells.keys()) + 1
        table = document.add_table(rows=max_row, cols=max_col)
        table.style = 'Table Grid'
        section = document.sections[-1]
        page_width = section.page_width.inches
        page_height = section.page_height.inches
        left_margin = section.left_margin.inches
        right_margin = section.right_margin.inches
        top_margin = section.top_margin.inches
        bottom_margin = section.bottom_margin.inches
        available_width = page_width - left_margin - right_margin
        available_height = page_height - top_margin - bottom_margin
        max_cell_width = available_width / max_col
        max_cell_height = available_height / max_row
        cell_size_inches = min(max_cell_width, max_cell_height)
        min_cell_size_inches = 0.2
        cell_size_inches = max(cell_size_inches, min_cell_size_inches)
        cell_size = Inches(cell_size_inches)
        for col in table.columns:
            for cell in col.cells:
                cell.width = cell_size
        for row in table.rows:
            row.height = cell_size
            row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
        for row in table.rows:
            tr = row._tr
            trPr = tr.get_or_add_trPr()
            cant_split = parse_xml('<w:cantSplit xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>')
            trPr.append(cant_split)
        starting_positions = {}
        for word, (start_row, start_col), direction in self.word_positions:
            index = self.clue_indices.get(word, '')
            starting_positions[(start_row, start_col)] = index
        word_cells = set()
        for word, (start_row, start_col), direction in self.word_positions:
            for i in range(len(word)):
                row_idx = start_row + (i if direction == 'vertical' else 0)
                col_idx = start_col + (i if direction == 'horizontal' else 0)
                word_cells.add((row_idx, col_idx))

        for row in range(max_row):
            for col in range(max_col):
                cell = table.cell(row, col)
                paragraph = cell.paragraphs[0]
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                if (row, col) in word_cells:
                    char = self.grid.cells[(row, col)][WIDGET].cget("text") if with_answers else ""
                    if (row, col) in starting_positions and not with_answers:
                        index = str(starting_positions[(row, col)])
                        run = paragraph.add_run(index + ' ')
                        run.font.size = Pt(6)
                    if char:
                        run = paragraph.add_run(char)
                        run.font.size = Pt(12)
                else:
                    shading_elm = parse_xml(r'<w:shd {} w:fill="D9D9D9"/>'.format(nsdecls('w')))
                    cell._tc.get_or_add_tcPr().append(shading_elm)
        return table