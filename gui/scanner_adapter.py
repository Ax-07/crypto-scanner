"""
Adaptateur pour permettre l'utilisation du scanner depuis la GUI
Ajoute le support des callbacks de progression sans modifier scanner.py
"""

import exchange
import scanner
from logger import get_logger

logger = get_logger()


def run_scan(exchange_instance=None, progress_callback=None, log_callback=None):
    """
    Wrapper pour scan_market() qui ajoute le support des callbacks

    Args:
        exchange_instance: Instance exchange (optionnel, sera créée si None)
        progress_callback: Fonction callback(current, total) pour progression
        log_callback: Fonction callback(message) pour logs

    Returns:
        list: Résultats du scan
    """
    # Si pas d'exchange fourni, en créer un
    if exchange_instance is None:
        if log_callback:
            log_callback("Initialisation de l'exchange...")
        exchange_instance = exchange.init_exchange()

    # Monkey patch temporaire du logger pour capturer les logs
    original_info = logger.info
    original_warning = logger.warning
    original_error = logger.error

    def patched_info(msg):
        original_info(msg)
        if log_callback:
            log_callback(msg)

    def patched_warning(msg):
        original_warning(msg)
        if log_callback:
            log_callback(f"⚠️ {msg}")

    def patched_error(msg):
        original_error(msg)
        if log_callback:
            log_callback(f"❌ {msg}")

    # Appliquer le patch
    logger.info = patched_info
    logger.warning = patched_warning
    logger.error = patched_error

    try:
        # Lancer le scan
        results = scanner.scan_market()
        return results

    finally:
        # Restaurer le logger
        logger.info = original_info
        logger.warning = original_warning
        logger.error = original_error
