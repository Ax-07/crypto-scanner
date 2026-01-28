"""
Utilitaires de calcul d'indicateurs techniques pour les graphiques
Fonctions pures pour calculer SMA, EMA, RSI, MACD, Bollinger Bands, Stochastic
"""

import pandas as pd


class ChartCalculator:
    """Calcule indicateurs pour affichage graphique"""

    @staticmethod
    def calculate_sma(df, period):
        """
        Calcule la Simple Moving Average (SMA)

        Args:
            df (pd.DataFrame): DataFrame avec colonne 'close'
            period (int): Période de la moyenne (ex: 20, 50)

        Returns:
            pd.Series: Série des valeurs SMA
        """
        if df is None or 'close' not in df.columns:
            return pd.Series(dtype=float)

        return df['close'].rolling(window=period, min_periods=period).mean()

    @staticmethod
    def calculate_ema(df, period):
        """
        Calcule l'Exponential Moving Average (EMA)

        Args:
            df (pd.DataFrame): DataFrame avec colonne 'close'
            period (int): Période de la moyenne (ex: 20, 50)

        Returns:
            pd.Series: Série des valeurs EMA
        """
        if df is None or 'close' not in df.columns:
            return pd.Series(dtype=float)

        return df['close'].ewm(span=period, adjust=False, min_periods=period).mean()

    @staticmethod
    def calculate_rsi(df, period=14):
        """
        Calcule le RSI (Relative Strength Index)
        Implémentation méthode Wilder

        Args:
            df (pd.DataFrame): DataFrame avec colonne 'close'
            period (int): Période du RSI (défaut: 14)

        Returns:
            pd.Series: Série des valeurs RSI (0-100)
        """
        if df is None or 'close' not in df.columns or len(df) < period + 1:
            return pd.Series(dtype=float)

        prices = df['close']
        delta = prices.diff()

        # Séparer gains et pertes
        gains = delta.copy()
        losses = delta.copy()

        gains[gains < 0] = 0
        losses[losses > 0] = 0
        losses = abs(losses)

        # Calcul moyennes (méthode Wilder)
        avg_gain = gains.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        avg_loss = losses.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

        # Calcul RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def calculate_macd(df, fast=12, slow=26, signal=9):
        """
        Calcule le MACD (Moving Average Convergence Divergence)

        Args:
            df (pd.DataFrame): DataFrame avec colonne 'close'
            fast (int): Période EMA rapide (défaut: 12)
            slow (int): Période EMA lente (défaut: 26)
            signal (int): Période ligne de signal (défaut: 9)

        Returns:
            dict: {
                'macd': pd.Series,      # MACD Line
                'signal': pd.Series,    # Signal Line
                'histogram': pd.Series  # Histogramme (MACD - Signal)
            }
        """
        if df is None or 'close' not in df.columns:
            return {
                'macd': pd.Series(dtype=float),
                'signal': pd.Series(dtype=float),
                'histogram': pd.Series(dtype=float)
            }

        prices = df['close']

        # Calcul EMAs
        ema_fast = prices.ewm(span=fast, adjust=False, min_periods=fast).mean()
        ema_slow = prices.ewm(span=slow, adjust=False, min_periods=slow).mean()

        # MACD Line
        macd_line = ema_fast - ema_slow

        # Signal Line
        signal_line = macd_line.ewm(span=signal, adjust=False, min_periods=signal).mean()

        # Histogramme
        histogram = macd_line - signal_line

        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }

    @staticmethod
    def calculate_bollinger_bands(df, period=20, std_dev=2):
        """
        Calcule les Bollinger Bands

        Args:
            df (pd.DataFrame): DataFrame avec colonne 'close'
            period (int): Période de la SMA (défaut: 20)
            std_dev (int): Nombre d'écarts-types (défaut: 2)

        Returns:
            dict: {
                'upper': pd.Series,  # Bande supérieure
                'middle': pd.Series, # Bande médiane (SMA)
                'lower': pd.Series   # Bande inférieure
            }
        """
        if df is None or 'close' not in df.columns:
            return {
                'upper': pd.Series(dtype=float),
                'middle': pd.Series(dtype=float),
                'lower': pd.Series(dtype=float)
            }

        prices = df['close']

        # Bande médiane (SMA)
        middle_band = prices.rolling(window=period, min_periods=period).mean()

        # Écart-type
        std = prices.rolling(window=period, min_periods=period).std()

        # Bandes supérieure et inférieure
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)

        return {
            'upper': upper_band,
            'middle': middle_band,
            'lower': lower_band
        }

    @staticmethod
    def calculate_stochastic(df, k_period=14, d_period=3):
        """
        Calcule le Stochastic Oscillator

        Args:
            df (pd.DataFrame): DataFrame avec colonnes 'high', 'low', 'close'
            k_period (int): Période %K (défaut: 14)
            d_period (int): Période %D (défaut: 3, SMA de %K)

        Returns:
            dict: {
                'k': pd.Series,  # %K
                'd': pd.Series   # %D (SMA de %K)
            }
        """
        if df is None or not all(col in df.columns for col in ['high', 'low', 'close']):
            return {
                'k': pd.Series(dtype=float),
                'd': pd.Series(dtype=float)
            }

        # Plus haut et plus bas sur période K
        low_min = df['low'].rolling(window=k_period, min_periods=k_period).min()
        high_max = df['high'].rolling(window=k_period, min_periods=k_period).max()

        # %K = 100 * (Close - Low) / (High - Low)
        k_percent = 100 * ((df['close'] - low_min) / (high_max - low_min))

        # %D = SMA de %K
        d_percent = k_percent.rolling(window=d_period, min_periods=d_period).mean()

        return {
            'k': k_percent,
            'd': d_percent
        }
