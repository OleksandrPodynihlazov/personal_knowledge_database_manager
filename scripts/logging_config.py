import logging
import os
import shutil


QUARANTINE_PATH = os.path.abspath("../quarantine")


def setup_logging():
    """
    Sets up the logging module with a basic configuration.

    The logging level is set to INFO, and the format is set to
    '%(asctime)s - %(levelname)s - %(message)s' with the date format
    '%Y-%m-%d %H:%M:%S'.
    """
    logging.setLoggerClass(QuarantineLogger)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def quarantine(path: str):
    """
    Moves the given file to the quarantine directory.

    :param path: The path to the file that should be quarantined.
    :raises Exception: If there is an error during the quarantining process.
    """
    try:
        final_path = os.path.join(QUARANTINE_PATH, os.path.basename(path))
        os.makedirs(QUARANTINE_PATH, exist_ok=True)
        shutil.move(path, final_path)
        logging.info(f"Quarantining file: {path}")
    except Exception as e:
        logging.error(f"Failed to quarantine file {path}: {e}")


class QuarantineLogger(logging.Logger):
    def error(self, msg, *args, **kwargs):
        """
        Logs an error message with the given message and arguments.

        If the path argument is provided and the file exists,
        the file will be quarantined after logging the error message.

        :param msg: The error message to log.
        :param *args: Additional arguments to log.
        :param **kwargs: Additional keyword arguments to log, including the path argument.
        :raises Exception: If there is an error during the quarantining process.
        """
        path = kwargs.pop("path", None)

        if not path and args and isinstance(args[0], str) and os.path.exists(args[0]):
            path = args[0]
            args = args[1:]

        super().error(msg, *args, **kwargs)

        if path and os.path.exists(path):
            quarantine(path)
