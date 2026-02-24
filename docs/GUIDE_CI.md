# Guide CI/CD — NTL-SysToolbox

## Comment ca marche

On utilise **GitHub Actions** pour verifier automatiquement le code a chaque push.

### Quand la CI tourne

| Evenement | Branches concernees |
|-----------|-------------------|
| `git push` | `main`, `master`, `feature/*` |
| Ouverture d'une PR | vers `main` ou `master` |

**Exemple concret :**
```
Tu push sur feature/diagnostic  →  CI tourne
Tu push sur docs/readme         →  CI ne tourne PAS
Tu ouvres une PR vers main      →  CI tourne
```

### Ce que la CI verifie

La pipeline lance **2 jobs en parallele** :

**Job 1 — Lint & Type Check**
- **Ruff** : verifie le style du code (imports tries, variables inutilisees, etc.)
- **Mypy** : verifie les types Python (type hints)

**Job 2 — Tests**
- Lance `pytest` sur **3 versions de Python** (3.10, 3.11, 3.12)
- Genere un rapport de couverture de code
- Upload le rapport en artefact sur GitHub

### Ou voir les resultats

1. Aller sur la page du repo GitHub
2. Onglet **Actions** → voir les runs
3. Ou directement sur ta **PR** → les checks apparaissent en bas

```
✅ Lint & Type Check        — passed
✅ Tests (Python 3.10)      — passed
✅ Tests (Python 3.11)      — passed
✅ Tests (Python 3.12)      — passed
```

Si un check est rouge, cliquer dessus pour voir le detail de l'erreur.

---

## Commandes locales

Avant de push, tu peux lancer les memes verifications en local :

```bash
# Installer les outils de dev (une seule fois)
make setup-dev

# Lancer le linter
make lint

# Lancer le type checker
make typecheck

# Lancer les tests avec couverture
make test
```

**Conseil : lance `make lint && make test` avant chaque push.** Ca evite de decouvrir les erreurs sur GitHub.

---

## Erreurs courantes et solutions

### Ruff : import non utilise (F401)

```
F401 `os` imported but unused
```

**Solution :** Supprimer l'import inutile, ou ajouter `# noqa: F401` si c'est voulu (ex: template).

### Ruff : imports mal tries (I001)

```
I001 Import block is un-sorted or un-formatted
```

**Solution :** Lancer `ruff check --fix src/ tests/` pour corriger automatiquement.

### Mypy : module introuvable

```
Cannot find implementation or library stub for module named "xxx"
```

**Solution :** Normal pour les libs externes (mysql-connector, paramiko...). On a `ignore_missing_imports = true` dans `pyproject.toml`, donc ca ne devrait pas apparaitre.

### Pytest : test qui echoue

```
FAILED tests/test_diagnostic.py::test_check_dns - AssertionError
```

**Solution :** Lire le message d'erreur, corriger le code ou le test, re-push.

---

## Structure des fichiers CI

```
.github/workflows/ci.yml   ← Pipeline principale
pyproject.toml              ← Config ruff + mypy + pytest
requirements-dev.txt        ← Dependencies dev (ruff, mypy, pytest-cov)
tests/                      ← Dossier des tests
  __init__.py
  test_interfaces.py        ← Tests du module commun (deja fait)
  test_diagnostic.py        ← A creer par le dev Diagnostic
  test_backup.py            ← A creer par le dev Backup
  test_audit.py             ← A creer par le dev Audit
```

---

## Ecrire un test pour ton module

Chaque dev doit ecrire les tests de son module. Exemple pour le module diagnostic :

```python
# tests/test_diagnostic.py
from src.modules.diagnostic import check_dns

def test_check_dns_returns_ok_on_valid_target():
    result = check_dns(config={...}, target="dc01.ntl.local")
    assert result["status"] == "OK"
    assert result["exit_code"] == 0
    assert result["module"] == "diagnostic"

def test_check_dns_returns_unknown_on_unreachable():
    result = check_dns(config={...}, target="fake.host")
    assert result["status"] == "UNKNOWN"
    assert result["exit_code"] == 3
```

**Regles :**
- Un fichier `test_<module>.py` par module
- Chaque fonction publique doit avoir au moins 1 test OK et 1 test erreur
- Utiliser `build_result()` dans le module → le test verifie la structure du retour

---

## FAQ

**Q: La CI echoue mais mon code marche en local ?**
A: Verifier que tu as bien push tous les fichiers. La CI clone le repo depuis zero.

**Q: Comment voir le rapport de couverture ?**
A: Onglet Actions → cliquer sur le run → section Artifacts → telecharger `coverage-report`.

**Q: Je peux ignorer un check ruff ?**
A: Oui avec `# noqa: XXXX` en fin de ligne. Mais c'est mieux de corriger.

**Q: La CI prend combien de temps ?**
A: ~1-2 minutes par run.
