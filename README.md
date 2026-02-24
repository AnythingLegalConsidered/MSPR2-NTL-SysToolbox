# NTL-SysToolbox

![CI](https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox/actions/workflows/ci.yml/badge.svg)

Outil CLI d'administration système développé pour **NordTransit Logistics (NTL)**, une PME de logistique implantée dans les Hauts-de-France (siège à Lille, entrepôts à Lens, Valenciennes et Arras).

NTL-SysToolbox industrialise les vérifications d'exploitation, sécurise la gestion des sauvegardes de la base métier (WMS) et produit un audit d'obsolescence du parc informatique.

> **MSPR TPRE511** — Bloc E6.1 « Concevoir et tester des solutions applicatives »

## Modules

| Module | Objectif | Fonctions |
|--------|----------|-----------|
| **Diagnostic** | Confirmer la disponibilité des briques critiques du siège | Vérification AD/DNS, test MySQL, état serveur Windows/Ubuntu (OS, uptime, CPU, RAM, disques) |
| **Backup** | Garantir l'intégrité et la traçabilité des exports WMS | Sauvegarde BDD au format SQL, export table au format CSV, vérification SHA256 |
| **Audit** | Fournir un inventaire réseau et qualifier le statut EOL | Scan réseau nmap, détection OS, dates de fin de vie, rapport d'obsolescence |

## Architecture (cible)

```
src/
├── main.py              # Menu CLI interactif
├── config_loader.py     # Chargement YAML + surcharge .env
├── interfaces.py        # Contrat commun (exit codes, build_result)  ✔
├── modules/
│   ├── diagnostic.py    # Checks AD/DNS, MySQL, santé serveurs
│   ├── backup.py        # Dump MySQL, export CSV
│   └── audit.py         # Scan nmap, EOL, rapports
└── utils/
    ├── output.py        # Logging, JSON, affichage rich  ✔
    └── network.py       # Helpers réseau (ping, port check)
```

> Les fichiers marqués ✔ sont implémentés. Les autres seront créés au fur et à mesure du développement (voir les [issues GitHub](https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox/issues)).

Les sorties sont horodatées en JSON avec des codes de retour exploitables en supervision :

| Code | Statut | Signification |
|------|--------|---------------|
| `0` | OK | Tout fonctionne |
| `1` | WARNING | Dégradation (CPU/disque/RAM > 80%) |
| `2` | CRITICAL | Service down, backup échoué |
| `3` | UNKNOWN | Cible injoignable, timeout |

## Quick Start

```bash
# Cloner le repo
git clone https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox.git
cd MSPR2-NTL-SysToolbox

# Setup (Windows Git Bash)
make setup

# Setup (Linux)
make setup-linux

# Configurer
cp config/config.example.yaml config/config.yaml
cp .env.example .env
# Éditer .env avec vos identifiants MySQL / SSH

# Lancer l'outil
make run
```

## Développement

```bash
# Installer les outils de dev (ruff, mypy, pytest-cov)
make setup-dev

# Lancer les tests avec couverture
make test

# Lancer le linter
make lint

# Lancer le type checker
make typecheck
```

## Intégration continue

La pipeline GitHub Actions s'exécute automatiquement sur les branches `main`, `master` et `feature/*` :

- **Lint** — Ruff (style et erreurs statiques)
- **Type check** — Mypy (cohérence des types)
- **Tests** — Pytest sur Python 3.10, 3.11, 3.12 avec rapport de couverture

Voir [docs/GUIDE_CI.md](docs/GUIDE_CI.md) pour le guide d'utilisation et [docs/RAPPORT_CI.md](docs/RAPPORT_CI.md) pour le rapport technique.

## Infrastructure de lab

Le lab de développement est déployé sur Proxmox avec les VMs suivantes :

| VM | OS | Rôle | IP |
|----|----|------|----|
| DC01 | Windows Server 2022 | Contrôleur de domaine AD/DNS | 192.168.10.10 |
| WMS-DB | Ubuntu 20.04 | Base MySQL du WMS | 192.168.10.21 |
| SRV-OLD | Windows Server 2012 R2 | Serveur legacy (tests EOL) | 192.168.10.12 |
| SRV-LEGACY | Ubuntu 18.04 | Serveur legacy (tests EOL) | 192.168.10.18 |
| CLIENT-01 | Windows 10 | Poste d'exécution de l'outil | 192.168.10.50 |

Scripts de déploiement dans [`scripts/proxmox/`](scripts/proxmox/).

## Stack technique

- **Langage** — Python 3.10+
- **Librairies** — rich, paramiko, dnspython, python-nmap, mysql-connector, ldap3, psutil
- **Tests** — pytest, pytest-cov, ruff, mypy
- **CI/CD** — GitHub Actions
- **Lab** — Proxmox VE, cloud-init

## Équipe

| Rôle | Membre |
|------|--------|
| Lead / Intégrateur | Ianis PUICHAUD |
| Dev Diagnostic | Blaise WANDA NKONG |
| Dev Backup | Ojvind LANTSIGBLE |
| Dev Audit | Zaid ABOUYAALA |

## Documentation

| Document | Emplacement |
|----------|-------------|
| Guide CI pour l'équipe | [docs/GUIDE_CI.md](docs/GUIDE_CI.md) |
| Rapport technique CI | [docs/RAPPORT_CI.md](docs/RAPPORT_CI.md) |
| Dossier technique et fonctionnel | `docs/document_technique.md` (à venir) |
| Manuel d'installation | `docs/manuel_utilisation.md` (à venir) |
| Rapport d'exécution audit | `docs/rapport_audit.md` (à venir) |
