"""Accès MariaDB : lectures de capteurs et journal de l'assistant vocal.

La configuration (hôte, utilisateur, nom de la base) vient de config.py.
Chaque programme (contrôleur, assistant) crée sa propre instance de
BaseDeDonnees, ce qui lui donne une connexion à lui.

La connexion est ouverte paresseusement au premier appel : la base et les
tables sont alors créées si elles n'existent pas déjà.
"""
import mariadb

import config


class BaseDeDonnees:
    def __init__(self):
        self.connexion = None

    def _obtenir_connexion(self):
        """Retourne la connexion, en créant la base et les tables au besoin."""
        if self.connexion is None:
            self.connexion = mariadb.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                autocommit=True,
            )
            curseur = self.connexion.cursor()
            curseur.execute(f"CREATE DATABASE IF NOT EXISTS {config.DB_NAME}")
            curseur.execute(f"USE {config.DB_NAME}")
            self._creer_tables(curseur)
            curseur.close()
        return self.connexion

    def _creer_tables(self, curseur):
        # Une table de lectures par capteur (voir config.TABLES_CAPTEURS).
        for table in config.TABLES_CAPTEURS.values():
            curseur.execute(
                f"""CREATE TABLE IF NOT EXISTS {table} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    valeur DOUBLE NOT NULL,
                    unite VARCHAR(16) NOT NULL DEFAULT '',
                    horodatage DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )"""
            )
        #* TODO: Créer les tables de journalisation de l'assistant vocal (commandes recues et réponses vocales) avec curseur.execute(f"""CREATE TABLE IF NOT EXISTS {table} (...)""")

        # Table du journal des commandes vocales reçues
        curseur.execute(
            """CREATE TABLE IF NOT EXISTS journal_commandes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                phrase VARCHAR(255) NOT NULL,
                type_intention VARCHAR(16) NOT NULL,
                cible VARCHAR(64),
                action VARCHAR(8),
                horodatage DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )

        # Table du journal des réponses vocales générées
        curseur.execute(
            """CREATE TABLE IF NOT EXISTS journal_reponses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                texte VARCHAR(255) NOT NULL,
                horodatage DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )

    def inserer(self, table, valeurs):
        """Insère une ligne dans `table` ; `valeurs` est un dict colonne → valeur.

        C'est à l'appelant de dire dans quelle table écrire (le contrôleur la
        tire de config.TABLES_CAPTEURS, l'assistant nomme sa table de journal).
        """
        colonnes = ", ".join(valeurs)
        marqueurs = ", ".join("?" for _ in valeurs)
        curseur = self._obtenir_connexion().cursor()
        curseur.execute(
            f"INSERT INTO {table} ({colonnes}) VALUES ({marqueurs})",
            tuple(valeurs.values()),
        )
        curseur.close()

    def fermer(self):
        """Ferme la connexion (sans erreur si elle n'a jamais été ouverte)."""
        if self.connexion is not None:
            self.connexion.close()
            self.connexion = None
