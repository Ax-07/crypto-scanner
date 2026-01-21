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
            logger.warning(
                f"Données insuffisantes pour calculer RSI (besoin de {period + 1} valeurs, reçu {len(prices) if prices is not None else 0})"
            )
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
        avg_gain.iloc[period] = gains.iloc[1:period + 1].mean()
        avg_loss.iloc[period] = losses.iloc[1:period + 1].mean()

        # Application de la méthode de Wilder (EMA avec alpha = 1/period)
        for i in range(period + 1, len(gains)):
            avg_gain.iloc[i] = (
                avg_gain.iloc[i - 1] * (period - 1) + gains.iloc[i]
            ) / period
            avg_loss.iloc[i] = (
                avg_loss.iloc[i - 1] * (period - 1) + losses.iloc[i]
            ) / period

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
            logger.warning(
                f"Données insuffisantes pour calculer SMA{period} (besoin de {period} valeurs, reçu {len(prices) if prices is not None else 0})"
            )
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
            logger.warning(
                f"Données insuffisantes pour calculer EMA{period} (besoin de {period} valeurs, reçu {len(prices) if prices is not None else 0})"
            )
            return None

        # Calcul de la moyenne mobile exponentielle
        # span = période, donne plus de poids aux valeurs récentes
        ema = prices.ewm(span=period, adjust=False).mean()

        return ema

    except Exception as e:
        logger.error(f"Erreur lors du calcul de l'EMA{period}: {str(e)}")
        return None


def detect_trend(prices, sma20=None, sma50=None, ema20=None, ema50=None):
    """
    Détecte si la tendance est haussière ou baissière
    Fonctionne avec SMA uniquement, EMA uniquement, ou les deux

    Logique :
    - Si SMA disponibles : Prix > SMA20 ET Prix > SMA50
    - Si EMA disponibles : EMA20 > EMA50 (croisement haussier)
    - Si les deux : Prix > SMA20 ET Prix > SMA50 OU EMA20 > EMA50
    - Haussier si au moins une condition est vraie

    Args:
        prices (pd.Series): Série des prix de clôture
        sma20 (pd.Series ou float): SMA période 20 (optionnel)
        sma50 (pd.Series ou float): SMA période 50 (optionnel)
        ema20 (pd.Series ou float): EMA période 20 (optionnel)
        ema50 (pd.Series ou float): EMA période 50 (optionnel)

    Returns:
        bool: True si tendance haussière, False si baissière
        None: En cas d'erreur ou données insuffisantes
    """
    try:
        # Vérifier qu'on a au moins un type de MA
        has_sma = sma20 is not None and sma50 is not None
        has_ema = ema20 is not None and ema50 is not None

        if not has_sma and not has_ema:
            logger.warning(
                "Aucune moyenne mobile fournie pour la détection de tendance"
            )
            return None

        # Récupérer le dernier prix (peut être Series ou float)
        if isinstance(prices, pd.Series):
            last_price = prices.dropna().iloc[-1] if len(prices.dropna()) > 0 else None
        else:
            last_price = float(prices) if prices is not None else None

        if last_price is None:
            logger.warning("Prix manquant pour la détection de tendance")
            return None

        conditions = []

        # Condition SMA : Prix > SMA20 ET Prix > SMA50
        if has_sma:
            # Convertir en float si c'est une Series
            if isinstance(sma20, pd.Series):
                last_sma20 = (
                    sma20.dropna().iloc[-1] if len(sma20.dropna()) > 0 else None
                )
            else:
                last_sma20 = float(sma20) if sma20 is not None else None

            if isinstance(sma50, pd.Series):
                last_sma50 = (
                    sma50.dropna().iloc[-1] if len(sma50.dropna()) > 0 else None
                )
            else:
                last_sma50 = float(sma50) if sma50 is not None else None

            if last_sma20 is not None and last_sma50 is not None:
                price_above_sma = last_price > last_sma20 and last_price > last_sma50
                conditions.append(price_above_sma)
                logger.debug(
                    f"SMA: Prix={last_price:.2f} > SMA20={last_sma20:.2f} & SMA50={last_sma50:.2f} => {price_above_sma}"
                )

        # Condition EMA : EMA20 > EMA50 (croisement haussier)
        if has_ema:
            # Convertir en float si c'est une Series
            if isinstance(ema20, pd.Series):
                last_ema20 = (
                    ema20.dropna().iloc[-1] if len(ema20.dropna()) > 0 else None
                )
            else:
                last_ema20 = float(ema20) if ema20 is not None else None

            if isinstance(ema50, pd.Series):
                last_ema50 = (
                    ema50.dropna().iloc[-1] if len(ema50.dropna()) > 0 else None
                )
            else:
                last_ema50 = float(ema50) if ema50 is not None else None

            if last_ema20 is not None and last_ema50 is not None:
                ema_crossover = last_ema20 > last_ema50
                conditions.append(ema_crossover)
                logger.debug(
                    f"EMA: EMA20={last_ema20:.2f} > EMA50={last_ema50:.2f} => {ema_crossover}"
                )

        # Vérifier qu'on a au moins une condition valide
        if not conditions:
            logger.warning("Aucune condition valide pour la détection de tendance")
            return None

        # Tendance haussière si l'une des conditions est vraie
        is_bullish = any(conditions)

        logger.debug(
            f"Tendance: {'Haussière' if is_bullish else 'Baissière'} ({len([c for c in conditions if c])}/{len(conditions)} conditions)"
        )

        return is_bullish

    except Exception as e:
        logger.error(f"Erreur lors de la détection de tendance: {str(e)}")
        return None


# ============================================================================
# MULTI-INDICATEURS (V2.5)
# ============================================================================


def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
    """
    Calcule le MACD (Moving Average Convergence Divergence)

    Le MACD est un indicateur de momentum qui montre la relation entre deux moyennes mobiles.

    Args:
        prices (pd.Series): Série des prix de clôture
        fast_period (int): Période de l'EMA rapide (défaut 12)
        slow_period (int): Période de l'EMA lente (défaut 26)
        signal_period (int): Période de la ligne de signal (défaut 9)

    Returns:
        dict: {
            'macd': pd.Series - Ligne MACD (fast_ema - slow_ema),
            'signal': pd.Series - Ligne de signal (EMA du MACD),
            'histogram': pd.Series - Histogramme (MACD - signal)
        }
        None: En cas d'erreur
    """
    try:
        if prices is None or len(prices) < slow_period:
            logger.warning(
                f"Données insuffisantes pour calculer MACD (besoin de {slow_period} valeurs)"
            )
            return None

        # Calculer les EMA
        fast_ema = prices.ewm(span=fast_period, adjust=False).mean()
        slow_ema = prices.ewm(span=slow_period, adjust=False).mean()

        # Ligne MACD = différence entre les deux EMA
        macd_line = fast_ema - slow_ema

        # Ligne de signal = EMA du MACD
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

        # Histogramme = différence entre MACD et signal
        histogram = macd_line - signal_line

        return {"macd": macd_line, "signal": signal_line, "histogram": histogram}

    except Exception as e:
        logger.error(f"Erreur lors du calcul du MACD: {str(e)}")
        return None


def detect_macd_signal(macd_data):
    """
    Détecte les signaux d'achat/vente basés sur le MACD

    Signaux:
    - Achat (bullish): MACD croise au-dessus de la ligne de signal (histogram > 0)
    - Vente (bearish): MACD croise en-dessous de la ligne de signal (histogram < 0)

    Args:
        macd_data (dict): Résultat de calculate_macd()

    Returns:
        str: 'bullish', 'bearish', 'neutral'
        None: En cas d'erreur
    """
    try:
        if macd_data is None:
            return None

        histogram = macd_data["histogram"]
        if histogram is None or len(histogram) < 2:
            return None

        # Récupérer les 2 dernières valeurs pour détecter le croisement
        hist_current = histogram.iloc[-1]
        hist_previous = histogram.iloc[-2]

        # Croisement haussier : histogram passe de négatif à positif
        if hist_previous < 0 and hist_current > 0:
            return "bullish"

        # Croisement baissier : histogram passe de positif à négatif
        if hist_previous > 0 and hist_current < 0:
            return "bearish"

        # Tendance actuelle basée sur l'histogramme
        if hist_current > 0:
            return "bullish"
        elif hist_current < 0:
            return "bearish"
        else:
            return "neutral"

    except Exception as e:
        logger.error(f"Erreur lors de la détection du signal MACD: {str(e)}")
        return None


def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """
    Calcule les Bandes de Bollinger

    Les Bandes de Bollinger mesurent la volatilité et identifient les conditions
    de surachat/survente.

    Args:
        prices (pd.Series): Série des prix de clôture
        period (int): Période de la moyenne mobile (défaut 20)
        std_dev (float): Nombre d'écarts-types (défaut 2)

    Returns:
        dict: {
            'upper': pd.Series - Bande supérieure,
            'middle': pd.Series - Bande moyenne (SMA),
            'lower': pd.Series - Bande inférieure,
            'bandwidth': pd.Series - Largeur des bandes (mesure de volatilité)
        }
        None: En cas d'erreur
    """
    try:
        if prices is None or len(prices) < period:
            logger.warning(
                f"Données insuffisantes pour calculer Bollinger (besoin de {period} valeurs)"
            )
            return None

        # Bande moyenne = SMA
        middle_band = prices.rolling(window=period).mean()

        # Écart-type
        rolling_std = prices.rolling(window=period).std()

        # Bandes supérieure et inférieure
        upper_band = middle_band + (rolling_std * std_dev)
        lower_band = middle_band - (rolling_std * std_dev)

        # Bandwidth = (upper - lower) / middle (mesure de volatilité)
        bandwidth = (upper_band - lower_band) / middle_band

        return {
            "upper": upper_band,
            "middle": middle_band,
            "lower": lower_band,
            "bandwidth": bandwidth,
        }

    except Exception as e:
        logger.error(f"Erreur lors du calcul des Bollinger Bands: {str(e)}")
        return None


def detect_bollinger_signal(prices, bb_data):
    """
    Détecte les signaux basés sur les Bandes de Bollinger

    Signaux:
    - Survente (bullish): Prix touche ou dépasse la bande inférieure
    - Surachat (bearish): Prix touche ou dépasse la bande supérieure
    - Neutre: Prix dans les bandes

    Args:
        prices (pd.Series): Série des prix
        bb_data (dict): Résultat de calculate_bollinger_bands()

    Returns:
        str: 'oversold' (survente), 'overbought' (surachat), 'neutral'
        None: En cas d'erreur
    """
    try:
        if bb_data is None or prices is None:
            return None

        last_price = prices.iloc[-1]
        upper = bb_data["upper"].iloc[-1]
        lower = bb_data["lower"].iloc[-1]
        middle = bb_data["middle"].iloc[-1]

        # Prix en dessous de la bande inférieure = survente
        if last_price <= lower:
            return "oversold"

        # Prix au-dessus de la bande supérieure = surachat
        if last_price >= upper:
            return "overbought"

        # Prix proche de la bande inférieure (zone de survente)
        if last_price < middle and (last_price - lower) / (middle - lower) < 0.3:
            return "near_oversold"

        # Prix proche de la bande supérieure (zone de surachat)
        if last_price > middle and (upper - last_price) / (upper - middle) < 0.3:
            return "near_overbought"

        return "neutral"

    except Exception as e:
        logger.error(f"Erreur lors de la détection du signal Bollinger: {str(e)}")
        return None


def calculate_stochastic(high, low, close, k_period=14, d_period=3):
    """
    Calcule l'oscillateur Stochastique

    Le Stochastic mesure la position du prix de clôture par rapport à la fourchette
    high-low sur une période donnée. Valeurs entre 0 et 100.

    Args:
        high (pd.Series): Série des prix les plus hauts
        low (pd.Series): Série des prix les plus bas
        close (pd.Series): Série des prix de clôture
        k_period (int): Période pour %K (défaut 14)
        d_period (int): Période pour %D (moyenne de %K, défaut 3)

    Returns:
        dict: {
            'k': pd.Series - Ligne %K (Stochastic rapide),
            'd': pd.Series - Ligne %D (Stochastic lent, moyenne de %K)
        }
        None: En cas d'erreur
    """
    try:
        if close is None or len(close) < k_period:
            logger.warning(
                f"Données insuffisantes pour calculer Stochastic (besoin de {k_period} valeurs)"
            )
            return None

        # Plus bas sur k_period
        lowest_low = low.rolling(window=k_period).min()

        # Plus haut sur k_period
        highest_high = high.rolling(window=k_period).max()

        # %K = ((Close - Lowest Low) / (Highest High - Lowest Low)) * 100
        stoch_k = ((close - lowest_low) / (highest_high - lowest_low)) * 100

        # %D = Moyenne mobile de %K sur d_period
        stoch_d = stoch_k.rolling(window=d_period).mean()

        return {"k": stoch_k, "d": stoch_d}

    except Exception as e:
        logger.error(f"Erreur lors du calcul du Stochastic: {str(e)}")
        return None


def detect_stochastic_signal(stoch_data, oversold_level=20, overbought_level=80):
    """
    Détecte les signaux basés sur le Stochastic

    Signaux:
    - Survente (bullish): %K < oversold_level (défaut 20)
    - Surachat (bearish): %K > overbought_level (défaut 80)
    - Croisement haussier: %K croise au-dessus de %D en zone de survente
    - Croisement baissier: %K croise en-dessous de %D en zone de surachat

    Args:
        stoch_data (dict): Résultat de calculate_stochastic()
        oversold_level (int): Seuil de survente (défaut 20)
        overbought_level (int): Seuil de surachat (défaut 80)

    Returns:
        str: 'oversold', 'overbought', 'bullish_cross', 'bearish_cross', 'neutral'
        None: En cas d'erreur
    """
    try:
        if stoch_data is None:
            return None

        k_line = stoch_data["k"]
        d_line = stoch_data["d"]

        if k_line is None or len(k_line) < 2 or d_line is None:
            return None

        k_current = k_line.iloc[-1]
        k_previous = k_line.iloc[-2]
        d_current = d_line.iloc[-1]
        d_previous = d_line.iloc[-2]

        # Croisement haussier en zone de survente
        if (
            k_previous < d_previous
            and k_current > d_current
            and k_current < oversold_level + 10
        ):
            return "bullish_cross"

        # Croisement baissier en zone de surachat
        if (
            k_previous > d_previous
            and k_current < d_current
            and k_current > overbought_level - 10
        ):
            return "bearish_cross"

        # Survente
        if k_current < oversold_level:
            return "oversold"

        # Surachat
        if k_current > overbought_level:
            return "overbought"

        return "neutral"

    except Exception as e:
        logger.error(f"Erreur lors de la détection du signal Stochastic: {str(e)}")
        return None


# ============================================================================
# CONFLUENCE SCORE (V3)
# ============================================================================


def calculate_confluence_score(
    rsi_value=None,
    trend_score=None,
    max_trend_score=3,
    macd_signal=None,
    bb_position=None,
    stoch_signal=None,
    weights=None,
):
    """
    Calcule un score de confluence global (0-100) basé sur tous les indicateurs

    Le score agrège tous les signaux pour donner une mesure de la force de l'opportunité.
    Plus le score est élevé, plus les indicateurs convergent vers un signal haussier.

    Args:
        rsi_value (float): Valeur du RSI (0-100)
        trend_score (int): Score de tendance (0-max_trend_score)
        max_trend_score (int): Score maximum de tendance (nombre de TF)
        macd_signal (str): Signal MACD ('bullish', 'bearish', 'neutral')
        bb_position (str): Position Bollinger ('oversold', 'overbought', 'neutral', etc.)
        stoch_signal (str): Signal Stochastic ('oversold', 'bullish_cross', etc.)
        weights (dict): Pondérations de chaque indicateur (somme = 100)

    Returns:
        dict: {
            'score': float (0-100),
            'breakdown': dict (score par indicateur),
            'grade': str ('A+', 'A', 'B', 'C', 'D', 'F')
        }
        None: En cas d'erreur

    Algorithme de scoring:
    - RSI (0-20 pts): Plus le RSI est bas, plus le score est élevé
    - Tendance (0-25 pts): Proportionnel au trend_score
    - MACD (0-20 pts): bullish=20, neutral=10, bearish=0
    - Bollinger (0-20 pts): oversold=20, near_oversold=15, neutral=10, near_overbought=5, overbought=0
    - Stochastic (0-15 pts): oversold=15, bullish_cross=12, neutral=7, bearish_cross=3, overbought=0
    """
    try:
        # Pondérations par défaut (total = 100)
        default_weights = {
            "rsi": 20,
            "trend": 25,
            "macd": 20,
            "bollinger": 20,
            "stochastic": 15,
        }

        if weights is None:
            weights = default_weights

        breakdown = {}
        total_score = 0

        # === RSI Score (0-20 pts) ===
        if rsi_value is not None:
            # RSI bas = score élevé (opportunité d'achat)
            if rsi_value <= 20:
                rsi_score = 20
            elif rsi_value <= 30:
                rsi_score = 18
            elif rsi_value <= 40:
                rsi_score = 15
            elif rsi_value <= 50:
                rsi_score = 10
            elif rsi_value <= 60:
                rsi_score = 5
            else:
                rsi_score = 0

            # Appliquer pondération
            rsi_score = (rsi_score / 20) * weights["rsi"]
            breakdown["rsi"] = round(rsi_score, 2)
            total_score += rsi_score

        # === Tendance Score (0-25 pts) ===
        if trend_score is not None and max_trend_score > 0:
            # Proportionnel au nombre de TF haussiers
            trend_ratio = trend_score / max_trend_score
            trend_pts = trend_ratio * 25

            # Appliquer pondération
            trend_pts = (trend_pts / 25) * weights["trend"]
            breakdown["trend"] = round(trend_pts, 2)
            total_score += trend_pts

        # === MACD Score (0-20 pts) ===
        if macd_signal is not None:
            if macd_signal == "bullish":
                macd_score = 20
            elif macd_signal == "neutral":
                macd_score = 10
            elif macd_signal == "bearish":
                macd_score = 0
            else:
                macd_score = 10  # Par défaut

            # Appliquer pondération
            macd_score = (macd_score / 20) * weights["macd"]
            breakdown["macd"] = round(macd_score, 2)
            total_score += macd_score

        # === Bollinger Score (0-20 pts) ===
        if bb_position is not None:
            if bb_position == "oversold":
                bb_score = 20
            elif bb_position == "near_oversold":
                bb_score = 15
            elif bb_position == "neutral":
                bb_score = 10
            elif bb_position == "near_overbought":
                bb_score = 5
            elif bb_position == "overbought":
                bb_score = 0
            else:
                bb_score = 10  # Par défaut

            # Appliquer pondération
            bb_score = (bb_score / 20) * weights["bollinger"]
            breakdown["bollinger"] = round(bb_score, 2)
            total_score += bb_score

        # === Stochastic Score (0-15 pts) ===
        if stoch_signal is not None:
            if stoch_signal == "oversold":
                stoch_score = 15
            elif stoch_signal == "bullish_cross":
                stoch_score = 12
            elif stoch_signal == "neutral":
                stoch_score = 7
            elif stoch_signal == "bearish_cross":
                stoch_score = 3
            elif stoch_signal == "overbought":
                stoch_score = 0
            else:
                stoch_score = 7  # Par défaut

            # Appliquer pondération
            stoch_score = (stoch_score / 15) * weights["stochastic"]
            breakdown["stochastic"] = round(stoch_score, 2)
            total_score += stoch_score

        # Calculer le grade (A+ à F)
        if total_score >= 90:
            grade = "A+"
        elif total_score >= 80:
            grade = "A"
        elif total_score >= 70:
            grade = "B"
        elif total_score >= 60:
            grade = "C"
        elif total_score >= 50:
            grade = "D"
        else:
            grade = "F"

        return {"score": round(total_score, 2), "breakdown": breakdown, "grade": grade}

    except Exception as e:
        logger.error(f"Erreur lors du calcul du score de confluence: {str(e)}")
        return None


def check_signal_filters(
    macd_signal=None,
    bb_position=None,
    stoch_signal=None,
    filter_macd=None,
    filter_bb=None,
    filter_stoch=None,
):
    """
    Vérifie si les signaux passent les filtres configurés

    Args:
        macd_signal (str): Signal MACD actuel
        bb_position (str): Position Bollinger actuelle
        stoch_signal (str): Signal Stochastic actuel
        filter_macd (list): Signaux MACD acceptés (ex: ['bullish'])
        filter_bb (list): Positions BB acceptées (ex: ['oversold', 'near_oversold'])
        filter_stoch (list): Signaux Stoch acceptés (ex: ['oversold', 'bullish_cross'])

    Returns:
        bool: True si tous les filtres actifs sont respectés, False sinon
    """
    try:
        # Filtre MACD
        if filter_macd and macd_signal:
            if macd_signal not in filter_macd:
                return False

        # Filtre Bollinger
        if filter_bb and bb_position:
            if bb_position not in filter_bb:
                return False

        # Filtre Stochastic
        if filter_stoch and stoch_signal:
            if stoch_signal not in filter_stoch:
                return False

        return True

    except Exception as e:
        logger.error(f"Erreur lors de la vérification des filtres: {str(e)}")
        return True  # En cas d'erreur, on ne filtre pas
