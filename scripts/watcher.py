import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from logging_config import setup_logging
import logging
import subprocess
import sys

setup_logging()
logger = logging.getLogger(__name__)


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
        observer.stop()
        observer.join()


def process_file(file_path: str):
    """
    Process the given file using the main.py script.

    :param file_path: The path to the file that should be processed.
    :raises subprocess.CalledProcessError: If the file could not be processed using the main.py script.
    """
    try:
        subprocess.run([sys.executable, "../main.py", file_path], check=True)
        logging.info(f"Processed file successfully: {file_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error processing file {file_path}: {e}", file_path)


if __name__ == "__main__":
    watch_path = "../inbox"
    start_watching(watch_path)
