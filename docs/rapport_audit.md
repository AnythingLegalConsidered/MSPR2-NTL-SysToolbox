# Rapport d'Audit d'Obsolescence du Parc Informatique

---

**Client** : NordTransit Logistics (NTL)
**Prestataire** : Equipe MSPR TPRE511
**Date de l'audit** : Mars 2026
**Version du document** : 1.0
**Classification** : Confidentiel -- Usage interne NTL

---

## Sommaire

1. [Contexte et objectifs de l'audit](#1-contexte-et-objectifs-de-laudit)
2. [Methodologie](#2-methodologie)
3. [Inventaire du parc informatique](#3-inventaire-du-parc-informatique)
4. [Analyse d'obsolescence par machine](#4-analyse-dobsolescence-par-machine)
5. [Synthese par criticite](#5-synthese-par-criticite)
6. [Recommandations de migration](#6-recommandations-de-migration)
7. [Plan d'action recommande](#7-plan-daction-recommande)
8. [Conclusion](#8-conclusion)

---

## 1. Contexte et objectifs de l'audit

### 1.1 Presentation de l'entreprise

NordTransit Logistics (NTL) est une PME specialisee dans la logistique, implantee dans les Hauts-de-France. L'entreprise dispose de :

- **Siege social** : Lille
- **Entrepots** : Lens, Valenciennes, Arras
- **Parc informatique** : 19 machines (serveurs et postes de travail)

L'infrastructure informatique de NTL supporte des fonctions critiques : gestion des entrepots (WMS), telephonie (IPBX), controleurs de domaine Active Directory, serveurs de fichiers, supervision, et postes de travail operationnels sur les quais logistiques.

### 1.2 Objectifs de l'audit

L'audit repond a un besoin exprime par la direction de NTL :

1. **Qualifier l'obsolescence** de chaque machine du parc informatique
2. **Evaluer les risques** lies aux systemes en fin de vie (securite, conformite, continuite d'activite)
3. **Prioriser les migrations** en fonction de la criticite metier et du niveau d'obsolescence
4. **Fournir un plan d'action** realiste pour planifier les mises a niveau

### 1.3 Perimetre

L'audit couvre l'ensemble des 19 machines repertoriees dans l'inventaire NTL, incluant :

- 11 serveurs (physiques et virtuels)
- 1 NAS de sauvegarde
- 7 postes de travail (siege et entrepots)

---

## 2. Methodologie

### 2.1 Outil utilise : NTL-SysToolbox -- Module Audit

L'audit a ete realise a l'aide du module **audit** de la toolbox NTL-SysToolbox, un outil developpe specifiquement pour ce projet. Le module est implemente en Python et se compose de quatre fonctions principales :

| Fonction | Description |
|---|---|
| `scan_network()` | Scan reseau via nmap avec detection d'OS et categorisation des services |
| `list_os_eol()` | Lecture de la base de donnees EOL (End of Life) contenant 18 entrees d'OS |
| `audit_from_csv()` | Croisement de l'inventaire CSV avec les dates de fin de support |
| `generate_report()` | Generation d'un rapport complet au format JSON, trie par criticite |

### 2.2 Base de donnees EOL

La base de donnees de reference (`data/eol_database.json`) contient les dates de fin de support officiel et etendu pour 18 systemes d'exploitation :

- **Microsoft** : Windows Server 2022/2019/2016/2012 R2/2012/2008 R2, Windows 11/10/7
- **Canonical** : Ubuntu 24.04/22.04/20.04/18.04/16.04 LTS
- **Debian** : Debian 12/11/10
- **Red Hat** : CentOS 7

Les dates proviennent des annonces officielles des editeurs. Les dates de support etendu (ESU pour Microsoft, Ubuntu Pro pour Canonical) sont prises en compte lorsqu'elles existent.

### 2.3 Approche d'analyse

L'analyse de chaque machine suit le processus suivant :

1. **Identification** : lecture de l'inventaire CSV (hostname, OS, version, role)
2. **Croisement EOL** : comparaison de l'OS installe avec la base de donnees de fin de support
3. **Classification** : attribution d'un niveau de criticite selon la grille suivante :

| Niveau | Critere | Signification |
|---|---|---|
| **CRITICAL** | Date EOL (y compris support etendu) depassee | Plus aucun correctif de securite disponible. Risque immediat. |
| **WARNING** | Fin de support dans moins de 2 ans (avant mars 2028) | Migration a planifier a court ou moyen terme. |
| **OK** | Support actif au-dela de mars 2028 | Aucune action immediate requise. |

### 2.4 Date de reference

Toutes les analyses de ce rapport sont calculees a la date du **27 mars 2026**.

---

## 3. Inventaire du parc informatique

Le parc informatique de NTL se compose de 19 machines reparties comme suit :

| # | Hostname | Systeme d'exploitation | Role / Fonction | Site |
|---|---|---|---|---|
| 1 | DC01 | Windows Server 2022 | Controleur de domaine principal (AD/DNS) | Lille |
| 2 | DC02 | Windows Server 2019 | Controleur de domaine secondaire | Lille |
| 3 | WMS-DB | Ubuntu 20.04 LTS | Base de donnees MySQL (WMS) | Lille |
| 4 | WMS-APP | Ubuntu 20.04 LTS | Serveur applicatif (WMS) | Lille |
| 5 | IPBX-VM | CentOS 7 | Serveur IPBX telephonie | Lille |
| 6 | SUPER-01 | Windows Server 2016 | Supervision Zabbix | Lille |
| 7 | SRV-FILE | Windows Server 2012 R2 | Serveur de fichiers (partages legacy) | Lille |
| 8 | SRV-PRINT | Windows Server 2008 R2 | Serveur d'impression | Lille |
| 9 | NAS-01 | Debian 10 | NAS de sauvegarde | Lille |
| 10 | SRV-INTRANET | Debian 11 | Intranet / Wiki interne | Lille |
| 11 | SRV-BACKUP | Ubuntu 16.04 LTS | Scripts de sauvegarde | Lille |
| 12 | SRV-CDK | Ubuntu 18.04 LTS | Cross-dock saisonnier | Lille |
| 13 | PC-SIEGE-01 | Windows 10 | Poste de travail (siege) | Lille |
| 14 | PC-SIEGE-02 | Windows 10 | Poste de travail (siege) | Lille |
| 15 | PC-COMPTA-01 | Windows 10 | Poste comptabilite | Lille |
| 16 | PC-QUAI-WH1 | Windows 7 | Terminal quai | Lens |
| 17 | PC-QUAI-WH2 | Windows 7 | Terminal quai | Valenciennes |
| 18 | PC-QUAI-WH3 | Windows 7 | Terminal quai | Arras |
| 19 | PC-QUAI-BACKUP | Windows 10 | Poste de remplacement | Lille |

### 3.1 Repartition par systeme d'exploitation

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

### 3.2 Repartition par categorie

| Categorie | Nombre |
|---|---|
| Serveurs (infrastructure) | 8 |
| Serveurs (applicatif) | 4 |
| Postes de travail | 7 |
| **Total** | **19** |

---

## 4. Analyse d'obsolescence par machine

Le tableau ci-dessous presente le statut EOL de chaque machine du parc, a la date du 27 mars 2026.

| Hostname | OS | Fin de support standard | Fin de support etendu | Statut | Criticite |
|---|---|---|---|---|---|
| SRV-PRINT | Windows Server 2008 R2 | 14/01/2020 | 10/01/2023 | **Support expire depuis 3 ans** | **CRITICAL** |
| PC-QUAI-WH1 | Windows 7 | 14/01/2020 | 10/01/2023 | **Support expire depuis 3 ans** | **CRITICAL** |
| PC-QUAI-WH2 | Windows 7 | 14/01/2020 | 10/01/2023 | **Support expire depuis 3 ans** | **CRITICAL** |
| PC-QUAI-WH3 | Windows 7 | 14/01/2020 | 10/01/2023 | **Support expire depuis 3 ans** | **CRITICAL** |
| NAS-01 | Debian 10 | 30/06/2024 | N/A | **Support expire depuis 21 mois** | **CRITICAL** |
| IPBX-VM | CentOS 7 | 30/06/2024 | N/A | **Support expire depuis 21 mois** | **CRITICAL** |
| SRV-BACKUP | Ubuntu 16.04 LTS | 01/04/2021 | 01/04/2026 | **Support etendu expire dans 5 jours** | **CRITICAL** |
| SRV-FILE | Windows Server 2012 R2 | 10/10/2023 | 13/10/2026 | Support etendu restant : ~7 mois | WARNING |
| WMS-DB | Ubuntu 20.04 LTS | 02/04/2025 | 02/04/2030 | Support standard expire, support etendu actif | WARNING |
| WMS-APP | Ubuntu 20.04 LTS | 02/04/2025 | 02/04/2030 | Support standard expire, support etendu actif | WARNING |
| SRV-CDK | Ubuntu 18.04 LTS | 01/04/2023 | 01/04/2028 | Support etendu restant : ~2 ans | WARNING |
| PC-SIEGE-01 | Windows 10 | 14/10/2025 | 14/10/2028 | Fin de support standard dans ~7 mois | WARNING |
| PC-SIEGE-02 | Windows 10 | 14/10/2025 | 14/10/2028 | Fin de support standard dans ~7 mois | WARNING |
| PC-COMPTA-01 | Windows 10 | 14/10/2025 | 14/10/2028 | Fin de support standard dans ~7 mois | WARNING |
| PC-QUAI-BACKUP | Windows 10 | 14/10/2025 | 14/10/2028 | Fin de support standard dans ~7 mois | WARNING |
| SRV-INTRANET | Debian 11 | 01/06/2026 | N/A | Support restant : ~2 mois | WARNING |
| DC01 | Windows Server 2022 | 14/10/2031 | 14/10/2031 | Support actif | OK |
| DC02 | Windows Server 2019 | 09/01/2029 | 09/01/2029 | Support actif | OK |
| SUPER-01 | Windows Server 2016 | 12/01/2027 | 12/01/2027 | Support restant : ~10 mois | OK |

---

## 5. Synthese par criticite

### 5.1 Vue d'ensemble

| Criticite | Nombre de machines | Pourcentage |
|---|---|---|
| **CRITICAL** | 7 | 36,8 % |
| **WARNING** | 9 | 47,4 % |
| **OK** | 3 | 15,8 % |
| **Total** | **19** | **100 %** |

**Constat majeur** : Seules 3 machines sur 19 (15,8 %) disposent d'un support actif sans echeance proche. Plus d'un tiers du parc (36,8 %) fonctionne avec des systemes dont le support est deja termine.

### 5.2 Detail CRITICAL -- 7 machines

Ces machines ne recoivent plus aucun correctif de securite. Elles representent un risque immediat pour l'entreprise.

| Machine | OS | Fin de support effective | Delai depasse | Risque metier |
|---|---|---|---|---|
| SRV-PRINT | Win Server 2008 R2 | 10/01/2023 | +3 ans 2 mois | Moyen -- serveur d'impression, pas de donnees sensibles |
| PC-QUAI-WH1 | Windows 7 | 10/01/2023 | +3 ans 2 mois | Eleve -- terminal operationnel entrepot Lens |
| PC-QUAI-WH2 | Windows 7 | 10/01/2023 | +3 ans 2 mois | Eleve -- terminal operationnel entrepot Valenciennes |
| PC-QUAI-WH3 | Windows 7 | 10/01/2023 | +3 ans 2 mois | Eleve -- terminal operationnel entrepot Arras |
| NAS-01 | Debian 10 | 30/06/2024 | +21 mois | Eleve -- stockage des sauvegardes |
| IPBX-VM | CentOS 7 | 30/06/2024 | +21 mois | Eleve -- telephonie d'entreprise |
| SRV-BACKUP | Ubuntu 16.04 LTS | 01/04/2026 | ~5 jours | Critique -- scripts de sauvegarde |

**Points d'attention** :

- Les 3 terminaux de quai sous Windows 7 sont exposes directement dans les entrepots, avec un risque de compromission via le reseau local.
- Le NAS de sauvegarde sous Debian 10 met en danger la strategie de sauvegarde de l'entreprise.
- Le serveur IPBX sous CentOS 7 (distribution abandonnee par Red Hat) n'a plus de chemin de mise a jour direct.
- SRV-BACKUP expire dans 5 jours -- une migration imminente est imperativement requise.

### 5.3 Detail WARNING -- 9 machines

Ces machines approchent de leur fin de support. Une planification de migration est necessaire.

| Machine | OS | Echeance critique | Delai restant |
|---|---|---|---|
| SRV-INTRANET | Debian 11 | 01/06/2026 | ~2 mois |
| WMS-DB | Ubuntu 20.04 LTS | 02/04/2025 (std) / 02/04/2030 (ext) | Support standard expire, etendu actif |
| WMS-APP | Ubuntu 20.04 LTS | 02/04/2025 (std) / 02/04/2030 (ext) | Support standard expire, etendu actif |
| SRV-FILE | Win Server 2012 R2 | 13/10/2026 (ESU) | ~7 mois |
| PC-SIEGE-01 | Windows 10 | 14/10/2025 (std) / 14/10/2028 (ESU) | ~7 mois (std) |
| PC-SIEGE-02 | Windows 10 | 14/10/2025 (std) / 14/10/2028 (ESU) | ~7 mois (std) |
| PC-COMPTA-01 | Windows 10 | 14/10/2025 (std) / 14/10/2028 (ESU) | ~7 mois (std) |
| PC-QUAI-BACKUP | Windows 10 | 14/10/2025 (std) / 14/10/2028 (ESU) | ~7 mois (std) |
| SRV-CDK | Ubuntu 18.04 LTS | 01/04/2028 (ext) | ~2 ans |

### 5.4 Detail OK -- 3 machines

| Machine | OS | Fin de support | Delai restant |
|---|---|---|---|
| DC01 | Windows Server 2022 | 14/10/2031 | +5 ans |
| DC02 | Windows Server 2019 | 09/01/2029 | ~3 ans |
| SUPER-01 | Windows Server 2016 | 12/01/2027 | ~10 mois |

**Note** : SUPER-01 (Windows Server 2016) dispose d'un support jusqu'en janvier 2027. Bien que classe OK, cette machine devra etre planifiee pour migration dans les 12 prochains mois.

---

## 6. Recommandations de migration

Les recommandations sont classees par ordre de priorite decroissante.

### 6.1 Priorite 1 -- Urgences immediates (avril 2026)

#### SRV-BACKUP (Ubuntu 16.04 LTS)
- **Raison** : Support etendu expire le 01/04/2026 (dans 5 jours)
- **Recommandation** : Migration vers Ubuntu 24.04 LTS (support jusqu'en 2034)
- **Action** : Migrer les scripts de sauvegarde, tester la compatibilite, valider les planifications cron
- **Complexite** : Moyenne -- revalidation des scripts necessaire

#### PC-QUAI-WH1 / WH2 / WH3 (Windows 7)
- **Raison** : Support termine depuis janvier 2023, postes exposes dans les entrepots
- **Recommandation** : Remplacement du materiel + deploiement Windows 11 ou Windows 10 (avec support etendu)
- **Alternative** : Si le materiel ne supporte pas Windows 11, envisager un client leger Linux
- **Complexite** : Faible -- postes standardises

#### IPBX-VM (CentOS 7)
- **Raison** : CentOS 7 abandonne depuis juin 2024, pas de CentOS 8+
- **Recommandation** : Migration vers une distribution supportee (Rocky Linux 9 ou Debian 12) avec reconfiguration de la telephonie IP
- **Alternative** : Evaluation d'une solution de telephonie cloud (SaaS)
- **Complexite** : Elevee -- service critique, necessite une phase de test prealable

### 6.2 Priorite 2 -- Court terme (Q2-Q3 2026)

#### NAS-01 (Debian 10)
- **Raison** : Support termine depuis juin 2024
- **Recommandation** : Migration vers Debian 12 (support jusqu'en 2028)
- **Complexite** : Moyenne -- migration des donnees et validation de l'integrite des sauvegardes

#### SRV-PRINT (Windows Server 2008 R2)
- **Raison** : Support termine depuis janvier 2023
- **Recommandation** : Migration vers Windows Server 2022 ou consolidation des services d'impression sur un serveur existant
- **Alternative** : Deploiement d'une impression directe (sans serveur dedie) si le volume le permet
- **Complexite** : Faible a moyenne

#### SRV-INTRANET (Debian 11)
- **Raison** : Fin de support prevue pour juin 2026
- **Recommandation** : Migration vers Debian 12 (support jusqu'en 2028)
- **Complexite** : Faible -- migration standard avec mise a jour des paquets

#### SRV-FILE (Windows Server 2012 R2)
- **Raison** : Support etendu (ESU) expire en octobre 2026
- **Recommandation** : Migration vers Windows Server 2022. Profiter de la migration pour restructurer les partages et les permissions
- **Complexite** : Moyenne -- donnees volumineuses, droits NTFS a reconfigurer

### 6.3 Priorite 3 -- Moyen terme (Q4 2026 - Q2 2027)

#### PC-SIEGE-01 / PC-SIEGE-02 / PC-COMPTA-01 / PC-QUAI-BACKUP (Windows 10)
- **Raison** : Fin du support standard en octobre 2025 (support etendu payant disponible jusqu'en 2028)
- **Recommandation** : Planifier la migration vers Windows 11. Verifier la compatibilite materielle (TPM 2.0, Secure Boot)
- **Option** : Souscrire au programme ESU Microsoft si le materiel n'est pas compatible Windows 11
- **Complexite** : Faible -- migration standard des postes de travail

#### WMS-DB / WMS-APP (Ubuntu 20.04 LTS)
- **Raison** : Support standard expire en avril 2025, support etendu (Ubuntu Pro) actif jusqu'en 2030
- **Recommandation** : Planifier la migration vers Ubuntu 24.04 LTS lors de la prochaine fenetre de maintenance applicative
- **Attention** : Verifier la compatibilite de la version MySQL et de l'application WMS avant migration
- **Complexite** : Elevee -- environnement applicatif critique (WMS)

### 6.4 Priorite 4 -- Long terme (2027-2028)

#### SUPER-01 (Windows Server 2016)
- **Raison** : Fin de support en janvier 2027
- **Recommandation** : Migration vers Windows Server 2022 ou migration de Zabbix vers un serveur Linux (Ubuntu 24.04 LTS)
- **Complexite** : Moyenne

#### SRV-CDK (Ubuntu 18.04 LTS)
- **Raison** : Support etendu jusqu'en avril 2028
- **Recommandation** : Migration vers Ubuntu 24.04 LTS avant echeance
- **Complexite** : Faible -- serveur saisonnier

---

## 7. Plan d'action recommande

### Phase 1 -- Actions imminentes (avril 2026)

| Semaine | Action | Machine(s) | Responsable sugere |
|---|---|---|---|
| S14 | Migration SRV-BACKUP vers Ubuntu 24.04 LTS | SRV-BACKUP | Admin systeme |
| S14-S15 | Remplacement/reinstallation des postes de quai | PC-QUAI-WH1, WH2, WH3 | Support IT + Logistique |
| S15-S16 | PoC migration telephonie (environnement de test) | IPBX-VM | Admin systeme |

### Phase 2 -- Consolidation (mai - septembre 2026)

| Mois | Action | Machine(s) |
|---|---|---|
| Mai | Migration NAS-01 vers Debian 12 | NAS-01 |
| Mai | Migration SRV-INTRANET vers Debian 12 | SRV-INTRANET |
| Juin | Migration SRV-PRINT vers Windows Server 2022 ou decommissionnement | SRV-PRINT |
| Juillet-Aout | Migration SRV-FILE vers Windows Server 2022 (profiter de la periode estivale) | SRV-FILE |
| Septembre | Migration IPBX vers Rocky Linux 9 / Debian 12 (ou solution cloud) | IPBX-VM |

### Phase 3 -- Postes de travail et applicatif (Q4 2026 - Q2 2027)

| Periode | Action | Machine(s) |
|---|---|---|
| Oct-Nov 2026 | Migration des postes Windows 10 vers Windows 11 | PC-SIEGE-01/02, PC-COMPTA-01, PC-QUAI-BACKUP |
| Q1 2027 | Migration WMS (base de donnees + applicatif) vers Ubuntu 24.04 LTS | WMS-DB, WMS-APP |
| Q1 2027 | Migration SUPER-01 vers Windows Server 2022 | SUPER-01 |

### Phase 4 -- Finalisation (2027-2028)

| Periode | Action | Machine(s) |
|---|---|---|
| 2027 | Migration SRV-CDK vers Ubuntu 24.04 LTS | SRV-CDK |
| 2028 | Audit de suivi -- verification de la conformite du parc | Toutes |

### Estimation budgetaire indicative

| Poste de depense | Estimation |
|---|---|
| Licences Windows Server 2022 (2-3 licences) | Variable selon contrat Microsoft |
| Remplacement materiel postes de quai (3 postes) | 1 500 - 3 000 EUR |
| Licences Windows 11 Pro (si necessaire) | ~150 EUR/poste |
| Support etendu Ubuntu Pro (WMS-DB, WMS-APP) | Gratuit jusqu'a 5 machines |
| ESU Windows 10 (option temporaire) | ~61 EUR/poste/an (1ere annee) |
| Jours d'intervention admin systeme | A evaluer selon ressources internes |

*Note : Ces estimations sont indicatives et devront etre affinées avec les tarifs en vigueur au moment de la commande.*

---

## 8. Conclusion

L'audit du parc informatique de NordTransit Logistics revele une situation preoccupante : **84,2 % des machines** (16 sur 19) necessitent une attention immediate ou planifiee en matiere de fin de support.

Les constats majeurs sont :

1. **7 machines en situation critique** dont 6 sans aucun support depuis plus de 21 mois, et 1 (SRV-BACKUP) dont le support etendu expire dans les jours qui viennent. Ces systemes sont vulnerables aux failles de securite non corrigees.

2. **Les entrepots sont les plus exposes** : les 3 terminaux de quai sous Windows 7 fonctionnent sans correctifs de securite depuis plus de 3 ans, dans un environnement operationnel ou la continuite d'activite est essentielle.

3. **La chaine de sauvegarde est fragilisee** : le NAS (Debian 10) et le serveur de scripts de sauvegarde (Ubuntu 16.04) sont tous deux en fin de vie, mettant en risque la capacite de restauration en cas d'incident.

4. **La telephonie repose sur un systeme abandonne** : CentOS 7 n'a plus de successeur direct, ce qui necessite une migration vers une distribution alternative.

Le plan d'action propose s'etale sur 2 ans et priorise les migrations selon le risque metier. Les actions les plus urgentes (Phase 1) doivent etre lancees des avril 2026 pour securiser les systemes les plus critiques.

L'outil NTL-SysToolbox, et notamment son module d'audit, permettra a NTL de suivre l'evolution de la conformite du parc dans le temps grace a des audits reguliers et automatises.

---

*Rapport genere avec l'assistance du module audit de NTL-SysToolbox.*
*MSPR TPRE511 -- Mars 2026*
