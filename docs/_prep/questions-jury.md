# Questions / Réponses Jury — NTL-SysToolbox

> **50+ questions que le jury peut poser, classées par thème et difficulté.**
> Préparez vos réponses à voix haute. Le jury dispose de 30 minutes de questions.
> Chaque réponse indique **qui doit répondre** en priorité.

---

## 1. Contexte et compréhension métier

### Q1. Pourquoi NordTransit a besoin d'un outil CLI plutôt qu'une solution du marché (Zabbix, Nagios, PRTG) ?

**Qui répond :** Ianis

> "NTL a une équipe IT de 4 personnes avec un budget limité. Déployer un Zabbix complet demande du temps de configuration, un serveur dédié, et de la maintenance. Notre outil est léger, sans dépendance serveur, déployable en 5 minutes. C'est un premier pas avant une solution plus lourde — et nos codes retour 0-3 sont déjà compatibles Nagios/Zabbix pour une intégration future."

---

### Q2. Que se passe-t-il si le WMS tombe pendant les heures ouvrables ?

**Qui répond :** Ianis

> "Le WMS tourne de 5h30 à 18h30. S'il tombe, les 4 sites sont bloqués — plus de scan de colis, plus de préparation de commandes. C'est pour ça que la supervision est critique : détecter un problème AVANT qu'il ne provoque un arrêt. Notre module Diagnostic permet justement de vérifier en continu que MySQL, l'AD et le DNS répondent."

---

### Q3. Comment avez-vous identifié les 3 problématiques (supervision, backup, obsolescence) ?

**Qui répond :** Ianis

> "On a analysé le cahier des charges et l'existant de NTL. La DSI surveille des métriques basiques mais pas les services métier. Les backups existent mais n'ont jamais été testées. Et il n'y a aucun inventaire des OS en fin de vie. Ce sont 3 angles morts concrets qui représentent des risques opérationnels et de sécurité."

---

### Q4. Qu'est-ce qu'un RPO et un RTO ? Quels seraient ceux de NTL ?

**Qui répond :** Ojvind (ou Ianis)

> "Le RPO — Recovery Point Objective — c'est la quantité de données qu'on accepte de perdre. Si on fait un backup par jour, le RPO est de 24h. Le RTO — Recovery Time Objective — c'est le temps maximum acceptable pour restaurer le service. Pour NTL, avec le WMS critique, on recommanderait un RPO de quelques heures et un RTO court. Aujourd'hui il n'y a pas de RPO/RTO défini, c'est un des problèmes qu'on a identifiés."

---

### Q5. Pourquoi la maintenance est limitée à la nuit chez NTL ?

**Qui répond :** Ianis

> "Le WMS fonctionne de 5h30 à 18h30 — c'est la plage d'activité des entrepôts. Toute coupure en journée bloque l'ensemble de la logistique. L'équipe IT n'a donc qu'une fenêtre nocturne pour intervenir, ce qui renforce le besoin d'outils automatisés et fiables."

---

## 2. Architecture et choix techniques

### Q6. Pourquoi Python et pas Bash ou PowerShell ?

**Qui répond :** Ianis

> "Trois raisons. D'abord la portabilité : Python fonctionne sur Windows et Linux, alors que Bash est Linux-only et PowerShell est historiquement Windows. Ensuite l'écosystème de librairies : paramiko pour SSH, dnspython, python-nmap, ldap3 — tout est disponible en Python. Enfin la maintenabilité : un script Bash de 2000 lignes devient vite inmaintenable, Python est plus structuré."

---

### Q7. Pourquoi les codes retour 0, 1, 2, 3 ?

**Qui répond :** Ianis

> "C'est la convention Nagios. 0 = OK, 1 = WARNING, 2 = CRITICAL, 3 = UNKNOWN. C'est un standard de l'industrie utilisé par Zabbix, Nagios, Icinga, Centreon. En utilisant cette convention, notre outil est directement intégrable dans n'importe quelle solution de supervision sans adaptation."

---

### Q8. Pourquoi JSON pour les sorties et pas du texte brut ?

**Qui répond :** Ianis

> "Le JSON est structuré, parseable par n'importe quel outil — un script, une API, un dashboard. Du texte brut nécessite du parsing regex, c'est fragile. Le JSON est aussi horodatable et archivable proprement. Et avec `jq` en ligne de commande, c'est aussi lisible que du texte."

---

### Q9. Pourquoi ne pas avoir fait une interface web ?

**Qui répond :** Ianis

> "La DSI de NTL a 4 personnes qui travaillent en terminal. Un CLI est plus rapide à utiliser, plus scriptable — on peut l'intégrer dans un cron ou un Task Scheduler — et plus léger. Une interface web aurait nécessité un serveur, un framework, de la sécurité HTTP. C'est une perspective pour la V2, mais pour la V1 le CLI répond au besoin."

---

### Q10. Expliquez le rôle de `build_result()`. Pourquoi une fonction centralisée ?

**Qui répond :** Ianis (ou n'importe qui)

> "`build_result()` est défini dans `interfaces.py`. C'est la seule façon de construire un résultat. Elle prend 7 paramètres — module, function, status, exit_code, target, details, message — et retourne toujours un dict avec la même structure, plus un timestamp UTC automatique. Elle valide aussi que le status et l'exit_code sont valides. Ça garantit que TOUS les modules produisent exactement le même format, sans exception."

---

### Q11. Pourquoi `interfaces.py` plutôt qu'une classe abstraite ?

**Qui répond :** Ianis

> "On a choisi la simplicité. Une classe abstraite avec héritage aurait ajouté de la complexité — décorateurs, métaclasses, méthodes abstraites. Ici, une simple fonction `build_result()` suffit. C'est un contrat par convention, documenté et validé à l'exécution. Pour un projet de 19h avec 4 devs, c'est le bon niveau d'abstraction."

---

### Q12. Comment gérez-vous la configuration ? Pourquoi YAML et pas JSON ou TOML ?

**Qui répond :** Ianis

> "YAML est lisible par un humain — c'est important pour une équipe IT qui va maintenir le fichier. JSON n'autorise pas les commentaires, ce qui est gênant pour de la config. TOML est moins répandu dans l'écosystème Python ops. Le YAML est aussi le standard dans l'univers DevOps — Ansible, Docker Compose, Kubernetes."

---

### Q13. Comment gérez-vous les secrets dans la configuration ?

**Qui répond :** Ianis

> "Les secrets ne sont jamais en dur dans le code ni dans le YAML. Le fichier `config.yaml` utilise des placeholders `${MYSQL_PASSWORD}`. Le `config_loader.py` résout ces variables depuis l'environnement, chargé via un fichier `.env` avec python-dotenv. Le `.env` est dans le `.gitignore` — jamais commit. Et le mot de passe MySQL transite par la variable `MYSQL_PWD`, pas en argument de commande — sinon il serait visible dans `ps aux`."

---

### Q14. Que se passe-t-il si le fichier de config n'existe pas ?

**Qui répond :** Ianis

> "Le `config_loader` lève une `ModuleConfigError` avec un message explicite : 'Config file not found, copy config.example.yaml'. Pas de valeurs par défaut magiques — on préfère un échec explicite à un comportement imprévisible."

---

### Q15. Pourquoi avoir choisi `rich` pour le CLI ?

**Qui répond :** Ianis

> "`rich` permet des tableaux colorés, des barres de progression, et un rendu professionnel dans le terminal — sans complexité. Ça donne un outil qui fait pro devant le jury et devant la DSI. C'est une lib pure Python, zéro dépendance système."

---

### Q16. Votre architecture est-elle extensible ? Comment ajouter un 4e module ?

**Qui répond :** Ianis

> "Oui. Les modules sont indépendants. Pour ajouter un module, il suffit de créer un fichier dans `src/modules/`, implémenter une fonction `run(config, target, **kwargs)` qui retourne via `build_result()`, et l'ajouter au menu dans `main.py`. On a même un template dans `_template.py`. Le contrat JSON ne change pas."

---

### Q17. Pourquoi ne pas avoir utilisé un framework CLI comme Click ou Typer ?

**Qui répond :** Ianis

> "Notre menu est interactif — l'utilisateur navigue avec des choix numérotés. Click et Typer sont conçus pour des CLI avec des arguments/options (`--host`, `--port`). Notre approche est plus adaptée à un opérateur IT qui lance l'outil et se laisse guider. Et ça fait une dépendance en moins."

---

## 3. Module Diagnostic (Blaise)

### Q18. Pourquoi tester les ports plutôt qu'un simple ping ?

**Qui répond :** Blaise

> "Un ping vérifie que la machine est allumée et joignable, pas que le service répond. Un serveur peut répondre au ping mais avoir MySQL planté. Tester le port 3306 confirme que MySQL écoute. Tester le port 389 confirme que LDAP répond. C'est la différence entre 'la machine est là' et 'le service fonctionne'."

---

### Q19. Que se passe-t-il si l'AD (DC01) ne répond pas ?

**Qui répond :** Blaise

> "Si le serveur est injoignable — timeout — le résultat est UNKNOWN (code 3). Si le serveur répond mais que LDAP ne répond pas sur le port 389, c'est CRITICAL (code 2). Si LDAP répond mais que le DNS est en panne, c'est WARNING (code 1). On a un arbre de décision clair pour chaque scénario."

---

### Q20. Quelles librairies utilisez-vous pour le diagnostic ?

**Qui répond :** Blaise

> "`dnspython` pour les requêtes DNS, `ldap3` pour vérifier LDAP — c'est une lib pure Python cross-platform. `socket` pour les tests de ports. `paramiko` pour les connexions SSH vers les serveurs Linux. Et `psutil` pour les métriques système locales."

---

### Q21. Pourquoi `ldap3` et pas `python-ldap` ?

**Qui répond :** Blaise (ou Ianis)

> "`ldap3` est du pur Python — pas de compilation C, pas de dépendance à OpenLDAP. Ça s'installe avec un simple `pip install` sur Windows comme sur Linux. `python-ldap` nécessite des headers C et pose des problèmes d'installation sur Windows."

---

### Q22. Comment vérifiez-vous que le DNS fonctionne vraiment, au-delà du port ?

**Qui répond :** Blaise

> "On ne se contente pas de vérifier que le port 53 est ouvert. On fait une vraie résolution DNS — on demande au serveur de résoudre le domaine `ntl.local`. Si le port répond mais que la résolution échoue, c'est un indicateur de problème — le service tourne mais ne fonctionne pas correctement."

---

### Q23. `check_mysql()` s'authentifie-t-il sur la base ?

**Qui répond :** Blaise

> "Le check teste la connexion au port 3306 et récupère la version du serveur MySQL. On peut aussi exécuter un `SHOW DATABASES` et un `SHOW STATUS` pour vérifier l'uptime et le nombre de threads actifs. L'authentification se fait avec les credentials du fichier de config."

---

### Q24. Comment gérez-vous les timeouts dans le diagnostic ?

**Qui répond :** Blaise

> "Le timeout par défaut est de 10 secondes, configurable dans le YAML. Chaque connexion socket ou SSH a ce timeout. Si la cible ne répond pas dans ce délai, on retourne UNKNOWN (code 3) avec un message explicite 'timeout après Xs'. Pas de blocage infini."

---

## 4. Module Backup (Ojvind)

### Q25. Pourquoi `mysqldump` et pas un export logique en Python ?

**Qui répond :** Ojvind

> "`mysqldump` est l'outil standard de MySQL pour les sauvegardes. Il gère les locks, la cohérence transactionnelle, et produit un fichier SQL directement restaurable avec `mysql < dump.sql`. Refaire ça en Python serait réinventer la roue en moins fiable."

---

### Q26. Expliquez le mécanisme de fallback SSH.

**Qui répond :** Ojvind

> "Si `mysqldump` n'est pas installé en local — ce qui est courant si on lance l'outil depuis un poste Windows —, le module détecte son absence et bascule automatiquement sur une connexion SSH vers le serveur de base de données. Il exécute `mysqldump` à distance et rapatrie le dump. C'est transparent pour l'utilisateur."

---

### Q27. Comment sécurisez-vous le mot de passe MySQL ?

**Qui répond :** Ojvind

> "Le mot de passe ne passe jamais en argument de commande — sinon il serait visible dans `ps aux` ou dans l'historique shell. On le passe via la variable d'environnement `MYSQL_PWD` que `mysqldump` lit nativement. Et le mot de passe vient du fichier `.env`, jamais du code."

---

### Q28. Comment vérifiez-vous l'intégrité du backup ?

**Qui répond :** Ojvind

> "Après chaque dump, on calcule le hash SHA256 du fichier et on vérifie que la taille est supérieure à 0. Le hash est inclus dans le résultat JSON — la DSI peut le comparer ultérieurement pour vérifier que le fichier n'a pas été altéré."

---

### Q29. Un backup qui échoue en cours de route — que se passe-t-il ?

**Qui répond :** Ojvind

> "Si `mysqldump` échoue, on retourne CRITICAL (code 2). On ne laisse pas de fichier partiel sur le disque — un dump incomplet est pire qu'inutile, il pourrait donner une fausse impression de sécurité. Le fichier partiel est supprimé."

---

### Q30. Pourquoi pas de compression (gzip) du dump ?

**Qui répond :** Ojvind

> "On a priorisé la simplicité et la lisibilité pour une V1. Un fichier .sql brut peut être ouvert et inspecté immédiatement. La compression est une amélioration prévue — l'architecture le permet facilement en ajoutant un pipe gzip après mysqldump."

---

### Q31. Pourquoi pas de backup incrémental ?

**Qui répond :** Ojvind

> "Un backup incrémental avec les binlogs MySQL est plus complexe à mettre en place et à restaurer. Pour une V1, un dump complet est plus simple et plus fiable. La base WMS de NTL n'est pas volumineuse au point de nécessiter de l'incrémental. C'est une perspective pour la V2."

---

### Q32. Comment l'export CSV protège-t-il contre l'injection SQL ?

**Qui répond :** Ojvind

> "Le nom de la table est validé par une regex : `^[a-zA-Z_]\w{0,63}$`. Ça n'accepte que des lettres, chiffres et underscores — pas d'espaces, pas de guillemets, pas de points-virgules. Si le nom ne matche pas, l'opération est refusée. Et les chemins de sortie sont protégés contre le path traversal — pas de `..` autorisé."

---

## 5. Module Audit (Zaid)

### Q33. La base EOL, elle vient d'où ? Comment la maintenez-vous ?

**Qui répond :** Zaid

> "Le fichier `eol_database.json` contient les dates de fin de support officielles de chaque OS — données Microsoft et Ubuntu. C'est un fichier JSON versionné avec le code. Le compromis : pas de dépendance réseau, mais maintenance manuelle quand un nouvel OS sort ou qu'une date change. C'est cohérent avec un outil d'audit qui doit fonctionner même en réseau coupé."

---

### Q34. Pourquoi pas l'API endoflife.date ?

**Qui répond :** Zaid

> "On veut que l'outil fonctionne même en cas de panne réseau — c'est un outil d'audit de crise. Si le réseau est coupé et qu'on a besoin d'auditer les machines, on ne peut pas dépendre d'une API externe. Le fichier local est un compromis assumé."

---

### Q35. Le scan nmap nécessite-t-il les droits root/admin ?

**Qui répond :** Zaid

> "La détection d'OS (`-O`) nécessite les droits root. Le module détecte automatiquement les privilèges. Sans root, il fait un scan dégradé — scan TCP sans détection d'OS — et ajoute un WARNING dans le résultat. L'outil ne plante pas, il dégrade proprement."

---

### Q36. Comment le rapport est-il hiérarchisé ?

**Qui répond :** Zaid

> "Le rapport est trié par urgence : d'abord les OS expirés — CRITICAL —, puis ceux qui expirent dans moins de 6 mois — WARNING —, et enfin les OK. La DSI voit immédiatement où sont les risques. Le rendu `rich` colore les lignes en rouge, orange et vert."

---

### Q37. Que se passe-t-il si un OS du parc n'est pas dans votre base EOL ?

**Qui répond :** Zaid

> "L'OS est marqué UNKNOWN — code 3. Le rapport le signale clairement. La DSI sait qu'il y a une machine avec un OS non référencé et peut mettre à jour la base. C'est mieux que de l'ignorer silencieusement."

---

### Q38. Comment fonctionne le croisement CSV/EOL dans `audit_from_csv()` ?

**Qui répond :** Zaid

> "Le CSV d'inventaire contient les colonnes hostname, os_name, os_version, role. Pour chaque ligne, on cherche l'OS dans la base EOL. Si on trouve une correspondance, on compare la date EOL avec la date du jour. Si la date est passée : EXPIRÉ. Si elle est dans moins de 6 mois : BIENTÔT. Sinon : OK. Le résultat est un rapport complet avec toutes les machines."

---

### Q39. Le scan nmap, ça prend combien de temps sur un réseau /24 ?

**Qui répond :** Zaid

> "Un scan TCP basique sur un /24 prend 1 à 5 minutes selon le nombre de machines actives. Avec la détection d'OS, ça peut monter à 10-15 minutes. C'est pour ça qu'on le fait en mode non-bloquant avec un feedback de progression. En production, on le planifierait en cron la nuit."

---

## 6. CI/CD et qualité

### Q40. Décrivez votre pipeline CI.

**Qui répond :** Ianis

> "À chaque push ou PR sur master ou une branche `feature/*`, GitHub Actions lance deux jobs en parallèle. Le premier vérifie la qualité : `ruff` pour le lint et `mypy` pour la vérification de types. Le second lance `pytest` avec coverage sur 3 versions de Python — 3.10, 3.11 et 3.12. En moins de 2 minutes, on sait si le code est mergeable."

---

### Q41. Pourquoi tester sur 3 versions de Python ?

**Qui répond :** Ianis

> "La DSI de NTL peut avoir différentes versions de Python selon les machines. En testant sur 3.10, 3.11 et 3.12, on garantit la compatibilité. Si un dev utilise une syntaxe spécifique à 3.12, la CI le détecte immédiatement."

---

### Q42. 54% de couverture de tests, c'est pas faible ?

**Qui répond :** Ianis

> "On a concentré les tests sur les chemins critiques — le config_loader, le build_result, la validation des entrées. L'outil interagit avec du réseau, des VMs, des bases de données, SSH. Tester ça à 100% serait du mock — des tests qui vérifient que les mocks fonctionnent, pas que le code fonctionne. On a préféré des tests qui testent vraiment quelque chose, plus une validation manuelle sur le lab."

---

### Q43. Qu'est-ce que `ruff` ? Pourquoi pas `flake8` ou `pylint` ?

**Qui répond :** Ianis

> "`ruff` est un linter Python écrit en Rust — il est 10 à 100 fois plus rapide que flake8 ou pylint. Il supporte les mêmes règles, et il est le nouveau standard dans l'écosystème Python. Pour notre CI, ça veut dire un feedback en secondes plutôt qu'en minutes."

---

### Q44. Qu'est-ce que `mypy` apporte à votre projet ?

**Qui répond :** Ianis

> "`mypy` fait de la vérification de types statique. On annote nos fonctions — `def build_result(...) -> dict[str, Any]` — et mypy vérifie que les types sont cohérents dans tout le code. Ça détecte des bugs avant l'exécution : un argument `int` passé là où on attend un `str`, par exemple."

---

### Q45. Faites-vous du déploiement continu ?

**Qui répond :** Ianis

> "Non, pas de CD pour l'instant. Le déploiement est manuel — la DSI clone le repo et lance l'outil. C'est adapté au contexte : 4 personnes IT, un outil CLI, pas une webapp. Le CD serait pertinent si on passe à une version serveur ou à un dashboard web."

---

## 7. Organisation d'équipe et méthode

### Q46. Comment vous êtes-vous répartis le travail ?

**Qui répond :** Ianis

> "On a défini le contrat JSON commun dès le départ dans `interfaces.py`. Ensuite, chacun a travaillé sur sa branche : Ianis sur le framework et le CLI, Blaise sur le module Diagnostic, Ojvind sur le Backup, Zaid sur l'Audit. Les modules étant indépendants, on pouvait travailler en parallèle sans se bloquer."

---

### Q47. Comment avez-vous communiqué en équipe ?

**Qui répond :** Ianis

> "WhatsApp pour la communication quotidienne. Un format standup async : fait / en cours / bloqué. GitHub Issues pour le suivi des tâches. Et la règle : si bloqué plus de 30 minutes, on alerte immédiatement sur le canal."

---

### Q48. Quelle a été la plus grosse difficulté ?

**Qui répond :** Chacun pour son module

> - **Ianis** : "La coordination à 4 en 19 heures. Le contrat JSON défini en amont a été la clé — sans ça, l'intégration aurait été un cauchemar."
> - **Blaise** : "L'AD multi-protocole — gérer LDAP, DNS et Kerberos avec des arbres de décision différents."
> - **Ojvind** : "La sécurité des credentials — s'assurer que le mot de passe MySQL ne fuit jamais dans les logs ou les arguments de commande."
> - **Zaid** : "La fiabilité de nmap selon les privilèges — le comportement change complètement avec ou sans root."

---

### Q49. La répartition des commits est déséquilibrée (Ianis 40, les autres 3-4). Pourquoi ?

**Qui répond :** Ianis

> "Le Lead a codé le framework — main.py, config_loader, interfaces, utils, la CI, la structure du repo, l'intégration finale et la documentation. C'est 60% du code mais c'est le socle sur lequel les modules s'appuient. Le travail de chaque dev est concentré dans son fichier module — c'est normal qu'il y ait moins de commits mais ce sont des commits denses."

---

### Q50. Pourquoi squash merge et pas merge classique ?

**Qui répond :** Ianis

> "Le squash merge condense tous les commits d'une branche en un seul commit propre sur master. L'historique reste lisible : un commit = une feature. Avec un merge classique, on aurait des dizaines de 'wip', 'fix typo', 'test' dans l'historique."

---

## 8. Sécurité

### Q51. Quelles mesures de sécurité avez-vous prises ?

**Qui répond :** Ianis + Ojvind

> "Cinq mesures principales. Les secrets sont dans un `.env` jamais commit, jamais en dur. Le mot de passe MySQL passe par variable d'environnement, pas en argument CLI. Les noms de tables sont validés par regex contre l'injection SQL. Les chemins de sortie sont protégés contre le path traversal. Et chaque fonction catch ses exceptions — pas de stack trace avec des infos sensibles."

---

### Q52. Un attaquant a accès au fichier `.env` — quels sont les risques ?

**Qui répond :** Ianis

> "Il aurait les credentials MySQL et SSH. C'est pour ça que le `.env` doit avoir des permissions restrictives (600 sur Linux). En production, on recommanderait un gestionnaire de secrets — HashiCorp Vault, AWS Secrets Manager. Mais pour un outil CLI local, le `.env` est un compromis raisonnable."

---

### Q53. Les sorties JSON peuvent-elles contenir des données sensibles ?

**Qui répond :** Ianis

> "On fait attention à ne pas loguer de credentials dans les détails. Les mots de passe ne sont jamais inclus dans les résultats JSON. Si un dump contient des données métier sensibles, il est stocké dans `output/` qui est gitignore et dont l'accès dépend des permissions du système de fichiers."

---

### Q54. nmap est souvent considéré comme un outil offensif. Comment justifiez-vous son utilisation ?

**Qui répond :** Zaid

> "nmap est un outil de découverte réseau, pas un outil d'attaque. C'est l'équivalent d'un inventaire réseau. La DSI l'utilise pour savoir quelles machines sont actives et quels services tournent — c'est de l'hygiène informatique basique. Et on scan uniquement le réseau interne de NTL, pas des cibles externes."

---

## 9. Lab et environnement de test

### Q55. Pourquoi Proxmox et pas VirtualBox ou VMware ?

**Qui répond :** Ianis

> "Proxmox VE est un hyperviseur open source de type 1 — il tourne directement sur le hardware, pas au-dessus d'un OS. C'est plus performant et plus représentatif d'un environnement professionnel. Et c'est la technologie utilisée dans beaucoup de PME — cohérent avec le contexte NTL."

---

### Q56. Pourquoi avoir inclus des VMs legacy (Server 2012 R2, Ubuntu 18.04) ?

**Qui répond :** Ianis

> "Pour tester la détection des OS en fin de vie. Si on ne met que des OS récents dans le lab, le module Audit n'a rien à détecter. Les VMs legacy permettent de valider que le rapport identifie correctement les machines à risque. C'est une démarche délibérée de test des cas limites."

---

### Q57. Le lab est-il reproductible ?

**Qui répond :** Ianis

> "Oui. On a des scripts post-install dans `infra/post-install/` qui configurent les VMs automatiquement. Un administrateur peut remonter le lab en suivant la documentation dans `docs/10-lab-infra.md`. C'est important pour la pérennité — si quelqu'un reprend le projet, il peut reconstruire l'environnement de test."

---

## 10. Perspectives et évolution

### Q58. Comment intégrer l'outil avec Zabbix concrètement ?

**Qui répond :** Ianis

> "Zabbix peut exécuter des scripts externes et interpréter les codes retour 0-3 — c'est son mode 'User Parameter'. On configure Zabbix pour lancer `python src/main.py --check ad_dns` (en ajoutant un mode non-interactif). Le code retour déclenche les alertes Zabbix. Le JSON de sortie peut être parsé pour alimenter des graphiques. Zéro modification côté outil."

---

### Q59. Comment planifier les backups automatiquement ?

**Qui répond :** Ojvind

> "Sur Linux, un crontab qui lance la commande de backup à l'heure voulue — par exemple à 2h du matin. Sur Windows, le Task Scheduler fait la même chose. Le résultat JSON est écrit dans `output/logs/`, et le dump dans `output/backups/`. On pourrait ajouter une notification par mail si le code retour est 2 (CRITICAL)."

---

### Q60. Si vous aviez plus de temps, que changeriez-vous ?

**Qui répond :** Tous

> - "Un mode non-interactif avec des arguments CLI (`--module diagnostic --check ad_dns --target 192.168.10.10`) pour l'automation."
> - "La base EOL dynamique via l'API endoflife.date, avec cache local en fallback."
> - "Un dashboard web simple avec Flask ou FastAPI pour visualiser les résultats."
> - "Du backup incrémental avec les binlogs MySQL."
> - "L'extension multi-sites via VPN pour couvrir les 3 entrepôts."
> - "Des tests d'intégration sur le lab en CI (environnement de test automatisé)."

---

## 11. Questions pièges / déstabilisantes

### Q61. Votre outil ne fait-il pas doublon avec des solutions qui existent déjà ?

**Qui répond :** Ianis

> "Les solutions du marché existent mais elles ont un coût de déploiement et de maintenance que NTL ne peut pas assumer avec 4 personnes IT. Notre outil est un premier pas : simple, déployable en 5 minutes, sans infrastructure supplémentaire. Et il est conçu pour s'intégrer avec ces solutions quand NTL sera prêt — les codes retour sont déjà compatibles."

---

### Q62. 19 heures pour 4 personnes, c'est peu. Qu'avez-vous sacrifié ?

**Qui répond :** Ianis

> "On n'a rien sacrifié — on a priorisé. Le mode non-interactif, le dashboard web, le backup incrémental sont des perspectives, pas des manques. En 19 heures, on a livré 3 modules fonctionnels, un CLI interactif, une CI complète, un lab de test et 10 documents de documentation. Chaque choix a été fait en connaissance de cause."

---

### Q63. Que faites-vous si un collègue ne livre pas son module à temps ?

**Qui répond :** Ianis

> "On a prévu ce cas. Le menu affiche quand même le module, mais avec un stub 'Non implémenté'. La structure reste complète, la démo montre les modules qui fonctionnent, et on explique honnêtement la situation. C'est mieux que de retirer le module du menu — ça montre qu'on a anticipé le risque."

---

### Q64. Votre outil pourrait-il être utilisé à des fins malveillantes ?

**Qui répond :** Ianis

> "Comme tout outil d'administration système. Le scan nmap détecte des machines, le module backup accède à la base. Mais l'outil nécessite les credentials — sans accès légitime, il ne fonctionne pas. Et il est conçu pour être utilisé par la DSI de NTL sur son propre réseau, pas comme un outil offensif."

---

### Q65. Pourquoi ne pas avoir utilisé Docker pour le déploiement ?

**Qui répond :** Ianis

> "Docker ajouterait une couche de complexité pour un outil CLI local. La DSI de NTL n'utilise pas nécessairement Docker. Un `pip install -r requirements.txt` et c'est prêt. Par contre, conteneuriser l'outil est une perspective pertinente pour un déploiement multi-sites."

---

### Q66. Vous dites cross-platform. Avez-vous réellement testé sur les deux OS ?

**Qui répond :** Ianis

> "Oui. Le développement a été fait sur Windows, la CI tourne sur Ubuntu via GitHub Actions. Les librairies utilisées sont toutes cross-platform — paramiko, dnspython, ldap3, psutil. Les chemins fichiers utilisent `pathlib` pour gérer les différences de séparateurs."

---

### Q67. Et si la DSI de NTL n'a pas Python sur ses machines ?

**Qui répond :** Ianis

> "Python est pré-installé sur la plupart des distributions Linux. Sur Windows, l'installation prend 2 minutes. On pourrait aussi packager l'outil en exécutable avec PyInstaller — c'est une perspective V2. Mais pour une équipe IT de 4 personnes, installer Python n'est pas un obstacle."

---

## 12. Questions sur le code spécifique

### Q68. Montrez-moi le code de `build_result()`. Que se passe-t-il si je passe un status invalide ?

**Qui répond :** Ianis

> "`build_result()` valide le status contre un set `{'OK', 'WARNING', 'CRITICAL', 'UNKNOWN'}` et l'exit_code contre `{0, 1, 2, 3}`. Si on passe un status invalide, une `ValueError` est levée immédiatement. Ça empêche un développeur de retourner un résultat non standard par erreur."

---

### Q69. Le `config_loader` gère-t-il les références circulaires ?

**Qui répond :** Ianis

> "Oui. La résolution des variables d'environnement a une profondeur maximale de 20 niveaux. Au-delà, une `ModuleConfigError` est levée avec un message explicite. Ça protège contre les boucles infinies dans la config."

---

### Q70. Que fait le mode `strict` du config_loader ?

**Qui répond :** Ianis

> "En mode strict, si une variable d'environnement n'est pas définie — par exemple `${MYSQL_PASSWORD}` sans `.env` — le loader lève une erreur au lieu de garder le placeholder. C'est utile en production : on veut savoir immédiatement si un secret manque, pas découvrir le problème à l'exécution du module."

---

---

## Conseils pour les 30 minutes de questions

1. **Écoutez la question jusqu'au bout** avant de répondre.
2. **La personne concernée répond en premier** — les autres complètent si besoin.
3. **Si vous ne savez pas** : "C'est un bon point, dans notre V1 on n'a pas couvert ça, mais l'architecture permet de l'ajouter."
4. **Ne pas se contredire entre membres** — si un doute, laissez le Lead répondre.
5. **Reliez chaque réponse au métier NTL** — pas à l'exercice scolaire.
6. **Soyez concis** — 30 secondes par réponse, pas 3 minutes.
7. **Ne jamais dire "on n'a pas eu le temps"** — dire "on a priorisé X parce que Y".
