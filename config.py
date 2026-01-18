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
MAX_PAIRS = None  # Mode production

# ============================
# DONNÉES OHLCV
# ============================
TIMEFRAME = "4h"  # Timeframe pour le calcul du RSI
MIN_OHLCV_BARS = 200  # Nombre minimum de bougies à récupérer

# ============================
# INDICATEURS À UTILISER
# ============================
USE_RSI = False  # Activer le calcul et le filtrage RSI
USE_MA = True   # Activer le calcul des moyennes mobiles (SMA/EMA)

# ============================
# INDICATEUR RSI
# ============================
RSI_PERIOD = 14  # Période du RSI (standard)
RSI_THRESHOLD = 35  # Seuil de détection (RSI < threshold = survendu)

# ============================
# MOYENNES MOBILES (V1.5)
# ============================
# Note: USE_MA (ci-dessus) active/désactive le calcul des MA

# Types de moyennes mobiles à utiliser
USE_SMA = False   # Activer les SMA (Simple Moving Average)
USE_EMA = True   # Activer les EMA (Exponential Moving Average)

# Périodes pour chaque type de MA
SMA_PERIODS = [20, 50]  # Périodes des SMA (ex: [20, 50, 100, 200])
EMA_PERIODS = [20, 50]  # Périodes des EMA (ex: [12, 26, 50])

# Timeframes et paramètres communs
MA_TIMEFRAMES = ["1d", "4h", "1h"]  # Timeframes à analyser pour la détection de tendance haussière ( court terme: 4h, moyen terme: 1d, long terme: 1w)
MIN_TREND_SCORE = 3  # Score minimum de tendance haussière (0-3) pour filtrer les opportunités
MIN_MA_BARS = 60  # Nombre de bougies pour calculer les MA (max(periods) + marge)

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

# ============================
# CONCURRENCY (V2)
# ============================
ENABLE_CONCURRENCY = True  # Activer la parallélisation du scan (ThreadPoolExecutor)
MAX_WORKERS = 8  # Nombre de threads parallèles (5-10 recommandé pour respecter rate limits)
