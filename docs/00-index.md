# Documentation — Index

> Table des matieres de toute la documentation du projet.
> Choisis un parcours selon ton besoin.

---

## Parcours de lecture

### Nouveau dans l'equipe

1. [01-getting-started.md](01-getting-started.md) — Installer les outils, cloner, configurer
2. [02-team-guide.md](02-team-guide.md) — Comprendre ton role, le pattern de code, le workflow Git
3. [cheatsheet.md](cheatsheet.md) — Garder ouvert pendant le dev

### Comprendre l'architecture

1. [PROJECT_MAP.md](../PROJECT_MAP.md) — Vue d'ensemble en 5 minutes
2. [04-interfaces.md](04-interfaces.md) — Le contrat JSON (exit codes, build_result)
3. [07-cli.md](07-cli.md) — Comment main.py fonctionne
4. [03-module-logic.md](03-module-logic.md) — Logique detaillee de chaque fonction

### Developper un module

1. [03-module-logic.md](03-module-logic.md) — Implementation pas-a-pas + logique par fonction
2. [06-utils.md](06-utils.md) — Fonctions utilitaires reutilisables
3. [05-config.md](05-config.md) — Comment lire la configuration

### Deployer le lab

1. [10-lab-infra.md](10-lab-infra.md) — Vue d'ensemble de l'infra Proxmox
2. [infra/proxmox/README.md](../infra/proxmox/README.md) — Guide de deploiement detaille

### CI/CD

1. [08-ci-guide.md](08-ci-guide.md) — Guide pratique du pipeline
2. [09-ci-report.md](09-ci-report.md) — Rapport technique CI (livrable scolaire)

---

## Tous les fichiers

| # | Fichier | Contenu |
|---|---------|---------|
| 01 | [getting-started.md](01-getting-started.md) | Installation, clone, venv, config, premiere branche |
| 02 | [team-guide.md](02-team-guide.md) | Roles, pattern de code, sections par module, Git, checklist |
| 03 | [module-logic.md](03-module-logic.md) | Comment implementer + logique detaillee par fonction |
| 04 | [interfaces.md](04-interfaces.md) | Contrat JSON : exit codes, build_result(), exceptions |
| 05 | [config.md](05-config.md) | Chargement config YAML + variables d'environnement |
| 06 | [utils.md](06-utils.md) | Fonctions utilitaires : network.py, output.py |
| 07 | [cli.md](07-cli.md) | Structure du menu main.py |
| 08 | [ci-guide.md](08-ci-guide.md) | Guide pratique CI/CD (GitHub Actions) |
| 09 | [ci-report.md](09-ci-report.md) | Rapport technique CI (livrable) |
| 10 | [lab-infra.md](10-lab-infra.md) | Infrastructure lab Proxmox |
| -- | [cheatsheet.md](cheatsheet.md) | Aide-memoire 1 page (format retour, Git, commandes) |

## Archives projet

| Fichier | Contenu |
|---------|---------|
| [PLAN_COMPLET.md](../_specs/PLAN_COMPLET.md) | Reference master du projet (lab, roles, stack, planning) |
| [DECISIONS_PRISES.md](../_specs/DECISIONS_PRISES.md) | Archive des decisions d'equipe |
| [ETAPES.md](../_specs/ETAPES.md) | Timeline du projet (9 phases) |
