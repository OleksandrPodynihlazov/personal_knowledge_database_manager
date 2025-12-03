from scripts.zero_shot_service import ZeroShotService
from scripts.word_classifier import KeywordClassifier
import logging


class HybridClassifier:
    def __init__(self, config: dict, zs_service: ZeroShotService) -> None:
        """
        Initializes the HybridClassifier instance.

        The instance will load the zero-shot classification model during initialization,
        which is used to classify text into predefined categories.

        If the zero-shot classification model fails to initialize, the function will
        fall back to the keyword-based classification model.

        :param config: The configuration dictionary containing settings for the
            zero-shot classification model and the keyword-based classification model.
        :param zs_service: The ZeroShotService instance that provides the
            zero-shot classification model.
        :return: None
        :raises Exception: If there is an error during the initialization process.
        """
        try:
            self.ml_classifier = zs_service
            self.confidence_threshold = 0.6
        except Exception as e:
            logging.error(f"Failed to initialize ML classifier: {e}")
            self.ml_classifier = None

        word_config = config.get("word_classifier", {})
        self.word_classifier = KeywordClassifier(config=word_config.get("config", {}))

    def classify(self, text: str, labels: list) -> str:
        """
        Classify the given text into one of the predefined categories.

        The function first tries to classify the text using the zero-shot classification model.
        If the zero-shot classification model fails (e.g., due to an error during the classification process),
        the function falls back to the keyword-based classification model.

        :param text: The text content that should be classified.
        :return: The category that the text belongs to, or "uncategorized" if no category is found.
        :raises Exception: If there is an error during the classification process.
        """
        try:
            if self.ml_classifier:
                label, score = self.ml_classifier.predict(text=text, labels=labels)
                if score >= self.confidence_threshold:
                    return label
        except Exception as e:
            logging.info(f"ML classification failed: {e}")
        return self.word_classifier.classify(text=text)
