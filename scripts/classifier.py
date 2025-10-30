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
        text_lower = text.lower()
        for category, keywords in self.config.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                return category
        return "uncategorized"


if __name__ == '__main__':
    classifier_config = {
        "лекція": ["лекція", "професор", "університет", "курс"],
        "лабораторна": ["лабораторна", "завдання", "код", "виконати"],
        "стаття": ["стаття", "дослідження", "журнал", "опубліковано"]
    }

    classifier = KeywordClassifier(config=classifier_config)

    sample_text = "Це текст лабораторної роботи. Потрібно виконати завдання з програмування."

    category = classifier.classify(sample_text)
    print(f"Текст класифіковано як: '{category}'")

    sample_text_2 = "Нова стаття про дослідження клімату."
    category_2 = classifier.classify(sample_text_2)
    print(f"Текст класифіковано як: '{category_2}'")
