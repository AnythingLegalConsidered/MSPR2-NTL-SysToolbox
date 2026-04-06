# Documentation — Index

> Table des matières de toute la documentation du projet.
> Choisis un parcours selon ton besoin.

---

## Parcours de lecture

### Nouveau dans l'équipe

1. [01-getting-started.md](01-getting-started.md) — Installer les outils, cloner, configurer
2. [02-team-guide.md](02-team-guide.md) — Comprendre ton rôle, le pattern de code, le workflow Git
3. [cheatsheet.md](cheatsheet.md) — Garder ouvert pendant le dev

### Comprendre l'architecture

1. [PROJECT_MAP.md](../PROJECT_MAP.md) — Vue d'ensemble en 5 minutes
2. [04-interfaces.md](04-interfaces.md) — Le contrat JSON (exit codes, build_result)
3. [07-cli.md](07-cli.md) — Comment main.py fonctionne
4. [03-module-logic.md](03-module-logic.md) — Logique détaillée de chaque fonction

### Développer un module

1. [03-module-logic.md](03-module-logic.md) — Implémentation pas-à-pas + logique par fonction
2. [06-utils.md](06-utils.md) — Fonctions utilitaires réutilisables
3. [05-config.md](05-config.md) — Comment lire la configuration

### Déployer le lab

1. [10-lab-infra.md](10-lab-infra.md) — Vue d'ensemble de l'infra Proxmox
2. [infra/proxmox/README.md](../infra/proxmox/README.md) — Guide de déploiement détaillé

### Préparer la soutenance

1. [soutenance-plan.md](soutenance-plan.md) — Plan de soutenance (répartition, timing, notes speaker)
2. [guide-oral-soutenance.md](guide-oral-soutenance.md) — Guide oral : quoi dire diapo par diapo + questions jury
3. [slides-corrections-v5.md](slides-corrections-v5.md) — Corrections à appliquer aux slides (v4 → v5)
4. [demo-homelab.md](demo-homelab.md) — Scénario de démo sur le homelab

### CI/CD

1. [08-ci-guide.md](08-ci-guide.md) — Guide pratique du pipeline
2. [09-ci-report.md](09-ci-report.md) — Rapport technique CI (livrable scolaire)

---

## Tous les fichiers

| # | Fichier | Contenu |
|---|---------|---------|
| 01 | [getting-started.md](01-getting-started.md) | Installation, clone, venv, config, première branche |
| 02 | [team-guide.md](02-team-guide.md) | Rôles, pattern de code, sections par module, Git, checklist |
| 03 | [module-logic.md](03-module-logic.md) | Comment implémenter + logique détaillée par fonction |
| 04 | [interfaces.md](04-interfaces.md) | Contrat JSON : exit codes, build_result(), exceptions |
| 05 | [config.md](05-config.md) | Chargement config YAML + variables d'environnement |
| 06 | [utils.md](06-utils.md) | Fonctions utilitaires : network.py, output.py |
| 07 | [cli.md](07-cli.md) | Structure du menu main.py |
| 08 | [ci-guide.md](08-ci-guide.md) | Guide pratique CI/CD (GitHub Actions) |
| 09 | [ci-report.md](09-ci-report.md) | Rapport technique CI (livrable) |
| 10 | [lab-infra.md](10-lab-infra.md) | Infrastructure lab Proxmox |
| -- | [cheatsheet.md](cheatsheet.md) | Aide-mémoire 1 page (format retour, Git, commandes) |

## Livrables soutenance

| Fichier | Contenu |
|---------|---------|
| [document_technique.md](document_technique.md) | Document technique et fonctionnel complet |
| [manuel_utilisation.md](manuel_utilisation.md) | Manuel d'utilisation pas à pas |
| [rapport_audit.md](rapport_audit.md) | Rapport d'audit d'obsolescence du parc NTL |
| [rapport_soutenance.md](rapport_soutenance.md) | Rapport écrit de soutenance |
| [presentation_soutenance.md](presentation_soutenance.md) | Script et slides de la présentation orale |

## Préparation soutenance

| Fichier | Contenu |
|---------|---------|
| [soutenance-plan.md](soutenance-plan.md) | Plan de soutenance : répartition, timing, notes speaker |
| [guide-oral-soutenance.md](guide-oral-soutenance.md) | Guide oral : quoi dire diapo par diapo + questions jury |
| [slides-corrections-v5.md](slides-corrections-v5.md) | Corrections à appliquer aux slides (v4 → v5) |
| [demo-homelab.md](demo-homelab.md) | Scénario de démo sur le homelab |

## Archives projet

| Fichier | Contenu |
|---------|---------|
| [PLAN_COMPLET.md](../_specs/PLAN_COMPLET.md) | Référence master du projet (lab, rôles, stack, planning) |
| [DECISIONS_PRISES.md](../_specs/DECISIONS_PRISES.md) | Archive des décisions d'équipe |
| [ETAPES.md](../_specs/ETAPES.md) | Timeline du projet (9 phases) |
