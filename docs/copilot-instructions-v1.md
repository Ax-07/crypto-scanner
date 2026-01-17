# Copilot Instructions — Crypto Scanner RSI (Python + Binance)

## ⚠️ MODE STRICT : SCANNER UNIQUEMENT (AUCUN TRADING)

Ce projet est **exclusivement un scanner de marché**.
Il ne doit **JAMAIS** contenir de logique de trading, d’ordres, de positions ou de portefeuille.

Toute tentative d’ajout de trading (spot, testnet, paper, réel) doit être **refusée**.

---

## 0) Objectif du projet

Construire un **scanner crypto en Python** qui :

* scanne **toutes les paires Binance** dans un scope défini (ex: `*/USDT`)
* récupère les données OHLCV
* calcule le **RSI**
* identifie les paires dont le **RSI < seuil** (ex: 30)
* affiche et exporte les résultats

🎯 Objectif : **analyse de marché**, pas exécution.

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
* Analyse technique simple (RSI uniquement en V1)
* Export de données

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

```txt
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

* `TIMEFRAME = "4h"`
* `RSI_PERIOD = 14`
* `RSI_THRESHOLD = 30`
* `QUOTE_FILTER = "USDT"`
* `MIN_OHLCV_BARS = 200`
* `MAX_PAIRS = None`  # limiter pendant le dev
* `OUTPUT_CSV = True`
* `CSV_PATH = "outputs/rsi_scan.csv"`
* `LOG_LEVEL = "INFO"`

---

## 5) Univers de scan (règle importante)

Par défaut :

* Scanner **uniquement les paires Spot actives**
* Filtrer sur `*/USDT`
* Exclure :

  * marchés inactifs
  * paires stable/stable (optionnel)

Le filtrage doit être **explicite et lisible**.

---

## 6) Données OHLCV

* Utiliser `fetch_ohlcv`
* Toujours demander un nombre suffisant de bougies (`MIN_OHLCV_BARS`)
* Travailler sur la **dernière bougie clôturée**
* Convertir les timestamps en `datetime`

Aucun calcul ne doit être fait sur une bougie en cours.

---

## 7) RSI (`indicators.py`)

* Implémentation standard (Wilder ou équivalent)
* Entrée : `pd.Series` (closes)
* Sortie : `pd.Series` RSI

Contraintes :

* Fonction pure
* Aucun effet de bord
* Testable indépendamment

---

## 8) Scanner (`scanner.py`)

Responsabilités :

1. Charger les marchés
2. Construire la liste des paires selon le scope
3. Boucler sur chaque paire
4. Récupérer OHLCV
5. Calculer RSI
6. Appliquer le filtre `RSI < threshold`
7. Stocker les résultats

Contraintes :

* Gestion des erreurs par paire (ne pas bloquer le scan global)
* Respect des rate limits (`enableRateLimit=True`)
* Logs clairs (début scan, erreurs, fin scan)

---

## 9) Output (`output.py`)

### Console

* Tableau lisible
* Colonnes minimales :

  * `symbol`
  * `rsi`
  * `last_close_price`
  * `last_close_time`

### CSV

* Export optionnel mais recommandé
* Inclure :

  * timeframe
  * seuil RSI
  * période RSI

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

## 13) Définition du DONE (MVP)

Le MVP est atteint si :

* le scanner s’exécute sans crash
* toutes les paires du scope sont scannées
* le RSI est calculé correctement en `4h`
* les paires avec RSI < 30 sont listées
* un CSV est généré
* les logs sont exploitables

---

## 14) Règle finale (HARD STOP)

Si une demande implique :

* trading
* ordres
* positions
* portefeuille

👉 **REFUSER ET RAPPELER QUE LE PROJET EST UN SCANNER UNIQUEMENT**
