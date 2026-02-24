# Decisions d'equipe — NTL-SysToolbox

> **Objectif :** Parcourir ce document ensemble en ~50 min.
> Chaque question a une **recommandation pre-remplie**. L'equipe **valide** ou **surcharge**.
> Le scribe remplit la colonne "Decision". A la fin, chacun repart avec ses specs.
>
> **Date de la reunion :** _______________
> **Presents :** _______________

---

## Deroulement de la reunion (~50 min)

| Phase | Duree | Methode | Themes concernes |
|-------|-------|---------|-----------------|
| **Tier 1 — Validations rapides** | ~5 min | Lecture a voix haute, vote main levee, SUIVANT | 1.2 (Git), 2.1 (JSON), 2.4 (Signature), 3.2 (Prefixe env) |
| **Tier 2 — Choix techniques** | ~15 min | Presenter la reco, discuter si desaccord | 2.2 (Seuils), 2.3 (Erreurs), 3.1 (Config), 4.1-4.3 (Modules), 6.3 (Plan B) |
| **Tier 3 — Organisation equipe** | ~30 min | Discussion libre, consensus | 1.1 (Roles), 1.3 (Communication), 5.1 (Lab), 6.1 (Integration), 7.1 + 7.3 (Docs/Soutenance) |

> **Regle :** Si tout le monde est d'accord avec la reco → on valide en 10 secondes et on passe.
> On ne debat QUE si quelqu'un a un desaccord argumente.

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

| Question | Options | Recommande | Decision |
|----------|---------|------------|----------|
| Convention de branches ? | `feature/module-diagnostic`, `feature/module-backup`, `feature/module-audit`, `feature/cli-menu` | **Telles quelles** — standard, deja dans le plan | |
| Qui cree le repo + invite les autres ? | Lead | **Lead** | |
| Strategie de merge ? | A) Merge commit (historique lisible) — B) Squash (1 commit par branche) | **B) Squash** — 1 commit propre par feature, historique lisible | |
| Qui review les PRs ? | A) Le Lead review tout — B) Chacun review 1 autre — C) Pas de review | **A) Lead review tout** — plus rapide, 1 gatekeeper | |
| Branche `main` protegee ? | A) Oui (merge via PR uniquement) — B) Non (push direct) | **A) Oui** — empeche un push accidentel | |
| Convention de commits ? | `feat:`, `fix:`, `docs:`, `test:`, `chore:` (conventionnel) | **Oui, conventionnel** — standard de l'industrie | |
| Tag avant soutenance ? | `v1.0` sur main quand tout est pret | **Oui** — `v1.0` | |

### 1.3 Communication & suivi

| Question | Options | Recommande | Decision |
|----------|---------|------------|----------|
| Canal de communication ? | A) Discord — B) WhatsApp — C) Slack — D) Autre : _____ | **A) Discord** — voix + texte + partage ecran | |
| Standup async ? | Format : `[Fait] / [En cours] / [Bloque par]` — 1 message par session | **Oui, tel quel** — simple et efficace | |
| Outil de suivi des taches ? | A) GitHub Issues — B) Trello — C) Fichier TASKS.md — D) Autre | **A) GitHub Issues** — integre aux PRs, pas d'outil externe | |
| Regle si bloque > 30 min ? | Message immediat sur le canal + ping le Lead | **Oui, tel quel** — evite les heures perdues | |

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

| Question | Options | Recommande | Decision |
|----------|---------|------------|----------|
| Ce schema est-il complet ? | A) Oui tel quel — B) Ajouter des champs : _____ | **A) Oui** — deja implemente dans `interfaces.py` | |
| Format du timestamp ? | A) ISO 8601 UTC (`2026-02-24T14:30:00Z`) — B) Local avec timezone | **A) ISO 8601 UTC** — standard, deja dans `build_result()` | |
| Le champ `details` est libre par module ? | A) Oui, chaque module met ce qu'il veut — B) Sous-structure imposee | **A) Libre** — chaque module a ses propres metriques | |

### 2.2 Codes retour (exit codes)

| Code | Signification | Seuils a definir |
|------|--------------|------------------|
| `0` — OK | Tout fonctionne | — |
| `1` — WARNING | Degradation | CPU > ___% ? Disque > ___% ? RAM > ___% ? |
| `2` — CRITICAL | Service down, echec | Connexion refusee, backup echoue |
| `3` — UNKNOWN | Impossible de joindre la cible | Timeout apres ___ secondes ? |

| Question | Options | Recommande | Decision |
|----------|---------|------------|----------|
| Seuil WARNING CPU ? | A) > 80% — B) > 85% — C) > 90% | **A) > 80%** — regle simple, identique partout | |
| Seuil WARNING disque ? | A) > 80% — B) > 85% — C) > 90% | **A) > 80%** | |
| Seuil WARNING RAM ? | A) > 80% — B) > 85% — C) > 90% | **A) > 80%** | |
| Timeout par defaut ? | A) 5s — B) 10s — C) 15s | **B) 10s** — deja dans `config.example.yaml` | |

### 2.3 Gestion des erreurs

| Question | Options | Recommande | Decision |
|----------|---------|------------|----------|
| Exceptions custom ? | A) `ModuleConfigError` + `ModuleExecutionError` (voir `interfaces.py`) — B) Pas d'exceptions | **A) Custom** — deja dans `interfaces.py`, pret a l'emploi | |
| Un module plante = ? | A) Le CLI continue les autres modules — B) Le CLI s'arrete | **A) Continue** — resilience, montre de la maturite au jury | |
| Logging | A) Module `logging` Python uniquement — B) `print()` autorise pour le debug | **A) `logging` uniquement** — pro, pas de print en prod | |
| Niveau de log par defaut ? | A) INFO — B) WARNING — C) Configurable dans le YAML | **C) Configurable YAML** — deja prevu dans config | |

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

| Question | Options | Recommande | Decision |
|----------|---------|------------|----------|
| Cette signature convient ? | A) Oui — B) Modifier : _____ | **A) Oui** — deja dans `_template.py` | |
| Le menu appelle `run()` de chaque module ? | A) Oui, le Lead code les appels dans main.py — B) Chaque module a son propre sous-menu | **A) Oui** — le Lead centralise dans `main.py` | |

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

| Question | Options | Recommande | Decision |
|----------|---------|------------|----------|
| Cette structure est OK ? | A) Oui — B) Modifier : _____ | **A) Oui** — deja dans `config.example.yaml` | |
| Secrets : variables d'env ou fichier .env ? | A) `.env` + `python-dotenv` — B) Variables d'env systeme uniquement | **A) `.env` + python-dotenv** — standard, deja dans requirements | |
| Chemin du config par defaut ? | A) `config/config.yaml` — B) `~/.ntl-systoolbox/config.yaml` — C) Argument CLI `--config` | **A) `config/config.yaml`** — simple, + support `--config` en bonus | |
| Config par defaut si fichier absent ? | A) Erreur + exit — B) Valeurs par defaut hardcodees | **A) Erreur + exit** — explicite, pas de magie | |

### 3.2 Surcharge par variables d'environnement

Convention : `NTL_` + section + `_` + cle en majuscules.

```
NTL_MYSQL_USER=admin
NTL_MYSQL_PASSWORD=secret123
NTL_SSH_USER=sysadmin
NTL_SSH_PASSWORD=motdepasse
NTL_GENERAL_LOG_LEVEL=DEBUG
```

| Question | Options | Recommande | Decision |
|----------|---------|------------|----------|
| Prefixe des variables d'env ? | A) `NTL_` — B) `SYSTOOL_` — C) Pas de prefixe | **A) `NTL_`** — deja dans `.env.example` | |

---

## Theme 4 — Modules

### 4.1 Module Diagnostic (Personne B)

| Question | Options | Recommande | Decision |
|----------|---------|------------|----------|
| `check_ad_dns()` : lib DNS ? | A) `dnspython` — B) `nslookup` via subprocess | **A) `dnspython`** — cross-platform, dans requirements | |
| `check_ad_dns()` : port LDAP a tester ? | A) 389 uniquement — B) 389 + 636 (LDAPS) | **A) 389 uniquement** — LDAPS optionnel, gain de temps | |
| `check_mysql()` : quelles infos remonter ? | A) Connexion + `SHOW DATABASES` — B) + `SHOW STATUS` (uptime, threads) — C) + taille des bases | **B) + SHOW STATUS** — uptime/threads impressionnent le jury | |
| `check_windows_server()` : comment ? | A) `wmic` via subprocess — B) `psutil` si local — C) WinRM distant | **A) `wmic` via subprocess** — fonctionne a distance sans setup | |
| `check_ubuntu()` : commandes SSH ? | `lsb_release -a`, `uptime`, `free -m`, `df -h` — autres ? _____ | **Telles quelles** + `systemctl status mysql` | |
| Lib LDAP sur Windows ? | A) `ldap3` (pure Python, cross-platform) — B) `python-ldap` (compile C) | **A) `ldap3`** — pure Python, zero galere d'install | |
| Timeout SSH pour les checks ? | A) 10s — B) 15s — C) Valeur du config.yaml | **C) Valeur du config.yaml** — coherent avec le timeout global | |

### 4.2 Module Backup (Personne C)

| Question | Options | Recommande | Decision |
|----------|---------|------------|----------|
| `backup_database()` : methode ? | A) `mysqldump` via subprocess SSH — B) `mysqldump` en local — C) `mysql-connector` SELECT | **A) `mysqldump` via SSH** — le plus fiable pour un dump complet | |
| Nom du fichier backup ? | A) `wms_YYYYMMDD_HHMMSS.sql` — B) `backup_wms_YYYYMMDD.sql` — C) Autre : _____ | **A) `wms_YYYYMMDD_HHMMSS.sql`** — horodatage precis | |
| Compression du backup ? | A) Non (fichier .sql brut) — B) Oui (gzip -> .sql.gz) | **A) Non** — plus simple, le jury peut ouvrir le .sql | |
| `export_table_csv()` : encodage ? | A) UTF-8 — B) UTF-8 BOM (pour Excel) — C) Configurable | **A) UTF-8** — standard universel | |
| `export_table_csv()` : separateur ? | A) Virgule `,` — B) Point-virgule `;` (francais) — C) Configurable | **A) Virgule** — standard CSV, Excel sait lire | |
| Verification SHA256 : quand ? | A) Apres chaque backup automatiquement — B) Fonction separee a appeler | **A) Auto** — zero oubli, integrite garantie | |
| Ou stocker les backups ? | A) `output/backups/` — B) Configurable dans le YAML | **A) `output/backups/`** — coherent avec la structure du repo | |

### 4.3 Module Audit (Personne D)

| Question | Options | Recommande | Decision |
|----------|---------|------------|----------|
| `scan_network()` : flags nmap ? | A) `-sV` + `-O` si admin — B) `-sT -sV` seulement — C) Adapter selon privileges | **C) Adapter** — detecter les privileges + fallback, montre maturite | |
| Comportement sans privileges admin ? | A) Warning + scan degrade — B) Erreur + stop | **A) Warning + scan degrade** — resilience | |
| `list_os_eol()` : source des dates ? | A) Fichier `data/eol_database.json` local — B) API endoflife.date en ligne | **A) JSON local** — pas de dependance reseau, fiable en demo | |
| `audit_from_csv()` : format CSV attendu ? | Colonnes : `hostname, os_name, os_version, role` — OK ? _____ | **OK tel quel** — simple et suffisant | |
| `generate_report()` : format ? | A) JSON uniquement — B) JSON + tableau `rich` — C) JSON + HTML | **B) JSON + `rich`** — visuel en demo, exportable en JSON | |
| Tri du rapport ? | A) Par criticite (EXPIRE > BIENTOT > OK) — B) Par hostname | **A) Par criticite** — logique business, EXPIRE en premier | |
| Seuil "bientot expire" ? | A) < 6 mois — B) < 12 mois — C) Configurable | **A) < 6 mois** — assez urgent pour alerter | |

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

| Question | Options | Recommande | Decision |
|----------|---------|------------|----------|
| Quand fait-on le merge ? | A) Sync collective programmee — B) Chacun merge quand il est pret | **A) Sync collective** — evite les surprises | |
| Ordre de merge ? | A) diagnostic -> backup -> audit — B) Tous en meme temps — C) Peu importe | **A) diagnostic -> backup -> audit** — moins de risque | |
| Qui resout les conflits de merge ? | A) Le Lead — B) Chacun les siens | **A) Le Lead** — coherent avec son role d'integrateur | |
| Date de "code freeze" ? | _______ (date/heure apres laquelle on ne code plus) | **Suggere : 2h avant la fin du dev** | |

### 6.2 Protocole de test (checklist pre-merge)

**Chaque dev doit valider AVANT de merger :**

**Module Diagnostic :**
- [ ] `check_ad_dns()` : connexion LDAP port 389 sur DC01 -> status OK
- [ ] `check_ad_dns()` : resolution DNS `ntl.local` -> status OK
- [ ] `check_mysql()` : connexion + `SHOW DATABASES` sur WMS-DB -> status OK
- [ ] `check_windows_server()` : metriques CPU/RAM/Disque DC01 -> status OK ou WARNING
- [ ] `check_ubuntu()` : SSH + metriques WMS-DB -> status OK ou WARNING
- [ ] Toutes les fonctions retournent le format JSON commun
- [ ] Gestion d'erreur : timeout ou host down -> status UNKNOWN, pas de crash

**Module Backup :**
- [ ] `backup_database()` : dump de `wms` -> fichier .sql > 0 octets
- [ ] Hash SHA256 calcule et affiche
- [ ] `export_table_csv()` : export `shipments` -> fichier CSV lisible
- [ ] `export_table_csv()` : export `inventory` -> fichier CSV lisible
- [ ] Fichiers ecrits dans `output/backups/`
- [ ] Format JSON de retour conforme

**Module Audit :**
- [ ] `scan_network()` : scan du reseau lab -> detecte DC01 + WMS-DB
- [ ] Comportement sans privileges admin : warning, pas crash
- [ ] `list_os_eol()` : retourne les dates pour Windows Server 2022 et Ubuntu 20.04
- [ ] `audit_from_csv()` : croise l'inventaire CSV avec la base EOL
- [ ] `generate_report()` : rapport trie par criticite
- [ ] Fichiers ecrits dans `output/reports/`

**Integration (apres merge) :**
- [ ] Le menu CLI affiche les 3 modules
- [ ] Navigation : choix module -> choix fonction -> saisie arguments -> resultat
- [ ] Logs ecrits dans `output/logs/`
- [ ] Exit codes corrects (echo $? apres execution)
- [ ] Cross-platform : tester sur Windows ET Linux si possible

### 6.3 Plan B si un module n'est pas pret

| Question | Options | Recommande | Decision |
|----------|---------|------------|----------|
| Module pas fini a la deadline ? | A) Stub avec message "Non implemente" — B) On supprime du menu — C) Le Lead finit | **A) Stub** — le menu reste complet, montre la structure | |

---

## Theme 7 — Docs & Soutenance

> **A remplir en fin de projet, PAS maintenant.** Notez juste les noms et deadlines.

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
1. Lancer le CLI -> montrer le menu
2. Module 1 : diagnostic DC01 -> montrer sortie JSON
3. Module 1 : diagnostic WMS-DB -> montrer sortie JSON
4. Module 2 : backup base wms -> montrer le fichier + SHA256
5. Module 2 : export CSV -> montrer le fichier
6. Module 3 : scan reseau -> montrer les machines detectees
7. Module 3 : audit EOL -> montrer le rapport colore (rich)
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

| # | Decision | Recommande | Valeur retenue |
|---|----------|------------|---------------|
| 1 | Strategie de merge | Squash | |
| 2 | Review des PRs | Lead review tout | |
| 3 | Main protege | Oui | |
| 4 | Canal de communication | Discord | |
| 5 | Outil de suivi | GitHub Issues | |
| 6 | Seuils WARNING (CPU/Disque/RAM) | 80% partout | |
| 7 | Timeout par defaut | 10s | |
| 8 | Exceptions custom | Oui (Config + Execution) | |
| 9 | Module plante = continue | Oui | |
| 10 | Niveau de log | Configurable YAML | |
| 11 | Secrets | .env + python-dotenv | |
| 12 | Prefixe variables d'env | NTL_ | |
| 13 | Lib LDAP | ldap3 | |
| 14 | Methode backup | mysqldump via SSH | |
| 15 | Flags nmap | Adapter selon privileges | |
| 16 | Source EOL | JSON local | |
| 17 | Format rapport audit | JSON + rich | |
| 18 | Plan B module pas pret | Stub "Non implemente" | |
| 19 | Date code freeze | A definir | |

---

*Document genere le 2026-02-24 — a parcourir en reunion d'equipe avant de coder.*
*Voir `WORKFLOW.md` pour le deroulement etape par etape du projet.*
