"""
Styles et thème pour l'application PyQt6
Thème sombre professionnel inspiré des plateformes de trading modernes
"""


def get_dark_theme():
    """
    Retourne le style QSS (Qt Style Sheet) pour le thème sombre amélioré
    Palette de couleurs inspirée de Binance, TradingView et VS Code Dark+
    """
    return """
    /* ============================================================
       PALETTE DE COULEURS
       ============================================================
       Fond principal: #0b0e11
       Fond secondaire: #161a1e
       Fond carte: #1e2329
       Bordures: #2b3139
       Accent principal (bleu crypto): #f0b90b (gold) / #0ecb81 (green)
       Texte principal: #eaecef
       Texte secondaire: #848e9c
       Succès: #0ecb81
       Danger: #f6465d
       Warning: #f0b90b
    ============================================================ */
    
    /* Application principale */
    QMainWindow, QDialog {
        background-color: #0b0e11;
        color: #eaecef;
    }
    
    /* Onglets - Design moderne */
    QTabWidget::pane {
        border: 1px solid #2b3139;
        background-color: #161a1e;
        border-radius: 8px;
        margin-top: -1px;
    }
    
    QTabBar::tab {
        background-color: #1e2329;
        color: #848e9c;
        padding: 12px 24px;
        border: 1px solid #2b3139;
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        margin-right: 4px;
        font-size: 13px;
        font-weight: 600;
        min-width: 100px;
    }
    
    QTabBar::tab:selected {
        background-color: #161a1e;
        color: #f0b90b;
        border-bottom: 3px solid #f0b90b;
        padding-bottom: 9px;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #2b3139;
        color: #eaecef;
    }
    
    /* Labels - Typographie améliorée */
    QLabel {
        color: #eaecef;
        font-size: 12px;
        padding: 1px;
    }
    
    /* Boutons - Design moderne avec dégradés */
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #f0b90b, stop:1 #d4a00a);
        color: #0b0e11;
        border: none;
        padding: 8px 18px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
        min-height: 32px;
    }
    
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #fcd535, stop:1 #f0b90b);
    }
    
    QPushButton:pressed {
        background: #d4a00a;
        padding-top: 12px;
        padding-bottom: 8px;
    }
    
    QPushButton:disabled {
        background-color: #2b3139;
        color: #474d57;
    }
    
    /* Bouton secondaire - Style outline */
    QPushButton#secondaryButton {
        background-color: transparent;
        color: #848e9c;
        border: 2px solid #2b3139;
    }
    
    QPushButton#secondaryButton:hover {
        background-color: #1e2329;
        border-color: #848e9c;
        color: #eaecef;
    }
    
    QPushButton#secondaryButton:pressed {
        background-color: #2b3139;
    }
    
    /* Bouton danger - Rouge vif */
    QPushButton#dangerButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #f6465d, stop:1 #d63649);
        color: #ffffff;
    }
    
    QPushButton#dangerButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #ff6b7a, stop:1 #f6465d);
    }
    
    /* Bouton succès - Vert crypto */
    QPushButton#successButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #0ecb81, stop:1 #0bb871);
        color: #ffffff;
    }
    
    QPushButton#successButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #2edf9a, stop:1 #0ecb81);
    }
    
    /* Champs de texte - Style moderne */
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
        background-color: #1e2329;
        color: #eaecef;
        border: 1px solid #2b3139;
        border-radius: 4px;
        padding: 6px 10px;
        font-size: 12px;
        min-height: 28px;
    }
    
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
        border: 2px solid #f0b90b;
        background-color: #252930;
    }
    
    QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {
        border-color: #474d57;
    }
    
    QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QComboBox:disabled {
        background-color: #161a1e;
        color: #474d57;
        border-color: #2b3139;
    }
    
    /* SpinBox - Boutons + et - stylisés */
    QSpinBox::up-button, QDoubleSpinBox::up-button {
        background-color: #2b3139;
        border: none;
        border-top-right-radius: 6px;
        width: 20px;
    }
    
    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
        background-color: #474d57;
    }
    
    QSpinBox::down-button, QDoubleSpinBox::down-button {
        background-color: #2b3139;
        border: none;
        border-bottom-right-radius: 6px;
        width: 20px;
    }
    
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
        background-color: #474d57;
    }
    
    /* ComboBox - Dropdown moderne */
    QComboBox::drop-down {
        border: none;
        width: 30px;
        background-color: #2b3139;
        border-top-right-radius: 6px;
        border-bottom-right-radius: 6px;
    }
    
    QComboBox::drop-down:hover {
        background-color: #474d57;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 7px solid #848e9c;
        margin-right: 8px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #1e2329;
        color: #eaecef;
        selection-background-color: #f0b90b;
        selection-color: #0b0e11;
        border: 1px solid #2b3139;
        border-radius: 6px;
        padding: 4px;
    }
    
    QComboBox QAbstractItemView::item {
        padding: 8px;
        border-radius: 4px;
    }
    
    QComboBox QAbstractItemView::item:hover {
        background-color: #2b3139;
    }
    
    /* CheckBox - Style moderne */
    QCheckBox {
        color: #eaecef;
        spacing: 8px;
        font-size: 12px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 3px;
        border: 2px solid #2b3139;
        background-color: #1e2329;
    }
    
    QCheckBox::indicator:hover {
        border-color: #f0b90b;
        background-color: #252930;
    }
    
    QCheckBox::indicator:checked {
        background-color: #f0b90b;
        border: 2px solid #f0b90b;
        image: none;
    }
    
    QCheckBox::indicator:checked:hover {
        background-color: #fcd535;
        border-color: #fcd535;
    }
    
    QCheckBox:disabled {
        color: #474d57;
    }
    
    QCheckBox::indicator:disabled {
        background-color: #161a1e;
        border-color: #2b3139;
    }
    
    /* Widget général */
    QWidget {
        background-color: #161a1e;
        color: #eaecef;
    }
    
    /* ScrollArea - Design épuré */
    QScrollArea {
        background-color: #161a1e;
        border: none;
    }
    
    QScrollArea > QWidget > QWidget {
        background-color: #161a1e;
    }
    
    /* GroupBox - Style carte moderne */
    QGroupBox {
        color: #eaecef;
        border: 1px solid #2b3139;
        border-radius: 6px;
        margin-top: 12px;
        padding: 12px 10px 10px 10px;
        font-weight: 600;
        font-size: 13px;
        background-color: #1e2329;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 4px 10px;
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 #f0b90b, stop:1 #fcd535);
        color: #0b0e11;
        border-radius: 4px;
        font-weight: bold;
        font-size: 12px;
        left: 8px;
    }
    
    /* TableWidget - Style professionnel */
    QTableWidget {
        background-color: #161a1e;
        color: #eaecef;
        gridline-color: #2b3139;
        border: 1px solid #2b3139;
        border-radius: 8px;
        selection-background-color: #2b3139;
        alternate-background-color: #1a1e23;
    }
    
    QTableWidget::item {
        padding: 10px;
        border-bottom: 1px solid #2b3139;
    }
    
    QTableWidget::item:selected {
        background-color: #2b3139;
        color: #f0b90b;
    }
    
    QTableWidget::item:hover {
        background-color: #1e2329;
    }
    
    QHeaderView::section {
        background-color: #1e2329;
        color: #848e9c;
        padding: 12px;
        border: none;
        border-right: 1px solid #2b3139;
        border-bottom: 2px solid #2b3139;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
    }
    
    QHeaderView::section:hover {
        background-color: #252930;
        color: #eaecef;
    }
    
    QHeaderView::section:first {
        border-top-left-radius: 8px;
    }
    
    QHeaderView::section:last {
        border-top-right-radius: 8px;
        border-right: none;
    }
    
    /* ScrollBar - Style minimaliste */
    QScrollBar:vertical {
        background-color: #0b0e11;
        width: 12px;
        margin: 0px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #2b3139;
        min-height: 30px;
        border-radius: 6px;
        margin: 2px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #474d57;
    }
    
    QScrollBar::handle:vertical:pressed {
        background-color: #f0b90b;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QScrollBar:horizontal {
        background-color: #0b0e11;
        height: 12px;
        margin: 0px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #2b3139;
        min-width: 30px;
        border-radius: 6px;
        margin: 2px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #474d57;
    }
    
    QScrollBar::handle:horizontal:pressed {
        background-color: #f0b90b;
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    
    /* ProgressBar - Design crypto */
    QProgressBar {
        background-color: #1e2329;
        border: 1px solid #2b3139;
        border-radius: 6px;
        text-align: center;
        color: #eaecef;
        font-weight: bold;
        font-size: 12px;
        min-height: 24px;
    }
    
    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 #f0b90b, stop:1 #fcd535);
        border-radius: 5px;
    }
    
    /* TextEdit - Console style */
    QTextEdit, QPlainTextEdit {
        background-color: #0b0e11;
        color: #eaecef;
        border: 1px solid #2b3139;
        border-radius: 8px;
        padding: 12px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 12px;
        line-height: 1.5;
    }
    
    QTextEdit:focus, QPlainTextEdit:focus {
        border-color: #f0b90b;
    }
    
    /* MenuBar - Style moderne */
    QMenuBar {
        background-color: #1e2329;
        color: #eaecef;
        border-bottom: 1px solid #2b3139;
        padding: 4px;
    }
    
    QMenuBar::item {
        padding: 8px 16px;
        background-color: transparent;
        border-radius: 4px;
    }
    
    QMenuBar::item:selected {
        background-color: #2b3139;
        color: #f0b90b;
    }
    
    QMenu {
        background-color: #1e2329;
        color: #eaecef;
        border: 1px solid #2b3139;
        border-radius: 6px;
        padding: 4px;
    }
    
    QMenu::item {
        padding: 8px 32px 8px 16px;
        border-radius: 4px;
    }
    
    QMenu::item:selected {
        background-color: #f0b90b;
        color: #0b0e11;
    }
    
    QMenu::separator {
        height: 1px;
        background-color: #2b3139;
        margin: 4px 8px;
    }
    
    /* StatusBar - Barre de statut moderne */
    QStatusBar {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 #1e2329, stop:1 #161a1e);
        color: #848e9c;
        border-top: 1px solid #2b3139;
        font-size: 11px;
        padding: 4px;
    }
    
    QStatusBar::item {
        border: none;
    }
    
    /* Tooltips - Design élégant */
    QToolTip {
        background-color: #1e2329;
        color: #eaecef;
        border: 1px solid #f0b90b;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
    }
    
    /* Séparateur */
    QSplitter::handle {
        background-color: #2b3139;
    }
    
    QSplitter::handle:hover {
        background-color: #f0b90b;
    }
    
    /* Messages d'information */
    QMessageBox {
        background-color: #1e2329;
    }
    
    QMessageBox QLabel {
        color: #eaecef;
        font-size: 13px;
    }
    """


def get_light_theme():
    """
    Retourne le style QSS pour le thème clair (optionnel)
    """
    return """
    /* Thème clair - À implémenter si nécessaire */
    QMainWindow {
        background-color: #ffffff;
    }
    
    QLabel {
        color: #1e1e1e;
    }
    """
