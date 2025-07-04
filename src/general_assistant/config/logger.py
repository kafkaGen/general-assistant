from datetime import datetime
from pathlib import Path

from loguru import logger as loguru_logger


def format_console_record(record):
    base = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level:<8}</level> | "
        "<cyan>{extra[name]}</cyan> | "
        "<level>{message}</level>"
    )
    extras = [f"{v}" for k, v in record["extra"].items() if k != "name"]
    if extras:
        base += " | <magenta>" + " | ".join(extras) + "</magenta>"
    base += "\n"
    return base


def format_file_record(record):
    base = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level:<8} | "
        "{extra[name]} | "
        "{function}:{line} | "
        "{message}"
    )
    extras = [f"{v}" for k, v in record["extra"].items() if k != "name"]
    if extras:
        base += " | " + " | ".join(extras)
    return base


def create_logger(
    logger_name: str,
    console_level: str = "INFO",
    file_level: str = "DEBUG",
    rotation_size: str = "512 MB",
    retention_count: int = 3,
    compression: str = "gz",
):
    """
    Create a Loguru logger with console and file handlers

    Args:
        logger_name: Name of the logger (used for directory and file naming)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        rotation_size: File size before rotation (e.g., "512 MB", "100 MB")
        retention_count: Number of rotated files to keep
        compression: Compression format for rotated files ("gz", "bz2", "xz")

    Returns:
        Configured Loguru logger instance
    """
    # Create log directory
    log_dir = Path("logs") / logger_name
    log_dir.mkdir(parents=True, exist_ok=True)

    # Generate datetime string for filename
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{logger_name}_{current_time}.log"
    log_filepath = log_dir / log_filename

    # Remove root handlers
    try:
        loguru_logger.remove(0)
    except ValueError:
        # root handler is already removed
        pass

    # Create a new logger instance
    new_logger = loguru_logger.bind(name=logger_name)

    # Add console handler
    new_logger.add(
        sink=lambda msg: print(msg, end=""),
        level=console_level,
        format=format_console_record,
        colorize=True,
        filter=lambda record: record["extra"].get("name") == logger_name,
    )

    # Add file handler with rotation
    new_logger.add(
        sink=str(log_filepath),
        level=file_level,
        format=format_file_record,
        rotation=rotation_size,
        retention=retention_count,
        compression=compression,
        enqueue=False,  # Thread-safe logging
        backtrace=True,  # Better error tracing
        diagnose=True,  # Detailed error information
        filter=lambda record: record["extra"].get("name") == logger_name,
    )

    return new_logger
