from datetime import date
from scripts.data_models import EnrichedData
import re
from pathlib import Path
from scripts.logging_config import setup_logging
import logging
from collections import defaultdict

setup_logging()
logger = logging.getLogger(__name__)


def slugify(text: str) -> str:
    """
    Converts a given text string into a slug format.

    The slug format is lowercase, contains only alphanumeric characters,
    whitespace characters, and hyphens, and does not contain any leading or
    trailing hyphens.

    :param text: The text string to be converted into a slug format.
    :return: The slug formatted text string.
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text).strip('-')
    return text


class KBIntegrator:
    def __init__(self, vault_path: Path, templates_config: dict, project_root: Path) -> None:
        self.vault_path = vault_path
        self.project_root = project_root
        self.templates_config = templates_config

    def create_note(self, data: EnrichedData) -> str:
        """
        Creates a note in the Obsidian vault based on the given EnrichedData object.

        The note is created in the category-specific directory, with a filename
        containing the date and the slugified title of the original file.

        If an error occurs during the creation of the note, an empty string is
        returned.

        :param data: The EnrichedData object containing the information to be
            written to the note.
        :return: The path to the created note as a string, or an empty string
            if an error occurred.
        """
        try:
            # Get the relative template path from the config
            default_template_path = self.templates_config.get("Default", "templates/default.md")
            template_path = self.templates_config.get(data.category, default_template_path)

            # Create an absolute path to the template file
            absolute_template_path = self.project_root / template_path
            template_content = absolute_template_path.read_text(encoding='utf-8')

            # Prepare the content to be written to the note
            title = Path(data.source_path).stem
            entity_md = ""
            for label, items in data.entities.items():
                entity_md += f"- **{label}:** {', '.join(f'[[{item}]]' for item in items)}\n"

            action_items_md = ""
            if data.action_items:
                for item in data.action_items:
                    action_items_md += f"- [ ] {item}\n"

            data_for_template = data.__dict__
            data_for_template['title'] = title
            data_for_template['entities_list'] = entity_md
            data_for_template['action_items_list'] = action_items_md

            safe_data = defaultdict(str, data_for_template)
            file_content = template_content.format_map(safe_data)

            # Create the target directory and write the note
            target_dir = self.vault_path / slugify(data.category)
            target_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{date.today().isoformat()}-{slugify(title)}.md"
            final_path = target_dir / filename
            final_path.write_text(file_content, encoding='utf-8')

            logging.info(f"Note created at: {final_path}")
            return str(final_path)
        except Exception as e:
            logger.error(f"Error creating note for file {data.source_path}: {e}", data.source_path)
            return ""
