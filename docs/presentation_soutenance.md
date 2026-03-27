# NTL-SysToolbox — Présentation Soutenance

## MSPR TPRE511 — Bloc E6.1 « Concevoir et tester des solutions applicatives »

**Équipe :** Ianis PUICHAUD (Lead) · Blaise WANDA NKONG · Ojvind LANTSIGBLE · Zaid ABOUYAALA
**Date :** Avril 2026 | **Durée :** 20 min + 30 min Q&A

---

> Ce document sert de script et de base pour les slides de la soutenance.
> Chaque section `##` correspond à un slide. Le temps indicatif est entre parenthèses.

---

## Slide 1 — Page de titre (30s)

# NTL-SysToolbox

**Outil CLI d'administration système pour NordTransit Logistics**

MSPR TPRE511 — Bloc E6.1

| Rôle | Membre |
|------|--------|
| Lead / Architecte | Ianis PUICHAUD |
| Dev Diagnostic | Blaise WANDA NKONG |
| Dev Backup | Ojvind LANTSIGBLE |
| Dev Audit + Docs | Zaid ABOUYAALA |

---

## Slide 2 — Contexte et problématique (1min30)

### Le client : NordTransit Logistics

- **PME logistique** — Hauts-de-France (siège Lille, entrepôts Lens, Valenciennes, Arras)
- **Parc informatique** : 19 machines (serveurs Windows/Linux, postes de travail)
- **Application métier** : WMS (Warehouse Management System) sur MySQL

### Problématiques identifiées

1. **Pas de vérification systématique** de l'état des services critiques (AD, DNS, MySQL)
2. **Sauvegardes manuelles** de la base WMS — risque de perte de données
3. **Aucune visibilité** sur l'obsolescence du parc (OS en fin de vie)

### Notre mission

> Développer un outil CLI qui industrialise ces 3 opérations avec des sorties exploitables en supervision.

---

## Slide 3 — Solution proposée (1min)

### NTL-SysToolbox — 3 modules

| Module | Fonction | Valeur métier |
|--------|----------|---------------|
| **Diagnostic** | Vérifie AD/DNS, MySQL, santé serveurs | Détection proactive des pannes |
| **Backup** | Dump SQL + export CSV + SHA256 | Sauvegardes traçables et vérifiables |
| **Audit** | Scan réseau + analyse EOL | Plan de migration priorisé |

### Caractéristiques clés

- **Cross-platform** : Windows + Linux
- **Sorties JSON** horodatées (ISO 8601 UTC)
- **Codes retour standardisés** : 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN
- **Menu interactif** avec affichage Rich

---

## Slide 4 — Architecture technique (2min)

### Stack technologique

- **Langage** : Python 3.10+
- **Librairies** : rich, paramiko, dnspython, python-nmap, mysql-connector, ldap3, psutil
- **CI/CD** : GitHub Actions (lint, types, tests sur 3 versions Python)
- **Infra** : Proxmox VE, Ansible, cloud-init

### Structure du projet

```
src/
├── main.py              # Menu CLI interactif
├── config_loader.py     # YAML + .env
├── interfaces.py        # Contrat commun
├── modules/
│   ├── diagnostic/      # 4 checks (AD/DNS, MySQL, Linux, HTTP)
│   ├── backup.py        # Dump SQL + CSV
│   └── audit/           # Scan nmap + EOL + rapports
└── utils/               # output, network, validation
```

### Contrat d'interface unique

Chaque fonction retourne un JSON standardisé via `build_result()` — même format pour les 3 modules.

---

## Slide 5 — Module Diagnostic (2min) — Blaise

### Objectif
Confirmer la disponibilité des services critiques de NTL.

### 4 vérifications

| Fonction | Cible | Vérifications |
|----------|-------|---------------|
| `check_ad_dns` | DC01 | DNS résolution, port LDAP 389, services Windows |
| `check_mysql` | WMS-DB | Port 3306, version, connexion |
| `check_linux` | Serveurs Linux | Scan multi-ports (SSH, HTTP, MySQL, etc.) |
| `check_http` | Services web | Réponse HTTP/HTTPS, code retour |

### Seuils

- CPU/RAM/Disque > 80% → WARNING
- Service down → CRITICAL
- Timeout → UNKNOWN

### Démo
> Lancer un diagnostic sur DC01 et WMS-DB depuis le menu interactif.

---

## Slide 6 — Module Backup (2min) — Ojvind

### Objectif
Garantir l'intégrité et la traçabilité des exports de la base WMS.

### 2 fonctions

| Fonction | Description | Sortie |
|----------|-------------|--------|
| `backup_database()` | mysqldump de la base WMS | `wms_YYYYMMDD_HHMMSS.sql` + hash SHA256 |
| `export_table_csv()` | SELECT * → CSV par table | `shipments.csv`, `inventory.csv` |

### Sécurité

- Mot de passe MySQL via variable d'environnement (jamais en clair)
- Prévention injection SQL sur les noms de tables
- Validation des chemins de sortie (anti path traversal)

### Démo
> Lancer un backup complet et montrer le fichier .sql + vérification SHA256.

---

## Slide 7 — Module Audit (2min) — Zaid

### Objectif
Fournir un inventaire réseau qualifié et un rapport d'obsolescence.

### 4 fonctions

| Fonction | Description |
|----------|-------------|
| `scan_network()` | Scan nmap avec détection OS |
| `list_os_eol()` | Lecture base EOL (20 OS référencés) |
| `audit_from_csv()` | Croisement inventaire CSV + dates EOL |
| `generate_report()` | Rapport complet trié par criticité |

### Résultats clés du parc NTL (19 machines)

| Criticité | Nombre | Exemples |
|-----------|--------|----------|
| **CRITICAL** | 6 | SRV-PRINT (Win 2008 R2), PC-QUAI (Win 7), IPBX (CentOS 7) |
| **WARNING** | 7 | PC-SIEGE (Win 10), WMS-DB (Ubuntu 20.04) |
| **OK** | 6 | DC01 (Win Server 2022), DC02 (Win Server 2019) |

### Démo
> Lancer un audit depuis le CSV et montrer le rapport coloré.

---

## Slide 8 — Infrastructure de test (1min30)

### Lab Proxmox

```
Réseau lab : 192.168.10.0/24

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    DC01       │  │   WMS-DB     │  │  SRV-OLD     │
│ Win Srv 2022  │  │ Ubuntu 20.04 │  │ Win 2012 R2  │
│ .10.10        │  │ .10.21       │  │ .10.12       │
│ AD/DNS        │  │ MySQL        │  │ Legacy       │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Automatisation

- **7 playbooks Ansible** pour le provisionnement complet
- **Cloud-init** (Linux) + **autounattend.xml** (Windows)
- **Scripts Proxmox** : setup, orchestration, vérification, teardown

---

## Slide 9 — CI/CD et qualité (1min30)

### Pipeline GitHub Actions

```
Push/PR → [Lint (ruff)] → [Type check (mypy)] → [Tests (pytest × 3 versions)]
```

### Métriques

| Indicateur | Valeur |
|------------|--------|
| Test cases | 52+ |
| Fichiers de test | 8 |
| Versions Python testées | 3.10, 3.11, 3.12 |
| Couverture minimum | 50% |
| Linter | Ruff (règles E, F, W, I) |
| Type checker | Mypy (check_untyped_defs) |

### Workflow Git

- Branches `feature/*` par développeur
- PR avec CI obligatoire avant merge
- Review par le Lead

---

## Slide 10 — Organisation d'équipe (1min)

### Répartition

| Phase | Durée | Activité |
|-------|-------|----------|
| Setup | 3h | Lab Proxmox + squelette Python |
| Dev parallèle | 10h | Chacun sur son module en branche |
| Intégration | 3h | Merge, tests E2E, corrections |
| Docs + soutenance | 3h | Documentation, slides, répétition |

### Outils de collaboration

- **GitHub** : code, issues, PRs, CI
- **Discord** : communication temps réel
- **Conventions** : commits conventionnels (`feat:`, `fix:`, `docs:`)

---

## Slide 11 — Démo live (3min)

> Script de démo à suivre dans l'ordre :

1. **Lancer l'outil** : `make run`
2. **Diagnostic** → AD/DNS sur DC01 → montrer le JSON
3. **Diagnostic** → MySQL sur WMS-DB → montrer le JSON
4. **Backup** → Dump SQL → montrer le fichier + SHA256
5. **Backup** → Export CSV → montrer les fichiers
6. **Audit** → Audit depuis CSV → montrer le rapport coloré
7. **Montrer les logs** dans `output/logs/`

### Plan B (si lab down)
> Avoir des screenshots prêts de chaque étape de la démo.

---

## Slide 12 — Bilan et perspectives (1min30)

### Ce qui a été réalisé

- 3 modules fonctionnels avec interface standardisée
- Pipeline CI/CD automatisée avec 52+ tests
- Infrastructure as Code (Ansible + Proxmox)
- Documentation complète (technique, utilisation, audit)

### Difficultés rencontrées

- Hétérogénéité Windows/Linux (WinRM vs SSH)
- Gestion des timeouts réseau en environnement instable
- Coordination à 4 sur un planning serré (19h)

### Améliorations possibles

- Mode CLI non-interactif (arguments en ligne de commande) pour l'automatisation
- Banner grabbing automatique dans le scanner
- Intégration avec un outil de supervision (Zabbix, Grafana)
- Interface web pour les rapports d'audit
- Notifications (email, Slack) sur résultats critiques

---

## Slide 13 — Questions (30min)

### Questions anticipées et réponses

**Q : Pourquoi `mysqldump` plutôt que la réplication MySQL ?**
> mysqldump est adapté au contexte PME de NTL : simple, portable, et produit un fichier vérifiable. La réplication serait pertinente pour un plan de haute disponibilité, mais hors périmètre MSPR.

**Q : Comment gérez-vous le cross-platform ?**
> Python est nativement cross-platform. Les différences sont gérées dans les utilitaires réseau (ping -c/-n, chemins). La CI teste sur Ubuntu avec 3 versions Python.

**Q : Sécurité des credentials ?**
> Les secrets (mots de passe MySQL, SSH) sont dans `.env` (jamais commité). Le `config.yaml` utilise des placeholders `${VAR}` résolus au runtime. Pas de secret en dur dans le code.

**Q : Que feriez-vous avec plus de temps ?**
> Mode non-interactif pour le scheduling (cron), interface web pour les rapports, alerting automatique, et extension à d'autres services (DHCP, Exchange).

**Q : Pourquoi Python plutôt que Bash/PowerShell ?**
> Cross-platform, écosystème riche (nmap, paramiko, mysql-connector), maintenabilité et testabilité (pytest). Un script Bash ne serait pas portable sur Windows.

**Q : Comment garantissez-vous la qualité du code ?**
> Triple vérification automatique en CI : linter (Ruff), type checker (Mypy), tests unitaires (Pytest). Plus de 52 tests, couverture > 50%.

---

*Fin de la présentation — Merci pour votre attention*
