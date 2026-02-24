# NTL-SysToolbox

![CI](https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox/actions/workflows/ci.yml/badge.svg)

Boite a outils d'administration systeme pour le parc informatique NovaTech Logistics.

## Modules

| Module | Description |
|--------|-------------|
| **Diagnostic** | Verification AD/DNS, MySQL, sante serveurs |
| **Backup** | Dump MySQL, export CSV, verification SHA256 |
| **Audit** | Scan reseau nmap, detection OS EOL, rapports |

## Quick Start

```bash
# Setup (Windows Git Bash)
make setup

# Setup (Linux)
make setup-linux

# Installer les outils de dev (lint, tests)
make setup-dev

# Lancer les tests
make test

# Lancer le linter
make lint

# Lancer le type checker
make typecheck
```

## Stack

- Python 3.10+
- pytest / ruff / mypy
- GitHub Actions (CI)
