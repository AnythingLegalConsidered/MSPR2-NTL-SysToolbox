# Interfaces — Le contrat commun à tous les modules

> Fichier : `src/interfaces.py`
> Rôle : Définir les règles que TOUS les modules doivent respecter.

## Les exit codes

Chaque résultat de module a un code de sortie standardisé :

| Code | Nom | Signification | Exemple |
|------|-----|---------------|---------|
| `0` | OK | Tout fonctionne | MySQL répond, CPU < 80% |
| `1` | WARNING | Dégradation, pas critique | RAM à 85% |
| `2` | CRITICAL | Service down, échec | MySQL ne répond pas |
| `3` | UNKNOWN | Impossible de vérifier | Serveur injoignable, timeout |

## build_result() — La fonction obligatoire

Chaque fonction de module **doit** retourner un résultat via `build_result()`. C'est le format standard.

```python
from src.interfaces import build_result, EXIT_OK

result = build_result(
    module="diagnostic",           # Nom du module
    function="check_ad_dns",       # Nom de la fonction
    status="OK",                   # OK, WARNING, CRITICAL, UNKNOWN
    exit_code=EXIT_OK,             # 0, 1, 2 ou 3
    target="192.168.10.10",        # La cible testée
    details={"ldap": True, "dns": True},  # Données spécifiques
    message="AD et DNS opérationnels",     # Message lisible
)
```

### Ce que ça produit

```json
{
  "module": "diagnostic",
  "function": "check_ad_dns",
  "timestamp": "2026-02-26T14:30:00Z",
  "status": "OK",
  "exit_code": 0,
  "target": "192.168.10.10",
  "details": {
    "ldap": true,
    "dns": true
  },
  "message": "AD et DNS opérationnels"
}
```

Le `timestamp` est ajouté automatiquement (UTC, format ISO 8601).

## Les exceptions

Deux exceptions custom pour signaler les erreurs :

| Exception | Quand la lever | Qui la gère |
|-----------|---------------|-------------|
| `ModuleConfigError` | Config manquante ou invalide | `main.py` affiche l'erreur |
| `ModuleExecutionError` | Le module plante pendant l'exécution | `main.py` affiche l'erreur |

```python
from src.interfaces import ModuleConfigError

# Exemple : vérifier que la config MySQL existe
if "mysql" not in config:
    raise ModuleConfigError("Section 'mysql' manquante dans la config")
```

## Résumé des règles

1. Toute fonction de module retourne `build_result()`
2. Tout crash est attrapé (try/except) et retourné en status `UNKNOWN` ou `CRITICAL`
3. Les exit codes suivent la convention (0-3)
4. Les exceptions config/exécution sont les seules qui remontent à `main.py`
