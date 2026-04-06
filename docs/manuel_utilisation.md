# Manuel d'utilisation -- NTL-SysToolbox

**Version :** 1.0
**Date :** Mars 2026
**Projet :** MSPR TPRE511 -- NordTransit Logistics
**Public cible :** Techniciens IT, administrateurs système

---

## Table des matières

1. [Présentation générale](#1-presentation-generale)
2. [Prérequis](#2-prerequis)
3. [Installation](#3-installation)
   - 3.1 [Windows](#31-installation-sous-windows)
   - 3.2 [Linux](#32-installation-sous-linux)
4. [Configuration](#4-configuration)
   - 4.1 [Fichier config.yaml](#41-fichier-configyaml)
   - 4.2 [Variables d'environnement (.env)](#42-variables-denvironnement-env)
5. [Lancement de l'application](#5-lancement-de-lapplication)
6. [Module Diagnostic](#6-module-diagnostic)
   - 6.1 [Vérification AD/DNS](#61-verification-addns)
   - 6.2 [Vérification MySQL](#62-verification-mysql)
   - 6.3 [Vérification services Linux](#63-verification-services-linux)
   - 6.4 [Vérification HTTP/HTTPS](#64-verification-httphttps)
7. [Module Backup](#7-module-backup)
   - 7.1 [Sauvegarde base de données (dump SQL)](#71-sauvegarde-base-de-donnees-dump-sql)
   - 7.2 [Export table en CSV](#72-export-table-en-csv)
8. [Module Audit](#8-module-audit)
   - 8.1 [Scan réseau](#81-scan-reseau)
   - 8.2 [Liste des dates EOL](#82-liste-des-dates-eol)
   - 8.3 [Audit depuis un CSV](#83-audit-depuis-un-csv)
   - 8.4 [Rapport complet](#84-rapport-complet)
9. [Format de sortie JSON](#9-format-de-sortie-json)
10. [Codes de sortie](#10-codes-de-sortie)
11. [Arborescence des fichiers générés](#11-arborescence-des-fichiers-generes)
12. [Résolution de problèmes](#12-resolution-de-problemes)
13. [Commandes de développement](#13-commandes-de-developpement)
14. [Annexes](#14-annexes)

---

## 1. Présentation générale

**NTL-SysToolbox** est un outil en ligne de commande (CLI) interactif développé en Python pour **NordTransit Logistics**. Il permet aux techniciens IT de réaliser trois types d'opérations depuis une interface unifiée :

| Module        | Fonction                                                      |
|---------------|---------------------------------------------------------------|
| **Diagnostic** | Vérification de l'état des services réseau (AD/DNS, MySQL, Linux, HTTP) |
| **Backup**     | Sauvegarde de bases MySQL (dump SQL) et export de tables en CSV          |
| **Audit**      | Scan réseau, détection de systèmes en fin de vie (EOL), rapports         |

L'outil est conçu pour être **cross-platform** (Windows et Linux) et produit des résultats au format JSON standardisé, exploitables par d'autres outils ou pour du reporting.

---

## 2. Prérequis

### Logiciels requis

| Logiciel       | Version minimale | Obligatoire | Remarque                              |
|----------------|------------------|-------------|---------------------------------------|
| Python         | 3.10+            | Oui         | 3.12 recommandé                       |
| Git            | 2.x              | Oui         | Pour cloner le dépôt                  |
| Make           | -                | Oui         | Présent par défaut sous Linux         |
| nmap           | 7.x              | Non*        | Requis pour le module Audit (scan)    |
| mysqldump      | 8.x              | Non*        | Requis pour le module Backup (dump)   |

> \* Ces outils ne sont nécessaires que si vous utilisez les fonctions correspondantes.

### Accès réseau

- Accès au réseau de l'infrastructure NordTransit Logistics
- Credentials MySQL (utilisateur + mot de passe)
- Credentials SSH pour les serveurs Linux
- Credentials WinRM pour le Domain Controller (optionnel)

---

## 3. Installation

### 3.1 Installation sous Windows

**Étape 1 -- Installer Python 3.12**

```powershell
winget install Python.Python.3.12
```

Vérifier l'installation :

```bash
python --version
# Attendu : Python 3.12.x
```

**Étape 2 -- Installer Git et Make**

```powershell
winget install Git.Git
```

> Make est disponible via Git Bash ou en installant `make` via Chocolatey : `choco install make`

**Étape 3 -- Cloner le dépôt et configurer l'environnement**

```bash
git clone https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox.git
cd MSPR2-NTL-SysToolbox
make setup
```

<!-- [Capture d'écran : terminal après make setup réussi] -->

**Étape 4 -- Activer l'environnement virtuel**

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

### 3.3 Installation des outils de développement (optionnel)

Pour les contributeurs au projet :

```bash
make setup-dev
```

Cela installe `ruff`, `mypy`, `pytest` et `pytest-cov`.

---

## 4. Configuration

Deux fichiers doivent être configurés avant la première utilisation.

### 4.1 Fichier config.yaml

Copier le modèle fourni :

```bash
cp config/config.example.yaml config/config.yaml
```

Ouvrir `config/config.yaml` et adapter les valeurs à votre infrastructure.

#### Structure du fichier

```yaml
# --- Paramètres généraux ---
general:
  log_level: INFO          # Niveaux : DEBUG, INFO, WARNING
  output_dir: ./output     # Répertoire de sortie des fichiers générés
  timeout: 10              # Timeout par défaut en secondes

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
  user: "${NTL_MYSQL_USER}"       # Résolu depuis .env
  password: "${NTL_MYSQL_PASSWORD}" # Résolu depuis .env
  database: wms

# --- Connexion SSH ---
ssh:
  host: 192.168.10.21
  port: 22
  user: "${NTL_SSH_USER}"
  password: "${NTL_SSH_PASSWORD}"
  # key_file: ~/.ssh/id_rsa       # Alternative au mot de passe

# --- Découverte réseau ---
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

> **Important :** Les valeurs entre `${...}` sont résolues automatiquement depuis les variables d'environnement définies dans le fichier `.env`. Ne remplacez pas ces marqueurs directement.

### 4.2 Variables d'environnement (.env)

Copier le modèle fourni :

```bash
cp .env.example .env
```

Éditer `.env` avec vos identifiants réels :

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

> **Sécurité :** Le fichier `.env` contient des identifiants sensibles. Il est exclu du dépôt Git via `.gitignore`. Ne le commitez jamais.

---

## 5. Lancement de l'application

### Démarrage

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

<!-- [Capture d'écran : menu principal NTL-SysToolbox] -->

Saisissez le numéro du module souhaité et appuyez sur **Entrée**.

### Navigation

- Chaque module ouvre un **sous-menu** avec ses fonctions spécifiques.
- Saisissez `0` pour **revenir au menu précédent**.
- Saisissez `0` depuis le menu principal pour **quitter** l'application.
- `Ctrl+C` permet de quitter à tout moment.

---

## 6. Module Diagnostic

Le module Diagnostic permet de vérifier l'état des services de l'infrastructure.

### Sous-menu Diagnostic

```
── Diagnostic ──
  1. Vérifier AD/DNS (DC01)
  2. Vérifier MySQL (port + version)
  3. Vérifier services Linux (multi-ports)
  4. Vérifier HTTP/HTTPS
  0. Retour

  Choix :
```

<!-- [Capture d'écran : sous-menu Diagnostic] -->

---

### 6.1 Vérification AD/DNS

**Objectif :** Vérifier que le Domain Controller répond correctement aux requêtes DNS, que les ports Active Directory sont ouverts, que le service LDAP est accessible, et (optionnellement) que les services Windows tournent via WinRM.

**Utilisation :**

1. Choisir `1` dans le sous-menu Diagnostic.
2. Saisir l'adresse IP du Domain Controller (ou appuyer sur Entrée pour utiliser la valeur par défaut `dc01` dans `config.yaml`).

```
  Choix : 1
  IP du DC (défaut: dc01) : 192.168.10.10
```

**Vérifications effectuées :**

| Test     | Description                                    |
|----------|------------------------------------------------|
| DNS      | Résolution de nom via le serveur DNS cible     |
| Ports    | Vérification des ports AD (389, 636, 88, etc.) |
| LDAP     | Connexion LDAP au serveur                      |
| Services | État des services Windows via WinRM (optionnel)|

**Exemple de résultat :**

```
  [OK] AD/DNS check OK sur 192.168.10.10
```

<!-- [Capture d'écran : résultat check AD/DNS] -->

---

### 6.2 Vérification MySQL

**Objectif :** Vérifier que le serveur MySQL est accessible sur le port configuré et récupérer sa version.

**Utilisation :**

1. Choisir `2` dans le sous-menu Diagnostic.
2. Saisir l'adresse IP du serveur MySQL (ou Entrée pour la valeur par défaut).

```
  Choix : 2
  IP du serveur MySQL : 192.168.10.21
```

**Exemple de résultat :**

```
  [OK] MySQL accessible sur 192.168.10.21:3306 (version 8.0.35)
```

---

### 6.3 Vérification services Linux

**Objectif :** Scanner les ports ouverts sur un serveur Linux pour détecter les services actifs.

**Utilisation :**

1. Choisir `3` dans le sous-menu Diagnostic.
2. Saisir l'adresse IP du serveur Linux.

```
  Choix : 3
  IP du serveur Linux : 192.168.10.21
```

Les ports scannés sont ceux définis dans la section `discovery.ports` de `config.yaml`.

**Exemple de résultat :**

```
  [OK] 3 service(s) trouvé(s) sur 192.168.10.21: SSH, HTTP, MySQL
```

---

### 6.4 Vérification HTTP/HTTPS

**Objectif :** Vérifier qu'un service web répond correctement sur un port donné.

**Utilisation :**

1. Choisir `4` dans le sous-menu Diagnostic.
2. Saisir l'adresse IP et éventuellement le port (format `IP:port`).

```
  Choix : 4
  IP[:port] du serveur HTTP (défaut: port 80) : 192.168.10.21:8080
```

> Si aucun port n'est spécifié, le port **80** est utilisé par défaut.

**Exemple de résultat :**

```
  [OK] HTTP 200 sur 192.168.10.21:8080 — 45ms (Server: nginx/1.24)
```

---

## 7. Module Backup

Le module Backup permet de sauvegarder les données MySQL.

### Sous-menu Backup

```
── Backup ──
  1. Backup base de données (dump SQL)
  2. Export table en CSV
  0. Retour

  Choix :
```

<!-- [Capture d'écran : sous-menu Backup] -->

### Prérequis du module

- L'utilitaire `mysqldump` doit être installé et accessible dans le PATH (pour le dump SQL).
- Les identifiants MySQL doivent être configurés dans `.env`.

---

### 7.1 Sauvegarde base de données (dump SQL)

**Objectif :** Créer un dump complet d'une base de données MySQL au format SQL.

**Utilisation :**

1. Choisir `1` dans le sous-menu Backup.
2. Saisir le nom de la base de données (ou Entrée pour `wms` par défaut).

```
  Choix : 1
  Base à sauvegarder (défaut: wms) : wms
```

**Fichier généré :**

```
output/backups/wms_20260327_143022.sql
```

Le nom du fichier suit le format : `{base}_{date}_{heure}.sql`

**Exemple de résultat :**

```
  [OK] Backup wms sauvegardé: output/backups/wms_20260327_143022.sql (245780 octets)
```

**Options du dump :**

- `--single-transaction` : sauvegarde cohérente sans verrouiller les tables.
- `--routines` : inclut les procédures stockées et fonctions.

<!-- [Capture d'écran : résultat backup SQL] -->

---

### 7.2 Export table en CSV

**Objectif :** Exporter le contenu d'une table MySQL au format CSV.

**Utilisation :**

1. Choisir `2` dans le sous-menu Backup.
2. Saisir le nom exact de la table à exporter.

```
  Choix : 2
  Table à exporter (ex: shipments) : shipments
```

**Fichier généré :**

```
output/exports/shipments_20260327_143215.csv
```

**Exemple de résultat :**

```
  [OK] Export shipments: 1523 lignes -> output/exports/shipments_20260327_143215.csv
```

> **Note :** Le nom de table doit respecter les conventions SQL (lettres, chiffres, underscores, 64 caractères maximum).

---

## 8. Module Audit

Le module Audit permet de cartographier le réseau, d'identifier les systèmes obsolètes et de générer des rapports d'audit.

### Sous-menu Audit

```
── Audit ──
  1. Scanner le réseau
  2. Lister les dates EOL
  3. Auditer depuis un CSV
  4. Générer le rapport complet
  0. Retour

  Choix :
```

<!-- [Capture d'écran : sous-menu Audit] -->

### Prérequis du module

- L'utilitaire `nmap` doit être installé et accessible dans le PATH (pour le scan réseau).
- Le fichier `data/eol_database.json` doit être présent (pour les dates EOL).

---

### 8.1 Scan réseau

**Objectif :** Scanner une plage d'adresses IP pour détecter les hôtes actifs et les catégoriser.

**Utilisation :**

1. Choisir `1` dans le sous-menu Audit.
2. Saisir la plage réseau au format CIDR (ou Entrée pour la valeur par défaut dans `config.yaml`).

```
  Choix : 1
  Plage réseau (défaut: config) : 172.16.135.0/24
```

**Exemple de résultat :**

```
  [OK] Scan terminé: 12 host(s) trouvé(s) sur 172.16.135.0/24
```

---

### 8.2 Liste des dates EOL

**Objectif :** Afficher les systèmes d'exploitation recensés dans la base EOL et identifier ceux en fin de vie.

**Utilisation :**

1. Choisir `2` dans le sous-menu Audit.
2. Appuyer sur Entrée pour lancer.

```
  Choix : 2
  Appuyez sur Entrée pour continuer :
```

**Exemple de résultat :**

```
  [WARNING] 3/15 OS en fin de vie
```

---

### 8.3 Audit depuis un CSV

**Objectif :** Réaliser un audit à partir d'un fichier d'inventaire CSV contenant la liste des machines.

**Utilisation :**

1. Choisir `3` dans le sous-menu Audit.
2. Saisir le chemin du fichier CSV (ou Entrée pour utiliser le chemin par défaut dans `config.yaml`).

```
  Choix : 3
  Chemin du CSV (défaut: config) : ./data/sample_inventory.csv
```

**Exemple de résultat :**

```
  [OK] Inventaire: 25 hosts, 22 joignables, 4 EOL
```

---

### 8.4 Rapport complet

**Objectif :** Générer un rapport d'audit complet combinant scan réseau, vérification EOL et inventaire.

**Utilisation :**

1. Choisir `4` dans le sous-menu Audit.
2. Appuyer sur Entrée pour lancer la génération.

```
  Choix : 4
  Appuyez sur Entrée pour continuer :
```

**Fichier généré :**

Le rapport est sauvegardé dans le répertoire `output/reports/`.

**Exemple de résultat :**

```
  [OK] Rapport généré: output/reports/audit_20260327_144500.json
```

---

## 9. Format de sortie JSON

Chaque opération produit un résultat au **format JSON standardisé**. Ce format est identique quel que soit le module utilisé.

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
| `function`  | string | Nom de la fonction exécutée                          |
| `timestamp` | string | Horodatage UTC au format ISO-8601                    |
| `status`    | string | État du résultat (voir section suivante)             |
| `exit_code` | int    | Code de sortie numérique (voir section suivante)     |
| `target`    | string | Cible de l'opération (IP, base, plage réseau...)     |
| `details`   | object | Données spécifiques au module et à la fonction       |
| `message`   | string | Description lisible du résultat                      |

Les résultats sont automatiquement sauvegardés dans `output/logs/` au format JSON.

---

## 10. Codes de sortie

Chaque résultat est associé à un **status** et un **code de sortie** normalisés :

| Code | Status     | Signification                                          | Exemple                          |
|------|------------|--------------------------------------------------------|----------------------------------|
| 0    | `OK`       | L'opération a réussi, le service fonctionne            | MySQL accessible, backup terminé |
| 1    | `WARNING`  | Dégradation détectée, fonctionnement partiel           | Couverture WinRM incomplète      |
| 2    | `CRITICAL` | Service inaccessible, échec de l'opération             | MySQL injoignable, dump échoué   |
| 3    | `UNKNOWN`  | Impossible de déterminer l'état (timeout, erreur)      | Cible injoignable, timeout       |

---

## 11. Arborescence des fichiers générés

L'ensemble des fichiers produits par NTL-SysToolbox est organisé dans le répertoire `output/` :

```
output/
  logs/                          # Logs JSON de chaque opération
    diagnostic_check_mysql_20260327_143022.json
    backup_backup_database_20260327_143055.json
    ...
  backups/                       # Dumps SQL des bases de données
    wms_20260327_143022.sql
    ...
  exports/                       # Exports CSV des tables
    shipments_20260327_143215.csv
    ...
  reports/                       # Rapports d'audit
    audit_20260327_144500.json
    ...
```

> Le répertoire `output/` est créé automatiquement au premier lancement si nécessaire.

---

## 12. Résolution de problèmes

### Problèmes fréquents

| Symptôme                                         | Cause probable                              | Solution                                                    |
|--------------------------------------------------|---------------------------------------------|-------------------------------------------------------------|
| `python: command not found`                      | Python non installé ou absent du PATH       | Installer Python 3.10+ et vérifier le PATH                  |
| Erreur au lancement : config manquant            | `config.yaml` absent                        | Copier `config.example.yaml` vers `config.yaml`             |
| Erreur : variables non résolues (`${...}`)       | Fichier `.env` absent ou incomplet          | Copier `.env.example` vers `.env` et remplir les valeurs    |
| `MySQL connection refused`                       | Serveur MySQL éteint ou IP incorrecte       | Vérifier que WMS-DB est démarré et que l'IP est correcte    |
| `Access denied` sur MySQL                        | Mauvais identifiants                        | Vérifier `NTL_MYSQL_USER` et `NTL_MYSQL_PASSWORD` dans `.env` |
| `nmap: command not found`                        | nmap non installé                           | Installer nmap (`apt install nmap` ou téléchargement Windows) |
| `mysqldump: command not found`                   | mysql-client non installé                   | Installer mysql-client (`apt install mysql-client`)          |
| `Permission denied`                              | Droits insuffisants                         | Exécuter avec les privilèges adaptés (sudo sous Linux)       |
| `Module Xxx non disponible`                      | Dépendance Python manquante                 | Relancer `make setup` ou `pip install -r requirements.txt`   |
| Timeout sur une opération                        | Cible lente ou injoignable                  | Augmenter `general.timeout` dans `config.yaml`               |

### Activer le mode debug

Pour obtenir des logs détaillés, modifier le niveau de log :

**Option 1 -- Via le fichier `.env` :**

```ini
NTL_GENERAL_LOG_LEVEL=DEBUG
```

**Option 2 -- Via `config.yaml` :**

```yaml
general:
  log_level: DEBUG
```

Les logs détaillés permettent d'identifier la source exacte d'une erreur.

---

## 13. Commandes de développement

Ces commandes sont destinées aux contributeurs du projet.

| Commande            | Description                                        |
|---------------------|----------------------------------------------------|
| `make setup`        | Créer le venv et installer les dépendances (Windows)|
| `make setup-linux`  | Créer le venv et installer les dépendances (Linux)  |
| `make setup-dev`    | Installer les outils de développement               |
| `make run`          | Lancer le CLI                                        |
| `make test`         | Lancer les tests unitaires avec couverture           |
| `make lint`         | Vérifier le code avec ruff                           |
| `make typecheck`    | Vérifier les types avec mypy                         |
| `make clean`        | Supprimer les fichiers générés et le cache           |
| `make help`         | Afficher la liste des commandes disponibles          |

---

## 14. Annexes

### A. Dépendances Python

Le projet utilise les bibliothèques suivantes (installées automatiquement via `make setup`) :

| Bibliothèque             | Usage                                      |
|--------------------------|--------------------------------------------|
| `rich`                   | Affichage amélioré du CLI (tableaux, couleurs) |
| `mysql-connector-python` | Connexion MySQL pour le module Backup      |
| `paramiko`               | Connexion SSH pour les vérifications Linux |
| `dnspython`              | Résolution DNS pour le module Diagnostic   |
| `python-nmap`            | Interface Python pour nmap (module Audit)  |
| `pyyaml`                 | Lecture du fichier de configuration YAML   |
| `psutil`                 | Informations système                       |
| `ldap3`                  | Vérification LDAP/Active Directory         |
| `python-dotenv`          | Chargement des variables `.env`            |

### B. Schéma de navigation du CLI

```
Menu principal
  |
  |-- [1] Diagnostic
  |     |-- [1] Vérifier AD/DNS (DC01)
  |     |-- [2] Vérifier MySQL (port + version)
  |     |-- [3] Vérifier services Linux (multi-ports)
  |     |-- [4] Vérifier HTTP/HTTPS
  |     |-- [0] Retour
  |
  |-- [2] Backup
  |     |-- [1] Backup base de données (dump SQL)
  |     |-- [2] Export table en CSV
  |     |-- [0] Retour
  |
  |-- [3] Audit
  |     |-- [1] Scanner le réseau
  |     |-- [2] Lister les dates EOL
  |     |-- [3] Auditer depuis un CSV
  |     |-- [4] Générer le rapport complet
  |     |-- [0] Retour
  |
  |-- [0] Quitter
```

### C. Fichiers de configuration de référence

- `config/config.example.yaml` -- Modèle de configuration
- `.env.example` -- Modèle de variables d'environnement
- `data/eol_database.json` -- Base de données des dates de fin de vie
- `data/sample_inventory.csv` -- Exemple d'inventaire pour l'audit CSV
