# Corrections & ameliorations — Soutenance v5

> Guide pour passer de v4 a v5. Chaque section = 1 slide.
> Les textes sont prets a copier-coller dans PowerPoint.

---

## GLOBAL — Corrections a appliquer partout

### Contraste texte
- Sous-titres gris : passer de ~#808080 a **#B0B0B0** minimum
- Corps de texte : **#D0D0D0** minimum
- Titres : blanc pur **#FFFFFF** ou couleur accent
- **Tester en projection** avant la soutenance

### Accents manquants (7 corrections)
| Slide | Incorrect | Correct |
|-------|-----------|---------|
| 3 | service metier | service **metier** → **service metier** c'est bon, mais "orientee" → **orientee** ok. Le vrai problème : "→ Module Diagnostic" les fleches sont ok |
| 3 | Pas orientee service metier | Pas orientee service **metier** → **Pas orientee service metier** (en fait c'est "metier" sans accent dans le PPTX) |
| 4 | s'integrer a la supervision | s'integrer **a** → **s'integrer a** OK en fait tous les accents manquent |

Voici la liste exacte des corrections d'accents :

| Slide | Texte actuel | Texte corrige |
|-------|-------------|---------------|
| 3 | "service metier" | "service **metier**" |
| 4 | "s'intégrer a la supervision" | "s'intégrer **a** la supervision" |
| 5 | "le meme contrat" | "le **meme** contrat" |
| 8 | "Quels equipements" | "Quels **equipements**" |
| 12 | "a ete discuté" | "a **ete** discuté" |
| 12 | "developpement parallèle" | "**developpement** parallèle" |
| 13 | "des resultats" | "des **resultats**" |

Bon, c'est plus simple de lister correctement. Voici :

| Slide | Mot fautif | Correction |
|-------|-----------|------------|
| 3 | metier | **metier** |
| 4 | a la supervision | **a** la supervision |
| 5 | meme contrat | **meme** contrat |
| 8 | equipements | **equipements** |
| 12 | ete | **ete** |
| 12 | developpement | **developpement** |
| 13 | resultats | **resultats** |

---

## SLIDE 3 — Problematique (corrections accents)

Texte corrige complet :

**Titre** : Problematique
**Sous-titre** : 3 angles morts identifies dans le SI de NordTransit Logistics

| Colonne 1 | Colonne 2 | Colonne 3 |
|-----------|-----------|-----------|
| **Supervision** | **Sauvegardes** | **Obsolescence** |
| Surtout technique (ping, disque) | Scripts + NAS, jamais testees | Aucun inventaire EOL |
| Pas orientee service **metier** | Pas d'objectif RPO / RTO | OS en fin de vie non identifies |
| AD, DNS, MySQL non surveilles | Aucune verification d'integrite | Risque de faille non maitrise |
| → **Module Diagnostic** | → **Module Backup** | → **Module Audit** |

---

## SLIDE 4 — Notre solution (correction accent)

Corriger : "s'integrer **a** la supervision" → "s'integrer **a** la supervision"

Sous-titre corrige :
> Un outil unique couvrant les 3 besoins, concu pour s'integrer **a** la supervision existante

---

## SLIDE 5 — Architecture (REFONTE COMPLETE)

**Probleme** : Schema ASCII illisible en projection, contrat JSON pas clair.

### Nouveau contenu propose

**Titre** : Architecture
**Sous-titre** : Simple par choix — chaque module est independant mais parle le **meme** langage

**Partie gauche — Schema (faire avec des formes PowerPoint, pas du texte)**

```
┌─────────────────────┐
│   main.py (menu)    │  ← Point d'entree CLI
└─────────┬───────────┘
          │
    ┌─────┼─────┐
    ▼     ▼     ▼
┌──────┐┌──────┐┌──────┐
│ Diag ││Backup││Audit │  ← 3 modules independants
└──┬───┘└──┬───┘└──┬───┘
   └───────┼───────┘
           ▼
┌─────────────────────┐
│   build_result()    │  ← Contrat JSON uniforme
│   → fichier JSON    │
└─────────────────────┘
```

Faire ca avec 5 rectangles arrondis + fleches dans PowerPoint.
Couleurs suggerees :
- main.py : bleu
- Modules : orange/vert/violet (1 couleur par module)
- build_result : gris clair

**Partie droite — Exemple JSON annote**

```json
{
  "module": "diagnostic",
  "function": "check_ad_dns",
  "timestamp": "2026-04-02T14:30:00Z",
  "status": "OK",           ← OK | WARNING | CRITICAL | UNKNOWN
  "exit_code": 0,           ← Compatible Nagios / Zabbix
  "target": "192.168.10.10",
  "details": { ... },
  "message": "AD et DNS operationnels sur DC01"
}
```

**En bas — Une ligne explicative**
> Chaque module retourne le meme format JSON → la DSI peut integrer les resultats dans sa supervision existante sans adaptation.
> Seuils WARNING : CPU / RAM / Disque > 80%  |  Timeout par defaut : 10s

### Ce qui change vs v4
- Plus de schema ASCII
- Exemple JSON avec annotations visuelles (fleches)
- Le jury comprend en 5 secondes : "meme format partout = integreable"

---

## SLIDE 6 — Module Diagnostic (corrections debordement + screenshot)

**Probleme** : texte deborde des cellules du tableau, screenshot fait faux.

### Tableau corrige (texte raccourci)

| Fonction | Cible | Verification |
|----------|-------|-------------|
| check_ad_dns | DC01 | Ports LDAP / DNS / Kerberos + resolution DNS |
| check_mysql | WMS-DB | Port 3306 + version MySQL |
| check_linux | Tout serveur | Scan multi-ports, services actifs |
| check_http | Serveur web | Status HTTP, header Server, temps reponse |

→ Reduire la police du tableau a **11pt** si ca deborde encore.

### Screenshot
Remplacer les fausses fenetres par :
- **Option A** : vrai screenshot depuis Windows Terminal (theme sombre)
- **Option B** : utiliser Carbon (carbon.now.sh) pour generer un rendu propre du JSON
- **Option C** : mettre le JSON directement dans un bloc colore dans le slide (fond #1E1E1E, texte colore)

### Ajout suggere
Ajouter un mini schema de decision sous le tableau :

```
DC01 joignable ?
  ├─ Non → UNKNOWN (3)
  └─ Oui → LDAP OK ?
       ├─ Non → CRITICAL (2)
       └─ Oui → DNS OK ?
            ├─ Non → WARNING (1)
            └─ Oui → OK (0)
```

Ca montre la logique de decision, le jury adore ca.

---

## SLIDE 7 — Module Backup (corrections debordement)

### Tableau corrige

| Fonction | Action | Sortie |
|----------|--------|--------|
| backup_database | Dump SQL via mysqldump (local ou SSH) | output/backups/wms_*.sql |
| export_table_csv | Export table MySQL en CSV | output/exports/table_*.csv |

### Mesures de securite (reformuler en plus court)
- Mot de passe via variable d'env (MYSQL_PWD)
- Validation nom de table (regex anti-injection)
- Protection path traversal
- Fallback SSH si mysqldump absent

---

## SLIDE 8 — Module Audit (corrections debordement + accent)

**Titre corrige** : "Quels **equipements** du parc sont obsoletes et representent un risque ?"

### Pipeline (faire avec des formes PowerPoint, pas du texte)

4 blocs avec fleches :

```
[scan_network] → [list_os_eol] → [audit_from_csv] → [generate_report]
   (nmap)          (JSON local)     (croisement)       (rapport trie)
```

### Tableau corrige (texte raccourci)

| Fonction | Entree | Sortie |
|----------|--------|--------|
| scan_network | Plage IP (CIDR) | Machines + ports + OS |
| list_os_eol | Base JSON locale | Dates fin de support |
| audit_from_csv | Inventaire CSV | Croisement inventaire x EOL |
| generate_report | Resultats combines | Rapport JSON + tableau colore |

---

## SLIDE 9 — Lab & CI/CD (SPLITTER EN 2 SLIDES)

### Slide 9A — Lab de test Proxmox

**Titre** : Environnement de test
**Sous-titre** : Un lab qui reproduit l'infra reelle de NTL pour valider chaque module

**Partie gauche — Schema reseau simplifie**

Faire un mini diagramme avec les VMs :

```
        [Switch virtuel 192.168.10.0/24]
         |        |        |        |        |
      [DC01]   [WMS-DB] [WMS-APP] [SRV-OLD] [SRV-LEGACY]
      Win 2022  Ubuntu   Ubuntu    Win 2012R2  Ubuntu 18
      AD/DNS    MySQL    App WMS   Test EOL    Test EOL
      .10       .21      .22       .12         .18
```

**Partie droite — Explication**

> **Pourquoi un lab ?**
> - Tester en conditions reelles sans toucher a la production
> - Chaque module est valide sur des VMs identiques a l'infra NTL
> - Les VMs legacy (SRV-OLD, SRV-LEGACY) permettent de tester la detection EOL
>
> **Heberge sur** : Proxmox VE (hyperviseur open source)

### Slide 9B — CI/CD GitHub Actions

**Titre** : Integration continue
**Sous-titre** : Chaque commit est verifie automatiquement en moins de 2 minutes

**Schema pipeline (faire avec des formes)**

```
Push / PR sur master ou feature/*
           │
     ┌─────┴─────┐
     ▼           ▼
 [Job 1]      [Job 2]          ← En parallele
 Qualite      Tests
 ─────────    ─────────────
 ruff check   pytest --cov
 mypy src/    Python 3.10
              Python 3.11
              Python 3.12
     │           │
     └─────┬─────┘
           ▼
       ✓ Merge OK
```

**Encart metriques (en bas)**

> **110 tests** | **54% couverture** | **3 versions Python** | **< 2 min par run**

---

## SLIDE 12 — Difficultes (corrections accents)

| Difficulte | Notre approche |
|------------|----------------|
| Portabilite Windows / Linux | Python + libs cross-platform, tests CI sur Ubuntu |
| Acces WinRM optionnel | Fallback gracieux — fonctionne sans, mais signale le manque |
| Base EOL locale vs API externe | JSON local = pas de dependance reseau, mais maintenance manuelle |
| 4 devs, 19h, modules lies | Contrat JSON commun defini en amont → **developpement** parallele |
| Securite des credentials | Variables d'env + .env, zero secret dans le code ou les logs |

Corriger : "a **ete** discute" → "a **ete** discute" dans le sous-titre.

---

## SLIDE 13 — Bilan (corrections + ajout metriques)

**Corriger** : "des **resultats**" → "des **resultats**"

### Ajout : encart metriques du projet

Ajouter un bloc en bas ou en sidebar :

```
Le projet en chiffres
─────────────────────
  62 commits  ·  110 tests  ·  54% couverture
  ~2 500 lignes Python  ·  10 docs  ·  5 VMs lab
  CI : ruff + mypy + pytest x3 versions
```

Ca rassure le jury sur le travail reel fourni.

---

## NOUVELLE SLIDE (optionnelle) — Organisation equipe

A inserer entre slide 4 (Solution) et slide 5 (Architecture), ou apres slide 5.

**Titre** : Organisation de l'equipe
**Sous-titre** : 4 developpeurs, 19 heures, un contrat commun

**Contenu** :

| Membre | Role | Module |
|--------|------|--------|
| Ianis | Lead, architecture, CI/CD, integration | Framework + CLI |
| Blaise | Developpeur module | Diagnostic |
| Ojvind | Developpeur module | Backup |
| Zaid | Developpeur module | Audit |

**Methode de travail** :
- Contrat JSON defini ensemble en amont (interfaces.py)
- 1 branche par module (feature/module-*)
- Pull requests + code review par le Lead
- CI automatique a chaque push
- Merge squash sur master

**Repartition commits** :
Ianis 40 · Blaise 4 · Ojvind 4 · Zaid 3

> Note : la repartition des commits reflete le role de Lead (framework, CI, integration, reviews).
> Le travail de chaque dev est dans son module.

---

## Resume des changements v4 → v5

| # | Action | Impact |
|---|--------|--------|
| 1 | Corriger 7 accents manquants | Slides 3, 4, 5, 8, 12, 13 |
| 2 | Augmenter contraste texte gris | Toutes les slides |
| 3 | Refaire slide 5 (architecture) en formes | Slide 5 |
| 4 | Raccourcir texte tableaux (debordement) | Slides 6, 7, 8 |
| 5 | Remplacer screenshots faux par vrais | Slides 6, 7, 8 |
| 6 | Splitter slide 9 en Lab + CI | Slides 9A, 9B |
| 7 | Ajouter metriques projet | Slide 13 |
| 8 | Ajouter slide Organisation equipe | Nouvelle slide |
