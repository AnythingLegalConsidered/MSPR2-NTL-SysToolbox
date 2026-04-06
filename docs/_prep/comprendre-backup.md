# Comprendre le module Backup -- Guide pour Ojvind

Ce document t'explique tout ce que fait ton module Backup **sans avoir besoin de lire une seule ligne de Python**. L'objectif : que tu puisses l'expliquer clairement au jury, avec tes mots.

---

## 1. L'objectif du module

NordTransit Logistics utilise une base de donnees MySQL appelee **WMS** (Warehouse Management System). C'est la base qui gere les expeditions, les stocks, les commandes, etc.

Ton module fait deux choses :

- **Sauvegarder toute la base** dans un fichier SQL (un "dump")
- **Exporter une table specifique** dans un fichier CSV (lisible dans Excel)

En gros : on prend les donnees critiques de l'entreprise et on les met en securite dans des fichiers locaux.

---

## 2. Les deux fonctions

### 2.1 backup_database -- Sauvegarder toute la base

**Ce qu'elle fait** : elle lance l'outil `mysqldump` pour copier l'integralite d'une base de donnees MySQL dans un fichier `.sql`.

**Les etapes dans l'ordre** :

1. Elle lit la configuration (adresse du serveur MySQL, port, utilisateur, mot de passe, nom de la base)
2. Elle verifie que le nom de la base est valide (pas de caracteres bizarres)
3. Elle verifie que le dossier de sortie est autorise (pas d'ecriture n'importe ou)
4. Elle cree le dossier `output/backups/` s'il n'existe pas
5. Elle genere un nom de fichier avec la date et l'heure, par exemple : `wms_20260406_143022.sql`
6. Elle lance la commande `mysqldump` avec les parametres de connexion
7. Le mot de passe MySQL est passe via une **variable d'environnement** (pas en argument de commande)
8. Si tout va bien, le resultat du dump est ecrit dans le fichier
9. Elle renvoie un resultat standardise avec le chemin du fichier et sa taille

**Le mecanisme de fallback SSH** :

Si `mysqldump` n'est pas installe sur la machine locale (erreur "fichier introuvable"), le module ne s'arrete pas la. Il tente un **plan B** :

- Il se connecte au serveur MySQL **a distance via SSH** (avec la librairie Paramiko)
- Il execute `mysqldump` directement **sur le serveur distant**
- Il recupere le resultat et l'ecrit dans le meme fichier local

C'est transparent : le fichier de sortie est le meme, que le dump ait ete fait en local ou via SSH.

**Fichier de sortie** : `output/backups/wms_20260406_143022.sql`

**Quand est-ce OK, CRITICAL ou UNKNOWN ?**

| Resultat | Quand ? |
|----------|---------|
| **OK** | Le dump a reussi (en local ou via SSH), le fichier est cree |
| **CRITICAL** | Acces refuse a la base, erreur mysqldump, SSH echoue, ou toute autre erreur |
| **UNKNOWN** | Timeout (le dump prend trop de temps) ou action non reconnue |

**Exemple concret de resultat OK** :

```
Module   : backup
Fonction : backup_database
Status   : OK
Cible    : wms
Message  : Backup wms sauvegarde: output/backups/wms_20260406_143022.sql (245760 octets)
Details  : dump_path, size_bytes, database
```

---

### 2.2 export_table_csv -- Exporter une table en CSV

**Ce qu'elle fait** : elle se connecte a la base MySQL, lit tout le contenu d'une table, et l'ecrit dans un fichier CSV.

**Les etapes dans l'ordre** :

1. Elle lit la configuration MySQL depuis le fichier de config
2. Elle verifie que le nom de la table est valide (lettres, chiffres, underscores uniquement)
3. Elle verifie que le dossier de sortie est autorise
4. Elle cree le dossier `output/exports/` s'il n'existe pas
5. Elle se connecte a la base MySQL via le connecteur Python (pas via la ligne de commande cette fois)
6. Elle execute un `SELECT * FROM la_table` pour recuperer toutes les lignes
7. Elle recupere les noms des colonnes et toutes les donnees
8. Elle ferme la connexion a la base
9. Elle ecrit le tout dans un fichier CSV (avec les en-tetes en premiere ligne)
10. Elle renvoie le resultat avec le nombre de lignes exportees

**Fichier de sortie** : `output/exports/shipments_20260406_143022.csv`

**Quand est-ce OK, CRITICAL ou UNKNOWN ?**

| Resultat | Quand ? |
|----------|---------|
| **OK** | L'export a reussi, le CSV est cree |
| **CRITICAL** | Acces refuse, table introuvable, ou autre erreur |
| **UNKNOWN** | Serveur MySQL injoignable (connexion refusee, timeout) |

**Exemple concret de resultat OK** :

```
Module   : backup
Fonction : export_table_csv
Status   : OK
Cible    : shipments
Message  : Export shipments: 1523 lignes -> output/exports/shipments_20260406_143022.csv
Details  : csv_path, table, database, row_count, columns
```

---

## 3. Les 4 mesures de securite

### 3.1 Variable d'environnement MYSQL_PWD

**Le probleme** : quand tu lances une commande en ligne de commande, tout ce que tu tapes est visible. Si quelqu'un fait un `ps aux` (qui liste les processus en cours), il verrait le mot de passe en clair dans la commande.

**La solution** : au lieu de passer le mot de passe en argument (`mysqldump --password=monmotdepasse`), on le met dans une **variable d'environnement** appelee `MYSQL_PWD`. C'est la methode recommandee par MySQL pour les outils automatises. Ce n'est pas parfait (un admin root pourrait quand meme le voir via `/proc`), mais c'est beaucoup mieux que de l'afficher dans la liste des processus.

### 3.2 Regex sur les noms de tables (anti-injection SQL)

**Le probleme** : imagine qu'un utilisateur malveillant entre comme nom de table : `shipments; DROP DATABASE wms;`. Si on utilise ce texte tel quel dans une requete SQL, ca pourrait detruire la base de donnees. C'est ce qu'on appelle une **injection SQL**.

**La solution** : avant d'utiliser un nom de table ou de base, le module verifie qu'il respecte un format strict : uniquement des lettres, chiffres et underscores, 64 caracteres maximum, et il doit commencer par une lettre ou un underscore. Si le nom ne respecte pas ce format, le module refuse de continuer. Aucun caractere special ne passe.

### 3.3 Protection path traversal

**Le probleme** : un utilisateur pourrait essayer de configurer le dossier de sortie comme `../../etc/` pour ecrire des fichiers n'importe ou sur le serveur. C'est ce qu'on appelle du **path traversal**.

**La solution** : le module utilise une fonction de validation qui verifie que le chemin de sortie reste bien **a l'interieur d'un dossier autorise**. Il "resout" le chemin complet (en suivant les liens symboliques, en eliminant les `..`) puis verifie qu'il est bien un sous-dossier du repertoire courant ou du dossier de sortie configure. Si ce n'est pas le cas, il refuse.

### 3.4 Fallback SSH

Ce n'est pas juste une mesure de confort, c'est aussi une mesure de **resilience**. Si l'outil `mysqldump` n'est pas installe sur le poste d'administration, plutot que d'echouer betement, le module se connecte au serveur distant via SSH et execute le dump la-bas. Ca garantit que la sauvegarde peut etre faite meme depuis une machine qui n'a pas les outils MySQL installes. Et le mot de passe MySQL est aussi protege cote SSH (via `MYSQL_PWD` et `shlex.quote` pour eviter l'injection de commandes shell).

---

## 4. Vocabulaire technique a connaitre

| Terme | Explication simple |
|-------|-------------------|
| **mysqldump** | Outil en ligne de commande fourni avec MySQL. Il lit toute une base de donnees et genere un fichier texte contenant toutes les commandes SQL necessaires pour la recreer a l'identique. C'est l'outil standard pour faire des sauvegardes MySQL. |
| **Dump SQL** | Le fichier produit par mysqldump. C'est un fichier `.sql` qui contient des instructions `CREATE TABLE`, `INSERT INTO`, etc. Si tu le rejoues sur un serveur MySQL vide, tu retrouves ta base complete. |
| **CSV** | Comma-Separated Values. Un format de fichier texte ou chaque ligne est un enregistrement et les valeurs sont separees par des virgules. Lisible dans Excel, Google Sheets, ou n'importe quel tableur. |
| **SHA256** | Un algorithme de hachage. Il produit une "empreinte" unique pour un fichier. Si un seul octet change dans le fichier, le hash sera completement different. Ca permet de verifier l'integrite d'un fichier. (Utilise dans d'autres parties du projet.) |
| **SSH** | Secure Shell. Un protocole pour se connecter a distance a un serveur de maniere securisee (connexion chiffree). Le module l'utilise via la librairie Paramiko pour executer des commandes sur le serveur MySQL quand mysqldump n'est pas disponible en local. |
| **Injection SQL** | Une attaque ou un utilisateur malveillant insere du code SQL dans un champ de saisie pour manipuler la base de donnees (lire, modifier ou supprimer des donnees). Le module s'en protege en validant les noms de tables avec une regex stricte. |
| **Path traversal** | Une attaque ou un utilisateur utilise des `..` dans un chemin de fichier pour sortir du dossier prevu et acceder a d'autres fichiers du systeme. Le module s'en protege en verifiant que le chemin reste dans un dossier autorise. |

---

## 5. Questions que le jury peut poser et reponses

### "Pourquoi avoir choisi mysqldump plutot qu'une autre methode de sauvegarde ?"

mysqldump est l'outil officiel de MySQL, installe par defaut avec le serveur. Il produit un dump SQL portable qu'on peut restaurer sur n'importe quel serveur MySQL, meme d'une version differente. C'est la methode la plus universelle et la plus simple pour une PME. Les options `--single-transaction` et `--routines` permettent de faire le dump sans bloquer les utilisateurs et en incluant les procedures stockees.

### "Que se passe-t-il si le serveur MySQL est injoignable ?"

Pour le dump : la commande mysqldump echoue, et le module renvoie un resultat CRITICAL avec le message d'erreur. Pour l'export CSV : le connecteur Python n'arrive pas a se connecter, et le module renvoie UNKNOWN avec le message "serveur MySQL injoignable". Dans les deux cas, il n'y a pas de crash, le module retourne toujours un resultat propre.

### "Comment tu geres le mot de passe MySQL ?"

Le mot de passe n'est jamais passe en argument de commande, parce que ca le rendrait visible dans la liste des processus (`ps aux`). A la place, on utilise la variable d'environnement `MYSQL_PWD`, qui est la methode recommandee par la documentation officielle de MySQL pour les scripts automatises.

### "C'est quoi le fallback SSH ? Pourquoi c'est necessaire ?"

Le fallback SSH, c'est le plan B. Si `mysqldump` n'est pas installe sur la machine depuis laquelle on lance le script (par exemple un poste d'administration Windows), le module se connecte au serveur MySQL via SSH et execute `mysqldump` directement la-bas. Ca assure que la sauvegarde fonctionne meme si les outils MySQL ne sont pas installes localement. C'est une question de resilience.

### "Comment tu te proteges contre l'injection SQL ?"

Avant d'utiliser un nom de table ou de base de donnees dans une commande, on le valide avec une expression reguliere stricte : uniquement des lettres, des chiffres et des underscores, maximum 64 caracteres. Si le nom ne correspond pas, le module refuse de continuer. Ca empeche toute injection de code SQL ou de commandes shell.

### "Comment tu te proteges contre le path traversal ?"

Le dossier de sortie est valide avant toute ecriture. Le module resout le chemin complet (en eliminant les `..` et en suivant les liens symboliques), puis verifie qu'il se trouve bien sous un dossier autorise. Si quelqu'un essaie de configurer un chemin comme `../../etc/`, la validation echoue et le module refuse de continuer.

### "Quelle est la difference entre backup_database et export_table_csv ?"

`backup_database` sauvegarde **toute la base** dans un fichier SQL. C'est une sauvegarde complete qu'on peut restaurer. `export_table_csv` exporte **une seule table** dans un fichier CSV. C'est utile pour de l'analyse, du reporting, ou pour envoyer des donnees a quelqu'un qui n'a pas acces a MySQL.

### "Que se passe-t-il si la table demandee n'existe pas ?"

Le module renvoie un resultat CRITICAL avec le message "Table 'xxx' introuvable dans wms". Il ne crashe pas, il gere proprement l'erreur et retourne un resultat standardise.

### "C'est quoi build_result et pourquoi vous l'utilisez ?"

`build_result()` est une fonction partagee par tous les modules du projet. Elle garantit que chaque resultat a toujours le meme format : module, fonction, timestamp, status (OK/WARNING/CRITICAL/UNKNOWN), exit_code, cible, details et message. Ca permet d'uniformiser les sorties et de les traiter automatiquement (affichage, logs, export JSON). C'est le **contrat commun** de l'application.

### "Tu peux me decrire un scenario concret d'utilisation ?"

Scenario : l'administrateur de NordTransit veut faire une sauvegarde de la base WMS avant une mise a jour. Il lance l'outil, choisit "Backup", puis "Sauvegarder la base". Le module se connecte au serveur MySQL sur 192.168.10.21, execute mysqldump, et ecrit le fichier `wms_20260406_143022.sql` dans le dossier `output/backups/`. Il affiche "OK - 245 Ko sauvegardés". Si le lendemain il y a un probleme, on peut restaurer la base a partir de ce fichier.
