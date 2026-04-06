# Plan de Soutenance — NTL-SysToolbox (v6, 16 slides)

> **Durée** : 20 min de présentation + 30 min de questions
> **Public** : 2 jurys pros qui jouent le rôle de la DSI de NTL
> **Ton** : professionnel, on parle à un client, pas à un prof
> **Démo** : obligatoire (intégrée ou pendant les questions)
> **Métriques** : 110 tests, ~2500 lignes de code, 62 commits, 5 VMs

---

## Répartition équipe

| Slide(s) | Titre | Qui | Durée |
|----------|-------|-----|-------|
| 1 | Titre | Ianis | 30s |
| 2 | Contexte — NordTransit Logistics | Ianis | 1min30 |
| 3 | Problématique | Ianis | 1min30 |
| 4 | Notre solution | Ianis | 1min |
| 5 | Organisation de l'équipe | Ianis | 1min |
| 6 | Architecture | Ianis | 1min30 |
| 7 | Module Diagnostic | Blaise | 1min30 |
| 8 | Module Backup | Ojvind | 1min30 |
| 9 | Module Audit | Zaid | 1min30 |
| 10 | Environnement de test | Ianis | 45s |
| 11 | Intégration continue | Ianis | 45s |
| 12 | Démo live | Tous (Ianis pilote) | 4min |
| 13 | Documentation | Ianis | 1min |
| 14 | Difficultés & compromis | Ianis + équipe | 1min30 |
| 15 | Bilan & perspectives | Ianis | 1min30 |
| 16 | Questions | Tous | 30min |

**Total présentation** : ~19 min (1 min de marge)

---

## Slide 1 — Titre

**Visuel** : Logo NTL + nom outil + noms équipe

```
NTL-SysToolbox
Outil CLI d'administration système pour NordTransit Logistics

Ianis (Lead) — Blaise — Ojvind — Zaid
MSPR TPRE511 — EPSI — 2026
```

> **Notes speaker** : Pas de blabla. "Bonjour, nous sommes l'équipe X, nous allons
> vous présenter NTL-SysToolbox, un outil que nous avons développé pour répondre
> aux besoins de la DSI de NordTransit Logistics."

---

## Slide 2 — Contexte NTL

**Visuel** : Carte Hauts-de-France avec les 4 sites + chiffres clés

**Contenu** :
- PME logistique, siège Lille + 3 entrepôts (Lens, Valenciennes, Arras)
- ~240 employés, jusqu'à 300 en haute saison
- WMS (système d'entrepôt) = coeur de métier, arrêt = arrêt des opérations
- Équipe IT de 4 personnes (responsable, admin, technicien, alternant)
- Fenêtres de maintenance courtes (nuit uniquement)

> **Notes speaker** : Planter le décor rapidement. Le jury doit comprendre que NTL
> est une PME avec une infra critique mais une équipe IT réduite.
> "NTL est une entreprise de logistique dans les Hauts-de-France. Le système
> d'entrepôt tourne 13h par jour, son arrêt bloque les 4 sites immédiatement.
> L'équipe IT ne compte que 4 personnes pour gérer tout ça."

---

## Slide 3 — Problématique

**Visuel** : 3 colonnes avec icône + problème → mapping vers les modules

| Supervision | Sauvegardes | Obsolescence |
|-------------|-------------|--------------|
| Surtout technique (ping, disque) | Scripts + NAS, jamais testées | Aucun inventaire EOL |
| Pas orientée "service" | Pas d'objectif RPO/RTO | OS en fin de vie non identifiés |
| AD, DNS, MySQL non surveillés | Pas de vérification d'intégrité | Risque de faille non maîtrisé |
| → **Module Diagnostic** | → **Module Backup** | → **Module Audit** |

> **Notes speaker** : "La DSI nous a mandé pour répondre à 3 problèmes concrets :
> la supervision ne couvre pas les services métier, les sauvegardes ne sont pas
> vérifiées, et personne ne sait quels OS sont en fin de vie sur le parc."
>
> **Compétence ciblée** : Poser le besoin métier pour justifier chaque module.

---

## Slide 4 — Notre solution

**Visuel** : Schéma simple — 1 outil CLI Python, 3 modules, sorties exploitables

**Contenu** :
- **NTL-SysToolbox** : CLI Python, menu interactif
- 3 modules indépendants : Diagnostic, Backup, Audit
- Sorties JSON horodatées + codes retour standard (0-3)
- Configuration YAML + secrets via variables d'environnement
- Compatible Windows et Linux (cross-platform)

**Points clés à faire passer** :
- "On a choisi Python pour la portabilité et l'écosystème de libs sys/réseau"
- "Les codes retour permettent une intégration future avec Zabbix ou tout outil de supervision"
- "La config est séparée du code — la DSI peut adapter sans toucher au code"

> **Notes speaker** : C'est LA slide de synthèse. Le jury doit retenir : 1 outil,
> 3 modules, JSON + codes retour = exploitable en supervision.
>
> **Compétences** : BC01.9 (rationnaliser via scripts), BC03.9 (alertes/codes retour)

---

## Slide 5 — Organisation de l'équipe

**Visuel** : Tableau des membres + méthode + workflow Git en 4 étapes

**Contenu** :
- Tableau des rôles : Ianis (Lead/Archi), Blaise (Diagnostic), Ojvind (Backup), Zaid (Audit)
- Méthode : contrat JSON commun défini en amont → développement parallèle
- Workflow Git : branch feature → PR → review Lead → squash merge master
- 62 commits, branches isolées par module

> **Notes speaker** : "On a défini le contrat JSON commun dès le départ, ce qui
> nous a permis de travailler en parallèle sur nos modules respectifs. Chaque merge
> passe par une review du Lead pour garantir la cohérence."

---

## Slide 6 — Architecture

**Visuel** : Schéma main.py → modules → build_result() + tableau des 8 champs JSON

```
Utilisateur (terminal)
       |
   main.py (menu interactif)
       |
  +---------+---------+
  |         |         |
Diagnostic  Backup    Audit
  |         |         |
  +----+----+---------+
       |
  build_result() → JSON standard
       |
  +----+----+
  |         |
Terminal  output/logs/
(rich)    fichiers JSON
```

**Tableau des 8 champs JSON** :

| Champ | Description |
|-------|-------------|
| module | Nom du module (diagnostic, backup, audit) |
| function | Nom de la fonction appelée |
| timestamp | Horodatage ISO 8601 |
| status | OK, WARNING, CRITICAL, UNKNOWN |
| exit_code | 0, 1, 2, 3 |
| target | Cible vérifiée (IP, base, etc.) |
| details | Données techniques détaillées |
| message | Message lisible par un humain |

**Points clés** :
- Exit codes : 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN
- Seuils WARNING à 80% (CPU, RAM, disque) — norme industrie
- Chaque module est indépendant, même signature `run(config, target, action=...)`

> **Notes speaker** : "L'architecture est volontairement simple. Chaque module est
> indépendant mais respecte le même contrat de sortie. Ça veut dire que la DSI peut
> intégrer n'importe quel résultat dans sa supervision existante, parce que le
> format est toujours le même."
>
> **Compétences** : BC03.9 (alertes exploitables), BC01.9 (automatisation)

---

## Slide 7 — Module Diagnostic (Blaise)

**Visuel** : Tableau des 4 fonctions + schéma de décision pour check_ad_dns

| Fonction | Cible | Ce qu'elle vérifie |
|----------|-------|--------------------|
| `check_ad_dns` | DC01 | Ports LDAP/DNS/Kerberos + résolution DNS + connectivité LDAP |
| `check_mysql` | WMS-DB | Port 3306 + version MySQL (sans auth) |
| `check_linux` | Tout serveur | Scan multi-ports, catégorisation des services actifs |
| `check_http` | Tout serveur web | Status HTTP, header Server, temps de réponse |

**Exemple de décision** :
```
LDAP OK + DNS OK         → OK (0)
LDAP OK + DNS KO         → WARNING (1)
LDAP KO                  → CRITICAL (2)
DC01 injoignable         → UNKNOWN (3)
```

**Libs utilisées** : dnspython, ldap3, socket

> **Notes speaker (Blaise)** : "Mon module répond à la question : est-ce que les
> services critiques du siège fonctionnent ? Pour chaque vérification, j'ai une
> logique de décision claire qui produit un status et un code retour exploitable."
>
> Montrer qu'on comprend POURQUOI on teste ces services (AD = auth de tout le monde,
> DNS = résolution de noms, MySQL = WMS).
>
> **Compétences** : BC02.7 (supervision), BC03.9 (évaluation perturbations)

---

## Slide 8 — Module Backup (Ojvind)

**Visuel** : Schéma du flux backup_database + tableau des 2 fonctions + 4 mesures sécurité

| Fonction | Ce qu'elle fait | Sortie |
|----------|-----------------|--------|
| `backup_database` | mysqldump local ou via SSH (fallback) | `output/backups/wms_YYYYMMDD_HHMMSS.sql` |
| `export_table_csv` | SELECT * → fichier CSV | `output/exports/table_YYYYMMDD_HHMMSS.csv` |

**4 mesures de sécurité** :
1. Mot de passe MySQL passé via variable d'env (`MYSQL_PWD`), jamais en argument CLI
2. Validation du nom de table (regex) → protection injection SQL
3. Protection path traversal (pas de `..` dans les chemins)
4. Fallback SSH si mysqldump pas disponible localement

> **Notes speaker (Ojvind)** : "Mon module permet à la DSI de lancer une sauvegarde
> de la base WMS à tout moment. Le dump est fait via mysqldump, avec un fallback SSH
> si l'outil n'est pas installé localement. J'ai porté une attention particulière à
> la sécurité : les mots de passe ne transitent jamais en argument de commande."
>
> Si le jury demande pourquoi pas de compression : "C'est un choix d'équipe, on a
> privilégié la simplicité et la lisibilité du dump pour une première version."
>
> **Compétences** : BC01.11 (automatisation sauvegarde)

---

## Slide 9 — Module Audit (Zaid)

**Visuel** : Pipeline 4 étapes + tableau entrée/sortie

```
scan_network → list_os_eol → audit_from_csv → generate_report
(nmap)         (JSON local)   (croisement)     (rapport trié)
```

| Fonction | Entrée | Sortie |
|----------|--------|--------|
| `scan_network` | Plage IP (ex: 192.168.10.0/24) | Machines détectées + ports + OS |
| `list_os_eol` | Base EOL locale (JSON) | Liste des dates de fin de support |
| `audit_from_csv` | Inventaire CSV (hostname, OS, version) | Croisement avec dates EOL |
| `generate_report` | Résultats combinés | Rapport JSON + tableau coloré terminal |

**Exemple de sortie rapport** :
```
EXPIRÉ   | SRV-PRINT  | Win Server 2008 R2 | EOL: jan 2020 | -2285 jours
EXPIRÉ   | PC-QUAI    | Windows 7          | EOL: jan 2020 | -2285 jours
BIENTÔT  | SRV-FILE   | Win Server 2012 R2 | EOL: oct 2026 | +183 jours
OK       | DC01       | Win Server 2022    | EOL: oct 2031 | +2024 jours
```

> **Notes speaker (Zaid)** : "Mon module répond à la question : quels équipements
> du parc sont obsolètes et représentent un risque ? Le scan réseau détecte les
> machines, puis on croise avec notre base de dates de fin de vie pour produire
> un rapport classé par urgence."
>
> Si le jury demande la source des dates EOL : "On utilise une base JSON locale
> maintenue manuellement, basée sur les dates officielles Microsoft et Ubuntu.
> C'est un compromis : pas de dépendance réseau, mais nécessite une mise à jour
> périodique."
>
> **Compétences** : BC01.4 (identifier systèmes à corriger), BC02.8 (recenser ressources)

---

## Slide 10 — Environnement de test

**Visuel** : Schéma du lab Proxmox avec les 5 VMs

| VM | OS | Rôle | IP |
|----|------|------|-----|
| DC01 | Windows Server 2022 | AD/DNS | 192.168.10.10 |
| WMS-DB | Ubuntu 20.04 | MySQL | .21 |
| WMS-APP | Ubuntu 22.04 | Applicatif | .22 |
| SRV-OLD | Windows Server 2012 R2 | EOL test | .12 |
| SRV-LEGACY | Ubuntu 18.04 | EOL test | .18 |

- Proxmox VE avec 5 VMs reproduisant l'infra NTL
- Permet de tester en conditions réelles sans toucher à la prod

> **Notes speaker (Ianis)** : "Pour valider notre outil, on a monté un lab Proxmox
> qui reproduit l'infra NTL avec 5 VMs couvrant Windows Server, Ubuntu, et des
> machines volontairement obsolètes pour tester le module Audit."

---

## Slide 11 — Intégration continue

**Visuel** : Pipeline GitHub Actions — 2 jobs parallèles + métriques

**CI/CD (GitHub Actions)** :
- Déclenchement : push sur master/feature/*, PR sur master
- **Job 1** : Lint (ruff) + Types (mypy) — en parallèle
- **Job 2** : Tests (pytest) sur Python 3.10, 3.11, 3.12 — en parallèle
- **Métriques** : 110 tests, couverture minimum 50%

> **Notes speaker (Ianis)** : "Chaque push déclenche notre pipeline CI qui vérifie
> la qualité du code et lance 110 tests sur 3 versions de Python en parallèle."
>
> **Compétences** : BC02.7 (supervision/qualité)

---

## Slide 12 — Démo live

**Scénario** (4 minutes, Ianis pilote, chacun commente son module) :

### Étape 1 — Lancement du menu (Ianis, 30s)
```bash
python src/main.py
# Menu principal s'affiche
```
"Voici le menu interactif. La DSI peut naviguer sans documentation."

### Étape 2 — Diagnostic AD/DNS (Blaise, 1 min)
```
Choix 1 → Diagnostic
Choix 1 → Vérifier AD/DNS
IP : [Entrée pour défaut]
→ Résultat JSON : status OK/CRITICAL
```
"On vérifie que l'AD et le DNS du DC01 sont opérationnels."

### Étape 3 — Backup BDD (Ojvind, 1 min)
```
Choix 2 → Backup
Choix 1 → Backup base de données
Base : [Entrée pour défaut = wms]
→ Résultat : fichier SQL créé, taille, chemin
```
"On sauvegarde la base WMS. Le fichier est horodaté et prêt à être archivé."

### Étape 4 — Audit EOL (Zaid, 1 min)
```
Choix 3 → Audit
Choix 2 → Lister dates EOL
→ Résultat : tableau des OS avec jours restants
```
"On identifie immédiatement les OS en fin de vie."

### Étape 5 — Résultats (Ianis, 30s)
```
Choix 0 → Quitter
Montrer le fichier JSON généré dans output/logs/
```
"Tous les résultats sont sauvegardés en JSON horodaté, exploitables par la supervision."

> **IMPORTANT** : Préparer un plan B si le lab n'est pas accessible :
> - Screenshots/vidéo de la démo enregistrée
> - Fichiers JSON de sortie pré-générés à montrer

---

## Slide 13 — Documentation

**Visuel** : 6 livrables avec checkmarks + arborescence docs/ (12 fichiers)

**Livrables produits** :
- [x] **Dossier technique** : architecture, choix technologiques, gestion des secrets
- [x] **Guide d'installation** : setup en 5 commandes (clone, venv, deps, config, run)
- [x] **10 docs numérotées** : de getting-started à lab-infra
- [x] **Cheatsheet** : aide-mémoire 1 page pour l'équipe
- [x] **Rapport CI** : pipeline, couverture, résultats
- [x] **Arborescence docs/** : 12 fichiers organisés et indexés

**Points forts** :
- La DSI peut déployer et utiliser l'outil sans assistance (comme demandé)
- Documentation versionnée avec le code (dans le repo Git)
- ~2500 lignes de code documenté

> **Notes speaker** : "Notre documentation couvre l'installation, l'utilisation et
> l'architecture. Un administrateur qui récupère le repo peut déployer l'outil en
> moins de 5 minutes en suivant le guide."
>
> **Compétence** : BC04.2 (documentation technique)

---

## Slide 14 — Difficultés & compromis

**Visuel** : Tableau 5 difficultés/approches

| Difficulté | Notre approche |
|------------|----------------|
| Portabilité Windows/Linux | Python + libs cross-platform, tests CI sur Ubuntu |
| Accès WinRM optionnel | Fallback gracieux — fonctionne sans, mais signale le manque |
| Base EOL locale vs API externe | JSON local = pas de dépendance réseau, mais maintenance manuelle |
| 4 devs, 19h, modules interdépendants | Contrat JSON commun défini en amont → développement parallèle |
| Sécurité des credentials | Variables d'env + .env, jamais de secret dans le code ou les logs |

> **Notes speaker** : "On assume nos compromis. Par exemple, la base EOL est locale
> plutôt qu'une API en ligne. C'est moins dynamique, mais ça évite une dépendance
> réseau pour un outil qui doit fonctionner même en cas de panne."
>
> Le jury apprécie les compromis ASSUMÉS. Ne pas dire "on n'a pas eu le temps",
> dire "on a choisi X parce que Y".

---

## Slide 15 — Bilan & perspectives

**Visuel** : 7 objectifs avec checkmarks + 5 perspectives + métriques

**Objectifs atteints** :
- [x] 3 modules fonctionnels et indépendants
- [x] Menu CLI interactif
- [x] Sorties JSON horodatées + codes retour supervision
- [x] Configuration YAML + gestion secrets
- [x] CI/CD avec lint, types, 110 tests
- [x] Documentation complète (12 fichiers)
- [x] Lab Proxmox 5 VMs opérationnel

**Métriques finales** : 110 tests, ~2500 lignes, 62 commits, 5 VMs

**Perspectives (si NTL veut aller plus loin)** :
- Intégration Zabbix/supervision (les codes retour sont déjà compatibles)
- Planification automatique des backups (cron/Task Scheduler)
- Mise à jour automatique de la base EOL via API
- Extension aux sites distants (WH1, WH2, WH3)
- Dashboard web pour visualiser les résultats

> **Notes speaker** : "On a livré un outil fonctionnel qui répond au cahier des charges.
> Les perspectives montrent que l'architecture est pensée pour évoluer — les codes
> retour standard permettent déjà une intégration supervision sans modification."

---

## Slide 16 — Questions

**Visuel** : Sobre, titre + contacts

```
Merci pour votre attention.
Nous sommes prêts pour vos questions.
```

---

## Aide — Questions probables du jury

### Sur l'architecture
- **"Pourquoi Python et pas Bash/PowerShell ?"** → Portabilité Win+Linux, écosystème de libs (paramiko, nmap, ldap3), maintenabilité par l'équipe IT
- **"Pourquoi des codes retour 0-3 ?"** → Convention Nagios/Zabbix, standard industrie pour les checks de supervision
- **"Comment la config gère les secrets ?"** → Variables d'env via .env, substitution ${VAR}, jamais de secret en dur

### Sur les modules
- **"Que se passe-t-il si MySQL ne répond pas ?"** → Status CRITICAL (code 2), erreur dans details, message lisible
- **"Votre scan réseau nécessite-t-il les droits root ?"** → Détection auto, scan dégradé sans root avec WARNING
- **"Comment vous gérez un backup qui échoue ?"** → Status CRITICAL, pas de fichier corrompu laissé en place
- **"La base EOL, elle vient d'où ?"** → Données Microsoft/Ubuntu officielles, fichier JSON versionné avec le code

### Sur l'équipe
- **"Comment vous vous êtes répartis le travail ?"** → Contrat JSON commun défini ensemble, puis branches isolées par module, merge par le lead
- **"Quelle a été la plus grosse difficulté ?"** → Chacun répond selon son module (préparer individuellement)

### Sur la CI
- **"Pourquoi 3 versions de Python ?"** → La DSI peut avoir différentes versions installées, on garantit la compatibilité
- **"Quel est le taux de couverture ?"** → Seuil minimum 50%, focus sur les chemins critiques, 110 tests

### Pièges à éviter
- Ne PAS dire "on n'a pas eu le temps" → dire "on a priorisé X"
- Ne PAS dire "c'est un projet scolaire" → on parle à la DSI de NTL
- Ne PAS lire les slides — les connaître
- Chacun doit pouvoir expliquer son module ET le contrat commun
