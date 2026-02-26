# Guide Equipe — NTL-SysToolbox

> **C'est le seul document que tu dois lire pour coder ton module.**
> Tout ce dont tu as besoin est ici. Pas besoin d'aller chercher ailleurs.

---

## Comment l'outil fonctionne

L'outil est un menu dans le terminal. L'utilisateur choisit un module, puis une action.

```
Utilisateur                    Ton code                    Resultat
    |                              |                          |
    |   choisit "Diagnostic"       |                          |
    |   puis "Verifier MySQL"      |                          |
    |----------------------------->|                          |
    |                              |  ta fonction fait le     |
    |                              |  travail (connexion,     |
    |                              |  mesures, etc.)          |
    |                              |                          |
    |                              |  tu renvoies un dict     |
    |                              |  via build_result()      |
    |                              |------------------------->|
    |                              |                          | sauvegarde JSON
    |   voit le resultat           |                          | + affichage
    |<---------------------------------------------------------|
```

**En resume :**
1. `main.py` gere le menu (deja fait, tu n'y touches pas)
2. `main.py` appelle `ton_module.run(config, target, action="nom_fonction")`
3. Ta fonction fait son boulot puis renvoie un resultat avec `build_result()`
4. C'est tout.

---

## Se connecter a GitHub (une seule fois)

Le repo est prive. Tu dois d'abord te connecter a ton compte GitHub sinon tu auras une erreur "access denied".

### Option A — En ligne de commande (Git Bash / terminal)

1. Ouvre un terminal et tape :

```bash
gh auth login
```

2. Choisis **GitHub.com**, puis **HTTPS**, puis **Login with a web browser**
3. Ca ouvre ton navigateur — connecte-toi avec ton compte GitHub
4. C'est bon, tu es connecte

> **Tu n'as pas `gh` ?** Installe-le : https://cli.github.com/
> Sinon, Git te demandera ton login/mot de passe au moment du `git clone`. Dans ce cas le mot de passe est un **Personal Access Token** (pas ton mot de passe GitHub). Pour en creer un : GitHub > Settings > Developer settings > Personal access tokens > Generate new token (cocher `repo`).

### Option B — Avec VSCode

1. Ouvre VSCode
2. Clique sur l'icone de profil en bas a gauche (ou en haut a droite)
3. Clique **Sign in with GitHub**
4. Ca ouvre ton navigateur — connecte-toi avec ton compte GitHub
5. Autorise VSCode quand il demande
6. C'est bon, VSCode peut acceder aux repos prives

---

## Cloner le repo (une seule fois)

### En ligne de commande

```bash
git clone https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox.git
cd MSPR2-NTL-SysToolbox
```

### Avec VSCode

1. Ouvre VSCode
2. `Ctrl+Shift+P` → tape **Git: Clone**
3. Colle l'URL : `https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox.git`
4. Choisis un dossier ou sauvegarder le projet
5. Clique **Open** quand VSCode propose d'ouvrir le repo

### Installer les dependances

```bash
pip install -r requirements.txt
```

C'est fait. Tu ne refais plus jamais ces etapes.

---

## Le workflow Git — 5 commandes

Tu n'as besoin que de ces 5 commandes. Rien d'autre.

**Avant de coder (une seule fois au debut de chaque session) :**

```bash
git checkout feature/module-XXX      # remplace XXX par ton module
git pull origin master                # recupere les derniers changements
```

**Apres avoir code :**

```bash
git add src/modules/XXX.py            # remplace XXX par ton fichier
git commit -m "feat: add nom_fonction()"
git push origin feature/module-XXX
```

**Ensuite, previens Ianis sur WhatsApp.** Il s'occupe du merge. C'est tout.

Pas de Pull Request. Pas d'issue. Pas de review formelle. Tu codes, tu push, Ianis merge.

---

## Les 4 roles

| Qui | Branche | Fichier | Role |
|-----|---------|---------|------|
| **Ianis** (Lead) | `feature/cli-menu` | `main.py`, config, utils | Le menu + assemblage |
| **Blaise** | `feature/module-diagnostic` | `src/modules/diagnostic.py` | Verifier que les serveurs marchent |
| **Ojvind** | `feature/module-backup` | `src/modules/backup.py` | Sauvegarder la base de donnees |
| **Zaid** | `feature/module-audit` | `src/modules/audit.py` | Detecter les OS obsoletes |

**Regle d'or :** tu ne touches QUE ton fichier sur ta branche. Rien d'autre.

---

## Pour commencer — Copier le template

Avant de coder quoi que ce soit, copie le fichier template :

```bash
cp src/modules/_template.py src/modules/diagnostic.py   # Blaise
cp src/modules/_template.py src/modules/backup.py       # Ojvind
cp src/modules/_template.py src/modules/audit.py        # Zaid
```

Puis ouvre ton fichier et change la ligne :
```python
MODULE_NAME = "[nom]"
```
Par le nom de ton module (`"diagnostic"`, `"backup"` ou `"audit"`).

---

## Le pattern de base — Comment ecrire une fonction

Voici un exemple COMPLET d'une fonction qui marche. Lis-le, comprends-le, puis adapte-le.

```python
import socket
from src.interfaces import build_result, EXIT_OK, EXIT_UNKNOWN

def check_mysql(config: dict, target: str) -> dict:
    """Verifie que MySQL repond sur le serveur cible."""
    try:
        # 1. On essaie de se connecter au port 3306 (MySQL)
        sock = socket.socket()
        sock.settimeout(10)
        sock.connect((target, 3306))
        sock.close()

        # 2. Ca a marche -> on renvoie OK
        return build_result(
            module="diagnostic",
            function="check_mysql",
            status="OK",
            exit_code=EXIT_OK,
            target=target,
            details={"port_3306": True},
            message=f"MySQL repond sur {target}",
        )

    except Exception as e:
        # 3. Ca n'a pas marche -> on renvoie UNKNOWN (pas de crash !)
        return build_result(
            module="diagnostic",
            function="check_mysql",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=target,
            details={"error": str(e)},
            message=f"Impossible de joindre MySQL sur {target}: {e}",
        )
```

**Les 3 regles a retenir :**
1. **Toujours utiliser `build_result()`** pour renvoyer le resultat
2. **Toujours mettre un `try/except`** — ta fonction ne doit JAMAIS planter
3. **Les status possibles :** `"OK"`, `"WARNING"`, `"CRITICAL"`, `"UNKNOWN"`

---

## Section Blaise — Module Diagnostic

**Ton fichier :** `src/modules/diagnostic.py`
**Ta branche :** `feature/module-diagnostic`

### Ce que tu dois coder

| Fonction | Ce qu'elle fait en une phrase |
|----------|------------------------------|
| `check_ad_dns()` | Verifie que le serveur Active Directory (DC01) repond en testant le port 389 et la resolution DNS |
| `check_mysql()` | Verifie que MySQL tourne sur WMS-DB en se connectant et en executant une requete simple |
| `check_windows_server()` | Recupere les metriques du serveur Windows (CPU, RAM, disque) |
| `check_ubuntu()` | Recupere les metriques du serveur Linux via SSH (CPU, RAM, disque) |
| `run()` | Recoit l'action choisie par l'utilisateur et appelle la bonne fonction (deja dans le template) |

### Decisions a prendre ensemble avant de coder

On verra ca en session de travail. Les questions qu'on tranchera :

- Comment tester le port LDAP 389 ? (indice : `check_port()` existe deja dans `src/utils/network.py`)
- Comment se connecter en SSH pour executer des commandes sur Ubuntu ? (on utilisera `paramiko`)
- Quelles commandes Linux donnent le CPU, la RAM, le disque ? (`free -m`, `df -h`, `uptime`)
- Comment recuperer les metriques Windows a distance ?
- Quand est-ce qu'on met WARNING vs OK ? (regle : > 80% = WARNING)

### Par ou commencer

1. Copie le template (voir section au-dessus)
2. Commence par `check_ad_dns()` — c'est la plus simple
3. Utilise `check_port()` de `src/utils/network.py` (deja code !) pour tester le port 389
4. Utilise `resolve_dns()` de `src/utils/network.py` (deja code !) pour tester le DNS

---

## Section Ojvind — Module Backup

**Ton fichier :** `src/modules/backup.py`
**Ta branche :** `feature/module-backup`

### Ce que tu dois coder

| Fonction | Ce qu'elle fait en une phrase |
|----------|------------------------------|
| `backup_database()` | Se connecte en SSH au serveur, execute `mysqldump` pour exporter la base, et calcule le SHA256 du fichier |
| `export_table_csv()` | Se connecte a MySQL, fait un `SELECT *` sur une table, et ecrit le resultat dans un fichier CSV |
| `run()` | Recoit l'action et appelle la bonne fonction |

### Decisions a prendre ensemble avant de coder

- C'est quoi `mysqldump` ? (un programme qui exporte toute une base de donnees en fichier texte)
- Comment executer une commande sur un serveur distant ? (SSH avec `paramiko`)
- Comment calculer le SHA256 d'un fichier en Python ? (`hashlib`)
- Comment ecrire un fichier CSV en Python ? (module `csv` integre)
- Ou sauvegarder les fichiers ? (`output/backups/`)

### Par ou commencer

1. Copie le template
2. Commence par `export_table_csv()` — c'est la plus simple
3. Tu te connectes a MySQL, tu fais un SELECT, tu ecris dans un fichier CSV
4. Puis attaque `backup_database()` — plus complexe car il faut SSH + mysqldump

---

## Section Zaid — Module Audit

**Ton fichier :** `src/modules/audit.py`
**Ta branche :** `feature/module-audit`

### Ce que tu dois coder

| Fonction | Ce qu'elle fait en une phrase |
|----------|------------------------------|
| `scan_network()` | Utilise nmap pour scanner le reseau et trouver quelles machines sont connectees |
| `list_os_eol()` | Lit le fichier `data/eol_database.json` et affiche les dates de fin de support des OS |
| `audit_from_csv()` | Lit un fichier CSV d'inventaire et croise avec les dates EOL pour trouver les OS obsoletes |
| `generate_report()` | Genere un rapport colore qui trie les machines par urgence (expire > bientot > ok) |
| `run()` | Recoit l'action et appelle la bonne fonction |

### Decisions a prendre ensemble avant de coder

- Comment utiliser `python-nmap` pour scanner ? (on verra ensemble la syntaxe)
- Comment lire un fichier JSON en Python ? (`json.load()`)
- Comment lire un fichier CSV ? (`csv.DictReader`)
- Comment croiser deux sources de donnees ? (boucle + dictionnaire)
- Comment afficher un tableau colore ? (la lib `rich` — `Table()`)
- Qu'est-ce que "bientot expire" ? (regle : dans moins de 6 mois)

### Par ou commencer

1. Copie le template
2. Commence par `list_os_eol()` — c'est la plus simple (juste lire un fichier JSON)
3. Puis `audit_from_csv()` — lire un CSV et croiser avec le JSON
4. `scan_network()` et `generate_report()` sont plus complexes, on les fera ensemble

---

## Les outils deja codes (que tu peux reutiliser)

Ianis a deja code des utilitaires dans `src/utils/`. Utilise-les au lieu de recoder :

| Fonction | Fichier | Ce qu'elle fait |
|----------|---------|-----------------|
| `check_port(host, port)` | `src/utils/network.py` | Teste si un port est ouvert sur une machine |
| `ping_host(host)` | `src/utils/network.py` | Fait un ping |
| `resolve_dns(hostname)` | `src/utils/network.py` | Resout un nom de domaine en IP |
| `build_result(...)` | `src/interfaces.py` | Construit le dict de resultat standardise |
| `print_result(result)` | `src/utils/output.py` | Affiche un resultat joliment |
| `save_result_json(result, dir)` | `src/utils/output.py` | Sauvegarde un resultat en JSON |

Pour les utiliser dans ton code :
```python
from src.utils.network import check_port, ping_host
from src.interfaces import build_result, EXIT_OK, EXIT_UNKNOWN
```

---

## La config — Comment lire les parametres

La config est chargee depuis `config/config.yaml`. Elle arrive dans ta fonction via le parametre `config`.

```python
def check_mysql(config: dict, target: str) -> dict:
    # Lire le port MySQL depuis la config
    port = config.get("mysql", {}).get("port", 3306)
    user = config.get("mysql", {}).get("user", "root")
    password = config.get("mysql", {}).get("password", "")

    # Lire le timeout general
    timeout = config.get("general", {}).get("timeout", 10)
```

Les secrets (mots de passe) sont dans le fichier `.env` et sont automatiquement injectes dans la config. Tu n'as rien a faire pour ca.

---

## Si tu es bloque

1. **Regle des 30 minutes :** si tu bloques plus de 30 min, envoie un message sur WhatsApp
2. **L'erreur la plus courante :** oublier le `try/except` — ta fonction doit TOUJOURS renvoyer un `build_result()`, meme quand ca plante
3. **Pour tester ton module tout seul :** cree un petit fichier `test_rapide.py` a la racine :

```python
from src.config_loader import load_config
from src.modules.diagnostic import check_ad_dns  # adapte a ta fonction

config = load_config("config/config.yaml")
result = check_ad_dns(config, "192.168.10.10")
print(result)
```

4. **Si ton `import` ne marche pas :** lance Python depuis la racine du projet :
```bash
cd MSPR2-NTL-SysToolbox
python -m src.modules.diagnostic    # ou ton module
```

---

## Conventions de commit

| Prefixe | Quand | Exemple |
|---------|-------|---------|
| `feat:` | Nouvelle fonction | `feat: add check_ad_dns()` |
| `fix:` | Correction de bug | `fix: handle timeout in backup` |
| `test:` | Ajout de test | `test: add diagnostic tests` |
| `docs:` | Documentation | `docs: update README` |

---

## Planning simplifie

```
Etape 1 : Session de decisions par module (avec Ianis, en equipe)
Etape 2 : Chacun code sur sa branche
Etape 3 : Ianis merge tout
Etape 4 : On teste ensemble sur le lab
Etape 5 : Documentation + slides
Etape 6 : Soutenance
```

On en est a l'etape 1. On ne code pas encore. On discute d'abord.
