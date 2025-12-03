from scripts.logging_config import setup_logging
import logging
from transformers import pipeline

setup_logging()
logger = logging.getLogger(__name__)


class Summarizer:
    def __init__(self) -> None:
        """
        Initializes the Summarizer, loading the summarization model.
        """
        try:
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            logger.info("Summarization model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load summarization model: {e}")
            raise  # Re-raise the exception to halt execution if model loading fails

    def summarize(self, text: str) -> str:
        """
        Generates a summary for the given text.

        :param text: The text to summarize.
        :return: The summary string, or an empty string if summarization fails.
        """
        try:
            # Added length constraints for more predictable summaries
            summary_result = self.summarizer(text, max_length=150, min_length=40, do_sample=False)
            summary_text = summary_result[0]['summary_text']
            return summary_text
        except Exception as e:
            logger.error(f"Failed to summarize text: {e}")
            return ""
