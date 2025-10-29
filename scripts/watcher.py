import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import logging
from file_handler import get_file_text


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class Watcher(FileSystemEventHandler):
    def on_created(self, event):
        """
        Called when a file or directory is created within the directory that is being watched.
        Logs a message to the console indicating that a new file has been detected.
        :param event: A FileSystemEvent object that contains information about the file that was created.
        """
        if event.is_directory:
            return

        src_path_str: str
        if isinstance(event.src_path, str):
            src_path_str = event.src_path
        else:
            # event.src_path may be bytes or a memoryview (e.g. from some backends); convert to bytes then decode.
            try:
                src_bytes = bytes(event.src_path)
            except TypeError:
                # Fallback to string representation if conversion to bytes is not supported.
                src_path_str = str(event.src_path)
            else:
                src_path_str = src_bytes.decode("utf-8", "surrogateescape")

        logging.info(f"New file detected: {event.src_path}")
        process_file(src_path_str)


def start_watching(path: str):
    """
    Start watching the given directory for any changes.

    :param path: The path to the directory that should be watched for changes.
    """
    event_hander = Watcher()
    observer = Observer()
    observer.schedule(event_hander, path=path, recursive=False)
    observer.start()

    logging.info(f"Started watching directory {path}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info(f"Stopped watching directory {path}")
        observer.join()


def process_file(file_path: str):
    """
    Process the newly created file.

    :param file_path: The path to the newly created file.
    """
    logging.info(f"Processing file: {file_path}")
    text_content = get_file_text(file_path)
    if text_content:
        logging.info(f"Extracted text content: {text_content[:100]}...")
    else:
        logging.warning("No text content could be extracted from the file")


if __name__ == "__main__":
    watch_path = "../inbox"
    start_watching(watch_path)
