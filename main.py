import sys
from scripts.hybrid_classifier import HybridClassifier
from scripts.file_handler import get_file_text
import logging
from scripts.logging_config import setup_logging
from scripts.kb_integrator import KBIntegrator
import os
import zipfile
from datetime import date
from scripts.data_models import ClassifiedData
import yaml
from scripts.zero_shot_service import ZeroShotService
from pathlib import Path
from scripts.enrichment_pipeline import EnrichmentPipeline

# --- 1. Setup and Initialization ---

# Define base paths for the Obsidian vault, archive, and configuration file.
PROJECT_ROOT = Path(__file__).parent.resolve()
VAULT_PATH = PROJECT_ROOT / "knowledge_base"
ARCHIVE_PATH = PROJECT_ROOT / "archive"
CONFIG_PATH = PROJECT_ROOT / "config.yml"

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
        logger.error(f"Usage: python {sys.argv[0]} <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    # --- 3. Extract Text from File ---
    # Use file_handler to convert the file into clean text.
    text_content = get_file_text(file_path=file_path)

    if text_content is None:
        logging.warning(f"Could not extract text from file: {file_path}")
        sys.exit(1)

    # --- 4. Classify Text ---
    # Create a single instance of the ZeroShotService to be shared
    zs_service = ZeroShotService()
    enrichment_pipeline = EnrichmentPipeline(zs_service=zs_service, config=config)
    # Create an instance of the hybrid classifier
    hybrid_classifier = HybridClassifier(config=config, zs_service=zs_service)
    classifier_labels = config.get("ml_service", {}).get("labels", [])
    category = hybrid_classifier.classify(text=text_content, labels=classifier_labels)
    logging.info(f"File '{file_path}' classified as '{category}'")

    # Create a ClassifiedData object with initial data after classification.
    processed_data = ClassifiedData(
        text=text_content,
        source_path=file_path,
        category=category
    )

    enriched_data = enrichment_pipeline.run(data=processed_data)
    if enriched_data is None:
        logging.error(f"Enrichment pipeline failed for file: {file_path}")
        sys.exit(1)
    # Create a new note in Obsidian.
    templates_config = config.get('templates', {})
    kb_integrator = KBIntegrator(VAULT_PATH, templates_config, project_root=PROJECT_ROOT)
    final_path = kb_integrator.create_note(data=enriched_data)
    # Archive and delete the original file ONLY if note creation was successful.
    if final_path:
        try:
            archive_name = f"{date.today().isoformat()}-{os.path.basename(file_path)}.zip"
            archive_path = os.path.join(ARCHIVE_PATH, archive_name)
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
                archive.write(file_path, arcname=os.path.basename(file_path))
            logging.info(f"Original file archived at: {archive_path}")
            os.remove(file_path)
            logging.info(f"Original file '{file_path}' removed after archiving")
        except Exception as E:
            logger.error(f"Error archiving file {file_path}: {E}")
    else:
        # If note creation failed, the file is already quarantined by the logger.
        logging.warning(f"Skipping archive for {file_path} because note creation failed.")
