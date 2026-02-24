# Decisions d'equipe — NTL-SysToolbox

> **Objectif :** Parcourir ce document ensemble en ~1h. Chaque question doit etre tranchee.
> Le scribe remplit la colonne "Decision". A la fin, chacun repart avec ses specs.
>
> **Date de la reunion :** _______________
> **Presents :** _______________

---

## Theme 1 — Organisation & Git

### 1.1 Repartition des roles

| Role | Responsabilite | Qui ? |
|------|----------------|-------|
| **Lead / Integrateur** | `main.py`, menu CLI, config_loader, utils, merge final | _______ |
| **Dev Diagnostic** | `modules/diagnostic.py` — checks AD, DNS, MySQL, serveurs | _______ |
| **Dev Backup** | `modules/backup.py` — dump MySQL, export CSV, SHA256 | _______ |
| **Dev Audit** | `modules/audit.py` — scan nmap, EOL, rapport | _______ |

> **Regle :** Le Lead est le seul a toucher `main.py` et `src/utils/`. Les devs ne modifient QUE leur module.

### 1.2 Workflow Git

| Question | Options | Decision |
|----------|---------|----------|
| Convention de branches ? | `feature/module-diagnostic`, `feature/module-backup`, `feature/module-audit`, `feature/cli-menu` | |
| Qui cree le repo + invite les autres ? | Lead | |
| Strategie de merge ? | A) Merge commit (historique lisible) — B) Squash (1 commit par branche) | |
| Qui review les PRs ? | A) Le Lead review tout — B) Chacun review 1 autre personne — C) Pas de review (trop court) | |
| Branche `main` protegee ? | A) Oui (merge via PR uniquement) — B) Non (push direct autorise) | |
| Convention de commits ? | `feat:`, `fix:`, `docs:`, `test:`, `chore:` (conventionnel) | |
| Tag avant soutenance ? | `v1.0` sur main quand tout est pret | |

### 1.3 Communication & suivi

| Question | Options | Decision |
|----------|---------|----------|
| Canal de communication ? | A) Discord — B) WhatsApp — C) Slack — D) Autre : _____ | |
| Standup async ? | Format : `[Fait] / [En cours] / [Bloque par]` — 1 message par session de travail | |
| Outil de suivi des taches ? | A) GitHub Issues — B) Trello — C) Fichier TASKS.md dans le repo — D) Autre | |
| Regle si bloque > 30 min ? | Message immediat sur le canal + ping le Lead | |

---

## Theme 2 — Contrat technique

### 2.1 Format JSON de sortie

Chaque fonction de chaque module DOIT retourner un dict avec cette structure :

```json
{
  "module": "diagnostic | backup | audit",
  "function": "nom_de_la_fonction",
  "timestamp": "2026-02-24T14:30:00Z",
  "status": "OK | WARNING | CRITICAL | UNKNOWN",
  "exit_code": 0,
  "target": "192.168.10.10",
  "details": {},
  "message": "Description lisible du resultat"
}
```

| Question | Options | Decision |
|----------|---------|----------|
| Ce schema est-il complet ? | A) Oui tel quel — B) Ajouter des champs : _____ | |
| Format du timestamp ? | A) ISO 8601 UTC (`2026-02-24T14:30:00Z`) — B) Local avec timezone | |
| Le champ `details` est libre par module ? | A) Oui, chaque module met ce qu'il veut — B) Sous-structure imposee | |

### 2.2 Codes retour (exit codes)

| Code | Signification | Seuils a definir |
|------|--------------|------------------|
| `0` — OK | Tout fonctionne | — |
| `1` — WARNING | Degradation | CPU > ___% ? Disque > ___% ? RAM > ___% ? |
| `2` — CRITICAL | Service down, echec | Connexion refusee, backup echoue |
| `3` — UNKNOWN | Impossible de joindre la cible | Timeout apres ___ secondes ? |

| Question | Options | Decision |
|----------|---------|----------|
| Seuil WARNING CPU ? | A) > 80% — B) > 85% — C) > 90% | |
| Seuil WARNING disque ? | A) > 80% — B) > 85% — C) > 90% | |
| Seuil WARNING RAM ? | A) > 80% — B) > 85% — C) > 90% | |
| Timeout par defaut ? | A) 5s — B) 10s — C) 15s | |

### 2.3 Gestion des erreurs

| Question | Options | Decision |
|----------|---------|----------|
| Exceptions custom ? | A) `ModuleConfigError` + `ModuleExecutionError` (voir `interfaces.py`) — B) Pas d'exceptions, juste exit_code 2/3 | |
| Un module plante = ? | A) Le CLI continue les autres modules — B) Le CLI s'arrete | |
| Logging | A) Module `logging` Python uniquement — B) `print()` autorise pour le debug | |
| Niveau de log par defaut ? | A) INFO — B) WARNING — C) Configurable dans le YAML | |

### 2.4 Signature commune des modules

Chaque module expose UNE fonction principale :

```python
def run(config: dict, target: str, **kwargs) -> dict:
    """
    Args:
        config: Configuration chargee depuis config.yaml
        target: Cible (IP, hostname, nom de base, plage reseau...)
        **kwargs: Arguments specifiques au module
    Returns:
        dict au format JSON commun (voir 2.1)
    Raises:
        ModuleConfigError: configuration manquante ou invalide
        ModuleExecutionError: erreur d'execution
    """
```

| Question | Options | Decision |
|----------|---------|----------|
| Cette signature convient ? | A) Oui — B) Modifier : _____ | |
| Le menu appelle `run()` de chaque module ? | A) Oui, le Lead code les appels dans main.py — B) Chaque module a son propre sous-menu | |

---

## Theme 3 — Configuration

### 3.1 Structure du config.yaml

```yaml
# config/config.yaml (NE PAS COMMITER — contient des secrets)
general:
  log_level: INFO          # DEBUG, INFO, WARNING
  output_dir: ./output
  timeout: 10              # secondes, par defaut

targets:
  dc01:
    host: 192.168.10.10
    type: windows
    description: "Domain Controller"
  wms_db:
    host: 192.168.10.21
    type: linux
    description: "WMS Database Server"

mysql:
  host: 192.168.10.21
  port: 3306
  user: "${MYSQL_USER}"        # surcharge par variable d'env
  password: "${MYSQL_PASSWORD}"
  database: wms

ssh:
  user: "${SSH_USER}"
  password: "${SSH_PASSWORD}"  # ou key_file
  # key_file: ~/.ssh/id_rsa
  port: 22

audit:
  network_range: "192.168.10.0/24"
  eol_database: "./data/eol_database.json"
  inventory_csv: "./data/sample_inventory.csv"
```

| Question | Options | Decision |
|----------|---------|----------|
| Cette structure est OK ? | A) Oui — B) Modifier : _____ | |
| Secrets : variables d'env ou fichier .env ? | A) `.env` + `python-dotenv` — B) Variables d'env systeme uniquement | |
| Chemin du config par defaut ? | A) `config/config.yaml` — B) `~/.ntl-systoolbox/config.yaml` — C) Argument CLI `--config` | |
| Config par defaut si fichier absent ? | A) Erreur + exit — B) Valeurs par defaut hardcodees | |

### 3.2 Surcharge par variables d'environnement

Convention : `NTL_` + section + `_` + cle en majuscules.

```
NTL_MYSQL_USER=admin
NTL_MYSQL_PASSWORD=secret123
NTL_SSH_USER=sysadmin
NTL_SSH_PASSWORD=motdepasse
NTL_GENERAL_LOG_LEVEL=DEBUG
```

| Question | Options | Decision |
|----------|---------|----------|
| Prefixe des variables d'env ? | A) `NTL_` — B) `SYSTOOL_` — C) Pas de prefixe | |

---

## Theme 4 — Modules

### 4.1 Module Diagnostic (Personne B)

| Question | Options | Decision |
|----------|---------|----------|
| `check_ad_dns()` : lib DNS ? | A) `dnspython` — B) `nslookup` via subprocess | |
| `check_ad_dns()` : port LDAP a tester ? | A) 389 uniquement — B) 389 + 636 (LDAPS) | |
| `check_mysql()` : quelles infos remonter ? | A) Connexion + `SHOW DATABASES` — B) + `SHOW STATUS` (uptime, threads) — C) + taille des bases | |
| `check_windows_server()` : comment ? | A) `wmic` via subprocess — B) `psutil` si local — C) WinRM distant | |
| `check_ubuntu()` : commandes SSH ? | `lsb_release -a`, `uptime`, `free -m`, `df -h` — autres ? _____ | |
| Lib LDAP sur Windows ? | A) `ldap3` (pure Python, cross-platform) — B) `python-ldap` (compile C, galere sur Win) | |
| Timeout SSH pour les checks ? | A) 10s — B) 15s — C) Valeur du config.yaml | |

### 4.2 Module Backup (Personne C)

| Question | Options | Decision |
|----------|---------|----------|
| `backup_database()` : methode ? | A) `mysqldump` via subprocess SSH — B) `mysqldump` en local — C) `mysql-connector` SELECT | |
| Nom du fichier backup ? | A) `wms_YYYYMMDD_HHMMSS.sql` — B) `backup_wms_YYYYMMDD.sql` — C) Autre : _____ | |
| Compression du backup ? | A) Non (fichier .sql brut) — B) Oui (gzip → .sql.gz) | |
| `export_table_csv()` : encodage ? | A) UTF-8 — B) UTF-8 BOM (pour Excel) — C) Configurable | |
| `export_table_csv()` : separateur ? | A) Virgule `,` — B) Point-virgule `;` (francais) — C) Configurable | |
| Verification SHA256 : quand ? | A) Apres chaque backup automatiquement — B) Fonction separee a appeler | |
| Ou stocker les backups ? | A) `output/backups/` — B) Configurable dans le YAML | |

### 4.3 Module Audit (Personne D)

| Question | Options | Decision |
|----------|---------|----------|
| `scan_network()` : flags nmap ? | A) `-sV` (version) + `-O` (OS) si admin — B) `-sT -sV` seulement (pas de privileges) — C) Adapter selon privileges detectes | |
| Comportement sans privileges admin ? | A) Warning + scan degrade — B) Erreur + stop | |
| `list_os_eol()` : source des dates ? | A) Fichier `data/eol_database.json` local — B) API endoflife.date en ligne | |
| `audit_from_csv()` : format CSV attendu ? | Colonnes : `hostname, os_name, os_version, role` — OK ? _____ | |
| `generate_report()` : format ? | A) JSON uniquement — B) JSON + tableau `rich` dans le terminal — C) JSON + HTML | |
| Tri du rapport ? | A) Par criticite (EXPIRE > BIENTOT_EXPIRE > OK) — B) Par hostname | |
| Seuil "bientot expire" ? | A) < 6 mois — B) < 12 mois — C) Configurable | |

---

## Theme 5 — Lab

### 5.1 Attribution

| VM | Qui la monte ? | Deadline |
|----|---------------|----------|
| DC01 (Windows Server 2022) | _______ | _______ |
| WMS-DB (Ubuntu 20.04) | _______ | _______ |

### 5.2 Checklist de validation du lab

> Ne pas commencer a coder les modules avant que ces checks soient OK.

**DC01 :**
- [ ] Windows Server 2022 installe, IP 192.168.10.10
- [ ] Role AD DS installe, domaine `ntl.local` cree
- [ ] DNS fonctionne (resolution `ntl.local` depuis le client)
- [ ] Port 389 (LDAP) accessible depuis le client
- [ ] (Optionnel) DHCP configure

**WMS-DB :**
- [ ] Ubuntu 20.04 installe, IP 192.168.10.21
- [ ] MySQL Server installe et demarre
- [ ] Base `wms` creee avec tables `shipments` + `inventory`
- [ ] Donnees de demo inserees (voir script SQL dans PLAN_PROJET.md)
- [ ] SSH actif, connexion possible depuis le client
- [ ] Utilisateur MySQL cree pour l'outil (pas root !)

**Reseau :**
- [ ] Ping entre toutes les machines OK
- [ ] Le PC client voit DC01 et WMS-DB

### 5.3 Donnees de test

| Donnee | Responsable | Fichier |
|--------|-------------|---------|
| Base MySQL `wms` (shipments + inventory) | Personne qui monte WMS-DB | Script SQL dans PLAN_PROJET.md |
| Base EOL (`eol_database.json`) | Dev Audit | `data/eol_database.json` |
| Inventaire CSV (`sample_inventory.csv`) | Dev Audit | `data/sample_inventory.csv` |

---

## Theme 6 — Integration & Tests

### 6.1 Planning d'integration

| Question | Options | Decision |
|----------|---------|----------|
| Quand fait-on le merge ? | A) Sync collective programmee — B) Chacun merge quand il est pret | |
| Ordre de merge ? | A) diagnostic → backup → audit — B) Tous en meme temps — C) Peu importe | |
| Qui resout les conflits de merge ? | A) Le Lead — B) Chacun les siens | |
| Date de "code freeze" ? | _______ (date/heure apres laquelle on ne code plus, on fixe et on documente) | |

### 6.2 Protocole de test (checklist pre-merge)

**Chaque dev doit valider AVANT de merger :**

**Module Diagnostic :**
- [ ] `check_ad_dns()` : connexion LDAP port 389 sur DC01 → status OK
- [ ] `check_ad_dns()` : resolution DNS `ntl.local` → status OK
- [ ] `check_mysql()` : connexion + `SHOW DATABASES` sur WMS-DB → status OK
- [ ] `check_windows_server()` : metriques CPU/RAM/Disque DC01 → status OK ou WARNING
- [ ] `check_ubuntu()` : SSH + metriques WMS-DB → status OK ou WARNING
- [ ] Toutes les fonctions retournent le format JSON commun
- [ ] Gestion d'erreur : timeout ou host down → status UNKNOWN, pas de crash

**Module Backup :**
- [ ] `backup_database()` : dump de `wms` → fichier .sql > 0 octets
- [ ] Hash SHA256 calcule et affiche
- [ ] `export_table_csv()` : export `shipments` → fichier CSV lisible
- [ ] `export_table_csv()` : export `inventory` → fichier CSV lisible
- [ ] Fichiers ecrits dans `output/backups/`
- [ ] Format JSON de retour conforme

**Module Audit :**
- [ ] `scan_network()` : scan du reseau lab → detecte DC01 + WMS-DB
- [ ] Comportement sans privileges admin : warning, pas crash
- [ ] `list_os_eol()` : retourne les dates pour Windows Server 2022 et Ubuntu 20.04
- [ ] `audit_from_csv()` : croise l'inventaire CSV avec la base EOL
- [ ] `generate_report()` : rapport trie par criticite
- [ ] Fichiers ecrits dans `output/reports/`

**Integration (apres merge) :**
- [ ] Le menu CLI affiche les 3 modules
- [ ] Navigation : choix module → choix fonction → saisie arguments → resultat
- [ ] Logs ecrits dans `output/logs/`
- [ ] Exit codes corrects (echo $? apres execution)
- [ ] Cross-platform : tester sur Windows ET Linux si possible

### 6.3 Plan B si un module n'est pas pret

| Question | Options | Decision |
|----------|---------|----------|
| Module pas fini a la deadline ? | A) Stub avec message "Non implemente" — B) On supprime du menu — C) Le Lead finit | |

---

## Theme 7 — Docs & Soutenance

> **A remplir en fin de projet, PAS maintenant.**

### 7.1 Repartition de la documentation

| Document | Qui redige ? | Deadline |
|----------|-------------|----------|
| Document technique et fonctionnel | _______ | _______ |
| Manuel d'installation et d'utilisation | _______ | _______ |
| Rapport d'execution de l'audit | _______ | _______ |
| Resume en anglais | _______ | _______ |
| Slides de soutenance | Tous — _______ pilote | _______ |

### 7.2 Script de demo (a preparer avant la soutenance)

```
1. Lancer le CLI → montrer le menu
2. Module 1 : diagnostic DC01 → montrer sortie JSON
3. Module 1 : diagnostic WMS-DB → montrer sortie JSON
4. Module 2 : backup base wms → montrer le fichier + SHA256
5. Module 2 : export CSV → montrer le fichier
6. Module 3 : scan reseau → montrer les machines detectees
7. Module 3 : audit EOL → montrer le rapport colore (rich)
8. Montrer les logs dans output/logs/
```

### 7.3 Soutenance — repartition du temps

| Temps | Contenu | Qui ? |
|-------|---------|-------|
| 0-3 min | Contexte NTL, problematique | _______ |
| 3-7 min | Architecture technique | _______ |
| 7-11 min | Demo Modules 1 + 2 | _______ |
| 11-15 min | Demo Module 3 | _______ |
| 15-18 min | Difficultes et solutions | _______ |
| 18-20 min | Perspectives + conclusion | _______ |

---

## Resume des decisions prises

> Remplir a la fin de la reunion.

| # | Decision | Valeur retenue |
|---|----------|---------------|
| 1 | Strategie de merge | |
| 2 | Review des PRs | |
| 3 | Canal de communication | |
| 4 | Outil de suivi | |
| 5 | Seuils WARNING (CPU/Disque/RAM) | |
| 6 | Timeout par defaut | |
| 7 | Gestion des erreurs | |
| 8 | Niveau de log | |
| 9 | Secrets (.env vs env vars) | |
| 10 | Prefixe variables d'env | |
| 11 | Lib LDAP | |
| 12 | Methode backup | |
| 13 | Flags nmap | |
| 14 | Source EOL | |
| 15 | Format rapport audit | |
| 16 | Date code freeze | |
| 17 | Plan B module pas pret | |

---

*Document genere le 2026-02-24 — a parcourir en reunion d'equipe avant de coder.*
