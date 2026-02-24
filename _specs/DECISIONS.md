# Décisions d'équipe — NTL-SysToolbox

> **Objectif :** Parcourir ce document ensemble en ~50 min.
> Chaque question a une **recommandation pré-remplie**. L'équipe **valide** ou **surcharge**.
> Le scribe remplit la colonne "Décision". À la fin, chacun repart avec ses specs.
>
> **Date de la réunion :** 26 février 2026
> **Présents :** Ianis PUICHAUD, Zaid ABOUYAALA, Ojvind LANTSIGBLE, Blaise WANDA NKONG

---

## Déroulement de la réunion (~50 min)

| Phase | Durée | Méthode | Thèmes concernés |
|-------|-------|---------|-----------------|
| **Tier 1 — Validations rapides** | ~5 min | Lecture à voix haute, vote main levée, SUIVANT | 1.2 (Git), 2.1 (JSON), 2.4 (Signature), 3.2 (Préfixe env) |
| **Tier 2 — Choix techniques** | ~15 min | Présenter la reco, discuter si désaccord | 2.2 (Seuils), 2.3 (Erreurs), 3.1 (Config), 4.1-4.3 (Modules), 6.3 (Plan B) |
| **Tier 3 — Organisation équipe** | ~30 min | Discussion libre, consensus | 1.1 (Rôles), 1.3 (Communication), 5.1 (Lab), 6.1 (Intégration), 7.1 + 7.3 (Docs/Soutenance) |

> **Règle :** Si tout le monde est d'accord avec la reco → on valide en 10 secondes et on passe.
> On ne débat QUE si quelqu'un a un désaccord argumenté.

---

## Thème 1 — Organisation & Git

### 1.1 Répartition des rôles

| Rôle | Responsabilité | Qui ? |
|------|----------------|-------|
| **Lead / Intégrateur** | `main.py`, menu CLI, config_loader, utils, merge final | **Ianis PUICHAUD** |
| **Dev Diagnostic** | `modules/diagnostic.py` — checks AD, DNS, MySQL, serveurs | À attribuer (Zaid / Ojvind / Blaise) |
| **Dev Backup** | `modules/backup.py` — dump MySQL, export CSV, SHA256 | À attribuer (Zaid / Ojvind / Blaise) |
| **Dev Audit** | `modules/audit.py` — scan nmap, EOL, rapport | À attribuer (Zaid / Ojvind / Blaise) |

> **Règle :** Le Lead est le seul à toucher `main.py` et `src/utils/`. Les devs ne modifient QUE leur module.

### 1.2 Workflow Git

| Question | Options | Recommandé | Décision |
|----------|---------|------------|----------|
| Convention de branches ? | `feature/module-diagnostic`, `feature/module-backup`, `feature/module-audit`, `feature/cli-menu` | **Telles quelles** — standard, déjà dans le plan | Telles quelles |
| Qui crée le repo + invite les autres ? | Lead | **Lead** | Lead |
| Stratégie de merge ? | A) Merge commit (historique lisible) — B) Squash (1 commit par branche) | **B) Squash** — 1 commit propre par feature, historique lisible | B) Squash |
| Qui review les PRs ? | A) Le Lead review tout — B) Chacun review 1 autre — C) Pas de review | **A) Lead review tout** — plus rapide, 1 gatekeeper | A) Lead review tout |
| Branche `main` protégée ? | A) Oui (merge via PR uniquement) — B) Non (push direct) | **A) Oui** — empêche un push accidentel | A) Oui |
| Convention de commits ? | `feat:`, `fix:`, `docs:`, `test:`, `chore:` (conventionnel) | **Oui, conventionnel** — standard de l'industrie | Conventionnel |
| Tag avant soutenance ? | `v1.0` sur main quand tout est prêt | **Oui** — `v1.0` | Oui, `v1.0` |

### 1.3 Communication & suivi

| Question | Options | Recommandé | Décision |
|----------|---------|------------|----------|
| Canal de communication ? | A) Discord — B) WhatsApp — C) Slack — D) Autre : _____ | **A) Discord** — voix + texte + partage écran | B) WhatsApp |
| Standup async ? | Format : `[Fait] / [En cours] / [Bloqué par]` — 1 message par session | **Oui, tel quel** — simple et efficace | Oui, tel quel |
| Outil de suivi des tâches ? | A) GitHub Issues — B) Trello — C) Fichier TASKS.md — D) Autre | **A) GitHub Issues** — intégré aux PRs, pas d'outil externe | A) GitHub Issues |
| Règle si bloqué > 30 min ? | Message immédiat sur le canal + ping le Lead | **Oui, tel quel** — évite les heures perdues | Oui, tel quel |

---

## Thème 2 — Contrat technique

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
  "message": "Description lisible du résultat"
}
```

| Question | Options | Recommandé | Décision |
|----------|---------|------------|----------|
| Ce schéma est-il complet ? | A) Oui tel quel — B) Ajouter des champs : _____ | **A) Oui** — déjà implémenté dans `interfaces.py` | A) Oui tel quel |
| Format du timestamp ? | A) ISO 8601 UTC (`2026-02-24T14:30:00Z`) — B) Local avec timezone | **A) ISO 8601 UTC** — standard, déjà dans `build_result()` | A) ISO 8601 UTC |
| Le champ `details` est libre par module ? | A) Oui, chaque module met ce qu'il veut — B) Sous-structure imposée | **A) Libre** — chaque module a ses propres métriques | A) Libre par module |

### 2.2 Codes retour (exit codes)

| Code | Signification | Seuils à définir |
|------|--------------|------------------|
| `0` — OK | Tout fonctionne | — |
| `1` — WARNING | Dégradation | CPU > ___% ? Disque > ___% ? RAM > ___% ? |
| `2` — CRITICAL | Service down, échec | Connexion refusée, backup échoué |
| `3` — UNKNOWN | Impossible de joindre la cible | Timeout après ___ secondes ? |

| Question | Options | Recommandé | Décision |
|----------|---------|------------|----------|
| Seuil WARNING CPU ? | A) > 80% — B) > 85% — C) > 90% | **A) > 80%** — règle simple, identique partout | A) > 80% |
| Seuil WARNING disque ? | A) > 80% — B) > 85% — C) > 90% | **A) > 80%** | A) > 80% |
| Seuil WARNING RAM ? | A) > 80% — B) > 85% — C) > 90% | **A) > 80%** | A) > 80% |
| Timeout par défaut ? | A) 5s — B) 10s — C) 15s | **B) 10s** — déjà dans `config.example.yaml` | B) 10s |

### 2.3 Gestion des erreurs

| Question | Options | Recommandé | Décision |
|----------|---------|------------|----------|
| Exceptions custom ? | A) `ModuleConfigError` + `ModuleExecutionError` (voir `interfaces.py`) — B) Pas d'exceptions | **A) Custom** — déjà dans `interfaces.py`, prêt à l'emploi | A) Custom |
| Un module plante = ? | A) Le CLI continue les autres modules — B) Le CLI s'arrête | **A) Continue** — résilience, montre de la maturité au jury | A) Continue |
| Logging | A) Module `logging` Python uniquement — B) `print()` autorisé pour le debug | **A) `logging` uniquement** — pro, pas de print en prod | A) `logging` uniquement |
| Niveau de log par défaut ? | A) INFO — B) WARNING — C) Configurable dans le YAML | **C) Configurable YAML** — déjà prévu dans config | C) Configurable YAML |

### 2.4 Signature commune des modules

Chaque module expose UNE fonction principale :

```python
def run(config: dict, target: str, **kwargs) -> dict:
    """
    Args:
        config: Configuration chargée depuis config.yaml
        target: Cible (IP, hostname, nom de base, plage réseau...)
        **kwargs: Arguments spécifiques au module
    Returns:
        dict au format JSON commun (voir 2.1)
    Raises:
        ModuleConfigError: configuration manquante ou invalide
        ModuleExecutionError: erreur d'exécution
    """
```

| Question | Options | Recommandé | Décision |
|----------|---------|------------|----------|
| Cette signature convient ? | A) Oui — B) Modifier : _____ | **A) Oui** — déjà dans `_template.py` | A) Oui |
| Le menu appelle `run()` de chaque module ? | A) Oui, le Lead code les appels dans main.py — B) Chaque module a son propre sous-menu | **A) Oui** — le Lead centralise dans `main.py` | A) Oui |

---

## Thème 3 — Configuration

### 3.1 Structure du config.yaml

```yaml
# config/config.yaml (NE PAS COMMITER — contient des secrets)
general:
  log_level: INFO          # DEBUG, INFO, WARNING
  output_dir: ./output
  timeout: 10              # secondes, par défaut

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

| Question | Options | Recommandé | Décision |
|----------|---------|------------|----------|
| Cette structure est OK ? | A) Oui — B) Modifier : _____ | **A) Oui** — déjà dans `config.example.yaml` | A) Oui |
| Secrets : variables d'env ou fichier .env ? | A) `.env` + `python-dotenv` — B) Variables d'env système uniquement | **A) `.env` + python-dotenv** — standard, déjà dans requirements | A) `.env` + python-dotenv |
| Chemin du config par défaut ? | A) `config/config.yaml` — B) `~/.ntl-systoolbox/config.yaml` — C) Argument CLI `--config` | **A) `config/config.yaml`** — simple, + support `--config` en bonus | A) `config/config.yaml` |
| Config par défaut si fichier absent ? | A) Erreur + exit — B) Valeurs par défaut hardcodées | **A) Erreur + exit** — explicite, pas de magie | A) Erreur + exit |

### 3.2 Surcharge par variables d'environnement

Convention : `NTL_` + section + `_` + clé en majuscules.

```
NTL_MYSQL_USER=admin
NTL_MYSQL_PASSWORD=secret123
NTL_SSH_USER=sysadmin
NTL_SSH_PASSWORD=motdepasse
NTL_GENERAL_LOG_LEVEL=DEBUG
```

| Question | Options | Recommandé | Décision |
|----------|---------|------------|----------|
| Préfixe des variables d'env ? | A) `NTL_` — B) `SYSTOOL_` — C) Pas de préfixe | **A) `NTL_`** — déjà dans `.env.example` | A) `NTL_` |

---

## Thème 4 — Modules

### 4.1 Module Diagnostic (Personne B)

| Question | Options | Recommandé | Décision |
|----------|---------|------------|----------|
| `check_ad_dns()` : lib DNS ? | A) `dnspython` — B) `nslookup` via subprocess | **A) `dnspython`** — cross-platform, dans requirements | A) `dnspython` |
| `check_ad_dns()` : port LDAP à tester ? | A) 389 uniquement — B) 389 + 636 (LDAPS) | **A) 389 uniquement** — LDAPS optionnel, gain de temps | A) 389 uniquement |
| `check_mysql()` : quelles infos remonter ? | A) Connexion + `SHOW DATABASES` — B) + `SHOW STATUS` (uptime, threads) — C) + taille des bases | **B) + SHOW STATUS** — uptime/threads impressionnent le jury | B) + SHOW STATUS |
| `check_windows_server()` : comment ? | A) `wmic` via subprocess — B) `psutil` si local — C) WinRM distant | **A) `wmic` via subprocess** — fonctionne à distance sans setup | A) `wmic` subprocess |
| `check_ubuntu()` : commandes SSH ? | `lsb_release -a`, `uptime`, `free -m`, `df -h` — autres ? _____ | **Telles quelles** + `systemctl status mysql` | Telles quelles + systemctl |
| Lib LDAP sur Windows ? | A) `ldap3` (pure Python, cross-platform) — B) `python-ldap` (compile C) | **A) `ldap3`** — pure Python, zéro galère d'install | A) `ldap3` |
| Timeout SSH pour les checks ? | A) 10s — B) 15s — C) Valeur du config.yaml | **C) Valeur du config.yaml** — cohérent avec le timeout global | C) Valeur config.yaml |

### 4.2 Module Backup (Personne C)

| Question | Options | Recommandé | Décision |
|----------|---------|------------|----------|
| `backup_database()` : méthode ? | A) `mysqldump` via subprocess SSH — B) `mysqldump` en local — C) `mysql-connector` SELECT | **A) `mysqldump` via SSH** — le plus fiable pour un dump complet | A) mysqldump via SSH |
| Nom du fichier backup ? | A) `wms_YYYYMMDD_HHMMSS.sql` — B) `backup_wms_YYYYMMDD.sql` — C) Autre : _____ | **A) `wms_YYYYMMDD_HHMMSS.sql`** — horodatage précis | A) `wms_YYYYMMDD_HHMMSS.sql` |
| Compression du backup ? | A) Non (fichier .sql brut) — B) Oui (gzip -> .sql.gz) | **A) Non** — plus simple, le jury peut ouvrir le .sql | A) Non |
| `export_table_csv()` : encodage ? | A) UTF-8 — B) UTF-8 BOM (pour Excel) — C) Configurable | **A) UTF-8** — standard universel | A) UTF-8 |
| `export_table_csv()` : séparateur ? | A) Virgule `,` — B) Point-virgule `;` (français) — C) Configurable | **A) Virgule** — standard CSV, Excel sait lire | A) Virgule |
| Vérification SHA256 : quand ? | A) Après chaque backup automatiquement — B) Fonction séparée à appeler | **A) Auto** — zéro oubli, intégrité garantie | A) Auto |
| Où stocker les backups ? | A) `output/backups/` — B) Configurable dans le YAML | **A) `output/backups/`** — cohérent avec la structure du repo | A) `output/backups/` |

### 4.3 Module Audit (Personne D)

| Question | Options | Recommandé | Décision |
|----------|---------|------------|----------|
| `scan_network()` : flags nmap ? | A) `-sV` + `-O` si admin — B) `-sT -sV` seulement — C) Adapter selon privilèges | **C) Adapter** — détecter les privilèges + fallback, montre maturité | C) Adapter selon privilèges |
| Comportement sans privilèges admin ? | A) Warning + scan dégradé — B) Erreur + stop | **A) Warning + scan dégradé** — résilience | A) Warning + scan dégradé |
| `list_os_eol()` : source des dates ? | A) Fichier `data/eol_database.json` local — B) API endoflife.date en ligne | **A) JSON local** — pas de dépendance réseau, fiable en démo | A) JSON local |
| `audit_from_csv()` : format CSV attendu ? | Colonnes : `hostname, os_name, os_version, role` — OK ? _____ | **OK tel quel** — simple et suffisant | OK tel quel |
| `generate_report()` : format ? | A) JSON uniquement — B) JSON + tableau `rich` — C) JSON + HTML | **B) JSON + `rich`** — visuel en démo, exportable en JSON | B) JSON + `rich` |
| Tri du rapport ? | A) Par criticité (EXPIRE > BIENTOT > OK) — B) Par hostname | **A) Par criticité** — logique business, EXPIRE en premier | A) Par criticité |
| Seuil "bientôt expiré" ? | A) < 6 mois — B) < 12 mois — C) Configurable | **A) < 6 mois** — assez urgent pour alerter | A) < 6 mois |

---

## Thème 5 — Lab

### 5.1 Attribution

| VM | Qui la monte ? | Deadline |
|----|---------------|----------|
| DC01 (Windows Server 2022) | **Ianis PUICHAUD** | 26 février 2026 |
| WMS-DB (Ubuntu 20.04) | **Ianis PUICHAUD** | 26 février 2026 |

### 5.2 Checklist de validation du lab

> Ne pas commencer à coder les modules avant que ces checks soient OK.

**DC01 :**
- [ ] Windows Server 2022 installé, IP 192.168.10.10
- [ ] Rôle AD DS installé, domaine `ntl.local` créé
- [ ] DNS fonctionne (résolution `ntl.local` depuis le client)
- [ ] Port 389 (LDAP) accessible depuis le client
- [ ] (Optionnel) DHCP configuré

**WMS-DB :**
- [ ] Ubuntu 20.04 installé, IP 192.168.10.21
- [ ] MySQL Server installé et démarré
- [ ] Base `wms` créée avec tables `shipments` + `inventory`
- [ ] Données de démo insérées (voir script SQL dans PLAN_PROJET.md)
- [ ] SSH actif, connexion possible depuis le client
- [ ] Utilisateur MySQL créé pour l'outil (pas root !)

**Réseau :**
- [ ] Ping entre toutes les machines OK
- [ ] Le PC client voit DC01 et WMS-DB

### 5.3 Données de test

| Donnée | Responsable | Fichier |
|--------|-------------|---------|
| Base MySQL `wms` (shipments + inventory) | Personne qui monte WMS-DB | Script SQL dans PLAN_PROJET.md |
| Base EOL (`eol_database.json`) | Dev Audit | `data/eol_database.json` |
| Inventaire CSV (`sample_inventory.csv`) | Dev Audit | `data/sample_inventory.csv` |

---

## Thème 6 — Intégration & Tests

### 6.1 Planning d'intégration

| Question | Options | Recommandé | Décision |
|----------|---------|------------|----------|
| Quand fait-on le merge ? | A) Sync collective programmée — B) Chacun merge quand il est prêt | **A) Sync collective** — évite les surprises | A) Sync collective |
| Ordre de merge ? | A) diagnostic -> backup -> audit — B) Tous en même temps — C) Peu importe | **A) diagnostic -> backup -> audit** — moins de risque | A) diag -> backup -> audit |
| Qui résout les conflits de merge ? | A) Le Lead — B) Chacun les siens | **A) Le Lead** — cohérent avec son rôle d'intégrateur | A) Le Lead |
| Date de "code freeze" ? | _______ (date/heure après laquelle on ne code plus) | **Suggéré : 2h avant la fin du dev** | 2h avant fin dev |

### 6.2 Protocole de test (checklist pré-merge)

**Chaque dev doit valider AVANT de merger :**

**Module Diagnostic :**
- [ ] `check_ad_dns()` : connexion LDAP port 389 sur DC01 -> status OK
- [ ] `check_ad_dns()` : résolution DNS `ntl.local` -> status OK
- [ ] `check_mysql()` : connexion + `SHOW DATABASES` sur WMS-DB -> status OK
- [ ] `check_windows_server()` : métriques CPU/RAM/Disque DC01 -> status OK ou WARNING
- [ ] `check_ubuntu()` : SSH + métriques WMS-DB -> status OK ou WARNING
- [ ] Toutes les fonctions retournent le format JSON commun
- [ ] Gestion d'erreur : timeout ou host down -> status UNKNOWN, pas de crash

**Module Backup :**
- [ ] `backup_database()` : dump de `wms` -> fichier .sql > 0 octets
- [ ] Hash SHA256 calculé et affiché
- [ ] `export_table_csv()` : export `shipments` -> fichier CSV lisible
- [ ] `export_table_csv()` : export `inventory` -> fichier CSV lisible
- [ ] Fichiers écrits dans `output/backups/`
- [ ] Format JSON de retour conforme

**Module Audit :**
- [ ] `scan_network()` : scan du réseau lab -> détecte DC01 + WMS-DB
- [ ] Comportement sans privilèges admin : warning, pas crash
- [ ] `list_os_eol()` : retourne les dates pour Windows Server 2022 et Ubuntu 20.04
- [ ] `audit_from_csv()` : croise l'inventaire CSV avec la base EOL
- [ ] `generate_report()` : rapport trié par criticité
- [ ] Fichiers écrits dans `output/reports/`

**Intégration (après merge) :**
- [ ] Le menu CLI affiche les 3 modules
- [ ] Navigation : choix module -> choix fonction -> saisie arguments -> résultat
- [ ] Logs écrits dans `output/logs/`
- [ ] Exit codes corrects (echo $? après exécution)
- [ ] Cross-platform : tester sur Windows ET Linux si possible

### 6.3 Plan B si un module n'est pas prêt

| Question | Options | Recommandé | Décision |
|----------|---------|------------|----------|
| Module pas fini à la deadline ? | A) Stub avec message "Non implémenté" — B) On supprime du menu — C) Le Lead finit | **A) Stub** — le menu reste complet, montre la structure | A) Stub |

---

## Thème 7 — Docs & Soutenance

> **À remplir en fin de projet, PAS maintenant.** Notez juste les noms et deadlines.

### 7.1 Répartition de la documentation

| Document | Qui rédige ? | Deadline |
|----------|-------------|----------|
| Document technique et fonctionnel | **Ianis PUICHAUD** | 31 mars 2026 |
| Manuel d'installation et d'utilisation | **Ianis PUICHAUD** | 31 mars 2026 |
| Rapport d'exécution de l'audit | **Dev Audit** (à confirmer) | 31 mars 2026 |
| Résumé en anglais | **Ianis PUICHAUD** | 31 mars 2026 |
| Slides de soutenance | Tous — **Ianis** pilote | 4 avril 2026 |

### 7.2 Script de démo (à préparer avant la soutenance)

```
1. Lancer le CLI -> montrer le menu
2. Module 1 : diagnostic DC01 -> montrer sortie JSON
3. Module 1 : diagnostic WMS-DB -> montrer sortie JSON
4. Module 2 : backup base wms -> montrer le fichier + SHA256
5. Module 2 : export CSV -> montrer le fichier
6. Module 3 : scan réseau -> montrer les machines détectées
7. Module 3 : audit EOL -> montrer le rapport coloré (rich)
8. Montrer les logs dans output/logs/
```

### 7.3 Soutenance — répartition du temps

| Temps | Contenu | Qui ? |
|-------|---------|-------|
| 0-3 min | Contexte NTL, problématique | **Ianis** (présentation globale) |
| 3-7 min | Architecture technique | **Ianis** (Lead) |
| 7-11 min | Démo Modules 1 + 2 | **Dev Diagnostic** + **Dev Backup** (chacun son script) |
| 11-15 min | Démo Module 3 | **Dev Audit** (son script) |
| 15-18 min | Difficultés et solutions | **Chacun** sur son module |
| 18-20 min | Perspectives + conclusion | **Ianis** |

---

## Résumé des décisions prises

> Remplir à la fin de la réunion.

| # | Décision | Recommandé | Valeur retenue |
|---|----------|------------|---------------|
| 1 | Stratégie de merge | Squash | Squash |
| 2 | Review des PRs | Lead review tout | Lead review tout |
| 3 | Main protégé | Oui | Oui |
| 4 | Canal de communication | Discord | **WhatsApp** |
| 5 | Outil de suivi | GitHub Issues | GitHub Issues |
| 6 | Seuils WARNING (CPU/Disque/RAM) | 80% partout | 80% partout |
| 7 | Timeout par défaut | 10s | 10s |
| 8 | Exceptions custom | Oui (Config + Exécution) | Oui |
| 9 | Module plante = continue | Oui | Oui |
| 10 | Niveau de log | Configurable YAML | Configurable YAML |
| 11 | Secrets | .env + python-dotenv | .env + python-dotenv |
| 12 | Préfixe variables d'env | NTL_ | NTL_ |
| 13 | Lib LDAP | ldap3 | ldap3 |
| 14 | Méthode backup | mysqldump via SSH | mysqldump via SSH |
| 15 | Flags nmap | Adapter selon privilèges | Adapter selon privilèges |
| 16 | Source EOL | JSON local | JSON local |
| 17 | Format rapport audit | JSON + rich | JSON + rich |
| 18 | Plan B module pas prêt | Stub "Non implémenté" | Stub "Non implémenté" |
| 19 | Date code freeze | À définir | 2h avant fin dev |

---

*Document généré le 2026-02-24 — à parcourir en réunion d'équipe avant de coder.*
*Voir `WORKFLOW.md` pour le déroulement étape par étape du projet.*
