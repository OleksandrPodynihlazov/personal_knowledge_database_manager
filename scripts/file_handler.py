import logging
from pathlib import Path
import abc
from unstructured.partition.auto import partition


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class FileConverter(abc.ABC):
    @abc.abstractmethod
    def convert(self, file_path: str) -> str:
        pass


class UnstructuredConverter(FileConverter):
    def convert(self, file_path: str) -> str:
        """
        Converts a file to a string of unstructured text.

        :param file_path: The path to the file that should be converted.
        :return: A string of unstructured text if the conversion was successful, otherwise an empty string.
        :raises Exception: An exception is raised if there is an error during the conversion process.
        """
        try:
            element_list = partition(file_path)
            text_content = "\n\n".join([str(element) for element in element_list])
            logging.info(f"File converted successfully: {file_path}")
            return text_content
        except Exception as e:
            logging.error(f"Error converting file {file_path}: {e}")
            return ""


unstructured_converter_instance = UnstructuredConverter()

UNSTRUCTURED_SUPPORTED_EXTENSIONS = [
    ".txt", ".doc", ".docx", ".pdf", ".md", ".csv", ".tsv", ".xls", ".xlsx",
    ".ppt", ".pptx", ".epub", ".html", ".hml", ".png", ".jpg", ".jpeg",
    ".heic", ".log", ".rtf", ".js", ".py", ".cpp", ".c", ".ts"
]

CONVERTERS = dict.fromkeys(UNSTRUCTURED_SUPPORTED_EXTENSIONS, UnstructuredConverter())


def get_file_text(file_path: str) -> str | None:
    """
    Gets the text content of the given file using the appropriate converter.

    :param file_path: The path to the file whose text content should be retrieved.
    :return: The text content of the given file, or None if no converter is found for the given file extension.
    """
    extension = Path(file_path).suffix.lower()
    converter_class = CONVERTERS.get(extension)
    if converter_class is None:
        logging.warning(f"No converter found for file extension: {extension}")
        return None
    return converter_class.convert(file_path)
