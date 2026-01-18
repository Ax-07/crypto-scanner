# 🎯 Personnalisation des Moyennes Mobiles

## Date : 17 janvier 2026

## Fonctionnalité : Configuration indépendante SMA/EMA avec périodes personnalisées

---

## 📝 Résumé

Amélioration majeure du système de moyennes mobiles permettant de :

1. **Choisir les types de MA** : SMA uniquement, EMA uniquement, ou les deux
2. **Configurer les périodes indépendamment** : SMA et EMA peuvent avoir des périodes différentes
3. **Optimiser la détection de tendance** : Fonctionne avec SMA seules, EMA seules, ou combinées

---

## ⚙️ Nouveaux Paramètres (config.py)

### Avant (V1.5 initial)

```python
ENABLE_MA = True
MA_PERIODS = [20, 50]  # Même périodes pour SMA et EMA
```

### Après (V1.5 amélioré) ✨

```python
USE_MA = True           # Active le module MA
USE_SMA = True          # Active les SMA
USE_EMA = True          # Active les EMA
SMA_PERIODS = [20, 50]  # Périodes SMA indépendantes
EMA_PERIODS = [20, 50]  # Périodes EMA indépendantes
```

---

## 🎨 Possibilités de Configuration

### 1️⃣ SMA + EMA avec périodes identiques (Défaut)

```python
USE_SMA = True
USE_EMA = True
SMA_PERIODS = [20, 50]
EMA_PERIODS = [20, 50]
```

✅ Configuration équilibrée et complète

---

### 2️⃣ SMA uniquement

```python
USE_SMA = True
USE_EMA = False
SMA_PERIODS = [20, 50, 100, 200]
```

✅ Analyse stable, moins de bruit  
✅ Parfait pour long terme

---

### 3️⃣ EMA uniquement

```python
USE_SMA = False
USE_EMA = True
EMA_PERIODS = [9, 21, 50]
```

✅ Analyse réactive, signaux rapides  
✅ Parfait pour day trading

---

### 4️⃣ Périodes différenciées (Avancé)

```python
USE_SMA = True
USE_EMA = True
SMA_PERIODS = [50, 100, 200]  # Long terme
EMA_PERIODS = [9, 21]         # Court terme
```

✅ Multi-horizon : EMA rapides + SMA validation  
⚠️ Nécessite SMA20/50 ou EMA20/50 pour détection auto

---

## 🔧 Modifications Techniques

### Fichiers modifiés

#### 1. **config.py**

```python
# Avant
MA_PERIODS = [20, 50]

# Après
USE_SMA = True
USE_EMA = True
SMA_PERIODS = [20, 50]
EMA_PERIODS = [20, 50]
```

#### 2. **scanner.py**

- Calcul SMA conditionnel (`if config.USE_SMA`)
- Calcul EMA conditionnel (`if config.USE_EMA`)
- Limite de bougies dynamique : `max(SMA_PERIODS + EMA_PERIODS)`
- Détection tendance adaptative (SMA seules, EMA seules, ou combinées)

```python
# Boucle principale adaptée
if config.USE_SMA:
    for period in config.SMA_PERIODS:
        sma = calculate_sma(df['close'], period)
        # ...

if config.USE_EMA:
    for period in config.EMA_PERIODS:
        ema = calculate_ema(df['close'], period)
        # ...
```

#### 3. **indicators.py - detect_trend()**

- **Avant** : Nécessitait TOUS les paramètres (sma20, sma50, ema20, ema50)
- **Après** : Paramètres optionnels avec valeurs par défaut `None`

```python
def detect_trend(prices, sma20=None, sma50=None, ema20=None, ema50=None):
    """
    Détection flexible :
    - SMA uniquement : Prix > SMA20 ET Prix > SMA50
    - EMA uniquement : EMA20 > EMA50
    - Les deux : L'une OU l'autre condition
    """
    has_sma = sma20 is not None and sma50 is not None
    has_ema = ema20 is not None and ema50 is not None
    
    conditions = []
    if has_sma:
        conditions.append(price > sma20 and price > sma50)
    if has_ema:
        conditions.append(ema20 > ema50)
    
    return any(conditions)  # Haussier si au moins 1 condition vraie
```

#### 4. **output.py**

- Export CSV adapté : colonnes SMA et/ou EMA selon config
- Ordre colonnes : `sma{period}_{tf}` puis `ema{period}_{tf}`

```python
for tf in config.MA_TIMEFRAMES:
    if config.USE_SMA:
        for period in config.SMA_PERIODS:
            columns_order.append(f'sma{period}_{tf}')
    
    if config.USE_EMA:
        for period in config.EMA_PERIODS:
            columns_order.append(f'ema{period}_{tf}')
```

---

## 📊 Structure CSV selon Configuration

### SMA + EMA (20/50) - 24 colonnes

```md
symbol, rsi, price, time, timeframe, trend_score,
sma20_1w, sma50_1w, ema20_1w, ema50_1w,
sma20_1d, sma50_1d, ema20_1d, ema50_1d,
sma20_4h, sma50_4h, ema20_4h, ema50_4h,
trend_1w, trend_1d, trend_4h,
rsi_period, rsi_threshold, scan_date
```

### SMA uniquement (20/50/100) - 21 colonnes

```md
symbol, rsi, price, time, timeframe, trend_score,
sma20_1w, sma50_1w, sma100_1w,
sma20_1d, sma50_1d, sma100_1d,
sma20_4h, sma50_4h, sma100_4h,
trend_1w, trend_1d, trend_4h,
rsi_period, rsi_threshold, scan_date
```

### EMA uniquement (9/21) - 18 colonnes

```md
symbol, rsi, price, time, timeframe, trend_score,
ema9_1w, ema21_1w,
ema9_1d, ema21_1d,
ema9_4h, ema21_4h,
trend_1w, trend_1d, trend_4h,
rsi_period, rsi_threshold, scan_date
```

⚠️ **Note** : Si périodes 20/50 absentes, `trend_X` sera `None`

---

## 🎯 Détection de Tendance

### Exigences Minimales

Pour que `detect_trend()` fonctionne, il faut **AU MOINS** :

#### Option A : SMA 20 et 50

```python
USE_SMA = True
SMA_PERIODS = [20, 50]  # ou [20, 50, 100, ...]
```

#### Option B : EMA 20 et 50

```python
USE_EMA = True
EMA_PERIODS = [20, 50]  # ou [9, 20, 50, ...]
```

#### Option C : Les deux

```python
USE_SMA = True
USE_EMA = True
SMA_PERIODS = [20, 50]
EMA_PERIODS = [20, 50]
```

### Logique de Détection

| Config             | Condition Haussière                               |
|--------------------|---------------------------------------------------|
| SMA seules (20/50) | Prix > SMA20 ET Prix > SMA50                      |
| EMA seules (20/50) | EMA20 > EMA50                                     |
| SMA + EMA          | (Prix > SMA20 ET Prix > SMA50) OU (EMA20 > EMA50) |

**Important** : Si vous utilisez d'autres périodes (ex: 9/21), ajoutez 20/50 :

```python
# ❌ Ne fonctionnera pas pour détection
EMA_PERIODS = [9, 21]

# ✅ Fonctionne
EMA_PERIODS = [9, 20, 21, 50]  # Détection avec 20/50, analyse avec 9/21
```

---

## 📈 Impact Performance

| Configuration            | Colonnes | Calculs Locaux | Vitesse |
|--------------------------|----------|----------------|---------|
| SMA+EMA (20/50) × 3 TF   | 24       | 4 × 3 TF       | ⏱️      |
| SMA (20/50/100) × 3 TF   | 21       | 3 × 3 TF       | ⏱️      |
| EMA (9/21) × 3 TF        | 18       | 2 × 3 TF       | ⚡      |
| SMA+EMA (4 périodes) × 3 | 30       | 8 × 3 TF       | ⏱️      |

**Note** :

- Nombre de périodes ≠ vitesse scan (calcul local instantané)
- Vitesse dépend du nombre d'appels API (timeframes)
- Plus de colonnes = fichier CSV plus gros

---

## 🧪 Tests et Validation

### Test automatique

Créez `test_ma_config.py` :

```python
import config

# Test 1 : SMA uniquement
config.USE_SMA = True
config.USE_EMA = False
config.SMA_PERIODS = [20, 50]
config.MAX_PAIRS = 3

from main import main
print("\n=== TEST 1: SMA UNIQUEMENT ===")
main()

# Test 2 : EMA uniquement
config.USE_SMA = False
config.USE_EMA = True
config.EMA_PERIODS = [20, 50]

print("\n=== TEST 2: EMA UNIQUEMENT ===")
main()

# Test 3 : Les deux
config.USE_SMA = True
config.USE_EMA = True

print("\n=== TEST 3: SMA + EMA ===")
main()
```

```bash
python test_ma_config.py
```

### Validation manuelle

```bash
# Vérifier config actuelle
python -c "import config; print('SMA:', config.USE_SMA, config.SMA_PERIODS if config.USE_SMA else 'OFF'); print('EMA:', config.USE_EMA, config.EMA_PERIODS if config.USE_EMA else 'OFF')"
```

---

## 📖 Documentation Créée

### Nouveaux fichiers

1. **[docs/CONFIGURATION_MA.md](docs/CONFIGURATION_MA.md)**
   - 8 configurations détaillées
   - Guide des périodes courantes (9/12/20/50/100/200)
   - Stratégies par profil (day trading, swing, long terme)
   - Explications détection de tendance
   - Impact performance

### Fichiers mis à jour

1. **[README.md](README.md)**
   - Section MA enrichie avec USE_SMA/USE_EMA
   - Lien vers CONFIGURATION_MA.md

2. **[config.py](config.py)**
   - Nouveaux paramètres documentés
   - Commentaires explicatifs

---

## 🎯 Cas d'Usage Recommandés

| Profil                 | Configuration                                           |
|------------------------|---------------------------------------------------------|
| **Débutant**           | SMA+EMA 20/50 (défaut)                                  |
| **Day Trader**         | EMA 9/21 (+ 20/50 pour détection)                       |
| **Swing Trader**       | SMA+EMA 20/50, timeframes 1d+4h                         |
| **Investisseur LT**    | SMA 50/100/200, timeframes 1w+1d                        |
| **Analyste technique** | SMA+EMA custom selon stratégie                          |
| **Performance**        | SMA 20/50, 1 timeframe                                  |

---

## ✅ Checklist Implémentation

- [x] Paramètres USE_SMA et USE_EMA dans config.py
- [x] Paramètres SMA_PERIODS et EMA_PERIODS séparés
- [x] Scanner adapté pour calculs conditionnels
- [x] detect_trend() avec paramètres optionnels
- [x] Output CSV avec colonnes adaptatives
- [x] Logs affichant types MA actifs
- [x] Documentation complète (CONFIGURATION_MA.md)
- [x] README mis à jour
- [x] Exemples de configurations
- [x] Tests manuels réussis

---

## 🚀 Utilisation

### Configuration rapide

```python
# config.py

# Exemple 1 : SMA uniquement pour stabilité
USE_SMA = True
USE_EMA = False
SMA_PERIODS = [20, 50, 100]

# Exemple 2 : EMA uniquement pour réactivité
USE_SMA = False
USE_EMA = True
EMA_PERIODS = [9, 20, 21, 50]

# Exemple 3 : Combiné optimal (défaut)
USE_SMA = True
USE_EMA = True
SMA_PERIODS = [20, 50]
EMA_PERIODS = [20, 50]
```

```bash
python main.py
```

### Test inline

```bash
python -c "
import config
config.USE_SMA = True
config.USE_EMA = False
config.SMA_PERIODS = [50, 200]
config.MAX_PAIRS = 5
from main import main
main()
"
```

---

## 💡 Conseils Pratiques

1. **Débutants** : Gardez config par défaut (SMA+EMA 20/50)
2. **Détection** : Incluez toujours 20 et 50 dans au moins un type
3. **Périodes** : Utilisez multiples (20/50, 50/100, 50/200)
4. **Timeframes** : 2-3 suffisent (1w+1d ou 1d+4h)
5. **SMA = long terme** : Plus stable, moins de faux signaux
6. **EMA = court terme** : Plus réactif, meilleur pour trading actif
7. **Testez** : MAX_PAIRS=5 avant scan complet

---

## 🔜 Évolutions Possibles

- [ ] WMA (Weighted Moving Average)
- [ ] SMMA (Smoothed Moving Average)
- [ ] VWMA (Volume Weighted MA)
- [ ] Périodes Fibonacci automatiques (21, 55, 89, 144)
- [ ] Détection avec autres combinaisons (10/30, 5/20)
- [ ] Croisements historiques (golden/death cross récents)
- [ ] Optimisation automatique périodes par paire

---

## 📌 Résumé

✅ **Configuration flexible SMA/EMA**  
✅ **Périodes indépendantes par type**  
✅ **Détection tendance adaptative**  
✅ **Export CSV optimisé**  
✅ **Documentation complète**  
✅ **Rétrocompatible**  
✅ **8 configurations MA documentées**

🎯 **Personnalisation totale des moyennes mobiles !**
