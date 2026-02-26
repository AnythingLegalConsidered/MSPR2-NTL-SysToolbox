# main.py — Le menu interactif

> Fichier : `src/main.py`
> Rôle : Point d'entrée de l'application. Affiche un menu, prend les choix de l'utilisateur, lance le bon module.

## Comment ça marche

```
Lancement : python src/main.py [--config chemin/config.yaml]
```

### Flux principal

```
Démarrage
  │
  ├─ 1. Charger la config (config.yaml + .env)
  ├─ 2. Activer les logs
  │
  └─ 3. Boucle menu principal
       │
       ├─ 1. Diagnostic  ──► sous-menu diagnostic
       ├─ 2. Backup      ──► sous-menu backup
       ├─ 3. Audit       ──► sous-menu audit
       └─ 0. Quitter
```

### Exemple : l'utilisateur lance un diagnostic AD/DNS

```
Menu principal → choix "1" (Diagnostic)
  └─ Sous-menu diagnostic → choix "1" (Vérifier AD/DNS)
       └─ Prompt : "IP du DC (défaut: 192.168.10.10) : "
            └─ L'utilisateur appuie Entrée (utilise le défaut)
                 └─ Appel : diagnostic.run(config, "192.168.10.10", action="check_ad_dns")
                      └─ Résultat affiché en JSON + sauvegardé dans output/logs/
```

## Ce que fait chaque sous-menu

| Module | Actions disponibles |
|--------|-------------------|
| **Diagnostic** | 1. Vérifier AD/DNS — 2. Tester MySQL — 3. État serveur Windows — 4. État serveur Ubuntu |
| **Backup** | 1. Sauvegarder BDD — 2. Exporter table CSV |
| **Audit** | 1. Scanner réseau — 2. Inventaire matériel — 3. Vérifier OS EOL — 4. Générer rapport |

## Comment un module est appelé

```python
# main.py appelle toujours la même signature :
result = module.run(config, target, action="nom_de_la_fonction")

# config  → dict complet du config.yaml (déjà résolu)
# target  → IP, hostname, nom de BDD... selon l'action
# action  → quelle fonction exécuter dans le module
```

Le résultat est ensuite :
1. Affiché dans le terminal (`print_result()`)
2. Sauvegardé en JSON dans `output/logs/`

## Gestion des erreurs

| Situation | Comportement |
|-----------|-------------|
| Module pas encore codé | Message "Module non disponible", retour au menu |
| Config manquante | Message d'erreur, l'app quitte proprement |
| Erreur dans un module | Message d'erreur affiché, retour au menu (pas de crash) |
| Ctrl+C | Quitte proprement avec message "Arrêt" |

## Cibles par défaut

Quand l'utilisateur appuie Entrée sans rien taper, `main.py` utilise les valeurs du `config.yaml` :

| Action | Cible par défaut |
|--------|-----------------|
| `check_ad_dns` | IP de DC01 (`192.168.10.10`) |
| `check_mysql` | IP de WMS-DB (`192.168.10.21`) |
| `backup_database` | Nom de la BDD (`wms`) |
| `scan_network` | Plage réseau (`192.168.10.0/24`) |
