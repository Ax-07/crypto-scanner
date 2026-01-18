"""
Script pour afficher le CSV de résultats sous forme de tableau
"""

import pandas as pd
import sys

# Chemin du CSV
csv_path = "outputs/rsi_scan.csv"

try:
    # Lire le CSV
    df = pd.read_csv(csv_path)

    # Afficher les informations générales
    print("\n" + "="*120)
    print(f"📊 RÉSULTATS DU SCAN - {len(df)} paire(s)")
    print("="*120)

    # Colonnes principales à afficher
    main_cols = ['symbol', 'rsi', 'last_close_price', 'last_close_time', 'trend_score']

    # Vérifier quelles colonnes existent
    display_cols = [col for col in main_cols if col in df.columns]

    # Ajouter les tendances si elles existent
    trend_cols = [col for col in df.columns if col.startswith('trend_') and col != 'trend_score']
    display_cols.extend(trend_cols)

    # Créer le DataFrame d'affichage
    display_df = df[display_cols].copy()

    # Formater les colonnes de tendance (True/False → ✓/✗)
    for col in trend_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: '✓' if x else '✗')

    # Afficher le tableau
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 120)
    pd.set_option('display.max_colwidth', 20)

    print(display_df.to_string(index=False))
    print("="*120)

    # Option : afficher toutes les colonnes (détaillé)
    if len(sys.argv) > 1 and sys.argv[1] == '--full':
        print("\n" + "="*120)
        print("📈 TOUTES LES COLONNES (incluant moyennes mobiles)")
        print("="*120)
        print(df.to_string(index=False))
        print("="*120)

    print("\n💡 Utilisez 'python view_csv.py --full' pour voir toutes les colonnes\n")

except FileNotFoundError:
    print(f"❌ Fichier non trouvé : {csv_path}")
    print("Lancez d'abord le scanner avec 'python main.py'")
except Exception as e:
    print(f"❌ Erreur : {e}")
