# 🔍 Scanner RSI + Moyennes Mobiles Binance

Scanner de marché crypto qui détecte les opportunités de trading en combinant **RSI** et **analyse multi-timeframe des moyennes mobiles** sur Binance.

⚠️ **MODE SCANNER UNIQUEMENT - AUCUN TRADING**

Ce projet est exclusivement un outil d'analyse de marché. Il ne contient aucune logique de trading, d'ordres ou de gestion de positions.

---

## 📋 Fonctionnalités

### V1 - Base RSI

* Scan automatique de toutes les paires Binance (scope configurable)
* Calcul du RSI (Relative Strength Index)
* Détection des paires survendues (RSI < seuil)
* Export des résultats en CSV
* Affichage console formaté
* Gestion des erreurs et rate limits
* Logs détaillés

### V1.5 - Moyennes Mobiles Multi-Timeframe ✨ NEW

* **Calcul des moyennes mobiles** (SMA et EMA) sur périodes 20 et 50
* **Analyse multi-timeframe** (Hebdo, Daily, H4)
* **Détection de tendance** haussière/baissière par timeframe
* **Trend Score (0-3)** : Nombre de timeframes haussiers
* **Filtre combiné** : RSI bas + tendance haussière
* **Export enrichi** avec 12 colonnes de moyennes mobiles

### V2 - Parallélisation (Concurrency) 🚀 NEW

* **ThreadPoolExecutor** pour traitement parallèle des paires
* **Gain de performance : 3-4x plus rapide** (testé sur 50 paires)
* **Gestion intelligente des workers** (5-10 threads, configurable)
* **Compatible avec rate limits** Binance
* **Mode séquentiel** toujours disponible (fallback)

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

📖 Voir [docs/CONFIGURATION_MA.md](docs/CONFIGURATION_MA.md) pour 8 configurations MA détaillées

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

### Résultats V1.5

**Console:**

```md
========================================================================================================================
RÉSULTATS DU SCAN - RSI < 35
TENDANCE HAUSSIÈRE ≥ 2/3 timeframes
========================================================================================================================
 Symbole   RSI           Prix             Date TF  Trend 1W 1D 4H
XRP/USDC 32.15     2.05400000 2026-01-17 16:00 4h      2  ✗  ✓  ✓
BTC/USDC 34.82 95000.00000000 2026-01-17 16:00 4h      3  ✓  ✓  ✓
========================================================================================================================
Total: 2 paire(s)
========================================================================================================================

📁 Fichier CSV créé: outputs/rsi_scan.csv
```

**Interprétation** :

* **Trend** : Score de tendance (nombre de timeframes haussiers sur 3)
* **✓** : Tendance haussière sur ce timeframe
* **✗** : Tendance baissière sur ce timeframe
* Plus le trend_score est élevé, plus l'opportunité est forte

**CSV (24 colonnes):**

```csv
symbol,rsi,last_close_price,last_close_time,timeframe,trend_score,
sma20_1w,ema20_1w,sma50_1w,ema50_1w,trend_1w,
sma20_1d,ema20_1d,sma50_1d,ema50_1d,trend_1d,
sma20_4h,ema20_4h,sma50_4h,ema50_4h,trend_4h,
rsi_period,rsi_threshold,scan_date
```

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

**Métadonnées** :

* `rsi_period`: Période RSI
* `rsi_threshold`: Seuil RSI
* `scan_date`: Date du scan

---

## 📁 Structure du projet

```md
scanner_binance/
├── config.py           # Configuration centralisée
├── logger.py           # Système de logging
├── exchange.py         # Initialisation CCXT + filtrage paires
├── data.py             # Récupération OHLCV
├── indicators.py       # Calcul RSI + SMA/EMA (V1.5)
├── scanner.py          # Logique principale du scan + analyse multi-timeframe
├── output.py           # Affichage et export (enrichi V1.5)
├── main.py             # Point d'entrée CLI
├── test_modules.py     # Tests unitaires
│
├── requirements.txt    # Dépendances Python
├── .gitignore
├── .env.example
│
├── docs/               # Documentation
│   ├── cahier_des_charges_scanner.md
│   ├── V1.5_RELEASE_NOTES.md
│   └── copilot-instruction.md
│
├── logs/               # Fichiers de log
│   └── scanner.log
│
└── outputs/            # Résultats CSV
    └── rsi_scan.csv
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
* Timeframe unique par exécution
* RSI comme seul indicateur en V1
* Rate limits Binance (gérés automatiquement)

---

## 🚀 Évolutions futures (V3)

* Scan multi-timeframes simultanés
* Notifications (Telegram/Discord)
* Multi-indicateurs (MACD, Bollinger, etc.)
* Cache OHLCV optimisé
* Dashboard web interactif

---

## 📄 Licence

Projet privé - Outil d'analyse uniquement

---

## ❓ Support

Consultez le [cahier des charges](docs/cahier_des_charges_scanner.md) pour plus de détails sur le projet.
