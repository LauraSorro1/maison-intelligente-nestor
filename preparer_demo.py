"""Prepare l'etat de depart avant l'enregistrement de la video de demo.

Publie directement sur MQTT (sans passer par Nestor) pour remettre les
trois actionneurs dans l'etat attendu par le scenario du README (§6.2) :
    - pompe de l'aquarium : allumee
    - UV de l'aquarium    : eteint
    - serrure de l'entree : deverrouillee

Sans cet etat de depart, Nestor repondrait "c'est deja fait" et aucun
effet ne serait visible a l'ecran pendant le tournage.

Usage :
    py -3.13 preparer_demo.py
"""

import json

import paho.mqtt.client as mqtt

HOTE = "localhost"
PORT = 1883

# (sujet, commande) -- memes sujets et vocabulaire que maison_mqtt.py
ETAT_DE_DEPART = [
    ("maison/salon/aquarium/pompe/cmd", "allume"),
    ("maison/salon/aquarium/uv/cmd", "eteint"),
    ("maison/entree/serrure/cmd", "deverrouille"),
]


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="preparer-demo")
    client.connect(HOTE, PORT)
    client.loop_start()

    for sujet, commande in ETAT_DE_DEPART:
        charge = json.dumps({"commande": commande})
        client.publish(sujet, charge)
        print(f"Publie sur {sujet} : {charge}")

    client.loop_stop()
    client.disconnect()
    print("Etat de depart pret pour la demo.")


if __name__ == "__main__":
    main()