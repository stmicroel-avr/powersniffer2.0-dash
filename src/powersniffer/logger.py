import logging

def _configure_logging() -> None:
    """
    Configure logging for the application.
    :return:
    """
    logging.basicConfig(
        level=logging.INFO,
        format="[%(process)d] [%(levelname)s] %(asctime)s - %(message)s"
    )


def get_app_logger(name: str) -> logging.Logger:
    """
    Get logger for the application.

    :param name: App / module name
    :return:
    """
    _configure_logging()
    return logging.getLogger(name)