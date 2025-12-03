from scripts.data_models import EnrichedData, ClassifiedData
from scripts.enricher import NerEnricher
from scripts.summarizer import Summarizer
from scripts.action_item_detector import ActionItemDetector
from scripts.zero_shot_service import ZeroShotService
from scripts.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)


class EnrichmentPipeline:
    def __init__(self, zs_service: ZeroShotService, config: dict) -> None:
        """
        Initializes the EnrichmentPipeline instance.

        The instance will load the zero-shot classification model during initialization,
        which is used to classify text into predefined categories.

        :param zs_service: The ZeroShotService instance that provides the
            zero-shot classification model.
        :param config: The configuration dictionary containing settings for the
            zero-shot classification model and the keyword-based classification model.
        :return: None
        :raises Exception: If there is an error during the model loading process.
        """
        self.action_items_labels = config.get("ml_service", {}).get("action_items_labels", [])

        self.enricher = NerEnricher()
        self.summarizer = Summarizer()
        self.action_item_detector = ActionItemDetector(zs_service=zs_service)

    def run(self, data: ClassifiedData) -> EnrichedData | None:
        """
        Runs the enrichment pipeline for the given ClassifiedData object.

        The pipeline enriches the given data with named entities, a summary of the text content,
        and action items detected in the text content.

        :param data: The ClassifiedData object that should be enriched.
        :return: The EnrichedData object containing the enriched data,
          or None if an error occurred during the enrichment process.
        :raises Exception: If there is an error during the enrichment process.
        """
        try:
            logger.info(f"Running enrichment pipeline for file: {data.source_path}")
            enriched_data = self.enricher.enrich(data=data)

            if enriched_data:
                summary = self.summarizer.summarize(text=enriched_data.text)
                enriched_data.summary = summary
                logger.info(f"File '{data.source_path}' enriched with summary and action items.")

                action_items = self.action_item_detector.detect(text=enriched_data.text,
                                                                labels=self.action_items_labels)
                enriched_data.action_items = action_items
                logger.info(f"Action items detected for file '{data.source_path}': {action_items}")
            return enriched_data
        except Exception as e:
            logger.error(f"Error during enrichment pipeline for file {data.source_path}: {e}")
            return None
