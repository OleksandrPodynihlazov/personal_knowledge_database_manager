import sys
from scripts.hybrid_classifier import HybridClassifier
from scripts.file_handler import get_file_text
import logging
from scripts.logging_config import setup_logging
from scripts.enricher import NerEnricher
from scripts.kb_integrator import KBIntegrator
import os
import zipfile
from datetime import date
from scripts.data_models import ClassifiedData
import yaml
from scripts.summarizer import Summarizer
from scripts.action_item_detector import ActionItemDetector
from scripts.zero_shot_service import ZeroShotService

# --- 1. Setup and Initialization ---

# Define base paths for the Obsidian vault, archive, and configuration file.
VAULT_PATH = os.path.abspath("../knowledge_base")
ARCHIVE_PATH = os.path.abspath("../archive")
BASE_PATH = os.path.abspath("..")
CONFIG_PATH = os.path.join(BASE_PATH, "config.yml")

# Configure the logging system.
setup_logging()
logger = logging.getLogger(__name__)

# Load configuration from the YAML file.
# This allows modifying settings without changing the code.
with open(CONFIG_PATH, 'r', encoding='utf-8') as config_file:
    config = yaml.safe_load(config_file)


if __name__ == '__main__':
    # --- 2. Handle Command-Line Arguments ---
    if len(sys.argv) != 2:
        logger.error("Usage: python main.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    # --- 3. Extract Text from File ---
    # Use file_handler to convert the file into clean text.
    text_content = get_file_text(file_path=file_path)

    if text_content is None:
        logging.warning(f"Could not extract text from file: {file_path}")
        sys.exit(1)

    # --- 4. Classify Text ---
    # Create an instance of the hybrid classifier, which encapsulates the logic
    # for choosing between an ML model and keyword-based classification.
    zs_service = ZeroShotService()
    classifier_labels = config.get("ml_service", {}).get("labels", [])
    hybrid_classifier = HybridClassifier(config=config, zs_service=zs_service)
    category = hybrid_classifier.classify(text=text_content, labels=classifier_labels)
    logging.info(f"File '{file_path}' classified as '{category}'")

    # Create a ClassifiedData object with initial data after classification.
    processed_data = ClassifiedData(
        text=text_content,
        source_path=file_path,
        category=category
    )

    # --- 5. Enrich Data ---
    # Extract Named Entities (NER) from the text.
    enricher = NerEnricher()
    enriched_data = enricher.enrich(data=processed_data)

    # --- 6. Integrate into Knowledge Base and Archive ---
    if enriched_data:
        logging.info(f"File '{file_path}' classified as '{enriched_data.category}'\
                     with entities: {enriched_data.entities}")
        # Summarize the text content.
        summarizer = Summarizer()
        summary = summarizer.summarize(text=enriched_data.text)
        enriched_data.summary = summary
        # Detect action items in the text content.
        action_items_labels = config.get("ml_service", {}).get("action_items_labels", [])
        action_item_detector = ActionItemDetector(zs_service=zs_service)
        action_items = action_item_detector.detect(text=enriched_data.text, labels=action_items_labels)
        enriched_data.action_items = action_items
        # Create a new note in Obsidian.
        templates_config = config.get('templates', {})
        kb_integrator = KBIntegrator(VAULT_PATH, templates_config)
        final_path = kb_integrator.create_note(data=enriched_data)

        # Archive and delete the original file.
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
