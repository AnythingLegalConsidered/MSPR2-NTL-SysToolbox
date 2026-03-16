# Guide CI/CD — NTL-SysToolbox

> Ce document explique le concept de CI/CD, puis detaille ce qui est mis en place dans notre projet.
> Pour le rapport technique complet (livrable scolaire), voir le [Rapport technique CI](09-ci-report.md).

---

## 1. Comprendre CI/CD — Les concepts

### 1.1 C'est quoi la CI ? (Continuous Integration)

La **CI (Integration Continue)** est une pratique de developpement ou chaque modification de code est **automatiquement verifiee** par une machine, sans intervention humaine.

**Le principe est simple :**

```
Un dev push du code  →  Un serveur lance des verifications  →  Resultat : ✅ ou ❌
```

Les verifications typiques sont :
- **Linting** : le code respecte-t-il les regles de style ?
- **Type checking** : les types sont-ils coherents ?
- **Tests unitaires** : les fonctions retournent-elles les bons resultats ?
- **Build** : le projet compile-t-il sans erreur ?

**Pourquoi c'est utile :**
- On detecte les bugs **avant** qu'ils arrivent sur la branche principale
- Tout le monde respecte les memes standards de qualite
- Pas besoin d'un humain pour verifier chaque contribution a la main
- Le feedback est rapide (quelques minutes)

### 1.2 C'est quoi le CD ? (Continuous Delivery / Deployment)

Le **CD** est l'etape suivante de la CI :

| Terme | Signification | Exemple |
|-------|--------------|---------|
| **Continuous Delivery** (Livraison Continue) | Le code est automatiquement pret a etre deploye (mais un humain decide quand) | Un bouton "Deploy" a cliquer |
| **Continuous Deployment** (Deploiement Continu) | Le code est automatiquement deploye en production apres les checks | Chaque merge sur `main` = mise en production |

> **Dans notre projet**, on fait uniquement de la **CI** (pas de CD). On n'a pas de serveur de production a deployer — c'est un outil CLI.

### 1.3 Le cycle complet

```
Code → Push → CI (verifications auto) → PR Review → Merge → [CD (deploiement)]
                                                                    ^
                                                        Pas dans notre projet
```

### 1.4 Pipeline, Jobs et Steps — Le vocabulaire

Un **pipeline** CI est compose de :

| Terme | Definition | Analogie |
|-------|-----------|----------|
| **Pipeline** | L'ensemble du processus automatise | La chaine de montage |
| **Job** | Un groupe de taches qui tourne sur une machine | Un poste de travail |
| **Step** | Une action individuelle dans un job | Une operation |
| **Runner** | La machine (VM) qui execute les jobs | L'ouvrier |
| **Trigger** | L'evenement qui declenche le pipeline | Le signal de depart |
| **Artifact** | Un fichier produit par le pipeline (rapport, build...) | Le produit fini |

Les jobs peuvent tourner **en parallele** (en meme temps) ou **en sequence** (l'un apres l'autre).

---

## 2. Ce qui est en place dans notre projet

### 2.1 La plateforme : GitHub Actions

On utilise **GitHub Actions**, le systeme CI integre a GitHub. Il lit un fichier YAML dans le repo (`.github/workflows/ci.yml`) et execute les instructions automatiquement.

**Alternatives possibles** (pour comparaison) :

| Plateforme | Avantage principal | Inconvenient |
|------------|-------------------|-------------|
| **GitHub Actions** (notre choix) | Integre a GitHub, zero config serveur | Limite a 2000 min/mois (gratuit) |
| GitLab CI | Similaire, integre a GitLab | Necessite migration du repo |
| Jenkins | Tres flexible | Serveur a installer et maintenir |

### 2.2 Quand le pipeline se declenche

Le fichier de config (`ci.yml`) definit deux declencheurs :

| Evenement | Branches concernees | Pourquoi |
|-----------|-------------------|----------|
| `git push` | `main`, `master`, `feature/*` | Feedback immediat pour le dev |
| Ouverture d'une PR | vers `main` ou `master` | Validation avant merge |

**Exemples concrets :**
```
Tu push sur feature/diagnostic  →  CI tourne      ✅
Tu push sur docs/readme         →  CI ne tourne PAS  (pas dans les branches ciblees)
Tu ouvres une PR vers main      →  CI tourne      ✅
```

### 2.3 Les 2 jobs de notre pipeline

Le pipeline lance **2 jobs en parallele** :

```
Push / PR sur GitHub
       |
       ├──► Job 1 "Lint & Type Check"   →  ruff + mypy       →  ✅ ou ❌
       |        (1 instance, Python 3.10)
       |
       └──► Job 2 "Tests"               →  pytest + coverage  →  ✅ ou ❌
                (3 instances en parallele : Python 3.10 / 3.11 / 3.12)
                        |
                        └──► Upload rapport de couverture (artifact)
```

#### Job 1 — Lint & Type Check

Verifie la **qualite du code** sans l'executer (analyse statique).

| Step | Commande | Ce que ca fait |
|------|----------|---------------|
| 1. Checkout | `actions/checkout@v4` | Clone le repo sur la VM |
| 2. Setup Python | `actions/setup-python@v5` | Installe Python 3.10 + cache pip |
| 3. Install deps | `pip install -r requirements-dev.txt` | Installe les outils de dev |
| 4. Ruff (lint) | `ruff check src/ tests/` | Verifie le style : imports tries, variables inutilisees, syntaxe |
| 5. Mypy (types) | `mypy src/ --ignore-missing-imports` | Verifie les types : tu passes un `str` la ou il faut un `int` ? |

> **Si un step echoue, le job s'arrete immediatement** et affiche ❌ sur GitHub.

#### Job 2 — Tests

Lance les tests unitaires et mesure la couverture.

| Step | Commande | Ce que ca fait |
|------|----------|---------------|
| 1. Checkout | `actions/checkout@v4` | Clone le repo |
| 2. Setup Python | `actions/setup-python@v5` | Installe Python (3.10 OU 3.11 OU 3.12 selon la matrice) |
| 3. Install deps | `pip install -r requirements-dev.txt` | Installe les deps |
| 4. Pytest | `pytest tests/ -v --cov=src --cov-report=xml` | Execute les tests + mesure la couverture |
| 5. Upload | `actions/upload-artifact@v4` | Sauvegarde le rapport XML (uniquement sur Python 3.10) |

**La matrice** : ce job tourne **3 fois en parallele**, une fois par version de Python. Ca garantit que le code fonctionne partout.

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
```

### 2.4 Resultat visible sur GitHub

Quand le pipeline tourne, les resultats apparaissent sur la PR et dans l'onglet Actions :

```
✅ Lint & Type Check        — passed
✅ Tests (Python 3.10)      — passed
✅ Tests (Python 3.11)      — passed
✅ Tests (Python 3.12)      — passed
```

Si un check est ❌, on clique dessus pour voir les logs et comprendre l'erreur.

### 2.5 Schema recapitulatif complet

```
Developer                     GitHub                         VM Runner (Ubuntu)
   |                            |                                  |
   |-- git push feature/xx ---->|                                  |
   |                            |-- Detecte le push                |
   |                            |-- Lit .github/workflows/ci.yml   |
   |                            |-- Lance 2 jobs en parallele ---->|
   |                            |                                  |
   |                            |              Job 1: Lint         |
   |                            |              1. Clone le repo    |
   |                            |              2. Install Python   |
   |                            |              3. Install deps     |
   |                            |              4. ruff check       |
   |                            |              5. mypy check       |
   |                            |              → Resultat ✅/❌    |
   |                            |                                  |
   |                            |              Job 2: Tests (x3)   |
   |                            |              1. Clone le repo    |
   |                            |              2. Install Python   |
   |                            |              3. Install deps     |
   |                            |              4. pytest + cov     |
   |                            |              5. Upload artifact  |
   |                            |              → Resultat ✅/❌    |
   |                            |                                  |
   |<-- Notification resultat --|<---------------------------------|
   |                            |                                  |
```

---

## 3. Guide pratique

### 3.1 Lancer les verifications en local

Avant de push, lance les memes commandes que la CI sur ta machine :

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

### 3.2 Ou voir les resultats

1. Aller sur la page du repo GitHub
2. Onglet **Actions** → voir les runs
3. Ou directement sur ta **PR** → les checks apparaissent en bas

Pour le rapport de couverture : Actions → cliquer sur le run → section Artifacts → telecharger `coverage-report`.

### 3.3 Ecrire un test pour ton module

Chaque dev doit ecrire les tests de son module :

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

## 4. Erreurs courantes et solutions

### Ruff : import non utilise (F401)

```
F401 `os` imported but unused
```

**Solution :** Supprimer l'import inutile, ou ajouter `# noqa: F401` si c'est voulu.

### Ruff : imports mal tries (I001)

```
I001 Import block is un-sorted or un-formatted
```

**Solution :** Lancer `ruff check --fix src/ tests/` pour corriger automatiquement.

### Mypy : module introuvable

```
Cannot find implementation or library stub for module named "xxx"
```

**Solution :** Normal pour les libs externes. On a `ignore_missing_imports = true` dans `pyproject.toml`.

### Pytest : test qui echoue

```
FAILED tests/test_diagnostic.py::test_check_dns - AssertionError
```

**Solution :** Lire le message d'erreur, corriger le code ou le test, re-push.

### La CI echoue mais mon code marche en local

**Solution :** Verifier que tous les fichiers sont bien push. La CI clone le repo depuis zero — elle n'a pas acces a tes fichiers locaux non-commites.

---

## 5. Structure des fichiers CI

```
.github/workflows/ci.yml   ← Definition du pipeline (YAML)
pyproject.toml              ← Config ruff + mypy + pytest
requirements.txt            ← Deps runtime
requirements-dev.txt        ← Deps dev (inclut requirements.txt + outils CI)
tests/                      ← Dossier des tests
  __init__.py
  test_interfaces.py        ← Tests du contrat commun
  test_diagnostic.py        ← Tests du module diagnostic
  test_backup.py            ← Tests du module backup
  test_audit.py             ← Tests du module audit
```

---

## 6. Resume — Ce qu'il faut retenir

| Question | Reponse |
|----------|---------|
| **CI/CD c'est quoi ?** | Verification automatique du code a chaque push (CI) + deploiement auto (CD) |
| **On fait du CI ou du CD ?** | Uniquement de la CI (pas de deploiement, c'est un outil CLI) |
| **Quelle plateforme ?** | GitHub Actions (integre a GitHub, gratuit) |
| **Quand ca tourne ?** | A chaque push sur `main`/`master`/`feature/*` et a chaque PR |
| **Ca verifie quoi ?** | Style du code (ruff), types (mypy), tests (pytest) sur 3 versions Python |
| **Combien de temps ?** | ~1-2 minutes par run |
| **Ou voir les resultats ?** | Onglet Actions sur GitHub, ou directement sur la PR |
| **Comment eviter les echecs ?** | `make lint && make test` avant de push |
