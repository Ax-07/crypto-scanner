"""
Point d'entrée de l'application desktop PyQt6
Lance l'interface graphique du scanner crypto

Usage:
    python gui_main.py

⚠️ MODE SCANNER UNIQUEMENT - AUCUN TRADING
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from gui.main_window import MainWindow


def main():
    """Point d'entrée principal de l'application GUI"""

    # Activer High DPI scaling AVANT de créer QApplication
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Créer l'application Qt
    app = QApplication(sys.argv)

    # Configurer l'application
    app.setApplicationName("Crypto Scanner")
    app.setOrganizationName("Crypto Scanner Project")

    # Créer et afficher la fenêtre principale
    window = MainWindow()
    window.show()

    # Lancer la boucle d'événements
    sys.exit(app.exec())


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Lancement de Crypto Scanner GUI")
    print("=" * 60)
    print("⚠️  MODE SCANNER UNIQUEMENT - AUCUN TRADING")
    print("📊 Analyse de marché Binance avec multi-indicateurs")
    print("=" * 60)
    print()

    main()
