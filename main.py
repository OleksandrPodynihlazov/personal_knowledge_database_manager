import sys
from scripts.classifier import KeywordClassifier
from scripts.file_handler import get_file_text
import logging
from scripts.logging_config import setup_logging

setup_logging()

"""Classify a given file into one of the predefined categories.

Usage:
    python main.py <file_path>

Example:
    python main.py ../path/to/file.txt

The following categories are supported:
    - лекція
    - лабораторна
    - стаття

The script will log the classification result to the console.

The script will exit with code 1 if the text content of the given file could not be extracted."""

if __name__ == '__main__':
    if len(sys.argv) != 2:
        logging.error("Usage: python main.py <file_path>")
        sys.exit(1)
    file_path = sys.argv[1]
    text_content = get_file_text(file_path=file_path)
    if text_content is None:
        logging.warning(f"Could not extract text from file: {file_path}")
        sys.exit(1)
    classifier_config = {
        "лекція": ["лекція", "професор", "університет", "курс"],
        "лабораторна": ["лабораторна", "завдання", "код", "виконати"],
        "стаття": ["стаття", "дослідження", "журнал", "опубліковано"]
    }
    classifier = KeywordClassifier(config=classifier_config)
    category = classifier.classify(text=text_content)
    logging.info(f"File '{file_path}' classified as: '{category}'")
