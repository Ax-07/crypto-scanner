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

### ✅ Validé (V1.5 - Moyennes Mobiles + Personnalisation)

* Calcul des moyennes mobiles (SMA et EMA)
* **Choix des indicateurs** : USE_RSI, USE_MA (V1.5+)
* **Personnalisation MA** : USE_SMA, USE_EMA, périodes indépendantes (V1.5+)
* Analyse multi-timeframes (Hebdo, Daily, H4)
* Détection de tendance adaptative (SMA seules, EMA seules, ou combinées)
* Filtre combiné : RSI + Tendance haussière
* Export CSV enrichi dynamique (18-30 colonnes selon config)
* Tests unitaires complets (6/6 réussis)

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

### Paramètres de base

* `TIMEFRAME = "4h"`
* `QUOTE_FILTER = "USDC"`  (scanner `*/USDC` - modifiable: USDT, BUSD, etc.)
* `MIN_OHLCV_BARS = 200` (assurer assez d'historique)
* `MAX_PAIRS = None` (pour limiter pendant le dev)
* `OUTPUT_CSV = True`
* `CSV_PATH = "outputs/rsi_scan.csv"`
* `LOG_LEVEL = "INFO"`
* `MAX_RETRIES = 3`

### Choix des indicateurs (V1.5+)

* `USE_RSI = True` (activer/désactiver le calcul et filtrage RSI)
* `USE_MA = True` (activer/désactiver les moyennes mobiles)

**Configurations possibles** :

* `USE_RSI=True, USE_MA=False` : Scanner RSI uniquement (V1 classique)
* `USE_RSI=False, USE_MA=True` : Scanner tendance uniquement
* `USE_RSI=True, USE_MA=True` : Filtre combiné (V1.5 optimal)
* `USE_RSI=False, USE_MA=False` : Lister toutes les paires sans filtre

### Paramètres RSI

* `RSI_PERIOD = 14`
* `RSI_THRESHOLD = 30`

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
* **Concurrency (V2)** : ✅ Implémenté avec ThreadPoolExecutor
  * Gain de performance : **3-4x plus rapide**
  * 8 workers par défaut (configurable 5-10)
  * Compatible avec rate limits Binance
  * Mode séquentiel disponible en fallback

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

**Détection adaptative selon configuration** :

* **Si SMA activées (20/50)** : Prix > SMA20 ET Prix > SMA50
* **Si EMA activées (20/50)** : EMA20 > EMA50 (croisement haussier)
* **Si les deux activées** : L'une OU l'autre condition (OU logique)

**Note** : La détection nécessite au moins SMA 20/50 OU EMA 20/50.
Si vous utilisez d'autres périodes (ex: 9/21), ajoutez 20/50 pour la détection.

**Filtre combiné optimal** :

1. `USE_RSI=True` : RSI < threshold (survendu)
2. `USE_MA=True` : Tendance haussière confirmée sur MIN_TREND_SCORE timeframes
3. Prix au-dessus des moyennes mobiles (rebond potentiel)

### Sorties enrichies

Colonnes dynamiques selon configuration :

**Si USE_SMA=True** :

* `sma{period}_{tf}` pour chaque période dans SMA_PERIODS et chaque timeframe
* Exemple : `sma20_1w`, `sma50_1w`, `sma100_1w`

**Si USE_EMA=True** :

* `ema{period}_{tf}` pour chaque période dans EMA_PERIODS et chaque timeframe
* Exemple : `ema9_1w`, `ema21_1w`, `ema50_1w`

**Si USE_MA=True** :

* `trend_{tf}` : bool (haussier/baissier) pour chaque timeframe
* `trend_score` : 0-3 (nombre de TF haussiers)

**Si USE_RSI=True** :

* `rsi` : valeur du RSI
* `rsi_period`, `rsi_threshold` : métadonnées

### Configuration

Paramètres dans `config.py` :

```python
# Activation des indicateurs
USE_MA = True           # Activer le module moyennes mobiles
USE_SMA = True          # Activer les SMA
USE_EMA = True          # Activer les EMA

# Périodes personnalisées par type
SMA_PERIODS = [20, 50]  # Périodes des SMA (ex: [50, 100, 200])
EMA_PERIODS = [20, 50]  # Périodes des EMA (ex: [9, 21, 50])

# Timeframes et filtrage
MA_TIMEFRAMES = ["1w", "1d", "4h"]  # Timeframes à analyser
MIN_TREND_SCORE = 2  # Score minimum pour valider la tendance (0-3)
MIN_MA_BARS = 60  # Nombre de bougies pour calculer les MA
```

**Flexibilité** :

* SMA uniquement : `USE_SMA=True, USE_EMA=False`
* EMA uniquement : `USE_SMA=False, USE_EMA=True`
* Les deux : `USE_SMA=True, USE_EMA=True` (optimal)
* Périodes différenciées : `SMA_PERIODS=[50,100,200]`, `EMA_PERIODS=[9,21]`

---

## 7️⃣bis Configuration Avancée (V1.5+)

### Personnalisation des Indicateurs

Le scanner offre une **flexibilité totale** sur les indicateurs utilisés :

#### Choix RSI / MA

| Config           | USE_RSI  | USE_MA   | Usage                           |
|------------------|----------|----------|---------------------------------|
| V1 classique     | True     | False    | Scanner RSI uniquement          |
| Tendance seule   | False    | True     | Scanner tendance multi-TF       |
| **V1.5 optimal** | **True** | **True** | **Filtre combiné (recommandé)** |
| Liste brute      | False    | False    | Toutes les paires               |

#### Personnalisation MA

**Types de moyennes mobiles** :

| Config         | USE_SMA  | USE_EMA  | Avantages                         |
|----------------|----------|----------|-----------------------------------|
| SMA uniquement | True     | False    | Stabilité, moins de bruit         |
| EMA uniquement | False    | True     | Réactivité, signaux rapides       |
| **Les deux**   | **True** | **True** | **Optimal, confirmation croisée** |

**Périodes personnalisées** :

```python
# Exemple : Multi-horizon
SMA_PERIODS = [50, 100, 200]  # Long terme
EMA_PERIODS = [9, 20, 21, 50]  # Court terme + détection
```

**Configurations types** :

* **Day Trading** : EMA 9/21, timeframes 4h/1h/15m
* **Swing Trading** : SMA+EMA 20/50, timeframes 1d/4h
* **Long Terme** : SMA 50/100/200, timeframes 1w/1d
* **Performance** : SMA 20/50, 1 timeframe uniquement

📖 Voir `docs/CONFIGURATION_MA.md` pour 8 configurations détaillées

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

* [x] Calcul SMA et EMA fonctionnel sur périodes 20 et 50
* [x] Multi-timeframe opérationnel (1w, 1d, 4h)
* [x] Détection de tendance haussière précise
* [x] Calcul du trend_score cohérent (0-3)
* [x] Filtre combiné RSI + tendance fonctionnel
* [x] Export CSV enrichi avec toutes les colonnes MA (24 colonnes)
* [x] Tests unitaires pour SMA/EMA (6/6 réussis)
* [x] Performance acceptable (scan complet < 10 min)

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

* [x] `indicators.py` : fonction `calculate_sma(series, period)`
* [x] `indicators.py` : fonction `calculate_ema(series, period)`
* [x] Fonction de détection de tendance `detect_trend()`
* [x] Multi-timeframe : récupération OHLCV pour 1w, 1d, 4h
* [x] Calcul du `trend_score`
* [x] Tests unitaires SMA/EMA

### 🔎 Scan

* [x] `scanner.py` : boucle + gestion erreurs + rate limit
* [x] Filtre `rsi < threshold`
* [x] Tri par RSI
* [x] Intégration multi-timeframe dans la boucle
* [x] Filtre combiné : RSI + trend_score
* [x] Optimisation des appels API

### 🧾 Output

* [x] `output.py` : affichage console propre
* [x] Export CSV dans `outputs/`
* [x] Affichage enrichi avec colonnes MA et trend_score
* [x] Export CSV avec toutes les colonnes V1.5 (24 colonnes)

### 📝 Logs & robustesse

* [x] `logger.py` : console + fichier
* [x] retries + backoff
* [x] arrêt propre (Ctrl+C)

### ✅ Validation MVP

* [x] Scan complet `*/USDC` en `4h` sans crash
* [x] Résultat console OK
* [x] CSV généré
* [x] Tests unitaires (6/6 réussis)

### ✅ Validation V1.5 (Moyennes Mobiles) - COMPLÈTE

* [x] Calcul MA correct et validé
* [x] Multi-timeframe fonctionnel (1w, 1d, 4h)
* [x] Détection de tendance fiable
* [x] Filtre combiné opérationnel (RSI + trend_score)
* [x] Export CSV enrichi (24 colonnes)
* [x] Tests unitaires MA (6/6 réussis)
* [x] Performance acceptable (optimisations appliquées)

---

## 📋 État du projet (18 janvier 2026)

### ✅ V2 COMPLÈTE ET VALIDÉE (Concurrency)

Le projet est **100% opérationnel** avec parallélisation et performances optimales :

* **Architecture complète** : 9 modules Python conformes aux spécifications
* **Tests validés** : 6/6 tests réussis (config, logger, exchange, data, indicators, scan complet)
* **Fonctionnalités V1 implémentées** :
  * Scan automatique des paires Binance Spot
  * Calcul RSI avec méthode de Wilder
  * Filtrage intelligent des paires (actives, spot, exclusion stables)
  * Export CSV avec métadonnées
  * Logging complet (console + fichier)
  * Gestion erreurs et rate limits
  * Tests modulaires

* **Fonctionnalités V1.5 implémentées** :
  * Calcul moyennes mobiles : SMA et EMA (périodes 20, 50)
  * Analyse multi-timeframe (1w, 1d, 4h)
  * Détection automatique de tendance haussière
  * Calcul du trend_score (0-3)
  * Filtre combiné : RSI < 30 + tendance haussière confirmée
  * Export CSV enrichi (24 colonnes)
  * Tests unitaires complets pour SMA/EMA

* **Fonctionnalités V1.5+ (Personnalisation)** :
  * **Choix des indicateurs** : USE_RSI, USE_MA (4 modes possibles)
  * **Choix types MA** : USE_SMA, USE_EMA (3 modes : SMA seul, EMA seul, les deux)
  * **Périodes indépendantes** : SMA_PERIODS et EMA_PERIODS configurables séparément
  * **Détection adaptative** : Fonctionne avec SMA seules, EMA seules, ou combinées
  * **Export dynamique** : 18-30 colonnes selon configuration active
  * **8 configurations documentées** : Day trading, swing, long terme, etc.

* **Fonctionnalités V2 (Concurrency) 🚀 NEW** :
  * **ThreadPoolExecutor** : Traitement parallèle avec 8 workers
  * **Gain de performance** : 3-4x plus rapide (testé sur 50 paires)
  * **Thread-safe** : Fonction analyze_single_pair() isolée
  * **Gestion d'erreurs** : Parallèle sans blocage du scan global
  * **Compteurs détaillés** : Succès, filtrées, erreurs séparés
  * **Statistiques** : Durée, vitesse (paires/sec), rate
  * **Mode séquentiel** : Disponible en fallback (ENABLE_CONCURRENCY=False)
  * **Compatible rate limits** : Respect automatique avec CCXT

* **Configuration actuelle** :
  * **Indicateurs** : RSI désactivé, MA activées (EMA uniquement)
  * **MA types** : EMA activées (périodes 20/50)
  * **Concurrency** : ✅ Activée (8 workers)
  * Quote currency : USDC
  * Timeframe RSI : 4h
  * Timeframes MA : 1d, 4h, 1h
  * Score minimum : 3/3 timeframes haussiers
  * ~4184 marchés disponibles sur Binance

### 📁 Fichiers livrés

```txt
scanner_binance/
├── config.py              ✅ Configuration centralisée
├── logger.py              ✅ Système de logging
├── exchange.py            ✅ Gestion Binance/CCXT
├── data.py                ✅ Récupération OHLCV
├── indicators.py          ✅ RSI + SMA + EMA + Tendance (V1.5)
├── scanner.py             ✅ Logique de scan
├── output.py              ✅ Affichage + export CSV
├── main.py                ✅ Point d'entrée
├── test_modules.py        ✅ Tests unitaires
├── requirements.txt       ✅ Dépendances
├── .gitignore            ✅
├── .env.example          ✅
├── README.md             ✅ Documentation complète
├── QUICKSTART.md         ✅ Guide démarrage
├── test_configurations.py ✅ Tests des 4 modes indicateurs
└── docs/
    ├── cahier_des_charges_scanner.md  ✅ (ce fichier)
    ├── CONFIGURATIONS_EXEMPLES.md     ✅ 8 configs types
    ├── CONFIGURATION_MA.md            ✅ Guide MA détaillé
    ├── FEATURE_CHOIX_INDICATEURS.md  ✅ Doc technique USE_RSI/USE_MA
    └── FEATURE_PERSONNALISATION_MA.md ✅ Doc technique SMA/EMA
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

* ✅ Choix des indicateurs (USE_RSI, USE_MA) - FAIT
* ✅ Personnalisation MA (USE_SMA, USE_EMA, périodes) - FAIT
* Tester différentes quote currencies (USDT, BUSD)
* Tester différents timeframes RSI (1h, 1d)
* Tester configurations avancées (ex: SMA 50/100/200)
* Ajouter WMA, SMMA (autres types de MA)
* Optimiser avec cache OHLCV
* Implémenter V2 (concurrency, notifications, dashboard)

### ✅ V1.5 - Moyennes Mobiles (COMPLÈTE)

**Objectif** : Détecter les opportunités combinant RSI bas + tendance haussière ✅

**Modifications réalisées** :

1. **indicators.py** :
   * ✅ `calculate_sma(prices, period)` → calcule SMA
   * ✅ `calculate_ema(prices, period)` → calcule EMA
   * ✅ `detect_trend(prices, sma20, sma50, ema20, ema50)` → détecte tendance haussière/baissière

2. **config.py** :
   * ✅ Paramètres indicateurs (USE_RSI, USE_MA)
   * ✅ Paramètres MA types (USE_SMA, USE_EMA)
   * ✅ Périodes indépendantes (SMA_PERIODS, EMA_PERIODS)
   * ✅ Paramètres communs (MA_TIMEFRAMES, MIN_TREND_SCORE, MIN_MA_BARS)

3. **scanner.py** :
   * ✅ Fonction `analyze_pair_ma()` pour analyse multi-timeframe
   * ✅ Calcul du trend_score pour chaque paire
   * ✅ Filtre combiné RSI + trend_score appliqué

4. **output.py** :
   * ✅ Affichage console enrichi avec colonnes MA et flags ✓/✗
   * ✅ Export CSV avec 24 colonnes (base + 12 MA + 4 tendance + 3 métadonnées)

5. **test_modules.py** :
   * ✅ Tests pour SMA/EMA ajoutés
   * ✅ Test de détection de tendance validé
   * ✅ 6/6 tests réussis

**Validation complète** :

* ✅ Tests unitaires : 6/6 passés
* ✅ Test d'intégration : 4/5 paires trouvées avec critères stricts
* ✅ Export CSV : 18-30 colonnes selon configuration
* ✅ Tests configurations : 4 modes indicateurs validés
* ✅ Détection adaptative : SMA seules, EMA seules, combinées OK
* ✅ Performance : scan complet < 10 min
* ✅ Documentation : 5 fichiers docs créés/mis à jour

---

## 🔜 Évolutions (V3)

* ✅ **Concurrency (V2)** : ThreadPoolExecutor implémenté (gain 3-4x)
* Notifications (Telegram/Discord)
* Multi-indicateurs (MACD, Bollinger, Stochastic)
* Cache OHLCV optimisé avec TTL
* Dashboard web interactif
* Scan multi-quotes simultanés (USDT + USDC + BUSD)
