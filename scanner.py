"""
Logique principale du scanner RSI + Moyennes Mobiles
Orchestration du scan et filtrage des paires
V2 : Concurrency avec ThreadPoolExecutor
"""

import config
from logger import get_logger
from exchange import get_filtered_pairs
from data import fetch_ohlcv, get_last_closed_candle
from indicators import get_latest_rsi, calculate_sma, calculate_ema, detect_trend
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

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
    if not config.USE_MA:
        return None

    results = {}
    trend_score = 0

    try:
        for tf in config.MA_TIMEFRAMES:
            # Récupérer OHLCV pour ce timeframe
            # Calculer la limite nécessaire (max des périodes SMA et EMA)
            all_periods = []
            if config.USE_SMA:
                all_periods.extend(config.SMA_PERIODS)
            if config.USE_EMA:
                all_periods.extend(config.EMA_PERIODS)

            if not all_periods:
                logger.warning(f"    ⚠ Aucune période MA configurée pour {symbol}")
                continue

            max_period = max(all_periods)
            limit = max(config.MIN_MA_BARS, max_period + 10)  # +10 pour marge

            df = fetch_ohlcv(exchange, symbol, timeframe=tf, limit=limit)

            if df is None or len(df) < max_period:
                logger.debug(f"    ⚠ Données insuffisantes pour MA sur {tf}")
                continue

            # Calculer les moyennes mobiles configurées
            sma_results = {}
            ema_results = {}

            if config.USE_SMA:
                for period in config.SMA_PERIODS:
                    sma = calculate_sma(df['close'], period)
                    if sma is not None:
                        sma_value = float(sma.iloc[-1])
                        results[f'sma{period}_{tf}'] = round(sma_value, 8)
                        sma_results[period] = sma_value

            if config.USE_EMA:
                for period in config.EMA_PERIODS:
                    ema = calculate_ema(df['close'], period)
                    if ema is not None:
                        ema_value = float(ema.iloc[-1])
                        results[f'ema{period}_{tf}'] = round(ema_value, 8)
                        ema_results[period] = ema_value

            # Détecter la tendance si on a les MA nécessaires (20 et 50)
            has_sma_20_50 = 20 in sma_results and 50 in sma_results
            has_ema_20_50 = 20 in ema_results and 50 in ema_results

            if has_sma_20_50 or has_ema_20_50:
                sma20 = sma_results.get(20) if has_sma_20_50 else None
                sma50 = sma_results.get(50) if has_sma_20_50 else None
                ema20 = ema_results.get(20) if has_ema_20_50 else None
                ema50 = ema_results.get(50) if has_ema_20_50 else None

                is_bullish = detect_trend(
                    df['close'],
                    sma20,
                    sma50,
                    ema20,
                    ema50
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


def analyze_single_pair(exchange, symbol, idx, total):
    """
    Analyse une seule paire (isolée pour parallélisation)
    Thread-safe, gère ses propres erreurs

    Args:
        exchange: Instance CCXT
        symbol (str): Symbole à analyser
        idx (int): Index de la paire (pour logs)
        total (int): Nombre total de paires

    Returns:
        tuple: (status, result)
        status: 'success', 'filtered', 'error'
        result: dict ou None
    """
    try:
        logger.debug(f"[{idx}/{total}] Traitement de {symbol}...")

        # ===== A. CALCUL RSI (si activé) =====
        rsi = None
        df_rsi = None
        last_candle = None

        if config.USE_RSI:
            # Récupérer les données OHLCV pour le RSI
            df_rsi = fetch_ohlcv(exchange, symbol, timeframe=config.TIMEFRAME)

            if df_rsi is None or len(df_rsi) == 0:
                logger.debug(f"  ⚠ Données insuffisantes pour {symbol}")
                return ('error', None)

            # Calculer le RSI
            rsi = get_latest_rsi(df_rsi['close'], period=config.RSI_PERIOD)

            if rsi is None:
                logger.debug(f"  ⚠ Impossible de calculer RSI pour {symbol}")
                return ('error', None)

            logger.debug(f"  ✓ {symbol}: RSI = {rsi:.2f}")

            # Filtrer si RSI < seuil
            if rsi >= config.RSI_THRESHOLD:
                return ('filtered', None)

            last_candle = get_last_closed_candle(df_rsi)
        else:
            # Si RSI non activé, récupérer quand même les données de base pour le prix
            df_rsi = fetch_ohlcv(exchange, symbol, timeframe=config.TIMEFRAME, limit=1)
            if df_rsi is not None and len(df_rsi) > 0:
                last_candle = get_last_closed_candle(df_rsi)

        # ===== B. CALCUL MOYENNES MOBILES (V1.5) =====
        ma_data = None
        if config.USE_MA:
            logger.debug("    Analyse MA multi-timeframe...")
            ma_data = analyze_pair_ma(exchange, symbol)

        # ===== C. FILTRE COMBINÉ =====
        # Si MA activée, vérifier le trend_score
        if config.USE_MA and ma_data:
            trend_score = ma_data.get('trend_score', 0)

            if trend_score < config.MIN_TREND_SCORE:
                logger.debug(f"    ⚠ Trend score insuffisant: {trend_score}/{len(config.MA_TIMEFRAMES)}")
                return ('filtered', None)

        # ===== D. CONSTRUIRE LE RÉSULTAT =====
        result = {
            'symbol': symbol,
            'timeframe': config.TIMEFRAME
        }

        # Ajouter RSI si calculé
        if rsi is not None:
            result['rsi'] = round(rsi, 2)

        # Ajouter prix et date si disponibles
        if last_candle:
            result['last_close_price'] = last_candle['close']
            result['last_close_time'] = last_candle['time']

        # Ajouter les données MA si disponibles
        if ma_data:
            result.update(ma_data)

        # Log détaillé
        log_parts = [symbol]
        if rsi is not None:
            log_parts.append(f"RSI={rsi:.2f}")
        if config.USE_MA and ma_data:
            trend_score = ma_data.get('trend_score', 0)
            log_parts.append(f"Trend={trend_score}/{len(config.MA_TIMEFRAMES)}")

        logger.info(f"  🎯 {' | '.join(log_parts)}")

        return ('success', result)

    except Exception as e:
        logger.error(f"  ✗ Erreur inattendue pour {symbol}: {str(e)}")
        return ('error', None)


def scan_market():
    """
    Scanne le marché et retourne les paires avec RSI < seuil
    Et optionnellement avec tendance haussière multi-timeframe (V1.5)
    Utilise ThreadPoolExecutor pour parallélisation (V2)

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
    start_time = time.time()

    logger.info("=" * 60)
    logger.info("DÉBUT DU SCAN")
    logger.info("=" * 60)
    logger.info("Paramètres du scan:")
    logger.info(f"  - Exchange: {config.EXCHANGE_ID}")
    logger.info(f"  - Quote: {config.QUOTE_FILTER}")
    logger.info(f"  - Max paires: {config.MAX_PAIRS if config.MAX_PAIRS else 'Toutes'}")
    logger.info(f"  - Concurrency: {'✓ Activée' if config.ENABLE_CONCURRENCY else '✗ Désactivée'}")
    if config.ENABLE_CONCURRENCY:
        logger.info(f"    Workers: {config.MAX_WORKERS}")
    logger.info("  - Indicateurs activés:")

    if config.USE_RSI:
        logger.info(f"    • RSI: seuil < {config.RSI_THRESHOLD} (période {config.RSI_PERIOD}, TF {config.TIMEFRAME})")

    if config.USE_MA:
        ma_types = []
        if config.USE_SMA:
            ma_types.append(f"SMA{config.SMA_PERIODS}")
        if config.USE_EMA:
            ma_types.append(f"EMA{config.EMA_PERIODS}")

        logger.info(f"    • Moyennes Mobiles: {' + '.join(ma_types)}")
        logger.info(f"      - Timeframes: {', '.join(config.MA_TIMEFRAMES)}")
        logger.info(f"      - Min trend score: {config.MIN_TREND_SCORE}")

    if not config.USE_RSI and not config.USE_MA:
        logger.warning("  ⚠ AUCUN INDICATEUR ACTIVÉ - Le scan listera toutes les paires")

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

    # 2. Scanner les paires (séquentiel ou parallèle)
    results = []
    success_count = 0
    filtered_count = 0
    error_count = 0

    try:
        if config.ENABLE_CONCURRENCY:
            # === MODE PARALLÈLE (ThreadPoolExecutor) ===
            logger.info(f"🚀 Mode parallèle activé ({config.MAX_WORKERS} workers)")

            with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
                # Soumettre toutes les tâches
                future_to_symbol = {
                    executor.submit(analyze_single_pair, exchange, symbol, idx, len(symbols)): symbol
                    for idx, symbol in enumerate(symbols, 1)
                }

                # Traiter les résultats au fur et à mesure
                for future in as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    try:
                        status, result = future.result()

                        if status == 'success':
                            results.append(result)
                            success_count += 1
                        elif status == 'filtered':
                            filtered_count += 1
                        else:  # error
                            error_count += 1

                    except Exception as e:
                        logger.error(f"  ✗ Exception future pour {symbol}: {str(e)}")
                        error_count += 1
        else:
            # === MODE SÉQUENTIEL (boucle classique) ===
            logger.info("🐢 Mode séquentiel (ENABLE_CONCURRENCY=False)")

            for idx, symbol in enumerate(symbols, 1):
                try:
                    status, result = analyze_single_pair(exchange, symbol, idx, len(symbols))

                    if status == 'success':
                        results.append(result)
                        success_count += 1
                    elif status == 'filtered':
                        filtered_count += 1
                    else:  # error
                        error_count += 1

                except KeyboardInterrupt:
                    logger.warning("Interruption utilisateur (Ctrl+C)")
                    logger.info(f"Scan arrêté après {idx}/{len(symbols)} paires")
                    break

    except KeyboardInterrupt:
        logger.warning("Interruption utilisateur (Ctrl+C)")

    # 3. Trier les résultats
    # Si RSI activé, trier par RSI ascendant
    # Sinon si MA activée, trier par trend_score descendant
    # Sinon par symbole
    if config.USE_RSI and results and 'rsi' in results[0]:
        results.sort(key=lambda x: x.get('rsi', 999))
    elif config.USE_MA and results and 'trend_score' in results[0]:
        results.sort(key=lambda x: x.get('trend_score', 0), reverse=True)
    else:
        results.sort(key=lambda x: x.get('symbol', ''))

    # 4. Logs de fin
    elapsed_time = time.time() - start_time

    logger.info("-" * 60)
    logger.info("FIN DU SCAN")
    logger.info(f"Durée totale: {elapsed_time:.2f}s")
    logger.info(f"Paires traitées: {success_count + filtered_count + error_count}/{len(symbols)}")
    logger.info(f"  - Succès: {success_count}")
    logger.info(f"  - Filtrées: {filtered_count}")
    logger.info(f"  - Erreurs: {error_count}")

    # Message selon les filtres actifs
    filter_parts = []
    if config.USE_RSI:
        filter_parts.append(f"RSI < {config.RSI_THRESHOLD}")
    if config.USE_MA:
        filter_parts.append(f"Trend ≥ {config.MIN_TREND_SCORE}")

    if filter_parts:
        logger.info(f"Opportunités ({' + '.join(filter_parts)}): {len(results)}")
    else:
        logger.info(f"Paires listées: {len(results)}")

    if len(symbols) > 0:
        rate = len(symbols) / elapsed_time
        logger.info(f"Vitesse: {rate:.2f} paires/seconde")

    logger.info("=" * 60)

    return results
