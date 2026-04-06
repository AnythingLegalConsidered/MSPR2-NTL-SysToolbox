# Guide Oral Soutenance — NTL-SysToolbox

> **Ce document = ce que vous devez DIRE devant le jury, diapo par diapo.**
> Le jury joue le role de la DSI de NordTransit Logistics. Parlez-leur comme a un client, pas a un prof.
> Duree cible : 20 min de presentation + 30 min de questions.

---

## SLIDE 1 — Titre (Ianis, 30s)

### Ce qu'il faut dire :

> "Bonjour. Nous sommes Ianis, Blaise, Ojvind et Zaid. Nous allons vous presenter NTL-SysToolbox, un outil en ligne de commande que nous avons developpe pour repondre aux besoins de votre DSI en matiere de supervision, de sauvegarde et d'audit de votre parc informatique."

### Ce que le jury attend :

- Une intro **courte** et **pro**. Pas de "on est etudiants", pas de "c'est un projet scolaire".
- Que vous vous presentiez rapidement (prenom + role dans le projet).
- Que le nom de l'outil et son objectif soient poses d'entree.

### Erreurs a eviter :

- Lire la slide
- Se presenter trop longuement (pas de parcours perso)
- Dire "merci de nous recevoir" — on n'est pas en entretien, on presente un livrable

---

## SLIDE 2 — Contexte NTL (Ianis, 1min30)

### Ce qu'il faut dire :

> "NordTransit Logistics est une PME de logistique basee a Lille, avec 3 entrepots dans les Hauts-de-France : Lens, Valenciennes et Arras. L'entreprise emploie environ 240 personnes, jusqu'a 300 en haute saison."
>
> "Le coeur de leur activite repose sur un systeme de gestion d'entrepot — le WMS — qui tourne 13 heures par jour. Si ce systeme s'arrete, c'est l'ensemble des 4 sites qui est bloque."
>
> "L'equipe IT ne compte que 4 personnes : un responsable, un admin, un technicien et un alternant. Les fenetres de maintenance sont limitees a la nuit uniquement."

### Ce que le jury attend :

- Que vous **compreniez le metier du client** — pas juste la technique.
- Que vous montriez pourquoi la situation est **critique** : infra vitale + equipe IT reduite.
- Le jury veut sentir que vous avez **analyse le contexte metier** avant de coder.

### Le message cle a faire passer :

**"Petite equipe IT, systeme critique, zero marge d'erreur"** — ca justifie tout le reste du projet.

---

## SLIDE 3 — Problematique (Ianis, 1min30)

### Ce qu'il faut dire :

> "On a identifie 3 angles morts dans le SI de NTL."
>
> "**Premier probleme : la supervision.** Aujourd'hui, la DSI surveille surtout des indicateurs techniques — le ping, l'espace disque. Mais les services metier comme l'Active Directory, le DNS ou MySQL ne sont pas surveilles. Si l'AD tombe, personne ne peut se connecter, et personne n'est alerte."
>
> "**Deuxieme probleme : les sauvegardes.** Il y a bien des scripts de backup sur un NAS, mais ces sauvegardes n'ont jamais ete testees. Il n'y a pas d'objectif RPO ou RTO defini, et aucune verification d'integrite."
>
> "**Troisieme probleme : l'obsolescence.** Personne ne sait exactement quels OS du parc sont en fin de vie. Il n'y a pas d'inventaire EOL. Ca veut dire qu'il y a potentiellement des machines avec des failles non corrigees qui tournent sans que personne le sache."
>
> "Chacun de ces problemes a donne naissance a un module de notre outil."

### Ce que le jury attend :

- **3 problemes concrets, pas techniques pour le plaisir** — lies au risque metier.
- Que chaque probleme mene logiquement a un module. C'est le fil rouge de la presentation.
- Que vous utilisiez le vocabulaire metier : RPO, RTO, EOL, Active Directory.

### Conseils :

- Pointer chaque colonne en la nommant
- Ne pas detailler les solutions ici — juste les problemes
- Le jury doit se dire : "OK, ce sont de vrais problemes, voyons leur solution"

---

## SLIDE 4 — Notre solution (Ianis, 1min)

### Ce qu'il faut dire :

> "Notre reponse, c'est NTL-SysToolbox : un outil CLI Python avec un menu interactif. Il couvre les 3 besoins en 3 modules independants : Diagnostic, Backup et Audit."
>
> "On a fait des choix techniques precis :"
> - "**Python** pour la portabilite Windows/Linux et l'ecosysteme de librairies systeme et reseau."
> - "**Des sorties JSON horodatees** avec des codes retour standard 0 a 3. Ce format est directement compatible avec des outils de supervision comme Zabbix ou Nagios."
> - "**Une configuration YAML separee du code**, avec les secrets geres par variables d'environnement. La DSI peut adapter la config sans toucher au code source."

### Ce que le jury attend :

- Les **choix techniques justifies** — pas "on a pris Python parce qu'on le connait", mais "Python pour la portabilite et les libs".
- Que vous montriez que l'outil est **integrable** dans l'existant (codes retour standard).
- Que la **separation config/code** soit mentionnee — c'est un signe de maturite.

### Le message cle :

**"1 outil, 3 modules, des sorties exploitables par la supervision existante."**

---

## SLIDE 5 — Architecture (Ianis, 1min30)

### Ce qu'il faut dire :

> "L'architecture est volontairement simple. En haut, le point d'entree : `main.py`, qui affiche le menu interactif. En dessous, les 3 modules — Diagnostic, Backup, Audit — qui sont completement independants. Chacun peut tourner seul."
>
> "Le point commun, c'est le contrat de sortie. Tous les modules passent par la fonction `build_result()` qui genere un JSON avec toujours la meme structure : module, fonction, timestamp, status, code retour, cible, details, message."
>
> *(pointer l'exemple JSON)* "Voici un exemple concret. Le status peut etre OK, WARNING, CRITICAL ou UNKNOWN. Le code retour va de 0 a 3, c'est la convention standard de l'industrie — compatible Nagios et Zabbix."
>
> "Les seuils WARNING sont a 80% pour CPU, RAM et disque. Le timeout par defaut est de 10 secondes."

### Ce que le jury attend :

- Que vous expliquiez **pourquoi cette architecture** (simplicite, independance, integrabilite).
- Que le **contrat JSON** soit clair et concret — c'est LA decision technique du projet.
- Que les **codes retour** soient expliques avec leur signification.
- Que vous mentionniez que c'est un **standard industrie**, pas un choix arbitraire.

### Conseils :

- Ne pas se perdre dans les details du code
- Pointer visuellement le schema et l'exemple JSON
- Le jury doit comprendre en 10 secondes : "format unique partout = facile a integrer"

---

## SLIDE Organisation equipe (Ianis, 1min) — si presente

### Ce qu'il faut dire :

> "On est 4 developpeurs pour 19 heures de projet. On s'est organises autour du contrat JSON commun : on l'a defini ensemble en amont, puis chacun a developpe son module de facon independante."
>
> "Ianis en lead sur le framework, le CLI et la CI/CD. Blaise sur le diagnostic, Ojvind sur le backup, Zaid sur l'audit."
>
> "On a travaille en branches isolees — une par module — avec des pull requests et une review systematique par le lead avant le merge."

### Ce que le jury attend :

- **Qui a fait quoi** — concretement.
- Que la methode de travail soit **structuree** (branches, PRs, reviews).
- Que le contrat commun ait permis le **travail en parallele**.

---

## SLIDE 6 — Module Diagnostic (Blaise, 1min30)

### Ce qu'il faut dire :

> "Mon module repond a la question : est-ce que les services critiques de NTL fonctionnent en ce moment ?"
>
> "J'ai 4 fonctions de verification :"
> - "`check_ad_dns` verifie l'Active Directory et le DNS sur le DC01 — les ports LDAP, DNS et Kerberos, plus une resolution DNS pour confirmer que le service repond vraiment."
> - "`check_mysql` teste la connexion au serveur MySQL qui heberge le WMS — port 3306 et version du serveur."
> - "`check_linux` fait un scan multi-ports sur n'importe quel serveur Linux pour identifier les services actifs."
> - "`check_http` verifie qu'un serveur web repond — status HTTP, header Server, temps de reponse."
>
> *(pointer le schema de decision)* "Chaque verification suit une logique de decision claire. Par exemple pour l'AD : si le serveur est injoignable, c'est UNKNOWN. Si LDAP ne repond pas, c'est CRITICAL. Si LDAP repond mais le DNS est en panne, c'est WARNING. Et si tout va bien, OK."

### Ce que le jury attend :

- Que Blaise comprenne **pourquoi** on teste ces services — pas juste "comment".
  - AD = authentification de tous les employes
  - DNS = resolution de noms, si ca tombe tout tombe
  - MySQL = la base du WMS, coeur de metier
- La **logique de decision** (arbre OK/WARNING/CRITICAL/UNKNOWN).
- Que chaque check retourne un **resultat exploitable**.

### Questions probables pour Blaise :

- "Que se passe-t-il si MySQL ne repond pas ?" → CRITICAL (code 2), erreur dans les details
- "Vous utilisez quelles libs ?" → dnspython, ldap3, socket
- "Pourquoi ne pas utiliser un simple ping ?" → Un ping ne verifie pas que le service repond, juste que la machine est allumee

---

## SLIDE 7 — Module Backup (Ojvind, 1min30)

### Ce qu'il faut dire :

> "Mon module permet a la DSI de lancer une sauvegarde de la base WMS a tout moment, de facon fiable et securisee."
>
> "J'ai 2 fonctions principales :"
> - "`backup_database` fait un dump SQL complet via mysqldump. Si mysqldump n'est pas installe localement, le module bascule automatiquement sur une connexion SSH pour l'executer sur le serveur distant."
> - "`export_table_csv` permet d'exporter une table specifique en CSV — utile pour des extractions ponctuelles."
>
> "J'ai porte une attention particuliere a la securite :"
> - "Le mot de passe MySQL transite par variable d'environnement, jamais en argument de commande — ca evite qu'il apparaisse dans `ps aux` ou dans l'historique."
> - "Le nom de table est valide par regex pour empecher toute injection SQL."
> - "Les chemins de sortie sont proteges contre le path traversal."

### Ce que le jury attend :

- Le **mecanisme de fallback** SSH — ca montre de la robustesse.
- La **securite des credentials** — c'est un sujet sensible, le jury va creuser.
- Que Ojvind sache expliquer **pourquoi** ces choix (pas juste "on a fait ca").

### Questions probables pour Ojvind :

- "Pourquoi pas de compression du dump ?" → "On a priorise la simplicite et la lisibilite du dump pour une V1. La compression est une amelioration possible."
- "Comment vous verifiez l'integrite ?" → Hash SHA256 du fichier, verification taille > 0
- "Pourquoi mysqldump et pas un export logique Python ?" → mysqldump est l'outil standard, il gere les locks et la coherence transactionnelle

---

## SLIDE 8 — Module Audit (Zaid, 1min30)

### Ce qu'il faut dire :

> "Mon module repond a la question : quels equipements du parc sont obsoletes et representent un risque de securite ?"
>
> "Le processus se fait en 4 etapes :"
> 1. "`scan_network` utilise nmap pour scanner une plage IP et detecter les machines actives, leurs ports ouverts et leur OS."
> 2. "`list_os_eol` consulte notre base JSON locale qui contient les dates de fin de support officielles de chaque OS."
> 3. "`audit_from_csv` croise un inventaire CSV — qui contient les machines du parc avec leur OS — avec les dates EOL."
> 4. "`generate_report` produit un rapport trie par urgence : d'abord les OS expires, puis ceux qui expirent bientot, puis les OK."
>
> *(pointer l'exemple de rapport)* "Dans cet exemple, on voit immediatement que SRV-PRINT et PC-QUAI tournent sur des OS expires depuis plus de 2000 jours — ce sont des risques critiques. SRV-FILE expire dans 6 mois — c'est un WARNING. Et DC01 est tranquille jusqu'en 2031."

### Ce que le jury attend :

- Le **pipeline en 4 etapes** — scan, reference, croisement, rapport. C'est methodique.
- La **hierarchisation par risque** — pas juste une liste, un rapport actionnable.
- Que Zaid sache defendre le choix d'une **base JSON locale** vs une API en ligne.

### Questions probables pour Zaid :

- "La base EOL, elle vient d'ou ?" → "Donnees officielles Microsoft et Ubuntu, dans un fichier JSON versionne avec le code. C'est un compromis : pas de dependance reseau, mais maintenance manuelle."
- "Le scan nmap necessite les droits root ?" → "Detection auto, scan degrade sans root avec un WARNING."
- "Pourquoi pas une API comme endoflife.date ?" → "On veut que l'outil fonctionne meme en reseau coupe — coherent avec un outil d'audit de crise."

---

## SLIDE 9A — Lab de test Proxmox (Ianis, 45s)

### Ce qu'il faut dire :

> "Pour valider notre outil en conditions reelles, on a monte un lab sur Proxmox VE — un hyperviseur open source."
>
> "Le lab reproduit l'infra de NTL : un DC01 sous Windows Server 2022 avec Active Directory et DNS, un WMS-DB sous Ubuntu avec MySQL, et des VMs legacy — Windows Server 2012 R2 et Ubuntu 18.04 — specifiquement pour tester la detection des OS en fin de vie."
>
> "Ca nous a permis de tester chaque module sur des machines identiques a la production, sans jamais toucher a l'infra reelle du client."

### Ce que le jury attend :

- Que vous ayez un **environnement de test** — ca montre du professionnalisme.
- Que le lab **reproduise l'infra reelle** — pas un test en local sur localhost.
- Les VMs legacy montrent une **demarche deliberee** de test des cas limites.

---

## SLIDE 9B — CI/CD (Ianis, 45s)

### Ce qu'il faut dire :

> "Chaque commit est verifie automatiquement par notre pipeline GitHub Actions."
>
> "On a 2 jobs en parallele : un job qualite qui execute ruff pour le lint et mypy pour le typage, et un job tests qui lance pytest sur 3 versions de Python — 3.10, 3.11 et 3.12 — pour garantir la compatibilite."
>
> "On a 110 tests, 54% de couverture, et le pipeline tourne en moins de 2 minutes."

### Ce que le jury attend :

- Que la CI soit **reelle et automatisee** — pas un truc fait a la main.
- **3 versions de Python** = on anticipe que la DSI peut avoir differentes versions.
- Les **metriques concretes** (110 tests, 54% couverture) rassurent.

### Question probable :

- "Pourquoi seulement 54% de couverture ?" → "On a concentre les tests sur les chemins critiques et les cas d'erreur. 100% de couverture sur un outil qui interagit avec du reseau et des VMs serait largement du mock — on a prefere des tests qui testent vraiment quelque chose."

---

## SLIDE 10 — Demo live (Tous, 4min)

### Deroulement :

**Ianis (30s)** — Lancement :
> "Je lance l'outil. Vous voyez le menu interactif — la DSI peut naviguer sans documentation."

*(lancer `python src/main.py`, montrer le menu)*

**Blaise (1min)** — Diagnostic :
> "Je vais verifier que l'AD et le DNS du DC01 sont operationnels."

*(Choix 1 → Diagnostic → Verifier AD/DNS → montrer le resultat JSON)*

> "Le resultat est immediat : status OK, les ports LDAP et DNS repondent, la resolution DNS fonctionne. Si un service etait en panne, on aurait un CRITICAL avec le detail de ce qui ne repond pas."

**Ojvind (1min)** — Backup :
> "Je vais sauvegarder la base WMS."

*(Choix 2 → Backup → Backup base de donnees → montrer le fichier genere)*

> "Le dump SQL est cree avec un horodatage. On voit la taille du fichier et son chemin. Le fichier est pret a etre archive par la DSI."

**Zaid (1min)** — Audit :
> "Je vais lister les OS en fin de vie sur le parc."

*(Choix 3 → Audit → Lister dates EOL → montrer le tableau)*

> "Le tableau montre immediatement quels OS sont expires, lesquels approchent de la fin de vie, et lesquels sont OK. La DSI sait instantanement ou sont les risques."

**Ianis (30s)** — Conclusion demo :
> "Tous les resultats sont sauvegardes en JSON horodate dans le dossier output. Ces fichiers sont directement exploitables par n'importe quel outil de supervision."

*(montrer un fichier JSON dans output/)*

### Ce que le jury attend pendant la demo :

- Que **chaque membre commente son propre module** — pas qu'une seule personne parle.
- Que ca **fonctionne** (avoir un plan B : screenshots ou video pre-enregistree).
- Que les **resultats soient lisibles et exploitables** — montrer le JSON.
- Que vous montriez des **cas OK ET des cas d'erreur** si possible.

### Plan B (si le lab est inaccessible) :

- Screenshots reels de l'outil en fonctionnement
- Fichiers JSON de sortie pre-generes a montrer
- Video de la demo enregistree a l'avance
- **Dites-le clairement** : "On a enregistre la demo car le lab n'est pas accessible depuis cette salle, mais l'outil tourne sur notre infrastructure."

---

## SLIDE 11 — Documentation (Ianis, 1min)

### Ce qu'il faut dire :

> "On a produit une documentation complete : un guide d'installation en 5 commandes, 10 documents techniques numerotes qui couvrent de l'architecture au lab, et un cheatsheet d'une page pour l'equipe IT."
>
> "Un administrateur qui recupere le repo Git peut deployer et utiliser l'outil en moins de 5 minutes. C'est ce qui etait demande dans le cahier des charges : un outil que la DSI peut gerer en autonomie."

### Ce que le jury attend :

- Que la doc **permette l'autonomie** de la DSI — c'est explicitement demande.
- Que la doc soit **versionnee avec le code** — pas un PDF envoye par mail.
- Pas besoin de tout lister — juste montrer que c'est complet et utilisable.

---

## SLIDE 12 — Difficultes et compromis (Ianis + equipe, 1min30)

### Ce qu'il faut dire :

> "On assume nos choix et nos compromis."
>
> *(parcourir le tableau en pointant chaque ligne)*
>
> "La **portabilite Windows/Linux** : Python et des librairies cross-platform, valides par la CI sur Ubuntu."
>
> "L'**acces WinRM** : on a fait un fallback gracieux. L'outil fonctionne sans, mais signale le manque — ca n'empeche pas le diagnostic, ca le degrade proprement."
>
> "La **base EOL locale** : c'est un compromis assume. Pas de dependance reseau, l'outil fonctionne meme en cas de panne, mais ca impose une mise a jour manuelle. Pour une V2, une API serait envisageable."
>
> "La **coordination a 4** en 19 heures : le contrat JSON defini en amont a ete la cle. Chacun a pu developper son module en parallele sans bloquer les autres."
>
> "La **securite des credentials** : variables d'environnement, fichier `.env`, zero secret dans le code ou dans les logs."

### Ce que le jury attend :

- **Des compromis ASSUMES, pas des excuses.** La phrase interdite : "on n'a pas eu le temps". La bonne formulation : "on a priorise X parce que Y".
- Que chaque contrainte ait ete **identifiee et traitee** — meme imparfaitement.
- C'est LA slide ou le jury juge votre **maturite professionnelle**.

---

## SLIDE 13 — Bilan et perspectives (Ianis, 1min30)

### Ce qu'il faut dire :

> "On a livre un outil fonctionnel qui repond au cahier des charges."
>
> *(parcourir la checklist)* "3 modules fonctionnels et independants, menu CLI interactif, sorties JSON horodatees avec codes retour, configuration YAML avec gestion des secrets, CI/CD complete, documentation utilisable."
>
> "Le projet en chiffres : 62 commits, 110 tests, 54% de couverture, environ 2500 lignes de Python, 10 documents, 5 VMs de lab."
>
> "Pour les perspectives — si NTL veut aller plus loin :"
> - "Integration directe avec Zabbix — les codes retour sont deja compatibles, ca demande zero modification cote outil."
> - "Planification automatique des backups via cron ou Task Scheduler."
> - "Mise a jour automatique de la base EOL via une API comme endoflife.date."
> - "Extension aux sites distants — les 3 entrepots."
> - "Et eventuellement un dashboard web pour visualiser les resultats."

### Ce que le jury attend :

- Un **bilan factuel** — pas de vantardise, des faits et des chiffres.
- Des **perspectives realistes** qui montrent que l'architecture est pensee pour evoluer.
- Le point cle : les codes retour standard signifient que **l'integration supervision est deja possible** sans toucher au code.

### Le message final :

**"L'outil est livrable aujourd'hui et evoluera demain."**

---

## SLIDE 14 — Questions (Tous, 30min)

### Ce qu'il faut dire :

> "Merci pour votre attention. Nous sommes prets pour vos questions."

### Preparation aux questions — par theme :

#### Architecture & choix techniques

| Question probable | Reponse |
|-------------------|---------|
| "Pourquoi Python et pas Bash/PowerShell ?" | "Portabilite Win+Linux, ecosysteme de libs (paramiko, nmap, ldap3), maintenabilite par une equipe IT qui connait deja Python." |
| "Pourquoi les codes retour 0-3 ?" | "C'est la convention Nagios/Zabbix — un standard industrie. Ca rend l'outil integrable sans adaptation." |
| "Comment la config gere les secrets ?" | "Variables d'environnement via `.env`, substitution `${VAR}` dans le YAML. Jamais de secret en dur dans le code." |
| "Pourquoi pas une interface web ?" | "La DSI a 4 personnes, elle travaille en terminal. Un CLI est plus rapide, plus scriptable, plus leger. Le web est une perspective V2." |

#### Modules (questions croisees)

| Question | Qui repond | Reponse |
|----------|-----------|---------|
| "Si MySQL ne repond pas ?" | Blaise ou Ojvind | "CRITICAL (code 2), erreur dans details, message lisible. Pas de crash." |
| "Le scan nmap necessite root ?" | Zaid | "Detection auto. Sans root, scan degrade + WARNING dans le resultat." |
| "Un backup qui echoue ?" | Ojvind | "CRITICAL, pas de fichier corrompu laisse sur le disque. Le fichier partiel est supprime." |
| "Comment vous gerez un timeout ?" | Tous | "Timeout par defaut de 10s, configurable dans le YAML. Timeout = UNKNOWN (code 3)." |

#### Equipe & methode

| Question | Reponse |
|----------|---------|
| "Comment vous vous etes repartis ?" | "Contrat JSON commun defini ensemble en amont, puis branches isolees par module, merge par le lead apres review." |
| "Quelle a ete la plus grosse difficulte ?" | Chacun repond pour son module. Ianis : coordination. Blaise : AD multi-protocol. Ojvind : securite credentials. Zaid : fiabilite nmap. |
| "Repartition des commits ?" | "Ianis 40, les autres 3-4 chacun. Le lead a fait le framework, la CI, l'integration et les reviews. Le travail de chaque dev est dans son module." |

#### CI/CD

| Question | Reponse |
|----------|---------|
| "Pourquoi 3 versions Python ?" | "La DSI peut avoir differentes versions. On garantit la compatibilite 3.10 a 3.12." |
| "54% de couverture, c'est pas faible ?" | "On a concentre sur les chemins critiques. L'outil interagit avec du reseau et des VMs — tester a 100% serait du mock sans valeur." |
| "Vous faites du deploiement continu ?" | "Non, deploiement manuel pour l'instant. Le CD est une perspective — l'outil est pensé pour etre deploye par la DSI elle-meme." |

---

## REGLES D'OR POUR TOUTE LA SOUTENANCE

1. **Ne JAMAIS lire les slides.** Vous les connaissez par coeur.
2. **Ne JAMAIS dire "on n'a pas eu le temps".** Dire "on a priorise X".
3. **Ne JAMAIS dire "c'est un projet scolaire".** Vous parlez a la DSI de NTL.
4. **Chacun parle pour son module.** Pas qu'Ianis pendant 20 minutes.
5. **Pointer les visuels.** Quand il y a un schema ou un tableau, montrez-le physiquement.
6. **Repondre avec assurance.** Si vous ne savez pas : "C'est un bon point, dans notre V1 on n'a pas couvert ca, mais l'architecture permet de l'ajouter."
7. **Relier au metier.** Chaque choix technique doit etre justifie par un besoin de NTL, pas par un exercice scolaire.
8. **Garder le rythme.** 20 minutes max. Si une diapo prend trop de temps, avancez — le jury pourra revenir en questions.
9. **Demo : avoir un plan B.** Toujours.
10. **Finir proprement.** Pas de "voila c'est fini". Juste : "Merci, on est prets pour vos questions."
