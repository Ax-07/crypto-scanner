"""
Récupération et préparation des données OHLCV
"""

import pandas as pd
import time
import ccxt
import config
from logger import get_logger

logger = get_logger()


def fetch_ohlcv(exchange, symbol, timeframe=None, limit=None):
    """
    Récupère les données OHLCV pour un symbole donné

    Args:
        exchange: Instance ccxt de l'exchange
        symbol (str): Symbole de la paire (ex: 'BTC/USDT')
        timeframe (str): Timeframe des bougies (par défaut: config.TIMEFRAME)
        limit (int): Nombre de bougies à récupérer (par défaut: config.MIN_OHLCV_BARS)

    Returns:
        pd.DataFrame: DataFrame avec colonnes [time, open, high, low, close, volume]
        None: En cas d'erreur
    """
    if timeframe is None:
        timeframe = config.TIMEFRAME
    if limit is None:
        limit = config.MIN_OHLCV_BARS

    retry_count = 0
    delay = config.RETRY_DELAY

    while retry_count < config.MAX_RETRIES:
        try:
            logger.debug(f"Récupération OHLCV pour {symbol} ({timeframe}, limit={limit})")

            ohlcv = exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit
            )

            if not ohlcv or len(ohlcv) == 0:
                logger.warning(f"Aucune donnée OHLCV pour {symbol}")
                return None

            # Conversion en DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['time', 'open', 'high', 'low', 'close', 'volume']
            )

            # Conversion du timestamp en datetime
            df['time'] = pd.to_datetime(df['time'], unit='ms')

            # S'assurer que les colonnes OHLC sont bien numériques
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            logger.debug(f"✓ {len(df)} bougies récupérées pour {symbol}")
            return df

        except ccxt.RateLimitExceeded:
            logger.warning(f"Rate limit dépassé pour {symbol}, attente de {delay}s...")
            time.sleep(delay)
            delay *= 2  # Backoff exponentiel
            retry_count += 1

        except ccxt.NetworkError as e:
            logger.warning(f"Erreur réseau pour {symbol} (tentative {retry_count + 1}/{config.MAX_RETRIES}): {str(e)}")
            time.sleep(delay)
            delay *= 2
            retry_count += 1

        except ccxt.ExchangeError as e:
            logger.error(f"Erreur exchange pour {symbol}: {str(e)}")
            return None

        except Exception as e:
            logger.error(f"Erreur inattendue pour {symbol}: {str(e)}")
            return None

    logger.error(f"Échec après {config.MAX_RETRIES} tentatives pour {symbol}")
    return None


def get_last_closed_candle(df):
    """
    Retourne les informations de la dernière bougie clôturée

    Args:
        df (pd.DataFrame): DataFrame OHLCV

    Returns:
        dict: Dictionnaire avec time, open, high, low, close, volume
        None: Si le DataFrame est vide
    """
    if df is None or len(df) == 0:
        return None

    # On prend la dernière ligne (dernière bougie clôturée)
    last = df.iloc[-1]

    return {
        'time': last['time'],
        'open': last['open'],
        'high': last['high'],
        'low': last['low'],
        'close': last['close'],
        'volume': last['volume']
    }
