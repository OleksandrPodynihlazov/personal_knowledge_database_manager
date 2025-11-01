from dataclasses import dataclass, field
from typing import List


@dataclass
class ClassifiedData:
    text: str
    source_path: str
    category: str = "uncategorized"
    tags: List[str] = field(default_factory=list)


class KeywordClassifier:
    def __init__(self, config):
        self.config = config

    def classify(self, text: str) -> str:
        """
        Classify the given text into one of the predefined categories.

        :param text: The text content that should be classified.
        :return: The category that the text belongs to, or "uncategorized" if no category is found.
        """
        text_lower = text.lower()
        for category, keywords in self.config.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                return category
        return "uncategorized"
