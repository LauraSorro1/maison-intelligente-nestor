# Maison intelligente simulée + assistant vocal « Merlin »

Cours **420-315-AH — Développement d'objets intelligents**
Étudiante : **Laura Sorro** — Collège Ahuntsic, session été 2026

---

## Vue d'ensemble

Le dépôt contient deux couches successives d'un même système :

| | Contenu | Apport |
|---|---|---|
| **Projet 1** | Maison connectée simulée : 3 pièces (Salon, Entrée, Garage) + aquarium, 12 capteurs, 9 actionneurs, contrôleur à règles automatiques, tableau de bord Node-RED | Infrastructure MQTT |
| **Projet 2** | Assistant vocal francophone « Merlin » greffé sur cette infrastructure, et persistance MariaDB des lectures et des interactions | Voix + base de données |

Le Projet 2 est documenté en premier, car c'est la couche active. Le Projet 1 suit
comme référence technique de l'infrastructure sous-jacente.

---
---

# PROJET 2 — Assistant vocal « Merlin »

Merlin écoute au micro, reconnaît un mot-clé, analyse l'intention de la phrase,
commande les actionneurs réels via MQTT, répond à voix haute, et journalise chaque
interaction dans MariaDB ainsi que dans un tableau de bord Node-RED.

## 1. Architecture

```mermaid
graph LR
    MIC[🎤 Micro] -->|audio| OR[Oreille<br/>voix.py]
    OR -->|texte brut| INT[intentions.py<br/>normaliser → tokeniser → analyser]
    INT -->|type, cible, action| AS[assistant.py<br/>point de convergence unique]

    AS --> VX[parler<br/>pyttsx3]
    VX --> HP[🔊 Haut-parleur]

    AS -->|inserer| DB[(MariaDB « maison »<br/>journal_commandes<br/>journal_reponses)]

    AS --> MM[maison_mqtt.py]

    MM -->|publish : assistant/journal| M[Mosquitto :1883]
    MM -->|publish : maison/salon/aquarium/pompe/cmd| M
    MM -->|publish : maison/salon/aquarium/uv/cmd| M
    MM -->|publish : maison/entree/serrure/cmd| M
    M -->|subscribe : maison/salon/temperature| MM
    M -->|subscribe : maison/salon/aquarium/temperature| MM

    M -->|subscribe| A3[pompe aquarium]
    M -->|subscribe| A4[UV aquarium]
    M -->|subscribe| A6[serrure entrée]
    M -->|subscribe : assistant/journal| N[Node-RED<br/>widget « Assistant vocal »]

    C4[capteur aquarium<br/>température] -->|publish| M
    C1[capteur salon<br/>température] -->|publish| M
```

> Seuls les capteurs et actionneurs **réellement utilisés par l'assistant** figurent
> sur ce diagramme. L'infrastructure complète est décrite dans la partie Projet 1.

**Note d'architecture — espaces de noms disjoints.** Le journal vocal publie sur
`assistant/journal`, hors de l'arbre `maison/`. Le tableau de bord comporte un nœud
abonné à `maison/#` pour la carte de la maison : si le journal vivait sous `maison/`,
le courtier livrerait chaque interaction **deux fois** au client Node-RED — une fois
par souscription correspondante — et chaque ligne apparaîtrait en double dans le
widget. Séparer les racines garantit à chaque flux un périmètre exclusif.

---

## 2. Grammaire des commandes vocales

### 2.1 Principe de l'analyse

`analyser()` ne fait pas de reconnaissance de phrase complète : elle cherche
**deux éléments indépendants** parmi les jetons, puis les combine.

| Éléments trouvés | Type retourné |
|---|---|
| un verbe d'action **et** un actionneur | `ACTION` |
| un capteur **et aucun** verbe d'action | `REQUETE` |
| tout autre cas | `INCONNUE` |

Conséquence : l'ordre des mots n'a aucune importance, et aucune formule
interrogative n'est nécessaire. « Merlin, le salon » suffit à obtenir la
température du salon ; « Merlin, quelle est la température ? » sans nom de pièce
retourne INCONNUE.

Le mot-clé peut être suivi directement de la commande, ou prononcé seul — Merlin
répond alors « Oui, je vous écoute » et attend la phrase pendant 5 secondes.

### 2.2 Le mot-clé : « Merlin »

| Critère | Justification |
|---|---|
| Prononciation | Mot français natif, correctement synthétisé par pyttsx3 en voix fr-CA |
| Reconnaissance | Bien transcrit par Google Speech fr-FR, contrairement à « Gandalf » (anglicisme mal rendu) |
| Distinction | Deux syllabes nettes, aucun mot proche dans le vocabulaire domotique |
| Robustesse | Les transcriptions erronées (« Bernard », « Berlin », « merlan ») ne contiennent pas le mot-clé : elles sont filtrées sans effet de bord |

### 2.3 Verbes reconnus

Impératif **et** infinitif, pour accepter aussi bien « allume la pompe » que
« peux-tu allumer la pompe » (la formule de politesse est retirée, le verbe reste à
l'infinitif).

| Intention | Verbes |
|---|---|
| **ON** | allume, allumer, active, activer, demarre, demarrer, verrouille, verrouiller, barre, barrer |
| **OFF** | eteins, eteint, eteindre, ferme, fermer, arrete, arreter, desactive, desactiver, deverrouille, deverrouiller, debarre, debarrer |

Les verbes sont comparés **après normalisation**, donc sans accents : la table
ci-dessus reflète exactement le contenu de `VERBES_ON` et `VERBES_OFF`.

> **« ouvre » est volontairement exclu.** Appliqué à une serrure, le mot est ambigu
> (ouvrir la porte ≠ déverrouiller). L'ambiguïté produirait une action non voulue
> plutôt qu'un rejet propre. « ferme » reste dans `VERBES_OFF` car il sert aussi
> aux autres actionneurs — pour la serrure, « ferme la porte » est donc interprété
> comme un déverrouillage. Préférer « verrouille » et « déverrouille », qui ne
> souffrent d'aucune ambiguïté.

### 2.4 Cibles reconnues

**Actionneurs** — dictionnaire `ACTIONNEURS`, surnom → nom interne :

| Mots reconnus | Nom interne |
|---|---|
| pompe | `aquarium_pompe` |
| uv, sterilisateur | `aquarium_uv` |
| serrure, porte, verrou | `entree_serrure` |

**Capteurs** — dictionnaire `CAPTEURS`, mot de lieu → nom interne :

| Mot reconnu | Nom interne |
|---|---|
| aquarium | `temperature_aquarium` |
| salon | `temperature_salon` |

Le nom de la grandeur mesurée (« température ») n'est pas analysé : chaque lieu
n'expose qu'un seul capteur interrogeable, le mot de lieu suffit donc à lever
l'ambiguïté. Ajouter une deuxième grandeur par pièce demanderait d'étendre la
clé du dictionnaire.

### 2.5 Phrases-types

| Phrase prononcée | Type | Réponse de Merlin |
|---|---|---|
| Merlin, quelle est la température de l'aquarium ? | REQUETE | La température de l'aquarium est de 24.2 degrés Celsius. |
| Merlin, donne-moi la température du salon | REQUETE | Il fait 21.5 degrés Celsius dans le salon. |
| Merlin, éteins la pompe s'il te plaît | ACTION | J'éteins la pompe de l'aquarium. |
| Merlin, peux-tu allumer l'UV | ACTION | J'allume la lumière UV de l'aquarium. |
| Merlin, verrouille la porte | ACTION | Je verrouille la serrure de l'entrée. |
| Merlin, déverrouille le verrou | ACTION | Je déverrouille la serrure de l'entrée. |
| Merlin, allume la pomme | INCONNUE | Désolé, je n'ai pas compris votre demande. |

> **Cas limite à connaître.** « Merlin, éteins la lumière du salon » est analysée
> comme une REQUETE ? Non : « eteins » est un verbe d'action, mais « lumiere » ne
> figure pas dans `ACTIONNEURS` — et bien que « salon » soit un capteur, la branche
> REQUETE exige l'absence de verbe d'action. Le résultat est donc INCONNUE, ce qui
> est le comportement voulu : la lumière du salon est pilotée par le contrôleur,
> pas par la voix.

### 2.6 Normalisation — l'ordre compte

`normaliser()` applique les transformations dans cet ordre strict :

| # | Étape | Effet |
|---|---|---|
| 1 | minuscules | « Merlin » ≡ « merlin » |
| 2 | décomposition NFD + retrait des diacritiques | « éteins » → « eteins » |
| 3 | apostrophes et tirets → espaces | « s'il » → « s il », « peux-tu » → « peux tu » |
| 4 | retrait des formules de politesse (regex `POLITESSE`) | « s il te plait » disparaît |
| 5 | ponctuation restante → espaces | tout ce qui n'est pas `[a-z0-9 ]` |
| 6 | espaces multiples → espace simple | |

**Inverser 3 et 4 casserait la regex.** `POLITESSE` est écrite sans accents ni
apostrophes (`s il te plait`, `peux tu`) précisément parce qu'elle s'applique après
les étapes 2 et 3. C'est le piège principal de cette fonction.

Formules retirées : bonjour, salut, merci, s'il te plaît, s'il vous plaît, stp, svp,
je voudrais, peux-tu, pouvez-vous.

La tokenisation utilise `nltk.word_tokenize(language="french")`. Le corpus
`punkt_tab` est téléchargé une seule fois, au premier import
(`try nltk.data.find` / `except nltk.download`).

> **Pourquoi les phrases journalisées sont sans accents.** C'est la phrase
> *normalisée* qui est enregistrée, car c'est elle que l'assistant a réellement
> analysée. Journaliser le texte brut donnerait une trace différente de ce qui a été
> traité, ce qui rendrait le débogage trompeur.

---

## 3. Sujets MQTT de l'assistant

### 3.1 Journal vocal (publish)

| Sujet | Charge utile | Description |
|---|---|---|
| `assistant/journal` | `{"phrase","type","reponse"}` | Une interaction complète : phrase normalisée, type d'intention, réponse vocale. Consommé par Node-RED. |

> Racine **volontairement distincte** de `maison/` — voir la note d'architecture (§1).

### 3.2 Capteurs lus (subscribe)

| Sujet | Nom interne | Usage |
|---|---|---|
| `maison/salon/aquarium/temperature` | `temperature_aquarium` | Requête d'état n° 1 |
| `maison/salon/temperature` | `temperature_salon` | Requête d'état n° 2 |

L'assistant conserve la dernière valeur reçue en mémoire (`dernieres_valeurs`) : il
ne consulte jamais la base pour répondre. Tant qu'aucune lecture n'est arrivée, il
répond « Je n'ai pas encore reçu de lecture pour ce capteur ».

### 3.3 Actionneurs commandés (publish)

| Sujet de commande | Nom interne | ON | OFF |
|---|---|---|---|
| `maison/salon/aquarium/pompe/cmd` | `aquarium_pompe` | `allume` | `eteint` |
| `maison/salon/aquarium/uv/cmd` | `aquarium_uv` | `allume` | `eteint` |
| `maison/entree/serrure/cmd` | `entree_serrure` | `verrouille` | `deverrouille` |

Charge utile : `{"commande": "..."}` — **format identique à celui du contrôleur du
Projet 1**. Les actionneurs ne font aucune différence entre une commande automatique
et une commande vocale.

La table de correspondance `COMMANDES` (attribut de classe de `MaisonMQTT`) traduit
l'intention abstraite ON/OFF en vocabulaire propre à chaque appareil : la serrure
parle « verrouille/deverrouille », les autres « allume/eteint ».

> **Choix du trio « zéro conflit ».** Aucun de ces trois actionneurs n'est piloté par
> une règle automatique du contrôleur (voir le tableau des règles du Projet 1).
> Pendant la démonstration, le contrôleur ne peut donc pas annuler une commande
> vocale — contrairement à la lumière du salon, que la règle de luminosité
> rallumerait aussitôt. Ce sont aussi des objets **uniques** dans la maison : aucune
> ambiguïté de pièce à lever dans la phrase.

---

## 4. Base de données

### 4.1 Schéma

Base `maison`, **14 tables** créées automatiquement au premier appel :
12 tables de lectures de capteurs (une par entrée de `config.TABLES_CAPTEURS`,
alimentées par le contrôleur) et 2 tables de journalisation vocale.

**`journal_commandes`** — ce que Merlin a *entendu et compris*

| Colonne | Type | Nullable | Justification |
|---|---|---|---|
| `id` | `INT AUTO_INCREMENT PRIMARY KEY` | non | Clé primaire |
| `phrase` | `VARCHAR(255) NOT NULL` | non | Phrase normalisée, telle qu'analysée |
| `type_intention` | `VARCHAR(16) NOT NULL` | non | `ACTION`, `REQUETE` ou `INCONNUE` |
| `cible` | `VARCHAR(64)` | **oui** | NULL pour une INCONNUE : aucune cible identifiée |
| `action` | `VARCHAR(8)` | **oui** | NULL pour une REQUETE ou une INCONNUE : seules les ACTIONs portent ON/OFF |
| `horodatage` | `DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP` | non | Rempli par le SGBD |

**`journal_reponses`** — ce que Merlin a *dit*

| Colonne | Type | Nullable | Justification |
|---|---|---|---|
| `id` | `INT AUTO_INCREMENT PRIMARY KEY` | non | Clé primaire |
| `texte` | `VARCHAR(255) NOT NULL` | non | Réponse vocale exacte |
| `horodatage` | `DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP` | non | Rempli par le SGBD |

**`lectures_*`** (× 12) — structure commune à tous les capteurs

| Colonne | Type | Justification |
|---|---|---|
| `id` | `INT AUTO_INCREMENT PRIMARY KEY` | Clé primaire |
| `valeur` | `DOUBLE NOT NULL` | Accepte entiers et décimaux sans distinction |
| `unite` | `VARCHAR(16) NOT NULL DEFAULT ''` | °C, lux, %, ppm — rend la lecture autoportante |
| `horodatage` | `DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP` | Rempli par le SGBD |

### 4.2 Décisions de conception

**Une table par capteur plutôt qu'une table unique.** Chaque capteur a son propre
type de valeur et sa propre cadence ; les séparer évite une colonne `capteur` répétée
sur des millions de lignes et permet de purger un historique sans toucher aux autres.
La correspondance capteur → table est centralisée dans `config.TABLES_CAPTEURS`.

**Deux tables de journal plutôt qu'une.** Une commande et une réponse sont deux
événements distincts : toute commande est journalisée, y compris rejetée, alors
qu'une réponse existe même sans commande valide. Les séparer évite des colonnes
majoritairement NULL et permet d'interroger l'un sans l'autre.

**`cible` et `action` NULL-ables.** C'est ce qui rend traçables les échecs de
compréhension. Une intention INCONNUE laisse une ligne complète avec la phrase
exacte — matière première pour enrichir `ACTIONNEURS` et `CAPTEURS`.

**Horodatage côté SGBD.** `DEFAULT CURRENT_TIMESTAMP` plutôt qu'un `datetime.now()`
Python : une seule source de vérité temporelle, insensible aux écarts d'horloge entre
les processus (contrôleur et assistant tournent séparément).

**Une seule fonction d'insertion.** `inserer(table, valeurs)` construit la requête à
partir des clés du dictionnaire et passe les valeurs en **paramètres liés** (`?`) —
aucune valeur n'est concaténée dans une chaîne SQL. Aucune requête `INSERT` n'est
écrite deux fois dans le projet.

**Connexion paresseuse.** `_obtenir_connexion()` n'ouvre la connexion qu'au premier
appel réel : un module importé sans être utilisé ne mobilise pas MariaDB. La création
de la base et des tables (`CREATE ... IF NOT EXISTS`) se fait au même moment, ce qui
rend le projet installable sans script SQL préalable.

**`autocommit=True`.** Chaque insertion est indépendante : il n'existe aucune
opération multi-tables à rendre atomique, donc pas de transaction explicite à gérer.

**Une instance par programme.** Le contrôleur et l'assistant créent chacun leur
`BaseDeDonnees`, donc leur propre connexion — aucun objet partagé entre processus.

---

## 5. Installation (Projet 2)

### 5.1 Prérequis supplémentaires

En plus de Mosquitto et Node-RED (voir Projet 1) :

- **Python 3.13** — *pas 3.14* : PyAudio n'a pas de binaire précompilé pour 3.14 (échec sur `portaudio.h`). Toutes les commandes utilisent `py -3.13`.
- **MariaDB** sur `localhost:3306`
- Un microphone fonctionnel

### 5.2 Dépendances

```powershell
py -3.13 -m pip install -r requirements.txt
```

Deux versions sont épinglées pour des raisons précises :

| Paquet | Version | Raison |
|---|---|---|
| `pyttsx3` | 2.71 | Les versions ultérieures ne relisent plus après le premier `runAndWait()` (bug du pilote SAPI5) |
| `python-dotenv` | 1.0.1 | Lecture du fichier `.env` |

### 5.3 Identifiants de la base

Le mot de passe n'est **pas** dans le code. Copier le modèle et le renseigner :

```powershell
copy .env.exemple .env
```

Puis éditer `.env` :

```
DB_PASSWORD=votre_mot_de_passe_mariadb
```

`config.py` le lit via `os.getenv()` et lève une erreur explicite si la variable est
absente. Le fichier `.env` est ignoré par Git.

### 5.4 Voix de synthèse

`voix.py` cible la voix **Microsoft Claude (fr-CA)**, avec repli automatique sur la
première voix française disponible si elle est absente du système. Le moteur pyttsx3
est initialisé **une seule fois** au niveau du module (`init()` prend environ une
seconde).

Le `pause_threshold` de l'écoute est porté à **1,2 s** (défaut : 0,8 s), qui coupait
les phrases longues avant leur fin.

---

## 6. Exécution (Projet 2)

Un terminal par commande, depuis la racine du projet.

```powershell
# Terminal 1 — contrôleur + journalisation MariaDB des capteurs
py -3.13 -m controleur.controleur

# Terminaux 2-3 — les deux capteurs interrogeables
py -3.13 -m capteurs.capteur_aquarium_temperature
py -3.13 -m capteurs.capteur_salon_temperature

# Terminaux 4-6 — les trois actionneurs commandables
py -3.13 -m actionneurs.actionneur_aquarium_pompe
py -3.13 -m actionneurs.actionneur_aquarium_uv
py -3.13 -m actionneurs.actionneur_entree_serrure

# Terminal 7 — Merlin
py -3.13 -m assistant.assistant
```

Laisser les capteurs publier deux ou trois secondes avant de parler.

### Banc d'essai de l'analyse d'intentions

Sans micro ni courtier :

```powershell
py -3.13 test_intentions.py
```

6 phrases, 6 analyses attendues : 3 ACTION, 2 REQUETE, 1 INCONNUE.

### Tableau de bord

Le groupe **Assistant vocal** (page « Maison ») affiche les 15 dernières
interactions, horodatées, avec le type d'intention et la réponse.

> L'historique est conservé dans le contexte de flux Node-RED : il est vidé à chaque
> `Deploy` et à chaque redémarrage. C'est voulu — la liste se remplit en direct
> pendant la démonstration.

---

## 7. Débogage

L'assistant imprime en continu ce qu'il **entend** et ce qu'il **répond** :

```
Entendu : Merlin quelle est la temperature de l aquarium
Assistant : La température de l'aquarium est de 24.23 degrés Celsius.
```

Les phrases sans mot-clé apparaissent aussi (`Entendu :` sans `Assistant :`) : c'est
ce qui rend visible le filtrage du mot-clé.

Vérifier la journalisation en base :

```sql
SELECT * FROM maison.journal_commandes ORDER BY horodatage DESC LIMIT 10;
SELECT * FROM maison.journal_reponses  ORDER BY horodatage DESC LIMIT 10;
```

---

## 8. Bugs du squelette trouvés et corrigés

| Fichier | Problème | Correction |
|---|---|---|
| `config.py` | `DB_PORT` absent alors que `db.py` l'utilise | Ajout de `DB_PORT = 3306` |
| `assistant/assistant.py` | Variable `appareil` inexistante dans `executer_intention()` | Renommée `actionneur` |
| `assistant/maison_mqtt.py` | `on_connect` à 4 paramètres, incompatible avec `CallbackAPIVersion.VERSION2` | Signature portée à 5 paramètres (`reason_code`, `properties`) |
| `assistant/assistant.py` | `self.arreter()` appelé hors de la classe, en fin de fichier | Ligne supprimée — `main()` appelle déjà `self.arreter()` |

---
---

# PROJET 1 — Infrastructure MQTT

Simulation d'une maison connectée avec 3 pièces (Salon, Entrée, Garage) et un
aquarium : 12 capteurs, 9 actionneurs, un contrôleur à règles automatiques, et un
tableau de bord Node-RED en temps réel.

## Architecture complète (flux publish-subscribe)

```mermaid
graph LR
    subgraph Capteurs
        C1[salon - température]
        C2[salon - luminosité]
        C3[salon - humidité]
        C4[aquarium - température]
        C5[aquarium - pH]
        C6[aquarium - niveau]
        C7[entrée - mouvement]
        C8[entrée - porte]
        C9[garage - température]
        C10[garage - CO]
        C11[garage - véhicule]
        C12[garage - code-barres]
    end

    subgraph Courtier
        M[Mosquitto :1883]
    end

    subgraph Contrôleur
        K[controleur.py]
    end

    subgraph Actionneurs
        A1[salon - lumière]
        A2[salon - thermopompe]
        A3[aquarium - pompe]
        A4[aquarium - UV]
        A5[entrée - lumière]
        A6[entrée - serrure]
        A7[garage - chauffage]
        A8[garage - porte]
        A9[garage - lumière]
    end

    subgraph Visualisation
        N[Node-RED Dashboard]
    end

    C1 & C2 & C3 & C4 & C5 & C6 & C7 & C8 & C9 & C10 & C11 & C12 -->|publish| M
    M -->|subscribe| K
    K -->|commandes| M
    M -->|subscribe| A1 & A2 & A3 & A4 & A5 & A6 & A7 & A8 & A9
    A1 & A2 & A3 & A4 & A5 & A6 & A7 & A8 & A9 -->|états| M
    M -->|maison/#| N
```

---

## Règles d'automatisation

Le contrôleur relie capteurs et actionneurs via les règles suivantes :

| # | Capteur déclencheur | Condition | Actionneur | Commande |
|---|---------------------|-----------|------------|----------|
| 1 | Luminosité salon | < 200 lux | Lumière salon | `allume` |
| 2 | Luminosité salon | ≥ 200 lux | Lumière salon | `eteint` |
| 3 | Température salon | < 18°C | Thermopompe salon | `chauffe` |
| 4 | Température salon | > 23°C | Thermopompe salon | `climatise` |
| 5 | Température salon | 18–23°C | Thermopompe salon | `arrete` |
| 6 | pH aquarium | < 6.8 ou > 7.5 | — | log surveillance |
| 7 | Niveau aquarium | < 70% | UV aquarium | `eteint` |
| 8 | Niveau aquarium | ≥ 70% | UV aquarium | `allume` |
| 9 | Mouvement entrée | détecté (1) | Lumière entrée | `allume` |
| 10 | Mouvement entrée | absent (0) | Lumière entrée | `eteint` |
| 11 | Température garage | < 15°C | Chauffage garage | `allume` |
| 12 | Température garage | ≥ 17°C | Chauffage garage | `eteint` |
| 13 | CO garage | > 25 ppm | Porte garage | `ouvre` |
| 14 | Véhicule + code-barres valide | AUTO-001/002/003 | Porte + lumière garage | `ouvre` / `allume` |
| 15 | Véhicule parti | absent (0) | Porte + lumière garage | `ferme` / `eteint` |

**Notes sur les seuils :**
- Température garage : 15°C minimum selon le Règlement 03-096 de la Ville de Montréal
- CO garage : 25 ppm selon le Ministère de la Sécurité publique du Québec
- pH aquarium : 6.8–7.5 selon les normes d'aquariophilie eau douce

> **Lien avec le Projet 2.** La pompe et la serrure n'apparaissent dans aucune de
> ces règles ; l'UV n'y figure que via la règle de niveau d'eau (7-8), qui ne se
> déclenche pas tant que le capteur de niveau n'est pas lancé. C'est ce qui garantit
> l'absence de conflit pendant la démonstration vocale.

---

## Installation de l'infrastructure

**1. Mosquitto**
- Télécharger : https://mosquitto.org/download/
- Éditer `C:\Program Files\mosquitto\mosquitto.conf` :
```
  listener 1883 localhost
  allow_anonymous true
```
- Dans un terminal **administrateur** :
```powershell
  net stop mosquitto
  net start mosquitto
```

**2. Node-RED**
- Installer **Node.js LTS** : https://nodejs.org/
```powershell
  npm install -g node-red
  node-red
```
- Ouvrir http://localhost:1880
- Importer `flows.json` : menu ☰ → **Import** → sélectionner `flows.json` → **Deploy**
- Tableau de bord : http://localhost:1880/dashboard

---

## Exécution complète (les 22 processus)

> Pour la démonstration du Projet 2, seuls 7 terminaux sont nécessaires — voir la
> section 6 plus haut.

```powershell
# Contrôleur
py -3.13 -m controleur.controleur

# Capteurs (un terminal par capteur)
py -3.13 -m capteurs.capteur_salon_temperature
py -3.13 -m capteurs.capteur_salon_luminosite
py -3.13 -m capteurs.capteur_salon_humidite
py -3.13 -m capteurs.capteur_aquarium_temperature
py -3.13 -m capteurs.capteur_aquarium_ph
py -3.13 -m capteurs.capteur_aquarium_niveau
py -3.13 -m capteurs.capteur_entree_mouvement
py -3.13 -m capteurs.capteur_entree_porte
py -3.13 -m capteurs.capteur_garage_temperature
py -3.13 -m capteurs.capteur_garage_co
py -3.13 -m capteurs.capteur_garage_vehicule
py -3.13 -m capteurs.capteur_garage_barcode

# Actionneurs (un terminal par actionneur)
py -3.13 -m actionneurs.actionneur_salon_lumiere
py -3.13 -m actionneurs.actionneur_salon_thermopompe
py -3.13 -m actionneurs.actionneur_aquarium_pompe
py -3.13 -m actionneurs.actionneur_aquarium_uv
py -3.13 -m actionneurs.actionneur_entree_lumiere
py -3.13 -m actionneurs.actionneur_entree_serrure
py -3.13 -m actionneurs.actionneur_garage_chauffage
py -3.13 -m actionneurs.actionneur_garage_porte
py -3.13 -m actionneurs.actionneur_garage_lumiere
```

---

## Sujets MQTT complets

### Capteurs (publish)

| Sujet | Charge utile | Description |
|-------|-------------|-------------|
| `maison/salon/temperature` | `{"type","valeur","unite","horodatage"}` | Température salon (°C) |
| `maison/salon/luminosite` | `{"type","valeur","unite","horodatage"}` | Luminosité salon (lux) |
| `maison/salon/humidite` | `{"type","valeur","unite","horodatage"}` | Humidité salon (%) |
| `maison/salon/aquarium/temperature` | `{"type","valeur","unite","horodatage"}` | Température aquarium (°C) |
| `maison/salon/aquarium/ph` | `{"type","valeur","unite","horodatage"}` | pH aquarium (6.8–7.5 normal) |
| `maison/salon/aquarium/niveau` | `{"type","valeur","unite","horodatage"}` | Niveau eau aquarium (%) |
| `maison/entree/mouvement` | `{"type","valeur","unite","horodatage"}` | Mouvement entrée (0/1) |
| `maison/entree/porte` | `{"type","valeur","unite","horodatage"}` | État porte entrée (ouvert/ferme) |
| `maison/garage/temperature` | `{"type","valeur","unite","horodatage"}` | Température garage (°C) |
| `maison/garage/co` | `{"type","valeur","unite","horodatage"}` | CO garage (ppm) |
| `maison/garage/vehicule` | `{"type","valeur","unite","horodatage"}` | Présence véhicule (0/1) |
| `maison/garage/barcode` | `{"type","valeur","unite","horodatage"}` | Code-barres lu (AUTO-001/002/003/INCONNU) |

### Actionneurs (commande / état)

| Sujet commande | Sujet état | Commandes |
|----------------|------------|-----------|
| `maison/salon/lumiere/cmd` | `maison/salon/lumiere/etat` | `allume` / `eteint` |
| `maison/salon/thermopompe/cmd` | `maison/salon/thermopompe/etat` | `chauffe` / `climatise` / `ventile` / `arrete` |
| `maison/salon/aquarium/pompe/cmd` | `maison/salon/aquarium/pompe/etat` | `allume` / `eteint` |
| `maison/salon/aquarium/uv/cmd` | `maison/salon/aquarium/uv/etat` | `allume` / `eteint` |
| `maison/entree/lumiere/cmd` | `maison/entree/lumiere/etat` | `allume` / `eteint` |
| `maison/entree/serrure/cmd` | `maison/entree/serrure/etat` | `verrouille` / `deverrouille` |
| `maison/garage/chauffage/cmd` | `maison/garage/chauffage/etat` | `allume` / `eteint` |
| `maison/garage/porte/cmd` | `maison/garage/porte/etat` | `ouvre` / `ferme` |
| `maison/garage/lumiere/cmd` | `maison/garage/lumiere/etat` | `allume` / `eteint` |

### Santé des capteurs (LWT)

Chaque capteur publie `{"etat":"hors-ligne"}` sur son sujet `/sante` en cas de
déconnexion brutale :

`maison/salon/temperature/sante`, `maison/salon/luminosite/sante`,
`maison/salon/humidite/sante`, `maison/salon/aquarium/temperature/sante`,
`maison/salon/aquarium/ph/sante`, `maison/salon/aquarium/niveau/sante`,
`maison/entree/mouvement/sante`, `maison/entree/porte/sante`,
`maison/garage/temperature/sante`, `maison/garage/co/sante`,
`maison/garage/vehicule/sante`, `maison/garage/barcode/sante`

---

## Bonus

### #2 — Carte maison en temps réel (+5%)

Une deuxième page Node-RED affiche un plan de la maison en HTML/CSS. La couleur de la
bordure change selon l'état : 🟢 normal, 🟡 attention (thermopompe active), 🔴 alerte
(mouvement détecté). Les données proviennent d'un abonnement `maison/#` via un nœud
`function` qui maintient l'état global en mémoire de flux.

### #4 — Robustesse MQTT (+5%)

- **QoS 0** pour les capteurs : publication fréquente (2 s), une valeur perdue est sans conséquence
- **QoS 2** pour les abonnements des actionneurs : une commande doit être exécutée exactement une fois
- **retain=True** sur tous les sujets capteurs et états actionneurs : le tableau de bord affiche une valeur dès l'ouverture
- **LWT** sur chaque capteur : en cas de déconnexion brutale, le courtier publie automatiquement `{"etat":"hors-ligne"}` sur le sujet `/sante`

### Bonus retirés

**#1 — Capteur de vision OpenCV :** la bibliothèque ne permettait pas d'afficher le
flux vidéo dans le tableau de bord Node-RED. Sans visualisation, la valeur ajoutée par
rapport à un capteur simulé était insuffisante.

**#3 — Alertes et notifications :** les données étant simulées aléatoirement, les
alertes se déclenchaient continuellement sans refléter une situation réelle. La
persistance MariaDB du Projet 2 rend désormais ce type d'analyse pertinent.

---
---

## Structure du dépôt

```
projet1-420-315-E26/
├── .env                                Secrets locaux — NON versionné
├── .env.exemple                        Modèle à copier
├── .gitignore
├── config.py                           Constantes : MQTT, BD, sujets, tables
├── requirements.txt
├── flows.json                          Flux Node-RED exportés
├── test_intentions.py                  Banc d'essai de l'analyse
├── assistant/                          ── PROJET 2 ──
│   ├── __init__.py
│   ├── assistant.py                    Boucle principale, mot-clé, journalisation
│   ├── intentions.py                   normaliser / tokeniser / analyser
│   ├── maison_mqtt.py                  commander, lire, publier_interaction
│   └── voix.py                         Oreille (écoute) + parler (synthèse)
├── basededonnees/                      ── PROJET 2 ──
│   ├── __init__.py
│   └── db.py                           Connexion paresseuse + inserer()
├── capteurs/                           ── PROJET 1 ──
│   ├── __init__.py
│   ├── base_capteur.py                 Classe de base Capteur (LWT, retain, QoS)
│   ├── capteur_salon_temperature.py
│   ├── capteur_salon_luminosite.py
│   ├── capteur_salon_humidite.py
│   ├── capteur_aquarium_temperature.py
│   ├── capteur_aquarium_ph.py          Capteur pH (ajouté par la prof)
│   ├── capteur_aquarium_niveau.py
│   ├── capteur_entree_mouvement.py
│   ├── capteur_entree_porte.py
│   ├── capteur_garage_temperature.py
│   ├── capteur_garage_co.py            Détection monoxyde de carbone
│   ├── capteur_garage_vehicule.py
│   ├── capteur_garage_barcode.py       Lecteur de code-barres simulé
│   └── exemples/
│       └── capteur_aquarium.py         Exemple fourni par la prof
├── actionneurs/                        ── PROJET 1 ──
│   ├── __init__.py
│   ├── base_actionneur.py              Classe de base Actionneur (QoS 2, retain)
│   ├── actionneur_salon_lumiere.py
│   ├── actionneur_salon_thermopompe.py
│   ├── actionneur_aquarium_pompe.py
│   ├── actionneur_aquarium_uv.py
│   ├── actionneur_entree_lumiere.py
│   ├── actionneur_entree_serrure.py    Verrouillée par défaut
│   ├── actionneur_garage_chauffage.py
│   ├── actionneur_garage_porte.py
│   └── actionneur_garage_lumiere.py
└── controleur/
    ├── __init__.py
    └── controleur.py                   Règles d'automatisation + journalisation MariaDB
```

---

*Projet réalisé dans le cadre du cours 420-315-AH — Collège Ahuntsic, session été 2026.*