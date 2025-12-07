import logging
from logging.handlers import RotatingFileHandler

LOG_LEVEL = "INFO"

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"

# "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"


def configure_logging():
    level = LOG_LEVEL.upper()

    # проверяем что уровень валидный
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    if level not in valid_levels:
        level = "ERROR"

    # основной хендлер — в stdout
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT_DEBUG if level == "DEBUG" else LOG_FORMAT))

    # хендлер в файл (опционально)
    file_handler = RotatingFileHandler("app.log", maxBytes=10_000_000, backupCount=5)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    # корневой логгер
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    root.addHandler(handler)
    root.addHandler(file_handler)

    # отключаем спам uvicorn.access
    logging.getLogger("uvicorn.access").propagate = False

