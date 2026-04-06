# Rapport d'Audit d'Obsolescence du Parc Informatique

---

**Client** : NordTransit Logistics (NTL)
**Prestataire** : Équipe MSPR TPRE511
**Date de l'audit** : Mars 2026
**Version du document** : 1.0
**Classification** : Confidentiel -- Usage interne NTL

---

## Sommaire

1. [Contexte et objectifs de l'audit](#1-contexte-et-objectifs-de-laudit)
2. [Méthodologie](#2-methodologie)
3. [Inventaire du parc informatique](#3-inventaire-du-parc-informatique)
4. [Analyse d'obsolescence par machine](#4-analyse-dobsolescence-par-machine)
5. [Synthèse par criticité](#5-synthese-par-criticite)
6. [Recommandations de migration](#6-recommandations-de-migration)
7. [Plan d'action recommandé](#7-plan-daction-recommande)
8. [Conclusion](#8-conclusion)

---

## 1. Contexte et objectifs de l'audit

### 1.1 Présentation de l'entreprise

NordTransit Logistics (NTL) est une PME spécialisée dans la logistique, implantée dans les Hauts-de-France. L'entreprise dispose de :

- **Siège social** : Lille
- **Entrepôts** : Lens, Valenciennes, Arras
- **Parc informatique** : 19 machines (serveurs et postes de travail)

L'infrastructure informatique de NTL supporte des fonctions critiques : gestion des entrepôts (WMS), téléphonie (IPBX), contrôleurs de domaine Active Directory, serveurs de fichiers, supervision, et postes de travail opérationnels sur les quais logistiques.

### 1.2 Objectifs de l'audit

L'audit répond à un besoin exprimé par la direction de NTL :

1. **Qualifier l'obsolescence** de chaque machine du parc informatique
2. **Évaluer les risques** liés aux systèmes en fin de vie (sécurité, conformité, continuité d'activité)
3. **Prioriser les migrations** en fonction de la criticité métier et du niveau d'obsolescence
4. **Fournir un plan d'action** réaliste pour planifier les mises à niveau

### 1.3 Périmètre

L'audit couvre l'ensemble des 19 machines répertoriées dans l'inventaire NTL, incluant :

- 11 serveurs (physiques et virtuels)
- 1 NAS de sauvegarde
- 7 postes de travail (siège et entrepôts)

---

## 2. Méthodologie

### 2.1 Outil utilisé : NTL-SysToolbox -- Module Audit

L'audit a été réalisé à l'aide du module **audit** de la toolbox NTL-SysToolbox, un outil développé spécifiquement pour ce projet. Le module est implémenté en Python et se compose de quatre fonctions principales :

| Fonction | Description |
|---|---|
| `scan_network()` | Scan réseau via nmap avec détection d'OS et catégorisation des services |
| `list_os_eol()` | Lecture de la base de données EOL (End of Life) contenant 18 entrées d'OS |
| `audit_from_csv()` | Croisement de l'inventaire CSV avec les dates de fin de support |
| `generate_report()` | Génération d'un rapport complet au format JSON, trié par criticité |

### 2.2 Base de données EOL

La base de données de référence (`data/eol_database.json`) contient les dates de fin de support officiel et étendu pour 18 systèmes d'exploitation :

- **Microsoft** : Windows Server 2022/2019/2016/2012 R2/2012/2008 R2, Windows 11/10/7
- **Canonical** : Ubuntu 24.04/22.04/20.04/18.04/16.04 LTS
- **Debian** : Debian 12/11/10
- **Red Hat** : CentOS 7

Les dates proviennent des annonces officielles des éditeurs. Les dates de support étendu (ESU pour Microsoft, Ubuntu Pro pour Canonical) sont prises en compte lorsqu'elles existent.

### 2.3 Approche d'analyse

L'analyse de chaque machine suit le processus suivant :

1. **Identification** : lecture de l'inventaire CSV (hostname, OS, version, rôle)
2. **Croisement EOL** : comparaison de l'OS installé avec la base de données de fin de support
3. **Classification** : attribution d'un niveau de criticité selon la grille suivante :

| Niveau | Critère | Signification |
|---|---|---|
| **CRITICAL** | Date EOL (y compris support étendu) dépassée | Plus aucun correctif de sécurité disponible. Risque immédiat. |
| **WARNING** | Fin de support dans moins de 2 ans (avant mars 2028) | Migration à planifier à court ou moyen terme. |
| **OK** | Support actif au-delà de mars 2028 | Aucune action immédiate requise. |

### 2.4 Date de référence

Toutes les analyses de ce rapport sont calculées à la date du **27 mars 2026**.

---

## 3. Inventaire du parc informatique

Le parc informatique de NTL se compose de 19 machines réparties comme suit :

| # | Hostname | Système d'exploitation | Rôle / Fonction | Site |
|---|---|---|---|---|
| 1 | DC01 | Windows Server 2022 | Contrôleur de domaine principal (AD/DNS) | Lille |
| 2 | DC02 | Windows Server 2019 | Contrôleur de domaine secondaire | Lille |
| 3 | WMS-DB | Ubuntu 20.04 LTS | Base de données MySQL (WMS) | Lille |
| 4 | WMS-APP | Ubuntu 20.04 LTS | Serveur applicatif (WMS) | Lille |
| 5 | IPBX-VM | CentOS 7 | Serveur IPBX téléphonie | Lille |
| 6 | SUPER-01 | Windows Server 2016 | Supervision Zabbix | Lille |
| 7 | SRV-FILE | Windows Server 2012 R2 | Serveur de fichiers (partages legacy) | Lille |
| 8 | SRV-PRINT | Windows Server 2008 R2 | Serveur d'impression | Lille |
| 9 | NAS-01 | Debian 10 | NAS de sauvegarde | Lille |
| 10 | SRV-INTRANET | Debian 11 | Intranet / Wiki interne | Lille |
| 11 | SRV-BACKUP | Ubuntu 16.04 LTS | Scripts de sauvegarde | Lille |
| 12 | SRV-CDK | Ubuntu 18.04 LTS | Cross-dock saisonnier | Lille |
| 13 | PC-SIEGE-01 | Windows 10 | Poste de travail (siège) | Lille |
| 14 | PC-SIEGE-02 | Windows 10 | Poste de travail (siège) | Lille |
| 15 | PC-COMPTA-01 | Windows 10 | Poste comptabilité | Lille |
| 16 | PC-QUAI-WH1 | Windows 7 | Terminal quai | Lens |
| 17 | PC-QUAI-WH2 | Windows 7 | Terminal quai | Valenciennes |
| 18 | PC-QUAI-WH3 | Windows 7 | Terminal quai | Arras |
| 19 | PC-QUAI-BACKUP | Windows 10 | Poste de remplacement | Lille |

### 3.1 Répartition par système d'exploitation

| Famille OS | Version | Nombre de machines |
|---|---|---|
| Windows Server | 2022 | 1 |
| Windows Server | 2019 | 1 |
| Windows Server | 2016 | 1 |
| Windows Server | 2012 R2 | 1 |
| Windows Server | 2008 R2 | 1 |
| Windows 10 | -- | 4 |
| Windows 7 | -- | 3 |
| Ubuntu LTS | 20.04 | 2 |
| Ubuntu LTS | 18.04 | 1 |
| Ubuntu LTS | 16.04 | 1 |
| Debian | 11 | 1 |
| Debian | 10 | 1 |
| CentOS | 7 | 1 |
| **Total** | | **19** |

### 3.2 Répartition par catégorie

| Catégorie | Nombre |
|---|---|
| Serveurs (infrastructure) | 8 |
| Serveurs (applicatif) | 4 |
| Postes de travail | 7 |
| **Total** | **19** |

---

## 4. Analyse d'obsolescence par machine

Le tableau ci-dessous présente le statut EOL de chaque machine du parc, à la date du 27 mars 2026.

| Hostname | OS | Fin de support standard | Fin de support étendu | Statut | Criticité |
|---|---|---|---|---|---|
| SRV-PRINT | Windows Server 2008 R2 | 14/01/2020 | 10/01/2023 | **Support expiré depuis 3 ans** | **CRITICAL** |
| PC-QUAI-WH1 | Windows 7 | 14/01/2020 | 10/01/2023 | **Support expiré depuis 3 ans** | **CRITICAL** |
| PC-QUAI-WH2 | Windows 7 | 14/01/2020 | 10/01/2023 | **Support expiré depuis 3 ans** | **CRITICAL** |
| PC-QUAI-WH3 | Windows 7 | 14/01/2020 | 10/01/2023 | **Support expiré depuis 3 ans** | **CRITICAL** |
| NAS-01 | Debian 10 | 30/06/2024 | N/A | **Support expiré depuis 21 mois** | **CRITICAL** |
| IPBX-VM | CentOS 7 | 30/06/2024 | N/A | **Support expiré depuis 21 mois** | **CRITICAL** |
| SRV-BACKUP | Ubuntu 16.04 LTS | 01/04/2021 | 01/04/2026 | **Support étendu expiré dans 5 jours** | **CRITICAL** |
| SRV-FILE | Windows Server 2012 R2 | 10/10/2023 | 13/10/2026 | Support étendu restant : ~7 mois | WARNING |
| WMS-DB | Ubuntu 20.04 LTS | 02/04/2025 | 02/04/2030 | Support standard expiré, support étendu actif | WARNING |
| WMS-APP | Ubuntu 20.04 LTS | 02/04/2025 | 02/04/2030 | Support standard expiré, support étendu actif | WARNING |
| SRV-CDK | Ubuntu 18.04 LTS | 01/04/2023 | 01/04/2028 | Support étendu restant : ~2 ans | WARNING |
| PC-SIEGE-01 | Windows 10 | 14/10/2025 | 14/10/2028 | Fin de support standard dans ~7 mois | WARNING |
| PC-SIEGE-02 | Windows 10 | 14/10/2025 | 14/10/2028 | Fin de support standard dans ~7 mois | WARNING |
| PC-COMPTA-01 | Windows 10 | 14/10/2025 | 14/10/2028 | Fin de support standard dans ~7 mois | WARNING |
| PC-QUAI-BACKUP | Windows 10 | 14/10/2025 | 14/10/2028 | Fin de support standard dans ~7 mois | WARNING |
| SRV-INTRANET | Debian 11 | 01/06/2026 | N/A | Support restant : ~2 mois | WARNING |
| DC01 | Windows Server 2022 | 14/10/2031 | 14/10/2031 | Support actif | OK |
| DC02 | Windows Server 2019 | 09/01/2029 | 09/01/2029 | Support actif | OK |
| SUPER-01 | Windows Server 2016 | 12/01/2027 | 12/01/2027 | Support restant : ~10 mois | OK |

---

## 5. Synthèse par criticité

### 5.1 Vue d'ensemble

| Criticité | Nombre de machines | Pourcentage |
|---|---|---|
| **CRITICAL** | 7 | 36,8 % |
| **WARNING** | 9 | 47,4 % |
| **OK** | 3 | 15,8 % |
| **Total** | **19** | **100 %** |

**Constat majeur** : Seules 3 machines sur 19 (15,8 %) disposent d'un support actif sans échéance proche. Plus d'un tiers du parc (36,8 %) fonctionne avec des systèmes dont le support est déjà terminé.

### 5.2 Détail CRITICAL -- 7 machines

Ces machines ne reçoivent plus aucun correctif de sécurité. Elles représentent un risque immédiat pour l'entreprise.

| Machine | OS | Fin de support effective | Délai dépassé | Risque métier |
|---|---|---|---|---|
| SRV-PRINT | Win Server 2008 R2 | 10/01/2023 | +3 ans 2 mois | Moyen -- serveur d'impression, pas de données sensibles |
| PC-QUAI-WH1 | Windows 7 | 10/01/2023 | +3 ans 2 mois | Élevé -- terminal opérationnel entrepôt Lens |
| PC-QUAI-WH2 | Windows 7 | 10/01/2023 | +3 ans 2 mois | Élevé -- terminal opérationnel entrepôt Valenciennes |
| PC-QUAI-WH3 | Windows 7 | 10/01/2023 | +3 ans 2 mois | Élevé -- terminal opérationnel entrepôt Arras |
| NAS-01 | Debian 10 | 30/06/2024 | +21 mois | Élevé -- stockage des sauvegardes |
| IPBX-VM | CentOS 7 | 30/06/2024 | +21 mois | Élevé -- téléphonie d'entreprise |
| SRV-BACKUP | Ubuntu 16.04 LTS | 01/04/2026 | ~5 jours | Critique -- scripts de sauvegarde |

**Points d'attention** :

- Les 3 terminaux de quai sous Windows 7 sont exposés directement dans les entrepôts, avec un risque de compromission via le réseau local.
- Le NAS de sauvegarde sous Debian 10 met en danger la stratégie de sauvegarde de l'entreprise.
- Le serveur IPBX sous CentOS 7 (distribution abandonnée par Red Hat) n'a plus de chemin de mise à jour direct.
- SRV-BACKUP expire dans 5 jours -- une migration imminente est impérativement requise.

### 5.3 Détail WARNING -- 9 machines

Ces machines approchent de leur fin de support. Une planification de migration est nécessaire.

| Machine | OS | Échéance critique | Délai restant |
|---|---|---|---|
| SRV-INTRANET | Debian 11 | 01/06/2026 | ~2 mois |
| WMS-DB | Ubuntu 20.04 LTS | 02/04/2025 (std) / 02/04/2030 (ext) | Support standard expiré, étendu actif |
| WMS-APP | Ubuntu 20.04 LTS | 02/04/2025 (std) / 02/04/2030 (ext) | Support standard expiré, étendu actif |
| SRV-FILE | Win Server 2012 R2 | 13/10/2026 (ESU) | ~7 mois |
| PC-SIEGE-01 | Windows 10 | 14/10/2025 (std) / 14/10/2028 (ESU) | ~7 mois (std) |
| PC-SIEGE-02 | Windows 10 | 14/10/2025 (std) / 14/10/2028 (ESU) | ~7 mois (std) |
| PC-COMPTA-01 | Windows 10 | 14/10/2025 (std) / 14/10/2028 (ESU) | ~7 mois (std) |
| PC-QUAI-BACKUP | Windows 10 | 14/10/2025 (std) / 14/10/2028 (ESU) | ~7 mois (std) |
| SRV-CDK | Ubuntu 18.04 LTS | 01/04/2028 (ext) | ~2 ans |

### 5.4 Détail OK -- 3 machines

| Machine | OS | Fin de support | Délai restant |
|---|---|---|---|
| DC01 | Windows Server 2022 | 14/10/2031 | +5 ans |
| DC02 | Windows Server 2019 | 09/01/2029 | ~3 ans |
| SUPER-01 | Windows Server 2016 | 12/01/2027 | ~10 mois |

**Note** : SUPER-01 (Windows Server 2016) dispose d'un support jusqu'en janvier 2027. Bien que classé OK, cette machine devra être planifiée pour migration dans les 12 prochains mois.

---

## 6. Recommandations de migration

Les recommandations sont classées par ordre de priorité décroissante.

### 6.1 Priorité 1 -- Urgences immédiates (avril 2026)

#### SRV-BACKUP (Ubuntu 16.04 LTS)
- **Raison** : Support étendu expiré le 01/04/2026 (dans 5 jours)
- **Recommandation** : Migration vers Ubuntu 24.04 LTS (support jusqu'en 2034)
- **Action** : Migrer les scripts de sauvegarde, tester la compatibilité, valider les planifications cron
- **Complexité** : Moyenne -- revalidation des scripts nécessaire

#### PC-QUAI-WH1 / WH2 / WH3 (Windows 7)
- **Raison** : Support terminé depuis janvier 2023, postes exposés dans les entrepôts
- **Recommandation** : Remplacement du matériel + déploiement Windows 11 ou Windows 10 (avec support étendu)
- **Alternative** : Si le matériel ne supporte pas Windows 11, envisager un client léger Linux
- **Complexité** : Faible -- postes standardisés

#### IPBX-VM (CentOS 7)
- **Raison** : CentOS 7 abandonné depuis juin 2024, pas de CentOS 8+
- **Recommandation** : Migration vers une distribution supportée (Rocky Linux 9 ou Debian 12) avec reconfiguration de la téléphonie IP
- **Alternative** : Évaluation d'une solution de téléphonie cloud (SaaS)
- **Complexité** : Élevée -- service critique, nécessite une phase de test préalable

### 6.2 Priorité 2 -- Court terme (Q2-Q3 2026)

#### NAS-01 (Debian 10)
- **Raison** : Support terminé depuis juin 2024
- **Recommandation** : Migration vers Debian 12 (support jusqu'en 2028)
- **Complexité** : Moyenne -- migration des données et validation de l'intégrité des sauvegardes

#### SRV-PRINT (Windows Server 2008 R2)
- **Raison** : Support terminé depuis janvier 2023
- **Recommandation** : Migration vers Windows Server 2022 ou consolidation des services d'impression sur un serveur existant
- **Alternative** : Déploiement d'une impression directe (sans serveur dédié) si le volume le permet
- **Complexité** : Faible à moyenne

#### SRV-INTRANET (Debian 11)
- **Raison** : Fin de support prévue pour juin 2026
- **Recommandation** : Migration vers Debian 12 (support jusqu'en 2028)
- **Complexité** : Faible -- migration standard avec mise à jour des paquets

#### SRV-FILE (Windows Server 2012 R2)
- **Raison** : Support étendu (ESU) expiré en octobre 2026
- **Recommandation** : Migration vers Windows Server 2022. Profiter de la migration pour restructurer les partages et les permissions
- **Complexité** : Moyenne -- données volumineuses, droits NTFS à reconfigurer

### 6.3 Priorité 3 -- Moyen terme (Q4 2026 - Q2 2027)

#### PC-SIEGE-01 / PC-SIEGE-02 / PC-COMPTA-01 / PC-QUAI-BACKUP (Windows 10)
- **Raison** : Fin du support standard en octobre 2025 (support étendu payant disponible jusqu'en 2028)
- **Recommandation** : Planifier la migration vers Windows 11. Vérifier la compatibilité matérielle (TPM 2.0, Secure Boot)
- **Option** : Souscrire au programme ESU Microsoft si le matériel n'est pas compatible Windows 11
- **Complexité** : Faible -- migration standard des postes de travail

#### WMS-DB / WMS-APP (Ubuntu 20.04 LTS)
- **Raison** : Support standard expiré en avril 2025, support étendu (Ubuntu Pro) actif jusqu'en 2030
- **Recommandation** : Planifier la migration vers Ubuntu 24.04 LTS lors de la prochaine fenêtre de maintenance applicative
- **Attention** : Vérifier la compatibilité de la version MySQL et de l'application WMS avant migration
- **Complexité** : Élevée -- environnement applicatif critique (WMS)

### 6.4 Priorité 4 -- Long terme (2027-2028)

#### SUPER-01 (Windows Server 2016)
- **Raison** : Fin de support en janvier 2027
- **Recommandation** : Migration vers Windows Server 2022 ou migration de Zabbix vers un serveur Linux (Ubuntu 24.04 LTS)
- **Complexité** : Moyenne

#### SRV-CDK (Ubuntu 18.04 LTS)
- **Raison** : Support étendu jusqu'en avril 2028
- **Recommandation** : Migration vers Ubuntu 24.04 LTS avant échéance
- **Complexité** : Faible -- serveur saisonnier

---

## 7. Plan d'action recommandé

### Phase 1 -- Actions imminentes (avril 2026)

| Semaine | Action | Machine(s) | Responsable suggéré |
|---|---|---|---|
| S14 | Migration SRV-BACKUP vers Ubuntu 24.04 LTS | SRV-BACKUP | Admin système |
| S14-S15 | Remplacement/réinstallation des postes de quai | PC-QUAI-WH1, WH2, WH3 | Support IT + Logistique |
| S15-S16 | PoC migration téléphonie (environnement de test) | IPBX-VM | Admin système |

### Phase 2 -- Consolidation (mai - septembre 2026)

| Mois | Action | Machine(s) |
|---|---|---|
| Mai | Migration NAS-01 vers Debian 12 | NAS-01 |
| Mai | Migration SRV-INTRANET vers Debian 12 | SRV-INTRANET |
| Juin | Migration SRV-PRINT vers Windows Server 2022 ou décommissionnement | SRV-PRINT |
| Juillet-Août | Migration SRV-FILE vers Windows Server 2022 (profiter de la période estivale) | SRV-FILE |
| Septembre | Migration IPBX vers Rocky Linux 9 / Debian 12 (ou solution cloud) | IPBX-VM |

### Phase 3 -- Postes de travail et applicatif (Q4 2026 - Q2 2027)

| Période | Action | Machine(s) |
|---|---|---|
| Oct-Nov 2026 | Migration des postes Windows 10 vers Windows 11 | PC-SIEGE-01/02, PC-COMPTA-01, PC-QUAI-BACKUP |
| Q1 2027 | Migration WMS (base de données + applicatif) vers Ubuntu 24.04 LTS | WMS-DB, WMS-APP |
| Q1 2027 | Migration SUPER-01 vers Windows Server 2022 | SUPER-01 |

### Phase 4 -- Finalisation (2027-2028)

| Période | Action | Machine(s) |
|---|---|---|
| 2027 | Migration SRV-CDK vers Ubuntu 24.04 LTS | SRV-CDK |
| 2028 | Audit de suivi -- vérification de la conformité du parc | Toutes |

### Estimation budgétaire indicative

| Poste de dépense | Estimation |
|---|---|
| Licences Windows Server 2022 (2-3 licences) | Variable selon contrat Microsoft |
| Remplacement matériel postes de quai (3 postes) | 1 500 - 3 000 EUR |
| Licences Windows 11 Pro (si nécessaire) | ~150 EUR/poste |
| Support étendu Ubuntu Pro (WMS-DB, WMS-APP) | Gratuit jusqu'à 5 machines |
| ESU Windows 10 (option temporaire) | ~61 EUR/poste/an (1ère année) |
| Jours d'intervention admin système | À évaluer selon ressources internes |

*Note : Ces estimations sont indicatives et devront être affinées avec les tarifs en vigueur au moment de la commande.*

---

## 8. Conclusion

L'audit du parc informatique de NordTransit Logistics révèle une situation préoccupante : **84,2 % des machines** (16 sur 19) nécessitent une attention immédiate ou planifiée en matière de fin de support.

Les constats majeurs sont :

1. **7 machines en situation critique** dont 6 sans aucun support depuis plus de 21 mois, et 1 (SRV-BACKUP) dont le support étendu expire dans les jours qui viennent. Ces systèmes sont vulnérables aux failles de sécurité non corrigées.

2. **Les entrepôts sont les plus exposés** : les 3 terminaux de quai sous Windows 7 fonctionnent sans correctifs de sécurité depuis plus de 3 ans, dans un environnement opérationnel où la continuité d'activité est essentielle.

3. **La chaîne de sauvegarde est fragilisée** : le NAS (Debian 10) et le serveur de scripts de sauvegarde (Ubuntu 16.04) sont tous deux en fin de vie, mettant en risque la capacité de restauration en cas d'incident.

4. **La téléphonie repose sur un système abandonné** : CentOS 7 n'a plus de successeur direct, ce qui nécessite une migration vers une distribution alternative.

Le plan d'action proposé s'étale sur 2 ans et priorise les migrations selon le risque métier. Les actions les plus urgentes (Phase 1) doivent être lancées dès avril 2026 pour sécuriser les systèmes les plus critiques.

L'outil NTL-SysToolbox, et notamment son module d'audit, permettra à NTL de suivre l'évolution de la conformité du parc dans le temps grâce à des audits réguliers et automatisés.

---

*Rapport généré avec l'assistance du module audit de NTL-SysToolbox.*
*MSPR TPRE511 -- Mars 2026*
