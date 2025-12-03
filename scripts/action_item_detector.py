from scripts.logging_config import setup_logging
import logging
from transformers import pipeline
from typing import List

setup_logging()
logger = logging.getLogger(__name__)


class ActionItemDetector:
    def __init__(self) -> None:
        """
        Initializes the ActionItemDetector instance.

        The instance will load the zero-shot classification model during initialization,
        which is used to detect action items from text content.

        :raises Exception: If there is an error during the model loading process.
        """
        self.labels = ["action item", "task", "reminder", "to-do", "task list", "follow up", "deadline"]
        self.confidence_threshold = 0.75
        try:
            self.classifier = pipeline(task="zero-shot-classification", model="facebook/bart-large-mnli")
            logging.info("Zero-shot classification model loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load zero-shot classification mode: {e}")
            raise

    def detect(self, text: str) -> List[str]:
        """
        Detects action items from the given text content.

        The function splits the text content into sentences and then uses the
        zero-shot classification model to detect action items from each sentence.

        :param text: The text content to detect action items from.
        :return: A list of detected action items, or an empty list if detection fails.
        :raises Exception: If there is an error during the detection process.
        """

        sentences = text.split('\n')
        action_items = []
        try:
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                results = self.classifier(sentence, self.labels)
                if results and isinstance(results, dict):
                    label = results.get('labels', [""])[0]
                    score = results.get('scores', [0.0])[0]
                    if label in self.labels and score >= self.confidence_threshold:
                        action_items.append(sentence)
            return action_items
        except Exception as e:
            logger.error(f"Failed to detect action items: {e}")
            return []
