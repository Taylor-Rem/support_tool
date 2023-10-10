import re
import spacy
import en_core_web_sm
from nltk.tokenize import word_tokenize
from nltk import pos_tag

# Load the English NLP model
nlp = en_core_web_sm.load()


class BaseInterpreter:
    def __init__(self):
        pass

    def _tokenize_and_tag(self, text):
        words = word_tokenize(text)
        tagged = pos_tag(words)
        return words, tagged

    def _keyword_proximity(self, text, keywords, numbers):
        # Separate numbers from adjacent words using a regex replacement
        modified_text = re.sub(r"(\d+)([^\d\s])", r"\1 \2", text)
        words, _ = self._tokenize_and_tag(modified_text)
        if not numbers:
            return None

        keyword_proximity = []
        for number in numbers:
            min_distance = float("inf")  # Start with a very large default value

            # Get all indices of the current number in words list
            number_indices = [i for i, word in enumerate(words) if word == number]

            for keyword in keywords:
                # Get all indices of the current keyword in words list
                keyword_indices = [i for i, word in enumerate(words) if word == keyword]
                for ni in number_indices:
                    for ki in keyword_indices:
                        min_distance = min(min_distance, abs(ni - ki))

            keyword_proximity.append(min_distance)

        return numbers[keyword_proximity.index(min(keyword_proximity))]


class TaxInterpreter(BaseInterpreter):
    def determine_operation(self, text):
        keywords = ["monthly taxes", "recurring taxes", "taxes"]
        for keyword in keywords:
            if keyword in text and ("monthly" in keyword or "recurring" in keyword):
                return "add_monthly_taxes"
        return None


class NumberInterpreter(BaseInterpreter):
    def find_nouns_in_text(self, text, limit=4):
        modified_text = re.sub(r"(\d+)([^\d\s])", r"\1 \2", text)
        words, tagged = self._tokenize_and_tag(modified_text)

        # Find nouns that are digits and have a length up to the limit
        nouns = [
            word
            for word, pos in tagged
            if word.isdigit() and len(word) <= limit and pos in ["NN", "NNS"]
        ]

        # If we found no suitable nouns, then find any number (regardless of POS tag)
        if not nouns:
            nouns = [
                word for word, pos in tagged if word.isdigit() and len(word) <= limit
            ]

        return nouns

    def extract_unit_number(self, text):
        numbers = self.find_nouns_in_text(text)
        unit_number = self._keyword_proximity(text, ["unit", "space", "lot"], numbers)
        return None if unit_number and len(unit_number) > 4 else unit_number

    def extract_dollar_amount(self, text):
        match = re.search(r"\$\s?(\d+(?:,\d{3})*(?:\.\d{2})?)", text)
        return match.group(1) if match else None


class TextInterpreter(BaseInterpreter):
    def extract_resident_name(self, text):
        doc = nlp(text)
        names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        full_names = [name.split() for name in names if len(name.split()) >= 2]
        if full_names:
            return f"{full_names[0][0]} {full_names[0][-1]}"
        return None

    def extract_month(self, text):
        month_pattern = r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\b"
        match = re.search(month_pattern, text, re.IGNORECASE)
        return match.group() if match else None


class Interpretation(NumberInterpreter, TaxInterpreter, TextInterpreter):
    pass
