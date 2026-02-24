# Rapport Technique — Integration Continue

**Projet :** NTL-SysToolbox
**Equipe :** Ianis PUICHAUD, Zaid ABOUYAALA, Ojvind LANTSIGBLE, Blaise WANDA NKONG
**Date :** Fevrier 2026
**Cours :** Integration Continue (TPRE511)

---

## 1. Introduction

### 1.1 Contexte

Le projet NTL-SysToolbox est un outil d'administration systeme developpe en Python pour le parc informatique de NovaTech Logistics. Il est compose de trois modules independants (diagnostic, backup, audit) developpes en parallele par quatre personnes.

Ce contexte multi-developpeurs necessite un mecanisme automatise pour :
- Verifier que le code de chacun respecte les memes standards
- Detecter les regressions avant l'integration sur la branche principale
- Garantir la qualite du code tout au long du cycle de developpement

### 1.2 Objectif

Mettre en place une pipeline d'integration continue (CI) qui valide automatiquement chaque contribution au projet, sans intervention manuelle.

---

## 2. Choix techniques

### 2.1 Plateforme : GitHub Actions

| Critere | GitHub Actions | GitLab CI | Jenkins |
|---------|---------------|-----------|---------|
| Integration avec le repo | Native (meme plateforme) | Necessite migration | Serveur externe |
| Cout | Gratuit (2000 min/mois) | Gratuit (400 min/mois) | Auto-heberge |
| Configuration | Fichier YAML dans le repo | Fichier YAML dans le repo | Interface web + Groovy |
| Maintenance | Zero (SaaS) | Zero (SaaS) | Lourde (serveur a gerer) |

**Justification :** Le repository etant heberge sur GitHub, GitHub Actions offre l'integration la plus naturelle sans infrastructure supplementaire. Les 2000 minutes gratuites mensuelles sont largement suffisantes pour un projet de cette taille.

### 2.2 Outils de qualite

| Outil | Role | Justification |
|-------|------|---------------|
| **Ruff** | Linter Python | Rapide (ecrit en Rust), remplace flake8 + isort en un seul outil |
| **Mypy** | Verification de types | Detecte les erreurs de typage avant l'execution |
| **Pytest** | Framework de tests | Standard Python, ecosysteme riche (plugins, fixtures) |
| **pytest-cov** | Couverture de code | Mesure le pourcentage de code couvert par les tests |

---

## 3. Architecture de la pipeline

### 3.1 Declenchement

```yaml
on:
  push:
    branches: [main, master, "feature/*"]
  pull_request:
    branches: [main, master]
```

La pipeline se declenche dans deux cas :
- **Push** sur `main`, `master`, ou toute branche `feature/*`
- **Pull Request** ouverte vers `main` ou `master`

Ce choix permet a chaque developpeur d'avoir un retour immediat sur sa branche feature, tout en validant egalement les pull requests avant merge.

### 3.2 Jobs

La pipeline comprend **deux jobs qui s'executent en parallele** :

```
                    ┌──────────────────────┐
  git push ────────►│   GitHub Actions      │
                    │                      │
                    │  ┌────────────────┐  │
                    │  │  Job: Lint     │  │  Ruff + Mypy
                    │  │  (1 instance)  │  │
                    │  └────────────────┘  │
                    │                      │
                    │  ┌────────────────┐  │
                    │  │  Job: Tests    │  │  Pytest + Coverage
                    │  │  (3 instances) │  │  Python 3.10 / 3.11 / 3.12
                    │  └────────────────┘  │
                    │                      │
                    └──────────────────────┘
```

#### Job 1 — Lint & Type Check

| Etape | Commande | Description |
|-------|----------|-------------|
| Checkout | `actions/checkout@v4` | Clone le repository |
| Setup Python | `actions/setup-python@v5` | Installe Python 3.10 avec cache pip |
| Install deps | `pip install -r requirements-dev.txt` | Installe les dependances + outils dev |
| Lint | `ruff check src/ tests/` | Verifie le style et les erreurs statiques |
| Type check | `mypy src/ --ignore-missing-imports` | Verifie la coherence des types |

#### Job 2 — Tests

| Etape | Commande | Description |
|-------|----------|-------------|
| Checkout | `actions/checkout@v4` | Clone le repository |
| Setup Python | `actions/setup-python@v5` | Installe Python (matrice 3.10/3.11/3.12) |
| Install deps | `pip install -r requirements-dev.txt` | Installe les dependances |
| Tests | `pytest tests/ -v --cov=src --cov-report=xml` | Execute les tests avec couverture |
| Artefact | `actions/upload-artifact@v4` | Upload le rapport de couverture |

### 3.3 Strategie de matrice

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
```

La matrice execute les tests sur **trois versions de Python en parallele**. Cela garantit la compatibilite du code et detecte les eventuelles differences de comportement entre versions.

### 3.4 Artefacts

Le rapport de couverture (`coverage.xml`) est uploade comme artefact GitHub. Il est consultable dans l'onglet Actions du repository et permet de suivre l'evolution de la couverture de tests au fil du temps.

---

## 4. Gestion des dependances

### 4.1 Separation runtime / dev

Les dependances sont separees en deux fichiers :

**`requirements.txt`** — Dependances d'execution :
```
rich, mysql-connector-python, paramiko, dnspython,
python-nmap, pyyaml, psutil, ldap3, python-dotenv
```

**`requirements-dev.txt`** — Dependances de developpement :
```
-r requirements.txt     # inclut les deps runtime
pytest, pytest-cov, ruff, mypy
```

**Justification :** Cette separation evite d'installer les outils de dev en production et clarifie ce qui est necessaire pour executer l'application vs. pour la developper.

### 4.2 Configuration centralisee

Le fichier `pyproject.toml` centralise la configuration de tous les outils :

```toml
[tool.ruff]
target-version = "py310"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "W", "I"]    # erreurs, pyflakes, warnings, imports

[tool.mypy]
python_version = "3.10"
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
```

---

## 5. Tests

### 5.1 Organisation

```
tests/
  __init__.py
  test_interfaces.py     ← Module commun (Lead)
  test_diagnostic.py     ← Module diagnostic (Dev Diagnostic)
  test_backup.py         ← Module backup (Dev Backup)
  test_audit.py          ← Module audit (Dev Audit)
```

Chaque developpeur est responsable des tests de son module. La pipeline execute **tous les tests** a chaque run, ce qui detecte les regressions croisees.

### 5.2 Tests existants

Le module `interfaces.py` (contrat commun entre modules) dispose de **12 tests** couvrant :
- Les codes de sortie (EXIT_OK, EXIT_WARNING, EXIT_CRITICAL, EXIT_UNKNOWN)
- La fonction `build_result()` (structure, valeurs, format timestamp)
- Les exceptions personnalisees (ModuleConfigError, ModuleExecutionError)

**Couverture actuelle :** 100% sur `interfaces.py`.

### 5.3 Couverture de code

La couverture est mesuree avec `pytest-cov` et exportee en XML. Elle mesure le pourcentage de lignes de code executees par les tests. La couverture augmentera au fur et a mesure que les modules seront developpes et testes.

---

## 6. Workflow de developpement

### 6.1 Cycle de vie d'une contribution

```
1. Le dev cree sa branche        git checkout -b feature/diagnostic
2. Le dev code + teste            make lint && make test
3. Le dev push                    git push origin feature/diagnostic
4. La CI tourne automatiquement   GitHub Actions verifie lint + tests
5. Le dev ouvre une PR            feature/diagnostic → main
6. La CI re-tourne sur la PR      Validation avant merge
7. Le Lead review + merge         Squash merge sur main
```

### 6.2 Commandes locales

| Commande | Description |
|----------|-------------|
| `make setup-dev` | Installe les outils de dev |
| `make lint` | Verifie le style du code |
| `make typecheck` | Verifie les types Python |
| `make test` | Lance les tests avec couverture |

Les developpeurs sont encourages a lancer `make lint && make test` avant chaque push pour eviter les echecs CI.

---

## 7. Resultats et metriques

### 7.1 Temps d'execution

Chaque run de la pipeline dure environ **1 a 2 minutes**, ce qui permet un feedback rapide sans bloquer le workflow de developpement.

### 7.2 Visibilite

- **Badge CI** dans le README : indique l'etat de la branche principale
- **Checks sur les PR** : chaque PR affiche le statut des checks (vert/rouge)
- **Onglet Actions** : historique complet de tous les runs avec logs detailles

---

## 8. Conclusion

La pipeline CI mise en place garantit un niveau de qualite constant tout au long du developpement. Elle automatise trois verifications essentielles :

1. **Qualite du code** (lint) — standards de style et erreurs statiques
2. **Coherence des types** (type check) — detection des erreurs de typage
3. **Comportement fonctionnel** (tests) — validation des fonctionnalites sur 3 versions Python

Cette approche permet a l'equipe de se concentrer sur le developpement tout en ayant l'assurance que chaque contribution est validee automatiquement avant integration.
