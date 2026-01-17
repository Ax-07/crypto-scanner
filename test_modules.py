"""
Script de test pour valider les modules individuellement
Usage: python test_modules.py
"""

import sys


def test_config():
    """Test du module config"""
    print("\n" + "="*60)
    print("TEST: config.py")
    print("="*60)
    try:
        import config
        print("✓ Module config importé")
        print(f"  - TIMEFRAME: {config.TIMEFRAME}")
        print(f"  - RSI_PERIOD: {config.RSI_PERIOD}")
        print(f"  - RSI_THRESHOLD: {config.RSI_THRESHOLD}")
        print(f"  - QUOTE_FILTER: {config.QUOTE_FILTER}")
        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False


def test_logger():
    """Test du module logger"""
    print("\n" + "="*60)
    print("TEST: logger.py")
    print("="*60)
    try:
        from logger import setup_logger
        logger = setup_logger()
        print("✓ Logger configuré")
        logger.info("Test log INFO")
        logger.debug("Test log DEBUG")
        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False


def test_exchange():
    """Test du module exchange"""
    print("\n" + "="*60)
    print("TEST: exchange.py")
    print("="*60)
    try:
        import config
        from exchange import init_exchange, load_markets
        print("Initialisation de l'exchange...")
        exchange = init_exchange()
        print(f"✓ Exchange {exchange.id} initialisé")

        print("Chargement des marchés...")
        markets = load_markets(exchange)
        print(f"✓ {len(markets)} marchés chargés")

        # Test de quelques marchés connus avec la quote currency configurée
        test_pairs = [f'BTC/{config.QUOTE_FILTER}', f'ETH/{config.QUOTE_FILTER}', f'BNB/{config.QUOTE_FILTER}']
        for pair in test_pairs:
            if pair in markets:
                print(f"  ✓ {pair} trouvé")
            else:
                print(f"  ⚠ {pair} non trouvé")

        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False


def test_data():
    """Test du module data"""
    print("\n" + "="*60)
    print("TEST: data.py")
    print("="*60)
    try:
        import config
        from exchange import init_exchange, load_markets
        from data import fetch_ohlcv, get_last_closed_candle

        exchange = init_exchange()
        load_markets(exchange)

        symbol = f'BTC/{config.QUOTE_FILTER}'
        print(f"Récupération OHLCV pour {symbol}...")

        df = fetch_ohlcv(exchange, symbol, timeframe='1h', limit=50)

        if df is not None and len(df) > 0:
            print(f"✓ {len(df)} bougies récupérées")
            print(f"  Colonnes: {list(df.columns)}")
            print(f"  Première date: {df['time'].iloc[0]}")
            print(f"  Dernière date: {df['time'].iloc[-1]}")

            last_candle = get_last_closed_candle(df)
            print(f"  Dernier prix: {last_candle['close']}")
            return True
        else:
            print("✗ Aucune donnée récupérée")
            return False

    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False


def test_indicators():
    """Test du module indicators - RSI + Moyennes Mobiles"""
    print("\n" + "="*60)
    print("TEST: indicators.py (RSI + MA)")
    print("="*60)
    try:
        import pandas as pd
        from indicators import calculate_rsi, get_latest_rsi, calculate_sma, calculate_ema, detect_trend

        # ===== TEST RSI =====
        # Créer des données de test
        test_prices = pd.Series([
            100, 102, 101, 103, 105, 104, 106, 108, 107, 109,
            111, 110, 112, 114, 113, 115, 117, 116, 118, 120
        ])

        print("Calcul RSI sur données de test...")
        rsi_series = calculate_rsi(test_prices, period=14)

        if rsi_series is not None:
            last_rsi = get_latest_rsi(test_prices, period=14)
            print("✓ RSI calculé")
            print(f"  Dernière valeur RSI: {last_rsi:.2f}")

            if 0 <= last_rsi <= 100:
                print("  ✓ Valeur cohérente (0-100)")
            else:
                print("  ✗ Valeur hors limites")
                return False
        else:
            print("✗ Échec du calcul RSI")
            return False

        # ===== TEST SMA =====
        print("\nCalcul SMA20 et SMA50 sur données de test...")
        test_prices_ma = pd.Series([100 + i for i in range(60)])  # Prix croissants
        sma20 = calculate_sma(test_prices_ma, period=20)
        sma50 = calculate_sma(test_prices_ma, period=50)

        if sma20 is not None and sma50 is not None:
            print("✓ SMA calculées")
            last_sma20 = sma20.dropna().iloc[-1]
            last_sma50 = sma50.dropna().iloc[-1]
            print(f"  SMA20: {last_sma20:.2f}")
            print(f"  SMA50: {last_sma50:.2f}")

            # Sur données croissantes, SMA20 doit être > SMA50
            if last_sma20 > last_sma50:
                print("  ✓ SMA cohérente (SMA20 > SMA50 sur données croissantes)")
            else:
                print("  ✗ SMA incohérente")
                return False
        else:
            print("✗ Échec du calcul SMA")
            return False

        # ===== TEST EMA =====
        print("\nCalcul EMA20 et EMA50 sur données de test...")
        ema20 = calculate_ema(test_prices_ma, period=20)
        ema50 = calculate_ema(test_prices_ma, period=50)

        if ema20 is not None and ema50 is not None:
            print("✓ EMA calculées")
            last_ema20 = ema20.dropna().iloc[-1]
            last_ema50 = ema50.dropna().iloc[-1]
            print(f"  EMA20: {last_ema20:.2f}")
            print(f"  EMA50: {last_ema50:.2f}")

            # Sur données croissantes, EMA20 doit être > EMA50
            if last_ema20 > last_ema50:
                print("  ✓ EMA cohérente (EMA20 > EMA50 sur données croissantes)")
            else:
                print("  ✗ EMA incohérente")
                return False
        else:
            print("✗ Échec du calcul EMA")
            return False

        # ===== TEST DÉTECTION TENDANCE =====
        print("\nTest de détection de tendance...")
        is_bullish = detect_trend(test_prices_ma, sma20, sma50, ema20, ema50)

        if is_bullish is not None:
            print(f"✓ Tendance détectée: {'Haussière' if is_bullish else 'Baissière'}")

            # Sur données croissantes, doit être haussière
            if is_bullish:
                print("  ✓ Détection cohérente (haussière sur données croissantes)")
                return True
            else:
                print("  ✗ Détection incohérente (devrait être haussière)")
                return False
        else:
            print("✗ Échec de la détection de tendance")
            return False

    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False


def test_full_scan_single_pair():
    """Test complet sur une seule paire"""
    print("\n" + "="*60)
    print("TEST: Scan complet")
    print("="*60)
    try:
        from exchange import init_exchange, load_markets
        from data import fetch_ohlcv
        from indicators import get_latest_rsi
        import config

        exchange = init_exchange()
        load_markets(exchange)

        symbol = f'BTC/{config.QUOTE_FILTER}'
        print(f"Scan de {symbol} (timeframe={config.TIMEFRAME})...")

        # Récupérer OHLCV
        df = fetch_ohlcv(exchange, symbol)
        if df is None or len(df) == 0:
            print("✗ Impossible de récupérer les données")
            return False

        print(f"✓ {len(df)} bougies récupérées")

        # Calculer RSI
        rsi = get_latest_rsi(df['close'], period=config.RSI_PERIOD)
        if rsi is None:
            print("✗ Impossible de calculer le RSI")
            return False

        print(f"✓ RSI calculé: {rsi:.2f}")

        if rsi < config.RSI_THRESHOLD:
            print(f"  🎯 {symbol} est en survente (RSI < {config.RSI_THRESHOLD})")
        else:
            print(f"  ℹ {symbol} n'est pas en survente (RSI >= {config.RSI_THRESHOLD})")

        return True

    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False


def main():
    """Lance tous les tests"""
    print("\n" + "="*60)
    print("TESTS DES MODULES DU SCANNER")
    print("="*60)

    tests = [
        ("Configuration", test_config),
        ("Logger", test_logger),
        ("Exchange", test_exchange),
        ("Data", test_data),
        ("Indicators", test_indicators),
        ("Scan complet", test_full_scan_single_pair),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except KeyboardInterrupt:
            print("\n\n⚠️ Tests interrompus par l'utilisateur")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Erreur lors du test {name}: {e}")
            results[name] = False

    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {name}")

    print("="*60)
    print(f"Résultat: {passed}/{total} tests réussis")
    print("="*60 + "\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
