import os
import psycopg2
from psycopg2 import sql
import ssl


CONN_STRING = "postgresql://clothing_recommender_db_user:N4xrmoiOOJxoKNaxXcxZYr30SDag4CkN@dpg-df8dfeuncj78730654ag-a.oregon-postgres.render.com:5432/clothing_recommender_db?sslmode=require"

# Configuration de la base de données
DB_CONFIG = {
    "host": "dpg-df8dfeuncj78730654ag-a.oregon-postgres.render.com",
    "database": "clothing_recommender_db",
    "user": "clothing_recommender_db_user",
    "password": "N4xrmoiOOJxoKNaxXcxZYr30SDag4CkN",
    "port": 5432,
    "sslmode": "require",
    "sslrootcert": "render.crt",  # Optionnel si vous avez le certificat
    "connect_timeout": 10,
    "keepalives": 1,
    "keepalives_idle": 30,
    "keepalives_interval": 10,
    "keepalives_count": 5
}

def get_db_connection(max_retries=3, retry_delay=2):
    """Établit une connexion à la base de données avec reprise en cas d'échec"""
    for attempt in range(max_retries):
        try:
            # Essai avec la chaîne de connexion directe
            conn = psycopg2.connect(CONN_STRING)
            print("✅ Connexion établie avec succès (méthode chaîne de connexion)")
            return conn
            
        except psycopg2.OperationalError as e:
            print(f"⚠ Tentative {attempt + 1} échouée avec la chaîne de connexion. Essai avec les paramètres séparés...")
            
            try:
                # Essai avec les paramètres séparés et configuration SSL personnalisée
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                conn_params = DB_CONFIG.copy()
                if not os.path.exists(conn_params.get('sslrootcert', '')):
                    conn_params.pop('sslrootcert', None)
                
                conn = psycopg2.connect(**conn_params)
                print("✅ Connexion établie avec succès (méthode paramètres séparés)")
                return conn
                
            except psycopg2.OperationalError as e:
                print(f"⚠ Tentative {attempt + 1} échouée: {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ Nouvel essai dans {retry_delay} secondes...")
                    time.sleep(retry_delay)
    
    print("❌ Échec de toutes les tentatives de connexion")
    return None

    
def create_tables():
    """Crée toutes les tables dans la base existante"""
    tables = {
        "pull": """
            CREATE TABLE IF NOT EXISTS pull (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """,
        "t_shirt": """
            CREATE TABLE IF NOT EXISTS t_shirt (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """,
        "jupe": """
            CREATE TABLE IF NOT EXISTS jupe (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """,
        "robe": """
            CREATE TABLE IF NOT EXISTS robe (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """,
        "pantalon": """
            CREATE TABLE IF NOT EXISTS pantalon (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """,
        "chemise": """
            CREATE TABLE IF NOT EXISTS chemise (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """,
        "manteau": """
            CREATE TABLE IF NOT EXISTS manteau (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """,
        "short": """
            CREATE TABLE IF NOT EXISTS short (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """,
        "couvre_chef": """
            CREATE TABLE IF NOT EXISTS couvre_chef (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """,
        "bonnet": """
            CREATE TABLE IF NOT EXISTS bonnet (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """,
        "haut_sport": """
            CREATE TABLE IF NOT EXISTS haut_sport (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """,
        "veste": """
            CREATE TABLE IF NOT EXISTS veste (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """,
        "chaussure": """
            CREATE TABLE IF NOT EXISTS chaussure (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """,
        "costume": """
            CREATE TABLE IF NOT EXISTS costume (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """,
        "collants": """
            CREATE TABLE IF NOT EXISTS collants (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """,
        "bas_sport": """
            CREATE TABLE IF NOT EXISTS bas_sport (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """,
        "chaussure_sport": """
            CREATE TABLE IF NOT EXISTS chaussure_sport (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """,
        "maillot_bain_femme": """
            CREATE TABLE IF NOT EXISTS maillot_bain_femme (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """,
        "maillot_bain_homme": """
            CREATE TABLE IF NOT EXISTS maillot_bain_homme (
                id SERIAL PRIMARY KEY,
                couleur VARCHAR(50),
                nom VARCHAR(100),
                chaleur INT CHECK (chaleur BETWEEN 1 AND 10),
                utilisateur VARCHAR(200),
                nb_utilisation INT DEFAULT 0
            )
        """
    }

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            print("❌ Impossible d'établir une connexion à la base de données")
            return

        cur = conn.cursor()

        # Supprimer toutes les tables existantes
        print("🔍 Suppression des tables existantes...")
        cur.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        for table in cur.fetchall():
            try:
                cur.execute(sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(
                    sql.Identifier(table[0])
                ))
                print(f"✓ Table {table[0]} supprimée")
            except Exception as e:
                print(f"⚠ Erreur lors de la suppression de {table[0]}: {e}")

        # Créer toutes les tables
        print("🔨 Création des nouvelles tables...")
        for table_name, table_sql in tables.items():
            try:
                cur.execute(table_sql)
                print(f"✔ Table '{table_name}' créée")
            except Exception as e:
                print(f"⚠ Erreur lors de la création de {table_name}: {e}")

        print("✅ Structure de base de données mise à jour avec succès")

    except Exception as e:
        print(f"❌ Erreur critique: {e}")
    finally:
        if conn:
            conn.close()
            print("🔌 Connexion fermée")

if __name__ == "__main__":
    print("🚀 Début de l'initialisation de la base de données...")
    create_tables()
    print("🏁 Opération terminée")