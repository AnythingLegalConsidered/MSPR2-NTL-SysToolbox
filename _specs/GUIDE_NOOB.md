# Guide de Survie pour Boulets — NTL-SysToolbox

> Si tu lis ce guide, c'est que t'as pas reussi a cloner un repo Git en 2026.
> On est fiers de toi. Non je deconne, on est consterne.

---

## Etape 0 — Verifie que t'es pret

- [ ] T'as un PC ? (pas une calculatrice TI-82, un vrai PC)
- [ ] Il est allume ?
- [ ] T'as trouve le navigateur ? (Non, Google c'est pas un navigateur. Chrome, Edge, Firefox. Cherche l'icone. Prends ton temps.)

Formidable. T'as deja fait mieux que ce qu'on attendait de toi.

---

## Etape 1 — Installer les trucs de base

On va te demander d'installer 3 logiciels. Oui, 3. On sait que c'est beaucoup pour toi mais accroche-toi.

| Truc | Lien | C'est quoi parce que visiblement faut expliquer |
|------|------|------------------------------------------------|
| **Python** | https://www.python.org/downloads/ | Le langage de programmation. Tu sais, le metier que t'as choisi. Rappelle-toi. |
| **Git** | https://git-scm.com/downloads | Pour sauvegarder ton code. Parce que "je l'ai envoye par mail" c'est pas du versionning. |
| **VSCode** | https://code.visualstudio.com/ | L'editeur de code. Non, le Bloc-notes ca compte pas. Non, Word non plus. Non, PowerPoint non plus. Arrete. |

> **ATTENTION CRITIQUE** : Quand tu installes Python, il y a une case "Add to PATH" **EN BAS DE LA FENETRE**. Tu la coches. Si tu la coches pas, t'es condamne a revenir ici dans 20 minutes en pleurant. On t'aura prevenu.

---

## Etape 2 — Te connecter a GitHub

Le repo est **prive**. Ca veut dire que si t'es pas connecte, GitHub va te regarder droit dans les yeux et te dire "non". Comme ta derniere soiree Tinder.

### Option A — Avec VSCode (le mode assistanat)

1. Ouvre VSCode. Si tu sais pas ou il est, t'as un probleme plus grave que ce guide peut resoudre.
2. En bas a gauche (ou en haut a droite, oui ils bougent les boutons, bienvenue en 2026), y'a une **icone de profil**. Clique dessus.
3. Clique **"Sign in with GitHub"**. Pas "Sign in with Microsoft". Pas "Sign in with Google". **GitHub**. C'est ecrit. Lis.
4. Ton navigateur s'ouvre. Connecte-toi avec **TON** compte GitHub. Pas celui d'Ianis. Pas celui de ta mere. Le tien.
5. Clique "Authorize". C'est le GROS BOUTON VERT. Si tu le rates, va chez l'ophtalmo.

### Option B — En terminal (mode "je suis un vrai dev" alors que non)

```bash
gh auth login
```

Choisis : GitHub.com > HTTPS > Login with browser.

Ensuite, lis. Les. Mots. Sur. L'ecran. Je sais que c'est un concept revolutionnaire mais essaie.

> T'as pas `gh` ? Installe-le : https://cli.github.com/
> Oui, c'est ENCORE un truc a installer. T'as choisi l'informatique, personne t'a force. Enfin j'espere.

---

## Etape 3 — Cloner le repo

"Cloner" ca veut dire "copier le projet sur ton PC". Oui, c'est juste ca. On aurait pu dire "telecharger" mais on est des developpeurs, faut qu'on se sente intelligents.

### Avec VSCode (recommande pour ton niveau)

1. Appuie sur `Ctrl+Shift+P`. Oui, les 3 touches EN MEME TEMPS. C'est comme un accord de piano, sauf que la c'est utile.
2. Tape `Git: Clone`. Pas "Git Clean". Pas "Git Close". Pas "Git Clone Wars". **Git: Clone.**
3. Colle cette URL. EXACTEMENT cette URL. Pas a peu pres. EXACTEMENT :

```
https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox.git
```

4. Choisis un dossier ou sauvegarder. Je te conseille "Documents" parce que le Bureau c'est pour les sauvages et le dossier Telechargements c'est la ou les fichiers vont mourir.
5. Clique **Open** quand VSCode te propose d'ouvrir le projet.

### En terminal (pour ceux qui veulent jouer aux hackeurs dans leur chambre)

```bash
git clone https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox.git
cd MSPR2-NTL-SysToolbox
```

Felicitations, t'as copie-colle 2 lignes. Mets-le sur ton CV.

---

## Etape 4 — Installer les dependances

Ouvre un terminal **dans le dossier du projet**. Dans VSCode : menu Terminal > New Terminal. C'est pas complique, meme toi tu peux y arriver.

```bash
pip install -r requirements.txt
```

Ca va installer plein de trucs. Non, c'est pas un virus. Oui, c'est normal que ca prenne du temps. Non, eteindre le PC en plein milieu c'est pas une bonne idee.

> **"pip not found"** = t'as pas coche "Add to PATH" a l'etape 1. Tu te rappelles quand j'ai dit que tu reviendrais en pleurant ? Voila. Reinstalle Python. Coche. La. Case.

---

## Etape 5 — Aller sur ta branche

La branche `master`, c'est la branche d'Ianis. Toi, t'as pas le droit d'y toucher. C'est comme le frigo de tes parents : tu prends ta part et tu refermes.

```bash
git checkout feature/module-XXX
```

Remplace `XXX` par ton module. Regarde le tableau si t'as deja oublie ton propre prenom :

| C'est toi ca ? | Ta branche | Ton SEUL fichier |
|----------------|-----------|------------------|
| Blaise | `feature/module-diagnostic` | `src/modules/diagnostic.py` |
| Ojvind | `feature/module-backup` | `src/modules/backup.py` |
| Zaid | `feature/module-audit` | `src/modules/audit.py` |

**Tu touches QUE ton fichier.** Un seul. Le tien. Si tu modifies un autre fichier, Ianis va le voir dans le diff et il va t'envoyer un message passif-agressif sur WhatsApp. Et tu l'auras merite.

---

## Etape 6 — Coder (la partie ou tu es cense savoir faire)

Ouvre ton fichier. Ecris du code. En Python. Pas en HTML. Pas en CSS. Pas en francais. En **Python**.

Relis le `GUIDE.md` si t'as deja oublie comment ecrire une fonction. Ce qui, statistiquement, est probable.

---

## Etape 7 — Envoyer ton code (le moment de verite)

Quand tu penses avoir fini — spoiler : t'as surement oublie un truc — tape :

```bash
git add src/modules/XXX.py
git commit -m "feat: add ma_fonction()"
git push origin feature/module-XXX
```

C'est 3 commandes. Trois. T-R-O-I-S. Copie-colle si t'as peur de te tromper. Y'a pas de honte. Enfin un peu quand meme.

Puis previens Ianis sur WhatsApp. Pas par SMS. Pas par mail. Pas par telepathie. **WhatsApp.**

---

## Les erreurs que tu VAS faire (c'est pas une question de "si")

| L'erreur | Pourquoi t'as fait ca | Comment te sauver |
|----------|----------------------|-------------------|
| `access denied` / `404` | T'es pas connecte a GitHub, champion | Relis l'etape 2. Oui, encore. Et cette fois LIS. |
| `pip not found` | T'as pas coche "Add to PATH". On avait dit. | Reinstalle Python. Coche la case. LA. CASE. |
| `ModuleNotFoundError` | T'as zappe l'etape 4. Bravo. | `pip install -r requirements.txt` |
| `not a git repository` | T'es dans le mauvais dossier. Genre tu codes depuis le Bureau. | `cd MSPR2-NTL-SysToolbox` |
| `merge conflict` | T'as touche un fichier qui est pas le tien. | Previens Ianis. Dis une priere. |
| "Ca marche pas" (sans plus de details) | T'es incapable de lire un message d'erreur | Lis. Le. Message. D'erreur. Tout le message. Avec tes yeux. |
| L'ecran est noir | T'as eteint le PC | Rallume-le. |

---

## Les 4 Commandements

1. **Tu ne toucheras point aux fichiers des autres.** Meme si "c'est juste un espace". Meme si "c'est pour aider". Meme si t'as une illumination divine. NON.

2. **Tu ne pusheras point sur `master`.** Master c'est sacre. C'est le territoire d'Ianis. Toi tu restes sur ta branche, dans ton coin, bien sagement.

3. **Tu ne feras JAMAIS `git push --force`.** Si tu sais ce que c'est : non. Si tu sais pas ce que c'est : encore mieux, continue de pas savoir. Oublie que ca existe. Efface-le de ta memoire.

4. **Tu ne supprimeras point au hasard.** "Ca marchait pas alors j'ai tout supprime" c'est pas du debug, c'est de la pyromanie numerique.

---

## FAQ (Foire Aux Questions que tu devrais pas avoir besoin de poser)

**Q : Ca marche pas.**
R : C'est pas une question. Et lis le message d'erreur.

**Q : J'ai modifie main.py par erreur.**
R : Mais POURQUOI. `git checkout -- src/main.py` et va te remettre en question.

**Q : J'ai push sur master.**
R : ... Envoie un message a Ianis. Vite. Genre maintenant. Arrete de lire ce guide. MAINTENANT.

**Q : C'est quoi un terminal ?**
R : C'est la fenetre noire ou on tape des commandes. Tu sais, comme dans les films de hackeurs. Sauf que toi tu tapes `pip install` pas `hack the pentagon`.

**Q : J'ai tout casse.**
R : Respire. Ferme VSCode. Supprime le dossier du projet. Recommence a l'etape 3. Et cette fois, suis les instructions.

---

> Si apres ce guide tu es ENCORE bloque, envoie un message a Ianis.
> Il viendra t'aider. Il sourira. Mais dans sa tete, il se demandera comment t'as eu le bac.
> Et honnêtement, nous aussi.
