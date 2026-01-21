"""
Script de diagnostic pour vérifier le scan RSI
Affiche les détails du calcul RSI sur quelques paires test
"""

import ccxt
import pandas as pd
import sys
from indicators import calculate_rsi
from config import TIMEFRAME, RSI_PERIOD, RSI_THRESHOLD, QUOTE_FILTER


def debug_rsi():
    """Teste le calcul RSI sur quelques paires connues"""

    print("=" * 60)
    print("🔍 DIAGNOSTIC RSI SCAN")
    print("=" * 60)
    print(f"Timeframe: {TIMEFRAME}")
    print(f"RSI Period: {RSI_PERIOD}")
    print(f"RSI Threshold: {RSI_THRESHOLD}")
    print(f"Quote Filter: {QUOTE_FILTER}")
    print("=" * 60)
    print()

    # Init exchange
    exchange = ccxt.binance(
        {"enableRateLimit": True, "options": {"defaultType": "spot"}}
    )

    # Paires de test
    test_pairs = [
        f"BTC/{QUOTE_FILTER}",
        f"ETH/{QUOTE_FILTER}",
        f"BNB/{QUOTE_FILTER}",
        f"SOL/{QUOTE_FILTER}",
        f"ADA/{QUOTE_FILTER}",
    ]

    results = []

    for symbol in test_pairs:
        try:
            print(f"📊 Test de {symbol}...")

            # Fetch OHLCV
            ohlcv = exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=TIMEFRAME,
                limit=RSI_PERIOD + 50,  # Suffisant pour RSI
            )

            if len(ohlcv) < RSI_PERIOD:
                print(f"  ❌ Pas assez de données ({len(ohlcv)} bars)")
                continue

            # Convertir en DataFrame
            df = pd.DataFrame(
                ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

            # Calculer RSI
            rsi_series = calculate_rsi(df["close"], RSI_PERIOD)

            if rsi_series.empty or rsi_series.isna().all():
                print("  ❌ RSI non calculable")
                continue

            # Dernière valeur RSI
            last_rsi = rsi_series.iloc[-1]
            last_price = df["close"].iloc[-1]
            last_time = df["timestamp"].iloc[-1]

            # Afficher
            status = "✅ MATCH" if last_rsi < RSI_THRESHOLD else "❌ NO MATCH"
            print(f"  {status} RSI: {last_rsi:.2f} | Prix: ${last_price:.6f}")
            print(f"  Temps: {last_time}")

            results.append(
                {
                    "symbol": symbol,
                    "rsi": last_rsi,
                    "price": last_price,
                    "match": last_rsi < RSI_THRESHOLD,
                }
            )

            print()

        except Exception as e:
            print(f"  ❌ ERREUR: {e}")
            print()

    # Résumé
    print("=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)

    if not results:
        print("❌ AUCUNE PAIRE TESTÉE AVEC SUCCÈS")
        return

    # Afficher tous les RSI
    print("\n📈 Valeurs RSI trouvées:")
    for r in sorted(results, key=lambda x: x["rsi"]):
        match_icon = "✅" if r["match"] else "❌"
        print(f"  {match_icon} {r['symbol']}: RSI {r['rsi']:.2f}")

    matches = [r for r in results if r["match"]]
    print(f"\n🎯 Résultats: {len(matches)}/{len(results)} paires < {RSI_THRESHOLD}")

    if len(matches) == 0:
        print(f"\n⚠️  AUCUNE PAIRE SOUS LE SEUIL RSI {RSI_THRESHOLD}")
        print("💡 Solutions possibles:")
        print("   1. Augmenter RSI_THRESHOLD à 35 ou 40")
        print("   2. Vérifier que le marché est en zone de survente")
        print("   3. Scanner plus de paires (élargir le scope)")

    print("=" * 60)


if __name__ == "__main__":
    try:
        debug_rsi()
    except Exception as e:
        print(f"\n❌ ERREUR FATALE: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
