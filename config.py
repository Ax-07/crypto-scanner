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
USE_RSI = True  # Activer le calcul et le filtrage RSI
USE_MA = True  # Activer le calcul des moyennes mobiles (SMA/EMA)

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
USE_SMA = True  # Activer les SMA (Simple Moving Average)
USE_EMA = True  # Activer les EMA (Exponential Moving Average)

# Périodes pour chaque type de MA
SMA_PERIODS = [20, 50]  # Périodes des SMA (ex: [20, 50, 100, 200])
EMA_PERIODS = [20, 50]  # Périodes des EMA (ex: [12, 26, 50])

# Timeframes et paramètres communs
MA_TIMEFRAMES = [
    "1w",
    "1d",
    "4h",
]  # Timeframes à analyser pour la détection de tendance haussière ( court terme: 4h, moyen terme: 1d, long terme: 1w)
MIN_TREND_SCORE = (
    2  # Score minimum de tendance haussière (0-3) pour filtrer les opportunités
)
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
MAX_WORKERS = (
    8  # Nombre de threads parallèles (5-10 recommandé pour respecter rate limits)
)


# ============================
# MULTI-INDICATEURS (V2.5)
# ============================

# === MACD (Moving Average Convergence Divergence) ===
USE_MACD = True
MACD_FAST_PERIOD = 12  # Période EMA rapide
MACD_SLOW_PERIOD = 26  # Période EMA lente
MACD_SIGNAL_PERIOD = 9  # Période ligne de signal

# === BOLLINGER BANDS ===
USE_BOLLINGER = True
BOLLINGER_PERIOD = 20  # Période de la bande moyenne (SMA)
BOLLINGER_STD_DEV = 2  # Nombre d'écarts-types

# === STOCHASTIC OSCILLATOR ===
USE_STOCHASTIC = True
STOCHASTIC_K_PERIOD = 14  # Période %K
STOCHASTIC_D_PERIOD = 3  # Période %D (moyenne de %K)
STOCHASTIC_OVERSOLD = 20  # Seuil de survente
STOCHASTIC_OVERBOUGHT = 80  # Seuil de surachat

# ============================
# CONFLUENCE & FILTRES AVANCÉS (V3)
# ============================

# === SCORE DE CONFLUENCE ===
USE_CONFLUENCE_SCORE = True  # Activer le calcul du score de confluence
MIN_CONFLUENCE_SCORE = 60  # Score minimum pour valider une opportunité (0-100)

# Pondérations des indicateurs dans le score (total = 100)
CONFLUENCE_WEIGHTS = {
    'rsi': 20,          # RSI : 20% du score
    'trend': 25,        # Tendance MA : 25% du score
    'macd': 20,         # MACD : 20% du score
    'bollinger': 20,    # Bollinger : 20% du score
    'stochastic': 15    # Stochastic : 15% du score
}

# === FILTRES AVANCÉS SUR SIGNAUX ===
# Filtrer uniquement certains signaux (laisser None ou [] pour désactiver le filtre)

# Filtre MACD : Accepter uniquement ces signaux
# Options: 'bullish', 'bearish', 'neutral'
FILTER_MACD_SIGNAL = None  # Ex: ['bullish'] pour signaux haussiers uniquement
# FILTER_MACD_SIGNAL = ['bullish']  # Décommenter pour activer

# Filtre Bollinger : Accepter uniquement ces positions
# Options: 'oversold', 'near_oversold', 'neutral', 'near_overbought', 'overbought'
FILTER_BB_POSITION = None  # Ex: ['oversold', 'near_oversold'] pour survente uniquement
# FILTER_BB_POSITION = ['oversold', 'near_oversold']  # Décommenter pour activer

# Filtre Stochastic : Accepter uniquement ces signaux
# Options: 'oversold', 'overbought', 'bullish_cross', 'bearish_cross', 'neutral'
FILTER_STOCH_SIGNAL = None  # Ex: ['oversold', 'bullish_cross'] pour signaux d'achat uniquement
# FILTER_STOCH_SIGNAL = ['oversold', 'bullish_cross']  # Décommenter pour activer
