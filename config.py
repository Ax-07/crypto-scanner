"""
Configuration globale du scanner RSI
Tous les paramètres sont centralisés ici.
"""

# ============================
# EXCHANGE
# ============================
EXCHANGE_ID = "binance"
EXCHANGE_SANDBOX = False  # Mode sandbox/testnet (non utilisé en V1)

# ============================
# UNIVERS DE SCAN
# ============================
QUOTE_FILTER = "USDC"  # Scanner uniquement les paires */USDC
MARKET_TYPE = "spot"  # Type de marché (spot uniquement en V1)
EXCLUDE_STABLE_PAIRS = True  # Exclure les paires stable/stable (ex: USDT/USDC)

# Limite de paires à scanner (utile pour le dev/test)
# None = scanner toutes les paires du scope
MAX_PAIRS = None

# ============================
# DONNÉES OHLCV
# ============================
TIMEFRAME = "4h"  # Timeframe pour le calcul du RSI
MIN_OHLCV_BARS = 200  # Nombre minimum de bougies à récupérer

# ============================
# INDICATEUR RSI
# ============================
RSI_PERIOD = 14  # Période du RSI (standard)
RSI_THRESHOLD = 35  # Seuil de détection (RSI < threshold = survendu)

# ============================
# MOYENNES MOBILES (V1.5)
# ============================
ENABLE_MA = True  # Activer l'analyse des moyennes mobiles
MA_PERIODS = [20, 50]  # Périodes des moyennes mobiles (SMA et EMA)
MA_TIMEFRAMES = ["1w", "1d", "4h"]  # Timeframes à analyser pour la détection de tendance
MIN_TREND_SCORE = 2  # Score minimum de tendance haussière (0-3) pour filtrer les opportunités
MIN_MA_BARS = 60  # Nombre de bougies pour calculer SMA50 (period + marge)

# ============================
# OUTPUT
# ============================
OUTPUT_CSV = True  # Activer l'export CSV
CSV_PATH = "outputs/rsi_scan.csv"  # Chemin du fichier CSV
CONSOLE_OUTPUT = True  # Afficher les résultats dans la console

# ============================
# LOGGING
# ============================
LOG_LEVEL = "INFO"  # Niveaux: DEBUG, INFO, WARNING, ERROR
LOG_FILE = "logs/scanner.log"  # Chemin du fichier de log
LOG_TO_CONSOLE = True  # Afficher les logs dans la console
LOG_TO_FILE = True  # Écrire les logs dans un fichier

# ============================
# RATE LIMITING & RETRIES
# ============================
ENABLE_RATE_LIMIT = True  # Activer la gestion automatique du rate limit par ccxt
MAX_RETRIES = 3  # Nombre maximum de tentatives en cas d'erreur réseau
RETRY_DELAY = 2  # Délai initial entre les tentatives (secondes) - doublé à chaque retry
