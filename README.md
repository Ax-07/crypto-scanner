# 🔍 Scanner Crypto Binance avec Interface Desktop

Scanner de marché crypto intelligent avec **interface PyQt6 professionnelle** qui détecte et **classe les opportunités de trading** en combinant **RSI**, **moyennes mobiles multi-timeframe** et **indicateurs techniques avancés** (MACD, Bollinger, Stochastic) dans un **score de confluence unique (0-100)** sur Binance.

⚠️ **MODE SCANNER UNIQUEMENT - AUCUN TRADING**

Ce projet est exclusivement un outil d'analyse de marché. Il ne contient aucune logique de trading, d'ordres ou de gestion de positions.

---

## 🖥️ Interface Desktop GUI (NOUVEAU !)

**Application PyQt6 professionnelle avec thème sombre élégant**

### 🚀 Lancement Rapide

```bash
# 1. Installer les dépendances GUI
python install_gui.py

# 2. Lancer l'interface
python gui_main.py
```

### 🎨 Fonctionnalités GUI

* **⚙️ Onglet Configuration** : Paramétrage complet du scanner (40+ paramètres)
* **🔍 Onglet Scanner** : Lancement et suivi en temps réel avec logs
* **📊 Onglet Résultats** : Tableau interactif avec tri, filtres et export CSV/Excel
* **📈 Onglet Détails** : Analyse approfondie d'une paire avec graphiques
* **🎨 Thème sombre professionnel** : Design élégant type plateforme de trading
* **⌨️ Raccourcis clavier** : F5 (scan), Esc (arrêt), Ctrl+Q (quitter)

📖 **Documentation complète** : [docs/GUI_README.md](docs/GUI_README.md)

---

## 📋 Fonctionnalités Scanner

### V1 - Base RSI

* Scan automatique de toutes les paires Binance (scope configurable)
* Calcul du RSI (Relative Strength Index)
* Détection des paires survendues (RSI < seuil)
* Export des résultats en CSV
* Affichage console formaté
* Gestion des erreurs et rate limits
* Logs détaillés

### V1.5 - Moyennes Mobiles Multi-Timeframe

* **Calcul des moyennes mobiles** (SMA et EMA) sur périodes 20 et 50
* **Analyse multi-timeframe** (Hebdo, Daily, H4)
* **Détection de tendance** haussière/baissière par timeframe
* **Trend Score (0-3)** : Nombre de timeframes haussiers
* **Filtre combiné** : RSI bas + tendance haussière
* **Export enrichi** avec 12 colonnes de moyennes mobiles

### V2 - Parallélisation (Concurrency) 🚀

* **ThreadPoolExecutor** pour traitement parallèle des paires
* **Gain de performance : 3-4x plus rapide** (testé sur 50 paires)
* **Gestion intelligente des workers** (5-10 threads, configurable)
* **Compatible avec rate limits** Binance
* **Mode séquentiel** toujours disponible (fallback)

### V2.5 - Multi-Indicateurs Techniques ✨ NEW

* **MACD (Moving Average Convergence Divergence)**
  * Détection de momentum (bullish/bearish)
  * Ligne MACD, Signal, Histogramme
  * Identification des croisements

* **Bollinger Bands (Bandes de Bollinger)**
  * Mesure de la volatilité
  * Détection de surachat/survente (overbought/oversold)
  * Bandes supérieure, moyenne, inférieure

* **Stochastic Oscillator**
  * Oscillateur de momentum (%K et %D)
  * Zones de survente (<20) et surachat (>80)
  * Détection de croisements haussiers/baissiers

* **12 nouvelles colonnes CSV** avec valeurs et signaux
* **Affichage console enrichi** avec signaux détectés
* **Activation/désactivation individuelle** de chaque indicateur

### V3 - Score de Confluence et Filtres Avancés 🎯 NEW

* **Score de Confluence (0-100)**
  * Agrégation pondérée de tous les indicateurs
  * Grades A+ à F pour classer les opportunités
  * Poids configurables par indicateur
  * Breakdown détaillé (score_rsi, score_trend, score_macd, etc.)

* **Filtres Avancés Multi-Indicateurs**
  * Filtrage AND sur signaux MACD/Bollinger/Stochastic
  * Stratégies personnalisables (ex: MACD bullish + BB oversold)
  * Élimination des faux signaux

* **Tri Intelligent**
  * Résultats triés par score décroissant
  * Meilleures opportunités en premier
  * Seuil minimum configurable (MIN_CONFLUENCE_SCORE)

* **Export Enrichi**
  * ~40 colonnes CSV avec scores détaillés
  * Analyse complète de chaque opportunité
  * Grades pour identification rapide

---

## 🛠️ Stack technique

* Python 3.10+
* CCXT (Binance API)
* Pandas / NumPy
* Lecture seule (données publiques)

---

## 📦 Installation

### 1. Cloner le projet

```bash
cd scanner_binance
```

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
```

### 3. Activer l'environnement virtuel

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux/Mac:**

```bash
source .venv/bin/activate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Tous les paramètres sont dans [config.py](config.py):

### Paramètres de base (V1)

| Paramètre       | Défaut                   | Description                            |
|-----------------|--------------------------|----------------------------------------|
| `TIMEFRAME`     | `"4h"`                   | Timeframe des bougies pour le RSI      |
| `RSI_PERIOD`    | `14`                     | Période du RSI                         |
| `RSI_THRESHOLD` | `35`                     | Seuil de détection (RSI < seuil)       |
| `QUOTE_FILTER`  | `"USDC"`                 | Scanner uniquement les paires */USDC   |
| `MAX_PAIRS`     | `None`                   | Limiter le nombre de paires (dev/test) |
| `OUTPUT_CSV`    | `True`                   | Activer l'export CSV                   |
| `CSV_PATH`      | `"outputs/rsi_scan.csv"` | Chemin du fichier CSV                  |

### Choix des indicateurs ✨ NEW

| Paramètre  | Défaut | Description                          |
|------------|--------|--------------------------------------|
| `USE_RSI`  | `True` | Activer le calcul et filtrage RSI    |
| `USE_MA`   | `True` | Activer les moyennes mobiles         |

### Concurrency / Performance 🚀 NEW

| Paramètre             | Défaut | Description                                      |
|-----------------------|--------|--------------------------------------------------|
| `ENABLE_CONCURRENCY`  | `True` | Activer la parallélisation (ThreadPoolExecutor)  |
| `MAX_WORKERS`         | `8`    | Nombre de threads parallèles (5-10 recommandé)   |

**Performance** :

* Mode séquentiel : ~0.8 paire/sec
* Mode parallèle (8 workers) : **~3-4 paires/sec** (gain 3-4x)

**Exemples de configurations** :

* `USE_RSI=True, USE_MA=False` : Scanner RSI uniquement (V1 classique)
* `USE_RSI=False, USE_MA=True` : Scanner tendance uniquement
* `USE_RSI=True, USE_MA=True` : Filtre combiné (V1.5 optimal)
* `USE_RSI=False, USE_MA=False` : Lister toutes les paires sans filtre

📖 Voir [docs/CONFIGURATIONS_EXEMPLES.md](docs/CONFIGURATIONS_EXEMPLES.md) pour 8 configurations détaillées

### Paramètres moyennes mobiles (V1.5)

| Paramètre         | Défaut                | Description                                    |
|-------------------|-----------------------|------------------------------------------------|
| `USE_SMA`         | `True`                | Activer les SMA (Simple Moving Average)        |
| `USE_EMA`         | `True`                | Activer les EMA (Exponential Moving Average)   |
| `SMA_PERIODS`     | `[20, 50]`            | Périodes des SMA                               |
| `EMA_PERIODS`     | `[20, 50]`            | Périodes des EMA                               |
| `MA_TIMEFRAMES`   | `["1w", "1d", "4h"]`  | Timeframes à analyser pour la tendance         |
| `MIN_TREND_SCORE` | `2`                   | Score minimum de tendance haussière (0-3)      |
| `MIN_MA_BARS`     | `60`                  | Nombre de bougies pour calculer les MA         |

**Exemples de configurations MA** :

* `USE_SMA=True, USE_EMA=False` : SMA uniquement (plus stable)
* `USE_SMA=False, USE_EMA=True` : EMA uniquement (plus réactif)
* `USE_SMA=True, USE_EMA=True` : Les deux (optimal) ⭐
* Périodes personnalisées : `SMA_PERIODS=[50,100,200]`, `EMA_PERIODS=[9,21]`

### Multi-Indicateurs (V2.5) 📊

```python
# MACD
USE_MACD = True
MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9

# BOLLINGER BANDS
USE_BOLLINGER = True
BOLLINGER_PERIOD = 20
BOLLINGER_STD_DEV = 2

# STOCHASTIC
USE_STOCHASTIC = True
STOCHASTIC_K_PERIOD = 14
STOCHASTIC_D_PERIOD = 3
STOCHASTIC_OVERSOLD = 20
STOCHASTIC_OVERBOUGHT = 80
```

**Modes d'utilisation** :

* `USE_MACD=True` : Activer MACD (momentum)
* `USE_BOLLINGER=True` : Activer Bollinger Bands (volatilité)
* `USE_STOCHASTIC=True` : Activer Stochastic (survente/surachat)
* Tous activés : Analyse complète multi-indicateurs 🎯

📖 Voir [docs/V2.5_RELEASE_NOTES.md](docs/V2.5_RELEASE_NOTES.md) pour détails complets

📖 Voir [docs/CONFIGURATION_MA.md](docs/CONFIGURATION_MA.md) pour 8 configurations MA détaillées

### Score de Confluence (V3) 🎯

```python
# Activation du scoring
USE_CONFLUENCE_SCORE = True
MIN_CONFLUENCE_SCORE = 60  # Seuil minimum (Grade C)

# Poids des indicateurs (total = 100)
CONFLUENCE_WEIGHTS = {
    'rsi': 20,          # RSI : 0-20 points
    'trend': 25,        # Tendance : 0-25 points
    'macd': 20,         # MACD : 0-20 points
    'bollinger': 20,    # Bollinger : 0-20 points
    'stochastic': 15    # Stochastic : 0-15 points
}

# Filtres avancés (None = désactivé)
FILTER_MACD_SIGNAL = None      # Ex: ['bullish']
FILTER_BB_POSITION = None      # Ex: ['oversold', 'near_oversold']
FILTER_STOCH_SIGNAL = None     # Ex: ['oversold', 'bullish_cross']
```

**Échelle de notation** :

| Score   | Grade | Interprétation            |
|---------|-------|---------------------------|
| 90-100  | A+    | Opportunité exceptionnelle|
| 80-89   | A     | Très bonne opportunité    |
| 70-79   | B     | Bonne opportunité         |
| 60-69   | C     | Opportunité acceptable    |
| 50-59   | D     | Opportunité faible        |
| 0-49    | F     | Opportunité insuffisante  |

**Exemples de stratégies** :

1. **Survente confirmée multi-indicateurs** :

   ```python
   FILTER_BB_POSITION = ['oversold', 'near_oversold']
   FILTER_STOCH_SIGNAL = ['oversold', 'bullish_cross']
   MIN_CONFLUENCE_SCORE = 70
   # Cible : rebonds techniques de qualité
   ```

2. **Momentum haussier fort** :

   ```python
   FILTER_MACD_SIGNAL = ['bullish']
   MIN_TREND_SCORE = 3  # 3/3 timeframes
   MIN_CONFLUENCE_SCORE = 80
   # Cible : tendances fortes établies
   ```

3. **Analyse exhaustive** :

   ```python
   MIN_CONFLUENCE_SCORE = 50
   # Pas de filtres, toutes opportunités avec breakdown
   ```

**Personnalisation des poids** :

```python
# Stratégie Trend-Following (accent sur tendance)
CONFLUENCE_WEIGHTS = {'rsi': 15, 'trend': 35, 'macd': 25, 'bollinger': 15, 'stochastic': 10}

# Stratégie Contrarian (accent sur RSI)
CONFLUENCE_WEIGHTS = {'rsi': 35, 'trend': 15, 'macd': 20, 'bollinger': 20, 'stochastic': 10}

# Stratégie Équilibrée (défaut)
CONFLUENCE_WEIGHTS = {'rsi': 20, 'trend': 25, 'macd': 20, 'bollinger': 20, 'stochastic': 15}
```

### Recommandations

**Configuration équilibrée (défaut)** :

```python
RSI_THRESHOLD = 35
MIN_TREND_SCORE = 2  # Au moins 2 timeframes haussiers
```

**Configuration stricte** :

```python
RSI_THRESHOLD = 30   # Survente forte
MIN_TREND_SCORE = 3  # Les 3 timeframes doivent être haussiers
```

**Configuration large** :

```python
RSI_THRESHOLD = 40-45
MIN_TREND_SCORE = 1
```

---

## 🚀 Utilisation

### Lancer le scanner

```bash
python main.py
```

### Résultats V3 avec Score de Confluence

**Console:**

```md
========================================================================================================================
RÉSULTATS DU SCAN - Score ≥ 60
OPPORTUNITÉS TRIÉES PAR SCORE (MEILLEURES EN PREMIER)
========================================================================================================================
 Symbole   RSI           Prix             Date TF  Score  Trend MACD     BB        Stoch
BTC/USDC 28.50 98500.00000000 2026-01-21 12:00 4h  85.0 (A)    3  bullish oversold  bullish_cross
ETH/USDC 32.15  3250.00000000 2026-01-21 12:00 4h  78.5 (B)    3  bullish near_os   oversold
XRP/USDC 34.20     2.10000000 2026-01-21 12:00 4h  72.0 (B)    2  neutral oversold  neutral
========================================================================================================================
Total: 3 paire(s) | Moyenne score: 78.5
========================================================================================================================

📁 Fichier CSV créé: outputs/rsi_scan.csv
```

**Interprétation** :

* **Score** : Note de confluence 0-100 avec grade (A+, A, B, C, D, F)
* **Trend** : Score de tendance (nombre de timeframes haussiers sur 3)
* **MACD** : Signal MACD (bullish/neutral/bearish)
* **BB** : Position Bollinger Bands (oversold/near_os/neutral/near_ob/overbought)
* **Stoch** : Signal Stochastic (oversold/bullish_cross/neutral/bearish_cross/overbought)
* Plus le score est élevé, plus l'opportunité est forte

**CSV (~40 colonnes):**

Le fichier contient les colonnes suivantes:

**Colonnes de base (V1)** :

* `symbol`: Nom de la paire
* `rsi`: Valeur du RSI
* `last_close_price`: Prix de clôture
* `last_close_time`: Date/heure de la bougie
* `timeframe`: Timeframe utilisé

**Colonnes moyennes mobiles (V1.5)** :

* `trend_score`: Score global (0-3)
* `sma20_1w`, `sma50_1w`: SMA hebdomadaire
* `ema20_1w`, `ema50_1w`: EMA hebdomadaire
* `trend_1w`: Tendance hebdo (True/False)
* `sma20_1d`, `sma50_1d`: SMA daily
* `ema20_1d`, `ema50_1d`: EMA daily
* `trend_1d`: Tendance daily (True/False)
* `sma20_4h`, `sma50_4h`: SMA 4h
* `ema20_4h`, `ema50_4h`: EMA 4h
* `trend_4h`: Tendance 4h (True/False)

**Colonnes multi-indicateurs (V2.5)** :

* `macd`, `macd_signal`, `macd_histogram`: Valeurs MACD
* `macd_signal_type`: Signal détecté (bullish/neutral/bearish)
* `bb_upper`, `bb_middle`, `bb_lower`: Bandes de Bollinger
* `bb_position`: Position (oversold/near_oversold/neutral/near_overbought/overbought)
* `stoch_k`, `stoch_d`: Valeurs Stochastic
* `stoch_signal`: Signal détecté (oversold/bullish_cross/neutral/bearish_cross/overbought)

**Colonnes confluence (V3)** 🎯 :

* `confluence_score`: Score total 0-100
* `confluence_grade`: Grade (A+, A, B, C, D, F)
* `score_rsi`: Points RSI (0-20)
* `score_trend`: Points tendance (0-25)
* `score_macd`: Points MACD (0-20)
* `score_bollinger`: Points Bollinger (0-20)
* `score_stochastic`: Points Stochastic (0-15)

**Métadonnées** :

* `rsi_period`: Période RSI
* `rsi_threshold`: Seuil RSI
* `scan_date`: Date du scan

---

## 📁 Structure du projet

```md
scanner_binance/
├── config.py                # Configuration centralisée (+ V3)
├── logger.py                # Système de logging
├── exchange.py              # Initialisation CCXT + filtrage paires
├── data.py                  # Récupération OHLCV
├── indicators.py            # RSI + MA + Multi-indicateurs + Confluence (V3)
├── scanner.py               # Logique principale + filtres + scoring (V3)
├── output.py                # Affichage et export enrichi (V3)
├── main.py                  # Point d'entrée CLI
│
├── test_modules.py          # Tests unitaires base
├── test_confluence.py       # Tests unitaires V3 (scoring + filtres)
├── test_scanner_v3.py       # Test intégration V3
├── test_configurations.py   # Tests configurations indicateurs
│
├── requirements.txt         # Dépendances Python
├── .gitignore
├── .env.example
│
├── docs/                    # Documentation
│   ├── cahier_des_charges_scanner.md  # Cahier des charges complet (V3)
│   ├── V1.5_RELEASE_NOTES.md
│   ├── V2.5_RELEASE_NOTES.md
│   ├── CONFIGURATION_MA.md
│   ├── CONFIGURATIONS_EXEMPLES.md
│   └── copilot-instructions*.md
│
├── logs/                    # Fichiers de log
│   └── scanner.log
│
└── outputs/                 # Résultats CSV
    └── rsi_scan.csv         # ~40 colonnes avec scores V3
```

---

## 📝 Logs

Les logs sont disponibles dans:

* **Console** (si activé dans config)
* **Fichier**: `logs/scanner.log`

---

## 🔒 Sécurité

* Ce scanner utilise uniquement l'API **publique** de Binance
* **Aucune clé API n'est nécessaire**
* Aucune opération de trading n'est possible
* Mode **lecture seule**

---

## ⚠️ Limites et contraintes

* **Scan uniquement** (pas de trading)
* Lecture seule des données publiques Binance
* Rate limits Binance (gérés automatiquement)
* Scoring basé sur données historiques (non prédictif)

---

## 🚀 Évolutions futures (V4+)

* ✅ ~~Concurrency (V2)~~ - FAIT
* ✅ ~~Multi-indicateurs (V2.5)~~ - FAIT
* ✅ ~~Score de confluence (V3)~~ - FAIT
* ✅ ~~Filtres avancés (V3)~~ - FAIT
* Notifications push (Telegram/Discord) pour scores A/A+
* Indicateurs additionnels (ADX, ATR, Volume Profile, Ichimoku)
* Backtesting du système de scoring
* Dashboard web interactif (Flask/FastAPI)
* API REST pour intégration externe
* Alertes temps réel (WebSocket)

---

## 📄 Licence

Projet privé - Outil d'analyse uniquement

---

## ❓ Support

Consultez le [cahier des charges](docs/cahier_des_charges_scanner.md) pour plus de détails sur le projet.
