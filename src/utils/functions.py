import os
from datetime import datetime

import pytz
import yaml
from pydantic import ValidationError

from src.settings.configuration import AgentsConfiguration
from src.utils.logger import create_logger

functions_logger = create_logger("functions")


def get_agents_configuration() -> dict:
    agents_configuration_path = os.getenv("AGENTS_CONFIGURATION_PATH")
    if not agents_configuration_path:
        functions_logger.error("AGENTS_CONFIGURATION_PATH is not set.")
        raise ValueError("AGENTS_CONFIGURATION_PATH is not set.")

    try:
        with open(agents_configuration_path) as fl:
            agents_configuration = yaml.safe_load(fl)
    except FileNotFoundError as e:
        functions_logger.error(
            f"Agents configuration file not found at {agents_configuration_path}."
        )
        raise ValueError(
            f"Agents configuration file not found at {agents_configuration_path}."
        ) from e
    except yaml.YAMLError as e:
        functions_logger.error(
            f"Invalid agents configuration file at {agents_configuration_path}."
        )
        raise ValueError(
            f"Invalid agents configuration file at {agents_configuration_path}."
        ) from e

    try:
        agents_configuration = AgentsConfiguration.model_validate(
            agents_configuration
        ).model_dump()
        functions_logger.info(
            f"Loaded agents configuration from {agents_configuration_path}."
        )
    except ValidationError as e:
        functions_logger.error(
            f"Invalid agents configuration file at {agents_configuration_path}."
        )
        raise e

    return agents_configuration


def get_date(timezone: str = "UTC") -> str:
    try:
        current_datetime = datetime.now(pytz.timezone(timezone))
    except pytz.exceptions.UnknownTimeZoneError:
        functions_logger.warning(f"Unknown timezone '{timezone}', using UTC instead.")
        current_datetime = datetime.now(pytz.UTC)

    return current_datetime.strftime("%A, %d/%m/%Y")
