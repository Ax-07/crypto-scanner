"""
Onglet Configuration - Paramétrage du scanner
Permet de configurer tous les paramètres du scan (RSI, MA, indicateurs, etc.)
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QCheckBox,
    QPushButton,
    QScrollArea,
    QGridLayout,
    QDialog,
    QDialogButtonBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
import config


# ============================================================
# HELPERS
# ============================================================


def create_info_label(tooltip_text):
    """Crée un label d'information avec tooltip"""
    info_label = QLabel("ℹ️")
    info_label.setToolTip(tooltip_text)
    info_label.setStyleSheet(
        """
        QLabel {
            color: #f0b90b;
            font-size: 14px;
            padding: 2px;
        }
        QLabel:hover {
            color: #fcd535;
        }
    """
    )
    info_label.setCursor(Qt.CursorShape.PointingHandCursor)
    return info_label


# ============================================================
# MODALES DE CONFIGURATION
# ============================================================


class RSIConfigDialog(QDialog):
    """Modale de configuration RSI"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration RSI")
        self.setModal(True)
        self.setMinimumWidth(450)

        layout = QVBoxLayout()
        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        # Période RSI
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Période RSI:"))
        period_layout.addWidget(
            create_info_label(
                "La période du RSI détermine le nombre de bougies utilisées pour le calcul.\n"
                "• 14 (défaut) : Standard, équilibre entre réactivité et stabilité\n"
                "• 7-9 : Plus réactif, pour le trading court terme\n"
                "• 21-25 : Plus stable, pour le trading moyen/long terme"
            )
        )
        period_layout.addStretch()
        form_layout.addLayout(period_layout, 0, 0)

        self.rsi_period_spin = QSpinBox()
        self.rsi_period_spin.setRange(2, 50)
        self.rsi_period_spin.setValue(config.RSI_PERIOD)
        form_layout.addWidget(self.rsi_period_spin, 0, 1)

        # Seuil RSI
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Seuil RSI (survendu):"))
        threshold_layout.addWidget(
            create_info_label(
                "Le seuil de survendu pour détecter les opportunités d'achat.\n"
                "• RSI < 30 : Zone de survente classique\n"
                "• RSI < 35 : Moins restrictif, plus d'opportunités\n"
                "• RSI < 20 : Très restrictif, survente extrême\n\n"
                "Plus la valeur est basse, plus les opportunités sont rares mais potentiellement fortes."
            )
        )
        threshold_layout.addStretch()
        form_layout.addLayout(threshold_layout, 1, 0)

        self.rsi_threshold_spin = QDoubleSpinBox()
        self.rsi_threshold_spin.setRange(10.0, 50.0)
        self.rsi_threshold_spin.setValue(config.RSI_THRESHOLD)
        form_layout.addWidget(self.rsi_threshold_spin, 1, 1)

        layout.addLayout(form_layout)

        # Boutons OK/Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)


class MAConfigDialog(QDialog):
    """Modale de configuration Moyennes Mobiles"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Moyennes Mobiles")
        self.setModal(True)
        self.setMinimumWidth(500)

        layout = QVBoxLayout()
        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        # USE_SMA / USE_EMA
        types_layout = QHBoxLayout()
        types_layout.addWidget(QLabel("Types de moyennes:"))
        types_layout.addWidget(
            create_info_label(
                "SMA (Simple Moving Average) : Moyenne arithmétique simple\n"
                "EMA (Exponential Moving Average) : Moyenne pondérée exponentielle, plus réactive\n\n"
                "• SMA : Meilleure pour identifier les tendances long terme\n"
                "• EMA : Meilleure pour le trading court terme et réagit plus vite aux changements"
            )
        )
        types_layout.addStretch()
        form_layout.addLayout(types_layout, 0, 0)

        ma_types_layout = QHBoxLayout()
        self.use_sma_check = QCheckBox("SMA")
        self.use_sma_check.setChecked(config.USE_SMA)
        self.use_ema_check = QCheckBox("EMA")
        self.use_ema_check.setChecked(config.USE_EMA)
        ma_types_layout.addWidget(self.use_sma_check)
        ma_types_layout.addWidget(self.use_ema_check)
        ma_types_layout.addStretch()
        form_layout.addLayout(ma_types_layout, 0, 1)

        # Périodes SMA
        sma_periods_layout = QHBoxLayout()
        sma_periods_layout.addWidget(QLabel("Périodes SMA:"))
        sma_periods_layout.addWidget(
            create_info_label(
                "Périodes des SMA à calculer (séparées par des virgules).\n\n"
                "Exemples courants:\n"
                "• 20,50 : Court et moyen terme\n"
                "• 50,100,200 : Moyen et long terme\n"
                "• 20,50,100 : Analyse multi-périodes complète"
            )
        )
        sma_periods_layout.addStretch()
        form_layout.addLayout(sma_periods_layout, 1, 0)

        self.sma_periods_edit = QComboBox()
        self.sma_periods_edit.setEditable(True)
        self.sma_periods_edit.addItems(["20,50", "50,100,200", "20,50,100", "9,20,50"])
        periods_str = ",".join(map(str, config.SMA_PERIODS))
        self.sma_periods_edit.setCurrentText(periods_str)
        form_layout.addWidget(self.sma_periods_edit, 1, 1)

        # Périodes EMA
        ema_periods_layout = QHBoxLayout()
        ema_periods_layout.addWidget(QLabel("Périodes EMA:"))
        ema_periods_layout.addWidget(
            create_info_label(
                "Périodes des EMA à calculer (séparées par des virgules).\n\n"
                "Exemples courants:\n"
                "• 12,26 : Configuration MACD standard\n"
                "• 9,21,50 : Trading court/moyen terme\n"
                "• 20,50 : Configuration classique"
            )
        )
        ema_periods_layout.addStretch()
        form_layout.addLayout(ema_periods_layout, 2, 0)

        self.ema_periods_edit = QComboBox()
        self.ema_periods_edit.setEditable(True)
        self.ema_periods_edit.addItems(["20,50", "9,21,50", "12,26", "9,20,21,50"])
        periods_str = ",".join(map(str, config.EMA_PERIODS))
        self.ema_periods_edit.setCurrentText(periods_str)
        form_layout.addWidget(self.ema_periods_edit, 2, 1)

        # Timeframes MA
        timeframes_layout = QHBoxLayout()
        timeframes_layout.addWidget(QLabel("Timeframes:"))
        timeframes_layout.addWidget(
            create_info_label(
                "Unités de temps pour l'analyse multi-timeframe.\n\n"
                "Exemples:\n"
                "• 1w,1d,4h : Analyse complète (hebdo, jour, 4h)\n"
                "• 1d,4h : Analyse moyen terme\n"
                "• 4h : Analyse unique sur 4h\n\n"
                "Plus de timeframes = analyse plus complète mais scan plus lent"
            )
        )
        timeframes_layout.addStretch()
        form_layout.addLayout(timeframes_layout, 3, 0)

        self.ma_timeframes_edit = QComboBox()
        self.ma_timeframes_edit.setEditable(True)
        self.ma_timeframes_edit.addItems(["1w,1d,4h", "1d,4h", "1w,1d", "4h"])
        tf_str = ",".join(config.MA_TIMEFRAMES)
        self.ma_timeframes_edit.setCurrentText(tf_str)
        form_layout.addWidget(self.ma_timeframes_edit, 3, 1)

        # Min trend score
        trend_score_layout = QHBoxLayout()
        trend_score_layout.addWidget(QLabel("Score tendance min:"))
        trend_score_layout.addWidget(
            create_info_label(
                "Nombre minimum de timeframes en tendance haussière (0-3).\n\n"
                "• 0 : Pas de filtre (toutes les paires)\n"
                "• 1 : Au moins 1 timeframe haussier\n"
                "• 2 : 2 timeframes haussiers (recommandé)\n"
                "• 3 : Tous les timeframes haussiers (très restrictif)\n\n"
                "Plus le score est élevé, plus la tendance est confirmée mais moins d'opportunités."
            )
        )
        trend_score_layout.addStretch()
        form_layout.addLayout(trend_score_layout, 4, 0)

        self.min_trend_score_spin = QSpinBox()
        self.min_trend_score_spin.setRange(0, 3)
        self.min_trend_score_spin.setValue(config.MIN_TREND_SCORE)
        form_layout.addWidget(self.min_trend_score_spin, 4, 1)

        layout.addLayout(form_layout)

        # Boutons OK/Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)


class MACDConfigDialog(QDialog):
    """Modale de configuration MACD"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration MACD")
        self.setModal(True)
        self.setMinimumWidth(450)

        layout = QVBoxLayout()
        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        # MACD Fast
        fast_layout = QHBoxLayout()
        fast_layout.addWidget(QLabel("Période rapide:"))
        fast_layout.addWidget(
            create_info_label(
                "EMA rapide pour le calcul du MACD.\n\n"
                "• 12 (défaut) : Configuration standard\n"
                "• 8-10 : Plus réactif pour le court terme\n"
                "• 15-20 : Plus stable pour le moyen terme"
            )
        )
        fast_layout.addStretch()
        form_layout.addLayout(fast_layout, 0, 0)

        self.macd_fast_spin = QSpinBox()
        self.macd_fast_spin.setRange(5, 50)
        self.macd_fast_spin.setValue(config.MACD_FAST_PERIOD)
        form_layout.addWidget(self.macd_fast_spin, 0, 1)

        # MACD Slow
        slow_layout = QHBoxLayout()
        slow_layout.addWidget(QLabel("Période lente:"))
        slow_layout.addWidget(
            create_info_label(
                "EMA lente pour le calcul du MACD.\n\n"
                "• 26 (défaut) : Configuration standard\n"
                "• 20-24 : Plus réactif\n"
                "• 30-40 : Plus stable\n\n"
                "Doit être supérieure à la période rapide."
            )
        )
        slow_layout.addStretch()
        form_layout.addLayout(slow_layout, 1, 0)

        self.macd_slow_spin = QSpinBox()
        self.macd_slow_spin.setRange(10, 100)
        self.macd_slow_spin.setValue(config.MACD_SLOW_PERIOD)
        form_layout.addWidget(self.macd_slow_spin, 1, 1)

        # MACD Signal
        signal_layout = QHBoxLayout()
        signal_layout.addWidget(QLabel("Période signal:"))
        signal_layout.addWidget(
            create_info_label(
                "EMA de la ligne MACD pour générer les signaux.\n\n"
                "• 9 (défaut) : Configuration standard\n"
                "• 5-7 : Signaux plus fréquents\n"
                "• 12-15 : Signaux plus fiables mais rares\n\n"
                "Le croisement MACD/Signal génère les signaux d'achat/vente."
            )
        )
        signal_layout.addStretch()
        form_layout.addLayout(signal_layout, 2, 0)

        self.macd_signal_spin = QSpinBox()
        self.macd_signal_spin.setRange(3, 20)
        self.macd_signal_spin.setValue(config.MACD_SIGNAL_PERIOD)
        form_layout.addWidget(self.macd_signal_spin, 2, 1)

        layout.addLayout(form_layout)

        # Boutons OK/Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)


class BollingerConfigDialog(QDialog):
    """Modale de configuration Bollinger Bands"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Bollinger Bands")
        self.setModal(True)
        self.setMinimumWidth(450)

        layout = QVBoxLayout()
        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        # Période
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Période:"))
        period_layout.addWidget(
            create_info_label(
                "Période de la moyenne mobile pour les bandes.\n\n"
                "• 20 (défaut) : Standard, équilibre optimal\n"
                "• 15 : Plus réactif, court terme\n"
                "• 25-30 : Plus stable, moyen/long terme\n\n"
                "Base de calcul pour les bandes supérieure et inférieure."
            )
        )
        period_layout.addStretch()
        form_layout.addLayout(period_layout, 0, 0)

        self.bb_period_spin = QSpinBox()
        self.bb_period_spin.setRange(10, 50)
        self.bb_period_spin.setValue(config.BOLLINGER_PERIOD)
        form_layout.addWidget(self.bb_period_spin, 0, 1)

        # Std Dev
        std_layout = QHBoxLayout()
        std_layout.addWidget(QLabel("Écart-type:"))
        std_layout.addWidget(
            create_info_label(
                "Multiplicateur de l'écart-type pour les bandes.\n\n"
                "• 2.0 (défaut) : Configuration standard (95% des prix)\n"
                "• 1.5 : Bandes plus serrées, plus de signaux\n"
                "• 2.5-3.0 : Bandes plus larges, signaux rares mais forts\n\n"
                "Prix touchant la bande inf. = survente potentielle."
            )
        )
        std_layout.addStretch()
        form_layout.addLayout(std_layout, 1, 0)

        self.bb_std_spin = QDoubleSpinBox()
        self.bb_std_spin.setRange(1.0, 4.0)
        self.bb_std_spin.setSingleStep(0.1)
        self.bb_std_spin.setValue(config.BOLLINGER_STD_DEV)
        form_layout.addWidget(self.bb_std_spin, 1, 1)

        layout.addLayout(form_layout)

        # Boutons OK/Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)


class StochasticConfigDialog(QDialog):
    """Modale de configuration Stochastic"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Stochastic")
        self.setModal(True)
        self.setMinimumWidth(450)

        layout = QVBoxLayout()
        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        # %K Period
        k_layout = QHBoxLayout()
        k_layout.addWidget(QLabel("Période %K:"))
        k_layout.addWidget(
            create_info_label(
                "Période pour le calcul de la ligne %K (stochastique rapide).\n\n"
                "• 14 (défaut) : Configuration standard\n"
                "• 9-12 : Plus réactif, court terme\n"
                "• 18-21 : Plus lisse, moyen terme\n\n"
                "Mesure la position du prix par rapport aux plus hauts/bas récents."
            )
        )
        k_layout.addStretch()
        form_layout.addLayout(k_layout, 0, 0)

        self.stoch_k_spin = QSpinBox()
        self.stoch_k_spin.setRange(5, 30)
        self.stoch_k_spin.setValue(config.STOCHASTIC_K_PERIOD)
        form_layout.addWidget(self.stoch_k_spin, 0, 1)

        # %D Period
        d_layout = QHBoxLayout()
        d_layout.addWidget(QLabel("Période %D:"))
        d_layout.addWidget(
            create_info_label(
                "Période de lissage de %K pour obtenir %D (stochastique lente).\n\n"
                "• 3 (défaut) : Configuration standard\n"
                "• 2 : Plus réactif\n"
                "• 5-7 : Plus lisse, moins de faux signaux\n\n"
                "Le croisement %K/%D génère les signaux. < 20 = survente."
            )
        )
        d_layout.addStretch()
        form_layout.addLayout(d_layout, 1, 0)

        self.stoch_d_spin = QSpinBox()
        self.stoch_d_spin.setRange(2, 10)
        self.stoch_d_spin.setValue(config.STOCHASTIC_D_PERIOD)
        form_layout.addWidget(self.stoch_d_spin, 1, 1)

        layout.addLayout(form_layout)

        # Boutons OK/Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)


# ============================================================
# ONGLET DE CONFIGURATION PRINCIPAL
# ============================================================


class ConfigTab(QWidget):
    """
    Onglet de configuration du scanner
    Permet de modifier tous les paramètres avant le scan
    """

    # Signal émis quand la configuration change
    config_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.advanced_mode = False  # Mode basique par défaut
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface de l'onglet"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # === Bouton Mode Avancé/Basique ===
        mode_layout = QHBoxLayout()
        mode_layout.addStretch()

        self.mode_button = QPushButton("⚙️ Mode Avancé")
        self.mode_button.setObjectName("secondaryButton")
        self.mode_button.setToolTip("Afficher/masquer les paramètres avancés")
        self.mode_button.clicked.connect(self.toggle_mode)
        mode_layout.addWidget(self.mode_button)

        main_layout.addLayout(mode_layout)

        # ScrollArea pour gérer beaucoup de paramètres
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: #161a1e;")  # Fond sombre explicite

        scroll_content = QWidget()
        scroll_content.setStyleSheet(
            "background-color: #161a1e;"
        )  # Fond sombre explicite
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(8, 8, 8, 8)
        scroll_layout.setSpacing(8)

        # === GROUPE: Paramètres de base ===
        self.base_group = self._create_base_group()
        scroll_layout.addWidget(self.base_group)

        # === GROUPE: Indicateurs (avec boutons de config) ===
        self.indicators_group = self._create_indicators_group()
        scroll_layout.addWidget(self.indicators_group)

        # === GROUPE: Confluence (AVANCÉ) ===
        self.confluence_group = self._create_confluence_group()
        scroll_layout.addWidget(self.confluence_group)

        # === GROUPE: Performance (AVANCÉ) ===
        self.performance_group = self._create_performance_group()
        scroll_layout.addWidget(self.performance_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Boutons d'action
        buttons_layout = QHBoxLayout()

        self.reset_button = QPushButton("Réinitialiser")
        self.reset_button.setObjectName("secondaryButton")
        self.reset_button.clicked.connect(self.reset_to_defaults)

        self.save_button = QPushButton("Sauvegarder")
        self.save_button.setObjectName("successButton")
        self.save_button.clicked.connect(self.save_config)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.save_button)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

        # Initialiser tous les widgets de configuration avec les valeurs par défaut
        self._init_config_widgets()

        # Appliquer le mode initial (basique)
        self._update_mode_visibility()

    def toggle_mode(self):
        """Bascule entre mode basique et mode avancé"""
        self.advanced_mode = not self.advanced_mode
        self._update_mode_visibility()

    def _update_mode_visibility(self):
        """Met à jour la visibilité des groupes selon le mode"""
        if self.advanced_mode:
            # Mode avancé : tout afficher
            self.mode_button.setText("📋 Mode Basique")
            self.confluence_group.setVisible(True)
            self.performance_group.setVisible(True)
        else:
            # Mode basique : masquer les paramètres avancés
            self.mode_button.setText("⚙️ Mode Avancé")
            self.confluence_group.setVisible(False)
            self.performance_group.setVisible(False)

    def _init_config_widgets(self):
        """Initialise tous les widgets de configuration avec les valeurs par défaut"""
        # RSI
        self.rsi_period_spin = QSpinBox()
        self.rsi_period_spin.setRange(2, 50)
        self.rsi_period_spin.setValue(config.RSI_PERIOD)

        self.rsi_threshold_spin = QDoubleSpinBox()
        self.rsi_threshold_spin.setRange(10.0, 50.0)
        self.rsi_threshold_spin.setValue(config.RSI_THRESHOLD)

        # MA (Moyennes Mobiles)
        self.use_sma_check = QCheckBox()
        self.use_sma_check.setChecked(config.USE_SMA)

        self.use_ema_check = QCheckBox()
        self.use_ema_check.setChecked(config.USE_EMA)

        self.sma_periods_edit = QComboBox()
        self.sma_periods_edit.setEditable(True)
        self.sma_periods_edit.setCurrentText(",".join(map(str, config.SMA_PERIODS)))

        self.ema_periods_edit = QComboBox()
        self.ema_periods_edit.setEditable(True)
        self.ema_periods_edit.setCurrentText(",".join(map(str, config.EMA_PERIODS)))

        self.ma_timeframes_edit = QComboBox()
        self.ma_timeframes_edit.setEditable(True)
        self.ma_timeframes_edit.setCurrentText(",".join(config.MA_TIMEFRAMES))

        self.min_trend_score_spin = QSpinBox()
        self.min_trend_score_spin.setRange(0, 10)
        self.min_trend_score_spin.setValue(config.MIN_TREND_SCORE)

        # MACD
        self.macd_fast_spin = QSpinBox()
        self.macd_fast_spin.setRange(5, 30)
        self.macd_fast_spin.setValue(config.MACD_FAST_PERIOD)

        self.macd_slow_spin = QSpinBox()
        self.macd_slow_spin.setRange(15, 50)
        self.macd_slow_spin.setValue(config.MACD_SLOW_PERIOD)

        self.macd_signal_spin = QSpinBox()
        self.macd_signal_spin.setRange(5, 20)
        self.macd_signal_spin.setValue(config.MACD_SIGNAL_PERIOD)

        # Bollinger
        self.bb_period_spin = QSpinBox()
        self.bb_period_spin.setRange(10, 50)
        self.bb_period_spin.setValue(config.BOLLINGER_PERIOD)

        self.bb_std_spin = QDoubleSpinBox()
        self.bb_std_spin.setRange(1.0, 4.0)
        self.bb_std_spin.setSingleStep(0.1)
        self.bb_std_spin.setValue(config.BOLLINGER_STD_DEV)

        # Stochastic
        self.stoch_k_spin = QSpinBox()
        self.stoch_k_spin.setRange(5, 30)
        self.stoch_k_spin.setValue(config.STOCHASTIC_K_PERIOD)

        self.stoch_d_spin = QSpinBox()
        self.stoch_d_spin.setRange(2, 10)
        self.stoch_d_spin.setValue(config.STOCHASTIC_D_PERIOD)

    def _create_base_group(self):
        """Crée le groupe des paramètres de base"""
        group = QGroupBox("Paramètres de base")
        layout = QGridLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        layout.setVerticalSpacing(6)
        layout.setHorizontalSpacing(8)

        # Timeframe
        timeframe_layout = QHBoxLayout()
        timeframe_layout.addWidget(QLabel("Timeframe:"))
        timeframe_layout.addWidget(
            create_info_label(
                "Unité de temps pour l'analyse principale (RSI, etc.).\n\n"
                "Exemples:\n"
                "• 4h (recommandé) : Moyen terme, équilibre qualité/quantité\n"
                "• 1h : Court terme, plus de signaux\n"
                "• 1d : Long terme, signaux plus fiables\n"
                "• 15m-30m : Scalping, très court terme\n\n"
                "⚠️ Plus le timeframe est court, plus il y a de bruit."
            )
        )
        timeframe_layout.addStretch()
        layout.addLayout(timeframe_layout, 0, 0)

        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(
            ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "1w"]
        )
        self.timeframe_combo.setCurrentText(config.TIMEFRAME)
        layout.addWidget(self.timeframe_combo, 0, 1)

        # Quote filter
        quote_layout = QHBoxLayout()
        quote_layout.addWidget(QLabel("Quote (paire):"))
        quote_layout.addWidget(
            create_info_label(
                "Devise de référence pour filtrer les paires.\n\n"
                "• USDC : Stablecoin, recommandé\n"
                "• USDT : Stablecoin le plus utilisé\n"
                "• BTC : Paires en Bitcoin\n"
                "• ETH : Paires en Ethereum\n\n"
                "Exemple: BTC/USDC = acheter du Bitcoin avec de l'USDC"
            )
        )
        quote_layout.addStretch()
        layout.addLayout(quote_layout, 1, 0)

        self.quote_combo = QComboBox()
        self.quote_combo.addItems(["USDC", "USDT", "BUSD", "BTC", "ETH"])
        self.quote_combo.setCurrentText(config.QUOTE_FILTER)
        layout.addWidget(self.quote_combo, 1, 1)

        # Min bars
        min_bars_layout = QHBoxLayout()
        min_bars_layout.addWidget(QLabel("Minimum de bougies:"))
        min_bars_layout.addWidget(
            create_info_label(
                "Nombre minimum de bougies OHLCV à récupérer.\n\n"
                "• 200 (défaut) : Suffisant pour la plupart des calculs\n"
                "• 100 : Minimum acceptable\n"
                "• 500+ : Analyse long terme avec grandes périodes MA\n\n"
                "Plus de données = calculs plus précis mais scan plus lent."
            )
        )
        min_bars_layout.addStretch()
        layout.addLayout(min_bars_layout, 2, 0)

        self.min_bars_spin = QSpinBox()
        self.min_bars_spin.setRange(50, 1000)
        self.min_bars_spin.setValue(config.MIN_OHLCV_BARS)
        layout.addWidget(self.min_bars_spin, 2, 1)

        # Max pairs (limite dev)
        max_pairs_layout = QHBoxLayout()
        max_pairs_layout.addWidget(QLabel("Limite paires (0=toutes):"))
        max_pairs_layout.addWidget(
            create_info_label(
                "Limiter le nombre de paires à scanner (pour les tests).\n\n"
                "• 0 : Scanner toutes les paires disponibles\n"
                "• 20-50 : Test rapide\n"
                "• 100+ : Test approfondi\n\n"
                "En production, laisser à 0 pour scanner tout le marché."
            )
        )
        max_pairs_layout.addStretch()
        layout.addLayout(max_pairs_layout, 3, 0)

        self.max_pairs_spin = QSpinBox()
        self.max_pairs_spin.setRange(0, 500)
        self.max_pairs_spin.setValue(config.MAX_PAIRS if config.MAX_PAIRS else 0)
        layout.addWidget(self.max_pairs_spin, 3, 1)

        # Exclure stables
        exclude_layout = QHBoxLayout()
        self.exclude_stables_check = QCheckBox("Exclure paires stable/stable")
        self.exclude_stables_check.setChecked(config.EXCLUDE_STABLE_PAIRS)
        exclude_layout.addWidget(self.exclude_stables_check)
        exclude_layout.addWidget(
            create_info_label(
                "Exclure les paires stablecoin/stablecoin.\n\n"
                "Exemples: USDC/USDT, DAI/BUSD, etc.\n\n"
                "Ces paires ont très peu de volatilité et ne sont\n"
                "généralement pas intéressantes pour le trading."
            )
        )
        exclude_layout.addStretch()
        layout.addLayout(exclude_layout, 4, 0, 1, 2)

        group.setLayout(layout)
        return group

    def _create_indicators_group(self):
        """Crée le groupe choix des indicateurs avec boutons de configuration"""
        group = QGroupBox("Indicateurs Techniques")
        layout = QGridLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        layout.setVerticalSpacing(8)
        layout.setHorizontalSpacing(10)

        # En-tête
        header_label = QLabel("Sélectionner et configurer les indicateurs à utiliser:")
        header_label.setStyleSheet("color: #848e9c; font-size: 11px;")
        layout.addWidget(header_label, 0, 0, 1, 3)

        row = 1

        # === RSI ===
        self.use_rsi_check = QCheckBox("RSI")
        self.use_rsi_check.setChecked(config.USE_RSI)
        self.use_rsi_check.stateChanged.connect(self._on_indicator_changed)
        layout.addWidget(self.use_rsi_check, row, 0)

        rsi_config_btn = QPushButton("⚙️ Configurer")
        rsi_config_btn.setObjectName("secondaryButton")
        rsi_config_btn.setMaximumWidth(120)
        rsi_config_btn.clicked.connect(self._open_rsi_config)
        layout.addWidget(rsi_config_btn, row, 1)

        rsi_info = QLabel("(Relative Strength Index)")
        rsi_info.setStyleSheet("color: #848e9c; font-size: 10px; font-style: italic;")
        layout.addWidget(rsi_info, row, 2)
        row += 1

        # === Moyennes Mobiles ===
        self.use_ma_check = QCheckBox("Moyennes Mobiles")
        self.use_ma_check.setChecked(config.USE_MA)
        self.use_ma_check.stateChanged.connect(self._on_indicator_changed)
        layout.addWidget(self.use_ma_check, row, 0)

        ma_config_btn = QPushButton("⚙️ Configurer")
        ma_config_btn.setObjectName("secondaryButton")
        ma_config_btn.setMaximumWidth(120)
        ma_config_btn.clicked.connect(self._open_ma_config)
        layout.addWidget(ma_config_btn, row, 1)

        ma_info = QLabel("(SMA / EMA)")
        ma_info.setStyleSheet("color: #848e9c; font-size: 10px; font-style: italic;")
        layout.addWidget(ma_info, row, 2)
        row += 1

        # === MACD ===
        self.use_macd_check = QCheckBox("MACD")
        self.use_macd_check.setChecked(config.USE_MACD)
        layout.addWidget(self.use_macd_check, row, 0)

        macd_config_btn = QPushButton("⚙️ Configurer")
        macd_config_btn.setObjectName("secondaryButton")
        macd_config_btn.setMaximumWidth(120)
        macd_config_btn.clicked.connect(self._open_macd_config)
        layout.addWidget(macd_config_btn, row, 1)

        macd_info = QLabel("(Moving Average Convergence Divergence)")
        macd_info.setStyleSheet("color: #848e9c; font-size: 10px; font-style: italic;")
        layout.addWidget(macd_info, row, 2)
        row += 1

        # === Bollinger Bands ===
        self.use_bollinger_check = QCheckBox("Bollinger Bands")
        self.use_bollinger_check.setChecked(config.USE_BOLLINGER)
        layout.addWidget(self.use_bollinger_check, row, 0)

        bb_config_btn = QPushButton("⚙️ Configurer")
        bb_config_btn.setObjectName("secondaryButton")
        bb_config_btn.setMaximumWidth(120)
        bb_config_btn.clicked.connect(self._open_bollinger_config)
        layout.addWidget(bb_config_btn, row, 1)

        bb_info = QLabel("(Bandes de Bollinger)")
        bb_info.setStyleSheet("color: #848e9c; font-size: 10px; font-style: italic;")
        layout.addWidget(bb_info, row, 2)
        row += 1

        # === Stochastic ===
        self.use_stochastic_check = QCheckBox("Stochastic")
        self.use_stochastic_check.setChecked(config.USE_STOCHASTIC)
        layout.addWidget(self.use_stochastic_check, row, 0)

        stoch_config_btn = QPushButton("⚙️ Configurer")
        stoch_config_btn.setObjectName("secondaryButton")
        stoch_config_btn.setMaximumWidth(120)
        stoch_config_btn.clicked.connect(self._open_stochastic_config)
        layout.addWidget(stoch_config_btn, row, 1)

        stoch_info = QLabel("(Oscillateur stochastique)")
        stoch_info.setStyleSheet("color: #848e9c; font-size: 10px; font-style: italic;")
        layout.addWidget(stoch_info, row, 2)

        group.setLayout(layout)
        return group

    # ============================================================
    # Méthodes pour ouvrir les modales de configuration
    # ============================================================

    def _open_rsi_config(self):
        """Ouvre la modale de configuration RSI"""
        dialog = RSIConfigDialog(self)
        # Initialiser avec les valeurs actuelles
        dialog.rsi_period_spin.setValue(self.rsi_period_spin.value())
        dialog.rsi_threshold_spin.setValue(self.rsi_threshold_spin.value())

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Mettre à jour les valeurs
            self.rsi_period_spin.setValue(dialog.rsi_period_spin.value())
            self.rsi_threshold_spin.setValue(dialog.rsi_threshold_spin.value())

    def _open_ma_config(self):
        """Ouvre la modale de configuration Moyennes Mobiles"""
        dialog = MAConfigDialog(self)
        # Initialiser avec les valeurs actuelles
        dialog.use_sma_check.setChecked(self.use_sma_check.isChecked())
        dialog.use_ema_check.setChecked(self.use_ema_check.isChecked())
        dialog.sma_periods_edit.setCurrentText(self.sma_periods_edit.currentText())
        dialog.ema_periods_edit.setCurrentText(self.ema_periods_edit.currentText())
        dialog.ma_timeframes_edit.setCurrentText(self.ma_timeframes_edit.currentText())
        dialog.min_trend_score_spin.setValue(self.min_trend_score_spin.value())

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Mettre à jour les valeurs
            self.use_sma_check.setChecked(dialog.use_sma_check.isChecked())
            self.use_ema_check.setChecked(dialog.use_ema_check.isChecked())
            self.sma_periods_edit.setCurrentText(dialog.sma_periods_edit.currentText())
            self.ema_periods_edit.setCurrentText(dialog.ema_periods_edit.currentText())
            self.ma_timeframes_edit.setCurrentText(
                dialog.ma_timeframes_edit.currentText()
            )
            self.min_trend_score_spin.setValue(dialog.min_trend_score_spin.value())

    def _open_macd_config(self):
        """Ouvre la modale de configuration MACD"""
        dialog = MACDConfigDialog(self)
        # Initialiser avec les valeurs actuelles
        dialog.macd_fast_spin.setValue(self.macd_fast_spin.value())
        dialog.macd_slow_spin.setValue(self.macd_slow_spin.value())
        dialog.macd_signal_spin.setValue(self.macd_signal_spin.value())

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Mettre à jour les valeurs
            self.macd_fast_spin.setValue(dialog.macd_fast_spin.value())
            self.macd_slow_spin.setValue(dialog.macd_slow_spin.value())
            self.macd_signal_spin.setValue(dialog.macd_signal_spin.value())

    def _open_bollinger_config(self):
        """Ouvre la modale de configuration Bollinger"""
        dialog = BollingerConfigDialog(self)
        # Initialiser avec les valeurs actuelles
        dialog.bb_period_spin.setValue(self.bb_period_spin.value())
        dialog.bb_std_spin.setValue(self.bb_std_spin.value())

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Mettre à jour les valeurs
            self.bb_period_spin.setValue(dialog.bb_period_spin.value())
            self.bb_std_spin.setValue(dialog.bb_std_spin.value())

    def _open_stochastic_config(self):
        """Ouvre la modale de configuration Stochastic"""
        dialog = StochasticConfigDialog(self)
        # Initialiser avec les valeurs actuelles
        dialog.stoch_k_spin.setValue(self.stoch_k_spin.value())
        dialog.stoch_d_spin.setValue(self.stoch_d_spin.value())

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Mettre à jour les valeurs
            self.stoch_k_spin.setValue(dialog.stoch_k_spin.value())
            self.stoch_d_spin.setValue(dialog.stoch_d_spin.value())

    def _create_confluence_group(self):
        """Crée le groupe score de confluence (V3)"""
        group = QGroupBox("Score de Confluence")
        layout = QGridLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        layout.setVerticalSpacing(6)
        layout.setHorizontalSpacing(8)

        # Activer confluence
        self.use_confluence_check = QCheckBox("Utiliser score de confluence")
        self.use_confluence_check.setChecked(config.USE_CONFLUENCE_SCORE)
        layout.addWidget(self.use_confluence_check, 0, 0, 1, 2)

        # Score minimum
        layout.addWidget(QLabel("Score minimum (0-100):"), 1, 0)
        self.min_confluence_spin = QDoubleSpinBox()
        self.min_confluence_spin.setRange(0, 100)
        self.min_confluence_spin.setValue(config.MIN_CONFLUENCE_SCORE)
        layout.addWidget(self.min_confluence_spin, 1, 1)

        layout.addWidget(QLabel("Poids des indicateurs:"), 2, 0, 1, 2)

        # Poids RSI
        layout.addWidget(QLabel("  RSI:"), 3, 0)
        self.weight_rsi_spin = QSpinBox()
        self.weight_rsi_spin.setRange(0, 50)
        self.weight_rsi_spin.setValue(config.CONFLUENCE_WEIGHTS["rsi"])
        layout.addWidget(self.weight_rsi_spin, 3, 1)

        # Poids Trend
        layout.addWidget(QLabel("  Tendance:"), 4, 0)
        self.weight_trend_spin = QSpinBox()
        self.weight_trend_spin.setRange(0, 50)
        self.weight_trend_spin.setValue(config.CONFLUENCE_WEIGHTS["trend"])
        layout.addWidget(self.weight_trend_spin, 4, 1)

        # Poids MACD
        layout.addWidget(QLabel("  MACD:"), 5, 0)
        self.weight_macd_spin = QSpinBox()
        self.weight_macd_spin.setRange(0, 50)
        self.weight_macd_spin.setValue(config.CONFLUENCE_WEIGHTS["macd"])
        layout.addWidget(self.weight_macd_spin, 5, 1)

        # Poids Bollinger
        layout.addWidget(QLabel("  Bollinger:"), 6, 0)
        self.weight_bollinger_spin = QSpinBox()
        self.weight_bollinger_spin.setRange(0, 50)
        self.weight_bollinger_spin.setValue(config.CONFLUENCE_WEIGHTS["bollinger"])
        layout.addWidget(self.weight_bollinger_spin, 6, 1)

        # Poids Stochastic
        layout.addWidget(QLabel("  Stochastic:"), 7, 0)
        self.weight_stochastic_spin = QSpinBox()
        self.weight_stochastic_spin.setRange(0, 50)
        self.weight_stochastic_spin.setValue(config.CONFLUENCE_WEIGHTS["stochastic"])
        layout.addWidget(self.weight_stochastic_spin, 7, 1)

        group.setLayout(layout)
        return group

    def _create_performance_group(self):
        """Crée le groupe performance/concurrency"""
        group = QGroupBox("Performance")
        layout = QGridLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        layout.setVerticalSpacing(6)
        layout.setHorizontalSpacing(8)

        # Enable concurrency
        self.enable_concurrency_check = QCheckBox("Activer mode parallèle")
        self.enable_concurrency_check.setChecked(config.ENABLE_CONCURRENCY)
        self.enable_concurrency_check.stateChanged.connect(self._on_concurrency_changed)
        layout.addWidget(self.enable_concurrency_check, 0, 0, 1, 2)

        # Max workers
        layout.addWidget(QLabel("Nombre de workers:"), 1, 0)
        self.max_workers_spin = QSpinBox()
        self.max_workers_spin.setRange(1, 20)
        self.max_workers_spin.setValue(config.MAX_WORKERS)
        self.max_workers_spin.setEnabled(config.ENABLE_CONCURRENCY)
        layout.addWidget(self.max_workers_spin, 1, 1)

        # Max retries
        layout.addWidget(QLabel("Tentatives max (erreurs):"), 2, 0)
        self.max_retries_spin = QSpinBox()
        self.max_retries_spin.setRange(1, 10)
        self.max_retries_spin.setValue(config.MAX_RETRIES)
        layout.addWidget(self.max_retries_spin, 2, 1)

        group.setLayout(layout)
        return group

    def _on_indicator_changed(self):
        """Callback quand un indicateur principal change"""
        # Activer/désactiver groupes selon choix
        pass

    def _on_concurrency_changed(self, state):
        """Callback quand le mode parallèle change"""
        self.max_workers_spin.setEnabled(state == Qt.CheckState.Checked.value)

    def reset_to_defaults(self):
        """Réinitialise tous les paramètres aux valeurs par défaut"""
        # Recharger le module config
        import importlib

        importlib.reload(config)

        # Mettre à jour l'UI
        self.timeframe_combo.setCurrentText(config.TIMEFRAME)
        self.quote_combo.setCurrentText(config.QUOTE_FILTER)
        self.min_bars_spin.setValue(config.MIN_OHLCV_BARS)
        self.max_pairs_spin.setValue(config.MAX_PAIRS if config.MAX_PAIRS else 0)
        self.exclude_stables_check.setChecked(config.EXCLUDE_STABLE_PAIRS)

        self.use_rsi_check.setChecked(config.USE_RSI)
        self.use_ma_check.setChecked(config.USE_MA)
        self.use_macd_check.setChecked(config.USE_MACD)
        self.use_bollinger_check.setChecked(config.USE_BOLLINGER)
        self.use_stochastic_check.setChecked(config.USE_STOCHASTIC)

        self.rsi_period_spin.setValue(config.RSI_PERIOD)
        self.rsi_threshold_spin.setValue(config.RSI_THRESHOLD)

        self.use_confluence_check.setChecked(config.USE_CONFLUENCE_SCORE)
        self.min_confluence_spin.setValue(config.MIN_CONFLUENCE_SCORE)

        self.enable_concurrency_check.setChecked(config.ENABLE_CONCURRENCY)
        self.max_workers_spin.setValue(config.MAX_WORKERS)

        self.config_changed.emit()

    def save_config(self):
        """Sauvegarde la configuration modifiée dans config.py"""
        # Note: Cette fonction met à jour les variables en mémoire
        # Pour persister entre les sessions, il faudrait écrire dans le fichier

        config.TIMEFRAME = self.timeframe_combo.currentText()
        config.QUOTE_FILTER = self.quote_combo.currentText()
        config.MIN_OHLCV_BARS = self.min_bars_spin.value()
        max_pairs_val = self.max_pairs_spin.value()
        config.MAX_PAIRS = max_pairs_val if max_pairs_val > 0 else None
        config.EXCLUDE_STABLE_PAIRS = self.exclude_stables_check.isChecked()

        config.USE_RSI = self.use_rsi_check.isChecked()
        config.USE_MA = self.use_ma_check.isChecked()
        config.USE_MACD = self.use_macd_check.isChecked()
        config.USE_BOLLINGER = self.use_bollinger_check.isChecked()
        config.USE_STOCHASTIC = self.use_stochastic_check.isChecked()

        config.RSI_PERIOD = self.rsi_period_spin.value()
        config.RSI_THRESHOLD = self.rsi_threshold_spin.value()

        config.USE_SMA = self.use_sma_check.isChecked()
        config.USE_EMA = self.use_ema_check.isChecked()

        # Parser les périodes
        try:
            sma_text = self.sma_periods_edit.currentText()
            config.SMA_PERIODS = [
                int(x.strip()) for x in sma_text.split(",") if x.strip()
            ]
        except (ValueError, AttributeError):
            pass

        try:
            ema_text = self.ema_periods_edit.currentText()
            config.EMA_PERIODS = [
                int(x.strip()) for x in ema_text.split(",") if x.strip()
            ]
        except (ValueError, AttributeError):
            pass

        try:
            tf_text = self.ma_timeframes_edit.currentText()
            config.MA_TIMEFRAMES = [x.strip() for x in tf_text.split(",") if x.strip()]
        except AttributeError:
            pass

        config.MIN_TREND_SCORE = self.min_trend_score_spin.value()

        config.MACD_FAST_PERIOD = self.macd_fast_spin.value()
        config.MACD_SLOW_PERIOD = self.macd_slow_spin.value()
        config.MACD_SIGNAL_PERIOD = self.macd_signal_spin.value()
        config.BOLLINGER_STD_DEV = self.bb_std_spin.value()

        config.STOCHASTIC_K_PERIOD = self.stoch_k_spin.value()
        config.STOCHASTIC_D_PERIOD = self.stoch_d_spin.value()

        config.USE_CONFLUENCE_SCORE = self.use_confluence_check.isChecked()
        config.MIN_CONFLUENCE_SCORE = self.min_confluence_spin.value()

        config.CONFLUENCE_WEIGHTS["rsi"] = self.weight_rsi_spin.value()
        config.CONFLUENCE_WEIGHTS["trend"] = self.weight_trend_spin.value()
        config.CONFLUENCE_WEIGHTS["macd"] = self.weight_macd_spin.value()
        config.CONFLUENCE_WEIGHTS["bollinger"] = self.weight_bollinger_spin.value()
        config.CONFLUENCE_WEIGHTS["stochastic"] = self.weight_stochastic_spin.value()

        config.ENABLE_CONCURRENCY = self.enable_concurrency_check.isChecked()
        config.MAX_WORKERS = self.max_workers_spin.value()
        config.MAX_RETRIES = self.max_retries_spin.value()

        self.config_changed.emit()

    def get_current_config(self):
        """Retourne la configuration actuelle sous forme de dict"""
        return {
            "timeframe": self.timeframe_combo.currentText(),
            "quote_filter": self.quote_combo.currentText(),
            "use_rsi": self.use_rsi_check.isChecked(),
            "use_ma": self.use_ma_check.isChecked(),
            "rsi_threshold": self.rsi_threshold_spin.value(),
            "min_trend_score": self.min_trend_score_spin.value(),
            # ... autres paramètres
        }
