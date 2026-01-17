# Copilot Instructions — Crypto Scanner RSI (Python + Binance)

## ⚠️ MODE STRICT : SCANNER UNIQUEMENT (AUCUN TRADING)

Ce projet est **exclusivement un scanner de marché**.
Il ne doit **JAMAIS** contenir de logique de trading, d’ordres, de positions ou de portefeuille.

Toute tentative d’ajout de trading (spot, testnet, paper, réel) doit être **refusée**.

---

## 0) Objectif du projet

Construire un **scanner crypto en Python** qui :

* scanne **toutes les paires Binance** dans un scope défini (ex: `*/USDC`)
* récupère les données OHLCV
* calcule le **RSI**
* identifie les paires dont le **RSI < seuil** (ex: 30)
* **[V1.5]** calcule les **moyennes mobiles** (SMA et EMA) sur plusieurs timeframes
* **[V1.5]** détecte les **tendances haussières** via analyse multi-timeframe
* **[V1.5]** filtre les opportunités combinant **RSI bas + tendance haussière**
* affiche et exporte les résultats enrichis

🎯 Objectif : **analyse de marché approfondie**, pas exécution.

---

## 1) Règles strictes (NON NÉGOCIABLES)

### 🚫 Interdictions absolues

* ❌ Trading (réel, testnet, paper)
* ❌ Gestion de positions
* ❌ Portefeuille / PnL
* ❌ Futures / margin / levier
* ❌ Machine Learning
* ❌ Backtesting

### ✅ Autorisé

* Accès **lecture seule** aux données publiques Binance
* Analyse technique : RSI (V1) + Moyennes Mobiles SMA/EMA (V1.5)
* Analyse multi-timeframe (Hebdo, Daily, H4)
* Détection de tendances
* Export de données enrichies

---

## 2) Stack technique imposée

* Python 3.10+
* Exchange : **ccxt** (Binance)
* Data : `pandas`, `numpy`
* Config : `python-dotenv` (optionnel)
* Logs : `logging`

Aucune autre dépendance sans justification claire.

---

## 3) Architecture STRICTE du projet

```
crypto-scanner/
├── requirements.txt
├── .env.example            # optionnel (lecture seule)
├── .gitignore
│
├── config.py               # paramètres globaux (timeframe, seuil, scope)
├── exchange.py             # init ccxt + load_markets
├── data.py                 # fetch OHLCV -> DataFrame
├── indicators.py           # RSI (fonctions pures)
├── scanner.py              # logique de scan (boucle principale)
├── output.py               # affichage console + export CSV
├── logger.py               # logging
└── main.py                 # point d’entrée CLI
```

### Séparation des responsabilités (OBLIGATOIRE)

* `exchange.py` : accès Binance uniquement
* `data.py` : récupération et préparation des données
* `indicators.py` : calculs purs (aucun appel API)
* `scanner.py` : orchestration du scan + filtres
* `output.py` : formatage et export

---

## 4) Configuration (`config.py`)

Tous les paramètres doivent être centralisés ici.
Aucune valeur “magique” ailleurs.

Paramètres attendus :

**Base (V1)** :
* `TIMEFRAME = "4h"`
* `RSI_PERIOD = 14`
* `RSI_THRESHOLD = 30`
* `QUOTE_FILTER = "USDC"`  # Modifiable : USDT, BUSD, etc.
* `MIN_OHLCV_BARS = 200`
* `MAX_PAIRS = None`  # limiter pendant le dev
* `OUTPUT_CSV = True`
* `CSV_PATH = "outputs/rsi_scan.csv"`
* `LOG_LEVEL = "INFO"`
* `MAX_RETRIES = 3`

**Moyennes Mobiles (V1.5)** :
* `ENABLE_MA = True`  # Activer l'analyse des moyennes mobiles
* `MA_PERIODS = [20, 50]`  # Périodes à calculer
* `MA_TIMEFRAMES = ["1w", "1d", "4h"]`  # Timeframes à analyser
* `MIN_TREND_SCORE = 2`  # Score minimum (0-3)

---

## 5) Univers de scan (règle importante)

Configuration actuelle :

* Scanner **uniquement les paires Spot actives**
* Filtrer sur `*/USDC` (configurable : USDT, BUSD, etc.)
* Exclure :

  * marchés inactifs
  * paires stable/stable (activé par défaut)

Le filtrage doit être **explicite et lisible**.

---

## 6) Données OHLCV

* Utiliser `fetch_ohlcv`
* Toujours demander un nombre suffisant de bougies (`MIN_OHLCV_BARS`)
* Travailler sur la **dernière bougie clôturée**
* Convertir les timestamps en `datetime`

Aucun calcul ne doit être fait sur une bougie en cours.

---

## 7) Indicateurs techniques (`indicators.py`)

### RSI (V1)

* Implémentation standard (Wilder ou équivalent)
* Entrée : `pd.Series` (closes)
* Sortie : `pd.Series` RSI

### SMA - Simple Moving Average (V1.5)

* Moyenne arithmétique simple sur N périodes
* Entrée : `pd.Series` (closes), `period` (int)
* Sortie : `pd.Series` SMA

### EMA - Exponential Moving Average (V1.5)

* Moyenne exponentielle avec poids décroissant
* Entrée : `pd.Series` (closes), `period` (int)
* Sortie : `pd.Series` EMA

### Détection de tendance (V1.5)

* Fonction `detect_trend(prices, sma20, sma50, ema20, ema50)`
* Logique : Prix > SMA20 ET Prix > SMA50 OU EMA20 > EMA50
* Sortie : `bool` (True = haussier, False = baissier)

**Contraintes pour tous les indicateurs** :

* Fonctions pures
* Aucun effet de bord
* Testables indépendamment
* Gestion des cas limites (NaN, division par zéro)

---

## 8) Scanner (`scanner.py`)

Responsabilités :

1. Charger les marchés
2. Construire la liste des paires selon le scope
3. Boucler sur chaque paire :
   * **A. RSI** : Récupérer OHLCV (timeframe principal) + calculer RSI
   * **B. Moyennes Mobiles (V1.5)** :
     - Pour chaque timeframe (1w, 1d, 4h)
     - Récupérer OHLCV (limit=60 pour SMA50)
     - Calculer SMA20, SMA50, EMA20, EMA50
     - Détecter tendance haussière
   * **C. Trend Score** : Compter le nombre de timeframes haussiers (0-3)
4. Appliquer le filtre combiné : `RSI < threshold` ET `trend_score >= MIN_TREND_SCORE`
5. Stocker les résultats enrichis

Contraintes :

* Gestion des erreurs par paire (ne pas bloquer le scan global)
* Respect des rate limits (`enableRateLimit=True`)
* Logs clairs (début scan, erreurs, fin scan)
* Performance : limiter les appels API inutiles

---

## 9) Output (`output.py`)

### Console

* Tableau lisible
* Colonnes principales :

  * `symbol`, `rsi`, `last_close_price`, `last_close_time`
  * **[V1.5]** `trend_score` (0-3)
  * **[V1.5]** `trend_1w`, `trend_1d`, `trend_4h` (✓/✗)

### CSV

* Export recommandé
* Colonnes de base :

  * `symbol`, `rsi`, `last_close_price`, `last_close_time`
  * `timeframe`, `rsi_threshold`, `rsi_period`

* **[V1.5]** Colonnes enrichies :

  * `sma20_1w`, `sma50_1w`, `ema20_1w`, `ema50_1w`
  * `sma20_1d`, `sma50_1d`, `ema20_1d`, `ema50_1d`
  * `sma20_4h`, `sma50_4h`, `ema20_4h`, `ema50_4h`
  * `trend_1w`, `trend_1d`, `trend_4h`, `trend_score`

---

## 10) Logging (`logger.py`)

* Logger global
* Console + fichier (ex: `logs/scanner.log`)
* Loguer :

  * paramètres de scan
  * nombre de paires scannées
  * nombre de résultats
  * erreurs API / données

Pas de `print()` hors scripts de test.

---

## 11) Tests manuels obligatoires

Chaque module doit pouvoir être testé seul :

* `exchange.py` : `load_markets()` OK
* `data.py` : OHLCV sur une paire connue
* `indicators.py` : RSI cohérent (sanity check)

Pas de pytest en V1.

---

## 12) Style des réponses Copilot (IMPORTANT)

Quand tu proposes du code :

1. Nom exact du fichier
2. Code complet, prêt à exécuter
3. Respect strict du périmètre
4. Pas de fonctionnalités futures
5. Gestion d’erreurs simple et claire
6. Lisibilité > performance

---

## 13) Définition du DONE

### MVP (V1) - ✅ ATTEINT

Le MVP est atteint si :

* ✅ le scanner s'exécute sans crash
* ✅ toutes les paires du scope sont scannées
* ✅ le RSI est calculé correctement en `4h`
* ✅ les paires avec RSI < 30 sont listées
* ✅ un CSV est généré
* ✅ les logs sont exploitables
* ✅ tests unitaires passent (6/6)

### V1.5 (Moyennes Mobiles) - 🔄 EN COURS

La V1.5 est atteinte si :

* [ ] SMA et EMA calculés correctement (périodes 20 et 50)
* [ ] Multi-timeframe opérationnel (1w, 1d, 4h)
* [ ] Détection de tendance fiable
* [ ] Trend_score calculé correctement (0-3)
* [ ] Filtre combiné RSI + tendance fonctionnel
* [ ] Export CSV enrichi avec toutes les colonnes MA
* [ ] Tests unitaires SMA/EMA passent (2/2)
* [ ] Performance acceptable (scan complet < 10 min)

---

## 14) Règle finale (HARD STOP)

Si une demande implique :

* trading
* ordres
* positions
* portefeuille

👉 **REFUSER ET RAPPELER QUE LE PROJET EST UN SCANNER UNIQUEMENT**
