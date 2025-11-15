# src/postprocess/punctuator.py

from deepmultilingualpunctuation import PunctuationModel

class Punctuator:
    """
    Offline punctuation restoration using deepmultilingualpunctuation.
    Runs on CPU, no HuggingFace download, works everywhere.
    """

    def __init__(self):
        self.model = PunctuationModel()

    def restore(self, text: str) -> str:
        text = text.strip()
        if not text:
            return text

        result = self.model.restore_punctuation(text)
        return result
