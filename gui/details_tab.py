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
    QScrollArea,
)
import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from gui.data_fetcher import OHLCVFetcher
from gui.chart_utils import ChartCalculator
import config

matplotlib.use("QtAgg")


class DetailsTab(QWidget):
    """
    Onglet de détails pour une paire sélectionnée
    Affiche graphiques de prix, RSI, MA, MACD, Bollinger, etc.
    """

    def __init__(self):
        super().__init__()
        self.current_pair = None
        self.current_data = None
        self.ohlcv_data = None
        self.fetcher = None
        self.calculator = ChartCalculator()
        self.exchange = None
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface de l'onglet"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)

        # En-tête
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

        # Informations clés
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

        # Graphique Prix
        price_group = QGroupBox("Graphique Prix + Moyennes Mobiles")
        price_layout = QVBoxLayout()
        self.price_figure = Figure(figsize=(10, 4), facecolor="#252526")
        self.price_canvas = FigureCanvas(self.price_figure)
        price_layout.addWidget(self.price_canvas)
        price_group.setLayout(price_layout)
        layout.addWidget(price_group)

        # Indicateurs ligne 1
        indicators_layout_1 = QHBoxLayout()

        # RSI
        rsi_group = QGroupBox("RSI")
        rsi_layout = QVBoxLayout()
        self.rsi_figure = Figure(figsize=(5, 3), facecolor="#252526")
        self.rsi_canvas = FigureCanvas(self.rsi_figure)
        rsi_layout.addWidget(self.rsi_canvas)
        rsi_group.setLayout(rsi_layout)
        indicators_layout_1.addWidget(rsi_group)

        # MACD
        macd_group = QGroupBox("MACD")
        macd_layout = QVBoxLayout()
        self.macd_figure = Figure(figsize=(5, 3), facecolor="#252526")
        self.macd_canvas = FigureCanvas(self.macd_figure)
        macd_layout.addWidget(self.macd_canvas)
        macd_group.setLayout(macd_layout)
        indicators_layout_1.addWidget(macd_group)

        layout.addLayout(indicators_layout_1)

        # Indicateurs ligne 2
        indicators_layout_2 = QHBoxLayout()

        # Bollinger
        bollinger_group = QGroupBox("Bollinger Bands")
        bollinger_layout = QVBoxLayout()
        self.bollinger_figure = Figure(figsize=(5, 3), facecolor="#252526")
        self.bollinger_canvas = FigureCanvas(self.bollinger_figure)
        bollinger_layout.addWidget(self.bollinger_canvas)
        bollinger_group.setLayout(bollinger_layout)
        indicators_layout_2.addWidget(bollinger_group)

        # Stochastic
        stochastic_group = QGroupBox("Stochastic Oscillator")
        stochastic_layout = QVBoxLayout()
        self.stochastic_figure = Figure(figsize=(5, 3), facecolor="#252526")
        self.stochastic_canvas = FigureCanvas(self.stochastic_figure)
        stochastic_layout.addWidget(self.stochastic_canvas)
        stochastic_group.setLayout(stochastic_layout)
        indicators_layout_2.addWidget(stochastic_group)

        layout.addLayout(indicators_layout_2)

        # Détails texte
        details_group = QGroupBox("Détails Confluence")
        details_layout = QVBoxLayout()
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        details_layout.addWidget(self.details_text)
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        layout.addStretch()

        scroll.setWidget(container)
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def update_details(self, result_data, exchange):
        """Affiche détails + graphiques pour une paire sélectionnée"""
        if not result_data:
            return

        self.current_data = result_data
        self.current_pair = result_data.get('symbol')
        self.exchange = exchange

        self.pair_label.setText(f"📊 {self.current_pair}")
        self.refresh_button.setEnabled(True)

        if self.fetcher is None and exchange is not None:
            self.fetcher = OHLCVFetcher(exchange)

        if self.fetcher:
            timeframe = config.TIMEFRAME
            self.ohlcv_data = self.fetcher.fetch_ohlcv(
                self.current_pair, timeframe=timeframe, limit=200
            )

            if self.ohlcv_data is None or len(self.ohlcv_data) == 0:
                self._show_error("Impossible de récupérer les données OHLCV")
                return

        self._update_key_info(result_data)
        self._display_confluence_details(result_data)

        if self.ohlcv_data is not None:
            self._plot_price_chart()
            self._plot_rsi_chart()
            self._plot_macd_chart()
            self._plot_bollinger_chart()
            self._plot_stochastic_chart()
        else:
            self._plot_placeholder()

    def _update_key_info(self, data):
        """Met à jour les informations clés"""
        rsi = data.get("rsi", 0)
        score = data.get("confluence_score", 0)
        grade = data.get("confluence_grade", "-")
        trend_score = data.get("trend_score", 0)
        price = data.get("last_close_price", 0)

        self.rsi_info.setText(f"RSI: {rsi:.2f}")
        self.score_info.setText(f"Score: {score:.1f} ({grade})")
        self.trend_info.setText(f"Tendance: {trend_score}/3")
        self.price_info.setText(f"Prix: ${price:.6f}")

    def _show_error(self, message):
        """Affiche un message d'erreur"""
        self.pair_label.setText(f"❌ {self.current_pair} - Erreur")
        self.details_text.setText(f"ERREUR:\n{message}")
        self._plot_placeholder()

    def _plot_price_chart(self):
        """Trace graphique prix + moyennes mobiles + volume"""
        self.price_figure.clear()
        if self.ohlcv_data is None:
            return

        gs = self.price_figure.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.05)
        ax_price = self.price_figure.add_subplot(gs[0])
        ax_volume = self.price_figure.add_subplot(gs[1], sharex=ax_price)

        ax_price.set_facecolor("#1e1e1e")
        ax_price.plot(
            self.ohlcv_data.index, self.ohlcv_data['close'],
            color='white', linewidth=1.5, label='Prix'
        )

        if hasattr(config, 'ENABLE_MA') and config.ENABLE_MA:
            if hasattr(config, 'MA_PERIODS'):
                for period in config.MA_PERIODS:
                    sma = self.calculator.calculate_sma(self.ohlcv_data, period)
                    if not sma.empty:
                        ax_price.plot(
                            sma.index, sma,
                            linewidth=1, alpha=0.7, label=f'SMA{period}'
                        )

                    ema = self.calculator.calculate_ema(self.ohlcv_data, period)
                    if not ema.empty:
                        ax_price.plot(
                            ema.index, ema,
                            linewidth=1, alpha=0.7, linestyle='--', label=f'EMA{period}'
                        )

        ax_price.set_ylabel('Prix (USDC)', color='#cccccc')
        ax_price.tick_params(colors='#cccccc')
        ax_price.legend(loc='upper left', fontsize=8, facecolor='#2d2d30', edgecolor='#555')
        ax_price.grid(True, alpha=0.2)
        plt.setp(ax_price.get_xticklabels(), visible=False)

        ax_volume.set_facecolor("#1e1e1e")
        colors = [
            'green' if self.ohlcv_data['close'].iloc[i] >= self.ohlcv_data['open'].iloc[i]
            else 'red' for i in range(len(self.ohlcv_data))
        ]
        ax_volume.bar(
            self.ohlcv_data.index, self.ohlcv_data['volume'],
            color=colors, alpha=0.5, width=0.1
        )
        ax_volume.set_ylabel('Volume', color='#cccccc')
        ax_volume.tick_params(colors='#cccccc')
        ax_volume.grid(True, alpha=0.2)

        self.price_figure.autofmt_xdate()
        self.price_canvas.draw()

    def _plot_rsi_chart(self):
        """Trace graphique RSI avec zones survente/surachat"""
        self.rsi_figure.clear()
        if self.ohlcv_data is None:
            return

        ax = self.rsi_figure.add_subplot(111)
        ax.set_facecolor("#1e1e1e")

        rsi = self.calculator.calculate_rsi(self.ohlcv_data, period=config.RSI_PERIOD)

        if rsi is not None and not rsi.empty:
            ax.plot(rsi.index, rsi, color='#9370DB', linewidth=1.5, label='RSI')
            ax.axhspan(0, 30, alpha=0.2, color='green', label='Survente')
            ax.axhspan(70, 100, alpha=0.2, color='red', label='Surachat')
            ax.axhline(y=50, color='white', linestyle='--', linewidth=0.5, alpha=0.5)
            ax.axhline(y=30, color='green', linestyle='--', linewidth=0.8, alpha=0.7)
            ax.axhline(y=70, color='red', linestyle='--', linewidth=0.8, alpha=0.7)
            ax.set_ylim(0, 100)
            ax.set_ylabel('RSI', color='#cccccc')
            ax.set_xlabel('Date', color='#cccccc')
            ax.tick_params(colors='#cccccc')
            ax.legend(loc='upper left', fontsize=7, facecolor='#2d2d30', edgecolor='#555')
            ax.grid(True, alpha=0.2)

        self.rsi_figure.autofmt_xdate()
        self.rsi_canvas.draw()

    def _plot_macd_chart(self):
        """Trace graphique MACD"""
        self.macd_figure.clear()
        if self.ohlcv_data is None:
            return

        ax = self.macd_figure.add_subplot(111)
        ax.set_facecolor("#1e1e1e")

        macd_data = self.calculator.calculate_macd(self.ohlcv_data)

        if macd_data and not macd_data['macd'].empty:
            ax.plot(
                macd_data['macd'].index, macd_data['macd'],
                color='#1E90FF', linewidth=1.2, label='MACD'
            )
            ax.plot(
                macd_data['signal'].index, macd_data['signal'],
                color='#FF8C00', linewidth=1.2, label='Signal'
            )
            colors = [
                'green' if val >= 0 else 'red'
                for val in macd_data['histogram']
            ]
            ax.bar(
                macd_data['histogram'].index, macd_data['histogram'],
                color=colors, alpha=0.5, width=0.1, label='Histogram'
            )
            ax.axhline(y=0, color='white', linestyle='--', linewidth=0.5, alpha=0.5)
            ax.set_ylabel('MACD', color='#cccccc')
            ax.set_xlabel('Date', color='#cccccc')
            ax.tick_params(colors='#cccccc')
            ax.legend(loc='upper left', fontsize=7, facecolor='#2d2d30', edgecolor='#555')
            ax.grid(True, alpha=0.2)

        self.macd_figure.autofmt_xdate()
        self.macd_canvas.draw()

    def _plot_bollinger_chart(self):
        """Trace graphique Bollinger Bands"""
        self.bollinger_figure.clear()
        if self.ohlcv_data is None:
            return

        ax = self.bollinger_figure.add_subplot(111)
        ax.set_facecolor("#1e1e1e")

        bb_data = self.calculator.calculate_bollinger_bands(self.ohlcv_data)

        if bb_data and not bb_data['middle'].empty:
            ax.plot(
                self.ohlcv_data.index, self.ohlcv_data['close'],
                color='white', linewidth=1.2, label='Prix'
            )
            ax.plot(
                bb_data['upper'].index, bb_data['upper'],
                color='red', linewidth=1, linestyle='--', alpha=0.7, label='Upper'
            )
            ax.plot(
                bb_data['middle'].index, bb_data['middle'],
                color='orange', linewidth=1, alpha=0.7, label='Middle'
            )
            ax.plot(
                bb_data['lower'].index, bb_data['lower'],
                color='green', linewidth=1, linestyle='--', alpha=0.7, label='Lower'
            )
            ax.fill_between(
                bb_data['upper'].index, bb_data['upper'], bb_data['lower'],
                alpha=0.1, color='gray'
            )
            ax.set_ylabel('Prix (USDC)', color='#cccccc')
            ax.set_xlabel('Date', color='#cccccc')
            ax.tick_params(colors='#cccccc')
            ax.legend(loc='upper left', fontsize=7, facecolor='#2d2d30', edgecolor='#555')
            ax.grid(True, alpha=0.2)

        self.bollinger_figure.autofmt_xdate()
        self.bollinger_canvas.draw()

    def _plot_stochastic_chart(self):
        """Trace graphique Stochastic Oscillator"""
        self.stochastic_figure.clear()
        if self.ohlcv_data is None:
            return

        ax = self.stochastic_figure.add_subplot(111)
        ax.set_facecolor("#1e1e1e")

        stoch_data = self.calculator.calculate_stochastic(self.ohlcv_data)

        if stoch_data and not stoch_data['k'].empty:
            ax.plot(
                stoch_data['k'].index, stoch_data['k'],
                color='#1E90FF', linewidth=1.2, label='%K'
            )
            ax.plot(
                stoch_data['d'].index, stoch_data['d'],
                color='#FF8C00', linewidth=1.2, label='%D'
            )
            ax.axhspan(0, 20, alpha=0.2, color='green', label='Survente')
            ax.axhspan(80, 100, alpha=0.2, color='red', label='Surachat')
            ax.axhline(y=20, color='green', linestyle='--', linewidth=0.8, alpha=0.7)
            ax.axhline(y=80, color='red', linestyle='--', linewidth=0.8, alpha=0.7)
            ax.axhline(y=50, color='white', linestyle='--', linewidth=0.5, alpha=0.5)
            ax.set_ylim(0, 100)
            ax.set_ylabel('Stochastic', color='#cccccc')
            ax.set_xlabel('Date', color='#cccccc')
            ax.tick_params(colors='#cccccc')
            ax.legend(loc='upper left', fontsize=7, facecolor='#2d2d30', edgecolor='#555')
            ax.grid(True, alpha=0.2)

        self.stochastic_figure.autofmt_xdate()
        self.stochastic_canvas.draw()

    def load_pair_data(self, pair_data):
        """DEPRECATED: Utiliser update_details() à la place"""
        self.update_details(pair_data, self.exchange)

    def _display_confluence_details(self, data):
        """Affiche le détail du score de confluence"""
        details = "=== BREAKDOWN SCORE DE CONFLUENCE ===\n\n"
        score_rsi = data.get("score_rsi", 0)
        details += f"RSI:        {score_rsi}/20 points\n"
        score_trend = data.get("score_trend", 0)
        details += f"Tendance:   {score_trend}/25 points\n"
        score_macd = data.get("score_macd", 0)
        macd_signal = data.get("macd_signal_type", "-")
        details += f"MACD:       {score_macd}/20 points ({macd_signal})\n"
        score_bb = data.get("score_bollinger", 0)
        bb_pos = data.get("bb_position", "-")
        details += f"Bollinger:  {score_bb}/20 points ({bb_pos})\n"
        score_stoch = data.get("score_stochastic", 0)
        stoch_signal = data.get("stoch_signal", "-")
        details += f"Stochastic: {score_stoch}/15 points ({stoch_signal})\n"
        details += f"\n{'='*40}\n"
        total = data.get("confluence_score", 0)
        grade = data.get("confluence_grade", "-")
        details += f"TOTAL:      {total:.1f}/100 (Grade {grade})\n"
        self.details_text.setText(details)

    def _plot_placeholder(self):
        """Affiche des graphiques placeholder"""
        for fig, canvas in [
            (self.price_figure, self.price_canvas),
            (self.rsi_figure, self.rsi_canvas),
            (self.macd_figure, self.macd_canvas),
            (self.bollinger_figure, self.bollinger_canvas),
            (self.stochastic_figure, self.stochastic_canvas)
        ]:
            fig.clear()
            ax = fig.add_subplot(111)
            ax.set_facecolor("#1e1e1e")
            ax.text(0.5, 0.5, "Données non disponibles", ha="center", va="center",
                    fontsize=10, color="#cccccc")
            ax.set_xticks([])
            ax.set_yticks([])
            canvas.draw()

    def refresh_data(self):
        """Actualise les données et graphiques"""
        if self.current_pair and self.exchange:
            self.pair_label.setText(f"📊 {self.current_pair} (Actualisation...)")

            if self.fetcher:
                self.ohlcv_data = self.fetcher.fetch_ohlcv(
                    self.current_pair, timeframe=config.TIMEFRAME, limit=200
                )

            if self.ohlcv_data is not None:
                self._plot_price_chart()
                self._plot_rsi_chart()
                self._plot_macd_chart()
                self._plot_bollinger_chart()
                self._plot_stochastic_chart()
                self.pair_label.setText(f"📊 {self.current_pair}")
            else:
                self._show_error("Impossible de rafraîchir les données")
