# Workflow NTL-SysToolbox — Guide linéaire

> Ce document se lit **de haut en bas**, étape par étape.
> Chaque étape a des prérequis et une définition de "fini".
> Cochez les cases au fur et à mesure.
>
> **Temps total prévu : 19h | Marge : quasi nulle**
> **Priorité absolue : code fonctionnel > documentation > slides**
>
> **Voir aussi :** [PLAN_PROJET.md](PLAN_PROJET.md) pour les détails techniques | [QUICKREF.md](QUICKREF.md) pendant le dev | [GUIDE_EQUIPE.md](GUIDE_EQUIPE.md) pour les issues GitHub

---

## Étape 0 — Réunion d'équipe (~1h)

**Qui :** Tous (4 personnes)
**Quand :** Début du projet, avant toute ligne de code
**Prérequis :** Avoir lu [PLAN_PROJET.md](PLAN_PROJET.md) en diagonale (sections 1 et 2)
**Document support :** `_specs/DECISIONS.md`

### Déroulement

1. [ ] Nommer un **scribe** (remplit les colonnes "Décision")
2. [ ] **Tier 1 (5 min)** — Validations rapides : lire chaque reco, vote main levée
   - Thèmes : 1.2 (Git), 2.1 (JSON), 2.4 (Signature), 3.2 (Préfixe env)
3. [ ] **Tier 2 (15 min)** — Choix techniques : présenter la reco, discuter si désaccord
   - Thèmes : 2.2 (Seuils), 2.3 (Erreurs), 3.1 (Config), 4.1-4.3 (Modules), 6.3 (Plan B)
4. [ ] **Tier 3 (30 min)** — Organisation équipe
   - Thème 1.1 : Répartition des rôles → écrire les noms
   - Thème 1.3 : Canal Discord/autre, outil de suivi
   - Thème 5.1 : Qui monte DC01 ? Qui monte WMS-DB ? Deadline ?
   - Thème 6.1 : Date du merge collectif, date du code freeze
   - Thème 7.1 : Répartition docs (noter les noms, on y reviendra en étape 7)
   - Thème 7.3 : Répartition soutenance (idem)
5. [ ] Remplir le **tableau récapitulatif** en bas de DECISIONS.md
6. [ ] Commit : `docs: decisions equipe validees`

**Fini quand :** Toutes les colonnes "Décision" sont remplies. Chacun connaît son rôle et ses fichiers.

---

## Étape 1 — Setup du lab (~2h, parallélisable)

**Qui :** Réparti selon les décisions (Thème 5.1)
**Prérequis :** Étape 0 terminée
**Référence :** [PLAN_PROJET.md](PLAN_PROJET.md) sections 1.1 à 1.3

### Track A — DC01 (personne désignée)

- [ ] Installer Windows Server 2022 (VM)
- [ ] IP statique : 192.168.10.10
- [ ] Installer le rôle AD DS, créer le domaine `ntl.local`
- [ ] Configurer DNS
- [ ] Vérifier que le port 389 (LDAP) est ouvert

### Track B — WMS-DB (personne désignée)

- [ ] Installer Ubuntu 20.04 (VM)
- [ ] IP statique : 192.168.10.21
- [ ] Installer MySQL Server
- [ ] Créer la base `wms` + tables (script SQL dans [PLAN_PROJET.md](PLAN_PROJET.md) section 1)
- [ ] Créer un utilisateur MySQL dédié (pas root !)
- [ ] Activer SSH

### Track C — Pendant ce temps (Lead + personne libre)

- [ ] Cloner le repo, `make setup`, vérifier que le venv fonctionne
- [ ] Copier `config.example.yaml` → `config/config.yaml`, remplir les IPs
- [ ] Copier `.env.example` → `.env`, remplir les credentials
- [ ] Vérifier : `python src/main.py` lance sans crash (même si menu vide)

**Fini quand :** Les 2 VMs tournent et le PC client peut les pinger.

---

## Étape 2 — Validation du lab (~30 min, tous ensemble)

**Qui :** Tous
**Prérequis :** Étape 1 terminée
**Référence :** `DECISIONS.md` section 5.2 (checklist)

Parcourir la checklist ensemble :

- [ ] **DC01 :** ping OK, LDAP 389 OK, DNS résolution `ntl.local` OK
- [ ] **WMS-DB :** ping OK, SSH OK, MySQL connexion OK, base `wms` avec données
- [ ] **Réseau :** toutes les machines se voient
- [ ] **Client :** le CLI s'exécute sans erreur

> **BLOQUANT :** Ne pas commencer le dev (étape 3) tant que cette checklist n'est pas verte.

**Fini quand :** Toutes les cases cochées. Screenshot ou log de validation partagé sur le canal de com.

---

## Étape 3 — Développement parallèle (~10h)

**Qui :** Chacun sur sa branche
**Prérequis :** Étape 2 terminée + lab fonctionnel
**Référence :** [PLAN_PROJET.md](PLAN_PROJET.md) section 2 (fiches par personne), `_specs/QUICKREF.md`

### Règles communes

- Créer sa branche : `git checkout -b feature/module-<nom>`
- Copier `src/modules/_template.py` → `src/modules/<nom>.py`
- Chaque fonction retourne `build_result(...)` — voir `src/interfaces.py`
- Commit régulier : `feat: add check_ad_dns()`
- **Message sur le canal si bloqué > 30 min**

### Track Lead

- [ ] Coder `src/main.py` : menu interactif (choix module → choix fonction)
- [ ] Coder `src/config_loader.py` : charge YAML + surcharge `.env`
- [ ] Compléter `src/utils/network.py` si besoin (helpers ping, port check)
- [ ] Tester le menu avec le module template (dry run)
- [ ] Être disponible pour débloquer les autres

### Track Diagnostic (Personne B)

- [ ] `check_ad_dns()` : LDAP port 389 + DNS résolution via `dnspython`
- [ ] `check_mysql()` : connexion + `SHOW DATABASES` + `SHOW STATUS`
- [ ] `check_windows_server()` : métriques CPU/RAM/disque via `wmic`
- [ ] `check_ubuntu()` : SSH + `lsb_release`, `uptime`, `free`, `df`
- [ ] `run()` : dispatcher vers les 4 fonctions selon kwargs
- [ ] Tester chaque fonction individuellement sur le lab

### Track Backup (Personne C)

- [ ] `backup_database()` : `mysqldump` via subprocess, fichier nommé
- [ ] SHA256 automatique après dump
- [ ] `export_table_csv()` : SELECT → CSV pour `shipments` et `inventory`
- [ ] `run()` : dispatcher vers les fonctions
- [ ] Tester sur le lab : vérifier fichiers dans `output/backups/`

### Track Audit (Personne D)

- [ ] Créer `data/eol_database.json` avec les dates EOL connues
- [ ] Créer `data/sample_inventory.csv` avec l'inventaire NTL
- [ ] `scan_network()` : nmap avec détection de privilèges
- [ ] `list_os_eol()` : lecture du JSON EOL
- [ ] `audit_from_csv()` : croisement CSV + EOL
- [ ] `generate_report()` : JSON + tableau rich, tri par criticité
- [ ] Tester sur le lab : scan détecte DC01 + WMS-DB

**Fini quand :** Chaque dev a toutes ses cases cochées et a poussé sa branche.

---

## Étape 4 — Tests pré-merge (~30 min, chacun)

**Qui :** Chaque dev sur sa branche
**Prérequis :** Son module est codé (étape 3 terminée pour soi)
**Référence :** `DECISIONS.md` section 6.2 (checklist pré-merge par module)

- [ ] Parcourir la checklist de **son module** dans `DECISIONS.md` section 6.2
- [ ] Toutes les fonctions retournent le format JSON commun
- [ ] Gestion d'erreur : timeout/host down → UNKNOWN, pas de crash
- [ ] Fichiers écrits dans le bon dossier (`output/logs`, `backups`, `reports`)
- [ ] Commit final : `feat: module <nom> ready for merge`
- [ ] Ouvrir une **PR vers main**

**Fini quand :** PR ouverte, tous les tests du module passent sur le lab.

---

## Étape 5 — Intégration / merge (~1h30)

**Qui :** Lead + tous en support
**Prérequis :** Toutes les PRs ouvertes (étape 4)
**Référence :** `DECISIONS.md` section 6.1

### Ordre de merge (décidé en étape 0)

1. [ ] Merge PR `feature/cli-menu` (Lead)
2. [ ] Merge PR `feature/module-diagnostic`
3. [ ] Merge PR `feature/module-backup`
4. [ ] Merge PR `feature/module-audit`

### Après chaque merge

- [ ] `git pull` sur main
- [ ] `python src/main.py` → vérifier que le menu fonctionne
- [ ] Le nouveau module apparaît et s'exécute sans crash

### Si conflit

- Le Lead résout les conflits
- Si conflit dans un module : appeler le dev concerné

**Fini quand :** `main` contient les 4 branches mergées, le CLI lance les 3 modules.

---

## Étape 6 — Tests E2E (~1h)

**Qui :** Tous ensemble
**Prérequis :** Étape 5 terminée
**Référence :** `DECISIONS.md` section 6.2 (checklist "Intégration")

- [ ] Menu CLI affiche les 3 modules
- [ ] Module 1 : diagnostic DC01 → JSON OK
- [ ] Module 1 : diagnostic WMS-DB → JSON OK
- [ ] Module 2 : backup wms → fichier .sql + SHA256
- [ ] Module 2 : export CSV shipments + inventory
- [ ] Module 3 : scan réseau → détecte les 2 VMs
- [ ] Module 3 : audit EOL → rapport trié par criticité
- [ ] Logs écrits dans `output/logs/`
- [ ] Exit codes corrects (`echo $?`)
- [ ] (Bonus) Tester sur Windows ET Linux

### Si un bug est trouvé

- Créer une branche `fix/<description>`
- Corriger, PR, merge rapide
- Re-tester

**Fini quand :** Toute la checklist est verte. Commit : `chore: e2e validation passed`

---

## Étape 7 — Documentation (~2h)

**Qui :** Réparti selon décisions (Thème 7.1)
**Prérequis :** Étape 6 terminée (code stable)

### Documents à produire

- [ ] `docs/document_technique.md` — Architecture, stack, format JSON, diagrammes
- [ ] `docs/manuel_utilisation.md` — Installation, configuration, utilisation pas à pas
- [ ] `docs/rapport_audit.md` — Sortie du module audit, analyse, recommandations
- [ ] Résumé en anglais (intégré dans le document technique ou séparé)
- [ ] `README.md` — Quick start, liens vers la doc

### Règles

- Chacun documente **son module** (le dev connaît le mieux)
- Le Lead assemble et uniformise
- Commit : `docs: add technical documentation`

**Fini quand :** Tous les documents sont dans le repo et relus par au moins 1 autre personne.

---

## Étape 8 — Préparation soutenance (~45 min)

**Qui :** Tous
**Prérequis :** Étape 7 terminée

- [ ] Créer les slides (répartition Thème 7.3 de `DECISIONS.md`)
- [ ] Préparer le script de démo (voir `DECISIONS.md` section 7.2)
- [ ] Vérifier que le lab est UP
- [ ] Préparer un **backup de la démo** : screenshots ou vidéo au cas où le lab plante
- [ ] Tag `v1.0` sur main : `git tag -a v1.0 -m "Release soutenance"`
- [ ] Push tag : `git push origin v1.0`

**Fini quand :** Slides prêtes, démo testée 1 fois, tag `v1.0` poussé.

---

## Étape 9 — Répétition + Soutenance (~15 min + présentation)

**Qui :** Tous
**Prérequis :** Étape 8 terminée

- [ ] Répétition complète : 20 min chrono
- [ ] Chacun connaît sa partie (voir répartition Thème 7.3)
- [ ] Anticiper les questions du jury :
  - Pourquoi `mysqldump` plutôt que réplication ?
  - Comment gérez-vous le cross-platform ?
  - Que feriez-vous avec plus de temps ?
  - Sécurité des credentials ?
- [ ] Vérifier que le lab démarre rapidement
- [ ] Avoir le plan B (screenshots) prêt

**Fini quand :** La soutenance est terminée !

---

## Résumé des temps

| Étape | Durée | Cumul |
|-------|-------|-------|
| 0 — Réunion décisions | 1h | 1h |
| 1 — Setup lab | 2h | 3h |
| 2 — Validation lab | 30 min | 3h30 |
| 3 — Dev parallèle | 10h | 13h30 |
| 4 — Tests pré-merge | 30 min | 14h |
| 5 — Intégration merge | 1h30 | 15h30 |
| 6 — Tests E2E | 1h | 16h30 |
| 7 — Documentation | 2h | 18h30 |
| 8 — Prép soutenance | 45 min | 19h15 |
| 9 — Répétition | ~15 min | ~19h30 |

> **Marge : quasi nulle.** Si le lab prend trop de temps, réduire la doc.
> **Priorité absolue : code fonctionnel > documentation > slides.**

---

*Voir `DECISIONS.md` pour les choix techniques | [PLAN_PROJET.md](PLAN_PROJET.md) pour les détails complets | `QUICKREF.md` pour l'aide-mémoire dev*
