"""
Module de récupération des données OHLCV pour les graphiques
Récupère les données de Binance via ccxt
"""

import ccxt
import pandas as pd
from logger import get_logger

logger = get_logger()


class OHLCVFetcher:
    """Récupère données OHLCV pour graphiques"""

    def __init__(self, exchange):
        """
        Initialise le fetcher avec une instance d'exchange

        Args:
            exchange: Instance ccxt.Exchange (Binance)
        """
        self.exchange = exchange

    def fetch_ohlcv(self, symbol, timeframe='4h', limit=200):
        """
        Récupère les données OHLCV pour une paire

        Args:
            symbol (str): Symbole de la paire (ex: 'BTC/USDC')
            timeframe (str): Timeframe des bougies (ex: '4h', '1d')
            limit (int): Nombre de bougies à récupérer (défaut: 200)

        Returns:
            pd.DataFrame: DataFrame avec colonnes [timestamp, open, high, low, close, volume]
                         Index = datetime
            None: En cas d'erreur
        """
        try:
            logger.info(f"Fetch OHLCV pour {symbol} (timeframe={timeframe}, limit={limit})")

            # Récupérer les données OHLCV
            ohlcv = self.exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                limit=limit
            )

            if not ohlcv:
                logger.warning(f"Aucune donnée OHLCV reçue pour {symbol}")
                return None

            # Convertir en DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )

            # Convertir timestamp (ms) en datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            # Définir l'index comme timestamp
            df.set_index('timestamp', inplace=True)

            logger.info(f"✅ {len(df)} bougies récupérées pour {symbol}")

            return df

        except ccxt.NetworkError as e:
            logger.error(f"❌ Erreur réseau lors du fetch OHLCV pour {symbol}: {str(e)}")
            return None
        except ccxt.ExchangeError as e:
            logger.error(f"❌ Erreur exchange lors du fetch OHLCV pour {symbol}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur inattendue lors du fetch OHLCV pour {symbol}: {str(e)}")
            return None
