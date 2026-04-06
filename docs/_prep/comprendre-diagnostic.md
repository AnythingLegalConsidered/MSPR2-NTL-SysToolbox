# Comprendre le module Diagnostic

Guide de vulgarisation pour Blaise -- pour pouvoir expliquer le module au jury sans avoir besoin de lire le code Python.

---

## 1. L'objectif du module

Le module Diagnostic, c'est le "docteur" de NTL-SysToolbox. Son boulot : **verifier que les services critiques de NordTransit Logistics fonctionnent correctement**. Il va toquer a la porte de chaque serveur, verifier que les bons services repondent, et donner un verdict : tout va bien, il y a un souci, ou c'est en panne.

Concretement, il repond a la question : **"Est-ce que mon infrastructure tourne normalement en ce moment ?"**

Il fait ca sans mot de passe pour la plupart des checks (sauf WinRM qui est optionnel). Il se contente de frapper aux portes (les ports reseau) et de regarder si quelqu'un repond.

---

## 2. Les 4 fonctions du module

### 2.1 check_ad_dns -- Verifier le controleur de domaine Windows

**Ce qu'elle fait :** Elle verifie que le serveur Active Directory / DNS de l'entreprise fonctionne. C'est LE serveur critique : si lui tombe, plus personne ne peut se connecter a son poste, plus de resolution de noms, plus rien.

**Quelle machine :** Le controleur de domaine DC01 (192.168.10.10, Windows Server 2022).

**Ce qu'elle regarde, etape par etape :**

1. **Resolution DNS** -- Elle demande au serveur "est-ce que tu sais resoudre le nom `ntl.local` ?" Si le serveur DNS repond avec une adresse IP, c'est bon.

2. **Ports critiques et importants** -- Elle verifie que ces ports sont ouverts :
   - Port 53 (DNS) -- le service de resolution de noms
   - Port 88 (Kerberos) -- le service d'authentification
   - Port 389 (LDAP) -- l'annuaire des utilisateurs
   - Port 445 (SMB) -- le partage de fichiers Windows
   - Port 3268 (LDAP Global Catalog) -- l'annuaire etendu pour les grandes infras

3. **Connexion LDAP** -- Elle tente une vraie connexion a l'annuaire LDAP pour verifier qu'il repond bien (pas juste que le port est ouvert, mais que le service derriere fonctionne).

4. **Services Windows via WinRM** (optionnel) -- Si des identifiants sont configures, elle se connecte au serveur Windows et verifie que les services NTDS (Active Directory), DNS et Netlogon tournent. Si pas d'identifiants, cette etape est simplement ignoree.

**Verdicts :**
- **OK** : DNS repond, tous les ports sont ouverts, LDAP fonctionne
- **WARNING** : un port important (445 ou 3268) est ferme, mais les critiques sont OK
- **CRITICAL** : le DNS ne repond pas, OU un port critique (53, 88, 389) est ferme, OU LDAP ne repond pas
- **UNKNOWN** : une erreur inattendue s'est produite (ex: probleme reseau complet)

**Exemple de resultat :**
> "AD/DNS check OK sur 192.168.10.10"
> DNS resolu : ntl.local -> 192.168.10.10
> Ports : 53 ouvert, 88 ouvert, 389 ouvert, 445 ouvert, 3268 ouvert
> LDAP : connecte avec succes

---

### 2.2 check_mysql -- Verifier la base de donnees

**Ce qu'elle fait :** Elle verifie que le serveur MySQL est accessible et recupere sa version. Le tout sans avoir besoin de mot de passe -- elle se contente de lire le message de bienvenue que MySQL envoie automatiquement quand on se connecte.

**Quelle machine :** Le serveur WMS-DB (192.168.10.21, Ubuntu 20.04) qui heberge la base de donnees du systeme de gestion d'entrepot (WMS = Warehouse Management System).

**Ce qu'elle regarde :**

1. Elle essaie d'ouvrir une connexion sur le port 3306 (le port standard de MySQL)
2. Si le port repond, elle lit le "paquet de bienvenue" de MySQL qui contient la version du serveur
3. Si elle n'arrive pas a lire la version MySQL, elle essaie au moins de lire la banniere generique du service

**Verdicts :**
- **OK** : le port 3306 est ouvert et MySQL repond (bonus : on a la version)
- **CRITICAL** : le port 3306 ne repond pas -- la base de donnees est injoignable
- **UNKNOWN** : erreur inattendue pendant le check

**Exemple de resultat :**
> "MySQL accessible sur 192.168.10.21:3306 (version 8.0.36)"

---

### 2.3 check_linux -- Scanner les services d'un serveur Linux

**Ce qu'elle fait :** Elle scanne une liste de ports sur un serveur Linux pour decouvrir quels services tournent. C'est comme faire le tour d'un immeuble et noter quelles fenetres sont eclairees.

**Quelles machines :** N'importe quel serveur Linux du parc -- typiquement SRV-LEGACY (192.168.10.18, Ubuntu 18.04) ou WMS-DB. On peut aussi l'utiliser sur le serveur Proxmox.

**Ce qu'elle regarde :**

Elle teste ces 7 ports par defaut :
| Port | Service | A quoi ca sert |
|------|---------|----------------|
| 22 | SSH | Acces a distance en ligne de commande |
| 80 | HTTP | Site web / application web |
| 443 | HTTPS | Site web securise |
| 3306 | MySQL | Base de donnees MySQL |
| 5432 | PostgreSQL | Base de donnees PostgreSQL |
| 8006 | Proxmox | Interface d'administration Proxmox |
| 8080 | HTTP-Proxy | Serveur web alternatif / proxy |

Pour chaque port, elle envoie une connexion TCP et attend la reponse (2 secondes max par port). Elle classe ensuite les services trouves par categorie.

**Verdicts :**
- **OK** : au moins un service a ete detecte (avec la liste des services trouves)
- **CRITICAL** : aucun port ne repond -- le serveur semble eteint ou isole du reseau
- **UNKNOWN** : erreur inattendue

**Exemple de resultat :**
> "3 service(s) trouves sur 192.168.10.21: MySQL, SSH, HTTP"

---

### 2.4 check_http -- Verifier un service web

**Ce qu'elle fait :** Elle envoie une requete HTTP (comme quand tu tapes une URL dans ton navigateur) et verifie que le serveur web repond correctement. Elle mesure aussi le temps de reponse.

**Quelles machines :** Tout serveur hebergeant un service web -- par exemple l'interface Proxmox (port 8006), un serveur Apache/Nginx, ou une application interne.

**Ce qu'elle regarde :**

1. Elle construit une URL (http:// ou https:// selon le port)
2. Elle envoie une requete GET sur le chemin "/" (la page d'accueil)
3. Elle note : le code de statut HTTP, le nom du serveur, la taille de la reponse, et le temps de reponse en millisecondes

Note : pour les ports connus comme HTTPS (443, 8443, etc.), elle passe automatiquement en HTTPS. La verification du certificat SSL est desactivee par defaut (normal en labo de test, les certificats sont souvent auto-signes).

**Verdicts :**
- **OK** : le serveur repond avec un code HTTP valide (200, 301, etc.)
- **CRITICAL** : le serveur ne repond pas, timeout, ou erreur de connexion
- **UNKNOWN** : erreur inattendue

**Exemple de resultat :**
> "HTTP 200 sur 192.168.10.5:8006 -- 45.2ms (Server: pve-api-daemon)"

---

## 3. Vocabulaire technique a connaitre

### Port
Imagine un immeuble (le serveur) avec plein de portes numerotees. Chaque service ecoute derriere une porte specifique. Le port 80 c'est la porte du web, le port 22 c'est la porte du SSH, etc. Quand on dit "verifier un port", ca veut dire : on frappe a cette porte et on regarde si quelqu'un repond.

### Timeout
C'est le temps qu'on accepte d'attendre avant de considerer que personne ne repond. Dans notre outil c'est generalement 2 a 10 secondes. Si au bout de ce delai le serveur n'a pas repondu, on considere que le service est en panne.

### DNS (Domain Name System)
C'est l'annuaire telephonique d'Internet (et du reseau local). Il transforme un nom comme `ntl.local` en adresse IP comme `192.168.10.10`. Sans DNS, il faudrait retenir toutes les adresses IP par coeur.

### LDAP (Lightweight Directory Access Protocol)
C'est le protocole qui permet d'interroger l'annuaire Active Directory. L'annuaire contient la liste de tous les utilisateurs, leurs groupes, leurs droits. Quand tu te connectes a ton PC Windows avec ton login, c'est LDAP qui va verifier que ton compte existe.

### Kerberos
C'est le systeme d'authentification utilise par Active Directory. Quand tu tapes ton mot de passe pour te connecter, c'est Kerberos qui verifie que c'est le bon et te donne un "ticket" (comme un badge temporaire) pour acceder aux ressources du reseau. Port 88.

### Active Directory (AD)
C'est le service Microsoft qui gere tous les comptes utilisateurs, les ordinateurs, les groupes et les droits dans une entreprise. C'est le cerveau du reseau Windows. Il s'appuie sur DNS, LDAP et Kerberos pour fonctionner.

### WinRM (Windows Remote Management)
Un protocole qui permet d'executer des commandes a distance sur un serveur Windows. Notre outil l'utilise pour verifier que les services Windows tournent bien (NTDS, DNS, Netlogon). C'est optionnel car il faut des identifiants.

### SMB (Server Message Block)
Le protocole de partage de fichiers de Windows. Port 445. Si ce port est ferme, les partages reseau ne fonctionnent plus.

### Banniere (banner)
Quand tu te connectes a certains services reseau, ils t'envoient un petit message de bienvenue automatique. Par exemple, MySQL envoie sa version. On appelle ca une "banniere". Notre outil lit cette banniere pour identifier le service sans avoir besoin de s'authentifier.

### TCP (Transmission Control Protocol)
Le protocole de base pour les connexions reseau fiables. Quand on "teste un port", on ouvre une connexion TCP vers ce port. Si la connexion s'etablit, le port est ouvert. Sinon, il est ferme ou filtre.

---

## 4. Les exit codes (codes de retour)

Le module utilise 4 niveaux de severite, inspires de Nagios (un outil de monitoring tres connu) :

| Code | Nom | Signification |
|------|------|------|
| 0 | OK | Tout fonctionne normalement |
| 1 | WARNING | Ca marche mais il y a un truc a surveiller |
| 2 | CRITICAL | Ca ne marche pas, intervention necessaire |
| 3 | UNKNOWN | Impossible de determiner l'etat (erreur dans le check lui-meme) |

---

## 5. Questions que le jury peut poser (et les reponses)

### "Qu'est-ce que fait concretement votre module Diagnostic ?"

> Il verifie que les services critiques de NordTransit Logistics fonctionnent. Il teste 4 types de services : l'Active Directory et le DNS (le controleur de domaine Windows), la base de donnees MySQL, les services sur les serveurs Linux, et les services web HTTP. Pour chaque check, il donne un verdict : OK, WARNING, CRITICAL ou UNKNOWN.

### "Pourquoi ne pas juste faire un ping ?"

> Un ping verifie seulement que la machine repond sur le reseau. Mais une machine peut repondre au ping alors que ses services sont plantes. Notre outil va plus loin : il verifie que chaque service specifique repond bien. Par exemple, on verifie que MySQL repond sur le port 3306, pas juste que le serveur est allume.

### "Comment vous verifiez MySQL sans mot de passe ?"

> MySQL envoie automatiquement un paquet de bienvenue quand on se connecte a son port, avant meme de demander un mot de passe. Ce paquet contient la version du serveur. On lit juste ce paquet. On ne se connecte pas a la base de donnees elle-meme, on verifie juste que le service MySQL tourne et repond.

### "C'est quoi la difference entre un port critique et un port important ?"

> Les ports critiques (53, 88, 389) sont ceux sans lesquels l'Active Directory ne peut pas fonctionner du tout : DNS, Kerberos et LDAP. Si un seul de ces ports est ferme, le verdict est CRITICAL. Les ports importants (445, 3268) sont utiles mais pas vitaux : si SMB est ferme, les partages reseau ne marchent plus mais les gens peuvent quand meme se connecter. Si un port important est ferme, le verdict est WARNING.

### "Pourquoi le check WinRM est optionnel ?"

> Parce qu'il necessite des identifiants (un login et un mot de passe d'administrateur Windows). On ne veut pas mettre des mots de passe en dur dans le code, donc c'est configure via des variables d'environnement. Si elles ne sont pas definies, on saute cette etape sans generer d'erreur. Les autres checks (DNS, ports, LDAP) fonctionnent sans authentification.

### "C'est quoi le contrat JSON / build_result ?"

> Toutes les fonctions de tous les modules renvoient un resultat dans le meme format standardise. Ca contient : le nom du module, la fonction appelee, le statut (OK/WARNING/CRITICAL/UNKNOWN), le code de retour (0 a 3), la cible verifiee, les details techniques, et un message lisible. Ca permet au menu principal d'afficher les resultats de maniere uniforme, quel que soit le module.

### "Comment vous gerez les erreurs ?"

> Chaque fonction est entouree d'un try/except. Si quelque chose plante de maniere inattendue (probleme reseau, librairie manquante, etc.), au lieu de crasher, le module renvoie un resultat UNKNOWN avec le message d'erreur. L'outil ne crashe jamais, c'est une regle du projet.

### "Pourquoi vous desactivez la verification SSL ?"

> Parce qu'on est dans un environnement de laboratoire. Les serveurs utilisent souvent des certificats auto-signes (pas emis par une autorite de certification reconnue). Si on gardait la verification SSL activee, le check echouerait systematiquement alors que le service web fonctionne tres bien. En production, on activerait la verification.

### "Quels sont les seuils de votre module ?"

> Pour le Diagnostic, les seuils sont binaires : un port est soit ouvert soit ferme, un service repond ou ne repond pas. Ce n'est pas comme le monitoring CPU/RAM ou il y a des seuils a 80%. Ici, c'est noir ou blanc : le service marche ou il ne marche pas.

### "Comment vous avez choisi les ports a scanner ?"

> Les ports critiques (53, 88, 389) et importants (445, 3268) viennent directement de la documentation Microsoft sur Active Directory -- ce sont les ports que AD utilise obligatoirement. Pour la decouverte Linux, on a choisi les ports des services les plus courants dans une PME : SSH (22), web (80/443), bases de donnees (3306/5432), et Proxmox (8006). Tout est defini dans un fichier de constantes, donc c'est facile a modifier.

### "Votre module peut-il tourner sur Windows et Linux ?"

> Oui, tout le code est compatible multi-plateforme. Les fonctions reseau utilisent des sockets Python standards qui marchent partout. La seule exception c'est le ping (qui utilise une commande differente selon l'OS), mais le module Diagnostic n'utilise pas le ping directement.
