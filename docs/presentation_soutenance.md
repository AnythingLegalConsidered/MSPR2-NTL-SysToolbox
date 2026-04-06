# NTL-SysToolbox — Présentation Soutenance

## MSPR TPRE511 — Bloc E6.1 « Concevoir et tester des solutions applicatives »

**Équipe :** Ianis PUICHAUD (Lead) · Blaise WANDA NKONG · Ojvind LANTSIGBLE · Zaid ABOUYAALA
**Date :** Avril 2026 | **Durée :** 20 min + 30 min Q&A

---

> Ce document sert de script et de base pour les slides de la soutenance.
> Chaque section `##` correspond à un slide (v6 — 16 slides). Le temps indicatif est entre parenthèses.

---

## Slide 1 — Page de titre (30s)

# NTL-SysToolbox

**CLI administration système pour NordTransit Logistics**

MSPR TPRE511 — Bloc E6.1

| Rôle | Membre |
|------|--------|
| Lead / Architecte | Ianis PUICHAUD |
| Dev Diagnostic | Blaise WANDA NKONG |
| Dev Backup | Ojvind LANTSIGBLE |
| Dev Audit + Docs | Zaid ABOUYAALA |

---

## Slide 2 — Contexte NTL (1min)

### Le client : NordTransit Logistics

- **PME logistique** — Hauts-de-France (siège Lille, entrepôts Lens, Valenciennes, Arras)
- **~240 employés**, équipe IT de 4 personnes
- **Application métier** : WMS (Warehouse Management System) — cœur de métier, plage critique 5h30-18h30
- **Maintenance** effectuée en créneau nocturne

---

## Slide 3 — Problématique (1min)

### 3 axes identifiés

| Problème actuel | Module réponse |
|-----------------|----------------|
| **Supervision** — Pas de vérification systématique des services critiques (AD, DNS, MySQL) | → **Diagnostic** |
| **Sauvegardes** — Exports manuels de la base WMS, risque de perte de données | → **Backup** |
| **Obsolescence** — Aucune visibilité sur les OS en fin de vie dans le parc | → **Audit** |

> Mission : développer un outil CLI qui industrialise ces 3 opérations avec des sorties exploitables en supervision.

---

## Slide 4 — Notre solution (1min)

### NTL-SysToolbox

- **CLI Python interactif** avec menu Rich
- **3 modules** : Diagnostic, Backup, Audit
- **Sorties JSON horodatées** (ISO 8601 UTC)
- **Codes retour standardisés** : 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN — compatibles Nagios/Zabbix
- **Configuration** : YAML + `.env` (secrets séparés)
- **Cross-platform** : Windows + Linux

---

## Slide 5 — Organisation équipe (1min30)

### Répartition des rôles

| Membre | Rôle | Périmètre |
|--------|------|-----------|
| Ianis PUICHAUD | Lead / Architecte | CLI, interfaces, config, CI, intégration |
| Blaise WANDA NKONG | Dev Diagnostic | 4 checks (AD/DNS, MySQL, Linux, HTTP) |
| Ojvind LANTSIGBLE | Dev Backup | Dump SQL, export CSV, sécurité |
| Zaid ABOUYAALA | Dev Audit + Docs | Scan réseau, EOL, rapports, documentation |

### Méthode de travail

- **Contrat JSON** commun (`build_result()`) défini en amont
- **Branches** `feature/*` par développeur
- **Pull Requests** avec CI obligatoire avant merge
- **Review** par le Lead, merge squash

### Workflow Git (4 étapes)

1. Créer branche `feature/module-xxx`
2. Développer + commiter (commits conventionnels)
3. Ouvrir PR → CI automatique (lint + types + tests)
4. Review Lead → merge squash dans `master`

---

## Slide 6 — Architecture (2min)

### Structure du projet

```
src/
├── main.py              # Menu CLI interactif
├── config_loader.py     # YAML + .env
├── interfaces.py        # Contrat commun build_result()
├── modules/
│   ├── diagnostic/      # 4 checks
│   ├── backup.py        # Dump SQL + CSV
│   └── audit/           # Scan nmap + EOL + rapports
└── utils/               # output, network, validation
```

### Contrat JSON — `build_result()` (8 champs)

Chaque fonction retourne un JSON standardisé :
`module`, `function`, `timestamp`, `status`, `exit_code`, `target`, `details`, `message`

### Règles

- **Seuils** : CPU/RAM/Disque > 80% → WARNING
- **Timeout** : 10s par défaut sur chaque opération réseau

---

## Slide 7 — Module Diagnostic (2min) — Blaise

### Question clé
> « Les services critiques du siège sont-ils opérationnels ? »

### 4 fonctions

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

---

## Slide 8 — Module Backup (2min) — Ojvind

### Question clé
> « Sauvegarder la base WMS de manière fiable et traçable »

### 2 fonctions

| Fonction | Description | Sortie |
|----------|-------------|--------|
| `backup_database()` | mysqldump de la base WMS | `wms_YYYYMMDD_HHMMSS.sql` + hash SHA256 |
| `export_table_csv()` | SELECT * → CSV par table | `shipments.csv`, `inventory.csv` |

### 4 mesures de sécurité

1. Mot de passe MySQL via variable d'environnement (jamais en clair)
2. Prévention injection SQL sur les noms de tables
3. Validation des chemins de sortie (anti path traversal)
4. Hash SHA256 pour vérification d'intégrité

---

## Slide 9 — Module Audit (2min) — Zaid

### Question clé
> « Quels équipements du parc sont obsolètes ? »

### Pipeline en 4 étapes

| Étape | Fonction | Description |
|-------|----------|-------------|
| 1. Scan | `scan_network()` | Scan nmap avec détection OS |
| 2. EOL | `list_os_eol()` | Lecture base EOL locale |
| 3. Croisement | `audit_from_csv()` | Croisement inventaire CSV + dates EOL |
| 4. Rapport | `generate_report()` | Rapport complet trié par criticité |

### Résultats clés du parc NTL (19 machines)

| Criticité | Nombre | Exemples |
|-----------|--------|----------|
| **CRITICAL** | 6 | SRV-PRINT (Win 2008 R2), PC-QUAI (Win 7), IPBX (CentOS 7) |
| **WARNING** | 7 | PC-SIEGE (Win 10), WMS-DB (Ubuntu 20.04) |
| **OK** | 6 | DC01 (Win Server 2022), DC02 (Win Server 2019) |

---

## Slide 10 — Environnement de test (1min)

### Lab Proxmox — 5 VMs

| VM | OS | Rôle | IP |
|----|----|------|----|
| DC01 | Windows Server 2022 | AD/DNS | 192.168.10.10 |
| WMS-DB | Ubuntu 20.04 | MySQL | 192.168.10.21 |
| WMS-APP | — | Application WMS | 192.168.10.x |
| SRV-OLD | Windows Server 2012 R2 | EOL test | 192.168.10.12 |
| SRV-LEGACY | Ubuntu 18.04 | EOL test | 192.168.10.18 |

**Réseau** : 192.168.10.0/24

---

## Slide 11 — Intégration continue (1min)

### Pipeline GitHub Actions

- **2 jobs parallèles** : qualité (lint + types) et tests (pytest)
- **3 versions Python** testées : 3.10, 3.11, 3.12
- **Durée** : < 2 minutes

### Outils de qualité

| Outil | Rôle |
|-------|------|
| **Ruff** | Linter (règles E, F, W, I) |
| **Mypy** | Type checker (`check_untyped_defs`) |
| **Pytest** | Tests unitaires + couverture |

---

## Slide 12 — Démo live (3min)

### 5 étapes

| Étape | Qui | Action |
|-------|-----|--------|
| 1 | Ianis | Menu principal — `make run` |
| 2 | Blaise | Module Diagnostic — AD/DNS + MySQL |
| 3 | Ojvind | Module Backup — Dump SQL + CSV |
| 4 | Zaid | Module Audit — Scan + rapport |
| 5 | Ianis | Montrer les sorties JSON horodatées |

### Plan B (si lab down)
> Screenshots prêts de chaque étape de la démo.

---

## Slide 13 — Documentation (1min)

### 6 livrables ✓

- Documentation technique complète
- Guide d'utilisation
- Documentation des interfaces (contrat JSON)
- Guide de configuration
- Rapport CI
- Documentation infrastructure lab

### Arborescence `docs/`

```
docs/
├── 00-index.md
├── 01-getting-started.md
├── 02-team-guide.md
├── 03-module-logic.md
├── 04-interfaces.md
├── 05-config.md
├── 06-utils.md
├── 07-cli.md
├── 08-ci-guide.md
├── 09-ci-report.md
├── 10-lab-infra.md
└── cheatsheet.md
```

---

## Slide 14 — Difficultés et compromis (1min)

| Difficulté | Compromis adopté |
|------------|------------------|
| **Portabilité** Windows/Linux | Abstraction dans les utilitaires réseau (ping -c/-n, chemins) |
| **WinRM** complexe à configurer | Rendu optionnel, fallback sur vérifications réseau |
| **Base EOL** — pas d'API temps réel | Base locale JSON (20 OS référencés), maintenue manuellement |
| **Coordination** à 4 sur 19h | Contrat JSON défini en amont, branches isolées, CI automatique |
| **Sécurité** des credentials | `.env` séparé (jamais commité), placeholders `${VAR}` dans YAML |

---

## Slide 15 — Bilan et perspectives (1min30)

### 7 objectifs atteints ✓

1. CLI interactif fonctionnel
2. 3 modules avec interface standardisée
3. Sorties JSON exploitables en supervision
4. Pipeline CI/CD automatisée
5. Infrastructure de test reproductible
6. Documentation complète
7. Cross-platform Windows/Linux

### Perspectives

- Mode CLI non-interactif (arguments en ligne de commande) pour cron/scheduling
- Banner grabbing automatique dans le scanner
- Intégration supervision (Zabbix, Grafana)
- Interface web pour les rapports d'audit
- Notifications (email, Slack) sur résultats critiques

### Métriques projet

| Indicateur | Valeur |
|------------|--------|
| Commits | 62 |
| Tests unitaires | 110 |
| Lignes de code | ~2 500 |
| Documents techniques | 10 |
| VMs de test | 5 |

---

## Slide 16 — Questions (30min)

**Merci pour votre attention — Prêts pour vos questions !**

---

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
> Triple vérification automatique en CI : linter (Ruff), type checker (Mypy), tests unitaires (Pytest). 110 tests, couverture > 50%.

**Q : Pourquoi une base EOL locale plutôt qu'une API ?**
> Fiabilité : pas de dépendance réseau externe lors de l'audit. La base JSON couvre les 20 OS du parc NTL. En perspective, on pourrait ajouter un mécanisme de mise à jour automatique.

**Q : Comment avez-vous géré la coordination à 4 ?**
> Contrat JSON défini dès le départ comme interface commune. Chacun développe sur sa branche feature/*, la CI valide automatiquement, et le Lead review avant merge squash. Discord pour la communication temps réel.

**Q : Pourquoi des codes retour compatibles Nagios/Zabbix ?**
> Pour que les sorties soient directement exploitables par un outil de supervision existant, sans adaptation. C'est un standard de fait dans le monitoring système.

---

*Fin de la présentation — 16 slides, v6*
