"""
Onglet Résultats - Affichage des opportunités détectées
Tableau interactif avec tri, filtres, et export
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QLineEdit,
    QHeaderView,
    QGroupBox,
    QComboBox,
    QFileDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
import pandas as pd
from datetime import datetime


class ResultsTab(QWidget):
    """
    Onglet d'affichage des résultats du scan
    Tableau avec les opportunités détectées + export
    """

    # Signal émis quand une paire est sélectionnée
    pair_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.results = []
        self.filtered_results = []
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface de l'onglet"""
        layout = QVBoxLayout()

        # === En-tête avec statistiques ===
        header_layout = QHBoxLayout()

        self.total_label = QLabel("Total: 0 opportunités")
        self.total_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(self.total_label)

        header_layout.addStretch()

        # Bouton export CSV
        self.export_button = QPushButton("📥 Exporter CSV")
        self.export_button.setObjectName("secondaryButton")
        self.export_button.clicked.connect(self.export_to_csv)
        self.export_button.setEnabled(False)
        header_layout.addWidget(self.export_button)

        # Bouton export Excel
        self.export_excel_button = QPushButton("📊 Exporter Excel")
        self.export_excel_button.setObjectName("secondaryButton")
        self.export_excel_button.clicked.connect(self.export_to_excel)
        self.export_excel_button.setEnabled(False)
        header_layout.addWidget(self.export_excel_button)

        layout.addLayout(header_layout)

        # === Filtres ===
        filters_group = QGroupBox("Filtres")
        filters_layout = QHBoxLayout()

        filters_layout.addWidget(QLabel("Rechercher:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Symbol, RSI, score...")
        self.search_input.textChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.search_input)

        filters_layout.addWidget(QLabel("Grade:"))
        self.grade_filter = QComboBox()
        self.grade_filter.addItems(["Tous", "A+", "A", "B", "C", "D", "F"])
        self.grade_filter.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.grade_filter)

        clear_filter_btn = QPushButton("✖ Effacer")
        clear_filter_btn.setObjectName("secondaryButton")
        clear_filter_btn.clicked.connect(self.clear_filters)
        filters_layout.addWidget(clear_filter_btn)

        filters_layout.addStretch()
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)

        # === Tableau ===
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(
            [
                "Symbol",
                "Score",
                "Grade",
                "RSI",
                "Tendance",
                "MACD",
                "Bollinger",
                "Stochastic",
                "Prix",
                "Date",
            ]
        )

        # Configurer colonnes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 10):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        # Activer tri
        self.table.setSortingEnabled(True)

        # Sélection ligne entière
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # Signal de sélection
        self.table.itemSelectionChanged.connect(self.on_selection_changed)

        layout.addWidget(self.table)

        # === Légende des grades ===
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("Légende:"))

        grades_info = [
            ("A+", "#4caf50"),
            ("A", "#8bc34a"),
            ("B", "#cddc39"),
            ("C", "#ffc107"),
            ("D", "#ff9800"),
            ("F", "#f44336"),
        ]

        for grade, color in grades_info:
            label = QLabel(f"  {grade}  ")
            label.setStyleSheet(
                f"background-color: {color}; color: white; "
                f"font-weight: bold; border-radius: 3px; padding: 2px 6px;"
            )
            legend_layout.addWidget(label)

        legend_layout.addStretch()
        layout.addLayout(legend_layout)

        self.setLayout(layout)

    def load_results(self, results):
        """Charge les résultats du scan dans le tableau"""
        self.results = results
        self.filtered_results = results.copy()

        # Activer boutons export
        self.export_button.setEnabled(len(results) > 0)
        self.export_excel_button.setEnabled(len(results) > 0)

        # Mettre à jour statistiques
        self.total_label.setText(f"Total: {len(results)} opportunités")

        # Remplir le tableau
        self.populate_table(results)

    def populate_table(self, results):
        """Remplit le tableau avec les résultats"""
        self.table.setRowCount(0)
        self.table.setSortingEnabled(False)

        for row_idx, result in enumerate(results):
            self.table.insertRow(row_idx)

            # Symbol
            symbol_item = QTableWidgetItem(result.get("symbol", "N/A"))
            symbol_item.setFlags(symbol_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_idx, 0, symbol_item)

            # Score (si V3 activée)
            score = result.get("confluence_score", 0)
            score_item = QTableWidgetItem(f"{score:.1f}")
            score_item.setFlags(score_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 1, score_item)

            # Grade avec couleur
            grade = result.get("confluence_grade", "-")
            grade_item = QTableWidgetItem(grade)
            grade_item.setFlags(grade_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            grade_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Couleur selon grade
            grade_colors = {
                "A+": QColor(76, 175, 80),
                "A": QColor(139, 195, 74),
                "B": QColor(205, 220, 57),
                "C": QColor(255, 193, 7),
                "D": QColor(255, 152, 0),
                "F": QColor(244, 67, 54),
            }
            if grade in grade_colors:
                grade_item.setBackground(grade_colors[grade])
                grade_item.setForeground(QColor(255, 255, 255))

            self.table.setItem(row_idx, 2, grade_item)

            # RSI
            rsi = result.get("rsi", 0)
            rsi_item = QTableWidgetItem(f"{rsi:.2f}")
            rsi_item.setFlags(rsi_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            rsi_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 3, rsi_item)

            # Tendance (score)
            trend_score = result.get("trend_score", 0)
            trend_item = QTableWidgetItem(f"{trend_score}/3")
            trend_item.setFlags(trend_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            trend_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 4, trend_item)

            # MACD signal
            macd_signal = result.get("macd_signal_type", "-")
            macd_item = QTableWidgetItem(macd_signal)
            macd_item.setFlags(macd_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            macd_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 5, macd_item)

            # Bollinger position
            bb_position = result.get("bb_position", "-")
            bb_item = QTableWidgetItem(bb_position)
            bb_item.setFlags(bb_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            bb_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 6, bb_item)

            # Stochastic signal
            stoch_signal = result.get("stoch_signal", "-")
            stoch_item = QTableWidgetItem(stoch_signal)
            stoch_item.setFlags(stoch_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            stoch_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 7, stoch_item)

            # Prix
            price = result.get("last_close_price", 0)
            price_item = QTableWidgetItem(f"${price:.6f}")
            price_item.setFlags(price_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            price_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.table.setItem(row_idx, 8, price_item)

            # Date
            timestamp = result.get("last_close_time", "")
            if timestamp:
                try:
                    # Convertir en string si c'est un objet pandas.Timestamp
                    timestamp_str = str(timestamp)
                    dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    date_str = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    # En cas d'erreur, utiliser la représentation string
                    date_str = str(timestamp)
            else:
                date_str = "-"

            date_item = QTableWidgetItem(str(date_str))
            date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 9, date_item)

        self.table.setSortingEnabled(True)
        # Trier par score décroissant par défaut
        self.table.sortItems(1, Qt.SortOrder.DescendingOrder)

    def apply_filters(self):
        """Applique les filtres de recherche et grade"""
        search_text = self.search_input.text().lower()
        grade_filter = self.grade_filter.currentText()

        filtered = self.results

        # Filtre recherche
        if search_text:
            filtered = [r for r in filtered if search_text in str(r).lower()]

        # Filtre grade
        if grade_filter != "Tous":
            filtered = [
                r for r in filtered if r.get("confluence_grade", "") == grade_filter
            ]

        self.filtered_results = filtered
        self.populate_table(filtered)
        self.total_label.setText(
            f"Affichage: {len(filtered)}/{len(self.results)} opportunités"
        )

    def clear_filters(self):
        """Efface tous les filtres"""
        self.search_input.clear()
        self.grade_filter.setCurrentText("Tous")

    def on_selection_changed(self):
        """Callback quand une ligne est sélectionnée"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return

        row = selected_rows[0].row()

        # Récupérer le symbol
        symbol = self.table.item(row, 0).text()

        # Trouver les données complètes
        result_data = None
        for result in self.filtered_results:
            if result.get("symbol") == symbol:
                result_data = result
                break

        if result_data:
            self.pair_selected.emit(result_data)

    def export_to_csv(self):
        """Exporte les résultats en CSV"""
        if not self.results:
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en CSV",
            f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)",
        )

        if filename:
            try:
                df = pd.DataFrame(self.results)
                df.to_csv(filename, index=False)
                self.total_label.setText(f"✅ Export CSV réussi: {filename}")
            except Exception as e:
                self.total_label.setText(f"❌ Erreur export: {str(e)}")

    def export_to_excel(self):
        """Exporte les résultats en Excel"""
        if not self.results:
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en Excel",
            f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)",
        )

        if filename:
            try:
                df = pd.DataFrame(self.results)
                df.to_excel(filename, index=False, engine="openpyxl")
                self.total_label.setText(f"✅ Export Excel réussi: {filename}")
            except Exception as e:
                self.total_label.setText(f"❌ Erreur export: {str(e)}")
