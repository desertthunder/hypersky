"""Loggers."""

import datetime
import logging


class LogFormatter(logging.Formatter):
    """Custom Formatter for BlueSky Logger."""

    DODGER_BLUE = "\033[38;5;25m"
    ERROR = "\033[91m"
    WARNING = "\033[93m"
    CRITICAL = "\033[95m"
    RESET = "\033[0m"

    def colorize(self, text: str, level: int) -> str:
        """Colorize log message."""
        match level:
            case logging.ERROR:
                return f"{self.ERROR}{text}{self.RESET}"
            case logging.WARNING:
                return f"{self.WARNING}{text}{self.RESET}"
            case logging.CRITICAL:
                return f"{self.CRITICAL}{text}{self.RESET}"
            case _:
                return f"{self.DODGER_BLUE}{text}{self.RESET}"

    def level_tag(self, record: logging.LogRecord) -> str:
        """Get level tag."""
        tag = f"[{record.levelname[:4]}]"
        match record.levelno:
            case logging.ERROR:
                return f"{self.ERROR}{tag}{self.RESET}"
            case logging.WARNING:
                return f"{self.WARNING}{tag}{self.RESET}"
            case logging.CRITICAL:
                return f"{self.CRITICAL}{tag}{self.RESET}"
            case _:
                return f"{self.DODGER_BLUE}{tag}{self.RESET}"

    def format_message(self, record: logging.LogRecord) -> str:
        """Build log message."""
        message = super().format(record)

        message = self.colorize(message, record.levelno)
        level = self.colorize(f"[{record.levelname[:4]}]", record.levelno)

        path = f"{record.filename}.{record.funcName}:{record.lineno}"
        timestamp = datetime.datetime.fromtimestamp(record.created).strftime(
            "%Y-%m-%d %H:%M:%S",
        )

        return f"{timestamp} {level} {path} {message}"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record.

        Makes the log message dodgerblue.
        """
        return self.format_message(record)


class Log(logging.Logger):
    """BlueSky Logger."""

    def __init__(self, name: str = "blue_sky_service") -> None:
        """Initialize the BlueSky Logger."""
        super().__init__(name)
        self.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setFormatter(LogFormatter())

        self.addHandler(handler)


blue_sky_logger = Log()
