"""Accès MariaDB — Projet 1.

Une table par capteur (voir schema.sql). 
"""
import mariadb
import config


def ouvrir_connexion():
    return mariadb.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
    )


def inserer_lecture(type_capteur, valeur, unite):
    """Insère une lecture dans la table du capteur concerné.

    type_capteur est traduit en nom de table via config.TABLES_CAPTEURS ;
    un type inconnu lève une erreur claire plutôt qu'une requête invalide.
    TODO: Consultez cette documentation pour vous aider avec l'implémentation :
    https://mariadb.com/docs/connectors/mariadb-connector-python/usage
    """
    pass
