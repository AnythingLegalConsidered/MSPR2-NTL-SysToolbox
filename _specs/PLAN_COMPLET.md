# Plan Projet MSPR — NTL-SysToolbox

## Contexte

**Sujet :** CLI interactif pour NordTransit Logistics — diagnostics, backup WMS, audit obsolescence.
**Équipe :** 4 personnes | **Durée :** 19h | **Soutenance :** 20 min + 30 min questions
**Contraintes :** Cross-platform (Win + Linux), sorties JSON horodatées, codes retour, menu interactif.

> **Pour coder ton module** → [GUIDE.md](GUIDE.md)
> **Etapes du projet :** [ETAPES.md](ETAPES.md) | **Decisions prises :** [DECISIONS_PRISES.md](DECISIONS_PRISES.md) | **Aide-memoire :** [AIDE_MEMOIRE.md](AIDE_MEMOIRE.md)

---

## 1. Lab — VMs à monter

> **2 VMs suffisent** pour couvrir les 3 modules. Pas besoin de reproduire toute l'infra NTL.

### Schéma réseau du lab

```
┌─────────────────────────────────────────────────┐
│               Réseau lab : 192.168.10.0/24      │
│                                                  │
│  ┌──────────────┐     ┌──────────────────────┐  │
│  │    DC01       │     │      WMS-DB           │  │
│  │ Win Server 22 │     │  Ubuntu 20.04        │  │
│  │ .10.10        │     │  .10.21              │  │
│  │               │     │                      │  │
│  │ Rôles :       │     │ Rôles :              │  │
│  │ - AD/DS       │     │ - MySQL Server       │  │
│  │ - DNS         │     │ - Base "wms" + data  │  │
│  │ - (optionnel  │     │ - SSH actif          │  │
│  │   DHCP)       │     │                      │  │
│  └──────────────┘     └──────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │         VOTRE PC (client)                 │   │
│  │  Windows ou Linux — exécute l'outil       │   │
│  │  Python 3.10+ / nmap installé             │   │
│  │  .10.100 (ou DHCP)                        │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### Détail des VMs

| VM | OS | IP | RAM | Disque | À installer | Testé quoi |
|----|----|----|-----|--------|-------------|-----------|
| **DC01** | Windows Server 2022 | 192.168.10.10 | 4 Go | 40 Go | Rôle AD DS + DNS, créer domaine `ntl.local` | Module 1 : `check_ad_dns()`, `check_windows_server()` |
| **WMS-DB** | Ubuntu 20.04 LTS | 192.168.10.21 | 2 Go | 20 Go | MySQL Server, base `wms` avec tables de démo, SSH | Module 1 : `check_mysql()`, `check_ubuntu()` + **Module 2 entier** |

### Préparation de la base MySQL de démo

```sql
CREATE DATABASE wms;
USE wms;

CREATE TABLE shipments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tracking_number VARCHAR(50),
    origin VARCHAR(100),
    destination VARCHAR(100),
    status ENUM('pending', 'in_transit', 'delivered'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_code VARCHAR(30),
    warehouse VARCHAR(10),
    quantity INT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quelques données pour que les exports aient du contenu
INSERT INTO shipments (tracking_number, origin, destination, status) VALUES
('NTL-2026-001', 'WH1-Lens', 'Client-Paris', 'delivered'),
('NTL-2026-002', 'WH2-Valenciennes', 'Client-Lyon', 'in_transit'),
('NTL-2026-003', 'WH3-Arras', 'Client-Marseille', 'pending');

INSERT INTO inventory (product_code, warehouse, quantity) VALUES
('SKU-A100', 'WH1', 250),
('SKU-B200', 'WH2', 180),
('SKU-C300', 'WH3', 420);
```

### Module 3 — pas besoin de VM supplémentaire

Le scan nmap se fait sur le réseau lab (192.168.10.0/24) et détectera DC01 + WMS-DB + votre PC. Pour le rapport EOL, on utilise un fichier CSV pré-rempli avec l'inventaire fictif NTL complet (toutes les annexes du sujet).

---

## 2. Répartition des rôles — fiche par personne

### Vue globale

```
            Phase 1 (3h)      Phase 2 (10h)       Phase 3 (3h)     Phase 4 (2h)    Phase 5 (1h)
            SETUP             DEV PARALLÈLE        INTÉGRATION      DOCS            SOUTENANCE
            ─────────         ────────────         ───────────      ────            ──────────
Ianis       Squelette CLI     Menu + config        Assembler les    Nettoyage Git   Slides
(Lead)      Structure repo    Loader YAML          3 modules        README final    Répét
            Format JSON       Template module

Blaise      Aide setup        check_ad_dns()       Tester Module 1  Doc Module 1    Slides
(Diag)      Monter DC01       check_mysql()        sur lab                          Répét
                              check_win_server()
                              check_ubuntu()
                              Synthèse JSON

Ojvind      Aide setup        backup_database()    Tester Module 2  Doc Module 2    Slides
(Backup)    Monter WMS-DB     export_table_csv()   sur lab                          Répét
            + base démo       Intégrité SHA256
                              Gestion erreurs

Zaid        Aide setup        scan_network()       Tester Module 3  Doc technique   Slides
(Audit)     Préparer CSV      list_os_eol()        sur lab          Manuel install  Répét
            inventaire        audit_from_csv()                      Rapport audit
                              generate_report()
```

### Fiche Ianis PUICHAUD — Lead Dev / Architecte

**Tu fais :** le squelette dans lequel les autres branchent leur module.
**Fichiers :** `main.py`, `config_loader.py`, `utils/output.py`, `utils/network.py`
**Phase 1 (3h) :**
- Créer le repo Git + `.gitignore` + `README.md`
- Coder le menu CLI interactif (choix module → choix fonction → saisie arguments)
- Coder le loader de config YAML + surcharge par variables d'env
- Définir le format de sortie JSON commun (voir section 4)
- Créer un template de module vide que les autres copient

**Phase 2 (10h) :** Aider les devs si bloqués, préparer l'intégration
**Phase 3 (3h) :** Assembler les 3 modules dans le menu, corriger les incohérences

### Fiche Blaise WANDA NKONG — Dev Diagnostic (Module 1)

**Tu fais :** les 4 fonctions de check + la synthèse.
**Fichier :** `modules/diagnostic.py`
**Cibles dans le lab :** DC01 (192.168.10.10), WMS-DB (192.168.10.21)

| Fonction | Ce qu'elle fait | Comment |
|----------|----------------|---------|
| `check_ad_dns()` | Vérifie AD/DNS sur DC01 | `socket.connect()` port 389 (LDAP) + `nslookup` via `dns.resolver` |
| `check_mysql()` | Teste la connexion MySQL | `mysql.connector.connect()` → `SHOW DATABASES` + `SHOW STATUS` |
| `check_windows_server()` | Métriques Windows | `wmic` via subprocess OU `psutil` si local |
| `check_ubuntu()` | Métriques Ubuntu | SSH (`paramiko`) → `lsb_release -a`, `uptime`, `free -m`, `df -h` |

Chaque fonction retourne un dict avec `status` (OK/WARNING/CRITICAL), `details`, `timestamp`.

### Fiche Ojvind LANTSIGBLE — Dev Backup (Module 2)

**Tu fais :** backup et export de la base WMS.
**Fichier :** `modules/backup.py`
**Cible dans le lab :** WMS-DB (192.168.10.21), base `wms`

| Fonction | Ce qu'elle fait | Comment |
|----------|----------------|---------|
| `backup_database()` | Dump SQL complet | `mysqldump` via subprocess, fichier `wms_YYYYMMDD_HHMMSS.sql` |
| `export_table_csv()` | Export 1 table en CSV | `SELECT * FROM table` → écriture CSV avec `csv` module Python |

Après chaque opération : hash SHA256 du fichier, vérification taille > 0, log JSON.

### Fiche Zaid ABOUYAALA — Dev Audit + Docs (Module 3)

**Tu fais :** scan réseau, croisement EOL, rapport + toute la doc du projet.
**Fichier :** `modules/audit.py`

| Fonction | Ce qu'elle fait | Comment |
|----------|----------------|---------|
| `scan_network()` | Liste les machines sur une plage | `python-nmap` : `nmap -sV -O <plage>` |
| `list_os_eol()` | Donne les dates EOL d'un OS | Lecture de `data/eol_database.json` |
| `audit_from_csv()` | Croise un CSV inventaire avec la base EOL | Lecture CSV → match dans le JSON EOL |
| `generate_report()` | Rapport final | Tri par statut : EXPIRÉ > BIENTÔT > OK |

**Docs à rédiger (Phase 4) :**
- Document technique et fonctionnel
- Manuel d'installation et d'utilisation
- Rapport d'exécution de l'audit (sortie du module)

---

## 3. Stack technique

| Composant | Choix | Pourquoi |
|-----------|-------|----------|
| **Langage** | Python 3.10+ | Cross-platform, riche en libs, tout le monde connaît |
| **CLI** | `rich` (tableaux, couleurs) + `input()` pour le menu | Rendu pro sans complexité |
| **MySQL** | `mysql-connector-python` | Connecteur officiel, zéro galère |
| **SSH** | `paramiko` | Standard pour exécuter des commandes à distance sur Linux |
| **DNS** | `dnspython` | Requêtes DNS programmatiques |
| **Scan réseau** | `python-nmap` | Wrapper Python autour de nmap |
| **Config** | `pyyaml` | YAML lisible + surcharge par `os.environ` |
| **Tests** | `pytest` | Simple et efficace |

```
# requirements.txt
rich>=13.0
mysql-connector-python>=8.0
paramiko>=3.0
dnspython>=2.4
python-nmap>=0.7
pyyaml>=6.0
pytest>=7.0
psutil>=5.9
```

---

## 4. Contrat entre modules — format de sortie commun

**CRITIQUE : Définir ça au jour 1.** C'est ce qui permet à chacun de dev son module indépendamment.

### Structure JSON de retour (chaque fonction)

```json
{
  "module": "diagnostic",
  "function": "check_ad_dns",
  "timestamp": "2026-02-24T14:30:00Z",
  "status": "OK",
  "exit_code": 0,
  "target": "192.168.10.10",
  "details": {
    "ldap_port_389": true,
    "dns_resolution": true,
    "response_time_ms": 12
  },
  "message": "AD/DNS services opérationnels sur DC01"
}
```

### Codes retour (exit codes)

| Code | Signification | Quand |
|------|--------------|-------|
| `0` | OK | Tout fonctionne |
| `1` | WARNING | Dégradation (ex: CPU > 80%, disque > 85%) |
| `2` | CRITICAL | Service down, backup échoué, erreur fatale |
| `3` | UNKNOWN | Impossible de joindre la cible, timeout |

### Fichier de log

Chaque exécution écrit dans `output/logs/YYYYMMDD_HHMMSS_<module>.json`.
Chaque backup écrit dans `output/backups/`.
Chaque rapport audit écrit dans `output/reports/`.

---

## 5. Structure du repo

```
NTL-SysToolbox/
├── README.md                    # Description + quick start
├── requirements.txt             # Dépendances Python
├── config/
│   └── config.example.yaml      # Template SANS secrets
├── src/
│   ├── main.py                  # Point d'entrée + menu interactif
│   ├── config_loader.py         # Charge YAML + surcharge env vars
│   ├── utils/
│   │   ├── output.py            # Formater JSON, écrire logs, codes retour
│   │   └── network.py           # Helpers communs (ping, port check...)
│   └── modules/
│       ├── diagnostic.py        # Blaise
│       ├── backup.py            # Ojvind
│       └── audit.py             # Zaid
├── data/
│   ├── eol_database.json        # Base de dates EOL connues
│   └── sample_inventory.csv     # Inventaire NTL pour audit
├── output/                      # .gitignore — artefacts générés
│   ├── logs/
│   ├── backups/
│   └── reports/
├── docs/
│   ├── document_technique.md
│   ├── manuel_utilisation.md
│   └── rapport_audit.md
└── tests/
    ├── test_diagnostic.py
    ├── test_backup.py
    └── test_audit.py
```

---

## 6. Planning détaillé (19h)

```
JOUR 1 ──────────────────────────────────────────────
│ [3h] Phase 1 — SETUP (tous ensemble)
│  ├── Monter DC01 + WMS-DB (Blaise + Ojvind)
│  ├── Créer repo Git + structure (Lead)
│  ├── Définir ensemble : format JSON, exit codes, config YAML
│  └── Lead code le menu CLI + config_loader + utils/output.py
│
│ [~7h] Phase 2 — DEV PARALLÈLE (chacun sur sa branche)
│  ├── Blaise → feature/module-diagnostic
│  ├── Ojvind → feature/module-backup
│  ├── Zaid → feature/module-audit
│  └── Lead → feature/cli-menu (finalise + aide les autres)
│
JOUR 2 ──────────────────────────────────────────────
│ [~3h] Phase 2 — FIN DEV
│
│ [3h] Phase 3 — INTÉGRATION + TESTS
│  ├── Merge des branches → main
│  ├── Tests E2E sur le lab (les 3 modules bout en bout)
│  └── Fix bugs, ajuster sorties
│
│ [2h] Phase 4 — DOCUMENTATION
│  ├── Document technique et fonctionnel (tous contribuent)
│  ├── Manuel d'installation (Zaid)
│  └── Exécution audit + rapport (Zaid)
│
│ [1h] Phase 5 — SOUTENANCE
│  ├── Slides (tous)
│  └── Répétition 20 min + anticiper questions
```

---

## 7. Gestion Git

- `main` : code stable uniquement, tagué (`v1.0`)
- Branches : `feature/module-diagnostic`, `feature/module-backup`, `feature/module-audit`, `feature/cli-menu`
- Commits conventionnels : `feat:`, `fix:`, `docs:`, `test:`, `chore:`
- Merge via PR avec relecture par 1 autre personne minimum
- Tag `v1.0` avant soutenance

---

## 8. Plan de la soutenance (20 min)

| Temps | Contenu | Qui |
|-------|---------|-----|
| 0-3 min | Contexte NTL, problématique, périmètre de l'outil | 1 personne |
| 3-7 min | Architecture technique : stack, structure, config, format JSON | Lead |
| 7-11 min | **Démo live** Module 1 (diagnostic DC01 + WMS-DB) puis Module 2 (backup) | Blaise + Ojvind |
| 11-15 min | **Démo live** Module 3 (scan + rapport EOL) | Zaid |
| 15-18 min | Difficultés, compromis, solutions | Tous |
| 18-20 min | Perspectives + conclusion | 1 personne |

---

## 9. Risques et mitigations

| Risque | Mitigation |
|--------|------------|
| Pas d'infra pour tester | 2 VMs suffisent (voir section 1) |
| nmap nécessite privilèges admin | Documenter, prévoir mode dégradé sans -O |
| Manque de temps | Priorité : Module 1 > Module 2 > Module 3 |
| Incompatibilité Win/Linux | Tester sur les 2, utiliser `platform.system()` pour les commandes OS-spécifiques |
| Merge conflicts Git | Chacun travaille dans son fichier module — conflits quasi impossibles |

---

## 10. Checklist livrables (à cocher avant soutenance)

- [ ] Repo Git propre avec historique lisible et branches
- [ ] Tag `v1.0` sur la version finale
- [ ] `config.example.yaml` présent (sans secrets)
- [ ] Les 3 modules fonctionnent via le menu interactif
- [ ] Sorties JSON horodatées dans `output/`
- [ ] Codes retour 0/1/2/3 fonctionnels
- [ ] Document technique et fonctionnel
- [ ] Manuel d'installation et d'utilisation
- [ ] Rapport d'exécution de l'audit d'obsolescence
- [ ] Support de présentation (slides)
- [ ] Résumé en anglais dans le dossier
- [ ] Démo préparée et testée

---

## 11. Bonnes pratiques et conseils

### Organisation d'équipe
- **Jour 1, première heure :** tout le monde ensemble pour définir le contrat JSON + codes retour. C'est le ciment du projet.
- **Kanban simple** (Trello, GitHub Projects, ou même un tableau papier) : TODO / EN COURS / FAIT par personne.
- **Daily standup** de 5 min entre chaque session de travail : "j'ai fait quoi, je fais quoi, je suis bloqué où".
- **Ne pas attendre le merge final** pour tester : chacun teste son module en standalone d'abord.

### Code
- **Un module = un fichier = une personne.** Pas de travail croisé dans le même fichier.
- **Toutes les fonctions retournent un dict au format commun** (section 4). Pas d'exception.
- **Gestion des erreurs :** chaque fonction catch ses exceptions et retourne `exit_code: 3` + message. Jamais de crash non géré.
- **Pas de hardcode d'IP ou de credentials.** Tout vient du fichier config.
- `output/` dans le `.gitignore` — ne jamais commit des dumps ou logs.

### Pour impressionner le jury
- **La démo live est décisive.** Préparez un script de démo (un .md avec les étapes exactes à suivre).
- **Montrer les sorties JSON structurées** : c'est ce qui prouve l'exploitabilité en supervision.
- **Documenter les compromis honnêtement** : "on a choisi mysqldump plutôt qu'une réplication car le temps était limité, en production on recommanderait X" — ça montre de la maturité.
- **Montrer le cross-platform** : lancer l'outil sur Windows ET Linux pendant la démo si possible.
- **Le rapport d'audit est un livrable visible** : faites-le propre, avec des couleurs (rich), un tri par criticité. C'est ce que le DSI regarde.

### Erreurs classiques à éviter
- Ne PAS commencer à coder avant d'avoir défini le format JSON commun
- Ne PAS travailler tous sur `main` directement (branches !)
- Ne PAS oublier le résumé en anglais (exigé dans le sujet)
- Ne PAS négliger la doc — elle compte autant que le code pour l'évaluation
- Ne PAS faire une démo qui plante — avoir un backup (screenshots, vidéo) au cas où
