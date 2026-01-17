# 🚀 Guide de démarrage rapide

## Installation

### 1. Créer l'environnement virtuel

```powershell
python -m venv .venv
```

### 2. Activer l'environnement virtuel

```powershell
.venv\Scripts\activate
```

Vous devriez voir `(.venv)` au début de votre ligne de commande.

### 3. Installer les dépendances

```powershell
pip install -r requirements.txt
```

---

## Premier test

### Test des modules individuellement

```powershell
python test_modules.py
```

Ce script va tester chaque module séparément et afficher le résultat.

---

## Première exécution du scanner

### Mode test (limité à 10 paires)

Pour votre premier test, modifiez temporairement le fichier `config.py` :

```python
MAX_PAIRS = 10  # Au lieu de None
```

Puis lancez :

```powershell
python main.py
```

### Mode production (toutes les paires)

Une fois le test réussi, remettez dans `config.py` :

```python
MAX_PAIRS = None  # Scanner toutes les paires
```

Et relancez :

```powershell
python main.py
```

---

## Résultats

Les résultats seront :

1. **Affichés dans la console** sous forme de tableau
2. **Exportés dans** `outputs/rsi_scan.csv`
3. **Loggés dans** `logs/scanner.log`

---

## Configuration

Tous les paramètres sont dans [config.py](config.py).

Pour modifier le seuil RSI :

```python
RSI_THRESHOLD = 25  # Au lieu de 30
```

Pour changer le timeframe :

```python
TIMEFRAME = "1h"  # Au lieu de "4h"
```

---

## Arrêt du scanner

Utilisez `Ctrl+C` pour arrêter proprement le scanner en cours d'exécution.

---

## Dépannage

### Erreur "Module not found"

Vérifiez que l'environnement virtuel est activé :

```powershell
.venv\Scripts\activate
```

### Erreur de connexion Binance

Vérifiez votre connexion internet. Le scanner utilise l'API publique (pas besoin de clés).

### Rate limit dépassé

Le scanner gère automatiquement les rate limits. Si le problème persiste, augmentez `RETRY_DELAY` dans `config.py`.

---

## Support

Consultez :

- [README.md](README.md) pour la documentation complète
- [docs/cahier_des_charges_scanner.md](docs/cahier_des_charges_scanner.md) pour les spécifications
