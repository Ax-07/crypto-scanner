"""
Système de logging pour le scanner
Logs dans la console et/ou fichier selon la configuration
"""

import logging
import os
import config


def setup_logger():
    """
    Configure et retourne le logger principal du scanner
    """
    logger = logging.getLogger("scanner")
    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))

    # Éviter les doublons de handlers si appelé plusieurs fois
    if logger.handlers:
        return logger

    # Format des logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler console
    if config.LOG_TO_CONSOLE:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Handler fichier
    if config.LOG_TO_FILE:
        # Créer le dossier logs s'il n'existe pas
        log_dir = os.path.dirname(config.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.FileHandler(config.LOG_FILE, encoding='utf-8')
        file_handler.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger():
    """
    Retourne le logger (ou le crée s'il n'existe pas)
    """
    logger = logging.getLogger("scanner")
    if not logger.handlers:
        return setup_logger()
    return logger
