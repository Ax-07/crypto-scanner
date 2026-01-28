"""
Fenêtre principale de l'application PyQt6
Gère les onglets, le menu, et l'orchestration globale
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QStatusBar,
    QMessageBox,
)
from PyQt6.QtGui import QAction

from gui.config_tab import ConfigTab
from gui.scanner_tab import ScannerTab
from gui.results_tab import ResultsTab
from gui.details_tab import DetailsTab
from gui.styles import get_dark_theme


class MainWindow(QMainWindow):
    """
    Fenêtre principale de l'application Crypto Scanner
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crypto Scanner - Binance RSI & Multi-Indicateurs")
        self.setGeometry(100, 100, 1400, 900)
        
        # Stocker l'exchange pour le passer aux détails
        self.exchange_instance = None

        # Appliquer le thème sombre
        self.setStyleSheet(get_dark_theme())

        # Créer l'interface
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface complète"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # === TabWidget (Onglets) ===
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)

        # Créer les onglets
        self.config_tab = ConfigTab()
        self.scanner_tab = ScannerTab()
        self.results_tab = ResultsTab()
        self.details_tab = DetailsTab()

        # Ajouter les onglets
        self.tabs.addTab(self.config_tab, "⚙️  Configuration")
        self.tabs.addTab(self.scanner_tab, "🔍  Scanner")
        self.tabs.addTab(self.results_tab, "📊  Résultats")
        self.tabs.addTab(self.details_tab, "📈  Détails")

        layout.addWidget(self.tabs)

        # === Connexions entre onglets ===
        # Quand scan terminé -> charger résultats
        self.scanner_tab.scan_finished.connect(self.on_scan_finished)

        # Quand paire sélectionnée -> afficher détails
        self.results_tab.pair_selected.connect(self.on_pair_selected)

        # Quand config change -> update
        self.config_tab.config_changed.connect(self.on_config_changed)

        # === Menu Bar ===
        self.create_menu_bar()

        # === Status Bar ===
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("✅ Prêt - Mode Scanner Uniquement (Aucun Trading)")

    def create_menu_bar(self):
        """Crée la barre de menu"""
        menu_bar = self.menuBar()

        # === Menu Fichier ===
        file_menu = menu_bar.addMenu("Fichier")

        export_action = QAction("📥 Exporter résultats...", self)
        export_action.triggered.connect(self.results_tab.export_to_csv)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        quit_action = QAction("🚪 Quitter", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # === Menu Scanner ===
        scanner_menu = menu_bar.addMenu("Scanner")

        start_scan_action = QAction("▶ Lancer le scan", self)
        start_scan_action.setShortcut("F5")
        start_scan_action.triggered.connect(self.start_scan)
        scanner_menu.addAction(start_scan_action)

        stop_scan_action = QAction("⏹ Arrêter le scan", self)
        stop_scan_action.setShortcut("Esc")
        stop_scan_action.triggered.connect(self.scanner_tab.stop_scan)
        scanner_menu.addAction(stop_scan_action)

        scanner_menu.addSeparator()

        config_action = QAction("⚙️ Configuration...", self)
        config_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        scanner_menu.addAction(config_action)

        # === Menu Affichage ===
        view_menu = menu_bar.addMenu("Affichage")

        config_view_action = QAction("⚙️  Configuration", self)
        config_view_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        view_menu.addAction(config_view_action)

        scanner_view_action = QAction("🔍  Scanner", self)
        scanner_view_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        view_menu.addAction(scanner_view_action)

        results_view_action = QAction("📊  Résultats", self)
        results_view_action.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        view_menu.addAction(results_view_action)

        details_view_action = QAction("📈  Détails", self)
        details_view_action.triggered.connect(lambda: self.tabs.setCurrentIndex(3))
        view_menu.addAction(details_view_action)

        # === Menu Aide ===
        help_menu = menu_bar.addMenu("Aide")

        about_action = QAction("ℹ️ À propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        docs_action = QAction("📖 Documentation", self)
        docs_action.triggered.connect(self.show_docs)
        help_menu.addAction(docs_action)

    def start_scan(self):
        """Lance le scan depuis le menu"""
        self.tabs.setCurrentIndex(1)  # Aller sur onglet Scanner
        self.scanner_tab.start_scan()

    def on_scan_finished(self, results, exchange_instance):
        """Callback quand un scan est terminé"""
        # Stocker l'exchange pour utilisation future
        self.exchange_instance = exchange_instance
        
        self.results_tab.load_results(results)

        # Passer à l'onglet résultats
        self.tabs.setCurrentIndex(2)

        # Mettre à jour status bar
        self.status_bar.showMessage(
            f"✅ Scan terminé - {len(results)} opportunités trouvées"
        )

    def on_pair_selected(self, pair_data):
        """Callback quand une paire est sélectionnée"""
        # Utiliser la nouvelle méthode update_details avec exchange
        self.details_tab.update_details(pair_data, self.exchange_instance)

        # Passer à l'onglet détails
        self.tabs.setCurrentIndex(3)

        symbol = pair_data.get("symbol", "N/A")
        self.status_bar.showMessage(f"📊 Détails: {symbol}")

    def on_config_changed(self):
        """Callback quand la configuration change"""
        self.status_bar.showMessage("⚙️ Configuration mise à jour")

    def show_about(self):
        """Affiche la boîte de dialogue À propos"""
        QMessageBox.about(
            self,
            "À propos de Crypto Scanner",
            "<h2>Crypto Scanner v3.0</h2>"
            "<p><b>Scanner de marché Binance avec analyse multi-indicateurs</b></p>"
            "<p>Détecte les opportunités de trading via:</p>"
            "<ul>"
            "<li>RSI (Relative Strength Index)</li>"
            "<li>Moyennes Mobiles (SMA/EMA)</li>"
            "<li>MACD</li>"
            "<li>Bollinger Bands</li>"
            "<li>Stochastic Oscillator</li>"
            "<li>Score de Confluence (V3)</li>"
            "</ul>"
            "<p><b>⚠️ MODE SCANNER UNIQUEMENT</b><br>"
            "Cette application ne fait AUCUN trading automatique.<br>"
            "Analyse de marché uniquement.</p>"
            "<hr>"
            "<p>Python 3.10+ | PyQt6 | CCXT | Pandas</p>"
            "<p>© 2026 - Crypto Scanner Project</p>",
        )

    def show_docs(self):
        """Affiche la documentation"""
        QMessageBox.information(
            self,
            "Documentation",
            "<h3>📖 Guide d'utilisation</h3>"
            "<p><b>1. Configuration</b><br>"
            "Paramétrez le scanner (timeframe, seuils, indicateurs)<br>"
            "puis cliquez sur 'Sauvegarder'</p>"
            "<p><b>2. Scanner</b><br>"
            "Lancez le scan avec le bouton ▶ Lancer le Scan<br>"
            "Suivez la progression en temps réel</p>"
            "<p><b>3. Résultats</b><br>"
            "Consultez le tableau des opportunités détectées<br>"
            "Triez par score, RSI, grade, etc.<br>"
            "Exportez en CSV ou Excel</p>"
            "<p><b>4. Détails</b><br>"
            "Sélectionnez une paire pour voir les graphiques<br>"
            "et le détail du score de confluence</p>"
            "<hr>"
            "<p>Pour plus d'informations, consultez:<br>"
            "<code>docs/cahier_des_charges_scanner.md</code><br>"
            "<code>README.md</code></p>",
        )

    def closeEvent(self, event):
        """Gère la fermeture de l'application"""
        reply = QMessageBox.question(
            self,
            "Quitter",
            "Voulez-vous vraiment quitter l'application?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Arrêter le scan si en cours
            if self.scanner_tab.worker and self.scanner_tab.worker.isRunning():
                self.scanner_tab.stop_scan()
            event.accept()
        else:
            event.ignore()
