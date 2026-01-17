"""
Point d'entrée principal du scanner RSI Binance
Usage: python main.py
"""

import sys
from datetime import datetime
from logger import setup_logger
from scanner import scan_market
from output import output_results
import config


def main():
    """
    Fonction principale du scanner
    """
    # Initialiser le logger
    logger = setup_logger()

    print("\n" + "=" * 80)
    print("🔍 SCANNER RSI BINANCE")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Exchange: {config.EXCHANGE_ID}")
    print(f"Timeframe: {config.TIMEFRAME}")
    print(f"RSI période: {config.RSI_PERIOD}")
    print(f"Seuil RSI: < {config.RSI_THRESHOLD}")
    print(f"Quote: {config.QUOTE_FILTER}")
    print("=" * 80)
    print("\n⚠️  MODE SCANNER UNIQUEMENT - AUCUN TRADING\n")

    try:
        # Lancer le scan
        results = scan_market()

        # Afficher et exporter les résultats
        output_results(results)

        logger.info("Scanner terminé avec succès")
        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Arrêt demandé par l'utilisateur (Ctrl+C)")
        logger.warning("Arrêt du scanner par l'utilisateur")
        return 1

    except Exception as e:
        print(f"\n\n❌ Erreur fatale: {str(e)}")
        logger.error(f"Erreur fatale: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
