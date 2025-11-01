from datetime import date
from scripts.enricher import EnrichedData
import re
from pathlib import Path
from scripts.logging_config import setup_logging
import logging

setup_logging()


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
    def __init__(self, vault_path: str) -> None:
        self.vault_path = Path(vault_path)

    def create_note(self, data: EnrichedData) -> str:
        """
        Creates a note in the specified vault path based on the given EnrichedData.

        The note is created in a directory with the same name as the category of the EnrichedData.
        The filename of the note is a combination of the current date and the slugified title of the EnrichedData.

        The content of the note is based on a template that is selected based on the category of the EnrichedData.
        The template is formatted with the
        category, source path, title, entities, text, and attendees of the EnrichedData.

        :param data: The EnrichedData object that contains the information to be used for creating the note.
        :return: The path to the created note as a string.
        """
        templates = {
                "Technical Article": """---
        type: article
        category: {category}
        source: {source_path}
        tags: [article]
        ---
        # {title}

        ## Entities
        {entities}

        ## Full Text
        {text}
        """,
                "Meeting Notes": """---
        type: meeting
        category: {category}
        source: {source_path}
        tags: [meeting]
        ---
        # {title}

        ## Attendees
        {attendees}

        ## Full Text
        {text}
        """,
                "default": """---
        type: note
        category: {category}
        source: {source_path}
        ---
        # {title}

        {text}
        """
             }
        try:
            template = templates.get(data.category, templates["default"])
            title = Path(data.source_path).stem
            entity_md = ""
            for label, items in data.entities.items():
                entity_md += f"- **{label}:** {', '.join(f'[[{item}]]' for item in items)}\n"

            file_content = template.format(
                category=data.category,
                source_path=data.source_path,
                title=title,
                entities=entity_md,
                text=data.text,
                attendees=""
            )
            target_dir = self.vault_path / slugify(data.category)
            target_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{date.today().isoformat()}-{slugify(title)}.md"
            final_path = target_dir / filename
            final_path.write_text(file_content, encoding='utf-8')
            logging.info(f"Note created at: {final_path}")
            return str(final_path)
        except Exception as e:
            logging.error(f"Error creating note for file {data.source_path}: {e}")
            return ""
