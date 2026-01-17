"""
Logique principale du scanner RSI + Moyennes Mobiles
Orchestration du scan et filtrage des paires
"""

import config
from logger import get_logger
from exchange import get_filtered_pairs
from data import fetch_ohlcv, get_last_closed_candle
from indicators import get_latest_rsi, calculate_sma, calculate_ema, detect_trend

logger = get_logger()


def analyze_pair_ma(exchange, symbol):
    """
    Analyse les moyennes mobiles d'une paire sur plusieurs timeframes

    Args:
        exchange: Instance CCXT de l'exchange
        symbol (str): Symbole de la paire (ex: "BTC/USDC")

    Returns:
        dict: Résultats de l'analyse MA
        {
            'sma20_1w': float,
            'sma50_1w': float,
            'ema20_1w': float,
            'ema50_1w': float,
            'trend_1w': bool,
            'sma20_1d': float,
            ...
            'trend_score': int (0-3)
        }
        None si erreur
    """
    if not config.ENABLE_MA:
        return None

    results = {}
    trend_score = 0

    try:
        for tf in config.MA_TIMEFRAMES:
            # Récupérer OHLCV pour ce timeframe
            df = fetch_ohlcv(exchange, symbol, timeframe=tf, limit=config.MIN_MA_BARS)

            if df is None or len(df) < max(config.MA_PERIODS):
                logger.debug(f"    ⚠ Données insuffisantes pour {tf}")
                # Stocker None pour ce timeframe
                for period in config.MA_PERIODS:
                    results[f'sma{period}_{tf}'] = None
                    results[f'ema{period}_{tf}'] = None
                results[f'trend_{tf}'] = None
                continue

            # Calculer SMA et EMA pour chaque période
            sma_results = {}
            ema_results = {}

            for period in config.MA_PERIODS:
                sma = calculate_sma(df['close'], period)
                ema = calculate_ema(df['close'], period)

                # Récupérer la dernière valeur
                last_sma = sma.dropna().iloc[-1] if sma is not None and len(sma.dropna()) > 0 else None
                last_ema = ema.dropna().iloc[-1] if ema is not None and len(ema.dropna()) > 0 else None

                results[f'sma{period}_{tf}'] = round(last_sma, 2) if last_sma else None
                results[f'ema{period}_{tf}'] = round(last_ema, 2) if last_ema else None

                sma_results[period] = sma
                ema_results[period] = ema

            # Détecter la tendance pour ce timeframe
            if 20 in sma_results and 50 in sma_results and 20 in ema_results and 50 in ema_results:
                is_bullish = detect_trend(
                    df['close'],
                    sma_results[20],
                    sma_results[50],
                    ema_results[20],
                    ema_results[50]
                )

                results[f'trend_{tf}'] = is_bullish

                # Incrémenter le trend_score si haussier
                if is_bullish:
                    trend_score += 1
            else:
                results[f'trend_{tf}'] = None

        # Ajouter le trend_score global
        results['trend_score'] = trend_score

        return results

    except Exception as e:
        logger.error(f"    ✗ Erreur analyse MA pour {symbol}: {str(e)}")
        return None


def scan_market():
    """
    Scanne le marché et retourne les paires avec RSI < seuil
    Et optionnellement avec tendance haussière multi-timeframe (V1.5)

    Returns:
        list: Liste de dictionnaires contenant les résultats
        [
            {
                'symbol': 'BTC/USDT',
                'rsi': 28.5,
                'last_close_price': 45000.0,
                'last_close_time': datetime(...),
                'timeframe': '4h',
                'sma20_1w': 44000.0,  # V1.5
                'sma50_1w': 43000.0,  # V1.5
                ...
                'trend_score': 2  # V1.5
            },
            ...
        ]
    """
    logger.info("=" * 60)
    logger.info("DÉBUT DU SCAN")
    logger.info("=" * 60)
    logger.info("Paramètres du scan:")
    logger.info(f"  - Exchange: {config.EXCHANGE_ID}")
    logger.info(f"  - Timeframe RSI: {config.TIMEFRAME}")
    logger.info(f"  - RSI période: {config.RSI_PERIOD}")
    logger.info(f"  - RSI seuil: {config.RSI_THRESHOLD}")
    logger.info(f"  - Quote: {config.QUOTE_FILTER}")
    logger.info(f"  - Max paires: {config.MAX_PAIRS if config.MAX_PAIRS else 'Toutes'}")

    if config.ENABLE_MA:
        logger.info("  - Analyse MA activée:")
        logger.info(f"    • Timeframes: {', '.join(config.MA_TIMEFRAMES)}")
        logger.info(f"    • Périodes: {config.MA_PERIODS}")
        logger.info(f"    • Min trend score: {config.MIN_TREND_SCORE}")

    logger.info("=" * 60)

    # 1. Initialiser l'exchange et obtenir les paires filtrées
    try:
        exchange, symbols = get_filtered_pairs()
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de l'exchange: {str(e)}")
        return []

    if not symbols:
        logger.warning("Aucune paire trouvée correspondant au scope")
        return []

    logger.info(f"Scan de {len(symbols)} paires...")
    logger.info("-" * 60)

    # 2. Parcourir chaque paire et calculer le RSI + MA
    results = []
    success_count = 0
    error_count = 0

    for idx, symbol in enumerate(symbols, 1):
        try:
            logger.debug(f"[{idx}/{len(symbols)}] Traitement de {symbol}...")

            # ===== A. CALCUL RSI =====
            # Récupérer les données OHLCV pour le RSI
            df_rsi = fetch_ohlcv(exchange, symbol, timeframe=config.TIMEFRAME)

            if df_rsi is None or len(df_rsi) == 0:
                logger.debug(f"  ⚠ Données insuffisantes pour {symbol}")
                error_count += 1
                continue

            # Calculer le RSI
            rsi = get_latest_rsi(df_rsi['close'], period=config.RSI_PERIOD)

            if rsi is None:
                logger.debug(f"  ⚠ Impossible de calculer RSI pour {symbol}")
                error_count += 1
                continue

            logger.debug(f"  ✓ {symbol}: RSI = {rsi:.2f}")

            # Filtrer si RSI < seuil
            if rsi >= config.RSI_THRESHOLD:
                success_count += 1
                continue

            # ===== B. CALCUL MOYENNES MOBILES (V1.5) =====
            ma_data = None
            if config.ENABLE_MA:
                logger.debug("    Analyse MA multi-timeframe...")
                ma_data = analyze_pair_ma(exchange, symbol)

            # ===== C. FILTRE COMBINÉ RSI + TENDANCE =====
            # Si MA activée, vérifier le trend_score
            if config.ENABLE_MA and ma_data:
                trend_score = ma_data.get('trend_score', 0)

                if trend_score < config.MIN_TREND_SCORE:
                    logger.debug(f"    ⚠ Trend score insuffisant: {trend_score}/{len(config.MA_TIMEFRAMES)}")
                    success_count += 1
                    continue

            # ===== D. CONSTRUIRE LE RÉSULTAT =====
            last_candle = get_last_closed_candle(df_rsi)

            result = {
                'symbol': symbol,
                'rsi': round(rsi, 2),
                'last_close_price': last_candle['close'],
                'last_close_time': last_candle['time'],
                'timeframe': config.TIMEFRAME
            }

            # Ajouter les données MA si disponibles
            if ma_data:
                result.update(ma_data)

            results.append(result)

            # Log détaillé
            if config.ENABLE_MA and ma_data:
                trend_score = ma_data.get('trend_score', 0)
                logger.info(f"  🎯 {symbol}: RSI={rsi:.2f} | Trend={trend_score}/{len(config.MA_TIMEFRAMES)}")
            else:
                logger.info(f"  🎯 {symbol}: RSI={rsi:.2f}")

            success_count += 1

        except KeyboardInterrupt:
            logger.warning("Interruption utilisateur (Ctrl+C)")
            logger.info(f"Scan arrêté après {idx}/{len(symbols)} paires")
            break

        except Exception as e:
            logger.error(f"  ✗ Erreur inattendue pour {symbol}: {str(e)}")
            error_count += 1
            continue

    # 3. Trier les résultats par RSI ascendant
    results.sort(key=lambda x: x['rsi'])

    # 4. Logs de fin
    logger.info("-" * 60)
    logger.info("FIN DU SCAN")
    logger.info(f"Paires scannées avec succès: {success_count}/{len(symbols)}")
    logger.info(f"Erreurs: {error_count}")

    if config.ENABLE_MA:
        logger.info(f"Opportunités (RSI < {config.RSI_THRESHOLD} + Trend ≥ {config.MIN_TREND_SCORE}): {len(results)}")
    else:
        logger.info(f"Paires avec RSI < {config.RSI_THRESHOLD}: {len(results)}")

    logger.info("=" * 60)

    return results
