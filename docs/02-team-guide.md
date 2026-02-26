# Guide Equipe — NTL-SysToolbox

> **C'est le document de reference pour coder ton module.**
> Setup deja fait ? Commence ici. Sinon, va d'abord lire [01-getting-started.md](01-getting-started.md).

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

## Les 4 roles

| Qui | Branche | Fichier | Role |
|-----|---------|---------|------|
| **Ianis** (Lead) | `feature/cli-menu` | `main.py`, config, utils | Le menu + assemblage |
| **Blaise** | `feature/module-diagnostic` | `src/modules/diagnostic.py` | Verifier que les serveurs marchent |
| **Ojvind** | `feature/module-backup` | `src/modules/backup.py` | Sauvegarder la base de donnees |
| **Zaid** | `feature/module-audit` | `src/modules/audit.py` | Detecter les OS obsoletes |

**Regle d'or :** tu ne touches QUE ton fichier sur ta branche. Rien d'autre.

---

## Le pattern de base — Comment ecrire une fonction

Chaque fonction que tu codes doit suivre ce pattern. **Copie-le et adapte-le** :

```python
def ma_fonction(config: dict, target: str) -> dict[str, Any]:
    """Description de ce que fait la fonction."""
    logger.info("Running ma_fonction on %s", target)
    timeout = config.get("general", {}).get("timeout", 10)

    try:
        # --- Ta logique ici ---
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

### Par ou commencer

1. Copie le template (voir [01-getting-started.md](01-getting-started.md#6-creer-ta-branche-et-commencer))
2. Commence par `check_ad_dns()` — c'est la plus simple
3. Utilise `check_port()` de `src/utils/network.py` (deja code !) pour tester le port 389
4. Utilise `resolve_dns()` de `src/utils/network.py` (deja code !) pour tester le DNS

> Logique detaillee de chaque fonction : [03-module-logic.md](03-module-logic.md#module-1--diagnostic)

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

### Par ou commencer

1. Copie le template
2. Commence par `export_table_csv()` — c'est la plus simple
3. Tu te connectes a MySQL, tu fais un SELECT, tu ecris dans un fichier CSV
4. Puis attaque `backup_database()` — plus complexe car il faut SSH + mysqldump

> Logique detaillee de chaque fonction : [03-module-logic.md](03-module-logic.md#module-2--backup)

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

### Par ou commencer

1. Copie le template
2. Commence par `list_os_eol()` — c'est la plus simple (juste lire un fichier JSON)
3. Puis `audit_from_csv()` — lire un CSV et croiser avec le JSON
4. `scan_network()` et `generate_report()` sont plus complexes, on les fera ensemble

> Logique detaillee de chaque fonction : [03-module-logic.md](03-module-logic.md#module-3--audit)

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
    port = config.get("mysql", {}).get("port", 3306)
    user = config.get("mysql", {}).get("user", "root")
    password = config.get("mysql", {}).get("password", "")
    timeout = config.get("general", {}).get("timeout", 10)
```

Les secrets (mots de passe) sont dans le fichier `.env` et sont automatiquement injectes dans la config.

---

## Tester ta fonction en isolation

Tu n'as PAS besoin de lancer tout le menu pour tester. Cree un fichier temporaire `test_manual.py` a la racine :

```python
"""Test rapide — a supprimer avant le merge."""
from src.config_loader import load_config
from src.modules.diagnostic import check_ad_dns  # adapte a ta fonction

config = load_config("config/config.yaml")
result = check_ad_dns(config, "192.168.10.10")
print(result)
```

Lance le test :
```bash
python test_manual.py
```

> **IMPORTANT** : supprime `test_manual.py` avant de prevenir Ianis ! Ne le commit pas.

---

## Workflow Git — pas a pas

### Sauvegarder ton travail (a faire souvent !)

```bash
git status                                        # Voir ce qui a change
git add src/modules/diagnostic.py                 # Ton fichier uniquement
git commit -m "feat: add check_ad_dns()"          # Message clair
git push -u origin feature/module-diagnostic      # Premier push
git push                                          # Push suivants
```

### Convention des messages de commit

| Prefix | Quand l'utiliser | Exemple |
|--------|-----------------|---------|
| `feat:` | Nouvelle fonctionnalite | `feat: add check_ad_dns()` |
| `fix:` | Correction de bug | `fix: handle MySQL timeout` |
| `docs:` | Documentation | `docs: update README` |
| `test:` | Tests | `test: add test for check_mysql` |

### Quand ton module est pret

1. Push ta branche (`git push`)
2. Previens Ianis sur WhatsApp : "Ma branche est prete"
3. Ianis s'occupe du merge. Tu n'as rien d'autre a faire.

---

## Checklist avant de prevenir Ianis

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

## Planning simplifie

```
Etape 1 : Session de decisions par module (avec Ianis, en equipe)
Etape 2 : Chacun code sur sa branche
Etape 3 : Ianis merge tout
Etape 4 : On teste ensemble sur le lab
Etape 5 : Documentation + slides
Etape 6 : Soutenance
```

---

*Reference detaillee par fonction : [03-module-logic.md](03-module-logic.md)*
*Aide-memoire rapide : [cheatsheet.md](cheatsheet.md)*
