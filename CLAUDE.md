# NTL-SysToolbox

CLI Python admin sys pour NordTransit Logistics (PME logistique).
3 modules : Diagnostic, Backup, Audit. Projet EPSI, 4 devs (Ianis lead).

## Commandes (Makefile)

```bash
make test           # pytest avec coverage
make lint           # ruff check src/ tests/
make typecheck      # mypy src/
make run            # python src/main.py
make setup          # venv + deps (Windows)
make setup-linux    # venv + deps (Linux)
make setup-dev      # ruff + mypy + pytest-cov
```

Prefixer avec `rtk` en session Claude Code.

## Stack

- **Python** 3.10+ (CI: 3.10, 3.11, 3.12)
- **Lint** : ruff
- **Types** : mypy
- **Tests** : pytest + pytest-cov
- **Libs** : paramiko, dnspython, python-nmap, mysql-connector, ldap3, psutil, rich
- **Config** : YAML + `.env` (python-dotenv)

## Architecture

```
src/
  main.py           # CLI menu (Rich)
  config_loader.py  # YAML + .env loader
  interfaces.py     # Contrat commun build_result()
  modules/          # diagnostic.py, backup.py, audit.py
  utils/            # Helpers partages
```

**Contrat JSON** : toutes les fonctions retournent `build_result(status, code, data)`
- Exit codes : 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN
- Seuils : CPU/RAM/Disk > 80% = WARNING

## Lab Proxmox (environnement de test)

| VM | OS | Role | IP |
|----|------|------|-----|
| DC01 | Windows Server 2022 | AD/DNS | 192.168.10.10 |
| WMS-DB | Ubuntu 20.04 | MySQL | .21 |
| SRV-OLD | Windows Server 2012 R2 | EOL test | .12 |
| SRV-LEGACY | Ubuntu 18.04 | EOL test | .18 |
| CLIENT-01 | Windows 10 | Poste exec | .50 |

## Conventions

- Commits : `feat|fix|docs|test|chore: msg` (atomiques)
- Merge : squash, review par Lead (Ianis)
- **NO CRASH** : try/except obligatoire dans chaque fonction
- **Return** : toujours `build_result()`, jamais de dict manuel
- Branches : `feature/module-{diagnostic|backup|audit}`, `feature/cli-menu`
- CI : GitHub Actions (ruff + mypy + pytest sur 3.10/3.11/3.12)
