# 📋 Exemples de Configurations

Ce document présente différentes configurations possibles du scanner selon vos besoins.

---

## 🎯 Configuration 1 : RSI uniquement (V1 classique)

**Objectif** : Scanner les paires survendues avec RSI < 30

```python
# config.py
USE_RSI = True   # ✓ Activer RSI
USE_MA = False   # ✗ Désactiver moyennes mobiles

RSI_THRESHOLD = 30
RSI_PERIOD = 14
TIMEFRAME = "4h"
```

**Résultat** : Liste des paires avec RSI < 30, triées par RSI croissant

**Colonnes CSV** :

- symbol, rsi, last_close_price, last_close_time, timeframe
- rsi_period, rsi_threshold, scan_date

---

## 📊 Configuration 2 : Moyennes Mobiles uniquement

**Objectif** : Trouver les paires en tendance haussière sans filtrer par RSI

```python
# config.py
USE_RSI = False  # ✗ Désactiver RSI
USE_MA = True    # ✓ Activer moyennes mobiles

MA_TIMEFRAMES = ["1w", "1d", "4h"]
MA_PERIODS = [20, 50]
MIN_TREND_SCORE = 3  # Tendance haussière sur les 3 timeframes
```

**Résultat** : Liste des paires avec tendance haussière confirmée sur 3 timeframes

**Colonnes CSV** :

- symbol, last_close_price, last_close_time, timeframe
- sma20_1w, sma50_1w, ema20_1w, ema50_1w (× 3 timeframes)
- trend_1w, trend_1d, trend_4h, trend_score
- scan_date

---

## 🎯 Configuration 3 : RSI + Tendance (V1.5 optimale)

**Objectif** : Opportunités combinant survendu + tendance haussière

```python
# config.py
USE_RSI = True   # ✓ Activer RSI
USE_MA = True    # ✓ Activer moyennes mobiles

RSI_THRESHOLD = 35
RSI_PERIOD = 14
TIMEFRAME = "4h"

MA_TIMEFRAMES = ["1w", "1d", "4h"]
MA_PERIODS = [20, 50]
MIN_TREND_SCORE = 2  # Au moins 2 timeframes haussiers
```

**Résultat** : Paires survendues (RSI < 35) en tendance haussière (2+ TF)

**Colonnes CSV** : Toutes les colonnes (24 colonnes complètes)

---

## 🔍 Configuration 4 : Liste complète (pas de filtres)

**Objectif** : Scanner toutes les paires sans filtrage (analyse brute)

```python
# config.py
USE_RSI = False  # ✗ Désactiver RSI
USE_MA = False   # ✗ Désactiver moyennes mobiles

MAX_PAIRS = 50   # Limiter pour éviter trop de résultats
```

**Résultat** : Toutes les paires du scope, triées par symbole

**Colonnes CSV** :

- symbol, last_close_price, last_close_time, timeframe
- scan_date

⚠️ **Note** : Configuration peu utile, mieux vaut activer au moins un indicateur

---

## 🎯 Configuration 5 : RSI agressif + Tendance stricte

**Objectif** : Opportunités rares mais très qualitatives

```python
# config.py
USE_RSI = True
USE_MA = True

RSI_THRESHOLD = 25   # RSI très bas (très survendu)
RSI_PERIOD = 14
TIMEFRAME = "1h"     # Timeframe court pour réactivité

MA_TIMEFRAMES = ["1w", "1d", "4h"]
MA_PERIODS = [20, 50, 100]  # Ajout SMA/EMA 100
MIN_TREND_SCORE = 3  # Tendance haussière sur TOUS les timeframes
```

**Résultat** : Peu de résultats mais opportunités de haute qualité

---

## 📊 Configuration 6 : Analyse moyen/long terme

**Objectif** : Scanner les opportunités sur timeframes plus longs

```python
# config.py
USE_RSI = True
USE_MA = True

RSI_THRESHOLD = 40
RSI_PERIOD = 14
TIMEFRAME = "1d"     # Daily pour analyse moyen terme

MA_TIMEFRAMES = ["1w", "1d"]  # Seulement hebdo et daily
MA_PERIODS = [50, 200]        # MAs long terme
MIN_TREND_SCORE = 2
```

**Résultat** : Opportunités moyen/long terme avec moins de bruit

---

## 🎯 Configuration 7 : Swing trading

**Objectif** : Scanner pour du swing trading (quelques jours)

```python
# config.py
USE_RSI = True
USE_MA = True

RSI_THRESHOLD = 30
RSI_PERIOD = 14
TIMEFRAME = "4h"

MA_TIMEFRAMES = ["1d", "4h"]  # Daily et H4
MA_PERIODS = [20, 50]
MIN_TREND_SCORE = 2
QUOTE_FILTER = "USDT"  # Plus de liquidité
```

**Résultat** : Setup pour entrées swing avec confirmation tendance

---

## 🔍 Configuration 8 : Day trading

**Objectif** : Scanner pour du day trading intraday

```python
# config.py
USE_RSI = True
USE_MA = True

RSI_THRESHOLD = 35
RSI_PERIOD = 14
TIMEFRAME = "15m"    # 15 minutes

MA_TIMEFRAMES = ["4h", "1h", "15m"]
MA_PERIODS = [20, 50]
MIN_TREND_SCORE = 2
MIN_OHLCV_BARS = 100  # Moins d'historique nécessaire
```

**Résultat** : Opportunités intraday pour day trading

---

## ⚙️ Recommandations

### Pour débuter

👉 **Configuration 3** (RSI + Tendance V1.5) avec paramètres par défaut

### Pour traders agressifs

👉 **Configuration 5** (seuils stricts) ou **Configuration 8** (day trading)

### Pour investisseurs long terme

👉 **Configuration 6** (analyse moyen/long terme)

### Pour analyse technique pure

👉 **Configuration 2** (moyennes mobiles uniquement)

---

## 🧪 Test de configuration

Pour tester une configuration rapidement :

```python
# config.py
MAX_PAIRS = 10  # Limiter à 10 paires pour test rapide
```

```bash
python main.py
```

Vérifiez les résultats avant de lancer un scan complet (`MAX_PAIRS = None`)

---

## 📝 Notes importantes

1. **Performance** : Plus vous activez d'indicateurs et de timeframes, plus le scan est long
2. **Pertinence** : `USE_RSI = True` + `USE_MA = True` donne les meilleurs résultats
3. **Flexibilité** : Vous pouvez ajuster les seuils selon la volatilité du marché
4. **Quote currency** : `USDC` = moins de paires, `USDT` = plus de liquidité
5. **Rate limits** : Respectés automatiquement par CCXT

---

## 🎯 Configuration actuelle

Pour voir votre configuration actuelle :

```bash
python -c "import config; print('RSI:', config.USE_RSI, '| MA:', config.USE_MA)"
```
