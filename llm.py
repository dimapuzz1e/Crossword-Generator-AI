from constants import *

class LLM:
    
    def __init__(self, model):
        self.model = model

    def create_auto_crossword_prompt(self, theme: str, word_count: int = 1) -> str:
        prompt_text = textwrap.dedent(f"""
        Create a crossword on the theme "{theme}" that includes exactly {word_count + 3} unique words in English.
        Requirements for the words:
        - Each word must be up to 10 characters long, without spaces or hyphens.
        - All words must be in uppercase.
        - The words must be able to intersect through common letters to form a classic crossword structure.
        
        Format for the returned result:
        - Return a list of tuples, each consisting of a pair (word, question for the word), without additional text or formatting.
        - Example format:
        [
            ("WORD1", "Clear question related to the theme"),
            ("WORD2", "Clear question related to the theme"),
            ...
        ]
        
        Additional requirements:
        - The questions must be concise, unambiguous, and closely related to the theme "{theme}".
        - The words in the list must be suitable for creating a crossword where they intersect.
        - Do not include any additional text or comments beyond the specified list format.
        
        The output must follow the specified format, be structured, and ready for use without additional processing.
    """).strip()
        return prompt_text
    
    def generate_custom_crossword_prompt(self, theme: str, words: list[str]) -> str:
        word_list = ", ".join(words)
        prompt_text = textwrap.dedent(f"""
            You are tasked with creating clues for a custom crossword puzzle. The theme is "{theme}", and the words are:
            {word_list}.
            
            Requirements:
            - Generate a concise and clear clue for each word, relevant to the theme.
            - The clues should be unambiguous and creative, helping players guess the words.
            - Return the result as a list of tuples in the format:
              [
                  ("WORD1", "Clue for WORD1"),
                  ("WORD2", "Clue for WORD2"),
                  ...
              ]
            - Do not include any additional comments or text outside this format.
        """).strip()
        return prompt_text
        
    def validate_theme(self, theme: str) -> bool:
        prompt_text = textwrap.dedent(f"""
            You are tasked with evaluating if a given topic is meaningful, appropriate, and non-offensive for creating a crossword puzzle. 
            A valid topic should:
            - Represent a clear, specific, and coherent subject or idea (e.g., "Space Exploration", "Famous Artists", "Technology").
            - Be understandable and relevant for generating related words and clues.
            - Avoid being random, nonsensical, or meaningless combinations of letters or words (e.g., "qqq ww", "dijfdjkf fmffm").
            - Not contain offensive, hateful, illegal, or otherwise inappropriate content.

            Examples of invalid topics:
            - Random or meaningless sequences of letters or words: "abcd xyz", "qqq www", "dijfdjkf".
            - Offensive or hateful content: "Racist terms", "Slurs", "Explicit violence".
            - Illegal or prohibited topics: "How to commit crimes", "Drugs trafficking".

            Topic: "{theme}"
            
            Respond with:
            - "Yes" if the topic is meaningful, appropriate, and suitable for generating a crossword puzzle.
            - "No" if the topic is offensive, illegal, nonsensical, or inappropriate for a crossword puzzle.
            
            Be strict in your evaluation and reject any topic that could be deemed offensive or inappropriate.
        """).strip()
        
        try:
            response = self.model.generate_content(prompt_text)
            if response and response.text.strip().lower() == "yes":
                return True
            return False
        except Exception as e:
            print(f"Error validating theme: {e}")
            return False
        
    def validate_word_list(self, words: list[str]) -> list[str]:
        word_list_str = ", ".join(f'"{word}"' for word in words)
        prompt_text = textwrap.dedent(f"""
            You are tasked with validating a list of words for use in a crossword puzzle.
            
            Requirements:
            - Each word must be a real, meaningful English word.
            - Words that are random letter combinations or nonsensical should be marked as invalid.
            - Return ONLY the invalid words from the list provided.

            Here is the list of words:
            {word_list_str}

            Format your response as:
            - A comma-separated list of invalid words, for example: WORD1, WORD2, WORD3
            - If all words are valid, respond with "ALL VALID".
        """).strip()

        try:
            response = self.model.generate_content(prompt_text)
            response_text = response.text.strip()
            
            if response_text.upper() == "ALL VALID":
                return []
            invalid_words = [word.strip().upper() for word in response_text.split(",") if word.strip()]
            return invalid_words
        except Exception as e:
            print(f"Error validating word list: {e}")
            return []

    def prompt_output(self, theme: str, word_count: int):
        try:
            prompt_text = self.create_auto_crossword_prompt(theme, word_count)
            response = self.model.generate_content(prompt_text)

            if response and response.text:
                return response.text
            else:
                return "Content creation failed. Try a different topic or word count."
        except Exception as e:
            return f"An error occurred during generation: {e}"