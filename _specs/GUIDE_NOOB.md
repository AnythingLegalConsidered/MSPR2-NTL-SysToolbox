# Le Guide Ultime pour Tocards — NTL-SysToolbox

> Ce guide existe parce que quelqu'un dans cette equipe a demande "c'est quoi un terminal".
> On ne donnera pas de nom. Mais son prenom rime avec "aide".

---

## Etape 0 — Le diagnostic mental

Avant de commencer, un petit QCM rapide :

- **Tu sais ce qu'est Git ?** → Passe a l'etape 2.
- **Tu penses que Git c'est le bruit que fait ton chat quand il vomit ?** → Lis tout depuis le debut. Lentement. Avec le doigt sur l'ecran si ca t'aide.
- **Tu as deja supprime `System32` parce qu'un mec sur Discord t'a dit que ca accelerait le PC ?** → Ferme ce guide. Eteins le PC. Sors prendre l'air. Reconsidere tes choix de carriere.

---

## Etape 1 — Installer les logiciels (oui, AVANT de coder, incroyable)

| Logiciel | Lien | Explication pour les... debutants |
|----------|------|----------------------------------|
| **Python** | https://www.python.org/downloads/ | Le langage qu'on utilise. Non, on peut pas faire le projet en Scratch. J'ai deja demande. |
| **Git** | https://git-scm.com/downloads | Le truc qui fait que quand tu supprimes tout par accident a 3h du mat', c'est pas grave. En theorie. |
| **VSCode** | https://code.visualstudio.com/ | L'editeur de code. Si tu codes sur Notepad, on est pas amis. Si tu codes sur Word, on est pas de la meme espece. |

### Le piege de l'installation Python

Il y a une case. UNE. SEULE. CASE. Elle dit **"Add to PATH"**. Elle est en bas de la fenetre. Si tu la coches pas, dans 15 minutes tu seras en train de googler "pip is not recognized" et tu te sentiras tres, tres seul.

```
[x] Add Python to PATH   ← COCHE CA OU JE VIENS CHEZ TOI
[ ] Install for all users
```

---

## Etape 2 — Se connecter a GitHub (le videur de la boite de nuit)

Notre repo est prive. C'est comme un bar select : si t'es pas sur la liste, tu rentres pas. Et spoiler : tu es sur la liste, mais faut quand meme montrer ta carte d'identite.

### Methode "j'ai peur du terminal" (VSCode)

1. Ouvre VSCode
2. Cherche l'icone de profil. C'est un petit bonhomme. En bas a gauche. Oui la. NON PAS LA. Plus bas. Voila.
3. **"Sign in with GitHub"**
4. Ton navigateur s'ouvre et te demande de te connecter. C'est le moment de te rappeler que ton mot de passe c'est pas `123456`. Ah si ? Change-le. La. Maintenant. On attend.
5. Clique **"Authorize"**. C'est le bouton vert. Il est GROS. Il est VERT. C'est comme un feu de circulation : vert = go. Tu vois, on fait des analogies simples pour toi.

### Methode "regardez-moi je suis un hackeur" (terminal)

```bash
gh auth login
```

Tu choisis GitHub.com, HTTPS, "Login with a web browser". Ca ouvre ton navigateur. Tu te connectes. Tu autorises. C'est exactement la meme chose qu'au-dessus mais en moins joli et en plus lent. Mais au moins tu te sens comme dans Matrix.

> Pas de `gh` ? → https://cli.github.com/
> Pas de navigateur ? → T'es sur quoi la, une Nintendo DS ?

---

## Etape 3 — Cloner le repo (telecharger le projet quoi)

"Cloner" en langage normal ca veut dire "copier le projet sur ton PC". On dit "cloner" parce que "copier" c'est pas assez pretentieux pour des developpeurs.

### La methode point-and-click pour ceux qui ont grandi avec une souris dans la main

1. `Ctrl+Shift+P` dans VSCode. C'est 3 touches. Ensemble. En meme temps. Comme un accord de guitare, sauf que toi t'arrives a faire ni l'un ni l'autre.
2. Tape **"Git: Clone"**. Attention :
   - `Git: Clone` ✅ OUI
   - `Git: Clean` ❌ NON (ca efface des trucs, comme toi tu effaces tes chances de reussite)
   - `Git: Close` ❌ CA EXISTE MEME PAS MAIS TU SERAIS CAPABLE DE CHERCHER
3. Colle ce lien. Ctrl+V. Tu sais faire ca au moins ?

```
https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox.git
```

4. Sauvegarde dans "Documents". Pas sur le Bureau. Le Bureau c'est pas un dossier de travail, c'est un cimetiere de raccourcis et de screenshots que tu supprimeras jamais.
5. VSCode dit "Open?". Tu dis oui. C'est le seul engagement qu'on te demande dans ta vie.

### La methode "je tape des commandes donc je suis superieur"

```bash
git clone https://github.com/AnythingLegalConsidered/MSPR2-NTL-SysToolbox.git
cd MSPR2-NTL-SysToolbox
```

Bravo. T'as fait l'equivalent numerique de "telecharger une piece jointe". Veux-tu un trophee ?

---

## Etape 4 — Installer les dependances

```bash
pip install -r requirements.txt
```

Ca telecharge les librairies Python dont on a besoin. C'est comme faire les courses avant de cuisiner. Tu cuisines pas sans ingredients. Enfin... vu ton niveau, tu serais capable d'essayer.

Ca prend 1-2 minutes. C'est normal. C'est pas plante. Pose ton telephone. Attends. Je sais, c'est dur pour ta generation.

> **Si ca dit `pip not found`** : t'as pas coche la case a l'etape 1. Je le savais. JE LE SAVAIS. Reinstalle Python et cette fois lis les instructions au lieu de cliquer "Next Next Next Finish" comme un robot avec un TDA.

---

## Etape 5 — Ta branche (ton petit coin a toi)

Git, c'est comme un immeuble. La branche `master` c'est l'appartement du proprietaire (Ianis). Toi, t'as ta chambre de bonne au 6eme sans ascenseur. Et t'as PAS le droit de rentrer dans l'appart du proprio.

```bash
git checkout feature/module-XXX
```

| Qui es-tu dans cette tragedie | Ta branche | Le SEUL fichier que tu as le droit de toucher |
|-------------------------------|-----------|----------------------------------------------|
| Blaise | `feature/module-diagnostic` | `src/modules/diagnostic.py` |
| Ojvind | `feature/module-backup` | `src/modules/backup.py` |
| Zaid | `feature/module-audit` | `src/modules/audit.py` |

Si tu modifies un autre fichier, Ianis recevra une notification. Ianis voit TOUT. Ianis est omniscient. Ianis est le Git himself. Crains-le.

---

## Etape 6 — Coder

C'est la partie ou normalement t'as appris a faire des trucs en 3 ans d'ecole. Normalement.

Ouvre ton fichier. Lis le `GUIDE.md` pour savoir quoi coder. Si t'as la flemme de lire un autre guide alors que tu es DEJA en train de lire celui-ci, je peux rien pour toi. Personne peut rien pour toi. Tu es au-dela de toute aide humaine.

---

## Etape 7 — Envoyer ton chef-d'oeuvre

```bash
git add src/modules/TON_FICHIER.py       # ton fichier, PAS celui des autres
git commit -m "feat: add ma_fonction()"   # un message qui DECRIT ce que t'as fait
git push origin feature/module-XXX        # envoie sur GitHub
```

Ensuite, message WhatsApp a Ianis : "C'est push". Pas besoin d'un roman. Pas besoin d'un PowerPoint. Pas besoin d'un vocal de 4 minutes. "C'est push." Point.

---

## Le tableau des catastrophes annoncees

| Le symptome | Le diagnostic | Le traitement |
|-------------|--------------|---------------|
| `access denied` | T'as pas fait l'etape 2. T'as SAUTE une etape. Dans un guide de 7 etapes. | Retourne a l'etape 2. Lentement. |
| `pip not found` | La fameuse case. LA CASE. | Reinstalle Python + coche la case. Tatoue-toi "PATH" sur le bras si ca peut aider. |
| `ModuleNotFoundError` | T'as pas fait `pip install`. Tu voulais que les modules s'installent par la pensee ? | `pip install -r requirements.txt` |
| `not a git repository` | T'es perdu dans ton propre PC. | `cd MSPR2-NTL-SysToolbox` et reflechis a ta vie. |
| `everything up to date` apres un push | T'as oublie de `git add` et `git commit`. T'as push du VIDE. Comme ton regard en ce moment. | Fais le `git add` et `git commit` d'abord. |
| `merge conflict` | T'as touche au fichier d'un autre. Pourquoi. POURQUOI. | Appelle Ianis. Prepare des excuses. Et un cafe. |
| "Mon ecran est noir" | ... | Appuie sur le bouton power. Celui du PC hein, pas celui de la prise. Quoique... |

---

## Les 4 Commandements Sacres

**I.** Tu ne toucheras point aux fichiers d'autrui, car le `git blame` est eternel et la honte est permanente.

**II.** Tu ne pusheras point sur `master`, car Ianis descendra sur toi tel la foudre divine un lundi matin.

**III.** Tu ne feras point de `git push --force`, car c'est l'equivalent numerique de rouler a contresens sur l'autoroute en disant "ca devrait passer".

**IV.** Tu ne supprimeras point de fichiers au hasard, car "ca marchait pas alors j'ai tout supprime" c'est pas du debugging, c'est de l'incendie volontaire.

---

## FAQ (Foire Aux Questions Qu'on Aurait Prefere Ne Jamais Entendre)

**Q : "Ca marche pas"**
C'est pas une question. C'est pas un rapport de bug. C'est un cri dans le vide. Lis le message d'erreur. Avec tes yeux. Google le message. Avec tes doigts. PUIS demande de l'aide.

**Q : "J'ai modifie main.py sans faire expres"**
"Sans faire expres" tu as ouvert un fichier, tape dedans, et sauvegarde. C'est 3 actions volontaires. Tape `git checkout -- src/main.py` pour annuler et va reflechir a la definition du mot "expres".

**Q : "J'ai push sur master"**
Arrete de lire ce guide. Appelle Ianis. Pas dans 5 min. Pas apres manger. MAINTENANT. Et commence a chercher un nouveau groupe de projet.

**Q : "Ca faisait la meme chose hier et ca marchait"**
Non. Ca faisait pas la meme chose. T'as change un truc. Tu sais pas quoi. Mais t'as change un truc. `git diff` te montrera ton mensonge.

**Q : "C'est quoi un terminal ?"**
C'est le rectangle noir ou on tape des commandes. Tu sais, le truc que tu vois dans les films quand le "hackeur" tape tres vite sur son clavier. Sauf que toi, tu vas taper `pip install` et te tromper 3 fois dans l'orthographe de "install".

---

> Si apres tout ca tu bloques encore, envoie un message a Ianis.
> Il t'aidera avec le sourire.
> Mais sache que chaque question basique que tu poses lui enleve une annee d'esperance de vie.
> Alors fais un effort. Pour Ianis. Pour l'equipe. Pour l'humanite.
