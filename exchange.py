"""
Gestion de l'exchange Binance via CCXT
Initialisation, chargement des marchés et filtrage des paires
"""

import ccxt
import config
from logger import get_logger

logger = get_logger()


def init_exchange():
    """
    Initialise la connexion à l'exchange Binance

    Returns:
        ccxt.Exchange: Instance de l'exchange configurée
    """
    logger.info(f"Initialisation de l'exchange {config.EXCHANGE_ID}...")

    exchange_class = getattr(ccxt, config.EXCHANGE_ID)

    exchange = exchange_class({
        'enableRateLimit': config.ENABLE_RATE_LIMIT,
        'timeout': 30000,  # 30 secondes
        'options': {
            'defaultType': config.MARKET_TYPE,
        }
    })

    logger.info(f"Exchange {config.EXCHANGE_ID} initialisé avec succès")
    return exchange


def load_markets(exchange):
    """
    Charge tous les marchés disponibles sur l'exchange

    Args:
        exchange: Instance ccxt de l'exchange

    Returns:
        dict: Dictionnaire des marchés
    """
    logger.info("Chargement des marchés...")
    markets = exchange.load_markets()
    logger.info(f"{len(markets)} marchés chargés")
    return markets


def filter_pairs(exchange):
    """
    Filtre les paires selon le scope défini dans la config

    Args:
        exchange: Instance ccxt de l'exchange

    Returns:
        list: Liste des symboles filtrés (ex: ['BTC/USDT', 'ETH/USDT', ...])
    """
    logger.info("Filtrage des paires selon le scope...")

    markets = exchange.markets
    filtered_symbols = []

    # Liste des stablecoins pour exclusion (si activé)
    stablecoins = ['USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'USDP', 'FDUSD']

    for symbol, market in markets.items():
        # Vérifier que le marché est actif
        if not market.get('active', False):
            continue

        # Vérifier le type de marché (spot uniquement)
        if market.get('type') != config.MARKET_TYPE:
            continue

        # Vérifier la quote currency
        if market.get('quote') != config.QUOTE_FILTER:
            continue

        # Exclure les paires stable/stable si activé
        if config.EXCLUDE_STABLE_PAIRS:
            base = market.get('base', '')
            if base in stablecoins:
                logger.debug(f"Exclusion paire stable/stable: {symbol}")
                continue

        filtered_symbols.append(symbol)

    # Appliquer la limite MAX_PAIRS si définie
    if config.MAX_PAIRS is not None and config.MAX_PAIRS > 0:
        filtered_symbols = filtered_symbols[:config.MAX_PAIRS]
        logger.warning(f"Limitation à {config.MAX_PAIRS} paires (config.MAX_PAIRS)")

    logger.info(f"{len(filtered_symbols)} paires correspondent au scope")
    logger.debug(f"Premières paires: {filtered_symbols[:5]}")

    return filtered_symbols


def get_filtered_pairs():
    """
    Fonction utilitaire qui initialise l'exchange et retourne les paires filtrées

    Returns:
        tuple: (exchange, filtered_symbols)
    """
    exchange = init_exchange()
    load_markets(exchange)
    filtered_symbols = filter_pairs(exchange)

    return exchange, filtered_symbols
