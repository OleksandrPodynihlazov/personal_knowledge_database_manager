from transformers import pipeline
import logging
from scripts.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class ZeroShotClassifier:
    def __init__(self, labels: list, model: str) -> None:
        """
        Initializes the ZeroShotClassifier instance.

        The instance will load the zero-shot classification model during initialization,
        which is used to classify text into predefined categories.

        :raises Exception: If there is an error during the model loading process.
        """
        self.labels = labels
        try:
            self.classifier = pipeline(task="zero-shot-classification", model=model)
            logging.info("Zero-shot classification model loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load zero-shot classification mode: {e}")
            raise

    def classify(self, text: str) -> tuple[str, float]:
        """
        Classifies the given text into one of the predefined categories.

        :param text: The text content that should be classified.
        :return: The category that the text belongs to, or "uncategorized" if no category is found.
        :raises Exception: If there is an error during the classification process.
        """
        try:
            results = self.classifier(text, self.labels)
            if not results or not isinstance(results, dict):
                return ("uncategorized", 0.0)
            label = results.get('labels', ["uncategorized"])[0]
            score = results.get('scores', [0.0])[0]
            return (label, score)
        except Exception as e:
            logging.error(f"Failed to classify text: {e}")
            return ("uncategorized", 0.0)
