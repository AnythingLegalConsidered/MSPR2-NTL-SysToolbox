# Comment implémenter un module

> Template : `src/modules/_template.py`
> Rôle : Guide pas-à-pas pour créer un module (diagnostic, backup ou audit).

## Étape 1 — Copier le template

```bash
cp src/modules/_template.py src/modules/diagnostic.py
```

## Étape 2 — Renommer les placeholders

En haut du fichier, change :

```python
MODULE_NAME = "diagnostic"  # était "[NOM DU MODULE]"
```

## Étape 3 — Implémenter la fonction run()

C'est le point d'entrée. `main.py` appelle toujours `run()`.

```python
def run(config: dict, target: str, **kwargs) -> dict:
    action = kwargs.get("action", "")

    if action == "check_ad_dns":
        return check_ad_dns(config, target)
    elif action == "check_mysql":
        return check_mysql(config, target)
    else:
        raise ModuleExecutionError(f"Action inconnue: {action}")
```

**Paramètres reçus :**
- `config` → tout le config.yaml (déjà résolu, secrets inclus)
- `target` → l'IP ou nom saisi par l'utilisateur
- `action` → quelle fonction appeler (passé par main.py)

## Étape 4 — Implémenter les fonctions

### Les 2 règles d'or

1. **Toujours** retourner `build_result()`
2. **Toujours** attraper les exceptions (jamais de crash)

### Exemple concret : check_ad_dns

```python
def check_ad_dns(config: dict, target: str) -> dict:
    try:
        # 1. Tester le port LDAP
        ldap_ok = check_port(target, 389, timeout=config.get("general", {}).get("timeout", 10))

        # 2. Tester la résolution DNS
        dns_result = resolve_dns("ntl.local", dns_server=target)
        dns_ok = dns_result is not None

        # 3. Déterminer le status
        if ldap_ok and dns_ok:
            status, code = "OK", EXIT_OK
            msg = "AD et DNS opérationnels"
        elif not ldap_ok:
            status, code = "CRITICAL", EXIT_CRITICAL
            msg = f"LDAP injoignable sur {target}:389"
        else:
            status, code = "WARNING", EXIT_WARNING
            msg = f"DNS ne résout pas ntl.local"

        return build_result(
            module=MODULE_NAME,
            function="check_ad_dns",
            status=status,
            exit_code=code,
            target=target,
            details={"ldap": ldap_ok, "dns": dns_ok, "dns_result": dns_result},
            message=msg,
        )

    except Exception as e:
        logger.error("check_ad_dns failed: %s", e)
        return build_result(
            module=MODULE_NAME,
            function="check_ad_dns",
            status="UNKNOWN",
            exit_code=EXIT_UNKNOWN,
            target=target,
            details={"error": str(e)},
            message=f"Impossible de vérifier {target}: {e}",
        )
```

## Checklist avant de push

- [ ] `MODULE_NAME` est correct
- [ ] `run()` dispatch vers les bonnes fonctions
- [ ] Chaque fonction retourne `build_result()`
- [ ] Chaque fonction a un try/except (pas de crash possible)
- [ ] Les imports sont en haut du fichier
- [ ] `ruff` et `mypy` passent (`make lint && make typecheck`)
