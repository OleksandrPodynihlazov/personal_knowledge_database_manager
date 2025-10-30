import spacy
from scripts.classifier import ClassifiedData
from scripts.logging_config import setup_logging
import logging

setup_logging()


class NerEnricher:
    def __init__(self) -> None:
        """
        Initializes the NerEnricher instance.

        The instance will load the en_core_web_sm spaCy model during initialization,
        which is used to extract named entities from the given text content.

        :return: None
        """
        self.nlp = spacy.load("en_core_web_sm")

    def enrich(self, data: ClassifiedData) -> ClassifiedData | None:
        """
        Enriches the given data with named entities using the spaCy library.

        :param data: The data that should be enriched with named entities.
        :return: The enriched data, or None if an error occurred during the enrichment process.
        """
        try:
            s_obj = self.nlp(data.text)
            entities = []
            for ent in s_obj.ents:
                entities.append(f"{ent.text} ({ent.label_})")
            data.entities = entities
            return data
        except Exception as e:
            logging.error(f"Error during NER enrichment for file {data.source_path}: {e}")
            return None
