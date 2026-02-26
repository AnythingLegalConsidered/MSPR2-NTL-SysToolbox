# Configuration — Comment l'app récupère ses paramètres

> Fichiers : `src/config_loader.py`, `config/config.example.yaml`, `.env`

## Les 3 couches

```
config.example.yaml    ──►  Copier en config.yaml     ──►  L'app charge config.yaml
(template, committé)        (tes valeurs, PAS committé)     au démarrage

.env                   ──►  Les ${VAR} dans le YAML sont remplacées
(secrets, PAS committé)     par les vraies valeurs
```

### Concrètement

1. Tu copies `config/config.example.yaml` → `config/config.yaml`
2. Tu copies `.env.example` → `.env`
3. Tu mets tes vrais mots de passe dans `.env`
4. L'app fait le reste automatiquement

## Structure du config.yaml

```yaml
general:
  log_level: INFO        # DEBUG pour voir tout, INFO pour la normale
  output_dir: ./output   # Où les résultats JSON sont sauvés
  timeout: 10            # Timeout par défaut (secondes)

targets:                 # Les machines du réseau
  dc01:
    host: 192.168.10.10
    type: windows
    description: "Domain Controller — AD/DNS"
  wms_db:
    host: 192.168.10.21
    type: linux
    description: "WMS Database Server"

mysql:                   # Connexion MySQL
  host: 192.168.10.21
  port: 3306
  user: "${NTL_MYSQL_USER}"        # ← remplacé par la valeur dans .env
  password: "${NTL_MYSQL_PASSWORD}" # ← idem

ssh:                     # Connexion SSH (pour check Ubuntu)
  host: 192.168.10.21
  port: 22
  user: "${NTL_SSH_USER}"
  password: "${NTL_SSH_PASSWORD}"

audit:                   # Config du module audit
  network_range: "192.168.10.0/24"
  eol_database: "./data/eol_database.json"
```

## Comment la substitution fonctionne

```
Fichier .env :
  NTL_MYSQL_USER=wms_user
  NTL_MYSQL_PASSWORD=monSuperMotDePasse

Dans config.yaml :
  user: "${NTL_MYSQL_USER}"

Après chargement :
  user: "wms_user"        ← remplacé automatiquement
```

Le `config_loader.py` :
1. Charge le `.env` (via `python-dotenv`)
2. Lit le YAML
3. Parcourt toutes les valeurs récursivement
4. Remplace chaque `${VAR}` par la variable d'environnement correspondante
5. Si la variable n'existe pas → garde le placeholder + log warning

## Ajouter un nouveau serveur

Ajoute une entrée dans `targets:` du config.yaml :

```yaml
targets:
  mon_serveur:
    host: 192.168.10.30
    type: linux
    description: "Mon nouveau serveur"
```

Puis dans ton module, récupère-le via :

```python
host = config["targets"]["mon_serveur"]["host"]
```

## Erreurs courantes

| Problème | Cause | Solution |
|----------|-------|----------|
| `ModuleConfigError: config not found` | `config.yaml` n'existe pas | Copier `config.example.yaml` |
| `WARNING: Variable NTL_MYSQL_USER not found` | `.env` manquant ou variable absente | Vérifier le `.env` |
| YAML parse error | Indentation cassée dans le YAML | Vérifier les espaces (pas de tabs) |
