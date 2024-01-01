import datetime
import enum
import logging
import os
import pathlib
import typing as t

__all__: t.Tuple[str, ...] = ("Logger",)


FLAIR: int = 95
FORMAT: str = "[%(asctime)s] | %(pathname)s:%(lineno)d | %(levelname)s | %(message)s"


class LogLevelColors(enum.Enum):
    DEBUG = "\033[96m"
    INFO = "\033[92m"
    WARNING = "\033[93m"
    ERROR = "\033[33m"
    CRITICAL = "\033[91m"
    ENDC = "\033[0m"
    FLAIR = "\033[95m"


class RelativePathFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.pathname = record.pathname.replace(os.getcwd(), "~")
        return True


class Formatter(logging.Formatter):
    def __init__(self) -> None:
        super().__init__(fmt=FORMAT, datefmt="%H:%M:%S", style="%")

    def format(self, record: logging.LogRecord) -> str:
        return f"{LogLevelColors[record.levelname].value}{super().format(record)}{LogLevelColors.ENDC.value}"


class FileHandler(logging.FileHandler):
    _last_entry: datetime.datetime = datetime.datetime.today()

    def __init__(self, *, ext: str, folder: t.Union[pathlib.Path, str] = "logs") -> None:
        self.folder = pathlib.Path(folder)
        self.ext = ext
        self.folder.mkdir(exist_ok=True)
        super().__init__(
            self.folder / f"{datetime.datetime.today().strftime('%Y-%m-%d')}-{ext}.log",
            encoding="utf-8",
        )
        self.setFormatter(Formatter())

    def emit(self, record: logging.LogRecord) -> None:
        if self._last_entry.date() != datetime.datetime.today().date():
            self._last_entry = datetime.datetime.today()
            self.close()
            self.baseFilename = (self.folder / f"{self._last_entry.strftime('%Y-%m-%d')}-{self.ext}.log").as_posix()
            self.stream = self._open()
        super().emit(record)


class Logger(logging.Logger):
    file_handler: t.Optional[FileHandler] = None

    def __init__(self, *, name: str, level: int = logging.DEBUG, file_logging: bool = False) -> None:
        super().__init__(name, level)
        self._handler = logging.StreamHandler()
        self._handler.addFilter(RelativePathFilter())
        self._handler.setFormatter(Formatter())
        self.addHandler(self._handler)
        if file_logging:
            self._file_handler = FileHandler(ext=name)
            self._file_handler.addFilter(RelativePathFilter())
            self.addHandler(self._file_handler)
        logging.addLevelName(FLAIR, "FLAIR")

    def set_formatter(self, formatter: logging.Formatter) -> None:
        self._handler.setFormatter(formatter)
        if self._file_handler is not None:
            self._file_handler.setFormatter(formatter)

    def flair(self, message: str, *args: t.Any, **kwargs: t.Any) -> None:
        self.log(FLAIR, message, *args, **kwargs)
