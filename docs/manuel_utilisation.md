# Manuel d'utilisation -- NTL-SysToolbox

**Version :** 1.0
**Date :** Mars 2026
**Projet :** MSPR TPRE511 -- NordTransit Logistics
**Public cible :** Techniciens IT, administrateurs systeme

---

## Table des matieres

1. [Presentation generale](#1-presentation-generale)
2. [Prerequis](#2-prerequis)
3. [Installation](#3-installation)
   - 3.1 [Windows](#31-installation-sous-windows)
   - 3.2 [Linux](#32-installation-sous-linux)
4. [Configuration](#4-configuration)
   - 4.1 [Fichier config.yaml](#41-fichier-configyaml)
   - 4.2 [Variables d'environnement (.env)](#42-variables-denvironnement-env)
5. [Lancement de l'application](#5-lancement-de-lapplication)
6. [Module Diagnostic](#6-module-diagnostic)
   - 6.1 [Verification AD/DNS](#61-verification-addns)
   - 6.2 [Verification MySQL](#62-verification-mysql)
   - 6.3 [Verification services Linux](#63-verification-services-linux)
   - 6.4 [Verification HTTP/HTTPS](#64-verification-httphttps)
7. [Module Backup](#7-module-backup)
   - 7.1 [Sauvegarde base de donnees (dump SQL)](#71-sauvegarde-base-de-donnees-dump-sql)
   - 7.2 [Export table en CSV](#72-export-table-en-csv)
8. [Module Audit](#8-module-audit)
   - 8.1 [Scan reseau](#81-scan-reseau)
   - 8.2 [Liste des dates EOL](#82-liste-des-dates-eol)
   - 8.3 [Audit depuis un CSV](#83-audit-depuis-un-csv)
   - 8.4 [Rapport complet](#84-rapport-complet)
9. [Format de sortie JSON](#9-format-de-sortie-json)
10. [Codes de sortie](#10-codes-de-sortie)
11. [Arborescence des fichiers generes](#11-arborescence-des-fichiers-generes)
12. [Resolution de problemes](#12-resolution-de-problemes)
13. [Commandes de developpement](#13-commandes-de-developpement)
14. [Annexes](#14-annexes)

---

## 1. Presentation generale

**NTL-SysToolbox** est un outil en ligne de commande (CLI) interactif developpe en Python pour **NordTransit Logistics**. Il permet aux techniciens IT de realiser trois types d'operations depuis une interface unifiee :

| Module        | Fonction                                                      |
|---------------|---------------------------------------------------------------|
| **Diagnostic** | Verification de l'etat des services reseau (AD/DNS, MySQL, Linux, HTTP) |
| **Backup**     | Sauvegarde de bases MySQL (dump SQL) et export de tables en CSV          |
| **Audit**      | Scan reseau, detection de systemes en fin de vie (EOL), rapports         |

L'outil est concu pour etre **cross-platform** (Windows et Linux) et produit des resultats au format JSON standardise, exploitables par d'autres outils ou pour du reporting.

---

## 2. Prerequis

### Logiciels requis

| Logiciel       | Version minimale | Obligatoire | Remarque                              |
|----------------|------------------|-------------|---------------------------------------|
| Python         | 3.10+            | Oui         | 3.12 recommande                       |
| Git            | 2.x              | Oui         | Pour cloner le depot                  |
| Make           | -                | Oui         | Presente par defaut sous Linux        |
| nmap           | 7.x              | Non*        | Requis pour le module Audit (scan)    |
| mysqldump      | 8.x              | Non*        | Requis pour le module Backup (dump)   |

> \* Ces outils ne sont necessaires que si vous utilisez les fonctions correspondantes.

### Acces reseau

- Acces au reseau de l'infrastructure NordTransit Logistics
- Credentials MySQL (utilisateur + mot de passe)
- Credentials SSH pour les serveurs Linux
- Credentials WinRM pour le Domain Controller (optionnel)

---

## 3. Installation

### 3.1 Installation sous Windows

**Etape 1 -- Installer Python 3.12**

```powershell
winget install Python.Python.3.12
```

Verifier l'installation :

```bash
python --version
# Attendu : Python 3.12.x
```

**Etape 2 -- Installer Git et Make**

```powershell
winget install Git.Git
```

> Make est disponible via Git Bash ou en installant `make` via Chocolatey : `choco install make`

**Etape 3 -- Cloner le depot et configurer l'environnement**

```bash
git clone https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox.git
cd MSPR2-NTL-SysToolbox
make setup
```

<!-- [Capture d'ecran : terminal apres make setup reussi] -->

**Etape 4 -- Activer l'environnement virtuel**

```bash
# Git Bash
source venv/Scripts/activate

# CMD
venv\Scripts\activate

# PowerShell
.\venv\Scripts\Activate.ps1
```

### 3.2 Installation sous Linux

```bash
git clone https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox.git
cd MSPR2-NTL-SysToolbox
make setup-linux
source venv/bin/activate
```

### 3.3 Installation des outils de developpement (optionnel)

Pour les contributeurs au projet :

```bash
make setup-dev
```

Cela installe `ruff`, `mypy`, `pytest` et `pytest-cov`.

---

## 4. Configuration

Deux fichiers doivent etre configures avant la premiere utilisation.

### 4.1 Fichier config.yaml

Copier le modele fourni :

```bash
cp config/config.example.yaml config/config.yaml
```

Ouvrir `config/config.yaml` et adapter les valeurs a votre infrastructure.

#### Structure du fichier

```yaml
# --- Parametres generaux ---
general:
  log_level: INFO          # Niveaux : DEBUG, INFO, WARNING
  output_dir: ./output     # Repertoire de sortie des fichiers generes
  timeout: 10              # Timeout par defaut en secondes

# --- Machines cibles ---
targets:
  dc01:
    host: 192.168.10.10
    type: windows
    description: "Domain Controller — AD/DNS"
  wms_db:
    host: 192.168.10.21
    type: linux
    description: "WMS Database Server"

# --- Connexion MySQL ---
mysql:
  host: 192.168.10.21
  port: 3306
  user: "${NTL_MYSQL_USER}"       # Resolu depuis .env
  password: "${NTL_MYSQL_PASSWORD}" # Resolu depuis .env
  database: wms

# --- Connexion SSH ---
ssh:
  host: 192.168.10.21
  port: 22
  user: "${NTL_SSH_USER}"
  password: "${NTL_SSH_PASSWORD}"
  # key_file: ~/.ssh/id_rsa       # Alternative au mot de passe

# --- Decouverte reseau ---
discovery:
  network_range: "172.16.135.0/24"
  timeout: 2
  ports:
    - 22    # SSH
    - 80    # HTTP
    - 443   # HTTPS
    - 3306  # MySQL
    - 5432  # PostgreSQL
    - 8006  # Proxmox
    - 8080  # HTTP proxy

# --- WinRM (optionnel) ---
winrm:
  user: "${NTL_WINRM_USER}"
  password: "${NTL_WINRM_PASSWORD}"

# --- Audit ---
audit:
  network_range: "172.16.135.0/24"
  eol_database: "./data/eol_database.json"
  inventory_csv: "./data/sample_inventory.csv"
```

> **Important :** Les valeurs entre `${...}` sont resolues automatiquement depuis les variables d'environnement definies dans le fichier `.env`. Ne remplacez pas ces marqueurs directement.

### 4.2 Variables d'environnement (.env)

Copier le modele fourni :

```bash
cp .env.example .env
```

Editer `.env` avec vos identifiants reels :

```ini
# MySQL
NTL_MYSQL_USER=wms_user
NTL_MYSQL_PASSWORD=VotreMotDePasseMySQL

# SSH (acces WMS-DB Ubuntu)
NTL_SSH_USER=sysadmin
NTL_SSH_PASSWORD=VotreMotDePasseSSH

# General
NTL_GENERAL_LOG_LEVEL=INFO
```

> **Securite :** Le fichier `.env` contient des identifiants sensibles. Il est exclu du depot Git via `.gitignore`. Ne le commitez jamais.

---

## 5. Lancement de l'application

### Demarrage

```bash
make run
```

Ou directement :

```bash
python src/main.py
```

### Option : fichier de configuration alternatif

```bash
python src/main.py --config config/mon_config.yaml
```

### Menu principal

Au lancement, le menu principal s'affiche :

```
── NTL-SysToolbox ──
  1. Diagnostic
  2. Backup
  3. Audit
  0. Quitter

  Choix :
```

<!-- [Capture d'ecran : menu principal NTL-SysToolbox] -->

Saisissez le numero du module souhaite et appuyez sur **Entree**.

### Navigation

- Chaque module ouvre un **sous-menu** avec ses fonctions specifiques.
- Saisissez `0` pour **revenir au menu precedent**.
- Saisissez `0` depuis le menu principal pour **quitter** l'application.
- `Ctrl+C` permet de quitter a tout moment.

---

## 6. Module Diagnostic

Le module Diagnostic permet de verifier l'etat des services de l'infrastructure.

### Sous-menu Diagnostic

```
── Diagnostic ──
  1. Verifier AD/DNS (DC01)
  2. Verifier MySQL (port + version)
  3. Verifier services Linux (multi-ports)
  4. Verifier HTTP/HTTPS
  0. Retour

  Choix :
```

<!-- [Capture d'ecran : sous-menu Diagnostic] -->

---

### 6.1 Verification AD/DNS

**Objectif :** Verifier que le Domain Controller repond correctement aux requetes DNS, que les ports Active Directory sont ouverts, que le service LDAP est accessible, et (optionnellement) que les services Windows tournent via WinRM.

**Utilisation :**

1. Choisir `1` dans le sous-menu Diagnostic.
2. Saisir l'adresse IP du Domain Controller (ou appuyer sur Entree pour utiliser la valeur par defaut `dc01` dans `config.yaml`).

```
  Choix : 1
  IP du DC (defaut: dc01) : 192.168.10.10
```

**Verifications effectuees :**

| Test     | Description                                    |
|----------|------------------------------------------------|
| DNS      | Resolution de nom via le serveur DNS cible     |
| Ports    | Verification des ports AD (389, 636, 88, etc.) |
| LDAP     | Connexion LDAP au serveur                      |
| Services | Etat des services Windows via WinRM (optionnel)|

**Exemple de resultat :**

```
  [OK] AD/DNS check OK sur 192.168.10.10
```

<!-- [Capture d'ecran : resultat check AD/DNS] -->

---

### 6.2 Verification MySQL

**Objectif :** Verifier que le serveur MySQL est accessible sur le port configure et recuperer sa version.

**Utilisation :**

1. Choisir `2` dans le sous-menu Diagnostic.
2. Saisir l'adresse IP du serveur MySQL (ou Entree pour la valeur par defaut).

```
  Choix : 2
  IP du serveur MySQL : 192.168.10.21
```

**Exemple de resultat :**

```
  [OK] MySQL accessible sur 192.168.10.21:3306 (version 8.0.35)
```

---

### 6.3 Verification services Linux

**Objectif :** Scanner les ports ouverts sur un serveur Linux pour detecter les services actifs.

**Utilisation :**

1. Choisir `3` dans le sous-menu Diagnostic.
2. Saisir l'adresse IP du serveur Linux.

```
  Choix : 3
  IP du serveur Linux : 192.168.10.21
```

Les ports scannes sont ceux definis dans la section `discovery.ports` de `config.yaml`.

**Exemple de resultat :**

```
  [OK] 3 service(s) trouve(s) sur 192.168.10.21: SSH, HTTP, MySQL
```

---

### 6.4 Verification HTTP/HTTPS

**Objectif :** Verifier qu'un service web repond correctement sur un port donne.

**Utilisation :**

1. Choisir `4` dans le sous-menu Diagnostic.
2. Saisir l'adresse IP et eventuellement le port (format `IP:port`).

```
  Choix : 4
  IP[:port] du serveur HTTP (defaut: port 80) : 192.168.10.21:8080
```

> Si aucun port n'est specifie, le port **80** est utilise par defaut.

**Exemple de resultat :**

```
  [OK] HTTP 200 sur 192.168.10.21:8080 — 45ms (Server: nginx/1.24)
```

---

## 7. Module Backup

Le module Backup permet de sauvegarder les donnees MySQL.

### Sous-menu Backup

```
── Backup ──
  1. Backup base de donnees (dump SQL)
  2. Export table en CSV
  0. Retour

  Choix :
```

<!-- [Capture d'ecran : sous-menu Backup] -->

### Prerequis du module

- L'utilitaire `mysqldump` doit etre installe et accessible dans le PATH (pour le dump SQL).
- Les identifiants MySQL doivent etre configures dans `.env`.

---

### 7.1 Sauvegarde base de donnees (dump SQL)

**Objectif :** Creer un dump complet d'une base de donnees MySQL au format SQL.

**Utilisation :**

1. Choisir `1` dans le sous-menu Backup.
2. Saisir le nom de la base de donnees (ou Entree pour `wms` par defaut).

```
  Choix : 1
  Base a sauvegarder (defaut: wms) : wms
```

**Fichier genere :**

```
output/backups/wms_20260327_143022.sql
```

Le nom du fichier suit le format : `{base}_{date}_{heure}.sql`

**Exemple de resultat :**

```
  [OK] Backup wms sauvegarde: output/backups/wms_20260327_143022.sql (245780 octets)
```

**Options du dump :**

- `--single-transaction` : sauvegarde coherente sans verrouiller les tables.
- `--routines` : inclut les procedures stockees et fonctions.

<!-- [Capture d'ecran : resultat backup SQL] -->

---

### 7.2 Export table en CSV

**Objectif :** Exporter le contenu d'une table MySQL au format CSV.

**Utilisation :**

1. Choisir `2` dans le sous-menu Backup.
2. Saisir le nom exact de la table a exporter.

```
  Choix : 2
  Table a exporter (ex: shipments) : shipments
```

**Fichier genere :**

```
output/exports/shipments_20260327_143215.csv
```

**Exemple de resultat :**

```
  [OK] Export shipments: 1523 lignes -> output/exports/shipments_20260327_143215.csv
```

> **Note :** Le nom de table doit respecter les conventions SQL (lettres, chiffres, underscores, 64 caracteres maximum).

---

## 8. Module Audit

Le module Audit permet de cartographier le reseau, d'identifier les systemes obsoletes et de generer des rapports d'audit.

### Sous-menu Audit

```
── Audit ──
  1. Scanner le reseau
  2. Lister les dates EOL
  3. Auditer depuis un CSV
  4. Generer le rapport complet
  0. Retour

  Choix :
```

<!-- [Capture d'ecran : sous-menu Audit] -->

### Prerequis du module

- L'utilitaire `nmap` doit etre installe et accessible dans le PATH (pour le scan reseau).
- Le fichier `data/eol_database.json` doit etre present (pour les dates EOL).

---

### 8.1 Scan reseau

**Objectif :** Scanner une plage d'adresses IP pour detecter les hotes actifs et les categoriser.

**Utilisation :**

1. Choisir `1` dans le sous-menu Audit.
2. Saisir la plage reseau au format CIDR (ou Entree pour la valeur par defaut dans `config.yaml`).

```
  Choix : 1
  Plage reseau (defaut: config) : 172.16.135.0/24
```

**Exemple de resultat :**

```
  [OK] Scan termine: 12 host(s) trouve(s) sur 172.16.135.0/24
```

---

### 8.2 Liste des dates EOL

**Objectif :** Afficher les systemes d'exploitation recenses dans la base EOL et identifier ceux en fin de vie.

**Utilisation :**

1. Choisir `2` dans le sous-menu Audit.
2. Appuyer sur Entree pour lancer.

```
  Choix : 2
  Appuyez sur Entree pour continuer :
```

**Exemple de resultat :**

```
  [WARNING] 3/15 OS en fin de vie
```

---

### 8.3 Audit depuis un CSV

**Objectif :** Realiser un audit a partir d'un fichier d'inventaire CSV contenant la liste des machines.

**Utilisation :**

1. Choisir `3` dans le sous-menu Audit.
2. Saisir le chemin du fichier CSV (ou Entree pour utiliser le chemin par defaut dans `config.yaml`).

```
  Choix : 3
  Chemin du CSV (defaut: config) : ./data/sample_inventory.csv
```

**Exemple de resultat :**

```
  [OK] Inventaire: 25 hosts, 22 joignables, 4 EOL
```

---

### 8.4 Rapport complet

**Objectif :** Generer un rapport d'audit complet combinant scan reseau, verification EOL et inventaire.

**Utilisation :**

1. Choisir `4` dans le sous-menu Audit.
2. Appuyer sur Entree pour lancer la generation.

```
  Choix : 4
  Appuyez sur Entree pour continuer :
```

**Fichier genere :**

Le rapport est sauvegarde dans le repertoire `output/reports/`.

**Exemple de resultat :**

```
  [OK] Rapport genere: output/reports/audit_20260327_144500.json
```

---

## 9. Format de sortie JSON

Chaque operation produit un resultat au **format JSON standardise**. Ce format est identique quel que soit le module utilise.

### Structure

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
    "version": "8.0.35",
    "port": 3306
  },
  "message": "MySQL accessible sur 192.168.10.21:3306 (version 8.0.35)"
}
```

### Description des champs

| Champ       | Type   | Description                                          |
|-------------|--------|------------------------------------------------------|
| `module`    | string | Nom du module : `diagnostic`, `backup` ou `audit`    |
| `function`  | string | Nom de la fonction executee                          |
| `timestamp` | string | Horodatage UTC au format ISO-8601                    |
| `status`    | string | Etat du resultat (voir section suivante)             |
| `exit_code` | int    | Code de sortie numerique (voir section suivante)     |
| `target`    | string | Cible de l'operation (IP, base, plage reseau...)     |
| `details`   | object | Donnees specifiques au module et a la fonction       |
| `message`   | string | Description lisible du resultat                      |

Les resultats sont automatiquement sauvegardes dans `output/logs/` au format JSON.

---

## 10. Codes de sortie

Chaque resultat est associe a un **status** et un **code de sortie** normalises :

| Code | Status     | Signification                                          | Exemple                          |
|------|------------|--------------------------------------------------------|----------------------------------|
| 0    | `OK`       | L'operation a reussi, le service fonctionne            | MySQL accessible, backup termine |
| 1    | `WARNING`  | Degradation detectee, fonctionnement partiel           | Couverture WinRM incomplete      |
| 2    | `CRITICAL` | Service inaccessible, echec de l'operation             | MySQL injoignable, dump echoue   |
| 3    | `UNKNOWN`  | Impossible de determiner l'etat (timeout, erreur)      | Cible injoignable, timeout       |

---

## 11. Arborescence des fichiers generes

L'ensemble des fichiers produits par NTL-SysToolbox est organise dans le repertoire `output/` :

```
output/
  logs/                          # Logs JSON de chaque operation
    diagnostic_check_mysql_20260327_143022.json
    backup_backup_database_20260327_143055.json
    ...
  backups/                       # Dumps SQL des bases de donnees
    wms_20260327_143022.sql
    ...
  exports/                       # Exports CSV des tables
    shipments_20260327_143215.csv
    ...
  reports/                       # Rapports d'audit
    audit_20260327_144500.json
    ...
```

> Le repertoire `output/` est cree automatiquement au premier lancement si necessaire.

---

## 12. Resolution de problemes

### Problemes frequents

| Symptome                                         | Cause probable                              | Solution                                                    |
|--------------------------------------------------|---------------------------------------------|-------------------------------------------------------------|
| `python: command not found`                      | Python non installe ou absent du PATH       | Installer Python 3.10+ et verifier le PATH                  |
| Erreur au lancement : config manquant            | `config.yaml` absent                        | Copier `config.example.yaml` vers `config.yaml`             |
| Erreur : variables non resolues (`${...}`)       | Fichier `.env` absent ou incomplet          | Copier `.env.example` vers `.env` et remplir les valeurs    |
| `MySQL connection refused`                       | Serveur MySQL eteint ou IP incorrecte       | Verifier que WMS-DB est demarre et que l'IP est correcte    |
| `Access denied` sur MySQL                        | Mauvais identifiants                        | Verifier `NTL_MYSQL_USER` et `NTL_MYSQL_PASSWORD` dans `.env` |
| `nmap: command not found`                        | nmap non installe                           | Installer nmap (`apt install nmap` ou telechargement Windows) |
| `mysqldump: command not found`                   | mysql-client non installe                   | Installer mysql-client (`apt install mysql-client`)          |
| `Permission denied`                              | Droits insuffisants                         | Executer avec les privileges adaptes (sudo sous Linux)       |
| `Module Xxx non disponible`                      | Dependance Python manquante                 | Relancer `make setup` ou `pip install -r requirements.txt`   |
| Timeout sur une operation                        | Cible lente ou injoignable                  | Augmenter `general.timeout` dans `config.yaml`               |

### Activer le mode debug

Pour obtenir des logs detailles, modifier le niveau de log :

**Option 1 -- Via le fichier `.env` :**

```ini
NTL_GENERAL_LOG_LEVEL=DEBUG
```

**Option 2 -- Via `config.yaml` :**

```yaml
general:
  log_level: DEBUG
```

Les logs detailles permettent d'identifier la source exacte d'une erreur.

---

## 13. Commandes de developpement

Ces commandes sont destinees aux contributeurs du projet.

| Commande            | Description                                        |
|---------------------|----------------------------------------------------|
| `make setup`        | Creer le venv et installer les dependances (Windows)|
| `make setup-linux`  | Creer le venv et installer les dependances (Linux)  |
| `make setup-dev`    | Installer les outils de developpement               |
| `make run`          | Lancer le CLI                                        |
| `make test`         | Lancer les tests unitaires avec couverture           |
| `make lint`         | Verifier le code avec ruff                           |
| `make typecheck`    | Verifier les types avec mypy                         |
| `make clean`        | Supprimer les fichiers generes et le cache           |
| `make help`         | Afficher la liste des commandes disponibles          |

---

## 14. Annexes

### A. Dependances Python

Le projet utilise les bibliotheques suivantes (installees automatiquement via `make setup`) :

| Bibliotheque             | Usage                                      |
|--------------------------|--------------------------------------------|
| `rich`                   | Affichage ameliore du CLI (tableaux, couleurs) |
| `mysql-connector-python` | Connexion MySQL pour le module Backup      |
| `paramiko`               | Connexion SSH pour les verifications Linux |
| `dnspython`              | Resolution DNS pour le module Diagnostic   |
| `python-nmap`            | Interface Python pour nmap (module Audit)  |
| `pyyaml`                 | Lecture du fichier de configuration YAML   |
| `psutil`                 | Informations systeme                       |
| `ldap3`                  | Verification LDAP/Active Directory         |
| `python-dotenv`          | Chargement des variables `.env`            |

### B. Schema de navigation du CLI

```
Menu principal
  |
  |-- [1] Diagnostic
  |     |-- [1] Verifier AD/DNS (DC01)
  |     |-- [2] Verifier MySQL (port + version)
  |     |-- [3] Verifier services Linux (multi-ports)
  |     |-- [4] Verifier HTTP/HTTPS
  |     |-- [0] Retour
  |
  |-- [2] Backup
  |     |-- [1] Backup base de donnees (dump SQL)
  |     |-- [2] Export table en CSV
  |     |-- [0] Retour
  |
  |-- [3] Audit
  |     |-- [1] Scanner le reseau
  |     |-- [2] Lister les dates EOL
  |     |-- [3] Auditer depuis un CSV
  |     |-- [4] Generer le rapport complet
  |     |-- [0] Retour
  |
  |-- [0] Quitter
```

### C. Fichiers de configuration de reference

- `config/config.example.yaml` -- Modele de configuration
- `.env.example` -- Modele de variables d'environnement
- `data/eol_database.json` -- Base de donnees des dates de fin de vie
- `data/sample_inventory.csv` -- Exemple d'inventaire pour l'audit CSV
