import logging

class ColorFormatter(logging.Formatter):
    """
    Custom logging formatter to add colors based on log level
    """
    RESET = "\033[0m"
    COLORS = {
        logging.DEBUG: "\033[36m",  # Cyan
        logging.INFO: "\033[33m",  # Yellow
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[31m",  # Red
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        record.msg = f"{color}{record.msg}{self.RESET}"
        return super().format(record)

def start_logger(level: str = "DEBUG") -> logging.Logger:
    """
    This will start the logger for the application

    Args:
        level (str): The logging level to use

    Returns:
        logging.Logger: The configured logger
    """
    # set logger data
    LOG = logging.getLogger(__name__)
    LOG.setLevel(level)

    # Attach the handler to your logger
    if not LOG.hasHandlers():
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # THIS IS THE KEY: use ColorFormatter, not plain Formatter
        formatter = ColorFormatter("%(asctime)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)

        LOG.addHandler(ch)

    return LOG