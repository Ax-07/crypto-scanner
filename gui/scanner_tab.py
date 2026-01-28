"""
Onglet Scanner - Lancement et suivi du scan
Affiche progression, logs temps réel, et statistiques
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QProgressBar,
    QLabel,
    QTextEdit,
    QGroupBox,
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QTextCursor
import time


class ScanWorker(QThread):
    """
    Worker thread pour exécuter le scan sans bloquer l'UI
    """

    # Signaux
    progress = pyqtSignal(int, int)  # current, total
    log_message = pyqtSignal(str)
    scan_completed = pyqtSignal(list, object)  # results, exchange
    scan_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.should_stop = False

    def run(self):
        """Exécute le scan dans un thread séparé"""
        try:
            self.log_message.emit("🚀 Initialisation du scanner...")

            # Import de l'adaptateur
            from gui.scanner_adapter import run_scan

            self.log_message.emit("📡 Connexion à Binance...")

            # Lancer le scan avec callbacks
            self.log_message.emit("🔍 Début du scan...")
            start_time = time.time()

            results, exchange_instance = run_scan(
                exchange_instance=None,  # L'adaptateur créera l'instance
                progress_callback=self._on_progress,
                log_callback=self._on_log,
            )

            elapsed = time.time() - start_time

            self.log_message.emit(f"\n✅ Scan terminé en {elapsed:.1f}s")
            self.log_message.emit(f"📊 {len(results)} opportunités trouvées")

            self.scan_completed.emit(results, exchange_instance)

        except Exception as e:
            self.log_message.emit(f"\n❌ Erreur: {str(e)}")
            self.scan_error.emit(str(e))

    def _on_progress(self, current, total):
        """Callback progression"""
        if not self.should_stop:
            self.progress.emit(current, total)

    def _on_log(self, message):
        """Callback log"""
        if not self.should_stop:
            self.log_message.emit(message)

    def stop(self):
        """Arrête le scan proprement"""
        self.should_stop = True


class ScannerTab(QWidget):
    """
    Onglet de contrôle du scanner
    Permet de lancer un scan et suivre sa progression
    """

    # Signal émis quand scan terminé (results, exchange_instance)
    scan_finished = pyqtSignal(list, object)

    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface de l'onglet"""
        layout = QVBoxLayout()

        # === Contrôles ===
        controls_group = QGroupBox("Contrôles")
        controls_layout = QHBoxLayout()

        self.start_button = QPushButton("▶ Lancer le Scan")
        self.start_button.setObjectName("successButton")
        self.start_button.setMinimumHeight(50)
        self.start_button.clicked.connect(self.start_scan)

        self.stop_button = QPushButton("⏹ Arrêter")
        self.stop_button.setObjectName("dangerButton")
        self.stop_button.setMinimumHeight(50)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_scan)

        controls_layout.addWidget(self.start_button, 3)
        controls_layout.addWidget(self.stop_button, 1)
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        # === Progression ===
        progress_group = QGroupBox("Progression")
        progress_layout = QVBoxLayout()

        self.progress_label = QLabel("En attente...")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # === Statistiques ===
        stats_group = QGroupBox("Statistiques")
        stats_layout = QHBoxLayout()

        self.pairs_scanned_label = QLabel("Paires scannées: 0")
        self.opportunities_label = QLabel("Opportunités: 0")
        self.speed_label = QLabel("Vitesse: -")

        stats_layout.addWidget(self.pairs_scanned_label)
        stats_layout.addWidget(self.opportunities_label)
        stats_layout.addWidget(self.speed_label)
        stats_layout.addStretch()

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # === Logs ===
        logs_group = QGroupBox("Logs temps réel")
        logs_layout = QVBoxLayout()

        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setMaximumHeight(250)
        logs_layout.addWidget(self.logs_text)

        # Bouton clear logs
        clear_logs_btn = QPushButton("Effacer logs")
        clear_logs_btn.setObjectName("secondaryButton")
        clear_logs_btn.clicked.connect(self.clear_logs)
        logs_layout.addWidget(clear_logs_btn)

        logs_group.setLayout(logs_layout)
        layout.addWidget(logs_group)

        layout.addStretch()
        self.setLayout(layout)

    def start_scan(self):
        """Lance le scan dans un thread séparé"""
        if self.worker and self.worker.isRunning():
            self.add_log("⚠️ Un scan est déjà en cours")
            return

        # Réinitialiser UI
        self.progress_bar.setValue(0)
        self.progress_label.setText("Démarrage...")
        self.pairs_scanned_label.setText("Paires scannées: 0")
        self.opportunities_label.setText("Opportunités: 0")
        self.speed_label.setText("Vitesse: -")

        # Activer/désactiver boutons
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # Créer et lancer worker
        self.worker = ScanWorker()
        self.worker.progress.connect(self.update_progress)
        self.worker.log_message.connect(self.add_log)
        self.worker.scan_completed.connect(self.on_scan_completed)
        self.worker.scan_error.connect(self.on_scan_error)
        self.worker.start()

        self.add_log("\n" + "=" * 60)
        self.add_log(f"🚀 Nouveau scan lancé - {time.strftime('%H:%M:%S')}")
        self.add_log("=" * 60 + "\n")

    def stop_scan(self):
        """Arrête le scan en cours"""
        if self.worker and self.worker.isRunning():
            self.add_log("\n⏹ Arrêt du scan demandé...")
            self.worker.stop()
            self.worker.wait()

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_label.setText("Scan arrêté")

    def update_progress(self, current, total):
        """Met à jour la barre de progression"""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.progress_label.setText(
                f"Scan en cours: {current}/{total} paires ({percentage}%)"
            )
            self.pairs_scanned_label.setText(f"Paires scannées: {current}")

    def add_log(self, message):
        """Ajoute un message aux logs"""
        self.logs_text.append(message)
        # Auto-scroll vers le bas
        cursor = self.logs_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.logs_text.setTextCursor(cursor)

    def clear_logs(self):
        """Efface tous les logs"""
        self.logs_text.clear()

    def on_scan_completed(self, results, exchange_instance):
        """Callback quand le scan est terminé avec succès"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setValue(100)
        self.progress_label.setText(f"✅ Scan terminé - {len(results)} opportunités")
        self.opportunities_label.setText(f"Opportunités: {len(results)}")

        # Émettre signal pour onglet résultats (avec exchange)
        self.scan_finished.emit(results, exchange_instance)

    def on_scan_error(self, error_msg):
        """Callback quand le scan échoue"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_label.setText("❌ Erreur lors du scan")
        self.add_log(f"\n❌ ERREUR: {error_msg}")
