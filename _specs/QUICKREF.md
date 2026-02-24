# Quick Reference — NTL-SysToolbox

> Aide-memoire a garder ouvert pendant le dev. 1 page, l'essentiel.

## Mon module

| Champ | Valeur |
|-------|--------|
| Mon role | __________________ |
| Mon fichier | `src/modules/__________.py` |
| Ma branche | `feature/module-__________` |

---

## Commandes Git

```bash
# Creer ma branche
git checkout -b feature/module-<nom>

# Workflow quotidien
git add src/modules/<nom>.py
git commit -m "feat: add check_xxx()"
git push -u origin feature/module-<nom>    # Premier push
git push                                    # Push suivants

# Avant de merger
git checkout main && git pull
git checkout feature/module-<nom>
git rebase main                             # Mettre a jour ma branche
```

---

## Format de retour OBLIGATOIRE

```python
from src.interfaces import build_result, EXIT_OK, EXIT_WARNING, EXIT_CRITICAL, EXIT_UNKNOWN

return build_result(
    module="diagnostic",          # diagnostic | backup | audit
    function="check_ad_dns",      # nom de la fonction
    status="OK",                  # OK | WARNING | CRITICAL | UNKNOWN
    exit_code=EXIT_OK,            # 0 | 1 | 2 | 3
    target="192.168.10.10",       # IP ou hostname cible
    details={"ldap_port_389": True, "dns_resolution": True},
    message="AD/DNS operationnels sur DC01"
)
```

---

## Statuts et exit codes

| Status | Code | Quand |
|--------|------|-------|
| `OK` | 0 | Tout fonctionne |
| `WARNING` | 1 | CPU > 80%, RAM > 80%, Disque > 80% |
| `CRITICAL` | 2 | Service down, backup echoue, erreur fatale |
| `UNKNOWN` | 3 | Timeout (10s), cible injoignable |

---

## Convention de commits

```
feat: nouvelle fonctionnalite      fix: correction de bug
docs: documentation                test: ajout/modif tests
chore: maintenance (deps, CI...)   refactor: restructuration sans changement fonctionnel
```

---

## Commandes projet

```bash
make setup          # Creer venv + installer deps (Windows)
make setup-linux    # Idem Linux
make run            # Lancer le CLI
make test           # Lancer pytest
make clean          # Nettoyer les artefacts generes
```

---

## Si je suis bloque

1. Relire `PLAN_PROJET.md` section de mon module
2. Relire `src/modules/_template.py` pour le pattern
3. **Si > 30 min** : message sur le canal + ping le Lead

---

*Voir `WORKFLOW.md` pour les etapes | `DECISIONS.md` pour les choix valides*
