# Rapport Technique — Intégration Continue

**Projet :** NTL-SysToolbox
**Équipe :** Ianis PUICHAUD, Zaid ABOUYAALA, Ojvind LANTSIGBLE, Blaise WANDA NKONG
**Date :** Février 2026
**Cours :** Intégration Continue (TPRE511)

---

## 1. Introduction

### 1.1 Contexte

Le projet NTL-SysToolbox est un outil d'administration système développé en Python pour le parc informatique de NordTransit Logistics (NTL), une PME de logistique implantée dans les Hauts-de-France. Il est composé de trois modules indépendants (diagnostic, backup, audit) développés en parallèle par quatre personnes.

Ce contexte multi-développeurs nécessite un mécanisme automatisé pour :
- Vérifier que le code de chacun respecte les mêmes standards
- Détecter les régressions avant l'intégration sur la branche principale
- Garantir la qualité du code tout au long du cycle de développement

### 1.2 Objectif

Mettre en place une pipeline d'intégration continue (CI) qui valide automatiquement chaque contribution au projet, sans intervention manuelle.

---

## 2. Choix techniques

### 2.1 Plateforme : GitHub Actions

| Critère | GitHub Actions | GitLab CI | Jenkins |
|---------|---------------|-----------|---------|
| Intégration avec le repo | Native (même plateforme) | Nécessite migration | Serveur externe |
| Coût | Gratuit (2000 min/mois) | Gratuit (400 min/mois) | Auto-hébergé |
| Configuration | Fichier YAML dans le repo | Fichier YAML dans le repo | Interface web + Groovy |
| Maintenance | Zéro (SaaS) | Zéro (SaaS) | Lourde (serveur à gérer) |

**Justification :** Le repository étant hébergé sur GitHub, GitHub Actions offre l'intégration la plus naturelle sans infrastructure supplémentaire. Les 2000 minutes gratuites mensuelles sont largement suffisantes pour un projet de cette taille.

### 2.2 Outils de qualité

| Outil | Rôle | Justification |
|-------|------|---------------|
| **Ruff** | Linter Python | Rapide (écrit en Rust), remplace flake8 + isort en un seul outil |
| **Mypy** | Vérification de types | Détecte les erreurs de typage avant l'exécution |
| **Pytest** | Framework de tests | Standard Python, écosystème riche (plugins, fixtures) |
| **pytest-cov** | Couverture de code | Mesure le pourcentage de code couvert par les tests |

---

## 3. Architecture de la pipeline

### 3.1 Déclenchement

```yaml
on:
  push:
    branches: [main, master, "feature/*"]
  pull_request:
    branches: [main, master]
```

La pipeline se déclenche dans deux cas :
- **Push** sur `main`, `master`, ou toute branche `feature/*`
- **Pull Request** ouverte vers `main` ou `master`

Ce choix permet à chaque développeur d'avoir un retour immédiat sur sa branche feature, tout en validant également les pull requests avant merge.

### 3.2 Jobs

La pipeline comprend **deux jobs qui s'exécutent en parallèle** :

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

| Étape | Commande | Description |
|-------|----------|-------------|
| Checkout | `actions/checkout@v4` | Clone le repository |
| Setup Python | `actions/setup-python@v5` | Installe Python 3.10 avec cache pip |
| Install deps | `pip install -r requirements-dev.txt` | Installe les dépendances + outils dev |
| Lint | `ruff check src/ tests/` | Vérifie le style et les erreurs statiques |
| Type check | `mypy src/ --ignore-missing-imports` | Vérifie la cohérence des types |

#### Job 2 — Tests

| Étape | Commande | Description |
|-------|----------|-------------|
| Checkout | `actions/checkout@v4` | Clone le repository |
| Setup Python | `actions/setup-python@v5` | Installe Python (matrice 3.10/3.11/3.12) |
| Install deps | `pip install -r requirements-dev.txt` | Installe les dépendances |
| Tests | `pytest tests/ -v --cov=src --cov-report=xml --cov-report=term-missing` | Exécute les tests avec couverture |
| Artefact | `actions/upload-artifact@v4` | Upload le rapport de couverture |

### 3.3 Stratégie de matrice

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
```

La matrice exécute les tests sur **trois versions de Python en parallèle**. Cela garantit la compatibilité du code et détecte les éventuelles différences de comportement entre versions.

### 3.4 Artefacts

Le rapport de couverture (`coverage.xml`) est uploadé comme artefact GitHub. Il est consultable dans l'onglet Actions du repository et permet de suivre l'évolution de la couverture de tests au fil du temps.

---

## 4. Gestion des dépendances

### 4.1 Séparation runtime / dev

Les dépendances sont séparées en deux fichiers :

**`requirements.txt`** — Dépendances d'exécution :
```
rich, mysql-connector-python, paramiko, dnspython,
python-nmap, pyyaml, psutil, ldap3, python-dotenv
```

**`requirements-dev.txt`** — Dépendances de développement :
```
-r requirements.txt     # inclut les deps runtime
pytest, pytest-cov, ruff, mypy
```

**Justification :** Cette séparation évite d'installer les outils de dev en production et clarifie ce qui est nécessaire pour exécuter l'application vs. pour la développer.

### 4.2 Configuration centralisée

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
check_untyped_defs = true

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

Chaque développeur est responsable des tests de son module. La pipeline exécute **tous les tests** à chaque run, ce qui détecte les régressions croisées.

### 5.2 Tests existants

Le module `interfaces.py` (contrat commun entre modules) dispose de **12 tests** couvrant :
- Les codes de sortie (EXIT_OK, EXIT_WARNING, EXIT_CRITICAL, EXIT_UNKNOWN)
- La fonction `build_result()` (structure, valeurs, format timestamp)
- Les exceptions personnalisées (ModuleConfigError, ModuleExecutionError)

**Couverture actuelle :** 100% sur `interfaces.py`.

### 5.3 Couverture de code

La couverture est mesurée avec `pytest-cov` et exportée en XML. Elle mesure le pourcentage de lignes de code exécutées par les tests. La couverture augmentera au fur et à mesure que les modules seront développés et testés.

---

## 6. Workflow de développement

### 6.1 Cycle de vie d'une contribution

```
1. Le dev crée sa branche        git checkout -b feature/diagnostic
2. Le dev code + teste            make lint && make test
3. Le dev push                    git push origin feature/diagnostic
4. La CI tourne automatiquement   GitHub Actions vérifie lint + tests
5. Le dev ouvre une PR            feature/diagnostic → main
6. La CI re-tourne sur la PR      Validation avant merge
7. Le Lead review + merge         Squash merge sur main
```

### 6.2 Commandes locales

| Commande | Description |
|----------|-------------|
| `make setup-dev` | Installe les outils de dev |
| `make lint` | Vérifie le style du code |
| `make typecheck` | Vérifie les types Python |
| `make test` | Lance les tests avec couverture |

Les développeurs sont encouragés à lancer `make lint && make test` avant chaque push pour éviter les échecs CI.

---

## 7. Résultats et métriques

### 7.1 Temps d'exécution

Chaque run de la pipeline dure environ **1 à 2 minutes**, ce qui permet un feedback rapide sans bloquer le workflow de développement.

### 7.2 Visibilité

- **Badge CI** dans le README : indique l'état de la branche principale
- **Checks sur les PR** : chaque PR affiche le statut des checks (vert/rouge)
- **Onglet Actions** : historique complet de tous les runs avec logs détaillés

---

## 8. Conclusion

La pipeline CI mise en place garantit un niveau de qualité constant tout au long du développement. Elle automatise trois vérifications essentielles :

1. **Qualité du code** (lint) — standards de style et erreurs statiques
2. **Cohérence des types** (type check) — détection des erreurs de typage
3. **Comportement fonctionnel** (tests) — validation des fonctionnalités sur 3 versions Python

Cette approche permet à l'équipe de se concentrer sur le développement tout en ayant l'assurance que chaque contribution est validée automatiquement avant intégration.
