"""
Formatage et export des résultats du scan
Console et CSV
"""

import os
import pandas as pd
from datetime import datetime
import config
from logger import get_logger

logger = get_logger()


def display_results_console(results):
    """
    Affiche les résultats dans la console sous forme de tableau
    Inclut les colonnes MA et trend_score si disponibles (V1.5)

    Args:
        results (list): Liste des résultats du scan
    """
    if not config.CONSOLE_OUTPUT:
        return

    print("\n" + "=" * 120)
    print(f"RÉSULTATS DU SCAN - RSI < {config.RSI_THRESHOLD}")
    if config.ENABLE_MA:
        print(f"TENDANCE HAUSSIÈRE ≥ {config.MIN_TREND_SCORE}/{len(config.MA_TIMEFRAMES)} timeframes")
    print("=" * 120)

    if not results:
        print("Aucune paire trouvée correspondant aux critères")
        print("=" * 120 + "\n")
        return

    # Créer un DataFrame pour un affichage propre
    df = pd.DataFrame(results)

    # Formater les colonnes de base
    df['rsi'] = df['rsi'].apply(lambda x: f"{x:.2f}")
    df['last_close_price'] = df['last_close_price'].apply(lambda x: f"{x:.8f}")
    df['last_close_time'] = df['last_close_time'].dt.strftime('%Y-%m-%d %H:%M')

    # Colonnes de base à afficher
    columns_to_display = ['symbol', 'rsi', 'last_close_price', 'last_close_time', 'timeframe']

    # Si MA activée, ajouter les colonnes de tendance
    if config.ENABLE_MA and 'trend_score' in df.columns:
        # Ajouter trend_score
        columns_to_display.append('trend_score')

        # Ajouter les flags de tendance pour chaque timeframe
        for tf in config.MA_TIMEFRAMES:
            col_name = f'trend_{tf}'
            if col_name in df.columns:
                # Convertir bool en symbole ✓/✗
                df[col_name] = df[col_name].apply(lambda x: '✓' if x is True else ('✗' if x is False else '-'))
                columns_to_display.append(col_name)

    # Créer le DataFrame d'affichage
    display_df = df[columns_to_display].copy()

    # Renommer les colonnes pour l'affichage
    rename_map = {
        'symbol': 'Symbole',
        'rsi': 'RSI',
        'last_close_price': 'Prix',
        'last_close_time': 'Date',
        'timeframe': 'TF',
        'trend_score': 'Trend'
    }

    # Ajouter les renommages pour les tendances
    if config.ENABLE_MA:
        for tf in config.MA_TIMEFRAMES:
            rename_map[f'trend_{tf}'] = tf.upper()

    display_df.rename(columns=rename_map, inplace=True)

    # Afficher le tableau
    print(display_df.to_string(index=False))
    print("=" * 120)
    print(f"Total: {len(results)} paire(s)")
    print("=" * 120 + "\n")


def export_to_csv(results):
    """
    Export les résultats dans un fichier CSV
    Inclut toutes les colonnes MA si disponibles (V1.5)

    Args:
        results (list): Liste des résultats du scan
    """
    if not config.OUTPUT_CSV:
        return

    if not results:
        logger.info("Aucun résultat à exporter")
        return

    try:
        # Créer le dossier de sortie s'il n'existe pas
        output_dir = os.path.dirname(config.CSV_PATH)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Créer le DataFrame
        df = pd.DataFrame(results)

        # Ajouter des métadonnées
        df['scan_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df['rsi_period'] = config.RSI_PERIOD
        df['rsi_threshold'] = config.RSI_THRESHOLD

        # Formater la colonne datetime
        df['last_close_time'] = df['last_close_time'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Réorganiser les colonnes
        columns_order = [
            'symbol',
            'rsi',
            'last_close_price',
            'last_close_time',
            'timeframe',
        ]

        # Ajouter les colonnes MA si disponibles (V1.5)
        if config.ENABLE_MA and 'trend_score' in df.columns:
            # Ajouter trend_score
            columns_order.append('trend_score')

            # Ajouter toutes les colonnes MA pour chaque timeframe
            for tf in config.MA_TIMEFRAMES:
                for period in config.MA_PERIODS:
                    col_sma = f'sma{period}_{tf}'
                    col_ema = f'ema{period}_{tf}'
                    if col_sma in df.columns:
                        columns_order.append(col_sma)
                    if col_ema in df.columns:
                        columns_order.append(col_ema)

                # Ajouter le flag de tendance
                col_trend = f'trend_{tf}'
                if col_trend in df.columns:
                    columns_order.append(col_trend)

        # Ajouter les métadonnées à la fin
        columns_order.extend(['rsi_period', 'rsi_threshold', 'scan_date'])

        # Filtrer les colonnes qui existent réellement
        columns_order = [col for col in columns_order if col in df.columns]

        df = df[columns_order]

        # Export CSV
        df.to_csv(config.CSV_PATH, index=False, encoding='utf-8')

        logger.info(f"✓ Résultats exportés vers: {config.CSV_PATH}")
        print(f"\n📁 Fichier CSV créé: {config.CSV_PATH}\n")

    except Exception as e:
        logger.error(f"Erreur lors de l'export CSV: {str(e)}")


def output_results(results):
    """
    Fonction principale d'output : affichage console + export CSV

    Args:
        results (list): Liste des résultats du scan
    """
    display_results_console(results)
    export_to_csv(results)
