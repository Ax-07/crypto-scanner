# 📘 Cahier des charges

## Scanner crypto Binance : détection RSI < seuil

---

## 1️⃣ Objectif

Développer un **scanner crypto** en **Python** qui :

* récupère la liste de **toutes les paires tradables** sur Binance (scope défini ci-dessous)
* télécharge les données OHLCV pour un **timeframe choisi** (par défaut `4h`)
* calcule le **RSI** (période standard 14, configurable)
* **liste / exporte** toutes les paires dont le **RSI est inférieur à un seuil** (par défaut 30)

🎯 Résultat attendu : une liste triée des paires "survendues" (RSI bas) au timeframe sélectionné.

---

## 2️⃣ Périmètre

### ✅ Inclus (V1)

* Binance via **CCXT**
* Scan de marché : récupération des marchés + filtrage des paires
* Téléchargement OHLCV pour chaque paire
* Calcul RSI
* Filtre : `RSI < threshold`
* Sortie :

  * affichage console (table)
  * export CSV (optionnel mais recommandé)
* Paramètres configurables (timeframe, seuil, période RSI, quote asset, etc.)
* Gestion des erreurs réseau + rate limits + retries

### ❌ Exclu (V1)

* Trading automatique
* Backtesting
* Signaux complexes (divergences)
* Notifications (Telegram/Discord)
* Interface web/GUI

### 🔄 En cours (V1.5 - Moyennes Mobiles)

* Calcul des moyennes mobiles (SMA et EMA)
* Analyse multi-timeframes (Hebdo, Daily, H4)
* Détection de tendance haussière
* Filtre combiné : RSI + Tendance haussière

---

## 3️⃣ Hypothèses & choix

### Exchange

* Binance Spot (par défaut)

### Univers de scan (important)

Pour éviter un scan trop large / inutile, définir un scope clair :

* Option configurée : **toutes les paires en `*/USDC`** (liquides et comparables)
* Modifiable facilement dans `config.py` vers USDT, BUSD, etc.
* Exclusions :

  * paires non actives (inactive)
  * paires non spot (si on reste en spot)
  * stable/stable (ex: USDT/USDC) (activé par défaut)

Le scope est configurable via `QUOTE_FILTER` dans `config.py`.

---

## 4️⃣ Paramètres (config)

Paramètres par défaut :

* `TIMEFRAME = "4h"`
* `RSI_PERIOD = 14`
* `RSI_THRESHOLD = 30`
* `QUOTE_FILTER = "USDC"`  (scanner `*/USDC` - modifiable: USDT, BUSD, etc.)
* `MIN_OHLCV_BARS = 200` (assurer assez d'historique)
* `MAX_PAIRS = None` (pour limiter pendant le dev)
* `OUTPUT_CSV = True`
* `CSV_PATH = "outputs/rsi_scan.csv"`
* `LOG_LEVEL = "INFO"`
* `MAX_RETRIES = 3`

---

## 5️⃣ Contraintes techniques

### Librairies

* `ccxt`
* `pandas`
* `numpy`
* `python-dotenv` (optionnel si clés API; **pas nécessaire** pour OHLCV public)

### Performance & rate limiting

* Activer `enableRateLimit=True`
* Implémenter :

  * retries exponentiels sur erreurs réseau
  * pause automatique sur `RateLimitExceeded`
* Possibilité d’ajouter **concurrency** (V2). En V1, rester simple et fiable.

---

## 6️⃣ Calcul RSI

* RSI calculé sur les **closes**
* Méthode recommandée : RSI de Wilder (EMA des gains/pertes) ou implémentation standard
* Le scanner utilise la **dernière bougie clôturée** (pas de bougie en cours si possible)

Sorties par paire :

* `symbol`
* `timeframe`
* `rsi`
* `last_close_time`
* `last_close_price`

---

## 7️⃣ Moyennes Mobiles (V1.5)

### Objectif

Ajouter une **détection de tendance haussière** via moyennes mobiles pour affiner le filtrage.

### Indicateurs

**SMA (Simple Moving Average)** :

* Moyenne arithmétique simple sur N périodes
* Plus lisse, moins réactive

**EMA (Exponential Moving Average)** :

* Moyenne exponentielle donnant plus de poids aux valeurs récentes
* Plus réactive aux changements

### Timeframes et Périodes

Analyse **multi-timeframe** pour confirmer la tendance :

| Timeframe      | SMA/EMA Périodes | Usage                |
|----------------|------------------|----------------------|
| **Hebdo (1w)** | 20, 50           | Tendance long terme  |
| **Daily (1d)** | 20, 50           | Tendance moyen terme |
| **H4 (4h)**    | 20, 50           | Tendance court terme |

### Logique de détection de tendance

**Tendance haussière confirmée si** :

* Prix > SMA20 ET Prix > SMA50
* OU EMA20 > EMA50 (croisement haussier)

**Filtre combiné optimal** :

1. RSI < 30 (survendu)
2. Tendance haussière confirmée sur au moins 2 timeframes
3. Prix au-dessus des moyennes mobiles (rebond potentiel)

### Sorties enrichies

Nouvelles colonnes dans les résultats :

* `sma20_1w`, `sma50_1w`, `ema20_1w`, `ema50_1w`
* `sma20_1d`, `sma50_1d`, `ema20_1d`, `ema50_1d`
* `sma20_4h`, `sma50_4h`, `ema20_4h`, `ema50_4h`
* `trend_1w`, `trend_1d`, `trend_4h` (bool : haussier/baissier)
* `trend_score` (0-3 : nombre de TF haussiers)

### Configuration

Nouveaux paramètres dans `config.py` :

```python
# Moyennes mobiles
ENABLE_MA = True  # Activer l'analyse des moyennes mobiles
MA_PERIODS = [20, 50]  # Périodes à calculer
MA_TIMEFRAMES = ["1w", "1d", "4h"]  # Timeframes à analyser
MIN_TREND_SCORE = 2  # Score minimum pour valider la tendance (0-3)
```

---

## 8️⃣ Architecture proposée

```txt
crypto-scanner/
├── .venv/
├── requirements.txt
├── .env.example            # optionnel
├── .gitignore
│
├── config.py               # paramètres (+ config MA)
├── exchange.py             # init ccxt + fetch markets
├── data.py                 # fetch_ohlcv -> DataFrame
├── indicators.py           # RSI + SMA + EMA (V1.5)
├── scanner.py              # boucle de scan + filtrage
├── output.py               # console + csv
├── logger.py               # logging
└── main.py                 # entrypoint CLI
```

---

## 9️⃣ Fonctionnement (flux V1.5)

1. **Init exchange** (ccxt, rate limit)
2. `load_markets()`
3. Construire la liste des paires selon le scope (ex: `*/USDC`, active, spot)
4. Pour chaque paire :

   **A. Récupération données RSI (timeframe principal)** :
   * récupérer OHLCV (`timeframe=4h`, `limit=MIN_OHLCV_BARS`)
   * convertir en DataFrame + timestamps
   * calculer RSI
   * récupérer RSI latest (bougie close)

   **B. Récupération données MA (multi-timeframe)** :
   * Pour chaque timeframe (1w, 1d, 4h) :
     * récupérer OHLCV (`limit=60` pour SMA50)
     * calculer SMA20, SMA50, EMA20, EMA50
     * détecter tendance (prix > MA, croisements)
   * calculer `trend_score` (nombre de TF haussiers)

   **C. Filtrage** :
   * si `rsi < threshold` ET `trend_score >= MIN_TREND_SCORE`
   * → ajouter au résultat avec toutes les données

5. Trier résultats par RSI ascendant (ou par trend_score)
6. Afficher tableau console enrichi
7. Exporter CSV avec colonnes MA

---

## 🔟 Sorties attendues (V1.5)

### Console

* Tableau avec colonnes principales :
  * `symbol`, `rsi`, `last_close_price`, `last_close_time`
  * `trend_score` (0-3)
  * `trend_1w`, `trend_1d`, `trend_4h` (✓/✗)
* Trié par RSI ascendant ou trend_score descendant

### CSV (recommandé)

* Fichier : `outputs/rsi_scan.csv`
* Colonnes de base + toutes les moyennes mobiles :
  * `symbol`, `rsi`, `last_close_price`, `last_close_time`
  * `sma20_1w`, `sma50_1w`, `ema20_1w`, `ema50_1w`
  * `sma20_1d`, `sma50_1d`, `ema20_1d`, `ema50_1d`
  * `sma20_4h`, `sma50_4h`, `ema20_4h`, `ema50_4h`
  * `trend_1w`, `trend_1d`, `trend_4h`, `trend_score`
  * `timeframe`, `rsi_threshold`, `rsi_period`

---

## 1️⃣1️⃣ Critères de réussite (V1.5)

**MVP (V1)** :

* ✅ Le scanner récupère une liste de paires valide (ex: toutes `*/USDC` actives)
* ✅ Le scanner calcule le RSI correctement sur `4h`
* ✅ Le scanner produit une liste (éventuellement vide) des paires RSI < 30
* ✅ Le scanner gère les erreurs API sans crash (retry + logs)
* ✅ Export CSV OK

**V1.5 (Moyennes Mobiles)** :

* [ ] Calcul SMA et EMA fonctionnel sur périodes 20 et 50
* [ ] Multi-timeframe opérationnel (1w, 1d, 4h)
* [ ] Détection de tendance haussière précise
* [ ] Calcul du trend_score cohérent
* [ ] Filtre combiné RSI + tendance fonctionnel
* [ ] Export CSV enrichi avec toutes les colonnes MA
* [ ] Tests unitaires pour SMA/EMA
* [ ] Performance acceptable (scan complet < 10 min)

---

## ✅ Checklist de suivi

### 🧱 Base projet

* [x] Créer dossier + `.venv`
* [x] Ajouter `requirements.txt`
* [x] Ajouter `.gitignore`
* [x] Ajouter structure des fichiers

### 🔌 Exchange & marchés

* [x] `exchange.py` : init ccxt + `load_markets()`
* [x] Filtre paires `*/USDC` actives (configurable)
* [x] Option limiter `MAX_PAIRS` pour dev

### 📊 Données

* [x] `data.py` : `fetch_ohlcv(symbol, timeframe, limit)`
* [x] DataFrame avec `time, open, high, low, close, volume`
* [x] Utiliser dernière bougie clôturée

### 📈 RSI

* [x] `indicators.py` : fonction `rsi(series, period)`
* [x] Test rapide sur une paire connue (sanity check)
* [x] Gestion des cas limites (division par zéro)

### 📊 Moyennes Mobiles (V1.5)

* [ ] `indicators.py` : fonction `calculate_sma(series, period)`
* [ ] `indicators.py` : fonction `calculate_ema(series, period)`
* [ ] Fonction de détection de tendance `detect_trend()`
* [ ] Multi-timeframe : récupération OHLCV pour 1w, 1d, 4h
* [ ] Calcul du `trend_score`
* [ ] Tests unitaires SMA/EMA

### 🔎 Scan

* [x] `scanner.py` : boucle + gestion erreurs + rate limit
* [x] Filtre `rsi < threshold`
* [x] Tri par RSI
* [ ] Intégration multi-timeframe dans la boucle
* [ ] Filtre combiné : RSI + trend_score
* [ ] Optimisation des appels API (cache si possible)

### 🧾 Output

* [x] `output.py` : affichage console propre
* [x] Export CSV dans `outputs/`
* [ ] Affichage enrichi avec colonnes MA et trend_score
* [ ] Export CSV avec toutes les colonnes V1.5

### 📝 Logs & robustesse

* [x] `logger.py` : console + fichier
* [x] retries + backoff
* [x] arrêt propre (Ctrl+C)

### ✅ Validation MVP

* [x] Scan complet `*/USDC` en `4h` sans crash
* [x] Résultat console OK
* [x] CSV généré
* [x] Tests unitaires (6/6 réussis)

### ✅ Validation V1.5 (Moyennes Mobiles)

* [ ] Calcul MA correct et validé
* [ ] Multi-timeframe fonctionnel
* [ ] Détection de tendance fiable
* [ ] Filtre combiné opérationnel
* [ ] Export CSV enrichi
* [ ] Tests unitaires MA (2/2 réussis)
* [ ] Performance acceptable

---

## 📋 État du projet (17 janvier 2026)

### ✅ MVP ATTEINT

Le projet est **100% opérationnel** :

* **Architecture complète** : 9 modules Python conformes aux spécifications
* **Tests validés** : 6/6 tests réussis (config, logger, exchange, data, indicators, scan complet)
* **Fonctionnalités implémentées** :
  * Scan automatique des paires Binance Spot
  * Calcul RSI avec méthode de Wilder
  * Filtrage intelligent des paires (actives, spot, exclusion stables)
  * Export CSV avec métadonnées
  * Logging complet (console + fichier)
  * Gestion erreurs et rate limits
  * Tests modulaires

* **Configuration actuelle** :
  * Quote currency : USDC
  * Timeframe : 4h
  * RSI période : 14
  * Seuil : 30
  * ~4184 marchés disponibles sur Binance

### 📁 Fichiers livrés

```txt
scanner_binance/
├── config.py              ✅ Configuration centralisée
├── logger.py              ✅ Système de logging
├── exchange.py            ✅ Gestion Binance/CCXT
├── data.py                ✅ Récupération OHLCV
├── indicators.py          ✅ Calcul RSI (corrigé)
├── scanner.py             ✅ Logique de scan
├── output.py              ✅ Affichage + export CSV
├── main.py                ✅ Point d'entrée
├── test_modules.py        ✅ Tests unitaires
├── requirements.txt       ✅ Dépendances
├── .gitignore            ✅
├── .env.example          ✅
├── README.md             ✅ Documentation complète
├── QUICKSTART.md         ✅ Guide démarrage
└── docs/
    └── cahier_des_charges_scanner.md  ✅ (ce fichier)
```

### 🚀 Utilisation

```bash
# Installation
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Tests
python test_modules.py

# Exécution
python main.py
```

### 🎯 Prochaines actions possibles

* Tester avec différentes quote currencies (USDT, BUSD)
* Tester avec différents timeframes (1h, 1d)
* Ajuster le seuil RSI selon les besoins
* Limiter MAX_PAIRS pour tests rapides

### 🚀 V1.5 - Moyennes Mobiles (EN COURS)

**Objectif** : Détecter les opportunités combinant RSI bas + tendance haussière

**Modifications prévues** :

1. **indicators.py** :
   * Ajouter `calculate_sma(prices, period)` → retourne SMA
   * Ajouter `calculate_ema(prices, period)` → retourne EMA
   * Ajouter `detect_trend(prices, sma20, sma50, ema20, ema50)` → retourne bool (haussier/baissier)

2. **config.py** :
   * Ajouter paramètres MA (périodes, timeframes, score min)

3. **scanner.py** :
   * Intégrer boucle multi-timeframe
   * Calculer trend_score pour chaque paire
   * Appliquer filtre combiné

4. **output.py** :
   * Enrichir affichage console avec colonnes MA
   * Ajouter toutes les colonnes MA au CSV

5. **test_modules.py** :
   * Ajouter tests pour SMA/EMA
   * Tester détection de tendance

**Planning** :

* Phase 1 : Implémentation SMA/EMA dans indicators.py
* Phase 2 : Détection de tendance et tests
* Phase 3 : Intégration multi-timeframe dans scanner.py
* Phase 4 : Enrichissement output + validation complète

---

## 🔜 Évolutions (V2)

* Concurrency (async/threads) pour accélérer
* Cache OHLCV / reprise incrémentale
* Multi-timeframes en une exécution
* Notifications (Telegram/Discord)
* Autres filtres : volume minimal, volatilité, tendance, multi-indicateurs
* Dashboard
