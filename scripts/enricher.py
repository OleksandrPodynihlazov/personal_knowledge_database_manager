import spacy
from scripts.logging_config import setup_logging
import logging
from scripts.data_models import EnrichedData, ClassifiedData
from collections import defaultdict

setup_logging()
logger = logging.getLogger(__name__)


class NerEnricher:
    def __init__(self) -> None:
        """
        Initializes the NerEnricher instance.

        The instance will load the en_core_web_sm spaCy model during initialization,
        which is used to extract named entities from the given text content.

        :return: None
        """
        self.nlp = spacy.load("en_core_web_sm")

    def enrich(self, data: ClassifiedData) -> EnrichedData | None:
        """
        Enriches the given data with named entities using the spaCy library.

        :param data: The data that should be enriched with named entities.
        :return: The enriched data, or None if an error occurred during the enrichment process.
        """
        enriched_data = EnrichedData(text=data.text,
                                     source_path=data.source_path,
                                     category=data.category,
                                     tags=data.tags)
        try:
            s_obj = self.nlp(data.text)
            entities = defaultdict(list)
            for ent in s_obj.ents:
                entities[ent.label_].append(ent.text)
            entities = dict(entities)
            enriched_data.entities = entities
            return enriched_data
        except Exception as e:
            logger.error(f"Error during NER enrichment for file {data.source_path}: {e}", data.source_path)
            return None
