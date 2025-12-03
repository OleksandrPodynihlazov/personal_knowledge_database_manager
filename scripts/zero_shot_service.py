from transformers import pipeline
import logging
from scripts.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class ZeroShotService:
    def __init__(self) -> None:
        """
        Initializes the ZeroShotService instance.

        The instance will load the zero-shot classification model during initialization,
        which is used to classify text into predefined categories.

        :param model: The name of the zero-shot classification model to use.
        :raises Exception: If there is an error during the model loading process.
        """
        try:
            self.classifier = pipeline(task="zero-shot-classification", model="facebook/bart-large-mnli")
            logging.info("Zero-shot classification model loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load zero-shot classification mode: {e}")
            raise

    def predict(self, text: str, labels: list) -> tuple[str, float]:

        """
        Predicts the category of the given text using the zero-shot classification model.

        The function takes in the text content and the list of labels to classify into.
        It returns a tuple containing the predicted category and the confidence score.

        If the prediction fails (e.g., due to an error during the classification process),
        the function returns a tuple with the category as "uncategorized" and the confidence score as 0.0.

        :param text: The text content to classify.
        :param labels: The list of labels to classify into.
        :return: A tuple containing the predicted category and the confidence score.
        :raises Exception: If there is an error during the classification process.
        """
        try:
            results = self.classifier(text, labels)
            if not results or not isinstance(results, dict):
                return ("uncategorized", 0.0)
            label = results.get('labels', ["uncategorized"])[0]
            score = results.get('scores', [0.0])[0]
            return (label, score)
        except Exception as e:
            logging.error(f"Failed to classify text: {e}")
            return ("uncategorized", 0.0)
