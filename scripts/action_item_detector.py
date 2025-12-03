from scripts.logging_config import setup_logging
import logging
from typing import List
from scripts.zero_shot_service import ZeroShotService

setup_logging()
logger = logging.getLogger(__name__)


class ActionItemDetector:
    def __init__(self, zs_service: ZeroShotService) -> None:
        self.confidence_threshold = 0.5
        try:
            self.service = zs_service
            logging.info("Zero-shot classification model loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load zero-shot classification mode: {e}")
            raise

    def detect(self, text: str, labels: list) -> List[str]:
        """
        Detects action items in the given text content.

        The function takes in the text content and the list of labels to classify into.
        It returns a list of action items detected in the text content.

        The function splits the text content into individual sentences, and then
        uses the zero-shot classification model to classify each sentence into one
        of the predefined labels. If the confidence score is above the
        threshold (0.75), the sentence is considered an action item.

        :param text: The text content to detect action items from.
        :param labels: The list of labels to classify into.
        :return: A list of action items detected in the text content.
        :raises Exception: If there is an error during the detection process.
        """
        sentences = text.split('\n')
        action_items = []
        try:
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                results = self.service.predict(sentence, labels)
                if results and isinstance(results, dict):
                    label = results.get('labels', [""])[0]
                    score = results.get('scores', [0.0])[0]
                    if label in labels and score >= self.confidence_threshold:
                        action_items.append(sentence)
            return action_items
        except Exception as e:
            logger.error(f"Failed to detect action items: {e}")
            return []
