"""
Formatage et export des résultats du scan
Console et CSV
V2.5 : Support multi-indicateurs (MACD, Bollinger, Stochastic)
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

    # Construire le titre selon les indicateurs actifs
    title_parts = []
    if config.USE_RSI:
        title_parts.append(f"RSI < {config.RSI_THRESHOLD}")
    if config.USE_MA:
        title_parts.append(f"TENDANCE ≥ {config.MIN_TREND_SCORE}/{len(config.MA_TIMEFRAMES)} TF")

    if title_parts:
        print(f"RÉSULTATS DU SCAN - {' + '.join(title_parts)}")
    else:
        print("RÉSULTATS DU SCAN - TOUTES LES PAIRES")

    print("=" * 120)

    if not results:
        print("Aucune paire trouvée correspondant aux critères")
        print("=" * 120 + "\n")
        return

    # Créer un DataFrame pour un affichage propre
    df = pd.DataFrame(results)

    # Formater les colonnes de base
    if 'rsi' in df.columns:
        df['rsi'] = df['rsi'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else '-')

    if 'last_close_price' in df.columns:
        df['last_close_price'] = df['last_close_price'].apply(lambda x: f"{x:.8f}" if pd.notna(x) else '-')

    if 'last_close_time' in df.columns:
        df['last_close_time'] = df['last_close_time'].apply(
            lambda x: x.strftime('%Y-%m-%d %H:%M') if pd.notna(x) else '-'
        )

    # Colonnes de base à afficher
    columns_to_display = ['symbol']

    if 'rsi' in df.columns and config.USE_RSI:
        columns_to_display.append('rsi')

    if 'last_close_price' in df.columns:
        columns_to_display.append('last_close_price')

    if 'last_close_time' in df.columns:
        columns_to_display.append('last_close_time')

    columns_to_display.append('timeframe')

    # Si MA activée, ajouter les colonnes de tendance
    if config.USE_MA and 'trend_score' in df.columns:
        # Ajouter trend_score
        columns_to_display.append('trend_score')

        # Ajouter les flags de tendance pour chaque timeframe
        for tf in config.MA_TIMEFRAMES:
            col_name = f'trend_{tf}'
            if col_name in df.columns:
                # Convertir bool en symbole ✓/✗
                df[col_name] = df[col_name].apply(lambda x: '✓' if x is True else ('✗' if x is False else '-'))
                columns_to_display.append(col_name)

    # V2.5 : Ajouter les colonnes multi-indicateurs
    if config.USE_MACD and 'macd_signal_type' in df.columns:
        columns_to_display.append('macd_signal_type')

    if config.USE_BOLLINGER and 'bb_position' in df.columns:
        columns_to_display.append('bb_position')

    if config.USE_STOCHASTIC and 'stoch_signal' in df.columns:
        columns_to_display.append('stoch_signal')

    # V3 : Ajouter le score de confluence
    if config.USE_CONFLUENCE_SCORE and 'confluence_score' in df.columns:
        # Formater le score avec le grade
        if 'confluence_grade' in df.columns:
            df['confluence_display'] = df.apply(
                lambda row: f"{row['confluence_score']:.1f} ({row['confluence_grade']})"
                if pd.notna(row['confluence_score']) else '-',
                axis=1
            )
            columns_to_display.append('confluence_display')
        else:
            df['confluence_score'] = df['confluence_score'].apply(
                lambda x: f"{x:.1f}" if pd.notna(x) else '-'
            )
            columns_to_display.append('confluence_score')

    # Créer le DataFrame d'affichage
    display_df = df[columns_to_display].copy()

    # Renommer les colonnes pour l'affichage
    rename_map = {
        'symbol': 'Symbole',
        'rsi': 'RSI',
        'last_close_price': 'Prix',
        'last_close_time': 'Date',
        'timeframe': 'TF',
        'trend_score': 'Trend',
        'confluence_display': 'Score',
        'confluence_score': 'Score',
        'macd_signal_type': 'MACD',
        'bb_position': 'Bollinger',
        'stoch_signal': 'Stochastic'
    }

    # Ajouter les renommages pour les tendances
    if config.USE_MA:
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

        if config.USE_RSI:
            df['rsi_period'] = config.RSI_PERIOD
            df['rsi_threshold'] = config.RSI_THRESHOLD

        # Formater la colonne datetime si elle existe
        if 'last_close_time' in df.columns:
            df['last_close_time'] = df['last_close_time'].apply(
                lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) else '-'
            )

        # Réorganiser les colonnes
        columns_order = ['symbol']

        # Ajouter RSI si activé
        if 'rsi' in df.columns and config.USE_RSI:
            columns_order.append('rsi')

        if 'last_close_price' in df.columns:
            columns_order.append('last_close_price')

        if 'last_close_time' in df.columns:
            columns_order.append('last_close_time')

        columns_order.append('timeframe')

        # Ajouter les colonnes MA si disponibles (V1.5)
        if config.USE_MA and 'trend_score' in df.columns:
            # Ajouter trend_score
            columns_order.append('trend_score')

            # Ajouter toutes les colonnes MA pour chaque timeframe
            for tf in config.MA_TIMEFRAMES:
                # Ajouter SMA si activées
                if config.USE_SMA:
                    for period in config.SMA_PERIODS:
                        col_sma = f'sma{period}_{tf}'
                        if col_sma in df.columns:
                            columns_order.append(col_sma)

                # Ajouter EMA si activées
                if config.USE_EMA:
                    for period in config.EMA_PERIODS:
                        col_ema = f'ema{period}_{tf}'
                        if col_ema in df.columns:
                            columns_order.append(col_ema)

                # Ajouter le flag de tendance
                col_trend = f'trend_{tf}'
                if col_trend in df.columns:
                    columns_order.append(col_trend)

        # V2.5 : Ajouter les colonnes multi-indicateurs
        if config.USE_MACD:
            for col in ['macd', 'macd_signal', 'macd_histogram', 'macd_signal_type']:
                if col in df.columns:
                    columns_order.append(col)

        if config.USE_BOLLINGER:
            for col in ['bb_upper', 'bb_middle', 'bb_lower', 'bb_position']:
                if col in df.columns:
                    columns_order.append(col)

        if config.USE_STOCHASTIC:
            for col in ['stoch_k', 'stoch_d', 'stoch_signal']:
                if col in df.columns:
                    columns_order.append(col)

        # V3 : Ajouter les colonnes de confluence
        if config.USE_CONFLUENCE_SCORE:
            for col in ['confluence_score', 'confluence_grade']:
                if col in df.columns:
                    columns_order.append(col)
            # Ajouter le breakdown si disponible (décomposé en colonnes séparées)
            if 'confluence_breakdown' in df.columns:
                # Extraire les sous-scores du breakdown
                try:
                    breakdown_df = pd.json_normalize(df['confluence_breakdown'])
                    for col in breakdown_df.columns:
                        df[f'score_{col}'] = breakdown_df[col]
                        columns_order.append(f'score_{col}')
                except (ValueError, TypeError, KeyError, AttributeError):
                    pass  # Ignorer si le breakdown n'est pas au bon format

        # Ajouter les métadonnées à la fin
        metadata_cols = []
        if 'rsi_period' in df.columns:
            metadata_cols.append('rsi_period')
        if 'rsi_threshold' in df.columns:
            metadata_cols.append('rsi_threshold')
        metadata_cols.append('scan_date')

        columns_order.extend([col for col in metadata_cols if col in df.columns])

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
