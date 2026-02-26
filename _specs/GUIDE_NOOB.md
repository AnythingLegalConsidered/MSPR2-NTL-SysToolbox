# Guide pour les Incompetents — NTL-SysToolbox

> Tu lis ce guide parce que tu n'arrives meme pas a cloner un repo. C'est pas grave. Enfin si, un peu.

---

## Etape 0 — Allumer ton PC

On sait jamais. Verifie.

---

## Etape 1 — Installer les trucs de base

Tu as besoin de 3 choses. Oui, seulement 3. Essaie de suivre.

| Truc | Lien | Pourquoi |
|------|------|----------|
| **Python** | https://www.python.org/downloads/ | C'est le langage. Tu sais, le truc avec le serpent. |
| **Git** | https://git-scm.com/downloads | Pour pas perdre ton code comme tu perds tes affaires. |
| **VSCode** | https://code.visualstudio.com/ | L'editeur. Non, Word c'est pas un editeur de code. |

> **IMPORTANT** : Quand tu installes Python, COCHE "Add to PATH". Si tu coches pas, on peut plus rien pour toi.

---

## Etape 2 — Te connecter a GitHub

Le repo est prive. Ca veut dire que t'as pas le droit d'y acceder tant que t'es pas connecte. Oui, comme un mot de passe. Incroyable.

### Si tu utilises VSCode (recommande pour toi)

1. Ouvre VSCode
2. Icone de profil en bas a gauche
3. **Sign in with GitHub**
4. Ca ouvre ton navigateur. Connecte-toi. Oui, avec TON compte GitHub.
5. Clique "Authorize". C'est le gros bouton vert. Tu peux pas le rater. Enfin j'espere.

### Si tu te sens courageux (terminal)

```bash
gh auth login
```

Choisis GitHub.com > HTTPS > Login with browser. Suis les instructions. Lis les mots sur l'ecran. Tous les mots.

> Tu n'as pas `gh` ? Installe-le : https://cli.github.com/ — Oui c'est encore un truc a installer. Bienvenue dans l'informatique.

---

## Etape 3 — Recuperer le code

### Avec VSCode (sans risque de tout casser)

1. `Ctrl+Shift+P`
2. Tape `Git: Clone` — PAS "Git: Clean", PAS "Git: Close". **Clone.**
3. Colle ca :

```
https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox.git
```

4. Choisis ou tu veux sauvegarder. Genre "Documents". Pas le Bureau. On est pas des animaux.
5. Clique **Open**

### En terminal (si tu veux te sentir hackeur)

```bash
git clone https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox.git
cd MSPR2-NTL-SysToolbox
```

Bravo. T'as copie un dossier. C'est exactement ce que `git clone` fait. Impressionnant, non ?

---

## Etape 4 — Installer les dependances

Ouvre un terminal **dans le dossier du projet** (VSCode : Terminal > New Terminal) et tape :

```bash
pip install -r requirements.txt
```

Ca installe les librairies. Non, c'est pas un virus. Oui, c'est normal que ca prenne du temps.

> Si ca dit "pip not found" c'est que t'as pas coche "Add to PATH" a l'etape 2. Relis l'etape 2. Lentement.

---

## Etape 5 — Aller sur ta branche

T'as pas le droit de toucher a la branche principale. C'est comme ca. Accepte.

```bash
git checkout feature/module-XXX
```

Remplace `XXX` par ton module. C'est ecrit juste la :

| Toi | Ta branche | Ton fichier |
|-----|-----------|-------------|
| Blaise | `feature/module-diagnostic` | `src/modules/diagnostic.py` |
| Ojvind | `feature/module-backup` | `src/modules/backup.py` |
| Zaid | `feature/module-audit` | `src/modules/audit.py` |

**Tu touches QUE ton fichier.** Si tu modifies autre chose, Ianis le saura. Ianis sait toujours.

---

## Etape 6 — Coder

Ouvre ton fichier. Code. C'est tout. Relis le `GUIDE.md` si t'as oublie comment faire.

---

## Etape 7 — Envoyer ton code

Quand t'as fini (ou quand tu crois avoir fini, ce qui est rarement la meme chose) :

```bash
git add src/modules/XXX.py
git commit -m "feat: add ma_fonction()"
git push origin feature/module-XXX
```

Puis previens Ianis sur WhatsApp. Pas par pigeon voyageur.

---

## Les erreurs que tu vas forcement faire

| Erreur | Pourquoi | Solution |
|--------|----------|----------|
| `access denied` / `404` | T'es pas connecte a GitHub | Relis l'etape 2. Oui, encore. |
| `pip not found` | T'as pas coche "Add to PATH" | Reinstalle Python. Coche la case. LA case. |
| `ModuleNotFoundError` | T'as pas installe les dependances | `pip install -r requirements.txt` |
| `not a git repository` | T'es pas dans le bon dossier | `cd MSPR2-NTL-SysToolbox` |
| Tout est casse | T'as touche a un fichier qui est pas le tien | Previens Ianis. Pleure un peu. Ca ira. |

---

## Regles a ne JAMAIS enfreindre

1. **Ne touche PAS aux fichiers des autres.** Jamais. Meme si tu penses que c'est une bonne idee. Ca ne l'est pas.
2. **Ne push PAS sur `master`.** C'est le travail d'Ianis. Toi tu push sur ta branche.
3. **Ne fais PAS `git push --force`.** Si tu sais pas ce que c'est, tant mieux. Continue a pas savoir.
4. **Ne supprime PAS des fichiers au hasard.** "Ca marchait pas alors j'ai supprime" n'est pas une strategie.

---

> Si apres tout ca tu es toujours bloque, envoie un message a Ianis. Il jugera en silence mais il t'aidera quand meme.
