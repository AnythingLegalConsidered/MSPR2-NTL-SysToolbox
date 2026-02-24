# Plan Projet MSPR — NTL-SysToolbox

## Contexte

**Sujet :** CLI interactif pour NordTransit Logistics — diagnostics, backup WMS, audit obsolescence.
**Equipe :** 4 personnes | **Duree :** 19h | **Soutenance :** 20 min + 30 min questions
**Contraintes :** Cross-platform (Win + Linux), sorties JSON horodatees, codes retour, menu interactif.

> **Guide operationnel :** Voir `_specs/WORKFLOW.md` pour le deroulement etape par etape.
> **Decisions :** Voir `_specs/DECISIONS.md` pour les choix techniques a valider en equipe.
> **Aide-memoire dev :** Voir `_specs/QUICKREF.md` pour les commandes et conventions.

---

## 1. Lab — VMs a monter

> **2 VMs suffisent** pour couvrir les 3 modules. Pas besoin de reproduire toute l'infra NTL.

### Schema reseau du lab

```
┌─────────────────────────────────────────────────┐
│               Reseau lab : 192.168.10.0/24      │
│                                                  │
│  ┌──────────────┐     ┌──────────────────────┐  │
│  │    DC01       │     │      WMS-DB           │  │
│  │ Win Server 22 │     │  Ubuntu 20.04        │  │
│  │ .10.10        │     │  .10.21              │  │
│  │               │     │                      │  │
│  │ Roles :       │     │ Roles :              │  │
│  │ - AD/DS       │     │ - MySQL Server       │  │
│  │ - DNS         │     │ - Base "wms" + data  │  │
│  │ - (optionnel  │     │ - SSH actif          │  │
│  │   DHCP)       │     │                      │  │
│  └──────────────┘     └──────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │         VOTRE PC (client)                 │   │
│  │  Windows ou Linux — execute l'outil       │   │
│  │  Python 3.10+ / nmap installe             │   │
│  │  .10.100 (ou DHCP)                        │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### Detail des VMs

| VM | OS | IP | RAM | Disque | A installer | Teste quoi |
|----|----|----|-----|--------|-------------|-----------|
| **DC01** | Windows Server 2022 | 192.168.10.10 | 4 Go | 40 Go | Role AD DS + DNS, creer domaine `ntl.local` | Module 1 : `check_ad_dns()`, `check_windows_server()` |
| **WMS-DB** | Ubuntu 20.04 LTS | 192.168.10.21 | 2 Go | 20 Go | MySQL Server, base `wms` avec tables de demo, SSH | Module 1 : `check_mysql()`, `check_ubuntu()` + **Module 2 entier** |

### Preparation de la base MySQL de demo

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

-- Quelques donnees pour que les exports aient du contenu
INSERT INTO shipments (tracking_number, origin, destination, status) VALUES
('NTL-2026-001', 'WH1-Lens', 'Client-Paris', 'delivered'),
('NTL-2026-002', 'WH2-Valenciennes', 'Client-Lyon', 'in_transit'),
('NTL-2026-003', 'WH3-Arras', 'Client-Marseille', 'pending');

INSERT INTO inventory (product_code, warehouse, quantity) VALUES
('SKU-A100', 'WH1', 250),
('SKU-B200', 'WH2', 180),
('SKU-C300', 'WH3', 420);
```

### Module 3 — pas besoin de VM supplementaire

Le scan nmap se fait sur le reseau lab (192.168.10.0/24) et detectera DC01 + WMS-DB + votre PC. Pour le rapport EOL, on utilise un fichier CSV pre-rempli avec l'inventaire fictif NTL complet (toutes les annexes du sujet).

---

## 2. Repartition des roles — fiche par personne

### Vue globale

```
            Phase 1 (3h)      Phase 2 (10h)       Phase 3 (3h)     Phase 4 (2h)    Phase 5 (1h)
            SETUP             DEV PARALLELE        INTEGRATION      DOCS            SOUTENANCE
            ─────────         ────────────         ───────────      ────            ──────────
Personne A  Squelette CLI     Menu + config        Assembler les    Nettoyage Git   Slides
(Lead)      Structure repo    Loader YAML          3 modules        README final    Repet
            Format JSON       Template module

Personne B  Aide setup        check_ad_dns()       Tester Module 1  Doc Module 1    Slides
(Diag)      Monter DC01       check_mysql()        sur lab                          Repet
                              check_win_server()
                              check_ubuntu()
                              Synthese JSON

Personne C  Aide setup        backup_database()    Tester Module 2  Doc Module 2    Slides
(Backup)    Monter WMS-DB     export_table_csv()   sur lab                          Repet
            + base demo       Integrite SHA256
                              Gestion erreurs

Personne D  Aide setup        scan_network()       Tester Module 3  Doc technique   Slides
(Audit)     Preparer CSV      list_os_eol()        sur lab          Manuel install  Repet
            inventaire        audit_from_csv()                      Rapport audit
                              generate_report()
```

### Fiche Personne A — Lead Dev / Architecte

**Tu fais :** le squelette dans lequel les autres branchent leur module.
**Fichiers :** `main.py`, `config_loader.py`, `utils/output.py`, `utils/network.py`
**Phase 1 (3h) :**
- Creer le repo Git + `.gitignore` + `README.md`
- Coder le menu CLI interactif (choix module → choix fonction → saisie arguments)
- Coder le loader de config YAML + surcharge par variables d'env
- Definir le format de sortie JSON commun (voir section 4)
- Creer un template de module vide que les autres copient

**Phase 2 (10h) :** Aider les devs si bloques, preparer l'integration
**Phase 3 (3h) :** Assembler les 3 modules dans le menu, corriger les incoherences

### Fiche Personne B — Dev Diagnostic (Module 1)

**Tu fais :** les 4 fonctions de check + la synthese.
**Fichier :** `modules/diagnostic.py`
**Cibles dans le lab :** DC01 (192.168.10.10), WMS-DB (192.168.10.21)

| Fonction | Ce qu'elle fait | Comment |
|----------|----------------|---------|
| `check_ad_dns()` | Verifie AD/DNS sur DC01 | `socket.connect()` port 389 (LDAP) + `nslookup` via `dns.resolver` |
| `check_mysql()` | Teste la connexion MySQL | `mysql.connector.connect()` → `SHOW DATABASES` + `SHOW STATUS` |
| `check_windows_server()` | Metriques Windows | `wmic` via subprocess OU `psutil` si local |
| `check_ubuntu()` | Metriques Ubuntu | SSH (`paramiko`) → `lsb_release -a`, `uptime`, `free -m`, `df -h` |

Chaque fonction retourne un dict avec `status` (OK/WARNING/CRITICAL), `details`, `timestamp`.

### Fiche Personne C — Dev Backup (Module 2)

**Tu fais :** backup et export de la base WMS.
**Fichier :** `modules/backup.py`
**Cible dans le lab :** WMS-DB (192.168.10.21), base `wms`

| Fonction | Ce qu'elle fait | Comment |
|----------|----------------|---------|
| `backup_database()` | Dump SQL complet | `mysqldump` via subprocess, fichier `wms_YYYYMMDD_HHMMSS.sql` |
| `export_table_csv()` | Export 1 table en CSV | `SELECT * FROM table` → ecriture CSV avec `csv` module Python |

Apres chaque operation : hash SHA256 du fichier, verification taille > 0, log JSON.

### Fiche Personne D — Dev Audit + Docs (Module 3)

**Tu fais :** scan reseau, croisement EOL, rapport + toute la doc du projet.
**Fichier :** `modules/audit.py`

| Fonction | Ce qu'elle fait | Comment |
|----------|----------------|---------|
| `scan_network()` | Liste les machines sur une plage | `python-nmap` : `nmap -sV -O <plage>` |
| `list_os_eol()` | Donne les dates EOL d'un OS | Lecture de `data/eol_database.json` |
| `audit_from_csv()` | Croise un CSV inventaire avec la base EOL | Lecture CSV → match dans le JSON EOL |
| `generate_report()` | Rapport final | Tri par statut : EXPIRE > BIENTOT > OK |

**Docs a rediger (Phase 4) :**
- Document technique et fonctionnel
- Manuel d'installation et d'utilisation
- Rapport d'execution de l'audit (sortie du module)

---

## 3. Stack technique

| Composant | Choix | Pourquoi |
|-----------|-------|----------|
| **Langage** | Python 3.10+ | Cross-platform, riche en libs, tout le monde connait |
| **CLI** | `rich` (tableaux, couleurs) + `input()` pour le menu | Rendu pro sans complexite |
| **MySQL** | `mysql-connector-python` | Connecteur officiel, zero galere |
| **SSH** | `paramiko` | Standard pour executer des commandes a distance sur Linux |
| **DNS** | `dnspython` | Requetes DNS programmatiques |
| **Scan reseau** | `python-nmap` | Wrapper Python autour de nmap |
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

**CRITIQUE : Definir ca au jour 1.** C'est ce qui permet a chacun de dev son module independamment.

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
  "message": "AD/DNS services operationnels sur DC01"
}
```

### Codes retour (exit codes)

| Code | Signification | Quand |
|------|--------------|-------|
| `0` | OK | Tout fonctionne |
| `1` | WARNING | Degradation (ex: CPU > 80%, disque > 85%) |
| `2` | CRITICAL | Service down, backup echoue, erreur fatale |
| `3` | UNKNOWN | Impossible de joindre la cible, timeout |

### Fichier de log

Chaque execution ecrit dans `output/logs/YYYYMMDD_HHMMSS_<module>.json`.
Chaque backup ecrit dans `output/backups/`.
Chaque rapport audit ecrit dans `output/reports/`.

---

## 5. Structure du repo

```
NTL-SysToolbox/
├── README.md                    # Description + quick start
├── requirements.txt             # Dependances Python
├── config/
│   └── config.example.yaml      # Template SANS secrets
├── src/
│   ├── main.py                  # Point d'entree + menu interactif
│   ├── config_loader.py         # Charge YAML + surcharge env vars
│   ├── utils/
│   │   ├── output.py            # Formater JSON, ecrire logs, codes retour
│   │   └── network.py           # Helpers communs (ping, port check...)
│   └── modules/
│       ├── diagnostic.py        # Personne B
│       ├── backup.py            # Personne C
│       └── audit.py             # Personne D
├── data/
│   ├── eol_database.json        # Base de dates EOL connues
│   └── sample_inventory.csv     # Inventaire NTL pour audit
├── output/                      # .gitignore — artefacts generes
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

## 6. Planning detaille (19h)

```
JOUR 1 ──────────────────────────────────────────────
│ [3h] Phase 1 — SETUP (tous ensemble)
│  ├── Monter DC01 + WMS-DB (Personne B + C)
│  ├── Creer repo Git + structure (Lead)
│  ├── Definir ensemble : format JSON, exit codes, config YAML
│  └── Lead code le menu CLI + config_loader + utils/output.py
│
│ [~7h] Phase 2 — DEV PARALLELE (chacun sur sa branche)
│  ├── Personne B → feature/module-diagnostic
│  ├── Personne C → feature/module-backup
│  ├── Personne D → feature/module-audit
│  └── Lead → feature/cli-menu (finalise + aide les autres)
│
JOUR 2 ──────────────────────────────────────────────
│ [~3h] Phase 2 — FIN DEV
│
│ [3h] Phase 3 — INTEGRATION + TESTS
│  ├── Merge des branches → main
│  ├── Tests E2E sur le lab (les 3 modules bout en bout)
│  └── Fix bugs, ajuster sorties
│
│ [2h] Phase 4 — DOCUMENTATION
│  ├── Document technique et fonctionnel (tous contribuent)
│  ├── Manuel d'installation (Personne D)
│  └── Execution audit + rapport (Personne D)
│
│ [1h] Phase 5 — SOUTENANCE
│  ├── Slides (tous)
│  └── Repetition 20 min + anticiper questions
```

---

## 7. Gestion Git

- `main` : code stable uniquement, tague (`v1.0`)
- Branches : `feature/module-diagnostic`, `feature/module-backup`, `feature/module-audit`, `feature/cli-menu`
- Commits conventionnels : `feat:`, `fix:`, `docs:`, `test:`, `chore:`
- Merge via PR avec relecture par 1 autre personne minimum
- Tag `v1.0` avant soutenance

---

## 8. Plan de la soutenance (20 min)

| Temps | Contenu | Qui |
|-------|---------|-----|
| 0-3 min | Contexte NTL, problematique, perimetre de l'outil | 1 personne |
| 3-7 min | Architecture technique : stack, structure, config, format JSON | Lead |
| 7-11 min | **Demo live** Module 1 (diagnostic DC01 + WMS-DB) puis Module 2 (backup) | Personne B + C |
| 11-15 min | **Demo live** Module 3 (scan + rapport EOL) | Personne D |
| 15-18 min | Difficultes, compromis, solutions | Tous |
| 18-20 min | Perspectives + conclusion | 1 personne |

---

## 9. Risques et mitigations

| Risque | Mitigation |
|--------|------------|
| Pas d'infra pour tester | 2 VMs suffisent (voir section 1) |
| nmap necessite privileges admin | Documenter, prevoir mode degrade sans -O |
| Manque de temps | Priorite : Module 1 > Module 2 > Module 3 |
| Incompatibilite Win/Linux | Tester sur les 2, utiliser `platform.system()` pour les commandes OS-specifiques |
| Merge conflicts Git | Chacun travaille dans son fichier module — conflits quasi impossibles |

---

## 10. Checklist livrables (a cocher avant soutenance)

- [ ] Repo Git propre avec historique lisible et branches
- [ ] Tag `v1.0` sur la version finale
- [ ] `config.example.yaml` present (sans secrets)
- [ ] Les 3 modules fonctionnent via le menu interactif
- [ ] Sorties JSON horodatees dans `output/`
- [ ] Codes retour 0/1/2/3 fonctionnels
- [ ] Document technique et fonctionnel
- [ ] Manuel d'installation et d'utilisation
- [ ] Rapport d'execution de l'audit d'obsolescence
- [ ] Support de presentation (slides)
- [ ] Resume en anglais dans le dossier
- [ ] Demo preparee et testee

---

## 11. Bonnes pratiques et conseils

### Organisation d'equipe
- **Jour 1, premiere heure :** tout le monde ensemble pour definir le contrat JSON + codes retour. C'est le ciment du projet.
- **Kanban simple** (Trello, GitHub Projects, ou meme un tableau papier) : TODO / EN COURS / FAIT par personne.
- **Daily standup** de 5 min entre chaque session de travail : "j'ai fait quoi, je fais quoi, je suis bloque ou".
- **Ne pas attendre le merge final** pour tester : chacun teste son module en standalone d'abord.

### Code
- **Un module = un fichier = une personne.** Pas de travail croise dans le meme fichier.
- **Toutes les fonctions retournent un dict au format commun** (section 4). Pas d'exception.
- **Gestion des erreurs :** chaque fonction catch ses exceptions et retourne `exit_code: 3` + message. Jamais de crash non gere.
- **Pas de hardcode d'IP ou de credentials.** Tout vient du fichier config.
- `output/` dans le `.gitignore` — ne jamais commit des dumps ou logs.

### Pour impressionner le jury
- **La demo live est decisive.** Preparez un script de demo (un .md avec les etapes exactes a suivre).
- **Montrer les sorties JSON structurees** : c'est ce qui prouve l'exploitabilite en supervision.
- **Documenter les compromis honnetement** : "on a choisi mysqldump plutot qu'une replication car le temps etait limite, en production on recommanderait X" — ca montre de la maturite.
- **Montrer le cross-platform** : lancer l'outil sur Windows ET Linux pendant la demo si possible.
- **Le rapport d'audit est un livrable visible** : faites-le propre, avec des couleurs (rich), un tri par criticite. C'est ce que le DSI regarde.

### Erreurs classiques a eviter
- Ne PAS commencer a coder avant d'avoir defini le format JSON commun
- Ne PAS travailler tous sur `main` directement (branches !)
- Ne PAS oublier le resume en anglais (exige dans le sujet)
- Ne PAS negliger la doc — elle compte autant que le code pour l'evaluation
- Ne PAS faire une demo qui plante — avoir un backup (screenshots, video) au cas ou
