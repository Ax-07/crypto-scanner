# 🎯 Scanner Binance - Choix des Indicateurs

## Date : 17 janvier 2026

## Fonctionnalité : Sélection flexible des indicateurs

---

## 📝 Résumé

Ajout d'une fonctionnalité permettant de **choisir les indicateurs à utiliser** pour le scan via configuration simple.

Avant, le scanner utilisait toujours RSI + MA (si `ENABLE_MA=True`).  
Maintenant, vous pouvez activer/désactiver chaque type d'indicateur indépendamment.

---

## ⚙️ Nouveaux Paramètres (config.py)

```python
# ============================
# INDICATEURS À UTILISER
# ============================
USE_RSI = True   # Activer le calcul et le filtrage RSI
USE_MA = True    # Activer le calcul des moyennes mobiles
```

### Changements de nommage

- `ENABLE_MA` → remplacé par `USE_MA` (cohérence avec `USE_RSI`)
- Ancienne config continue de fonctionner (mais `USE_MA` recommandé)

---

## 🎨 4 Modes de Scan Possibles

### 1️⃣ RSI uniquement (V1 classique)

```python
USE_RSI = True
USE_MA = False
```

**Utilité** : Scanner simple et rapide des paires survendues  
**Résultats** : Paires avec RSI < seuil, triées par RSI  
**Performance** : ⚡ Très rapide (1 appel API par paire)

---

### 2️⃣ Moyennes Mobiles uniquement

```python
USE_RSI = False
USE_MA = True
```

**Utilité** : Trouver les paires en tendance haussière  
**Résultats** : Paires avec trend_score ≥ MIN_TREND_SCORE  
**Performance** : ⏱️ Moyen (4 appels API par paire - 3 TF + RSI TF pour prix)

---

### 3️⃣ RSI + MA (V1.5 optimal) ⭐

```python
USE_RSI = True
USE_MA = True
```

**Utilité** : Opportunités de haute qualité (survendu + tendance)  
**Résultats** : Paires avec RSI < seuil ET trend_score ≥ MIN_TREND_SCORE  
**Performance** : ⏱️ Moyen (4 appels API par paire)  
**📌 Configuration recommandée**

---

### 4️⃣ Aucun indicateur (liste brute)

```python
USE_RSI = False
USE_MA = False
```

**Utilité** : Lister toutes les paires sans filtrage  
**Résultats** : Toutes les paires du scope  
**Performance** : ⚡ Rapide (1 appel API par paire pour prix)  
**⚠️ Configuration peu utile en pratique**

---

## 🔧 Modifications Techniques

### Fichiers modifiés

1. **config.py**
   - Ajout section `INDICATEURS À UTILISER`
   - `USE_RSI` et `USE_MA` remplacent `ENABLE_MA`

2. **scanner.py**
   - Calcul RSI conditionnel (if `USE_RSI`)
   - Calcul MA conditionnel (if `USE_MA`)
   - Filtrage adapté selon indicateurs actifs
   - Tri intelligent : RSI si actif, sinon trend_score, sinon symbol
   - Logs enrichis montrant indicateurs actifs

3. **output.py**
   - Affichage console adapté selon colonnes disponibles
   - Titre dynamique selon filtres actifs
   - Export CSV avec colonnes optionnelles
   - Gestion des valeurs `None` pour colonnes absentes

4. **indicators.py**
   - Aucun changement (fonctions pures inchangées)

### Comportements clés

**Calcul RSI** :

- Si `USE_RSI=True` : calcul normal + filtrage par seuil
- Si `USE_RSI=False` : pas de calcul, récupération prix uniquement

**Calcul MA** :

- Si `USE_MA=True` : analyse multi-timeframe complète
- Si `USE_MA=False` : aucun calcul MA, fonction retourne `None`

**Filtrage** :

- `USE_RSI=True` : filtre `RSI < threshold` appliqué
- `USE_MA=True` : filtre `trend_score >= MIN_TREND_SCORE` appliqué
- Les deux : filtre combiné (ET logique)
- Aucun : toutes les paires passent

**Tri des résultats** :

```python
if USE_RSI and 'rsi' in results:
    sort by rsi ascending
elif USE_MA and 'trend_score' in results:
    sort by trend_score descending
else:
    sort by symbol alphabetically
```

---

## 📊 Colonnes CSV selon Configuration

### RSI uniquement

- symbol, rsi, last_close_price, last_close_time, timeframe
- rsi_period, rsi_threshold, scan_date

### MA uniquement

- symbol, last_close_price, last_close_time, timeframe
- sma20_1w, sma50_1w, ema20_1w, ema50_1w (× 3 TF)
- trend_1w, trend_1d, trend_4h, trend_score
- scan_date

### RSI + MA (complet)

- **24 colonnes** : toutes les colonnes ci-dessus combinées

### Aucun indicateur

- symbol, last_close_price, last_close_time, timeframe
- scan_date

---

## 🧪 Fichier de Test

**test_configurations.py** : Teste les 4 modes automatiquement

```bash
python test_configurations.py
```

Valide :

- ✅ Chaque mode s'exécute sans erreur
- ✅ Les colonnes présentes correspondent aux indicateurs actifs
- ✅ Pas de colonnes inattendues

---

## 📖 Documentation

### Nouveaux fichiers

1. **docs/CONFIGURATIONS_EXEMPLES.md**
   - 8 configurations détaillées
   - Cas d'usage : swing trading, day trading, long terme
   - Paramètres recommandés par profil

### Fichiers mis à jour

1. **README.md**
   - Section "Choix des indicateurs" ajoutée
   - Lien vers CONFIGURATIONS_EXEMPLES.md

2. **docs/cahier_des_charges_scanner.md**
   - Statut V1.5 mis à jour (✅ COMPLÈTE)
   - Mention du choix des indicateurs

---

## 🎯 Cas d'Usage Recommandés

| Profil                | Config recommandée | Indicateurs        |
|-----------------------|--------------------|--------------------|
| **Débutant**          | Config 3           | RSI + MA           |
| **Day Trader**        | Config 1 ou 3      | RSI (±MA)          |
| **Swing Trader**      | Config 3           | RSI + MA           |
| **Investisseur LT**   | Config 2 ou 3      | MA (±RSI)          |
| **Analyse technique** | Config 2           | MA seules          |
| **Tests rapides**     | Config 1           | RSI uniquement     |

---

## ✅ Validation

### Tests manuels effectués

- [x] Config 1 (RSI seul) : fonctionne ✅
- [x] Config 2 (MA seules) : fonctionne ✅
- [x] Config 3 (RSI+MA) : fonctionne ✅
- [x] Config 4 (aucun) : fonctionne ✅

### Tests automatisés

```bash
python test_configurations.py
```

**Résultat attendu** : 4/4 tests réussis ✅

---

## 🚀 Utilisation

### Méthode 1 : Modifier config.py

```python
# config.py
USE_RSI = True   # Changer selon besoin
USE_MA = False   # Changer selon besoin
```

```bash
python main.py
```

### Méthode 2 : Test rapide inline

```bash
python -c "import config; config.USE_RSI=False; config.USE_MA=True; config.MAX_PAIRS=5; from main import main; main()"
```

### Méthode 3 : Créer des fichiers de config

```bash
# config_rsi_only.py
from config import *
USE_RSI = True
USE_MA = False
```

```bash
# Copier config_rsi_only.py vers config.py avant scan
```

---

## 📈 Impact Performance

| Configuration | Appels API/paire | Vitesse relative | Recommandé pour         |
|---------------|------------------|------------------|-------------------------|
| RSI seul      | 1                | Très rapide      | Scan quotidien rapide   |
| MA seules     | 4                | Moyen            | Analyse tendance hebdo  |
| RSI + MA      | 4                | Moyen            | Scan complet journalier |
| Aucun         | 1                | Très rapide      | Liste complète (rare)   |

**Note** : Les rate limits sont gérés automatiquement par CCXT

---

## 🔜 Évolutions Possibles

- [ ] Ajouter `USE_VOLUME` pour filtrer par volume
- [ ] Ajouter `USE_VOLATILITY` pour filtrer par ATR
- [ ] Permettre combinaison OU en plus de ET (`RSI < 30 OR trend=3`)
- [ ] Config presets : `--preset=swing`, `--preset=daytrading`
- [ ] Interface CLI : `python main.py --rsi --no-ma`

---

## 📌 Notes Importantes

1. **Compatibilité** : Toutes les anciennes configs fonctionnent toujours
2. **Par défaut** : `USE_RSI=True` et `USE_MA=True` (V1.5 optimal)
3. **Performance** : Désactiver MA si scan très rapide nécessaire
4. **Qualité** : RSI+MA donne meilleurs résultats mais plus lent
5. **Rate limits** : Respectés automatiquement, aucune action requise

---

## 🎉 Résumé

✅ **Fonctionnalité implémentée et testée**  
✅ **4 modes de scan disponibles**  
✅ **Documentation complète (exemples + README)**  
✅ **Tests automatisés créés**  
✅ **Rétrocompatible**  
✅ **Performance optimisée**

🎯 **Scanner maintenant 100% flexible et configurable !**
