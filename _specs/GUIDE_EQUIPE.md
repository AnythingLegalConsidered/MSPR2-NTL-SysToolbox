# Guide rapide — Qui fait quoi, sur quelle branche ?

> Ce document explique comment s'organiser avec les issues GitHub.
> Lisez-le une fois, et vous saurez exactement quoi faire.

---

## Les 4 rôles

| Rôle | Branche de travail | Quoi ? |
|------|--------------------|--------|
| **Lead Dev** (Ianis PUICHAUD) | `feature/cli-menu` | Le "chef d'orchestre" : menu CLI, config, utilitaires, merge final |
| **Dev Diagnostic** (Blaise WANDA NKONG) | `feature/module-diagnostic` | Le script qui vérifie que les serveurs fonctionnent |
| **Dev Backup** (Ojvind LANTSIGBLE) | `feature/module-backup` | Le script qui sauvegarde la base de données |
| **Dev Audit** (Zaid ABOUYAALA) | `feature/module-audit` | Le script qui détecte les OS obsolètes |

---

## Comment démarrer

### 1. Cloner le repo (si pas encore fait)

```bash
git clone https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox.git
cd MSPR2-NTL-SysToolbox
```

### 2. Se mettre sur SA branche

```bash
# Exemple pour le Dev Diagnostic :
git checkout feature/module-diagnostic

# Exemple pour le Dev Backup :
git checkout feature/module-backup

# Exemple pour le Dev Audit :
git checkout feature/module-audit

# Exemple pour le Lead :
git checkout feature/cli-menu
```

### 3. Installer les dépendances

```bash
make setup          # Windows (Git Bash)
make setup-linux    # Linux
```

### 4. Aller sur GitHub → Issues → S'assigner ses tâches

Lien : https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox/issues

Cliquer sur une issue → à droite "Assignees" → s'ajouter.

---

## Les 4 phases du projet

```
Phase 1          Phase 2              Phase 3           Phase 4
FONDATIONS  -->  MODULES         -->  INTEGRATION  -->  DOCUMENTATION
(Lead seul)      (3 devs en //)       (tous)            (tous)
~3h              ~10h                 ~3h               ~3h
```

---

## Phase 1 — Fondations (Lead Dev seul)

> Le Lead construit les briques partagées. Les autres attendent que #1 soit fini
> avant de commencer leurs modules (ou commencent par lire la doc/se former).

| Issue | Titre | Fichier à créer | Branche |
|-------|-------|-----------------|---------|
| [#1](../../issues/1) | Config loader | `src/config_loader.py` | `feature/cli-menu` |
| [#2](../../issues/2) | Menu CLI | `src/main.py` | `feature/cli-menu` |
| [#3](../../issues/3) | Utilitaires réseau | `src/utils/network.py` | `feature/cli-menu` |

**Ordre :** #1 d'abord (tout le monde en dépend), puis #2 et #3 en parallèle.

---

## Phase 2 — Développement des modules (3 devs en parallèle)

> Chacun travaille sur SA branche, dans SON fichier. Pas de conflit possible !

### Dev Diagnostic (Blaise WANDA NKONG) → branche `feature/module-diagnostic`

| Issue | Titre | Ce que ça fait |
|-------|-------|----------------|
| [#4](../../issues/4) | `check_ad_dns()` | Vérifie que Active Directory et DNS marchent sur DC01 |
| [#5](../../issues/5) | `check_mysql()` | Vérifie que MySQL répond sur WMS-DB |
| [#6](../../issues/6) | `check_windows_server()` + `check_ubuntu()` | Récupère CPU/RAM/Disque des serveurs |
| [#7](../../issues/7) | `run()` dispatcher | Fonction qui aiguille vers le bon check |
| [#13](../../issues/13) | Tests unitaires | Tests automatisés du module |

**Tout va dans un seul fichier :** `src/modules/diagnostic.py`

**Pour commencer :** Copier `src/modules/_template.py` → `src/modules/diagnostic.py`

### Dev Backup (Ojvind LANTSIGBLE) → branche `feature/module-backup`

| Issue | Titre | Ce que ça fait |
|-------|-------|----------------|
| [#8](../../issues/8) | `backup_database()` | Fait un dump SQL de la base MySQL + calcule le SHA256 |
| [#9](../../issues/9) | `export_table_csv()` + `run()` | Exporte une table en CSV + dispatcher |
| [#14](../../issues/14) | Tests unitaires (partagée avec Audit) | Tests automatisés du module |

**Tout va dans un seul fichier :** `src/modules/backup.py`

**Pour commencer :** Copier `src/modules/_template.py` → `src/modules/backup.py`

### Dev Audit (Zaid ABOUYAALA) → branche `feature/module-audit`

| Issue | Titre | Ce que ça fait |
|-------|-------|----------------|
| [#10](../../issues/10) | Fichiers de données | Créer `data/eol_database.json` et `data/sample_inventory.csv` |
| [#11](../../issues/11) | `scan_network()` | Scanne le réseau avec nmap pour trouver les machines |
| [#12](../../issues/12) | `list_os_eol()` + `audit_from_csv()` + `generate_report()` + `run()` | Croise l'inventaire avec les dates de fin de support, génère un rapport coloré |
| [#14](../../issues/14) | Tests unitaires (partagée avec Backup) | Tests automatisés du module |

**Tout va dans un seul fichier :** `src/modules/audit.py` (+ fichiers `data/`)

**Pour commencer :** Copier `src/modules/_template.py` → `src/modules/audit.py`

---

## Phase 3 — Intégration & Tests (tous ensemble)

> Le Lead merge les branches une par une. Tout le monde est disponible pour aider.

| Issue | Titre | Branche | Qui |
|-------|-------|---------|-----|
| [#15](../../issues/15) | Merge + Tests E2E | `master` | Lead (avec support de tous) |

**Ordre de merge :** `feature/cli-menu` → `feature/module-diagnostic` → `feature/module-backup` → `feature/module-audit`

---

## Phase 4 — Documentation & Livraison (répartition équipe)

| Issue | Titre | Branche | Qui |
|-------|-------|---------|-----|
| [#16](../../issues/16) | Document technique | `master` | Lead + 1 autre |
| [#17](../../issues/17) | Manuel utilisation + README | `master` | 1 personne |
| [#18](../../issues/18) | Rapport audit + Tag v1.0 | `master` | Dev Audit + Lead |

---

## Schéma visuel complet

```
                     master
                       |
          +------------+------------+-----------+
          |            |            |           |
  feature/cli-menu  feature/       feature/    feature/
  (Lead Dev)        module-        module-     module-
                    diagnostic     backup      audit
                    (Blaise)      (Ojvind)   (Zaid)
          |            |            |           |
       #1 config    #4 ad_dns    #8 backup   #10 data
       #2 menu      #5 mysql     #9 csv+run  #11 scan
       #3 network   #6 srv       #13 tests   #12 eol+report
                    #7 run                    #14 tests
                    #13 tests
          |            |            |           |
          +------------+------------+-----------+
                       |
                    #15 MERGE
                    (sur master)
                       |
                 #16 #17 #18
                 Documentation
                       |
                    Tag v1.0
```

---

## Commandes Git utiles

### Avant de coder (chaque session)

```bash
# 1. Se mettre sur sa branche
git checkout feature/module-diagnostic   # (remplacer par ta branche)

# 2. Récupérer les derniers changements du master
git pull origin master
```

### Après avoir codé

```bash
# 1. Voir ce qui a changé
git status

# 2. Ajouter les fichiers modifiés
git add src/modules/diagnostic.py        # (remplacer par ton fichier)

# 3. Commiter avec un message clair
git commit -m "feat: add check_ad_dns()"

# 4. Pousser sur GitHub
git push origin feature/module-diagnostic
```

### Conventions de commit

| Préfixe | Quand l'utiliser | Exemple |
|---------|-----------------|---------|
| `feat:` | Nouvelle fonctionnalité | `feat: add check_mysql()` |
| `fix:` | Correction de bug | `fix: handle timeout in backup` |
| `test:` | Ajout de tests | `test: add diagnostic module tests` |
| `docs:` | Documentation | `docs: add technical documentation` |
| `chore:` | Maintenance | `chore: update requirements.txt` |

---

## Règles importantes

1. **Chacun travaille UNIQUEMENT sur sa branche et ses fichiers**
2. **Ne JAMAIS push directement sur `master`** — on passe par des PRs
3. **Le Lead review toutes les PRs** avant merge
4. **Si bloqué > 30 min** → message immédiat sur le groupe + ping le Lead
5. **Toujours utiliser `build_result()`** pour le format de retour (voir `src/interfaces.py`)
6. **Pas de `print()`** — utiliser `logging` (voir `src/utils/output.py`)
7. **Pas de secrets dans le code** — tout dans `.env`

---

## Questions fréquentes

**Q: Je ne sais pas par où commencer ?**
→ Ouvre ton issue (#4, #8 ou #10 selon ton rôle). Tout est expliqué dedans avec des exemples de code.

**Q: Mon module a besoin du config_loader mais il n'est pas encore fait ?**
→ Commence par lire le template (`_template.py`), comprends la structure, prépare ton code. Dès que #1 est mergé dans master, fais un `git pull origin master` sur ta branche.

**Q: Comment tester sans les VMs du lab ?**
→ Utilise les mocks (simulations) dans les tests. Les issues #13 et #14 expliquent comment.

**Q: J'ai un conflit de merge ?**
→ Appelle le Lead. C'est son rôle de résoudre les conflits (décision d'équipe).

**Q: Mon module n'est pas fini à la deadline ?**
→ Pas de panique. On met un stub "Module non implémenté" dans le menu. L'outil reste fonctionnel (décision d'équipe, DECISIONS.md section 6.3).
