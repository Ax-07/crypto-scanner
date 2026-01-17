"""
Calcul d'indicateurs techniques
RSI (V1) + SMA/EMA (V1.5)
"""

import pandas as pd
import numpy as np
from logger import get_logger

logger = get_logger()


def calculate_rsi(prices, period=14):
    """
    Calcule le RSI (Relative Strength Index) sur une série de prix
    Implémentation standard avec moyennes mobiles exponentielles (méthode de Wilder)

    Args:
        prices (pd.Series): Série des prix de clôture
        period (int): Période du RSI (par défaut 14)

    Returns:
        pd.Series: Série des valeurs RSI (0-100)
        None: En cas d'erreur
    """
    try:
        if prices is None or len(prices) < period + 1:
            logger.warning(f"Données insuffisantes pour calculer RSI (besoin de {period + 1} valeurs, reçu {len(prices) if prices is not None else 0})")
            return None

        # Réinitialiser l'index pour éviter les problèmes
        prices = prices.reset_index(drop=True)

        # Calcul des variations de prix
        delta = prices.diff()

        # Séparer les gains et les pertes
        gains = delta.copy()
        losses = delta.copy()

        gains[gains < 0] = 0
        losses[losses > 0] = 0
        losses = abs(losses)

        # Calcul initial : moyenne simple sur la période
        avg_gain = pd.Series(index=gains.index, dtype=float)
        avg_loss = pd.Series(index=losses.index, dtype=float)

        # Première moyenne (moyenne simple)
        avg_gain.iloc[period] = gains.iloc[1:period+1].mean()
        avg_loss.iloc[period] = losses.iloc[1:period+1].mean()

        # Application de la méthode de Wilder (EMA avec alpha = 1/period)
        for i in range(period + 1, len(gains)):
            avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gains.iloc[i]) / period
            avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + losses.iloc[i]) / period

        # Calcul du RSI
        rsi = pd.Series(index=prices.index, dtype=float)

        for i in range(period, len(prices)):
            if avg_loss.iloc[i] == 0:
                # Si pas de pertes, RSI = 100
                rsi.iloc[i] = 100.0
            elif avg_gain.iloc[i] == 0:
                # Si pas de gains, RSI = 0
                rsi.iloc[i] = 0.0
            else:
                # Calcul normal
                rs = avg_gain.iloc[i] / avg_loss.iloc[i]
                rsi.iloc[i] = 100 - (100 / (1 + rs))

        return rsi

    except Exception as e:
        logger.error(f"Erreur lors du calcul du RSI: {str(e)}")
        return None


def get_latest_rsi(prices, period=14):
    """
    Calcule le RSI et retourne la dernière valeur

    Args:
        prices (pd.Series): Série des prix de clôture
        period (int): Période du RSI

    Returns:
        float: Dernière valeur du RSI
        None: En cas d'erreur ou données insuffisantes
    """
    rsi_series = calculate_rsi(prices, period)

    if rsi_series is None:
        return None

    # Récupérer la dernière valeur non-NaN
    rsi_clean = rsi_series.dropna()

    if len(rsi_clean) == 0:
        logger.warning("Aucune valeur RSI valide calculée")
        return None

    last_rsi = rsi_clean.iloc[-1]

    # Vérifier que la valeur est valide
    if pd.isna(last_rsi) or not np.isfinite(last_rsi):
        logger.warning(f"Valeur RSI invalide: {last_rsi}")
        return None

    return float(last_rsi)


# ============================================================================
# MOYENNES MOBILES (V1.5)
# ============================================================================

def calculate_sma(prices, period=20):
    """
    Calcule la SMA (Simple Moving Average) sur une série de prix

    Args:
        prices (pd.Series): Série des prix de clôture
        period (int): Période de la SMA (par défaut 20)

    Returns:
        pd.Series: Série des valeurs SMA
        None: En cas d'erreur
    """
    try:
        if prices is None or len(prices) < period:
            logger.warning(f"Données insuffisantes pour calculer SMA{period} (besoin de {period} valeurs, reçu {len(prices) if prices is not None else 0})")
            return None

        # Calcul de la moyenne mobile simple
        sma = prices.rolling(window=period).mean()

        return sma

    except Exception as e:
        logger.error(f"Erreur lors du calcul de la SMA{period}: {str(e)}")
        return None


def calculate_ema(prices, period=20):
    """
    Calcule l'EMA (Exponential Moving Average) sur une série de prix

    Args:
        prices (pd.Series): Série des prix de clôture
        period (int): Période de l'EMA (par défaut 20)

    Returns:
        pd.Series: Série des valeurs EMA
        None: En cas d'erreur
    """
    try:
        if prices is None or len(prices) < period:
            logger.warning(f"Données insuffisantes pour calculer EMA{period} (besoin de {period} valeurs, reçu {len(prices) if prices is not None else 0})")
            return None

        # Calcul de la moyenne mobile exponentielle
        # span = période, donne plus de poids aux valeurs récentes
        ema = prices.ewm(span=period, adjust=False).mean()

        return ema

    except Exception as e:
        logger.error(f"Erreur lors du calcul de l'EMA{period}: {str(e)}")
        return None


def detect_trend(prices, sma20, sma50, ema20, ema50):
    """
    Détecte si la tendance est haussière ou baissière

    Logique :
    - Haussier si : Prix > SMA20 ET Prix > SMA50 OU EMA20 > EMA50
    - Baissier sinon

    Args:
        prices (pd.Series): Série des prix de clôture
        sma20 (pd.Series): SMA période 20
        sma50 (pd.Series): SMA période 50
        ema20 (pd.Series): EMA période 20
        ema50 (pd.Series): EMA période 50

    Returns:
        bool: True si tendance haussière, False si baissière
        None: En cas d'erreur ou données insuffisantes
    """
    try:
        # Vérifier que toutes les séries ont des données
        if any(x is None for x in [prices, sma20, sma50, ema20, ema50]):
            logger.warning("Données manquantes pour la détection de tendance")
            return None

        # Récupérer les dernières valeurs valides
        last_price = prices.dropna().iloc[-1] if len(prices.dropna()) > 0 else None
        last_sma20 = sma20.dropna().iloc[-1] if len(sma20.dropna()) > 0 else None
        last_sma50 = sma50.dropna().iloc[-1] if len(sma50.dropna()) > 0 else None
        last_ema20 = ema20.dropna().iloc[-1] if len(ema20.dropna()) > 0 else None
        last_ema50 = ema50.dropna().iloc[-1] if len(ema50.dropna()) > 0 else None

        # Vérifier qu'on a toutes les valeurs
        if None in [last_price, last_sma20, last_sma50, last_ema20, last_ema50]:
            logger.warning("Valeurs manquantes pour la détection de tendance")
            return None

        # Condition 1 : Prix > SMA20 ET Prix > SMA50
        price_above_sma = last_price > last_sma20 and last_price > last_sma50

        # Condition 2 : EMA20 > EMA50 (croisement haussier)
        ema_crossover = last_ema20 > last_ema50

        # Tendance haussière si l'une des deux conditions est vraie
        is_bullish = price_above_sma or ema_crossover

        logger.debug(f"Tendance: {'Haussière' if is_bullish else 'Baissière'} | Prix>{last_price:.2f} SMA20>{last_sma20:.2f} SMA50>{last_sma50:.2f} | EMA20>{last_ema20:.2f} EMA50>{last_ema50:.2f}")

        return is_bullish

    except Exception as e:
        logger.error(f"Erreur lors de la détection de tendance: {str(e)}")
        return None
