# Rapport de Soutenance — NTL-SysToolbox

## MSPR TPRE511 — Bloc E6.1 « Concevoir et tester des solutions applicatives »

**Projet :** NTL-SysToolbox — Outil CLI d'administration système
**Client :** NordTransit Logistics (NTL)
**Date :** Avril 2026
**Durée du projet :** 19 heures

| Rôle | Membre |
|------|--------|
| Lead / Architecte | Ianis PUICHAUD |
| Dev Diagnostic | Blaise WANDA NKONG |
| Dev Backup | Ojvind LANTSIGBLE |
| Dev Audit + Documentation | Zaid ABOUYAALA |

---

## Sommaire

1. [Introduction](#1-introduction)
2. [Contexte et problématique](#2-contexte-et-problématique)
3. [Analyse des besoins](#3-analyse-des-besoins)
4. [Solution technique](#4-solution-technique)
5. [Réalisation](#5-réalisation)
6. [Tests et validation](#6-tests-et-validation)
7. [Organisation d'équipe](#7-organisation-déquipe)
8. [Bilan](#8-bilan)
9. [Conclusion et perspectives](#9-conclusion-et-perspectives)
10. [Annexes](#annexes)

---

## 1. Introduction

Ce rapport présente le travail réalisé dans le cadre de la MSPR TPRE511, bloc E6.1 « Concevoir et tester des solutions applicatives ». Le projet consiste à développer un outil CLI (Command-Line Interface) d'administration système pour le compte de NordTransit Logistics, une PME de logistique implantée dans les Hauts-de-France.

L'outil, baptisé **NTL-SysToolbox**, industrialise trois opérations critiques : la vérification de l'état des services, la sauvegarde de la base de données métier, et l'audit d'obsolescence du parc informatique.

---

## 2. Contexte et problématique

### 2.1 Le client

NordTransit Logistics est une PME spécialisée dans le transport et la logistique, implantée dans les Hauts-de-France avec :
- Un **siège social** à Lille (direction, comptabilité, IT)
- Trois **entrepôts** à Lens (WH1), Valenciennes (WH2) et Arras (WH3)

L'entreprise utilise un système de gestion d'entrepôt (WMS — Warehouse Management System) hébergé sur une infrastructure on-premise.

### 2.2 Le parc informatique

Le parc NTL comprend **19 machines** :
- 2 contrôleurs de domaine (Windows Server 2022 et 2019)
- 4 serveurs applicatifs (MySQL, WMS, fichiers, impression)
- 3 serveurs d'infrastructure (supervision, sauvegarde, intranet)
- 1 IPBX (téléphonie)
- 1 NAS de sauvegarde
- 7 postes de travail (dont 3 sous Windows 7)

### 2.3 Problématiques identifiées

1. **Absence de vérification systématique** : Les services critiques (Active Directory, DNS, MySQL) ne sont pas surveillés de manière automatisée. Les pannes sont détectées tardivement, impactant la productivité.

2. **Sauvegardes manuelles** : La base WMS est sauvegardée de manière ad hoc, sans horodatage ni vérification d'intégrité. Le risque de perte de données est élevé.

3. **Obsolescence non qualifiée** : Plusieurs machines fonctionnent avec des OS en fin de vie (Windows 7, Windows Server 2008 R2, CentOS 7), exposant l'entreprise à des vulnérabilités de sécurité non corrigées.

---

## 3. Analyse des besoins

### 3.1 Besoins fonctionnels

| ID | Besoin | Priorité |
|----|--------|----------|
| BF1 | Vérifier la disponibilité des services critiques (AD, DNS, MySQL) | Haute |
| BF2 | Surveiller l'état de santé des serveurs (CPU, RAM, disques) | Haute |
| BF3 | Sauvegarder la base WMS au format SQL avec vérification SHA256 | Haute |
| BF4 | Exporter les tables WMS au format CSV | Moyenne |
| BF5 | Scanner le réseau et détecter les OS | Haute |
| BF6 | Qualifier l'obsolescence de chaque machine | Haute |
| BF7 | Générer un rapport d'audit trié par criticité | Haute |
| BF8 | Fournir un menu interactif pour l'opérateur | Moyenne |

### 3.2 Besoins non fonctionnels

| ID | Besoin | Justification |
|----|--------|---------------|
| BNF1 | Cross-platform (Windows + Linux) | L'opérateur peut exécuter l'outil depuis n'importe quel poste |
| BNF2 | Sorties JSON horodatées (ISO 8601 UTC) | Interopérabilité avec des outils de supervision |
| BNF3 | Codes retour standardisés (0-3) | Compatibilité Nagios/Zabbix |
| BNF4 | Pas de secrets en dur dans le code | Sécurité des credentials |
| BNF5 | Tests automatisés en CI/CD | Qualité et non-régression |

### 3.3 Contraintes

- **Durée** : 19 heures de travail effectif pour 4 personnes
- **Équipe** : 4 développeurs avec des niveaux d'expérience variés
- **Infrastructure** : Lab de développement sur Proxmox (hyperviseur personnel)

---

## 4. Solution technique

### 4.1 Choix technologiques

| Choix | Technologie | Justification |
|-------|-------------|---------------|
| Langage | Python 3.10+ | Cross-platform, écosystème riche, testabilité |
| CLI | Rich + input() | Affichage coloré, tableaux formatés, fallback texte |
| MySQL | mysql-connector-python | Connecteur officiel Oracle, pur Python |
| SSH | Paramiko | Client SSH natif Python, pas de dépendance système |
| DNS | dnspython | Résolution DNS programmatique |
| Scan réseau | python-nmap | Wrapper Python autour de nmap |
| Config | PyYAML + python-dotenv | Séparation config/secrets |
| Tests | Pytest + ruff + mypy | Triple vérification (fonctionnel, style, types) |
| CI/CD | GitHub Actions | Intégration native GitHub, gratuit |

### 4.2 Architecture logicielle

L'architecture suit le principe de **séparation des responsabilités** :

```
┌─────────────────────────────────────────────┐
│                  main.py                     │
│            Menu CLI interactif               │
├─────────────────────────────────────────────┤
│              config_loader.py                │
│         Chargement YAML + .env               │
├──────────┬──────────┬───────────────────────┤
│ Module   │ Module   │ Module                │
│ Diagno.  │ Backup   │ Audit                 │
├──────────┴──────────┴───────────────────────┤
│              interfaces.py                   │
│      build_result() + exit codes             │
├─────────────────────────────────────────────┤
│                 utils/                        │
│      output · network · validation           │
└─────────────────────────────────────────────┘
```

### 4.3 Contrat d'interface

Toutes les fonctions de module retournent un dictionnaire standardisé via `build_result()` :

```json
{
  "module": "diagnostic|backup|audit",
  "function": "nom_de_la_fonction",
  "timestamp": "2026-03-27T14:30:00Z",
  "status": "OK|WARNING|CRITICAL|UNKNOWN",
  "exit_code": 0,
  "target": "192.168.10.10",
  "details": { ... },
  "message": "Description lisible"
}
```

Ce format unique permet :
- L'exploitation par des outils de supervision (Nagios, Zabbix)
- Le stockage en logs JSON exploitables
- L'affichage cohérent dans le menu CLI

---

## 5. Réalisation

### 5.1 Module Diagnostic

**Développeur :** Blaise WANDA NKONG

| Fonction | Description | Cibles |
|----------|-------------|--------|
| `check_ad_dns` | Résolution DNS + port LDAP 389 + services Windows | DC01 |
| `check_mysql` | Port 3306 + version MySQL + connexion | WMS-DB |
| `check_linux` | Scan multi-ports sur serveurs Linux | Serveurs Linux |
| `check_http` | Test HTTP/HTTPS + code retour | Services web |

**Points techniques :**
- Utilisation de `dnspython` pour la résolution DNS programmatique
- Vérification LDAP via connexion socket sur le port 389
- Seuils configurables : CPU/RAM/Disque > 80% = WARNING

### 5.2 Module Backup

**Développeur :** Ojvind LANTSIGBLE

| Fonction | Description | Sortie |
|----------|-------------|--------|
| `backup_database()` | Dump complet de la base WMS via `mysqldump` | `wms_YYYYMMDD_HHMMSS.sql` |
| `export_table_csv()` | Export SELECT * d'une table en CSV | `table_YYYYMMDD.csv` |

**Points techniques :**
- Mot de passe MySQL passé via variable d'environnement (pas en argument CLI)
- Hash SHA256 calculé automatiquement après chaque dump
- Prévention d'injection SQL sur les noms de tables
- Validation des chemins de sortie (anti path traversal)

### 5.3 Module Audit

**Développeur :** Zaid ABOUYAALA

| Fonction | Description |
|----------|-------------|
| `scan_network()` | Scan nmap avec détection de services (-sV) |
| `list_os_eol()` | Lecture de la base EOL (20 OS référencés) |
| `audit_from_csv()` | Croisement inventaire CSV avec dates EOL |
| `generate_report()` | Rapport complet trié par criticité |

**Points techniques :**
- Validation des ranges réseau (anti injection nmap)
- Base EOL couvrant Windows Server, Windows Desktop, Ubuntu LTS, Debian, CentOS
- Tri par criticité : EXPIRED → EXPIRING_SOON → OK
- Rapport avec tableaux Rich colorés

### 5.4 Infrastructure de test

Le lab de développement est déployé sur **Proxmox VE** avec les VMs suivantes :

| VM | OS | IP | Rôle |
|----|----|----|------|
| DC01 | Windows Server 2022 | 192.168.10.10 | Contrôleur de domaine AD/DNS |
| WMS-DB | Ubuntu 20.04 LTS | 192.168.10.21 | Base MySQL du WMS |
| SRV-OLD | Windows Server 2012 R2 | 192.168.10.12 | Serveur legacy (tests EOL) |
| SRV-LEGACY | Ubuntu 18.04 | 192.168.10.18 | Serveur legacy (tests EOL) |
| CLIENT-01 | Windows 10 | 192.168.10.50 | Poste d'exécution |

L'infrastructure est entièrement automatisée via **7 playbooks Ansible** et des scripts de déploiement Proxmox.

---

## 6. Tests et validation

### 6.1 Tests unitaires

| Module | Fichier de test | Nombre de tests |
|--------|-----------------|-----------------|
| Interfaces | `test_interfaces.py` | 12 |
| Config | `test_config_loader.py` | 8 |
| Network utils | `test_network.py` | 6 |
| Output utils | `test_output.py` | 7 |
| Diagnostic | `test_diagnostic.py` | 19 |
| Backup | `test_backup.py` | 18 |
| Audit | `test_audit.py` | 15 |
| **Total** | **8 fichiers** | **52+** |

### 6.2 CI/CD

La pipeline GitHub Actions s'exécute à chaque push et PR :

1. **Lint** (Ruff) — Vérifie le style et détecte les erreurs statiques
2. **Type check** (Mypy) — Vérifie la cohérence des types
3. **Tests** (Pytest) — Exécute les tests sur Python 3.10, 3.11 et 3.12

Couverture minimum : 50%. Le rapport de couverture est archivé comme artifact GitHub.

### 6.3 Tests E2E sur le lab

Les tests de bout en bout sont réalisés sur le lab Proxmox :

- [ ] Menu CLI affiche les 3 modules
- [ ] Diagnostic DC01 → JSON OK avec statut AD/DNS
- [ ] Diagnostic WMS-DB → JSON OK avec statut MySQL
- [ ] Backup base WMS → fichier .sql + SHA256
- [ ] Export CSV → fichiers shipments.csv et inventory.csv
- [ ] Scan réseau → détecte les VMs du lab
- [ ] Audit EOL depuis CSV → rapport trié par criticité
- [ ] Logs écrits dans `output/logs/`
- [ ] Exit codes corrects

---

## 7. Organisation d'équipe

### 7.1 Méthodologie

Le projet a suivi une approche en **4 phases** :

| Phase | Durée | Activités |
|-------|-------|-----------|
| **1. Setup** | 3h | Mise en place du lab Proxmox, squelette Python, CI/CD |
| **2. Dev parallèle** | 10h | Chaque développeur sur sa branche feature |
| **3. Intégration** | 3h | Merge des branches, tests E2E, corrections |
| **4. Finalisation** | 3h | Documentation, présentation, release |

### 7.2 Workflow Git

- **Branches** : `feature/module-diagnostic`, `feature/module-backup`, `feature/module-audit`
- **Commits conventionnels** : `feat:`, `fix:`, `docs:`, `test:`, `chore:`
- **Pull Requests** avec CI obligatoire avant merge
- **Review** par le Lead avant intégration

### 7.3 Outils de collaboration

- **GitHub** : code source, issues (21 créées, suivi par labels), PRs, CI/CD
- **Discord** : communication temps réel
- **Proxmox** : infrastructure partagée de test

---

## 8. Bilan

### 8.1 Objectifs atteints

| Objectif | Statut | Commentaire |
|----------|--------|-------------|
| Module Diagnostic fonctionnel | ✅ | 4 checks implémentés avec seuils |
| Module Backup fonctionnel | ✅ | Dump SQL + CSV + SHA256 |
| Module Audit fonctionnel | ✅ | Scan + EOL + rapports |
| Cross-platform | ✅ | Testé Windows + Linux |
| Sorties JSON standardisées | ✅ | Contrat `build_result()` respecté |
| CI/CD automatisée | ✅ | 52+ tests, 3 versions Python |
| Documentation complète | ✅ | Technique, utilisation, audit |

### 8.2 Difficultés rencontrées

1. **Hétérogénéité Windows/Linux** : La gestion des connexions distantes diffère selon l'OS cible (WinRM pour Windows, SSH pour Linux). La couche d'abstraction dans `utils/network.py` a permis d'uniformiser.

2. **Timeouts réseau** : En environnement de lab, les VMs peuvent être lentes à démarrer. Des timeouts configurables et un statut UNKNOWN permettent de gérer ces situations sans crash.

3. **Planning serré** : 19 heures pour 4 personnes avec des niveaux d'expérience variés. La structuration en phases et le squelette fourni par le Lead ont permis un développement parallèle efficace.

4. **Coordination Git** : Les merges entre 4 branches actives ont généré quelques conflits, résolus lors de la phase d'intégration.

### 8.3 Acquis de compétences

| Compétence E6.1 | Comment elle a été mobilisée |
|------------------|------------------------------|
| Concevoir une solution applicative | Architecture modulaire, contrat d'interface, choix technologiques |
| Développer la solution | Implémentation des 3 modules en Python |
| Tester la solution | 52+ tests unitaires, CI/CD, tests E2E sur lab |
| Documenter la solution | Document technique, manuel, rapport d'audit |

---

## 9. Conclusion et perspectives

### Conclusion

NTL-SysToolbox répond aux trois problématiques identifiées chez NordTransit Logistics :
- La **vérification systématique** des services critiques est désormais automatisée
- Les **sauvegardes** de la base WMS sont horodatées, vérifiables et traçables
- L'**audit d'obsolescence** fournit un état des lieux actionnable du parc

L'outil est conçu pour être utilisable en production par un opérateur IT, avec des sorties compatibles avec les outils de supervision standards.

### Perspectives d'amélioration

| Priorité | Amélioration | Valeur ajoutée |
|----------|--------------|----------------|
| Haute | Mode CLI non-interactif (arguments) | Scheduling via cron/Task Scheduler |
| Haute | Notifications (email, Slack) | Alerting automatique sur résultats CRITICAL |
| Moyenne | Interface web pour les rapports | Accessibilité pour les non-techniciens |
| Moyenne | Intégration Zabbix/Grafana | Dashboards de supervision centralisés |
| Basse | Extension à d'autres services | DHCP, Exchange, certificats SSL |

---

## Annexes

### A. Dépôt GitHub

https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox

### B. Structure du projet

```
MSPR2-NTL-SysToolbox/
├── src/                    # Code source Python
├── tests/                  # Tests unitaires (pytest)
├── config/                 # Templates de configuration
├── data/                   # Données de référence (EOL, inventaire)
├── docs/                   # Documentation complète
├── infra/                  # Infrastructure (Ansible, Proxmox)
├── school/                 # Sujet MSPR et grille d'évaluation
├── .github/workflows/      # Pipeline CI/CD
├── Makefile                # Commandes de développement
├── requirements.txt        # Dépendances production
└── requirements-dev.txt    # Dépendances développement
```

### C. Références

- Python Documentation : https://docs.python.org/3/
- Rich Library : https://rich.readthedocs.io/
- Nmap : https://nmap.org/
- GitHub Actions : https://docs.github.com/en/actions
- Proxmox VE : https://www.proxmox.com/en/proxmox-ve
- Ansible : https://docs.ansible.com/

---

*Document rédigé dans le cadre de la MSPR TPRE511 — NTL-SysToolbox v1.0*
