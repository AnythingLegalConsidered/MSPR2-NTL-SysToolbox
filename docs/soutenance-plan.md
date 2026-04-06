# Plan de Soutenance — NTL-SysToolbox

> **Duree** : 20 min de presentation + 30 min de questions
> **Public** : 2 jurys pros qui jouent le role de la DSI de NTL
> **Ton** : professionnel, on parle a un client, pas a un prof
> **Demo** : obligatoire (integree ou pendant les questions)

---

## Repartition equipe

| Slide(s) | Qui | Duree |
|----------|-----|-------|
| 1-3 (Contexte + Problematique) | Ianis | ~3 min |
| 4-5 (Solution + Architecture) | Ianis | ~2 min 30 |
| 6 (Module Diagnostic) | Blaise | ~1 min 30 |
| 7 (Module Backup) | Ojvind | ~1 min 30 |
| 8 (Module Audit) | Zaid | ~1 min 30 |
| 9 (Lab + CI/CD) | Ianis | ~1 min |
| 10 (Demo live) | Tous (Ianis pilote) | ~4 min |
| 11-13 (Docs + Difficultes + Bilan) | Ianis + equipe | ~3 min 30 |
| 14 (Questions) | -- | -- |

**Total** : ~19 min (1 min de marge)

---

## Slide 1 — Titre

**Visuel** : Logo NTL + nom outil + noms equipe

```
NTL-SysToolbox
Outil CLI d'administration systeme pour NordTransit Logistics

Ianis (Lead) — Blaise — Ojvind — Zaid
MSPR TPRE511 — EPSI — 2026
```

> **Notes speaker** : Pas de blabla. "Bonjour, nous sommes l'equipe X, nous allons
> vous presenter NTL-SysToolbox, un outil que nous avons developpe pour repondre
> aux besoins de la DSI de NordTransit Logistics."

---

## Slide 2 — Contexte NTL

**Visuel** : Carte Hauts-de-France avec les 4 sites + chiffres cles

**Contenu** :
- PME logistique, siege Lille + 3 entrepots (Lens, Valenciennes, Arras)
- ~240 employes, jusqu'a 300 en haute saison
- WMS (systeme d'entrepot) = coeur de metier, arret = arret des operations
- Equipe IT de 4 personnes (responsable, admin, technicien, alternant)
- Fenetres de maintenance courtes (nuit uniquement)

> **Notes speaker** : Planter le decor rapidement. Le jury doit comprendre que NTL
> est une PME avec une infra critique mais une equipe IT reduite.
> "NTL est une entreprise de logistique dans les Hauts-de-France. Le systeme
> d'entrepot tourne 13h par jour, son arret bloque les 4 sites immediatement.
> L'equipe IT ne compte que 4 personnes pour gerer tout ca."

---

## Slide 3 — Problematique

**Visuel** : 3 colonnes avec icone + probleme

| Supervision | Sauvegardes | Obsolescence |
|-------------|-------------|--------------|
| Surtout technique (ping, disque) | Scripts + NAS, jamais testees | Aucun inventaire EOL |
| Pas orientee "service" | Pas d'objectif RPO/RTO | OS en fin de vie non identifies |
| AD, DNS, MySQL non surveilles | Pas de verification d'integrite | Risque de faille non maitrise |

> **Notes speaker** : "La DSI nous a mande pour repondre a 3 problemes concrets :
> la supervision ne couvre pas les services metier, les sauvegardes ne sont pas
> verifiees, et personne ne sait quels OS sont en fin de vie sur le parc."
>
> **Competence ciblee** : Poser le besoin metier pour justifier chaque module.

---

## Slide 4 — Notre solution

**Visuel** : Schema simple — 1 outil, 3 modules, sorties exploitables

**Contenu** :
- **NTL-SysToolbox** : CLI Python, menu interactif
- 3 modules independants : Diagnostic, Backup, Audit
- Sorties JSON horodatees + codes retour standard (0-3)
- Compatible Windows et Linux
- Configuration YAML + secrets via variables d'environnement

**Points cles a faire passer** :
- "On a choisi Python pour la portabilite et l'ecosysteme de libs sys/reseau"
- "Les codes retour permettent une integration future avec Zabbix ou tout outil de supervision"
- "La config est separee du code — la DSI peut adapter sans toucher au code"

> **Notes speaker** : C'est LA slide de synthese. Le jury doit retenir : 1 outil,
> 3 modules, JSON + codes retour = exploitable en supervision.
>
> **Competences** : BC01.9 (rationnaliser via scripts), BC03.9 (alertes/codes retour)

---

## Slide 5 — Architecture

**Visuel** : Diagramme de flux (reprendre celui de PROJECT_MAP.md, simplifie)

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

**Points cles** :
- Contrat JSON uniforme : module, function, timestamp, status, exit_code, target, details, message
- Exit codes : 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN
- Seuils WARNING a 80% (CPU, RAM, disque) — norme industrie
- Chaque module est independant, meme signature `run(config, target, action=...)`

> **Notes speaker** : "L'architecture est volontairement simple. Chaque module est
> independant mais respecte le meme contrat de sortie. Ca veut dire que la DSI peut
> integrer n'importe quel resultat dans sa supervision existante, parce que le
> format est toujours le meme."
>
> **Competences** : BC03.9 (alertes exploitables), BC01.9 (automatisation)

---

## Slide 6 — Module Diagnostic (Blaise)

**Visuel** : Tableau des 4 fonctions + schema de decision pour check_ad_dns

| Fonction | Cible | Ce qu'elle verifie |
|----------|-------|--------------------|
| `check_ad_dns` | DC01 | Ports LDAP/DNS/Kerberos + resolution DNS + connectivite LDAP |
| `check_mysql` | WMS-DB | Port 3306 + version MySQL (sans auth) |
| `check_linux` | Tout serveur | Scan multi-ports, categorisation des services actifs |
| `check_http` | Tout serveur web | Status HTTP, header Server, temps de reponse |

**Exemple de decision** :
```
LDAP OK + DNS OK         → OK (0)
LDAP OK + DNS KO         → WARNING (1)
LDAP KO                  → CRITICAL (2)
DC01 injoignable         → UNKNOWN (3)
```

**Libs utilisees** : dnspython, ldap3, socket

> **Notes speaker (Blaise)** : "Mon module repond a la question : est-ce que les
> services critiques du siege fonctionnent ? Pour chaque verification, j'ai une
> logique de decision claire qui produit un status et un code retour exploitable."
>
> Montrer qu'on comprend POURQUOI on teste ces services (AD = auth de tout le monde,
> DNS = resolution de noms, MySQL = WMS).
>
> **Competences** : BC02.7 (supervision), BC03.9 (evaluation perturbations)

---

## Slide 7 — Module Backup (Ojvind)

**Visuel** : Schema du flux backup_database + tableau des 2 fonctions

| Fonction | Ce qu'elle fait | Sortie |
|----------|-----------------|--------|
| `backup_database` | mysqldump local ou via SSH (fallback) | `output/backups/wms_YYYYMMDD_HHMMSS.sql` |
| `export_table_csv` | SELECT * → fichier CSV | `output/exports/table_YYYYMMDD_HHMMSS.csv` |

**Points securite** :
- Mot de passe MySQL passe via variable d'env (`MYSQL_PWD`), jamais en argument CLI
- Validation du nom de table (regex) → protection injection SQL
- Protection path traversal (pas de `..` dans les chemins)
- Fallback SSH si mysqldump pas disponible localement

> **Notes speaker (Ojvind)** : "Mon module permet a la DSI de lancer une sauvegarde
> de la base WMS a tout moment. Le dump est fait via mysqldump, avec un fallback SSH
> si l'outil n'est pas installe localement. J'ai porte une attention particuliere a
> la securite : les mots de passe ne transitent jamais en argument de commande."
>
> Si le jury demande pourquoi pas de compression : "C'est un choix d'equipe, on a
> privilegie la simplicite et la lisibilite du dump pour une premiere version."
>
> **Competences** : BC01.11 (automatisation sauvegarde)

---

## Slide 8 — Module Audit (Zaid)

**Visuel** : Pipeline audit en 4 etapes + exemple de rapport

```
scan_network → list_os_eol → audit_from_csv → generate_report
(nmap)         (JSON local)   (croisement)     (rapport trie)
```

| Fonction | Entree | Sortie |
|----------|--------|--------|
| `scan_network` | Plage IP (ex: 192.168.10.0/24) | Machines detectees + ports + OS |
| `list_os_eol` | Base EOL locale (JSON) | Liste des dates de fin de support |
| `audit_from_csv` | Inventaire CSV (hostname, OS, version) | Croisement avec dates EOL |
| `generate_report` | Resultats combines | Rapport JSON + tableau colore terminal |

**Exemple de sortie rapport** :
```
EXPIRE   | SRV-PRINT  | Win Server 2008 R2 | EOL: jan 2020 | -2285 jours
EXPIRE   | PC-QUAI    | Windows 7          | EOL: jan 2020 | -2285 jours
BIENTOT  | SRV-FILE   | Win Server 2012 R2 | EOL: oct 2026 | +183 jours
OK       | DC01       | Win Server 2022    | EOL: oct 2031 | +2024 jours
```

> **Notes speaker (Zaid)** : "Mon module repond a la question : quels equipements
> du parc sont obsoletes et representent un risque ? Le scan reseau detecte les
> machines, puis on croise avec notre base de dates de fin de vie pour produire
> un rapport classe par urgence."
>
> Si le jury demande la source des dates EOL : "On utilise une base JSON locale
> maintenue manuellement, basee sur les dates officielles Microsoft et Ubuntu.
> C'est un compromis : pas de dependance reseau, mais necessite une mise a jour
> periodique."
>
> **Competences** : BC01.4 (identifier systemes a corriger), BC02.8 (recenser ressources)

---

## Slide 9 — Lab de test & CI/CD

**Visuel** : Schema du lab Proxmox + pipeline CI

**Lab** :
- Proxmox VE avec VMs reproduisant l'infra NTL
- DC01 (Windows Server, AD/DNS), WMS-DB (Ubuntu, MySQL)
- Permet de tester en conditions reelles sans toucher a la prod

**CI/CD (GitHub Actions)** :
- Declenchement : push sur master/feature/*, PR sur master
- Job 1 : Lint (ruff) + Types (mypy)
- Job 2 : Tests (pytest) sur Python 3.10, 3.11, 3.12
- Couverture minimum : 50%

> **Notes speaker (Ianis)** : "Pour valider notre outil, on a monte un lab Proxmox
> qui reproduit l'infra NTL. Chaque push declenche notre pipeline CI qui verifie
> la qualite du code et lance les tests sur 3 versions de Python."
>
> **Competences** : BC02.7 (supervision/qualite)

---

## Slide 10 — Demo live

**Scenario** (4 minutes, Ianis pilote, chacun commente son module) :

### Etape 1 — Lancement (Ianis, 30s)
```bash
python src/main.py
# Menu principal s'affiche
```
"Voici le menu interactif. La DSI peut naviguer sans documentation."

### Etape 2 — Diagnostic AD/DNS (Blaise, 1 min)
```
Choix 1 → Diagnostic
Choix 1 → Verifier AD/DNS
IP : [Entree pour defaut]
→ Resultat JSON : status OK/CRITICAL
```
"On verifie que l'AD et le DNS du DC01 sont operationnels."

### Etape 3 — Backup BDD (Ojvind, 1 min)
```
Choix 2 → Backup
Choix 1 → Backup base de donnees
Base : [Entree pour defaut = wms]
→ Resultat : fichier SQL cree, taille, chemin
```
"On sauvegarde la base WMS. Le fichier est horodate et pret a etre archive."

### Etape 4 — Audit EOL (Zaid, 1 min)
```
Choix 3 → Audit
Choix 2 → Lister dates EOL
→ Resultat : tableau des OS avec jours restants
```
"On identifie immediatement les OS en fin de vie."

### Etape 5 — Quitter (Ianis, 30s)
```
Choix 0 → Quitter
Montrer le fichier JSON genere dans output/logs/
```
"Tous les resultats sont sauvegardes en JSON horodate, exploitables par la supervision."

> **IMPORTANT** : Preparer un plan B si le lab n'est pas accessible :
> - Screenshots/video de la demo enregistree
> - Fichiers JSON de sortie pre-generes a montrer

---

## Slide 11 — Documentation

**Visuel** : Liste des livrables + capture d'ecran de la doc

**Livrables produits** :
- **Dossier technique** : architecture, choix technologiques, gestion des secrets
- **Guide d'installation** : setup en 5 commandes (clone, venv, deps, config, run)
- **10 docs numerotees** : de getting-started a lab-infra
- **Cheatsheet** : aide-memoire 1 page pour l'equipe
- **Rapport CI** : pipeline, couverture, resultats

**Points forts** :
- La DSI peut deployer et utiliser l'outil sans assistance (comme demande)
- Documentation versionee avec le code (dans le repo Git)

> **Notes speaker** : "Notre documentation couvre l'installation, l'utilisation et
> l'architecture. Un administrateur qui recupere le repo peut deployer l'outil en
> moins de 5 minutes en suivant le guide."
>
> **Competence** : BC04.2 (documentation technique)

---

## Slide 12 — Difficultes & compromis

**Visuel** : Tableau probleme → solution

| Difficulte | Notre approche |
|------------|----------------|
| Portabilite Windows/Linux | Python + libs cross-platform, tests CI sur Ubuntu |
| Acces WinRM optionnel | Fallback gracieux — fonctionne sans, mais signale le manque |
| Base EOL locale vs API externe | JSON local = pas de dependance reseau, mais maintenance manuelle |
| 4 devs, 19h, modules interdependants | Contrat JSON commun defini en amont → developpement parallele |
| Securite des credentials | Variables d'env + .env, jamais de secret dans le code ou les logs |

> **Notes speaker** : "On assume nos compromis. Par exemple, la base EOL est locale
> plutot qu'une API en ligne. C'est moins dynamique, mais ca evite une dependance
> reseau pour un outil qui doit fonctionner meme en cas de panne."
>
> Le jury apprecie les compromis ASSUMES. Ne pas dire "on n'a pas eu le temps",
> dire "on a choisi X parce que Y".

---

## Slide 13 — Bilan & perspectives

**Visuel** : Check-list des objectifs + roadmap v2

**Objectifs atteints** :
- [x] 3 modules fonctionnels et independants
- [x] Menu CLI interactif
- [x] Sorties JSON horodatees + codes retour supervision
- [x] Configuration YAML + gestion secrets
- [x] CI/CD avec lint, types, tests
- [x] Documentation complete

**Perspectives (si NTL veut aller plus loin)** :
- Integration Zabbix/supervision (les codes retour sont deja compatibles)
- Planification automatique des backups (cron/Task Scheduler)
- Mise a jour automatique de la base EOL via API
- Extension aux sites distants (WH1, WH2, WH3)
- Dashboard web pour visualiser les resultats

> **Notes speaker** : "On a livre un outil fonctionnel qui repond au cahier des charges.
> Les perspectives montrent que l'architecture est pensee pour evoluer — les codes
> retour standard permettent deja une integration supervision sans modification."

---

## Slide 14 — Questions

**Visuel** : Sobre, titre + contacts

```
Merci pour votre attention.
Nous sommes prets pour vos questions.
```

---

## Aide — Questions probables du jury

### Sur l'architecture
- **"Pourquoi Python et pas Bash/PowerShell ?"** → Portabilite Win+Linux, ecosysteme de libs (paramiko, nmap, ldap3), maintenabilite par l'equipe IT
- **"Pourquoi des codes retour 0-3 ?"** → Convention Nagios/Zabbix, standard industrie pour les checks de supervision
- **"Comment la config gere les secrets ?"** → Variables d'env via .env, substitution ${VAR}, jamais de secret en dur

### Sur les modules
- **"Que se passe-t-il si MySQL ne repond pas ?"** → Status CRITICAL (code 2), erreur dans details, message lisible
- **"Votre scan reseau necessite-t-il les droits root ?"** → Detection auto, scan degrade sans root avec WARNING
- **"Comment vous gerez un backup qui echoue ?"** → Status CRITICAL, pas de fichier corrompu laisse en place
- **"La base EOL, elle vient d'ou ?"** → Donnees Microsoft/Ubuntu officielles, fichier JSON versionne avec le code

### Sur l'equipe
- **"Comment vous vous etes repartis le travail ?"** → Contrat JSON commun defini ensemble, puis branches isolees par module, merge par le lead
- **"Quelle a ete la plus grosse difficulte ?"** → Chacun repond selon son module (preparer individuellement)

### Sur la CI
- **"Pourquoi 3 versions de Python ?"** → La DSI peut avoir differentes versions installees, on garantit la compatibilite
- **"Quel est le taux de couverture ?"** → Seuil minimum 50%, focus sur les chemins critiques

### Pieges a eviter
- Ne PAS dire "on n'a pas eu le temps" → dire "on a priorise X"
- Ne PAS dire "c'est un projet scolaire" → on parle a la DSI de NTL
- Ne PAS lire les slides — les connaitre
- Chacun doit pouvoir expliquer son module ET le contrat commun
