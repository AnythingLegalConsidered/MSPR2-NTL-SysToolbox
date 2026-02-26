# Guide de Demarrage — Developpeur

> Ce guide est pour toi si tu n'as jamais touche au projet. Suis-le **dans l'ordre**, etape par etape.
> Si tu es bloque plus de 30 minutes, envoie un message au Lead (Ianis) sur WhatsApp.

---

## 1. Prerequis a installer

Avant de toucher au code, tu dois avoir ces outils sur ton PC.

> **Astuce Windows** : utilise `winget` (gestionnaire de paquets integre a Windows 10/11) pour tout installer d'un coup depuis PowerShell ou cmd.

### Installation rapide (Windows, via winget)

```bash
winget install Python.Python.3.12
winget install Git.Git
winget install GitHub.cli
winget install GnuWin32.Make
winget install Microsoft.VisualStudioCode
```

> **Ferme et reouvre ton terminal** apres les installations pour que les commandes soient reconnues.

### Installation rapide (Linux)

```bash
sudo apt install python3 python3-venv python3-pip git gh make nmap
```

### Verification

Verifie que tout est installe :
```bash
python --version     # Python 3.10+ (Linux: python3)
git --version        # Git 2.x+
gh --version         # GitHub CLI 2.x+
make --version       # GNU Make 4.x+
pip --version        # pip 22+ (installe automatiquement avec Python)
```

### Details par outil

#### Python 3.10+

- **Windows** : `winget install Python.Python.3.12`. **COCHE la case "Add Python to PATH"** pendant l'installation. `pip` est inclus automatiquement.
- **Linux** : `sudo apt install python3 python3-venv python3-pip`

> Sur Linux, la commande est peut-etre `python3` au lieu de `python`.

#### Git

- **Windows** : `winget install Git.Git`. Ca installe aussi **Git Bash** (un terminal que tu utiliseras).
- **Linux** : `sudo apt install git`

#### GitHub CLI (gh)

Necessaire pour s'authentifier sur GitHub depuis le terminal (`gh auth login`).

- **Windows** : `winget install GitHub.cli`
- **Linux** : `sudo apt install gh` (ou voir [cli.github.com](https://cli.github.com/))

#### Make

Necessaire pour utiliser les commandes `make setup`, `make test`, etc. du projet.

- **Windows** : `winget install GnuWin32.Make`
- **Linux** : `sudo apt install make` (generalement deja installe)

#### nmap (uniquement si tu travailles sur le module Audit)

- **Windows** : Telecharge depuis [nmap.org](https://nmap.org/download.html) et installe.
- **Linux** : `sudo apt install nmap`

Verifie :
```bash
nmap --version
```

#### Editeur de code

On recommande **VS Code** : `winget install Microsoft.VisualStudioCode` (ou [code.visualstudio.com](https://code.visualstudio.com/)).
Extensions utiles : Python (Microsoft), GitLens.

---

## 2. Recuperer le projet

Ouvre un terminal (Git Bash sur Windows, terminal sur Linux) et tape :

```bash
git clone https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox.git
cd MSPR2-NTL-SysToolbox
```

> C'est quoi `git clone` ? Ca telecharge tout le code du projet depuis GitHub sur ton PC. Tu n'as besoin de le faire qu'une seule fois.

---

## 3. Installer l'environnement Python

Un "environnement virtuel" (venv) isole les bibliotheques du projet pour ne pas polluer ton systeme.

### Sur Windows (Git Bash)

```bash
make setup
```

Ensuite, active le venv :
```bash
source venv/Scripts/activate
```

> Tu sauras que le venv est actif quand tu vois `(venv)` au debut de ta ligne de commande.

### Sur Linux

```bash
make setup-linux
```

Ensuite, active le venv :
```bash
source venv/bin/activate
```

### Installer les outils de dev

```bash
make setup-dev
```

> **IMPORTANT :** A chaque fois que tu ouvres un nouveau terminal, tu dois reactiver le venv (`source venv/Scripts/activate` ou `source venv/bin/activate`). Sinon, Python ne trouvera pas les bibliotheques.

---

## 4. Creer le fichier de configuration

Le fichier de config contient les adresses IP et mots de passe pour se connecter aux serveurs du lab.

```bash
cp config/config.example.yaml config/config.yaml
```

Ouvre `config/config.yaml` dans ton editeur et remplace les `${NTL_...}` par les vraies valeurs.
Le Lead te donnera les mots de passe.

**Alternative** : cree un fichier `.env` a la racine du projet :
```
NTL_MYSQL_USER=sysadmin
NTL_MYSQL_PASSWORD=le_vrai_mot_de_passe
NTL_SSH_USER=sysadmin
NTL_SSH_PASSWORD=le_vrai_mot_de_passe
```

> **NE JAMAIS** commit ce fichier ! Il est deja dans le `.gitignore`.

---

## 5. Creer ta branche et ton fichier module

### Qui fait quoi ?

| Developpeur | Module | Branche | Fichier |
|-------------|--------|---------|---------|
| **Blaise** | Diagnostic | `feature/module-diagnostic` | `src/modules/diagnostic.py` |
| **Ojvind** | Backup | `feature/module-backup` | `src/modules/backup.py` |
| **Zaid** | Audit | `feature/module-audit` | `src/modules/audit.py` |

### Etape 1 — Creer ta branche

```bash
# Assure-toi d'etre sur master et a jour
git checkout master
git pull

# Cree ta branche (remplace <nom> par ton module)
git checkout -b feature/module-<nom>
```

Exemple pour Blaise :
```bash
git checkout -b feature/module-diagnostic
```

### Etape 2 — Creer ton fichier module

```bash
# Copie le template (remplace <nom> par diagnostic, backup ou audit)
cp src/modules/_template.py src/modules/<nom>.py
```

Exemple pour Blaise :
```bash
cp src/modules/_template.py src/modules/diagnostic.py
```

### Etape 3 — Modifier MODULE_NAME

Ouvre ton nouveau fichier dans l'editeur et change la ligne :
```python
MODULE_NAME = "[nom]"
```
en :
```python
MODULE_NAME = "diagnostic"   # ou "backup" ou "audit"
```

---

## 6. Le pattern de base — comment coder une fonction

Chaque fonction que tu codes doit suivre ce pattern. **Copie-le et adapte-le** :

```python
def ma_fonction(config: dict, target: str) -> dict[str, Any]:
    """Description de ce que fait la fonction."""
    logger.info("Running ma_fonction on %s", target)
    timeout = config.get("general", {}).get("timeout", 10)

    try:
        # --- Ta logique ici ---
        # Exemple : verifier qu'un port est ouvert
        result_data = {"mon_test": True}

        return build_result(
            module=MODULE_NAME,
            function="ma_fonction",
            status="OK",
            exit_code=EXIT_OK,
            target=target,
            details=result_data,
            message=f"Tout est OK sur {target}",
        )

    except ConnectionError as e:
        # Le serveur ne repond pas
        return build_result(
            module=MODULE_NAME,
            function="ma_fonction",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=target,
            details={"error": str(e)},
            message=f"Impossible de joindre {target}: {e}",
        )

    except Exception as e:
        # Erreur inattendue — on ne crash PAS, on renvoie CRITICAL
        logger.error("ma_fonction failed: %s", e)
        return build_result(
            module=MODULE_NAME,
            function="ma_fonction",
            status="CRITICAL",
            exit_code=EXIT_CRITICAL,
            target=target,
            details={"error": str(e)},
            message=f"Erreur sur {target}: {e}",
        )
```

**Les regles d'or :**
1. **Toujours** retourner `build_result()` — jamais un dict fait a la main
2. **Jamais** de crash non gere — tout est dans un `try/except`
3. **Jamais** de mot de passe en dur — tout vient de `config`
4. **Toujours** fermer les connexions (MySQL, SSH) dans un `finally`

---

## 7. Tester ta fonction en isolation

Tu n'as PAS besoin de lancer tout le menu pour tester ta fonction.
Cree un fichier temporaire `test_manual.py` a la racine du projet :

### Pour le module Diagnostic (Blaise)

```python
"""Test rapide — a supprimer avant le merge."""
from src.config_loader import load_config
from src.modules.diagnostic import check_ad_dns, check_mysql

config = load_config("config/config.yaml")

# Teste check_ad_dns sur DC01
result = check_ad_dns(config, "192.168.10.10")
print(result)

# Teste check_mysql sur WMS-DB
result = check_mysql(config, "192.168.10.21")
print(result)
```

### Pour le module Backup (Ojvind)

```python
"""Test rapide — a supprimer avant le merge."""
from src.config_loader import load_config
from src.modules.backup import backup_database, export_table_csv

config = load_config("config/config.yaml")

# Teste backup_database
result = backup_database(config, "wms")
print(result)

# Teste export CSV de la table shipments
result = export_table_csv(config, "wms", table_name="shipments")
print(result)
```

### Pour le module Audit (Zaid)

```python
"""Test rapide — a supprimer avant le merge."""
from src.config_loader import load_config
from src.modules.audit import scan_network, list_os_eol, audit_from_csv, generate_report

config = load_config("config/config.yaml")

# Teste scan_network
result = scan_network(config, "192.168.10.0/24")
print(result)

# Teste list_os_eol pour un OS specifique
result = list_os_eol(config, "Windows Server 2008 R2")
print(result)

# Teste audit_from_csv
result = audit_from_csv(config, "data/sample_inventory.csv")
print(result)

# Teste generate_report
result = generate_report(config, "data/sample_inventory.csv")
print(result)
```

Lance le test :
```bash
python test_manual.py
```

> **IMPORTANT** : supprime `test_manual.py` avant de prevenir Ianis ! Ne le commit pas.

---

## 8. Workflow Git — pas a pas

### Sauvegarder ton travail (a faire souvent !)

```bash
# 1. Voir ce qui a change
git status

# 2. Ajouter TON fichier (pas les autres !)
git add src/modules/diagnostic.py        # Remplace par ton fichier

# 3. Commit avec un message clair
git commit -m "feat: add check_ad_dns()"

# 4. Envoyer sur GitHub
git push -u origin feature/module-diagnostic    # Premier push
git push                                         # Push suivants
```

> **Qu'est-ce qu'un commit ?** C'est une "photo" de ton code a un instant donne. Si tu fais une erreur plus tard, tu peux revenir a cette photo. Fais un commit a chaque fonction terminee.

### Convention des messages de commit

| Prefix | Quand l'utiliser | Exemple |
|--------|-----------------|---------|
| `feat:` | Nouvelle fonctionnalite | `feat: add check_ad_dns()` |
| `fix:` | Correction de bug | `fix: handle MySQL timeout` |
| `docs:` | Documentation | `docs: update README` |
| `test:` | Tests | `test: add test for check_mysql` |

### Quand ton module est pret

Quand **toutes tes fonctions sont terminees** :

1. Push ta branche (`git push`)
2. Previens Ianis sur WhatsApp : "Ma branche est prete"
3. Ianis s'occupe du merge. Tu n'as rien d'autre a faire.

---

## 9. Quand ca ne marche pas — debug

### Erreur : `ModuleNotFoundError: No module named 'src'`

Tu as probablement lance le script depuis le mauvais dossier. Assure-toi d'etre a la racine du projet :
```bash
cd MSPR2-NTL-SysToolbox
python test_manual.py
```

### Erreur : `ModuleNotFoundError: No module named 'mysql'` (ou paramiko, nmap, etc.)

Le venv n'est pas actif. Active-le :
```bash
source venv/Scripts/activate   # Windows
source venv/bin/activate       # Linux
```

### Erreur : `ConnectionRefusedError` ou `Connection timed out`

Le serveur cible (DC01 ou WMS-DB) n'est pas allumee ou pas accessible. Verifie :
```bash
ping 192.168.10.10    # DC01
ping 192.168.10.21    # WMS-DB
```

Si le ping ne passe pas, le lab n'est peut-etre pas lance. Previens le Lead.

### Erreur : `mysql.connector.errors.AccessDeniedError`

Le mot de passe MySQL est faux dans ton `config/config.yaml`. Verifie les credentials aupres du Lead.

### Erreur : `paramiko.ssh_exception.AuthenticationException`

Meme chose mais pour SSH. Verifie les credentials SSH dans le config.

### Comment lire une erreur Python (traceback)

Quand Python plante, il affiche un message comme :
```
Traceback (most recent call last):
  File "test_manual.py", line 5, in <module>
    result = check_ad_dns(config, "192.168.10.10")
  File "src/modules/diagnostic.py", line 42, in check_ad_dns
    sock.connect((host, port))
ConnectionRefusedError: [Errno 111] Connection refused
```

**Lis de bas en haut** :
1. La derniere ligne = le type d'erreur (`ConnectionRefusedError`)
2. La ligne au-dessus = la ligne de code qui a plante (ligne 42)
3. Remonte pour voir d'ou ca vient

### Regle des 30 minutes

Si tu es bloque plus de **30 minutes** sur un probleme :
1. Note ce que tu as essaye
2. Copie le message d'erreur
3. Envoie un message au Lead sur WhatsApp

C'est normal de demander de l'aide. Personne ne sait tout.

---

## 10. Checklist avant de prevenir Ianis

Avant de dire que ta branche est prete, verifie :

- [ ] Toutes mes fonctions sont codees
- [ ] Mon module ne crash jamais (teste avec des mauvaises valeurs aussi)
- [ ] Toutes mes fonctions retournent `build_result()`
- [ ] La connexion MySQL/SSH est toujours fermee (meme en cas d'erreur)
- [ ] Aucun mot de passe n'est ecrit en dur dans le code
- [ ] `make lint` passe sans erreur
- [ ] `make test` passe sans erreur
- [ ] J'ai supprime `test_manual.py`
- [ ] Mes commits suivent la convention (`feat:`, `fix:`, etc.)

---

## Rappel : les fichiers importants

| Fichier | C'est quoi | Quand le lire |
|---------|-----------|---------------|
| `src/modules/_template.py` | Le modele a copier pour creer ton module | Au tout debut |
| `src/interfaces.py` | Le format standard `build_result()` et les exit codes | Quand tu codes tes retours |
| `src/utils/network.py` | Fonctions utilitaires : `check_port()`, `ping_host()`, `resolve_dns()` | Quand tu fais du diagnostic reseau |
| `src/utils/output.py` | Sauvegarde JSON et affichage | Pas besoin de le modifier |
| `config/config.example.yaml` | Le template de config | Pour creer ton config.yaml |
| `_specs/AIDE_MEMOIRE.md` | Aide-memoire (format retour, git, commandes) | A garder ouvert pendant le dev |

---

*En cas de doute, relis [GUIDE.md](../_specs/GUIDE.md) — section de ton module.*
