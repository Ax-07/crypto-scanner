# 📊 Configuration des Moyennes Mobiles

## Guide complet pour personnaliser les MA (SMA/EMA)

---

## 🎯 Nouveaux Paramètres

```python
# config.py - Section MOYENNES MOBILES

USE_SMA = True   # Activer les SMA (Simple Moving Average)
USE_EMA = True   # Activer les EMA (Exponential Moving Average)

SMA_PERIODS = [20, 50]  # Périodes des SMA
EMA_PERIODS = [20, 50]  # Périodes des EMA
```

---

## 📋 Configurations Possibles

### 1️⃣ SMA et EMA avec périodes 20/50 (Défaut - Optimal) ⭐

```python
USE_SMA = True
USE_EMA = True
SMA_PERIODS = [20, 50]
EMA_PERIODS = [20, 50]
```

**Utilité** : Configuration équilibrée pour tendances court/moyen terme  
**Détection** : Prix > SMA20/50 OU EMA20 > EMA50  
**Colonnes CSV** : 24 colonnes (6 SMA + 6 EMA + metadata)

---

### 2️⃣ SMA uniquement

```python
USE_SMA = True
USE_EMA = False
SMA_PERIODS = [20, 50, 100, 200]
```

**Utilité** : Analyse classique avec moyennes mobiles simples  
**Détection** : Prix > SMA20 ET Prix > SMA50  
**Avantages** : Plus stable, moins de faux signaux  
**Colonnes CSV** : 12 SMA (4 périodes × 3 timeframes)

---

### 3️⃣ EMA uniquement

```python
USE_SMA = False
USE_EMA = True
EMA_PERIODS = [12, 26, 50]
```

**Utilité** : Trading réactif (day trading, scalping)  
**Détection** : EMA12 > EMA26 (système MACD-like)  
**Avantages** : Plus réactif aux changements de prix  
**Colonnes CSV** : 9 EMA (3 périodes × 3 timeframes)

⚠️ **Note** : Détection nécessite EMA20 et EMA50, ajouter aux périodes si absentes

---

### 4️⃣ Périodes personnalisées par type

```python
USE_SMA = True
USE_EMA = True
SMA_PERIODS = [50, 100, 200]    # Long terme
EMA_PERIODS = [9, 21, 55]       # Court terme (Fibonacci)
```

**Utilité** : Analyse multi-horizon  
**Détection** : Nécessite SMA20/50 OU EMA20/50 (ajuster si besoin)  
**Stratégie** : Combiner signaux court terme (EMA) et validation long terme (SMA)

---

### 5️⃣ Configuration Swing Trading

```python
USE_SMA = True
USE_EMA = True
SMA_PERIODS = [20, 50, 100]
EMA_PERIODS = [20, 50]
MA_TIMEFRAMES = ["1d", "4h"]  # Daily et H4 uniquement
```

**Utilité** : Positions de quelques jours à semaines  
**Timeframes** : Éviter 1w pour plus de réactivité  
**Détection** : Tendance confirmée sur Daily + H4

---

### 6️⃣ Configuration Day Trading

```python
USE_SMA = True
USE_EMA = True
SMA_PERIODS = [20, 50]
EMA_PERIODS = [9, 21]
MA_TIMEFRAMES = ["4h", "1h", "15m"]
```

**Utilité** : Positions intraday  
**EMA rapides** : 9/21 pour signaux rapides  
**Timeframes courts** : 4h/1h/15m pour réactivité

---

### 7️⃣ Configuration Investissement Long Terme

```python
USE_SMA = True
USE_EMA = False
SMA_PERIODS = [50, 100, 200]
MA_TIMEFRAMES = ["1w", "1d"]
```

**Utilité** : Positions de plusieurs semaines/mois  
**SMA longues** : 100/200 pour tendances robustes  
**Pas d'EMA** : Éviter le bruit court terme

---

### 8️⃣ Configuration Minimaliste (Performance)

```python
USE_SMA = True
USE_EMA = False
SMA_PERIODS = [20, 50]
MA_TIMEFRAMES = ["1d"]  # Un seul timeframe
```

**Utilité** : Scan très rapide avec tendance simple  
**Performance** : 2x plus rapide (2 appels API vs 4)  
**Trade-off** : Moins de confirmation multi-timeframe

---

## 🔧 Périodes Courantes et Leurs Usages

| Période | Type | Usage                           | Réactivité |
|---------|------|---------------------------------|------------|
| **9**   | EMA  | Court terme, scalping           | ⚡⚡⚡     |
| **12**  | EMA  | MACD rapide                     | ⚡⚡⚡     |
| **20**  | Both | Court/moyen terme équilibré     | ⚡⚡       |
| **21**  | EMA  | Fibonacci, swing                | ⚡⚡       |
| **26**  | EMA  | MACD lent                       | ⚡⚡       |
| **50**  | Both | Moyen terme classique           | ⚡         |
| **55**  | EMA  | Fibonacci, tendance             | ⚡         |
| **100** | SMA  | Long terme                      | 🐢         |
| **200** | SMA  | Très long terme, support majeur | 🐢         |

---

## 📊 Détection de Tendance

### Logique Actuelle

La fonction `detect_trend()` analyse :

**Si SMA disponibles (20 et 50)** :

```md
Haussier = Prix > SMA20 ET Prix > SMA50
```

**Si EMA disponibles (20 et 50)** :

```md
Haussier = EMA20 > EMA50  (croisement)
```

**Si les deux disponibles** :

```md
Haussier = (Prix > SMA20 ET Prix > SMA50) OU (EMA20 > EMA50)
```

### Configuration Minimale Requise

Pour que la détection fonctionne, il faut **AU MOINS** :

- `USE_SMA=True` avec `20` et `50` dans `SMA_PERIODS`
- **OU** `USE_EMA=True` avec `20` et `50` dans `EMA_PERIODS`

⚠️ **Important** : Si vous utilisez d'autres périodes (ex: 9/21), ajoutez 20/50 pour la détection :

```python
# Exemple avec EMA 9/21 + détection
USE_EMA = True
EMA_PERIODS = [9, 20, 21, 50]  # 20/50 pour detect_trend, 9/21 pour analyse
```

---

## 🎨 Exemples de Stratégies

### Stratégie 1 : Golden Cross / Death Cross

```python
USE_SMA = True
USE_EMA = False
SMA_PERIODS = [50, 200]
MA_TIMEFRAMES = ["1d"]
```

**Signal** : SMA50 croise SMA200  
**Usage** : Investissement long terme  
**Note** : Ajouter SMA20 si détection auto nécessaire

---

### Stratégie 2 : Triple EMA

```python
USE_SMA = False
USE_EMA = True
EMA_PERIODS = [9, 20, 50]
MA_TIMEFRAMES = ["4h", "1h"]
```

**Signal** : EMA9 > EMA20 > EMA50 = tendance forte  
**Usage** : Day trading actif

---

### Stratégie 3 : Confirmation Multi-Horizon

```python
USE_SMA = True
USE_EMA = True
SMA_PERIODS = [100, 200]     # Contexte long terme
EMA_PERIODS = [20, 50]       # Signaux court terme
MA_TIMEFRAMES = ["1w", "1d", "4h"]
```

**Signal** : EMA haussier (court terme) + SMA haussier (long terme)  
**Usage** : Swing trading avec confirmation robuste

---

## 📈 Impact Performance

| Configuration           | Colonnes CSV | Appels API/paire | Vitesse  |
|-------------------------|--------------|------------------|----------|
| SMA+EMA (20/50) × 3 TF  | 24           | 4                | ⏱️ Moyen |
| SMA seul (20/50) × 3 TF | 18           | 4                | ⏱️ Moyen |
| EMA seul (20/50) × 3 TF | 18           | 4                | ⏱️ Moyen |
| SMA+EMA × 1 TF          | 10           | 2                | ⚡ Rapide|
| SMA (4 périodes) × 3 TF | 24           | 4                | ⏱️ Moyen |

**Note** : Le nombre de périodes n'affecte PAS la vitesse (calcul local)

---

## ✅ Validation Configuration

Avant de lancer un scan complet, testez :

```bash
# Tester avec 5 paires
python -c "
import config
config.MAX_PAIRS = 5
config.USE_SMA = True
config.USE_EMA = False
config.SMA_PERIODS = [20, 50, 100]
from main import main
main()
"
```

Vérifiez :

- ✅ Pas d'erreurs
- ✅ Colonnes SMA présentes dans CSV
- ✅ Pas de colonnes EMA (si désactivées)
- ✅ Détection de tendance fonctionne

---

## 🚀 Recommandations par Profil

| Profil              | Configuration recommandée                        |
|---------------------|--------------------------------------------------|
| **Débutant**        | Config 1 (SMA+EMA 20/50) - équilibrée            |
| **Day Trader**      | Config 6 (EMA rapides 9/21)                      |
| **Swing Trader**    | Config 5 (SMA+EMA, daily+H4)                     |
| **Investisseur LT** | Config 7 (SMA 50/100/200, weekly+daily)          |
| **Performance**     | Config 8 (SMA 20/50, 1 timeframe)                |
| **Stratège**        | Config 4 (périodes custom selon système)         |

---

## 🔜 Possibilités Futures

- [ ] Ajouter autres MA : WMA (Weighted), SMMA (Smoothed)
- [ ] Détection automatique périodes optimales par paire
- [ ] Calcul de force de tendance (ADX-like)
- [ ] Croisements historiques (signaux récents)
- [ ] Alertes sur changement de tendance

---

## 💡 Conseils Pratiques

1. **Commencez simple** : SMA 20/50 ou EMA 20/50
2. **Testez avant** : `MAX_PAIRS = 10` pour valider config
3. **Multi-timeframe** : Privilégiez 2-3 TF (1w+1d ou 1d+4h)
4. **Périodes cohérentes** : Respectez ratios classiques (20/50, 50/200)
5. **SMA = stabilité** : Préférez pour long terme
6. **EMA = réactivité** : Préférez pour court terme
7. **Combinez les deux** : Meilleur compromis pour la plupart des cas

---

## 📌 Configuration Actuelle

Pour voir votre config :

```bash
python -c "
import config
print('=== MOYENNES MOBILES ===')
print(f'USE_SMA: {config.USE_SMA}')
if config.USE_SMA:
    print(f'  SMA_PERIODS: {config.SMA_PERIODS}')
print(f'USE_EMA: {config.USE_EMA}')
if config.USE_EMA:
    print(f'  EMA_PERIODS: {config.EMA_PERIODS}')
print(f'MA_TIMEFRAMES: {config.MA_TIMEFRAMES}')
"
```

---

🎯 **Personnalisez les MA selon votre style de trading !**
