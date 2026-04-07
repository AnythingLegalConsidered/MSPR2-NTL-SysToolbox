# Guide Oral Soutenance — NTL-SysToolbox (v6)

> **Ce document = ce que vous devez DIRE devant le jury, diapo par diapo.**
> Le jury joue le rôle de la DSI de NordTransit Logistics. Parlez-leur comme à un client, pas à un prof.
> Durée cible : 20 min de présentation + 30 min de questions.
> Basé sur le PowerPoint **NTL-SysToolbox_Soutenance_v6.pptx** (16 slides).

---

## SLIDE 1 — Titre (Blaise, 30s)

**Contenu slide :** NTL-SysToolbox / Outil CLI d'administration système pour NordTransit Logistics / Noms équipe / MSPR TPRE511

### Ce qu'il faut dire :

> "Bonjour. Nous sommes Ianis, Blaise, Ojvind et Zaid. Nous allons vous présenter NTL-SysToolbox, un outil en ligne de commande que nous avons développé pour répondre aux besoins de votre DSI en matière de supervision, de sauvegarde et d'audit de votre parc informatique."

### Ce que le jury attend :

- Une intro **courte** et **pro**. Pas de "on est étudiants", pas de "c'est un projet scolaire".
- Que vous vous présentiez rapidement (prénom + rôle dans le projet).
- Que le nom de l'outil et son objectif soient posés d'entrée.

### Erreurs à éviter :

- Lire la slide
- Se présenter trop longuement (pas de parcours perso)
- Dire "merci de nous recevoir" — on n'est pas en entretien, on présente un livrable

---

## SLIDE 2 — Contexte NTL (Blaise, 1min30)

**Contenu slide :** PME logistique Hauts-de-France / ~240 employés / WMS cœur de métier / Équipe IT 4 personnes / Maintenance nocturne

### Ce qu'il faut dire :

> "NordTransit Logistics est une PME de logistique basée à Lille, avec 3 entrepôts dans les Hauts-de-France : Lens, Valenciennes et Arras. L'entreprise emploie environ 240 personnes, jusqu'à 300 en haute saison avec l'intérim."
>
> "Le cœur de leur activité repose sur un système de gestion d'entrepôt — le WMS — qui tourne de 5h30 à 18h30. Si ce système s'arrête, c'est l'ensemble des 4 sites qui est bloqué."
>
> "L'équipe IT ne compte que 4 personnes : un responsable, un admin sys/réseau, un technicien et un alternant. Les fenêtres de maintenance sont limitées à la nuit — zéro coupure autorisée en journée."

### Ce que le jury attend :

- Que vous **compreniez le métier du client** — pas juste la technique.
- Que vous montriez pourquoi la situation est **critique** : infra vitale + équipe IT réduite.
- Le jury veut sentir que vous avez **analysé le contexte métier** avant de coder.

### Le message clé à faire passer :

**"Petite équipe IT, système critique, zéro marge d'erreur"** — ça justifie tout le reste du projet.

---

## SLIDE 3 — Problématique (Zaid, 1min30)

**Contenu slide :** 3 colonnes — Supervision / Sauvegardes / Obsolescence → chacune mène à un module

### Ce qu'il faut dire :

> "On a identifié 3 angles morts dans le SI de NTL."
>
> "**Premier problème : la supervision.** Aujourd'hui, la DSI surveille surtout des indicateurs techniques — le ping, l'espace disque. Mais les services métier comme l'Active Directory, le DNS ou MySQL ne sont pas surveillés. Si l'AD tombe, personne ne peut se connecter, et personne n'est alerté. C'est ce qui a motivé le **module Diagnostic**."
>
> "**Deuxième problème : les sauvegardes.** Il y a bien des scripts de backup sur un NAS, mais ces sauvegardes n'ont jamais été testées. Il n'y a pas d'objectif RPO ou RTO défini, et aucune vérification d'intégrité. D'où le **module Backup**."
>
> "**Troisième problème : l'obsolescence.** Personne ne sait exactement quels OS du parc sont en fin de vie. Il n'y a pas d'inventaire EOL. Ça veut dire qu'il y a potentiellement des machines avec des failles non corrigées qui tournent sans que personne le sache. C'est le **module Audit**."

### Ce que le jury attend :

- **3 problèmes concrets, liés au risque métier** — pas techniques pour le plaisir.
- Que chaque problème mène logiquement à un module. C'est le fil rouge de la présentation.
- Que vous utilisiez le vocabulaire métier : RPO, RTO, EOL, Active Directory.

### Conseils :

- Pointer chaque colonne en la nommant
- Ne pas détailler les solutions ici — juste les problèmes
- Le jury doit se dire : "OK, ce sont de vrais problèmes, voyons leur solution"

---

## SLIDE 4 — Notre solution (Ojvind, 1min)

**Contenu slide :** CLI Python interactif / 3 modules / JSON horodaté / Codes retour 0-3 / Config YAML + .env / Cross-platform

### Ce qu'il faut dire :

> "Notre réponse, c'est NTL-SysToolbox : un outil CLI Python avec un menu interactif. Il couvre les 3 besoins en 3 modules indépendants : Diagnostic, Backup et Audit."
>
> "On a fait des choix techniques précis :"
> - "**Python** pour la portabilité Windows/Linux et l'écosystème de librairies système et réseau."
> - "**Des sorties JSON horodatées** avec des codes retour standard 0 à 3. Ce format est directement compatible avec des outils de supervision comme Zabbix ou Nagios — OK, WARNING, CRITICAL, UNKNOWN."
> - "**Une configuration YAML séparée du code**, avec les secrets gérés par variables d'environnement dans un fichier `.env`. Zéro secret en dur dans le code."
> - "Et l'outil est **cross-platform** — il fonctionne sur Windows et Linux."

### Ce que le jury attend :

- Les **choix techniques justifiés** — pas "on a pris Python parce qu'on le connaît", mais "Python pour la portabilité et les libs".
- Que vous montriez que l'outil est **intégrable** dans l'existant (codes retour standard).
- Que la **séparation config/code** soit mentionnée — c'est un signe de maturité.

### Le message clé :

**"1 outil, 3 modules, des sorties exploitables par la supervision existante."**

---

## SLIDE 5 — Organisation de l'équipe (Ojvind, 1min)

**Contenu slide :** Tableau membres/rôles/périmètre + Méthode de travail (contrat JSON, branches, PRs, CI) + Workflow Git en 4 étapes

### Ce qu'il faut dire :

> "On est 4 développeurs pour 19 heures de projet. On s'est organisés autour du contrat JSON commun qu'on a défini ensemble en amont dans le fichier `interfaces.py`."
>
> "Ianis en lead sur le framework, le CLI, la CI/CD et l'intégration. Blaise sur le module Diagnostic, Ojvind sur le Backup, Zaid sur l'Audit."
>
> "Notre workflow Git est structuré en 4 étapes : chaque dev code sur sa branche `feature/*`, chaque push déclenche la CI automatiquement, ensuite une pull request avec review par le lead, et enfin un merge squash sur master pour garder un historique propre."

### Ce que le jury attend :

- **Qui a fait quoi** — concrètement.
- Que la méthode de travail soit **structurée** (branches, PRs, reviews, CI).
- Que le contrat commun ait permis le **travail en parallèle**.
- Le workflow Git en 4 étapes montre une **vraie organisation d'équipe**.

---

## SLIDE 6 — Architecture (Ianis, 1min30)

**Contenu slide :** Schéma main.py → 3 modules → build_result() → Terminal + output/ + Tableau contrat JSON (8 champs) + Seuils et timeout

### Ce qu'il faut dire :

> "L'architecture est volontairement simple. En haut, le point d'entrée : `main.py`, qui affiche le menu interactif. En dessous, les 3 modules — Diagnostic, Backup, Audit — qui sont complètement indépendants. Chacun peut tourner seul."
>
> "Le point commun, c'est le contrat de sortie. Tous les modules passent par la fonction `build_result()` qui génère un JSON avec toujours la même structure."
>
> *(pointer le tableau)* "8 champs : le module, la fonction appelée, un timestamp ISO 8601, le status — OK, WARNING, CRITICAL ou UNKNOWN —, le code retour de 0 à 3, la cible, les détails spécifiques au check, et un message lisible par un humain."
>
> "Les seuils WARNING sont à 80% pour CPU, RAM et disque. Le timeout par défaut est de 10 secondes."

### Ce que le jury attend :

- Que vous expliquiez **pourquoi cette architecture** (simplicité, indépendance, intégrabilité).
- Que le **contrat JSON** soit clair — les 8 champs du tableau sont LA décision technique du projet.
- Que les **codes retour** soient un **standard industrie** (Nagios/Zabbix), pas un choix arbitraire.

### Conseils :

- Ne pas se perdre dans les détails du code
- Pointer visuellement le schéma et le tableau des champs
- Le jury doit comprendre en 10 secondes : "format unique partout = facile à intégrer"

---

## SLIDE 7 — Module Diagnostic (Blaise, 1min30)

**Contenu slide :** "Les services critiques du siège sont-ils opérationnels ?" / Tableau 4 fonctions (check_ad_dns, check_mysql, check_linux, check_http)

### Ce qu'il faut dire :

> "Mon module répond à la question affichée : est-ce que les services critiques du siège sont opérationnels ?"
>
> "J'ai 4 fonctions de vérification :"
> - "`check_ad_dns` vérifie l'Active Directory et le DNS sur le DC01 — les ports LDAP, DNS et Kerberos, plus une résolution DNS pour confirmer que le service répond vraiment."
> - "`check_mysql` teste la connexion au serveur MySQL qui héberge le WMS — port 3306 et version du serveur, sans avoir besoin de s'authentifier."
> - "`check_linux` fait un scan multi-ports sur n'importe quel serveur pour identifier et catégoriser les services actifs."
> - "`check_http` vérifie qu'un serveur web répond — status HTTP, header Server, temps de réponse."
>
> "Chaque vérification suit une logique de décision claire. Par exemple pour l'AD : si le serveur est injoignable, c'est UNKNOWN. Si LDAP ne répond pas, c'est CRITICAL. Si LDAP répond mais le DNS est en panne, c'est WARNING. Et si tout va bien, OK."

### Ce que le jury attend :

- Que Blaise comprenne **pourquoi** on teste ces services — pas juste "comment".
  - AD = authentification de tous les employés
  - DNS = résolution de noms, si ça tombe tout tombe
  - MySQL = la base du WMS, cœur de métier
- La **logique de décision** (arbre OK/WARNING/CRITICAL/UNKNOWN).
- Que chaque check retourne un **résultat exploitable**.

### Questions probables pour Blaise :

- "Que se passe-t-il si MySQL ne répond pas ?" → CRITICAL (code 2), erreur dans les détails
- "Vous utilisez quelles libs ?" → dnspython, ldap3, socket
- "Pourquoi ne pas utiliser un simple ping ?" → Un ping ne vérifie pas que le service répond, juste que la machine est allumée

---

## SLIDE 8 — Module Backup (Ojvind, 1min30)

**Contenu slide :** "Sauvegarder la base WMS de manière fiable et traçable" / 2 fonctions (backup_database, export_table_csv) / 4 mesures de sécurité

### Ce qu'il faut dire :

> "Mon module permet à la DSI de sauvegarder la base WMS de manière fiable et traçable."
>
> "J'ai 2 fonctions principales :"
> - "`backup_database` fait un dump SQL complet via mysqldump. Si mysqldump n'est pas installé localement, le module bascule automatiquement sur une connexion SSH pour l'exécuter sur le serveur distant. Le fichier de sortie est horodaté dans `output/backups/`."
> - "`export_table_csv` permet d'exporter une table spécifique en CSV horodaté — utile pour des extractions ponctuelles."
>
> "J'ai porté une attention particulière à la sécurité — vous pouvez voir les 4 mesures sur la slide :"
> - "Le mot de passe MySQL transite par variable d'environnement `MYSQL_PWD`, jamais en argument de commande."
> - "Le nom de table est validé par regex pour empêcher toute injection SQL."
> - "Les chemins de sortie sont protégés contre le path traversal — pas de `..` autorisé."
> - "Et le fallback SSH si mysqldump n'est pas disponible localement."

### Ce que le jury attend :

- Le **mécanisme de fallback** SSH — ça montre de la robustesse.
- La **sécurité des credentials** — c'est un sujet sensible, le jury va creuser.
- Qu'Ojvind sache expliquer **pourquoi** ces choix (pas juste "on a fait ça").

### Questions probables pour Ojvind :

- "Pourquoi pas de compression du dump ?" → "On a priorisé la simplicité et la lisibilité du dump pour une V1. La compression est une amélioration possible."
- "Comment vous vérifiez l'intégrité ?" → Hash SHA256 du fichier, vérification taille > 0
- "Pourquoi mysqldump et pas un export logique Python ?" → mysqldump est l'outil standard, il gère les locks et la cohérence transactionnelle

---

## SLIDE 9 — Module Audit (Zaid, 1min30)

**Contenu slide :** "Quels équipements du parc sont obsolètes et représentent un risque ?" / Pipeline 4 étapes / Tableau fonctions (entrée/sortie)

### Ce qu'il faut dire :

> "Mon module répond à la question : quels équipements du parc sont obsolètes et représentent un risque de sécurité ?"
>
> *(pointer le pipeline en haut)* "Le processus se fait en 4 étapes, de gauche à droite :"
> 1. "`scan_network` utilise nmap pour scanner une plage IP en CIDR et détecter les machines actives, leurs ports ouverts et leur OS."
> 2. "`list_os_eol` consulte notre base JSON locale qui contient les dates de fin de support officielles de chaque OS."
> 3. "`audit_from_csv` croise un inventaire CSV — qui contient les machines du parc avec leur OS — avec les dates EOL."
> 4. "`generate_report` produit un rapport trié par urgence : d'abord les OS expirés, puis ceux qui expirent bientôt, puis les OK. Le rapport est en JSON et aussi affiché en tableau coloré dans le terminal."

### Ce que le jury attend :

- Le **pipeline en 4 étapes** — scan, référence, croisement, rapport. C'est méthodique.
- La **hiérarchisation par risque** — pas juste une liste, un rapport actionnable.
- Que Zaid sache défendre le choix d'une **base JSON locale** vs une API en ligne.

### Questions probables pour Zaid :

- "La base EOL, elle vient d'où ?" → "Données officielles Microsoft et Ubuntu, dans un fichier JSON versionné avec le code. C'est un compromis : pas de dépendance réseau, mais maintenance manuelle."
- "Le scan nmap nécessite les droits root ?" → "Détection auto, scan dégradé sans root avec un WARNING."
- "Pourquoi pas une API comme endoflife.date ?" → "On veut que l'outil fonctionne même en réseau coupé — cohérent avec un outil d'audit de crise."

---

## SLIDE 10 — Environnement de test (Ianis, 45s)

**Contenu slide :** Tableau 5 VMs (DC01, WMS-DB, WMS-APP, SRV-OLD, SRV-LEGACY) avec OS/rôle/IP + Pourquoi un lab + Proxmox VE

### Ce qu'il faut dire :

> "Pour valider notre outil en conditions réelles, on a monté un lab sur Proxmox VE — un hyperviseur open source — avec 5 VMs sur le réseau 192.168.10.0/24."
>
> "Le lab reproduit l'infra de NTL : un DC01 sous Windows Server 2022 avec Active Directory et DNS, un WMS-DB sous Ubuntu avec MySQL, un WMS-APP pour l'application, et deux VMs legacy — Windows Server 2012 R2 et Ubuntu 18.04 — spécifiquement pour tester la détection des OS en fin de vie."
>
> "Ça nous a permis de tester chaque module sur des machines identiques à la production, sans jamais toucher à l'infra réelle du client."

### Ce que le jury attend :

- Que vous ayez un **environnement de test** — ça montre du professionnalisme.
- Que le lab **reproduise l'infra réelle** — pas un test en local sur localhost.
- Les VMs legacy montrent une **démarche délibérée** de test des cas limites.
- Le déploiement via **scripts post-install** montre que c'est reproductible.

---

## SLIDE 11 — Intégration continue (Ianis, 45s)

**Contenu slide :** Pipeline GitHub Actions en schéma (déclenchement → 2 jobs parallèles → merge OK) + Détails lint/types/tests/feedback

### Ce qu'il faut dire :

> "Chaque commit est vérifié automatiquement par notre pipeline GitHub Actions."
>
> *(pointer le schéma)* "Au déclenchement — push ou PR sur master ou `feature/*` — deux jobs tournent en parallèle : un job qualité avec ruff pour le lint et mypy pour la vérification de types, et un job tests avec pytest et couverture sur 3 versions de Python — 3.10, 3.11 et 3.12."
>
> "Le résultat est disponible en moins de 2 minutes. Si tout passe, le merge est autorisé."

### Ce que le jury attend :

- Que la CI soit **réelle et automatisée** — pas un truc fait à la main.
- **3 versions de Python** = on anticipe que la DSI peut avoir différentes versions.
- Les 2 jobs **en parallèle** montrent une optimisation du pipeline.
- Le feedback en moins de 2 minutes montre un pipeline **efficace**.

### Question probable :

- "Pourquoi seulement 54% de couverture ?" → "On a concentré les tests sur les chemins critiques et les cas d'erreur. 100% de couverture sur un outil qui interagit avec du réseau et des VMs serait largement du mock — on a préféré des tests qui testent vraiment quelque chose."

---

## SLIDE 12 — Démo live (Tous, 4min)

**Contenu slide :** 5 étapes numérotées avec qui fait quoi : 1. Menu (Ianis) / 2. Diagnostic (Blaise) / 3. Backup (Ojvind) / 4. Audit (Zaid) / 5. Résultats JSON (Ianis)

### Déroulement :

**Étape 1 — Ianis (30s)** — Lancement :
> "Je lance l'outil avec `python src/main.py`. Vous voyez le menu interactif — la DSI peut naviguer sans documentation ni formation."

*(lancer `python src/main.py`, montrer le menu)*

**Étape 2 — Blaise (1min)** — Diagnostic AD/DNS :
> "Je vais vérifier que le DC01 répond — que l'AD et le DNS sont opérationnels."

*(Choix 1 → Diagnostic → Vérifier AD/DNS → montrer le résultat JSON)*

> "Le résultat est immédiat : status OK, les ports LDAP et DNS répondent, la résolution DNS fonctionne. Si un service était en panne, on aurait un CRITICAL avec le détail de ce qui ne répond pas."

**Étape 3 — Ojvind (1min)** — Backup base WMS :
> "Je vais sauvegarder la base WMS en dump SQL."

*(Choix 2 → Backup → Backup base de données → montrer le fichier généré)*

> "Le dump SQL est créé avec un horodatage. On voit la taille du fichier et son chemin. Le fichier est prêt à être archivé par la DSI."

**Étape 4 — Zaid (1min)** — Audit EOL :
> "Je vais lister les OS en fin de vie sur le parc."

*(Choix 3 → Audit → Lister dates EOL → montrer le tableau)*

> "Le tableau montre immédiatement quels OS sont expirés, lesquels approchent de la fin de vie, et lesquels sont OK. La DSI sait instantanément où sont les risques."

**Étape 5 — Ianis (30s)** — Résultats JSON :
> "Tous les résultats sont sauvegardés en JSON horodaté dans le dossier `output/logs/`. Ces fichiers sont directement exploitables par n'importe quel outil de supervision."

*(montrer les fichiers JSON dans output/logs/)*

### Ce que le jury attend pendant la démo :

- Que **chaque membre commente son propre module** — pas qu'une seule personne parle.
- Que ça **fonctionne** (avoir un plan B : screenshots ou vidéo pré-enregistrée).
- Que les **résultats soient lisibles et exploitables** — montrer le JSON.
- Que vous montriez des **cas OK ET des cas d'erreur** si possible.

### Plan B (si le lab est inaccessible) :

- Screenshots réels de l'outil en fonctionnement (dossier `output/screenshots/`)
- Fichiers JSON de sortie pré-générés à montrer (dossier `output/logs/`)
- Vidéo de la démo enregistrée à l'avance
- **Dites-le clairement** : "On a enregistré la démo car le lab n'est pas accessible depuis cette salle, mais l'outil tourne sur notre infrastructure."

---

## SLIDE 13 — Documentation (Ianis, 1min)

**Contenu slide :** Liste livrables (6 ✓) + Message autonomie DSI + Arborescence docs/ complète (12 fichiers)

### Ce qu'il faut dire :

> "On a produit une documentation complète — vous pouvez voir les 6 livrables à gauche et l'arborescence complète à droite."
>
> "Un dossier technique et fonctionnel, un guide d'installation en 5 commandes, 10 documents numérotés qui couvrent de l'architecture au lab, un cheatsheet d'une page pour l'équipe, un rapport CI/CD, et une exécution de référence de l'audit d'obsolescence."
>
> "Un administrateur qui récupère le repo Git peut déployer et utiliser l'outil en moins de 5 minutes. La documentation est versionnée avec le code — pas un PDF envoyé par mail."

### Ce que le jury attend :

- Que la doc **permette l'autonomie** de la DSI — c'est explicitement demandé.
- Que la doc soit **versionnée avec le code** dans le repo Git.
- L'arborescence complète des docs montre un travail **exhaustif et organisé**.

---

## SLIDE 14 — Difficultés & compromis (Zaid, 1min30)

**Contenu slide :** "Chaque compromis a été discuté en équipe et assumé en connaissance de cause" / Tableau 5 difficultés avec approche

### Ce qu'il faut dire :

> "On assume nos choix et nos compromis. Chaque point a été discuté en équipe."
>
> *(parcourir le tableau en pointant chaque ligne)*
>
> "La **portabilité Windows/Linux** : Python et des librairies cross-platform, validées par la CI sur Ubuntu."
>
> "L'**accès WinRM** : on a fait un fallback gracieux. L'outil fonctionne sans, mais signale le manque — ça n'empêche pas le diagnostic, ça le dégrade proprement."
>
> "La **base EOL locale** plutôt qu'une API externe : c'est un compromis assumé. Pas de dépendance réseau, l'outil fonctionne même en cas de panne, mais ça impose une maintenance manuelle."
>
> "La **coordination à 4** en 19 heures : le contrat JSON défini en amont a été la clé. Chacun a pu développer son module en parallèle sans bloquer les autres."
>
> "La **sécurité des credentials** : variables d'environnement, fichier `.env`, zéro secret dans le code ou dans les logs."

### Ce que le jury attend :

- **Des compromis ASSUMÉS, pas des excuses.** La phrase interdite : "on n'a pas eu le temps". La bonne formulation : "on a priorisé X parce que Y".
- Que chaque contrainte ait été **identifiée et traitée** — même imparfaitement.
- C'est LA slide où le jury juge votre **maturité professionnelle**.

---

## SLIDE 15 — Bilan & perspectives (Blaise, 1min30)

**Contenu slide :** 7 objectifs atteints (✓) + 5 perspectives (→) avec détails + Métriques projet en bas

### Ce qu'il faut dire :

> "On a livré un outil fonctionnel qui répond au cahier des charges."
>
> *(parcourir les objectifs)* "3 modules fonctionnels et indépendants, menu CLI interactif avec Rich, sorties JSON horodatées avec codes retour, configuration YAML avec gestion des secrets, CI/CD complète, documentation complète avec 10 docs et un cheatsheet, et un lab de test Proxmox reproduisant l'infra NTL."
>
> "Pour les perspectives — si NTL veut aller plus loin :"
> - "Intégration Zabbix — les codes retour sont déjà compatibles, ça demande zéro modification côté outil."
> - "Backup planifié via cron ou Task Scheduler."
> - "Base EOL dynamique via l'API endoflife.date."
> - "Extension multi-sites pour couvrir les 3 entrepôts via les VPN existants."
> - "Et un dashboard web pour visualiser les résultats."
>
> *(pointer les métriques en bas)* "Le projet en chiffres : 62 commits, 110 tests, environ 2500 lignes Python, 10 docs, 5 VMs de lab, CI avec ruff, mypy et pytest sur 3 versions Python."

### Ce que le jury attend :

- Un **bilan factuel** — pas de vantardise, des faits et des chiffres.
- Des **perspectives réalistes** qui montrent que l'architecture est pensée pour évoluer.
- Le point clé : les codes retour standard signifient que **l'intégration supervision est déjà possible** sans toucher au code.
- Les **métriques concrètes** en bas rassurent sur le travail réel fourni.

### Le message final :

**"L'outil est livrable aujourd'hui et évoluera demain."**

---

## SLIDE 16 — Questions (Tous, 30min)

**Contenu slide :** "Merci pour votre attention. Nous sommes prêts pour vos questions."

### Ce qu'il faut dire :

> "Merci pour votre attention. Nous sommes prêts pour vos questions."

### Préparation aux questions — par thème :

#### Architecture & choix techniques

| Question probable | Réponse |
|-------------------|---------|
| "Pourquoi Python et pas Bash/PowerShell ?" | "Portabilité Win+Linux, écosystème de libs (paramiko, nmap, ldap3), maintenabilité par une équipe IT qui connaît déjà Python." |
| "Pourquoi les codes retour 0-3 ?" | "C'est la convention Nagios/Zabbix — un standard industrie. Ça rend l'outil intégrable sans adaptation." |
| "Comment la config gère les secrets ?" | "Variables d'environnement via `.env`, substitution `${VAR}` dans le YAML. Jamais de secret en dur dans le code." |
| "Pourquoi pas une interface web ?" | "La DSI a 4 personnes, elle travaille en terminal. Un CLI est plus rapide, plus scriptable, plus léger. Le web est une perspective V2." |

#### Modules (questions croisées)

| Question | Qui répond | Réponse |
|----------|-----------|---------|
| "Si MySQL ne répond pas ?" | Blaise ou Ojvind | "CRITICAL (code 2), erreur dans les détails, message lisible. Pas de crash." |
| "Le scan nmap nécessite root ?" | Zaid | "Détection auto. Sans root, scan dégradé + WARNING dans le résultat." |
| "Un backup qui échoue ?" | Ojvind | "CRITICAL, pas de fichier corrompu laissé sur le disque. Le fichier partiel est supprimé." |
| "Comment vous gérez un timeout ?" | Tous | "Timeout par défaut de 10s, configurable dans le YAML. Timeout = UNKNOWN (code 3)." |

#### Équipe & méthode

| Question | Réponse |
|----------|---------|
| "Comment vous vous êtes répartis ?" | "Contrat JSON commun défini ensemble en amont, puis branches isolées par module, merge par le lead après review." |
| "Quelle a été la plus grosse difficulté ?" | Chacun répond pour son module. Ianis : coordination. Blaise : AD multi-protocole. Ojvind : sécurité credentials. Zaid : fiabilité nmap. |
| "Répartition des commits ?" | "Ianis 40, les autres 3-4 chacun. Le lead a fait le framework, la CI, l'intégration et les reviews. Le travail de chaque dev est dans son module." |

#### CI/CD

| Question | Réponse |
|----------|---------|
| "Pourquoi 3 versions Python ?" | "La DSI peut avoir différentes versions. On garantit la compatibilité 3.10 à 3.12." |
| "54% de couverture, c'est pas faible ?" | "On a concentré sur les chemins critiques. L'outil interagit avec du réseau et des VMs — tester à 100% serait du mock sans valeur." |
| "Vous faites du déploiement continu ?" | "Non, déploiement manuel pour l'instant. Le CD est une perspective — l'outil est pensé pour être déployé par la DSI elle-même." |

---

## RÈGLES D'OR POUR TOUTE LA SOUTENANCE

1. **Ne JAMAIS lire les slides.** Vous les connaissez par cœur.
2. **Ne JAMAIS dire "on n'a pas eu le temps".** Dire "on a priorisé X".
3. **Ne JAMAIS dire "c'est un projet scolaire".** Vous parlez à la DSI de NTL.
4. **Chacun parle pour son module.** Pas qu'Ianis pendant 20 minutes.
5. **Pointer les visuels.** Quand il y a un schéma ou un tableau, montrez-le physiquement.
6. **Répondre avec assurance.** Si vous ne savez pas : "C'est un bon point, dans notre V1 on n'a pas couvert ça, mais l'architecture permet de l'ajouter."
7. **Relier au métier.** Chaque choix technique doit être justifié par un besoin de NTL, pas par un exercice scolaire.
8. **Garder le rythme.** 20 minutes max. Si une diapo prend trop de temps, avancez — le jury pourra revenir en questions.
9. **Démo : avoir un plan B.** Toujours. Screenshots dans `output/screenshots/`, JSON dans `output/logs/`.
10. **Finir proprement.** Pas de "voilà c'est fini". Juste : "Merci, on est prêts pour vos questions."

---

## Correspondance slides v6

| Slide | Titre | Qui parle | Durée |
|-------|-------|-----------|-------|
| 1 | Titre | Blaise | 30s |
| 2 | Contexte NTL | Blaise | 1min30 |
| 3 | Problématique | Zaid | 1min30 |
| 4 | Notre solution | Ojvind | 1min |
| 5 | Organisation équipe | Ojvind | 1min |
| 6 | Architecture | Ianis | 1min30 |
| 7 | Module Diagnostic | Blaise | 1min30 |
| 8 | Module Backup | Ojvind | 1min30 |
| 9 | Module Audit | Zaid | 1min30 |
| 10 | Environnement de test | Ianis | 45s |
| 11 | Intégration continue | Ianis | 45s |
| 12 | Démo live | Tous | 4min |
| 13 | Documentation | Ianis | 1min |
| 14 | Difficultés & compromis | Zaid | 1min30 |
| 15 | Bilan & perspectives | Blaise | 1min30 |
| 16 | Questions | Tous | 30min |
| | **Total présentation** | | **~19min30** |
