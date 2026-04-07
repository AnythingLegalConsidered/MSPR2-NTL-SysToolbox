"""
NTL-SysToolbox — CARTE DES FICHIERS (ouvrir ici en premier)
============================================================

QUESTION DU JURY                          → OUVRIR CE FICHIER
──────────────────────────────────────────────────────────────

"Comment marche le menu CLI ?"            → src/main.py
  Menu interactif Rich, dispatch vers les 3 modules.

"Comment chargez-vous la config ?"        → src/config_loader.py
  Lecture YAML + .env, remplacement des ${VAR} par les secrets.

"C'est quoi le contrat entre modules ?"   → src/interfaces.py
  build_result(), exit codes (0-3), exceptions communes.

"Comment faites-vous le backup MySQL ?"   → src/modules/backup.py
  mysqldump local ou via SSH (paramiko), export CSV.

"Comment testez-vous le reseau ?"         → src/utils/network.py
  ping, check port TCP, resolution DNS, banner grab, version MySQL, HTTP check.

"Comment detectez-vous l'OS ?"            → src/utils/network.py  (fonction ping_host)
  platform.system() → adapte la commande ping Windows vs Linux.

"Comment securisez-vous les inputs ?"     → src/utils/validation.py
  Anti path-traversal, validation port, validation plage reseau, sanitize filename.

"Comment affichez-vous les resultats ?"   → src/utils/output.py
  Affichage JSON Rich/brut, sauvegarde JSON horodate, config logging.

POURQUOI DES __init__.py PARTOUT ?
──────────────────────────────────
Les fichiers __init__.py disent a Python "ce dossier est un package importable".
Sans eux, les imports comme `from src.modules import backup` echoueraient.
→ C'est obligatoire pour que Python reconnaisse src/, modules/, utils/ comme packages.


POURQUOI audit/ ET diagnostic/ SONT DES DOSSIERS, MAIS backup EST UN FICHIER ?
───────────────────────────────────────────────────────────────────────────────
Audit et Diagnostic ont ete decoupes en plusieurs fichiers (sous-packages) :
  - diagnostic/  →  __init__.py (entry point) + checks.py (fonctions de test) + constant.py
  - audit/       →  __init__.py (entry point) + scanner.py (scan reseau + EOL)
Backup n'a que 2 fonctions (dump SQL + export CSV) → un seul fichier backup.py suffit.

Pour Python c'est transparent : `from src.modules import backup` et
`from src.modules import diagnostic` fonctionnent pareil, que ce soit
un fichier .py ou un dossier avec __init__.py.


ARCHITECTURE GLOBALE :
─────────────────────
  main.py  →  charge config_loader.py
           →  affiche menu (Rich)
           →  appelle modules/<module>.py  →  qui utilisent utils/network.py
                                           →  et retournent build_result() (interfaces.py)
                                           →  resultat affiché via utils/output.py

ARBORESCENCE MODULES :
─────────────────────
  src/modules/
  ├── __init__.py          (package marker)
  ├── _template.py         (modele vide pour creer un nouveau module)
  ├── backup.py            (fichier unique — dump SQL + export CSV)
  ├── audit/               (sous-package — plusieurs fichiers)
  │   ├── __init__.py      (point d'entree + fonction run())
  │   └── scanner.py       (scan reseau nmap + detection EOL)
  └── diagnostic/          (sous-package — plusieurs fichiers)
      ├── __init__.py      (point d'entree + fonction run())
      ├── checks.py        (tests AD/DNS, MySQL, services Linux, HTTP)
      └── constant.py      (constantes : ports par defaut, seuils)
"""
