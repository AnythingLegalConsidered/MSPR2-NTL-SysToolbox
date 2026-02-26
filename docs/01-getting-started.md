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

#### Editeur de code

On recommande **VS Code** : `winget install Microsoft.VisualStudioCode` (ou [code.visualstudio.com](https://code.visualstudio.com/)).
Extensions utiles : Python (Microsoft), GitLens.

---

## 2. Se connecter a GitHub (une seule fois)

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

## 3. Recuperer le projet

### En ligne de commande

```bash
git clone https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox.git
cd MSPR2-NTL-SysToolbox
```

### Avec VSCode

1. `Ctrl+Shift+P` → tape **Git: Clone**
2. Colle l'URL : `https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox.git`
3. Choisis un dossier ou sauvegarder le projet
4. Clique **Open** quand VSCode propose d'ouvrir le repo

---

## 4. Installer l'environnement Python

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

## 5. Creer le fichier de configuration

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

## 6. Creer ta branche et commencer

### Qui fait quoi ?

| Developpeur | Module | Branche | Fichier |
|-------------|--------|---------|---------|
| **Blaise** | Diagnostic | `feature/module-diagnostic` | `src/modules/diagnostic.py` |
| **Ojvind** | Backup | `feature/module-backup` | `src/modules/backup.py` |
| **Zaid** | Audit | `feature/module-audit` | `src/modules/audit.py` |

### Creer ta branche

```bash
git checkout master
git pull
git checkout -b feature/module-<nom>
```

### Copier le template

```bash
cp src/modules/_template.py src/modules/<nom>.py
```

Puis change `MODULE_NAME = "[nom]"` par le nom de ton module.

**La suite du dev est dans [02-team-guide.md](02-team-guide.md).**

---

## 7. Commandes utiles

```bash
make run            # Lancer le CLI
make test           # Lancer les tests
make lint           # Verifier le code (ruff)
make typecheck      # Verifier les types (mypy)
make clean          # Nettoyer les fichiers generes
```

---

## FAQ — Quand ca ne marche pas

| Symptome | Cause | Solution |
|----------|-------|----------|
| `access denied` | Pas connecte a GitHub | Retourne a la section 2 |
| `pip not found` | Python pas dans le PATH | Reinstalle Python et **coche "Add to PATH"** |
| `make: command not found` | Make pas installe | `winget install GnuWin32.Make`, reouvre le terminal |
| `gh: command not found` | GitHub CLI pas installe | `winget install GitHub.cli` |
| `ModuleNotFoundError` | venv pas actif ou deps pas installees | Active le venv + `pip install -r requirements.txt` |
| `not a git repository` | Pas dans le bon dossier | `cd MSPR2-NTL-SysToolbox` |
| `everything up to date` | Oublie de `git add` + `git commit` | Fais le add/commit avant le push |
| `merge conflict` | Tu as modifie le fichier d'un autre | Appelle Ianis |
| `ConnectionRefusedError` | Le serveur lab est eteint | Verifie avec `ping 192.168.10.10` |
| `AccessDeniedError` (MySQL) | Mauvais credentials dans config.yaml | Verifie aupres du Lead |

### Comment lire une erreur Python (traceback)

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

Si tu es bloque plus de **30 minutes** :
1. Note ce que tu as essaye
2. Copie le message d'erreur
3. Envoie un message au Lead sur WhatsApp
