import sys
from scripts.word_classifier import KeywordClassifier
from scripts.ml_classifier import ZeroShotClassifier
from scripts.file_handler import get_file_text
import logging
from scripts.logging_config import setup_logging
from scripts.enricher import NerEnricher
from scripts.kb_integrator import KBIntegrator
import os
import zipfile
from datetime import date
from scripts.data_models import ClassifiedData

VAULT_PATH = os.path.abspath("../knowledge_base")
ARCHIVE_PATH = os.path.abspath("../archive")

setup_logging()
logger = logging.getLogger(__name__)

"""Classify a given file into one of the predefined categories.

Usage:
    python main.py <file_path>

Example:
    python main.py ../path/to/file.txt

The following categories are supported:
    - "Meeting Notes"
    - "Technical Article"
    - "Code Snippet"


The script will log the classification result to the console.

The script will exit with code 1 if the text content of the given file could not be extracted."""

if __name__ == '__main__':
    if len(sys.argv) != 2:
        logger.error("Usage: python main.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    text_content = get_file_text(file_path=file_path)

    if text_content is None:
        logging.warning(f"Could not extract text from file: {file_path}")
        sys.exit(1)

    classifier_config = {
        "Meeting Notes": ["meeting", "agenda", "minutes", "attendees", "action items"],
        "Technical Article": ["study", "research", "published", "journal", "paper", "introduction", "conclusion"],
        "Code Snippet": ["python", "javascript", "function", "class", "import", "def", "const"]
    }
    ml_labels = ["Meeting Notes", "Technical Article", "Code Snippet", "uncategorized"]
    category = "uncategorized"
    try:
        ml_classifier = ZeroShotClassifier(labels=ml_labels)
        category = ml_classifier.classify(text=text_content)
    except Exception as e:
        logger.error(f"ML classification failed: {e}", file_path)
        logging.info("Falling back to keyword-based classification.")
        classifier = KeywordClassifier(config=classifier_config)
        category = classifier.classify(text=text_content)
    finally:
        logging.info(f"File '{file_path}' classified as '{category}'")

    processed_data = ClassifiedData(
        text=text_content,
        source_path=file_path,
        category=category
    )

    enricher = NerEnricher()
    enriched_data = enricher.enrich(data=processed_data)
    if enriched_data:
        logging.info(f"File '{file_path}'\
                    classified as '{enriched_data.category}'\
                    with entities: {enriched_data.entities}")
        kb_integrator = KBIntegrator(VAULT_PATH)
        final_path = kb_integrator.create_note(data=enriched_data)

        try:
            archive_name = f"{date.today().isoformat()}-{os.path.basename(file_path)}.zip"
            archive_path = os.path.join(ARCHIVE_PATH, archive_name)

            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
                archive.write(file_path, arcname=os.path.basename(file_path))
            logging.info(f"Original file archived at: {archive_path}")

            os.remove(file_path)
            logging.info(f"Original file '{file_path}' removed after archiving")

        except Exception as E:
            logger.error(f"Error archiving file {file_path}: {E}", file_path)

    else:
        logger.error(f"Failed to enrich data for file: {file_path}", file_path)
