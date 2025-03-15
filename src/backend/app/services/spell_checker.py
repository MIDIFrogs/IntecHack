from symspellpy import SymSpell, Verbosity
import pkg_resources
import os
from typing import Optional, Literal

class SpellChecker:
    def __init__(self):
        # Initialize SymSpell instances for both languages
        self.sym_spell_en = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        self.sym_spell_ru = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        
        # Load English dictionaries
        en_dict_path = pkg_resources.resource_filename(
            "symspellpy", "frequency_dictionary_en_82_765.txt"
        )
        en_bigram_path = pkg_resources.resource_filename(
            "symspellpy", "frequency_bigramdictionary_en_243_342.txt"
        )
        
        # Load English dictionaries
        self.sym_spell_en.load_dictionary(en_dict_path, term_index=0, count_index=1)
        self.sym_spell_en.load_bigram_dictionary(en_bigram_path, term_index=0, count_index=2)
        
        # Load Russian dictionary
        # You can download Russian frequency dictionary from:
        # https://github.com/hermitdave/FrequencyWords/blob/master/content/2018/ru/ru_full.txt
        ru_dict_path = os.path.join(os.path.dirname(__file__), 'dictionaries', 'ru_full.txt')
        
        if os.path.exists(ru_dict_path):
            self.sym_spell_ru.load_dictionary(ru_dict_path, term_index=0, count_index=1)
        else:
            print("Warning: Russian dictionary not found. Please download it to enable Russian spell checking.")
    
    def is_russian(self, text: str) -> bool:
        """
        Check if the text contains Russian characters.
        """
        return any(ord('а') <= ord(c) <= ord('я') or ord('А') <= ord(c) <= ord('Я') for c in text)
    
    def correct_text(self, text: str, language: Optional[Literal['en', 'ru']] = None) -> str:
        """
        Correct spelling in the given text using both word and contextual correction.
        
        Args:
            text (str): The input text to be corrected
            language (str, optional): Force specific language ('en' or 'ru'). 
                                    If None, language will be auto-detected.
            
        Returns:
            str: The corrected text
        """
        try:
            # Auto-detect language if not specified
            if language is None:
                language = 'ru' if self.is_russian(text) else 'en'
            
            # Select appropriate SymSpell instance
            sym_spell = self.sym_spell_ru if language == 'ru' else self.sym_spell_en
            
            # First try using compound correction
            suggestions = sym_spell.lookup_compound(
                text,
                max_edit_distance=2,
                transfer_casing=True
            )
            
            if suggestions:
                return suggestions[0].term
            
            # If compound correction fails, fall back to word-by-word correction
            words = text.split()
            corrected_words = []
            
            for word in words:
                suggestions = sym_spell.lookup(
                    word,
                    Verbosity.CLOSEST,
                    max_edit_distance=2,
                    transfer_casing=True
                )
                
                if suggestions:
                    corrected_words.append(suggestions[0].term)
                else:
                    corrected_words.append(word)
            
            return " ".join(corrected_words)
            
        except Exception as e:
            print(f"Error in spell correction: {str(e)}")
            return text  # Return original text if correction fails

# Create a singleton instance
spell_checker = SpellChecker() 