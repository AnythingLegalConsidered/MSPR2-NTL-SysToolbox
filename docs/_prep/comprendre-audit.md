# Comprendre le module Audit -- Guide pour Zaid

> Ce document t'explique tout ce que fait ton module Audit, sans une seule ligne de code Python.
> L'objectif : que tu puisses expliquer chaque partie au jury avec tes propres mots.

---

## 1. L'objectif du module

NordTransit Logistics a un parc informatique avec des serveurs et des postes de travail. Certaines de ces machines tournent sur des systemes d'exploitation qui ne sont plus supportes par leur editeur (Microsoft, Canonical, etc.). Ca veut dire : plus de mises a jour de securite, plus de correctifs. C'est un risque enorme pour l'entreprise.

**Le module Audit sert a repondre a une question simple : "Quelles machines de notre parc sont obsoletes ou vont bientot le devenir ?"**

Il fait ca en trois temps :
1. Il scanne le reseau pour decouvrir les machines actives
2. Il croise l'inventaire des machines avec une base de donnees des dates de fin de support
3. Il genere un rapport qui dit clairement ce qui est bon, ce qui est a risque, et ce qui est critique

---

## 2. Le pipeline en 4 etapes

Le module fonctionne comme une chaine de montage. Chaque etape fait un travail precis et passe le relais a la suivante.

### Etape 1 : `scan_network` -- Decouvrir les machines sur le reseau

**Ce que ca fait :**
On donne une plage d'adresses IP au module (par exemple `192.168.10.0/24`, ce qui represente toutes les adresses de 192.168.10.1 a 192.168.10.254). Le module utilise nmap (un outil de scan reseau) pour envoyer des paquets a chaque adresse et voir qui repond.

Pour chaque machine qui repond, on regarde aussi quels ports sont ouverts. Un port ouvert, c'est comme une porte d'entree vers un service : le port 22 c'est SSH (acces distant), le port 80 c'est un serveur web, le port 3306 c'est MySQL (base de donnees), etc.

**Entree :** Une plage reseau (ex : `172.16.135.0/24`) + la liste des ports a verifier (configurable, par defaut : 22, 80, 443, 3306, 5432, 8006, 8080)

**Sortie :** Une liste de machines avec pour chacune :
- Son adresse IP
- Son nom d'hote (si disponible)
- Ses ports ouverts et les services associes
- Ses categories (web, base de donnees, etc.)

**Exemple concret :** On scanne le reseau du lab. Le scan trouve 5 machines actives. DC01 (192.168.10.10) a le port 53 (DNS) ouvert, WMS-DB (192.168.10.21) a le port 3306 (MySQL) ouvert, etc.

### Etape 2 : `list_os_eol` -- Consulter la base des dates de fin de support

**Ce que ca fait :**
Le module lit le fichier `eol_database.json` qui contient la liste des systemes d'exploitation avec leur date de fin de support. Pour chaque OS, il compare la date EOL avec la date du jour et dit : "celui-la est encore supporte" ou "celui-la est en fin de vie".

**Entree :** Le fichier `data/eol_database.json`

**Sortie :** La liste complete des OS avec pour chacun :
- Le nom de l'OS (ex : "Windows Server 2012 R2")
- La date de fin de support (ex : "2023-10-10")
- Son statut : est-ce qu'il est en fin de vie ou pas
- L'editeur (Microsoft, Canonical, Debian, Red Hat)
- La categorie (serveur ou poste de travail)

**Exemple concret :** Aujourd'hui on est en avril 2026. Le module lit la base et constate que Windows Server 2008 R2 (fin de support le 14/01/2020) est en fin de vie depuis plus de 6 ans. Windows Server 2022 (fin de support le 14/10/2031) est encore bon pour 5 ans.

### Etape 3 : `audit_from_csv` -- Croiser l'inventaire avec les dates EOL

**Ce que ca fait :**
C'est le coeur du module. On prend le fichier CSV d'inventaire (la liste de toutes les machines de l'entreprise) et pour chaque machine :

1. On recupere son nom, son OS, sa version et son role
2. Si on a son adresse IP, on teste si elle repond (ping sur le port 22, puis sur le port 80 en secours)
3. Si on n'a pas son IP mais qu'on a son nom, on essaie de la retrouver via le DNS
4. On cherche son OS dans la base EOL pour savoir s'il est encore supporte

**Le croisement fonctionne comme ca :**
Le fichier CSV dit par exemple que la machine SRV-FILE tourne sous "Windows Server 2012 R2". Le module va chercher "Windows Server 2012 R2" dans la base EOL, trouve la date "2023-10-10", compare avec aujourd'hui, et conclut : "fin de vie depuis 2023, c'est critique".

**Entree :** Le fichier CSV d'inventaire (ex : `data/sample_inventory.csv`) + la base EOL

**Sortie :** Pour chaque machine :
- Nom d'hote, IP, OS complet, role
- Est-ce qu'elle repond sur le reseau (joignable ou pas)
- Est-ce que son OS est en fin de vie

Plus un resume global : combien de machines au total, combien joignables, combien en fin de vie.

**Exemple concret avec l'inventaire NTL :**

| Machine | OS | Role | EOL ? |
|---------|------|------|-------|
| DC01 | Windows Server 2022 | Controleur de domaine | Non (2031) |
| SRV-FILE | Windows Server 2012 R2 | Serveur de fichiers | Oui (2023) |
| SRV-PRINT | Windows Server 2008 R2 | Serveur d'impression | Oui (2020) |
| PC-QUAI-WH1 | Windows 7 | Terminal quai Lens | Oui (2020) |
| WMS-DB | Ubuntu 20.04 LTS | Base de donnees MySQL | Oui (2025) |
| SRV-BACKUP | Ubuntu 16.04 LTS | Scripts de sauvegarde | Oui (2021) |

### Etape 4 : `generate_report` -- Generer le rapport complet

**Ce que ca fait :**
Cette etape lance les trois precedentes dans l'ordre, rassemble tous les resultats, et les sauvegarde dans un fichier JSON horodate dans le dossier `output/reports/`.

**Le rapport contient :**
- La date de generation
- La plage reseau scannee
- Les resultats du scan reseau (quelles machines repondent)
- Les resultats de l'inventaire croise avec les dates EOL
- La liste complete des OS et leur statut
- Un resume avec les chiffres cles

**Le tri dans le rapport :**
Le rapport classe les machines par niveau de risque :
- **EXPIRE** : l'OS a depasse sa date de fin de support. C'est critique, il faut migrer.
- **BIENTOT** : l'OS arrive en fin de support dans les prochains mois. Il faut planifier la migration.
- **OK** : l'OS est encore supporte, pas d'action immediate.

Les machines les plus critiques apparaissent en premier pour que l'administrateur voie tout de suite ou agir.

**Nom du fichier de sortie :** `output/reports/audit_report_20260406_143022.json` (la date et l'heure sont dans le nom pour garder un historique)

---

## 3. La base EOL (`eol_database.json`)

### C'est quoi ?

EOL = End Of Life = Fin de Vie. C'est la date a partir de laquelle un editeur arrete de fournir des mises a jour de securite pour un systeme d'exploitation.

Le fichier `eol_database.json` est un dictionnaire qui associe chaque OS a ses informations :
- **eol_date** : la date de fin du support standard
- **eol_extended** : la date de fin du support etendu (payant, pour les entreprises qui veulent quelques annees de plus)
- **vendor** : l'editeur (Microsoft, Canonical, Debian, Red Hat)
- **category** : serveur ou poste de travail

### D'ou viennent les dates ?

Les dates sont recuperees sur les sites officiels des editeurs :
- Microsoft : pages de cycle de vie des produits
- Canonical (Ubuntu) : pages de support LTS
- Debian : wiki officiel des releases
- Red Hat / CentOS : pages de cycle de vie

### Pourquoi un fichier local et pas une API ?

Trois raisons :
1. **Fiabilite** : pas de dependance a un service externe. Si l'API est en panne, notre outil marche quand meme.
2. **Securite** : dans un environnement d'entreprise, les outils d'admin n'ont pas toujours acces a Internet. Un fichier local fonctionne en reseau isole.
3. **Controle** : on maitrise exactement les donnees. Pas de surprise si une API change son format ou ses tarifs.

Le compromis, c'est qu'il faut mettre a jour le fichier manuellement quand un nouvel OS sort ou quand une date change. Mais les dates EOL ne changent que rarement, donc c'est acceptable.

### Ce que contient la base aujourd'hui

| OS | Fin de support | Statut (avril 2026) |
|----|----------------|---------------------|
| Windows Server 2008 R2 | 14/01/2020 | EXPIRE depuis 6 ans |
| Windows 7 | 14/01/2020 | EXPIRE depuis 6 ans |
| Ubuntu 16.04 LTS | 01/04/2021 | EXPIRE depuis 5 ans |
| Windows Server 2012 | 10/10/2023 | EXPIRE depuis 2.5 ans |
| Windows Server 2012 R2 | 10/10/2023 | EXPIRE depuis 2.5 ans |
| Ubuntu 18.04 LTS | 01/04/2023 | EXPIRE depuis 3 ans |
| CentOS 7 | 30/06/2024 | EXPIRE depuis presque 2 ans |
| Debian 10 | 30/06/2024 | EXPIRE depuis presque 2 ans |
| Ubuntu 20.04 LTS | 02/04/2025 | EXPIRE depuis 1 an |
| Windows 10 | 14/10/2025 | EXPIRE depuis ~6 mois |
| Debian 11 | 01/06/2026 | BIENTOT (dans 2 mois) |
| Windows Server 2016 | 12/01/2027 | OK (encore ~9 mois) |
| Ubuntu 22.04 LTS | 01/04/2027 | OK |
| Windows 11 | 14/10/2027 | OK |
| Windows Server 2019 | 09/01/2029 | OK |
| Ubuntu 24.04 LTS | 01/04/2029 | OK |
| Windows Server 2022 | 14/10/2031 | OK |

---

## 4. Le scan reseau : comment ca marche

### nmap, c'est quoi ?

nmap (Network Mapper) est un outil open source de scan reseau. C'est le couteau suisse de la decouverte reseau, utilise par les administrateurs systeme et les pentesters du monde entier.

Concretement, nmap envoie des paquets reseau a des adresses IP et analyse les reponses pour savoir :
- Est-ce qu'une machine est allumee et connectee ?
- Quels ports sont ouverts (donc quels services tournent) ?
- Parfois, quel OS est installe (detection d'OS)

Notre module utilise `python-nmap`, une bibliotheque Python qui pilote nmap en arriere-plan.

### Pourquoi les droits root/administrateur ?

Certains types de scan nmap necessitent des droits eleves car ils manipulent des paquets reseau a bas niveau (raw sockets). Sans droits root/admin, nmap utilise un mode degrade : il fait un simple "connect scan" au lieu d'un "SYN scan". Ca marche, mais c'est plus lent et plus bruyant sur le reseau.

Dans notre cas, le scan fonctionne meme sans droits root, mais il sera moins performant. C'est ce qu'on appelle le **scan degrade** : le module ne plante pas, il s'adapte.

### Les options du scan

- **`-T4`** : vitesse de scan agressive (rapide mais pas trop pour ne pas saturer le reseau)
- **`--host-timeout`** : delai maximum par machine (configurable, 10 secondes par defaut). Si une machine ne repond pas dans ce delai, on passe a la suivante.

### Securite du scan

Le module valide la plage reseau avant de la passer a nmap pour empecher les injections de commandes. On ne peut pas mettre n'importe quoi comme adresse, ca doit etre un format IP/CIDR valide.

---

## 5. Vocabulaire technique a connaitre

| Terme | Explication |
|-------|-------------|
| **EOL (End Of Life)** | Date a laquelle un editeur arrete le support d'un logiciel. Plus de mises a jour de securite apres cette date. |
| **nmap** | Outil de scan reseau qui decouvre les machines et les services sur un reseau. |
| **CIDR** | Notation pour decrire une plage d'adresses IP. Par exemple `192.168.10.0/24` = toutes les adresses de 192.168.10.0 a 192.168.10.255 (256 adresses). Le `/24` indique que les 24 premiers bits sont fixes. |
| **Scan reseau** | Action d'envoyer des paquets a des adresses IP pour decouvrir quelles machines sont actives et quels services elles proposent. |
| **Port** | Un numero (de 1 a 65535) qui identifie un service sur une machine. Port 22 = SSH, port 80 = HTTP, port 443 = HTTPS, port 3306 = MySQL. |
| **Fin de support** | Synonyme d'EOL. Moment ou l'editeur ne corrige plus les failles de securite. |
| **CSV** | Format de fichier texte ou les donnees sont separees par des virgules. C'est notre format d'inventaire. |
| **JSON** | Format de fichier structure pour echanger des donnees. C'est le format de notre base EOL et de nos rapports. |
| **DNS** | Systeme qui traduit les noms de machines (ex : DC01) en adresses IP (ex : 192.168.10.10). |
| **build_result** | La fonction standard du projet qui formate tous les resultats de la meme facon (statut, code de sortie, donnees, message). |
| **Exit code** | Code numerique qui indique le resultat : 0 = OK, 1 = WARNING, 2 = CRITICAL, 3 = UNKNOWN. |

---

## 6. Questions que le jury peut poser (et les reponses)

### "Qu'est-ce que fait le module Audit ?"

> Le module Audit identifie les machines du parc informatique qui tournent sur des systemes d'exploitation obsoletes, c'est-a-dire en fin de support editeur. Il scanne le reseau, croise un inventaire CSV avec une base de donnees de dates de fin de vie, et genere un rapport qui classe les machines par niveau de criticite.

### "Pourquoi c'est important de detecter les OS en fin de vie ?"

> Un OS en fin de vie ne recoit plus de correctifs de securite. Ca veut dire que si une faille est decouverte, elle ne sera jamais corrigee. C'est une porte ouverte pour les attaquants. Pour une entreprise de logistique comme NTL qui gere des donnees clients et des flux de marchandises, c'est un risque majeur de cyberattaque, de fuite de donnees, ou de non-conformite reglementaire.

### "Comment fonctionne le croisement inventaire/EOL ?"

> On lit le fichier CSV qui contient la liste de toutes les machines avec leur nom, leur OS et leur version. Pour chaque machine, on concatene le nom de l'OS et sa version (par exemple "Windows Server" + "2012 R2" donne "Windows Server 2012 R2"), puis on cherche cette chaine dans la base EOL. Si on la trouve et que la date de fin de support est passee, la machine est marquee comme obsolete.

### "Pourquoi utiliser un fichier JSON local plutot qu'une API comme endoflife.date ?"

> Trois raisons : fiabilite (pas de dependance externe), securite (ca marche en reseau isole, ce qui est courant en entreprise), et controle (on maitrise nos donnees). Les dates EOL changent rarement donc la maintenance est minimale.

### "Que se passe-t-il si nmap n'est pas installe ?"

> Le module ne plante pas. Il detecte l'absence de python-nmap et retourne un resultat avec un code UNKNOWN et un message d'erreur explicite. Les autres fonctions (inventaire CSV, consultation EOL) continuent de fonctionner normalement.

### "Comment le module gere les erreurs ?"

> Chaque fonction est enveloppee dans un bloc try/except. Si quelque chose echoue (fichier introuvable, nmap pas installe, machine injoignable...), le module retourne un resultat standardise avec un statut UNKNOWN ou CRITICAL et un message d'erreur. Il ne plante jamais, c'est une regle du projet.

### "Qu'est-ce que le CIDR /24 ?"

> C'est une notation qui definit la taille d'un reseau. /24 signifie que les 24 premiers bits de l'adresse sont fixes, ce qui laisse 8 bits pour les hotes, soit 256 adresses (de .0 a .255, en pratique 254 utilisables). C'est le format le plus courant pour un reseau local d'entreprise.

### "Comment le rapport est-il structure ?"

> C'est un fichier JSON horodate qui contient quatre sections : les resultats du scan reseau, les donnees de la base EOL, les resultats de l'audit d'inventaire, et un resume avec les chiffres cles (nombre de machines decouvertes, nombre joignables, nombre en fin de vie). Le fichier est sauvegarde dans output/reports/ avec la date et l'heure dans le nom.

### "Pourquoi tester le port 22 puis le port 80 pour verifier si une machine est joignable ?"

> Le port 22 (SSH) est le plus courant sur les serveurs Linux. Le port 80 (HTTP) est un bon fallback car beaucoup de machines ont un serveur web. Si le port 22 est ferme (par exemple sur un serveur Windows qui n'a pas SSH), on essaie le port 80 avant de conclure que la machine est injoignable. Ca evite les faux negatifs.

### "Quels sont les OS les plus critiques dans l'inventaire NTL ?"

> SRV-PRINT tourne sur Windows Server 2008 R2 (fin de support en 2020, ca fait 6 ans !), et les deux terminaux de quai PC-QUAI-WH1 et WH2 sont sous Windows 7 (meme date). Ce sont les cas les plus urgents. Ensuite, SRV-BACKUP est sous Ubuntu 16.04 (fin de support 2021) et SRV-FILE sous Windows Server 2012 R2 (fin de support 2023).

### "Comment tu ajouterais un nouvel OS a la base ?"

> C'est simple : j'ouvre le fichier `eol_database.json` et j'ajoute une entree avec le nom de l'OS, la date de fin de support, la date de support etendu (si applicable), l'editeur et la categorie (serveur ou desktop). Pas besoin de toucher au code Python.

---

*Document genere pour la preparation de la soutenance MSPR -- Avril 2026*
