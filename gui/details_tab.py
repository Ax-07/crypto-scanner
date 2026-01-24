"""
Onglet Détails - Visualisation graphique d'une paire
Affiche les graphiques de prix + indicateurs pour une paire sélectionnée
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QPushButton,
    QTextEdit,
)
import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

matplotlib.use("QtAgg")  # Changé de "Qt5Agg" à "QtAgg" pour PyQt6


class DetailsTab(QWidget):
    """
    Onglet de détails pour une paire sélectionnée
    Affiche graphiques de prix, RSI, MA, MACD, Bollinger, etc.
    """

    def __init__(self):
        super().__init__()
        self.current_pair = None
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface de l'onglet"""
        layout = QVBoxLayout()

        # === En-tête ===
        header_layout = QHBoxLayout()

        self.pair_label = QLabel("Aucune paire sélectionnée")
        self.pair_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(self.pair_label)

        header_layout.addStretch()

        self.refresh_button = QPushButton("🔄 Actualiser")
        self.refresh_button.setObjectName("secondaryButton")
        self.refresh_button.clicked.connect(self.refresh_data)
        self.refresh_button.setEnabled(False)
        header_layout.addWidget(self.refresh_button)

        layout.addLayout(header_layout)

        # === Informations clés ===
        info_group = QGroupBox("Informations")
        info_layout = QHBoxLayout()

        self.rsi_info = QLabel("RSI: -")
        self.score_info = QLabel("Score: -")
        self.trend_info = QLabel("Tendance: -")
        self.price_info = QLabel("Prix: -")

        info_layout.addWidget(self.rsi_info)
        info_layout.addWidget(self.score_info)
        info_layout.addWidget(self.trend_info)
        info_layout.addWidget(self.price_info)
        info_layout.addStretch()

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # === Graphique principal (Prix + MA) ===
        price_group = QGroupBox("Graphique Prix + Moyennes Mobiles")
        price_layout = QVBoxLayout()

        self.price_figure = Figure(figsize=(10, 4), facecolor="#252526")
        self.price_canvas = FigureCanvas(self.price_figure)
        price_layout.addWidget(self.price_canvas)

        price_group.setLayout(price_layout)
        layout.addWidget(price_group)

        # === Graphiques indicateurs ===
        indicators_layout = QHBoxLayout()

        # RSI
        rsi_group = QGroupBox("RSI")
        rsi_layout = QVBoxLayout()
        self.rsi_figure = Figure(figsize=(5, 3), facecolor="#252526")
        self.rsi_canvas = FigureCanvas(self.rsi_figure)
        rsi_layout.addWidget(self.rsi_canvas)
        rsi_group.setLayout(rsi_layout)
        indicators_layout.addWidget(rsi_group)

        # MACD
        macd_group = QGroupBox("MACD")
        macd_layout = QVBoxLayout()
        self.macd_figure = Figure(figsize=(5, 3), facecolor="#252526")
        self.macd_canvas = FigureCanvas(self.macd_figure)
        macd_layout.addWidget(self.macd_canvas)
        macd_group.setLayout(macd_layout)
        indicators_layout.addWidget(macd_group)

        layout.addLayout(indicators_layout)

        # === Détails texte ===
        details_group = QGroupBox("Détails Confluence")
        details_layout = QVBoxLayout()

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        details_layout.addWidget(self.details_text)

        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        layout.addStretch()
        self.setLayout(layout)

    def load_pair_data(self, pair_data):
        """Charge et affiche les données d'une paire"""
        self.current_pair = pair_data
        symbol = pair_data.get("symbol", "N/A")

        self.pair_label.setText(f"📊 {symbol}")
        self.refresh_button.setEnabled(True)

        # Mettre à jour infos
        rsi = pair_data.get("rsi", 0)
        score = pair_data.get("confluence_score", 0)
        grade = pair_data.get("confluence_grade", "-")
        trend_score = pair_data.get("trend_score", 0)
        price = pair_data.get("last_close_price", 0)

        self.rsi_info.setText(f"RSI: {rsi:.2f}")
        self.score_info.setText(f"Score: {score:.1f} ({grade})")
        self.trend_info.setText(f"Tendance: {trend_score}/3")
        self.price_info.setText(f"Prix: ${price:.6f}")

        # Afficher détails confluence
        self._display_confluence_details(pair_data)

        # TODO: Charger données OHLCV et tracer graphiques
        # Pour le moment, affichage placeholder
        self._plot_placeholder()

    def _display_confluence_details(self, data):
        """Affiche le détail du score de confluence"""
        details = "=== BREAKDOWN SCORE DE CONFLUENCE ===\n\n"

        # Score RSI
        score_rsi = data.get("score_rsi", 0)
        details += f"RSI:        {score_rsi}/20 points\n"

        # Score Tendance
        score_trend = data.get("score_trend", 0)
        details += f"Tendance:   {score_trend}/25 points\n"

        # Score MACD
        score_macd = data.get("score_macd", 0)
        macd_signal = data.get("macd_signal_type", "-")
        details += f"MACD:       {score_macd}/20 points ({macd_signal})\n"

        # Score Bollinger
        score_bb = data.get("score_bollinger", 0)
        bb_pos = data.get("bb_position", "-")
        details += f"Bollinger:  {score_bb}/20 points ({bb_pos})\n"

        # Score Stochastic
        score_stoch = data.get("score_stochastic", 0)
        stoch_signal = data.get("stoch_signal", "-")
        details += f"Stochastic: {score_stoch}/15 points ({stoch_signal})\n"

        details += f"\n{'='*40}\n"
        total = data.get("confluence_score", 0)
        grade = data.get("confluence_grade", "-")
        details += f"TOTAL:      {total:.1f}/100 (Grade {grade})\n"

        self.details_text.setText(details)

    def _plot_placeholder(self):
        """Affiche des graphiques placeholder (à remplacer par vraies données)"""
        # Prix
        ax_price = self.price_figure.add_subplot(111)
        ax_price.set_facecolor("#1e1e1e")
        ax_price.text(
            0.5,
            0.5,
            "Graphique Prix\n(À implémenter avec données OHLCV)",
            ha="center",
            va="center",
            fontsize=12,
            color="#cccccc",
        )
        ax_price.set_xticks([])
        ax_price.set_yticks([])
        self.price_canvas.draw()

        # RSI
        ax_rsi = self.rsi_figure.add_subplot(111)
        ax_rsi.set_facecolor("#1e1e1e")
        ax_rsi.text(
            0.5,
            0.5,
            "Graphique RSI\n(À implémenter)",
            ha="center",
            va="center",
            fontsize=10,
            color="#cccccc",
        )
        ax_rsi.set_xticks([])
        ax_rsi.set_yticks([])
        self.rsi_canvas.draw()

        # MACD
        ax_macd = self.macd_figure.add_subplot(111)
        ax_macd.set_facecolor("#1e1e1e")
        ax_macd.text(
            0.5,
            0.5,
            "Graphique MACD\n(À implémenter)",
            ha="center",
            va="center",
            fontsize=10,
            color="#cccccc",
        )
        ax_macd.set_xticks([])
        ax_macd.set_yticks([])
        self.macd_canvas.draw()

    def refresh_data(self):
        """Actualise les données de la paire"""
        if self.current_pair:
            # TODO: Recharger les données depuis l'API
            self.pair_label.setText(
                f"📊 {self.current_pair.get('symbol', 'N/A')} (Actualisation...)"
            )
            # Pour le moment, juste recharger ce qu'on a
            self.load_pair_data(self.current_pair)
