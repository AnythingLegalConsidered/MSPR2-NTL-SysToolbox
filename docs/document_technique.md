# Document Technique et Fonctionnel

## NTL-SysToolbox

**Outil CLI de diagnostic, sauvegarde et audit pour NordTransit Logistics**

---

| | |
|---|---|
| **Projet** | MSPR TPRE511 -- Bloc E6.1 "Concevoir et tester des solutions applicatives" |
| **Client** | NordTransit Logistics (NTL) |
| **Version** | 1.0 |
| **Date** | 27 mars 2026 |

### Equipe de developpement

| Membre | Role | Responsabilite |
|---|---|---|
| Ianis PUICHAUD | Lead / Architecte | CLI, configuration, utilitaires |
| Blaise WANDA NKONG | Developpeur | Module Diagnostic |
| Ojvind LANTSIGBLE | Developpeur | Module Backup |
| Zaid ABOUYAALA | Developpeur | Module Audit + Documentation |

---

## Sommaire

1. [Introduction et contexte](#1-introduction-et-contexte)
2. [Architecture technique](#2-architecture-technique)
3. [Description fonctionnelle des modules](#3-description-fonctionnelle-des-modules)
   - 3.1 [Module Diagnostic](#31-module-diagnostic)
   - 3.2 [Module Backup](#32-module-backup)
   - 3.3 [Module Audit](#33-module-audit)
4. [Contrat d'interface JSON](#4-contrat-dinterface-json)
5. [Configuration et securite](#5-configuration-et-securite)
6. [Infrastructure de test](#6-infrastructure-de-test)
7. [Integration continue (CI/CD)](#7-integration-continue-cicd)
8. [Bilan et perspectives](#8-bilan-et-perspectives)

---

## 1. Introduction et contexte

### 1.1 Presentation du client

NordTransit Logistics (NTL) est une PME specialisee dans la logistique, implantee dans les Hauts-de-France. L'entreprise dispose d'un siege social a Lille et de trois entrepots situes a Lens, Valenciennes et Arras. Son systeme d'information repose sur une infrastructure heterogene comprenant des serveurs Windows et Linux, une base de donnees MySQL pour son WMS (Warehouse Management System), ainsi qu'un domaine Active Directory pour la gestion centralisee des identites.

### 1.2 Problematique

L'equipe IT de NTL est confrontee a plusieurs defis operationnels :

- **Diagnostic manuel** : la verification de l'etat des services (AD/DNS, MySQL, services Linux, HTTP) est effectuee manuellement, ce qui est chronophage et source d'erreurs.
- **Sauvegardes non standardisees** : les procedures de backup de la base WMS ne sont pas automatisees ni tracees de maniere fiable.
- **Obsolescence non suivie** : l'inventaire des systemes d'exploitation et le suivi des dates de fin de vie (EOL) ne sont pas formalises, exposant l'infrastructure a des risques de securite.

### 1.3 Solution proposee

NTL-SysToolbox est un outil CLI (Command Line Interface) interactif developpe en Python 3.10+, concu pour repondre a ces trois problematiques via trois modules complementaires :

| Module | Fonction |
|---|---|
| **Diagnostic** | Verification automatisee de l'etat des services reseau et applicatifs |
| **Backup** | Sauvegarde de la base MySQL (dump SQL) et export de tables en CSV |
| **Audit** | Scan reseau, detection des systemes en fin de vie, rapport de conformite |

L'outil est concu pour etre **cross-platform** (Windows et Linux), produit des **sorties JSON horodatees** pour la tracabilite, et utilise des **codes retour standardises** compatibles avec les systemes de supervision.

---

## 2. Architecture technique

### 2.1 Stack technologique

| Composant | Technologie | Version |
|---|---|---|
| Langage | Python | 3.10+ |
| Interface CLI | Rich (tables, JSON colore) | >= 13.0 |
| Base de donnees | MySQL Connector Python | >= 8.0 |
| SSH | Paramiko | >= 3.0 |
| DNS | dnspython | >= 2.4 |
| LDAP | ldap3 | >= 2.9 |
| Scan reseau | python-nmap | >= 0.7 |
| Configuration | PyYAML + python-dotenv | >= 6.0 / >= 1.0 |
| Monitoring systeme | psutil | >= 5.9 |
| Tests | pytest + pytest-cov | >= 7.0 |
| Linting | ruff | >= 0.4 |
| Typage statique | mypy | >= 1.10 |

### 2.2 Structure du projet

```
NTL-SysToolbox/
├── src/
│   ├── main.py                  # Point d'entree CLI interactif
│   ├── config_loader.py         # Chargement YAML + resolution ${VAR}
│   ├── interfaces.py            # Contrat commun (build_result, exit codes)
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── _template.py         # Template de module (reference)
│   │   ├── diagnostic/
│   │   │   ├── __init__.py      # Dispatcher des actions diagnostic
│   │   │   ├── checks.py        # Implementation des verifications
│   │   │   └── constant.py      # Ports, services, constantes reseau
│   │   ├── backup.py            # Dump SQL + export CSV
│   │   └── audit/
│   │       ├── __init__.py      # Dispatcher des actions audit
│   │       └── scanner.py       # Scan nmap, EOL, inventaire CSV
│   └── utils/
│       ├── output.py            # Logging JSON, formatage Rich
│       ├── network.py           # Helpers reseau (ping, port, HTTP, DNS)
│       └── validation.py        # Validation chemins, sanitisation
├── config/
│   └── config.example.yaml      # Template de configuration
├── data/
│   ├── eol_database.json        # Base de donnees EOL (20 OS)
│   └── sample_inventory.csv     # Inventaire d'exemple (19 machines)
├── tests/                       # 8 fichiers de tests, 52+ cas
├── infra/
│   ├── ansible/                 # Playbooks de deploiement (7 playbooks)
│   └── proxmox/                 # Scripts de provisioning du lab
├── requirements.txt             # Dependances runtime
├── requirements-dev.txt         # Dependances developpement
└── pyproject.toml               # Configuration ruff, mypy, pytest
```

### 2.3 Diagramme d'architecture logicielle

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                              │
│                   (Menu CLI interactif)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Menu     │  │ Menu     │  │ Menu     │                  │
│  │Diagnostic│  │ Backup   │  │ Audit    │                  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
└───────┼──────────────┼─────────────┼────────────────────────┘
        │              │             │
        ▼              ▼             ▼
┌──────────────┐ ┌───────────┐ ┌───────────────┐
│  diagnostic/ │ │ backup.py │ │    audit/      │
│  __init__.py │ │           │ │  __init__.py   │
│  checks.py   │ │           │ │  scanner.py    │
│  constant.py │ │           │ │                │
└──────┬───────┘ └─────┬─────┘ └──────┬────────┘
       │               │              │
       └───────────┐   │   ┌──────────┘
                   ▼   ▼   ▼
          ┌──────────────────────┐
          │     interfaces.py    │
          │  build_result()      │
          │  EXIT_OK/WARNING/    │
          │  CRITICAL/UNKNOWN    │
          └──────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌─────────────┐ ┌──────────┐ ┌────────────┐
│  output.py  │ │network.py│ │validation.py│
│ (logging,   │ │(port,    │ │(chemins,   │
│  JSON, Rich)│ │ DNS, HTTP)│ │ reseau)    │
└─────────────┘ └──────────┘ └────────────┘
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
      config/    config/     .env
    config.yaml  (YAML)   (secrets)
```

### 2.4 Flux d'execution

```
Utilisateur
    │
    ▼
main.py ──► load_config(config.yaml)
    │             │
    │             ├── Lecture .env (python-dotenv)
    │             ├── Parse YAML (pyyaml / safe_load)
    │             └── Resolution ${VAR} ──► os.environ
    │
    ▼
Menu principal (Rich Table)
    │
    ├── [1] Diagnostic ──► diagnostic.run(config, target, action=...)
    │                            │
    │                            ├── check_ad_dns  → DNS + Ports + LDAP + WinRM
    │                            ├── check_mysql   → Port TCP + Version MySQL
    │                            ├── check_linux   → Scan multi-ports
    │                            └── check_http    → GET HTTP/HTTPS
    │
    ├── [2] Backup ──► backup.run(config, target, action=...)
    │                       │
    │                       ├── backup_database → mysqldump → .sql
    │                       └── export_table_csv → SELECT * → .csv
    │
    └── [3] Audit ──► audit.run(config, target, action=...)
                          │
                          ├── scan_network    → nmap -sV
                          ├── list_os_eol     → eol_database.json
                          ├── audit_from_csv  → inventaire CSV + EOL
                          └── generate_report → rapport JSON complet
    │
    ▼
build_result() ──► Resultat JSON standardise
    │
    ├── print_result()     → Affichage console (Rich)
    └── save_result_json() → Fichier output/logs/<timestamp>_<module>_<fn>.json
```

---

## 3. Description fonctionnelle des modules

### 3.1 Module Diagnostic

**Responsable** : Blaise WANDA NKONG

**Objectif** : Verifier automatiquement l'etat de sante des services reseau et applicatifs de l'infrastructure NTL.

#### 3.1.1 check_ad_dns -- Verification Active Directory / DNS

**Entrees** :
- `config` : configuration complete (section `targets.dc01`, `winrm`)
- `target` : adresse IP du controleur de domaine (defaut : `192.168.10.10`)

**Algorithme** :
1. **Resolution DNS** : tente une resolution A via dnspython (si serveur DNS specifie) ou via `socket.gethostbyname()` en fallback.
2. **Verification des ports** : teste la connectivite TCP sur les ports critiques (53/DNS, 88/Kerberos, 389/LDAP) et importants (445/SMB, 3268/LDAP-GC).
3. **Test LDAP** : etablit une connexion LDAP anonyme via `ldap3` avec auto-bind pour valider le service d'annuaire.
4. **Verification des services Windows** (optionnel) : si les credentials WinRM sont configures, interroge les services NTDS, DNS et Netlogon via PowerShell distant.
5. **Calcul du statut global** : agrege les resultats individuels -- `CRITICAL` si au moins un check critique echoue, `WARNING` si seul WinRM est indisponible, `OK` sinon.

**Sorties** : resultat standardise avec details par sous-check (dns, ports, ldap, services).

#### 3.1.2 check_mysql -- Verification MySQL

**Entrees** :
- `config` : configuration complete (section `mysql.port`)
- `target` : adresse IP du serveur MySQL

**Algorithme** :
1. Tente une connexion TCP sur le port MySQL (defaut : 3306).
2. Si le port est ouvert, lit le paquet de greeting MySQL pour extraire la version du serveur (protocole MySQL : 3 octets longueur + 1 octet sequence + 1 octet protocole + chaine version terminee par null).
3. En cas d'echec de lecture de version, tente un `grab_banner` generique.

**Sorties** : resultat avec `reachable`, `port`, `version`, `banner`.

#### 3.1.3 check_linux -- Scan de services Linux

**Entrees** :
- `config` : configuration complete (section `discovery.ports`, `discovery.timeout`)
- `target` : adresse IP du serveur Linux

**Algorithme** :
1. Recupere la liste des ports a scanner depuis la configuration (defaut : 22, 80, 443, 3306, 5432, 8006, 8080).
2. Pour chaque port, effectue une tentative de connexion TCP avec timeout configurable.
3. Categorise les ports ouverts par nom de service (SSH, HTTP, MySQL, etc.) via la table `SERVICE_NAMES`.
4. Statut `OK` si au moins un service est detecte, `CRITICAL` sinon.

**Sorties** : resultat avec `open_ports` (liste detaillee) et `categories` (services identifies).

#### 3.1.4 check_http -- Verification HTTP/HTTPS

**Entrees** :
- `config` : configuration complete
- `target` : adresse IP eventuellement suivie du port (`IP:port`, defaut port 80)

**Algorithme** :
1. Parse la cible pour extraire le port (separation sur le dernier `:`).
2. Determine automatiquement le schema (`https` pour les ports 443, 8443, 4443, 9443 ; `http` sinon).
3. Effectue une requete HTTP GET via `urllib.request` avec User-Agent `NTL-SysToolbox/1.0`.
4. Mesure le temps de reponse en millisecondes (`time.monotonic()`).
5. Limite la lecture du body a 1 Mo pour eviter les debordements memoire.
6. La verification SSL est desactivee par defaut (contexte lab).

**Sorties** : resultat avec `status_code`, `server`, `content_length`, `response_time_ms`.

---

### 3.2 Module Backup

**Responsable** : Ojvind LANTSIGBLE

**Objectif** : Automatiser la sauvegarde de la base MySQL du WMS et l'export de tables en CSV avec tracabilite complete.

#### 3.2.1 backup_database -- Dump SQL

**Entrees** :
- `config` : configuration complete (sections `mysql`, `general`)
- `target` : nom de la base de donnees (defaut : `wms`)

**Algorithme** :
1. **Validation** : verifie la presence de la section `mysql` dans la configuration. Valide le chemin de sortie via `validate_path_within()` contre le repertoire courant.
2. **Construction de la commande** : genere la commande `mysqldump` avec les options `--single-transaction` (coherence transactionnelle) et `--routines` (inclusion des procedures stockees).
3. **Securite du mot de passe** : le mot de passe MySQL est passe via la variable d'environnement `MYSQL_PWD` (et non en argument CLI, qui serait visible dans `ps aux`).
4. **Execution** : lance `mysqldump` via `subprocess.run()` avec `capture_output=True` et timeout configurable.
5. **Ecriture** : sauvegarde le dump dans `output/backups/<database>_<YYYYMMDD_HHMMSS>.sql`.
6. **Gestion d'erreurs** : traitement specifique pour acces refuse, timeout, absence de `mysqldump`.

**Sorties** : resultat avec `dump_path`, `size_bytes`, `database`.

**Fichier genere** : `output/backups/wms_20260327_143022.sql` (exemple)

#### 3.2.2 export_table_csv -- Export CSV

**Entrees** :
- `config` : configuration complete (sections `mysql`, `general`)
- `target` : nom de la table a exporter (ex : `shipments`, `inventory`)

**Algorithme** :
1. **Validation du nom de table** : verifie via regex `^[a-zA-Z_]\w{0,63}$` que le nom ne contient que des caracteres surs (prevention d'injection SQL).
2. **Connexion MySQL** : etablit une connexion via `mysql.connector` avec timeout configurable.
3. **Requete** : execute `SELECT * FROM \`<table>\`` avec le nom de table encadre par des backticks. Une assertion de securite re-valide le nom avant execution.
4. **Ecriture CSV** : genere le fichier avec entetes (noms de colonnes) via le module `csv` standard.
5. **Gestion d'erreurs** : classification fine des erreurs (acces refuse, table inexistante, serveur injoignable).

**Sorties** : resultat avec `csv_path`, `table`, `database`, `row_count`, `columns`.

**Fichier genere** : `output/exports/shipments_20260327_143022.csv` (exemple)

---

### 3.3 Module Audit

**Responsable** : Zaid ABOUYAALA

**Objectif** : Scanner le reseau, detecter les systemes en fin de vie et generer un rapport de conformite.

#### 3.3.1 scan_network -- Scan reseau

**Entrees** :
- `config` : configuration complete (sections `discovery`, `general`, `audit`)
- `target` : plage reseau en notation CIDR (defaut depuis config : `172.16.135.0/24`)

**Algorithme** :
1. **Validation de la plage** : verifie le format via `ipaddress.ip_network()` pour prevenir les injections nmap.
2. **Validation des ports** : filtre la liste des ports configures pour ne garder que les entiers dans [1, 65535].
3. **Scan nmap** : execute un scan `nmap -T4 --host-timeout <timeout>s` sur les ports specifies via `python-nmap`.
4. **Categorisation** : pour chaque host actif, classe les ports ouverts par categorie de service.

**Sorties** : resultat avec `range`, `hosts_up`, `hosts` (liste detaillee par IP avec ports ouverts et categories).

#### 3.3.2 list_os_eol -- Base de donnees EOL

**Entrees** :
- `config` : configuration complete (section `audit.eol_database`)

**Algorithme** :
1. Charge le fichier `eol_database.json` contenant 20 systemes d'exploitation.
2. Pour chaque entree, compare la date EOL avec la date courante (UTC).
3. Classe chaque OS comme `is_eol: true` ou `is_eol: false`.
4. Statut `WARNING` si au moins un OS est en fin de vie, `OK` sinon.

**Donnees** : la base EOL couvre les OS suivants :

| Categorie | Systemes |
|---|---|
| Windows Server | 2022, 2019, 2016, 2012 R2, 2012, 2008 R2 |
| Windows Desktop | 11, 10, 8.1, 7 |
| Ubuntu | 24.04, 22.04, 20.04, 18.04, 16.04 |
| Debian | 12, 11, 10 |
| CentOS | 7 |
| Red Hat (RHEL) | 9 |

**Sorties** : resultat avec `total`, `eol_count`, `supported_count`, `entries`.

#### 3.3.3 audit_from_csv -- Audit depuis inventaire

**Entrees** :
- `config` : configuration complete
- `target` : chemin vers le fichier CSV d'inventaire (defaut : `./data/sample_inventory.csv`)

**Algorithme** :
1. **Validation du chemin** : verifie que le fichier CSV est situe dans un repertoire autorise (`./data/` ou `./output/`) via `validate_path_within()`.
2. **Lecture CSV** : parse le fichier avec `csv.DictReader` (colonnes attendues : `hostname`, `os_name`, `os_version`, `role`, optionnel : `ip`).
3. **Resolution DNS** : si la colonne `ip` est absente, tente de resoudre le hostname via DNS.
4. **Croisement EOL** : pour chaque machine, compare l'OS (concatenation `os_name os_version`) avec la base EOL.
5. **Test de connectivite** : pour chaque machine disposant d'une IP, teste la joignabilite via les ports 22 (SSH) puis 80 (HTTP) en fallback.
6. **Agregation** : compte les machines joignables, injoignables et en fin de vie.

**Sorties** : resultat avec `total_hosts`, `reachable`, `unreachable`, `eol_hosts`, `hosts` (detail par machine).

#### 3.3.4 generate_report -- Rapport complet

**Entrees** :
- `config` : configuration complete

**Algorithme** :
1. Execute sequentiellement les trois fonctions d'audit : `scan_network`, `list_os_eol`, `audit_from_csv`.
2. Agrege les resultats dans un rapport JSON avec resume (`hosts_discovered`, `inventory_total`, `inventory_reachable`, `eol_systems`).
3. Sauvegarde le rapport dans `output/reports/audit_report_<YYYYMMDD_HHMMSS>.json`.
4. Signale les erreurs partielles via le drapeau `has_errors`.

**Sorties** : resultat avec `report_path`, `has_errors`, sous-resultats `scan`, `inventory`, `eol`.

**Fichier genere** : `output/reports/audit_report_20260327_143022.json` (exemple)

---

## 4. Contrat d'interface JSON

### 4.1 Format standardise

Tous les modules retournent un dictionnaire construit via la fonction `build_result()` definie dans `src/interfaces.py`. Ce contrat garantit l'uniformite des sorties pour le traitement automatise et la supervision.

```json
{
  "module": "diagnostic|backup|audit",
  "function": "nom_de_la_fonction",
  "timestamp": "2026-03-27T14:30:22.123456+00:00",
  "status": "OK|WARNING|CRITICAL|UNKNOWN",
  "exit_code": 0,
  "target": "192.168.10.10",
  "details": { },
  "message": "Description lisible du resultat"
}
```

### 4.2 Codes retour

Les codes retour sont inspires du standard Nagios/Monitoring Plugins, assurant la compatibilite avec les systemes de supervision courants :

| Code | Constante | Status | Signification |
|------|-----------|--------|---------------|
| `0` | `EXIT_OK` | `OK` | Service fonctionnel, operation reussie |
| `1` | `EXIT_WARNING` | `WARNING` | Degradation (couverture partielle, seuil depasse) |
| `2` | `EXIT_CRITICAL` | `CRITICAL` | Service indisponible, operation echouee |
| `3` | `EXIT_UNKNOWN` | `UNKNOWN` | Cible injoignable, timeout, erreur interne |

### 4.3 Validation

La fonction `build_result()` effectue une validation stricte :
- Le `status` doit appartenir a l'ensemble `{"OK", "WARNING", "CRITICAL", "UNKNOWN"}`.
- L'`exit_code` doit appartenir a l'ensemble `{0, 1, 2, 3}`.
- Une `ValueError` est levee en cas de valeur invalide, empechant la generation de resultats malformes.

### 4.4 Exceptions personnalisees

| Exception | Usage |
|---|---|
| `ModuleConfigError` | Configuration manquante ou invalide (section YAML absente, variable non definie) |
| `ModuleExecutionError` | Erreur lors de l'execution d'une fonction de module |

### 4.5 Exemples de sorties

**Diagnostic -- check_mysql (succes)** :
```json
{
  "module": "diagnostic",
  "function": "check_mysql",
  "timestamp": "2026-03-27T14:30:22.123456+00:00",
  "status": "OK",
  "exit_code": 0,
  "target": "192.168.10.21",
  "details": {
    "reachable": true,
    "port": 3306,
    "version": "8.0.36",
    "banner": null
  },
  "message": "MySQL accessible sur 192.168.10.21:3306 (version 8.0.36)"
}
```

**Backup -- backup_database (succes)** :
```json
{
  "module": "backup",
  "function": "backup_database",
  "timestamp": "2026-03-27T14:35:00.456789+00:00",
  "status": "OK",
  "exit_code": 0,
  "target": "wms",
  "details": {
    "dump_path": "output/backups/wms_20260327_143500.sql",
    "size_bytes": 245760,
    "database": "wms"
  },
  "message": "Backup wms sauvegarde: output/backups/wms_20260327_143500.sql (245760 octets)"
}
```

**Audit -- scan_network (succes)** :
```json
{
  "module": "audit",
  "function": "scan_network",
  "timestamp": "2026-03-27T14:40:10.789012+00:00",
  "status": "OK",
  "exit_code": 0,
  "target": "192.168.10.0/24",
  "details": {
    "range": "192.168.10.0/24",
    "hosts_up": 5,
    "hosts": [
      {
        "ip": "192.168.10.10",
        "hostname": "DC01",
        "open_ports": [
          {"port": 53, "state": "open", "service": "domain"},
          {"port": 88, "state": "open", "service": "kerberos-sec"},
          {"port": 389, "state": "open", "service": "ldap"}
        ],
        "categories": ["DNS", "Kerberos", "LDAP"]
      }
    ]
  },
  "message": "Scan termine: 5 host(s) trouves sur 192.168.10.0/24"
}
```

### 4.6 Persistance des resultats

Chaque resultat est automatiquement sauvegarde dans un fichier JSON horodate :

- **Emplacement** : `output/logs/<YYYYMMDD_HHMMSS>_<module>_<function>.json`
- **Encodage** : UTF-8, indentation 2 espaces
- **Nommage** : les composants module et function sont assainis via `sanitize_filename_part()` (caracteres alphanumeriques, underscores et tirets uniquement, tronques a 50 caracteres).

---

## 5. Configuration et securite

### 5.1 Fichier de configuration YAML

La configuration de l'application est chargee depuis `config/config.yaml` (non commite dans le depot). Un template est fourni dans `config/config.example.yaml`.

**Sections du fichier** :

| Section | Description | Cles principales |
|---|---|---|
| `general` | Parametres globaux | `log_level`, `output_dir`, `timeout` |
| `targets` | Cibles a surveiller | `dc01.host`, `wms_db.host`, `type`, `description` |
| `mysql` | Connexion MySQL | `host`, `port`, `user`, `password`, `database` |
| `ssh` | Connexion SSH | `host`, `port`, `user`, `password`, `key_file` |
| `discovery` | Auto-decouverte reseau | `network_range`, `timeout`, `ports` |
| `winrm` | Connexion WinRM (Windows) | `user`, `password` |
| `audit` | Parametres audit | `network_range`, `eol_database`, `inventory_csv` |

### 5.2 Resolution des variables d'environnement

Le systeme de configuration supporte la substitution de variables d'environnement via la syntaxe `${VAR_NAME}` :

```yaml
mysql:
  user: "${NTL_MYSQL_USER}"
  password: "${NTL_MYSQL_PASSWORD}"
```

**Mecanisme de resolution** :
1. Le fichier `.env` a la racine du projet est charge via `python-dotenv`.
2. La fonction `_resolve_env_vars()` parcourt recursivement l'arborescence YAML (dicts, listes, chaines).
3. Chaque placeholder `${VAR}` est remplace par la valeur de `os.environ.get(VAR)`.
4. Si une variable n'est pas definie, un warning est emis dans les logs et le placeholder est conserve tel quel.
5. En mode `strict=True`, une `ModuleConfigError` est levee si des variables restent non resolues.
6. La profondeur de recursion est limitee a 20 niveaux pour prevenir les references circulaires.

### 5.3 Variables d'environnement requises

| Variable | Module | Description |
|---|---|---|
| `NTL_MYSQL_USER` | Backup | Utilisateur MySQL |
| `NTL_MYSQL_PASSWORD` | Backup | Mot de passe MySQL |
| `NTL_SSH_USER` | Diagnostic | Utilisateur SSH |
| `NTL_SSH_PASSWORD` | Diagnostic | Mot de passe SSH |
| `NTL_WINRM_USER` | Diagnostic | Utilisateur WinRM (AD) |
| `NTL_WINRM_PASSWORD` | Diagnostic | Mot de passe WinRM (AD) |

### 5.4 Mesures de securite

| Mesure | Implementation |
|---|---|
| **Secrets hors du code** | Variables d'environnement via `.env` + `${VAR}` dans YAML |
| **Mot de passe MySQL** | Passe via `MYSQL_PWD` (env var) et non en argument CLI |
| **Prevention injection SQL** | Validation regex des noms de table : `^[a-zA-Z_]\w{0,63}$` |
| **Prevention path traversal** | `validate_path_within()` verifie que les chemins restent dans les repertoires autorises |
| **Validation des entrees CLI** | Regex `^[a-zA-Z0-9._:/%\-]+$`, longueur max 255, rejet de `..` |
| **Validation des plages reseau** | `ipaddress.ip_network()` pour prevenir les injections nmap |
| **Validation des ports** | Verification dans l'intervalle [1, 65535] |
| **Sanitisation des noms de fichier** | `sanitize_filename_part()` remplace les caracteres non surs |
| **YAML safe_load** | Utilisation de `yaml.safe_load()` (pas de `yaml.load()`) pour prevenir l'execution de code arbitraire |
| **SSL desactive en lab** | Verification SSL desactivee par defaut, activable via `verify_ssl=True` |
| **Lecture HTTP limitee** | Body limite a 1 Mo (`_MAX_HTTP_BODY`) pour prevenir les debordements memoire |

### 5.5 Fichier .gitignore

Les fichiers sensibles et les sorties sont exclus du versionning :
- `config/config.yaml` (contient des secrets resolus)
- `.env` (contient les secrets en clair)
- `output/` (resultats, logs, dumps, exports)

---

## 6. Infrastructure de test

### 6.1 Lab Proxmox

L'infrastructure de test reproduit fidelement l'environnement de production de NTL dans un lab virtualise sur Proxmox VE.

**Reseau** : `192.168.10.0/24`

### 6.2 Machines virtuelles

| VMID | Hostname | OS | IP | vCPU | RAM | Disque | Role |
|------|----------|----|----|------|-----|--------|------|
| 1010 | DC01 | Windows Server 2022 | .10 | 2 | 4 Go | 40 Go | Domain Controller (AD/DNS) |
| 1011 | DC02 | Windows Server 2019 | .11 | 2 | 4 Go | 40 Go | DC Secondaire |
| 1012 | SRV-FILE | Windows Server 2012 R2 | .12 | 1 | 2 Go | 40 Go | Serveur de fichiers (legacy) |
| 1013 | SRV-PRINT | Windows Server 2008 R2 | .13 | 1 | 2 Go | 20 Go | Serveur d'impression |
| 1015 | SUPER-01 | Windows Server 2016 | .15 | 2 | 4 Go | 40 Go | Supervision Zabbix |
| 1021 | WMS-DB | Ubuntu 20.04 | .21 | 2 | 2 Go | 20 Go | Base de donnees MySQL (WMS) |
| 1022 | WMS-APP | Ubuntu 20.04 | .22 | 2 | 2 Go | 20 Go | Application WMS |
| 1030 | IPBX-VM | CentOS 7 | .30 | 2 | 2 Go | 20 Go | Telephonie (IPBX) |
| 1040 | NAS-01 | Debian 10 | .40 | 1 | 1 Go | 50 Go | NAS de sauvegarde |
| 1041 | SRV-INTRANET | Debian 11 | .41 | 1 | 1 Go | 20 Go | Intranet / Wiki |
| 1042 | SRV-BACKUP | Ubuntu 16.04 | .42 | 1 | 1 Go | 20 Go | Scripts de sauvegarde |
| 1043 | SRV-CDK | Ubuntu 18.04 | .43 | 1 | 1 Go | 10 Go | Cross-dock saisonnier |
| 1050 | PC-SIEGE-01 | Windows 11 | .50 | 2 | 4 Go | 40 Go | Poste de travail (siege) |
| 1051 | PC-SIEGE-02 | Windows 11 | .51 | 2 | 4 Go | 40 Go | Poste de travail (siege) |
| 1052 | PC-COMPTA-01 | Windows 10 | .52 | 2 | 4 Go | 40 Go | Poste comptabilite |
| 1060 | PC-QUAI-WH1 | Windows 7 | .60 | 1 | 2 Go | 30 Go | Terminal quai Lens |
| 1061 | PC-QUAI-WH2 | Windows 7 | .61 | 1 | 2 Go | 30 Go | Terminal quai Valenciennes |
| 1062 | PC-QUAI-WH3 | Windows 10 | .62 | 2 | 4 Go | 40 Go | Terminal quai Arras |

**Total** : 18 VMs, architecture heterogene representative d'une PME.

### 6.3 Diagramme reseau du lab

```
                    ┌─────────────────────┐
                    │    Proxmox VE Host   │
                    │   192.168.10.0/24    │
                    └─────────┬───────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
     ┌──────┴──────┐   ┌─────┴──────┐   ┌──────┴──────┐
     │   Serveurs   │   │   Serveurs  │   │   Postes    │
     │   Windows    │   │   Linux     │   │   Clients   │
     └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
            │                 │                 │
  ┌─────────┼─────┐    ┌─────┼──────┐    ┌─────┼──────┐
  │         │     │    │     │      │    │     │      │
DC01    SRV-FILE  │  WMS-DB  │   NAS-01  │  PC-SIEGE  │
(.10)   (.12)     │  (.21)   │   (.40)   │  (.50-52)  │
DC02    SRV-PRINT │  WMS-APP │  SRV-INT  │  PC-QUAI   │
(.11)   (.13)     │  (.22)   │  (.41)    │  (.60-62)  │
SUPER-01          │  IPBX-VM │  SRV-BKP  │            │
(.15)             │  (.30)   │  (.42)    │            │
                  │  SRV-CDK │          │            │
                  │  (.43)   │          │            │
                  └──────────┘          └────────────┘
```

### 6.4 Provisioning automatise

Le lab est provisionne automatiquement via :

- **Proxmox scripts** : `orchestrate-lab.sh` pour la creation et la configuration des VMs a partir du fichier `vms.csv` et des profils definis dans `profiles.conf`.
- **Cloud-init** (Linux) / **autounattend.xml** (Windows) : configuration initiale des VMs (hostname, reseau, utilisateurs).
- **Scripts post-installation** : scripts PowerShell (`.ps1`) pour Windows et Bash (`.sh`) pour Linux pour la configuration specifique de chaque role.

### 6.5 Deploiement Ansible

Le deploiement de l'application et la configuration des services sont automatises via 7 playbooks Ansible :

| Playbook | Description |
|---|---|
| `01-create-vms.yml` | Creation des VMs sur Proxmox |
| `02-configure-dc01.yml` | Configuration du DC principal (AD, DNS, DHCP) |
| `03-configure-wmsdb.yml` | Configuration du serveur MySQL (WMS) |
| `04-configure-srvfiles.yml` | Configuration du serveur de fichiers |
| `05-configure-wmsapp.yml` | Configuration du serveur applicatif WMS |
| `06-configure-backup.yml` | Configuration du serveur de sauvegarde |
| `07-join-domain-clients.yml` | Jonction au domaine des postes clients |
| `site.yml` | Playbook principal orchestrant l'ensemble |

---

## 7. Integration continue (CI/CD)

### 7.1 Pipeline GitHub Actions

Le projet dispose d'un pipeline CI automatise via GitHub Actions, declenche sur chaque push et pull request vers les branches `main` et `master`.

**Fichier** : `.github/workflows/ci.yml`

### 7.2 Jobs du pipeline

```
┌─────────────────────────────────────────────────┐
│              GitHub Actions — CI                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────────────────────────┐            │
│  │         Job: Lint               │            │
│  │  Python 3.10                    │            │
│  │  ├── ruff check src/ tests/     │            │
│  │  └── mypy src/                  │            │
│  └─────────────────────────────────┘            │
│                                                 │
│  ┌─────────────────────────────────┐            │
│  │         Job: Test               │            │
│  │  Matrice : 3.10, 3.11, 3.12    │            │
│  │  ├── pytest tests/ -v          │            │
│  │  ├── --cov=src                  │            │
│  │  ├── --cov-fail-under=50       │            │
│  │  └── Upload coverage (3.10)     │            │
│  └─────────────────────────────────┘            │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 7.3 Outils d'analyse

| Outil | Role | Configuration |
|---|---|---|
| **ruff** | Linting Python (PEP 8, imports, erreurs) | `target-version = "py310"`, `line-length = 120`, rules `E, F, W, I` |
| **mypy** | Verification de typage statique | `python_version = "3.10"`, `check_untyped_defs = true` |
| **pytest** | Framework de tests unitaires | `testpaths = ["tests"]`, verbosity activee |
| **pytest-cov** | Mesure de couverture de code | Seuil minimum : 50%, rapport XML + terminal |

### 7.4 Couverture de tests

Le projet comprend **52+ cas de test** repartis sur **8 fichiers** :

| Fichier de test | Module couvert | Focus |
|---|---|---|
| `test_interfaces.py` | `interfaces.py` | `build_result()`, validation status/exit_code |
| `test_config_loader.py` | `config_loader.py` | Chargement YAML, resolution `${VAR}`, erreurs |
| `test_diagnostic.py` | `modules/diagnostic/` | Dispatch, checks AD/DNS/MySQL/Linux/HTTP |
| `test_backup.py` | `modules/backup.py` | Dump SQL, export CSV, validation table |
| `test_audit.py` | `modules/audit/` | Scan, EOL, CSV, rapport |
| `test_network.py` | `utils/network.py` | check_port, ping, DNS, banner, HTTP |
| `test_output.py` | `utils/output.py` | Logging, save JSON, print Rich |

**Seuil de couverture** : 50% minimum (applique par `--cov-fail-under=50` dans le pipeline CI).

### 7.5 Matrice de compatibilite

Les tests sont executes sur trois versions de Python pour garantir la compatibilite :

| Version Python | Support |
|---|---|
| 3.10 | Version minimale cible + upload couverture |
| 3.11 | Version intermediaire |
| 3.12 | Derniere version stable |

---

## 8. Bilan et perspectives

### 8.1 Bilan technique

Le projet NTL-SysToolbox repond aux objectifs initiaux en livrant un outil CLI fonctionnel, modulaire et teste :

- **Architecture modulaire** : les trois modules (Diagnostic, Backup, Audit) sont independants et communiquent via un contrat d'interface strict (`build_result()`), ce qui facilite la maintenance et l'evolution.
- **Securite** : les credentials ne sont jamais exposes dans le code source, les entrees utilisateur sont validees et sanitisees, et les chemins de fichiers sont controles contre le path traversal.
- **Cross-platform** : l'outil fonctionne sur Windows et Linux grace a l'utilisation de bibliotheques multiplateformes et a la detection dynamique de l'OS.
- **Tracabilite** : chaque operation produit un resultat JSON horodate, persiste automatiquement dans un fichier.
- **Qualite du code** : le pipeline CI assure le linting, le typage statique et une couverture de tests minimum a chaque commit.

### 8.2 Repartition du travail

| Membre | Contribution |
|---|---|
| Ianis PUICHAUD | Architecture globale, CLI (`main.py`), configuration (`config_loader.py`), interfaces (`interfaces.py`), utilitaires (`output.py`, `network.py`, `validation.py`), CI/CD, infrastructure |
| Blaise WANDA NKONG | Module Diagnostic (`checks.py`, `constant.py`), verifications AD/DNS/MySQL/Linux/HTTP |
| Ojvind LANTSIGBLE | Module Backup (`backup.py`), dump MySQL, export CSV |
| Zaid ABOUYAALA | Module Audit (`scanner.py`), scan reseau, EOL, inventaire CSV, rapport, documentation |

### 8.3 Perspectives d'evolution

| Axe | Description |
|---|---|
| **Notifications** | Integration de notifications par email ou webhook (Slack, Teams) lors de la detection d'anomalies critiques |
| **Planification** | Ajout d'un mode non-interactif avec arguments CLI pour l'execution planifiee via cron/Task Scheduler |
| **Dashboard** | Generation de rapports HTML avec graphiques pour les presentations a la direction |
| **Checksum des backups** | Ajout de la verification SHA-256 des dumps SQL pour garantir l'integrite |
| **SNMP** | Integration du protocole SNMP pour la surveillance des equipements reseau (switches, routeurs) |
| **Conteneurisation** | Packaging Docker de l'outil pour un deploiement simplifie |
| **Couverture de tests** | Augmentation du seuil de couverture au-dela de 80% avec des tests d'integration |

---

*Document genere le 27 mars 2026 -- NTL-SysToolbox v1.0*
*MSPR TPRE511 -- Bloc E6.1 "Concevoir et tester des solutions applicatives"*
