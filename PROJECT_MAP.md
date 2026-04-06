# PROJECT MAP — NTL-SysToolbox

> Comprendre le projet en 5 minutes.

## C'est quoi ?

CLI Python pour l'administration systeme de **NordTransit Logistics** (PME logistique, Lille).
3 modules : Diagnostic, Backup, Audit. 4 developpeurs. 19h de projet (MSPR EPSI).

---

## Navigation rapide

| Je veux...                          | Aller a                                      |
|-------------------------------------|----------------------------------------------|
| Installer et configurer mon env     | [docs/01-getting-started.md](docs/01-getting-started.md) |
| Commencer a coder mon module        | [docs/02-team-guide.md](docs/02-team-guide.md)           |
| Comprendre la logique des fonctions | [docs/03-module-logic.md](docs/03-module-logic.md)       |
| Voir le contrat JSON (interfaces)   | [docs/04-interfaces.md](docs/04-interfaces.md)           |
| Aide-memoire rapide pendant le dev  | [docs/cheatsheet.md](docs/cheatsheet.md)                 |
| Comprendre la CI/CD                 | [docs/08-ci-guide.md](docs/08-ci-guide.md)               |
| Monter le lab Proxmox               | [docs/10-lab-infra.md](docs/10-lab-infra.md)             |
| Préparer la soutenance              | [docs/guide-oral-soutenance.md](docs/guide-oral-soutenance.md) |
| Voir le plan de soutenance          | [docs/soutenance-plan.md](docs/soutenance-plan.md)       |
| Lire le plan complet du projet      | [_specs/PLAN_COMPLET.md](_specs/PLAN_COMPLET.md)         |
| Voir les décisions de l'équipe      | [_specs/DECISIONS_PRISES.md](_specs/DECISIONS_PRISES.md) |

---

## Structure du repo

```
NTL-SysToolbox/
│
├── src/                         # Code Python principal
│   ├── main.py                  # Menu CLI interactif (point d'entree)
│   ├── config_loader.py         # Chargement YAML + variables d'env
│   ├── interfaces.py            # Contrat commun (exit codes, build_result)
│   ├── modules/                 # Les 3 modules metier
│   │   ├── _template.py         # Template a copier pour un nouveau module
│   │   ├── diagnostic/          # Module 1 : sante des serveurs
│   │   │   ├── __init__.py      # Point d'entree (run dispatcher)
│   │   │   ├── checks.py        # Fonctions de verification
│   │   │   └── constant.py      # Ports, services, constantes
│   │   ├── backup.py            # Module 2 : sauvegarde BDD
│   │   └── audit/               # Module 3 : obsolescence reseau
│   │       ├── __init__.py      # Point d'entree (run dispatcher)
│   │       └── scanner.py       # Fonctions de scan et audit
│   └── utils/                   # Utilitaires partages
│       ├── output.py            # Logging, JSON, affichage rich
│       ├── network.py           # Ping, DNS, check port, HTTP, MySQL
│       └── validation.py        # Validation chemins, plages reseau, sanitisation
│
├── tests/                       # Tests unitaires (pytest)
├── config/                      # Fichiers de configuration
│   └── config.example.yaml      # Template (copier vers config.yaml)
├── data/                        # Donnees de reference
│   ├── eol_database.json        # Dates fin de vie des OS
│   └── sample_inventory.csv     # Inventaire reseau exemple
├── output/                      # Artefacts generes (gitignore)
│
├── docs/                        # Documentation (numerotee, lire dans l'ordre)
├── _specs/                      # Planification projet (archives)
├── infra/                       # Infrastructure lab
│   ├── proxmox/                 # Scripts de deploiement Proxmox (18 VMs)
│   ├── post-install/            # Configuration des services (AD, MySQL, etc.)
│   └── templates/               # Templates cloud-init & autounattend
├── school/                      # Documents scolaires (sujet, grille)
│
├── .github/workflows/ci.yml     # Pipeline CI (ruff + mypy + pytest)
├── Makefile                     # Commandes dev (setup, test, lint, run)
├── requirements.txt             # Dependances production
└── requirements-dev.txt         # Dependances dev (ruff, mypy, pytest-cov)
```

---

## Equipe & modules

| Developpeur | Role | Module | Fichier | Branche |
|-------------|------|--------|---------|---------|
| **Ianis** (Lead) | CLI, config, utils, integration | Core | `src/main.py` | `feature/cli-menu` |
| **Blaise** | Verification sante serveurs | Diagnostic | `src/modules/diagnostic/` | `feature/module-diagnostic` |
| **Ojvind** | Sauvegarde BDD | Backup | `src/modules/backup.py` | `feature/module-backup` |
| **Zaid** | Audit obsolescence | Audit | `src/modules/audit/` | `feature/module-audit` |

---

## Architecture

```
┌──────────────┐
│  Utilisateur │
│  (terminal)  │
└──────┬───────┘
       │ choisit module + action
       ▼
┌──────────────┐     ┌─────────────────────┐
│   main.py    │────▶│  module.run(config,  │
│   (menu)     │     │    target, action)   │
└──────────────┘     └──────────┬──────────┘
                                │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │ diagnostic  │    │   backup    │    │    audit    │
   │ check_ad_dns│    │ backup_db   │    │ scan_network│
   │ check_mysql │    │ export_csv  │    │ list_os_eol │
   │ check_linux │    └──────┬──────┘    │ audit_csv   │
   │ check_http  │           │           │ gen_report  │
   └──────┬──────┘           │           └──────┬──────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
                    ┌─────────────────┐
                    │  build_result() │
                    │  (JSON standard)│
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
             ┌────────────┐   ┌────────────┐
             │ Terminal    │   │ output/    │
             │ (rich)     │   │ logs/*.json│
             └────────────┘   └────────────┘
```

---

## Conventions cles

| Regle | Detail |
|-------|--------|
| **Exit codes** | `0`=OK, `1`=WARNING, `2`=CRITICAL, `3`=UNKNOWN |
| **Seuils** | CPU/RAM/Disk > 80% = WARNING |
| **Timeout** | 10 secondes par defaut |
| **Commits** | `feat:` / `fix:` / `docs:` / `test:` / `chore:` |
| **Merge** | Squash, review par le Lead |
| **Secrets** | `.env` + `python-dotenv`, JAMAIS dans le code |
| **Retour** | Toujours `build_result()`, jamais un dict manuel |
| **Crash** | Interdit — `try/except` obligatoire dans chaque fonction |

---

## Commandes rapides

```bash
make setup          # Creer venv + installer deps (Windows)
make setup-linux    # Idem pour Linux
make setup-dev      # Installer outils dev (ruff, mypy, pytest-cov)
make run            # Lancer le CLI
make test           # Lancer les tests avec couverture
make lint           # Verifier le code (ruff)
make typecheck      # Verifier les types (mypy)
make clean          # Nettoyer les fichiers generes
```

---

## Lab d'infrastructure

5 VMs essentielles sur Proxmox VE (reseau `192.168.10.0/24`) :

| VM | OS | IP | Role |
|----|----|----|------|
| DC01 | Windows Server 2022 | .10 | Active Directory / DNS |
| WMS-DB | Ubuntu 20.04 | .21 | MySQL (base `wms`) |
| SRV-OLD | Windows Server 2012 R2 | .12 | Legacy (tests EOL) |
| SRV-LEGACY | Ubuntu 18.04 | .18 | Legacy (tests EOL) |
| CLIENT-01 | Windows 10 | .50 | Poste d'execution |

Scripts de deploiement : `infra/proxmox/`
