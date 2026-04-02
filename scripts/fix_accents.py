# -*- coding: utf-8 -*-
"""Fix missing French accents in gen_pptx.py."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('output/gen_pptx.py', 'r', encoding='utf-8') as f:
    content = f.read()

fixes = [
    ("Problematique", "Problématique"),
    ("identifies dans", "identifiés dans"),
    ("orientee service", "orientée service"),
    ("surveilles", "surveillés"),
    ("testees", "testées"),
    ("d'integrite", "d'intégrité"),
    ("non maitrise", "non maîtrisé"),
    ("non identifies", "non identifiés"),
    ("independants", "indépendants"),
    ("independant mais", "indépendant mais"),
    ("horodatees", "horodatées"),
    ("CSV horodate", "CSV horodaté"),
    ("structure exploitable", "structuré exploitable"),
    ("concu pour", "conçu pour"),
    ("s'integrer", "s'intégrer"),
    ("appelee", "appelée"),
    ("donnees specifiques", "données spécifiques"),
    ("donnees...", "données..."),
    ("Machines detectees", "Machines détectées"),
    ("detecte", "détecté"),
    ("Resultats combines", "Résultats combinés"),
    ("Resultats JSON", "Résultats JSON"),
    ("tableau colore", "tableau coloré"),
    ("reelles", "réelles"),
    ("reelle de NTL", "réelle de NTL"),
    ("qualite a chaque", "qualité à chaque"),
    ("deployer et utiliser", "déployer et utiliser"),
    ("pour deployer", "pour déployer"),
    ("numerotees", "numérotées"),
    ("versionnee", "versionnée"),
    ("maniere fiable et tracable", "manière fiable et traçable"),
    ("operationnels", "opérationnels"),
    ("representent", "représentent"),
    ("obsoletes et", "obsolètes et"),
    ("equipements du parc sont obsoletes", "équipements du parc sont obsolètes"),
    ("Declenchement", "Déclenchement"),
    ("parallele", "parallèle"),
    ("Verification", "Vérification"),
    ("categorisation des", "catégorisation des"),
    ("resolution DNS", "résolution DNS"),
    ("temps de reponse", "temps de réponse"),
    ("Mesures de securite", "Mesures de sécurité"),
    ("autorise", "autorisé"),
    ("Securite des credentials", "Sécurité des credentials"),
    ("zero secret", "zéro secret"),
    ("defini en amont", "défini en amont"),
    ("developpement parallele", "développement parallèle"),
    ("dependance reseau", "dépendance réseau"),
    ("discute en equipe et assume", "discuté en équipe et assumé"),
    ("repond au cahier des charges", "répond au cahier des charges"),
    ("Documentation complete", "Documentation complète"),
    ("par defaut", "par défaut"),
    ("Guide equipe", "Guide équipe"),
    ("Aide-memoire", "Aide-mémoire"),
    ("de reference de", "de référence de"),
    ("Execution de reference", "Exécution de référence"),
    ("Scenario complet", "Scénario complet"),
    ("presente son module", "présente son module"),
    ("Verifier que le DC01 repond", "Vérifier que le DC01 répond"),
    ("generes dans", "générés dans"),
    ("siege sont-ils", "siège sont-ils"),
    ("Backup planifie", "Backup planifié"),
    ("mise a jour auto", "mise à jour auto"),
    ("Visualisation des resultats", "Visualisation des résultats"),
    ("prets pour vos questions", "prêts pour vos questions"),
    ("Portabilite Windows", "Portabilité Windows"),
    ("Acces WinRM", "Accès WinRM"),
    ("modules lies", "modules liés"),
    ("Integration Zabbix", "Intégration Zabbix"),
    ("sont deja compatibles", "sont déjà compatibles"),
    ("Table des matieres", "Table des matières"),
    ("rapport trie", "rapport trié"),
    ("l'equipe", "l'équipe"),
    ("Separation code", "Séparation code"),
]

count = 0
for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"  {old} -> {new}")

with open('output/gen_pptx.py', 'w', encoding='utf-8') as f:
    f.write(content)
print(f"\n{count} corrections applied")
