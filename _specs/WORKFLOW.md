# Workflow NTL-SysToolbox — Guide lineaire

> Ce document se lit **de haut en bas**, etape par etape.
> Chaque etape a des prerequis et une definition de "fini".
> Cochez les cases au fur et a mesure.
>
> **Temps total prevu : 19h | Marge : quasi nulle**
> **Priorite absolue : code fonctionnel > documentation > slides**

---

## Etape 0 — Reunion d'equipe (~1h)

**Qui :** Tous (4 personnes)
**Quand :** Debut du projet, avant toute ligne de code
**Prerequis :** Avoir lu `PLAN_PROJET.md` en diagonale (sections 1 et 2)
**Document support :** `_specs/DECISIONS.md`

### Deroulement

1. [ ] Nommer un **scribe** (remplit les colonnes "Decision")
2. [ ] **Tier 1 (5 min)** — Validations rapides : lire chaque reco, vote main levee
   - Themes : 1.2 (Git), 2.1 (JSON), 2.4 (Signature), 3.2 (Prefixe env)
3. [ ] **Tier 2 (15 min)** — Choix techniques : presenter la reco, discuter si desaccord
   - Themes : 2.2 (Seuils), 2.3 (Erreurs), 3.1 (Config), 4.1-4.3 (Modules), 6.3 (Plan B)
4. [ ] **Tier 3 (30 min)** — Organisation equipe
   - Theme 1.1 : Repartition des roles → ecrire les noms
   - Theme 1.3 : Canal Discord/autre, outil de suivi
   - Theme 5.1 : Qui monte DC01 ? Qui monte WMS-DB ? Deadline ?
   - Theme 6.1 : Date du merge collectif, date du code freeze
   - Theme 7.1 : Repartition docs (noter les noms, on y reviendra en etape 7)
   - Theme 7.3 : Repartition soutenance (idem)
5. [ ] Remplir le **tableau recapitulatif** en bas de DECISIONS.md
6. [ ] Commit : `docs: decisions equipe validees`

**Fini quand :** Toutes les colonnes "Decision" sont remplies. Chacun connait son role et ses fichiers.

---

## Etape 1 — Setup du lab (~2h, parallelisable)

**Qui :** Reparti selon les decisions (Theme 5.1)
**Prerequis :** Etape 0 terminee
**Reference :** `PLAN_PROJET.md` sections 1.1 a 1.3

### Track A — DC01 (personne designee)

- [ ] Installer Windows Server 2022 (VM)
- [ ] IP statique : 192.168.10.10
- [ ] Installer le role AD DS, creer le domaine `ntl.local`
- [ ] Configurer DNS
- [ ] Verifier que le port 389 (LDAP) est ouvert

### Track B — WMS-DB (personne designee)

- [ ] Installer Ubuntu 20.04 (VM)
- [ ] IP statique : 192.168.10.21
- [ ] Installer MySQL Server
- [ ] Creer la base `wms` + tables (script SQL dans `PLAN_PROJET.md` section 1)
- [ ] Creer un utilisateur MySQL dedie (pas root !)
- [ ] Activer SSH

### Track C — Pendant ce temps (Lead + personne libre)

- [ ] Cloner le repo, `make setup`, verifier que le venv fonctionne
- [ ] Copier `config.example.yaml` → `config/config.yaml`, remplir les IPs
- [ ] Copier `.env.example` → `.env`, remplir les credentials
- [ ] Verifier : `python src/main.py` lance sans crash (meme si menu vide)

**Fini quand :** Les 2 VMs tournent et le PC client peut les pinger.

---

## Etape 2 — Validation du lab (~30 min, tous ensemble)

**Qui :** Tous
**Prerequis :** Etape 1 terminee
**Reference :** `DECISIONS.md` section 5.2 (checklist)

Parcourir la checklist ensemble :

- [ ] **DC01 :** ping OK, LDAP 389 OK, DNS resolution `ntl.local` OK
- [ ] **WMS-DB :** ping OK, SSH OK, MySQL connexion OK, base `wms` avec donnees
- [ ] **Reseau :** toutes les machines se voient
- [ ] **Client :** le CLI s'execute sans erreur

> **BLOQUANT :** Ne pas commencer le dev (etape 3) tant que cette checklist n'est pas verte.

**Fini quand :** Toutes les cases cochees. Screenshot ou log de validation partage sur le canal de com.

---

## Etape 3 — Developpement parallele (~10h)

**Qui :** Chacun sur sa branche
**Prerequis :** Etape 2 terminee + lab fonctionnel
**Reference :** `PLAN_PROJET.md` section 2 (fiches par personne), `_specs/QUICKREF.md`

### Regles communes

- Creer sa branche : `git checkout -b feature/module-<nom>`
- Copier `src/modules/_template.py` → `src/modules/<nom>.py`
- Chaque fonction retourne `build_result(...)` — voir `src/interfaces.py`
- Commit regulier : `feat: add check_ad_dns()`
- **Message sur le canal si bloque > 30 min**

### Track Lead

- [ ] Coder `src/main.py` : menu interactif (choix module → choix fonction)
- [ ] Coder `src/config_loader.py` : charge YAML + surcharge `.env`
- [ ] Completer `src/utils/network.py` si besoin (helpers ping, port check)
- [ ] Tester le menu avec le module template (dry run)
- [ ] Etre disponible pour debloquer les autres

### Track Diagnostic (Personne B)

- [ ] `check_ad_dns()` : LDAP port 389 + DNS resolution via `dnspython`
- [ ] `check_mysql()` : connexion + `SHOW DATABASES` + `SHOW STATUS`
- [ ] `check_windows_server()` : metriques CPU/RAM/disque via `wmic`
- [ ] `check_ubuntu()` : SSH + `lsb_release`, `uptime`, `free`, `df`
- [ ] `run()` : dispatcher vers les 4 fonctions selon kwargs
- [ ] Tester chaque fonction individuellement sur le lab

### Track Backup (Personne C)

- [ ] `backup_database()` : `mysqldump` via subprocess, fichier nomme
- [ ] SHA256 automatique apres dump
- [ ] `export_table_csv()` : SELECT → CSV pour `shipments` et `inventory`
- [ ] `run()` : dispatcher vers les fonctions
- [ ] Tester sur le lab : verifier fichiers dans `output/backups/`

### Track Audit (Personne D)

- [ ] Creer `data/eol_database.json` avec les dates EOL connues
- [ ] Creer `data/sample_inventory.csv` avec l'inventaire NTL
- [ ] `scan_network()` : nmap avec detection de privileges
- [ ] `list_os_eol()` : lecture du JSON EOL
- [ ] `audit_from_csv()` : croisement CSV + EOL
- [ ] `generate_report()` : JSON + tableau rich, tri par criticite
- [ ] Tester sur le lab : scan detecte DC01 + WMS-DB

**Fini quand :** Chaque dev a toutes ses cases cochees et a pousse sa branche.

---

## Etape 4 — Tests pre-merge (~30 min, chacun)

**Qui :** Chaque dev sur sa branche
**Prerequis :** Son module est code (etape 3 terminee pour soi)
**Reference :** `DECISIONS.md` section 6.2 (checklist pre-merge par module)

- [ ] Parcourir la checklist de **son module** dans `DECISIONS.md` section 6.2
- [ ] Toutes les fonctions retournent le format JSON commun
- [ ] Gestion d'erreur : timeout/host down → UNKNOWN, pas de crash
- [ ] Fichiers ecrits dans le bon dossier (`output/logs`, `backups`, `reports`)
- [ ] Commit final : `feat: module <nom> ready for merge`
- [ ] Ouvrir une **PR vers main**

**Fini quand :** PR ouverte, tous les tests du module passent sur le lab.

---

## Etape 5 — Integration / merge (~1h30)

**Qui :** Lead + tous en support
**Prerequis :** Toutes les PRs ouvertes (etape 4)
**Reference :** `DECISIONS.md` section 6.1

### Ordre de merge (decide en etape 0)

1. [ ] Merge PR `feature/cli-menu` (Lead)
2. [ ] Merge PR `feature/module-diagnostic`
3. [ ] Merge PR `feature/module-backup`
4. [ ] Merge PR `feature/module-audit`

### Apres chaque merge

- [ ] `git pull` sur main
- [ ] `python src/main.py` → verifier que le menu fonctionne
- [ ] Le nouveau module apparait et s'execute sans crash

### Si conflit

- Le Lead resout les conflits
- Si conflit dans un module : appeler le dev concerne

**Fini quand :** `main` contient les 4 branches mergees, le CLI lance les 3 modules.

---

## Etape 6 — Tests E2E (~1h)

**Qui :** Tous ensemble
**Prerequis :** Etape 5 terminee
**Reference :** `DECISIONS.md` section 6.2 (checklist "Integration")

- [ ] Menu CLI affiche les 3 modules
- [ ] Module 1 : diagnostic DC01 → JSON OK
- [ ] Module 1 : diagnostic WMS-DB → JSON OK
- [ ] Module 2 : backup wms → fichier .sql + SHA256
- [ ] Module 2 : export CSV shipments + inventory
- [ ] Module 3 : scan reseau → detecte les 2 VMs
- [ ] Module 3 : audit EOL → rapport trie par criticite
- [ ] Logs ecrits dans `output/logs/`
- [ ] Exit codes corrects (`echo $?`)
- [ ] (Bonus) Tester sur Windows ET Linux

### Si un bug est trouve

- Creer une branche `fix/<description>`
- Corriger, PR, merge rapide
- Re-tester

**Fini quand :** Toute la checklist est verte. Commit : `chore: e2e validation passed`

---

## Etape 7 — Documentation (~2h)

**Qui :** Reparti selon decisions (Theme 7.1)
**Prerequis :** Etape 6 terminee (code stable)

### Documents a produire

- [ ] `docs/document_technique.md` — Architecture, stack, format JSON, diagrammes
- [ ] `docs/manuel_utilisation.md` — Installation, configuration, utilisation pas a pas
- [ ] `docs/rapport_audit.md` — Sortie du module audit, analyse, recommandations
- [ ] Resume en anglais (integre dans le document technique ou separe)
- [ ] `README.md` — Quick start, liens vers la doc

### Regles

- Chacun documente **son module** (le dev connait le mieux)
- Le Lead assemble et uniformise
- Commit : `docs: add technical documentation`

**Fini quand :** Tous les documents sont dans le repo et relus par au moins 1 autre personne.

---

## Etape 8 — Preparation soutenance (~45 min)

**Qui :** Tous
**Prerequis :** Etape 7 terminee

- [ ] Creer les slides (repartition Theme 7.3 de `DECISIONS.md`)
- [ ] Preparer le script de demo (voir `DECISIONS.md` section 7.2)
- [ ] Verifier que le lab est UP
- [ ] Preparer un **backup de la demo** : screenshots ou video au cas ou le lab plante
- [ ] Tag `v1.0` sur main : `git tag -a v1.0 -m "Release soutenance"`
- [ ] Push tag : `git push origin v1.0`

**Fini quand :** Slides pretes, demo testee 1 fois, tag `v1.0` pousse.

---

## Etape 9 — Repetition + Soutenance (~15 min + presentation)

**Qui :** Tous
**Prerequis :** Etape 8 terminee

- [ ] Repetition complete : 20 min chrono
- [ ] Chacun connait sa partie (voir repartition Theme 7.3)
- [ ] Anticiper les questions du jury :
  - Pourquoi `mysqldump` plutot que replication ?
  - Comment gerez-vous le cross-platform ?
  - Que feriez-vous avec plus de temps ?
  - Securite des credentials ?
- [ ] Verifier que le lab demarre rapidement
- [ ] Avoir le plan B (screenshots) pret

**Fini quand :** La soutenance est terminee !

---

## Resume des temps

| Etape | Duree | Cumul |
|-------|-------|-------|
| 0 — Reunion decisions | 1h | 1h |
| 1 — Setup lab | 2h | 3h |
| 2 — Validation lab | 30 min | 3h30 |
| 3 — Dev parallele | 10h | 13h30 |
| 4 — Tests pre-merge | 30 min | 14h |
| 5 — Integration merge | 1h30 | 15h30 |
| 6 — Tests E2E | 1h | 16h30 |
| 7 — Documentation | 2h | 18h30 |
| 8 — Prep soutenance | 45 min | 19h15 |
| 9 — Repetition | ~15 min | ~19h30 |

> **Marge : quasi nulle.** Si le lab prend trop de temps, reduire la doc.
> **Priorite absolue : code fonctionnel > documentation > slides.**

---

*Voir `DECISIONS.md` pour les choix techniques | `PLAN_PROJET.md` pour les details complets | `QUICKREF.md` pour l'aide-memoire dev*
