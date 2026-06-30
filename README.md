# Projet 1 — Station de surveillance d'objets connectés

Cours **420-315-AH — Développement d'objets intelligents**

---

## Architecture (flux publish-subscribe)

INSÉREZ VOTRE DIAGRAMME D'ARCHITECTURE ICI

## RÈGLES D'AUTOMATISATION (le contrôleur relie au moins deux objets) :


   EXPLIQUEZ VOS RÈGLES D'AUTOMATISATION ET LES OBJETS QU'ELLES RELIENT.


---

## Structure

```
projet1-420-315-E26/
├── config.py                Constantes : MQTT, DB, sujets, tables
├── requirements.txt
├── capteurs/                 Capteurs simulés — classes Python (package)
│   ├── __init__.py
│   ├── base_capteur.py       Classe de base Capteur
│   ├── capteur_aquarium.py   Exemple de classe enfant
├── actionneurs/               Actionneurs simulés — classes Python (package)
│   ├── __init__.py
│   ├── base_actionneur.py     Classe de base Actionneur
│   ├── actionneur_aquarium.py Exemple de classe enfant
├── controleur/                (package)
│   ├── __init__.py
│   └── controleur.py        Classe Controleur (abonné + publieur)

```

---

## Prérequis

- **Python 3.11+**
- **Mosquitto** (courtier MQTT) en écoute sur `localhost:1883`
- **Node-RED** + le module **node-red-dashboard** pour le tableau de bord

Sur macOS (Homebrew) :

```bash
brew install mosquitto 
brew services start mosquitto

# Node-RED
npm install -g node-red
# puis, dans le menu Node-RED : Manage palette → installer
# "@flowfuse/node-red-dashboard" (Dashboard 2.0)
```

### Sur Windows 10/11

**1. Mosquitto (courtier MQTT)**

- Télécharger : <https://mosquitto.org/download/> (section *Windows*).
- Installer ; 
- Pour autoriser les connexions locales, éditer
  `C:\Program Files\mosquitto\mosquitto.conf` et ajouter :

  ```
  listener 1883 localhost
  allow_anonymous true
  ```

  puis, dans un terminal **administrateur** : `net stop mosquitto` puis
  `net start mosquitto`. Test rapide sans service :
  `& "C:\Program Files\mosquitto\mosquitto.exe" -v`.


**2. Node-RED**

- Installer d'abord **Node.js (LTS)** : <https://nodejs.org/> 
- Dans un nouveau terminal :

  ```powershell
  npm install -g node-red
  node-red          # puis ouvrir http://localhost:1880
  ```

---

## Installation

```bash
# Depuis le dossier projet1-420-315-E26/
cd projet1-420-315-E26

# Environnement virtuel
python3 -m venv .venv
#Pour MacOS
source .venv/bin/activate
#Pour Windows
.venv\Scripts\activate

pip install -r requirements.txt

---

## Exécution

> Les sous-dossiers (`capteurs/`, `actionneurs/`, `controleur/`) sont des
> **packages Python** (chacun contient un `__init__.py`). On lance donc chaque
> script **comme module** avec `python -m <package>.<module>`, **depuis le
> dossier `projet1-420-315-E26/`**. Chaque script tourne dans son propre terminal.

```bash

# Terminal 1 — Contrôleur (abonné + publieur)
python -m controleur.controleur

# Terminal 2 — Actionneur aquarium (exemple)
python -m actionneurs.actionneur_aquarium

# Terminal 3 — Capteur de température de l'aquarium (exemple)
python -m capteurs.capteur_aquarium

# Ajoutez vos propres capteurs/actionneurs sur ce modèle, puis lancez-les
# de la même façon : python -m capteurs.<votre_module>
```

### Tableau de bord Node-RED (Dashboard 2.0)

Ce flux utilise **Dashboard 2.0** (`@flowfuse/node-red-dashboard`)

1. Installer le module : menu ☰ → **Manage palette** → onglet **Install** →
   chercher **`@flowfuse/node-red-dashboard`** → installer.
   (ou au terminal : `cd ~/.node-red && npm install @flowfuse/node-red-dashboard`,
   puis redémarrer Node-RED).
2. Démarrer Node-RED : `node-red`, puis ouvrir `http://localhost:1880`.
3. **À VOUS DE CONSTRUIRE LE FLUX** : ajoutez des nœuds `mqtt in` abonnés à
   vos sujets capteurs et reliez-les à des nœuds du dashboard (jauge, graphe,
   texte...) pour visualiser les valeurs en temps réel.
4. **Deploy**.
5. Ouvrir le tableau de bord : **`http://localhost:1880/dashboard`**.

Les tuiles se mettent à jour automatiquement à chaque nouvelle valeur publiée.



## Sujets MQTT

| Sujet                          | Direction | Charge utile                                | Décrit                  |
|--------------------------------|-----------|---------------------------------------------|-------------------------|
| `maison/salon/aquarium/temperature`| publier   | `{"type","valeur","unite","horodatage"}`    | Capteur température de l'aquarium  |
| `maison/salon/aquarium/cmd`  | commande  | `{"commande":"sonne"\|"silence"}`           | Eteint ou allume l'alarme de l'aquarium   |
| `maison/salon/aquarium/etat` | état      | `{"nom":"aquarium","etat":...}`             | État de l'alarme publié par l'actionneur|
