import pymysql
import os
import shutil
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

load_dotenv()  # Charge les variables depuis .env

DB_PASSWORD = "N4xrmoiOOJxoKNaxXcxZYr30SDag4CkN"

def get_db_connection():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='mdpsql',
        database='clothes'
    )

def get_db_connection2():
    return psycopg2.connect(
        host="dpg-df8dfeuncj78730654ag-a",
        dbname="clothing_recommender_db",
        user="clothing_recommender_db_user",
        password="DB_PASSWORD",  # À stocker en variable d'environnement
        port="5432"
    )

    
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

    try:
        # Connexion à la DB existante
        conn = get_db_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Nettoyage des tables existantes
        cur.execute("""
            DO $$
            DECLARE
                tbl text;
            BEGIN
                FOR tbl IN 
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || tbl || ' CASCADE';
                    RAISE NOTICE 'Table supprimée: %', tbl;
                END LOOP;
            END $$;
        """)
        print("✔ Tables existantes supprimées")

        # Création des nouvelles tables
        for table_name, table_sql in tables.items():
            cur.execute(table_sql)
            print(f"✔ Table '{table_name}' créée")

        cur.close()
        print("✅ Structure de base de données mise à jour avec succès")

    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        if conn:
            conn.close()

def BDD_parmail(mail='local', couleur = ''): 
    conn = get_db_connection()

    cursor = conn.cursor()


    tables = ['pull', 't_shirt', 'jupe', 'robe','pantalon', 'chemise', 'manteau', 'short', 'couvre_chef','bonnet','haut_sport','bas_sport','chaussure_sport', 'veste', 'chaussure', 'costume','collants','maillot_bain_homme','maillot_bain_femme']

    clothes_database = []


    for table in tables:
        if couleur == '':
            cursor.execute(f"SELECT id, nom, chaleur, couleur, nb_utilisation FROM {table} WHERE utilisateur = '{mail}'")
            rows = cursor.fetchall()
            for row in rows:
                clothes_database.append({
                    "id": row[0],
                    "nom": row[1],
                    "type": table,
                    "chaleur": row[2],
                    "couleur": row[3],
                    "nb_utilisation": row[4] 
                })
        else:
            cursor.execute(f"SELECT id, nom, chaleur, couleur, nb_utilisation FROM {table} WHERE utilisateur = '{mail}' AND couleur = '{couleur}'")
            rows = cursor.fetchall()
            for row in rows:
                clothes_database.append({
                    "id": row[0],
                    "nom": row[1],
                    "type": table,
                    "chaleur": row[2],
                    "couleur": row[3],
                    "nb_utilisation": row[4] 
                })


    conn.close()

    return clothes_database

def BDD_total(): 
    conn = get_db_connection()

    cursor = conn.cursor()


    tables = ['pull', 't_shirt', 'jupe', 'robe','pantalon', 'chemise', 'manteau', 'short', 'couvre_chef','bonnet','haut_sport','bas_sport','chaussure_sport', 'veste', 'chaussure', 'costume','collants','maillot_bain_homme','maillot_bain_femme']

    clothes_database = []


    for table in tables:
        cursor.execute(f"SELECT id, nom, chaleur, couleur, nb_utilisation FROM {table}")
        rows = cursor.fetchall()
        for row in rows:
            clothes_database.append({
                "id": row[0],
                "nom": row[1],
                "type": table,
                "chaleur": row[2],
                "couleur": row[3],
                "nb_utilisation": row[4] 
            })


    conn.close()
    
    return clothes_database

def Enregistrement_Image(source_path, destination_dir, nom_image):
    nom_image = nom_image + '.jpg'
    destination_path = os.path.join(destination_dir, nom_image)

    os.makedirs(destination_dir, exist_ok=True)

    shutil.copy2(source_path, destination_path)

    print(f"Image enregistrée à : {destination_path}")
    

def Creer_item(Image_path, color, typ, chal, name, mail='local'):
    item = {}
    clothes_database = BDD_total()
    clothes_bon_type = [c for c in clothes_database if c['type'] == typ]
    id_max = max(clothes_bon_type, key=lambda x: x['id'])['id'] if clothes_bon_type else 0

    item["id"] = id_max + 1
    item["couleur"] = color
    item["nom"] = name
    item["type"] = typ
    item["chaleur"] = chal
    item["nb_utilisation"] = 0
    item["utilisateur"] = mail
    clothes_database.append(item)
    # Nom de l'image (ex: "pull5.jpg")
    nom_image = typ + str(item["id"])
    destination_dir = "static/images"  # ✅ chemin relatif correct

    # Sauvegarde réelle de l'image
    #Enregistrement_Image(Image_path, destination_dir, nom_image)

    return item


def insert_clothing_item(item):
    """
    Insère un vêtement dans la base de données dressing.

    :param item: dict avec les clés suivantes :
        
id (int)
type (str) : nom de la table (ex: 'pull', 't_shirt', etc.)
couleur (str)
nom (str)
chaleur (int),
nb_utilisation (int),
"""
    try:
        conn = get_db_connection()

        with conn.cursor() as cursor:
            query = f"""
                INSERT INTO `{item['type']}` (id, couleur, nom, chaleur, utilisateur, nb_utilisation)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                item["id"],
                item["couleur"],
                item["nom"],
                item["chaleur"],
                item['utilisateur'],
                item["nb_utilisation"]
            )

            cursor.execute(query, values)
            conn.commit()
            print(f"✅ Insertion réussie dans la table {item['type']} avec l'ID {item['id']}")
    
    except pymysql.IntegrityError as e:
        print(f"⚠️ Erreur d'intégrité : {e}")
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion : {e}")
    finally:
        if conn:
            conn.close()

def Afficher_tt_dressing(item, vet_dej_chang, mail='local'):
    clothes_database = BDD_parmail(mail)
    tables = ['pull', 't_shirt', 'jupe', 'robe', 'pantalon', 'chemise', 'manteau', 'short',
              'couvre_chef', 'bonnet', 'haut_sport', 'bas_sport', 'chaussure_sport',
              'veste', 'chaussure', 'costume', 'collants', 'maillot_bain_homme', 'maillot_bain_femme']
    
    dress = {}

    for table in tables:
        clothes_bon_type = [c for c in clothes_database if c['type'] == table]
        clothes_bon_type = sorted(clothes_bon_type, key=lambda c: c['nb_utilisation'])
        if len(clothes_bon_type) == len(vet_dej_chang[table]):
            vet_dej_chang[table] = []
        items = []

        for c in clothes_bon_type:
            # Ne pas ajouter l'item passé en paramètre dans la liste s’il est déjà présent
            if c['id'] == item['id'] and c['type'] == item['type'] and c not in vet_dej_chang[table]:
                filename = c['type'].lower().replace(' ', '') + str(c['id']) + '.jpg'
                path = f"static/images/{filename}"
                if not os.path.exists(path):
                    filename = 'default.jpg'
                image_path = f"/static/images/{filename}"

                items.append({
                    "nom": c['nom'],
                    "image": image_path,
                    "id": c['id'],
                    "type": c['type']
                })

        # Si c'est la catégorie de l'item, l'ajouter en premier
        if table == item['type']:
            filename = item['type'].lower().replace(' ', '') + str(item['id']) + '.jpg'
            path = f"static/images/{filename}"
            if not os.path.exists(path):
                filename = 'default.jpg'
            image_path = f"/static/images/{filename}"

            item_formate = {
                "nom": item['nom'],
                "image": image_path,
                "id": item['id'],
                "type": item['type']
            }

            items.insert(0, item_formate)
            vet_dej_chang[table].append(item)

        dress[table] = items
        
    return dress, vet_dej_chang

def dictionnaire_en_liste_valeurs(dico):
    return list(dico.values())

def delete_clothing_item(id, table_name):
    """
    Supprime un vêtement de la base de données dressing.

    :param id: int, identifiant de l'élément à supprimer
    :param table_name: str, nom de la table (ex: 'pull', 't_shirt', etc.)
    :return: bool, True si la suppression a réussi
    """
    conn = None
    try:
        conn = get_db_connection()


        with conn.cursor() as cursor:
            # First check if item exists
            query = f"SELECT * FROM `{table_name}` WHERE id = %s"
            cursor.execute(query, (id,))
            if not cursor.fetchone():
                print(f"❗ Aucun élément avec l'ID {id} trouvé dans la table {table_name}.")
                return False

            # Then delete the item
            query = f"DELETE FROM `{table_name}` WHERE id = %s"
            cursor.execute(query, (id,))
            conn.commit()

            if cursor.rowcount > 0:
                print(f"🗑️ Suppression réussie de l'élément ID {id} dans la table {table_name}.")
                return True
            return False

    except Exception as e:
        print(f"❌ Erreur lors de la suppression : {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def changer_item_dans_tenue(tenue, index_item, mail='local', vetements_deja_changes=None):
    """
    Remplace un item dans une tenue par le prochain item du même type (circulairement)
    à partir de la base dressing, en évitant les vêtements déjà proposés pour ce type.

    :param tenue: liste d’items actuels
    :param index_item: index dans la tenue de l’élément à changer
    :param mail: identifiant utilisateur pour accéder au dressing
    :param vetements_deja_changes: dict {type: [items déjà proposés]}
    :return: (nouvelle_tenue, vetements_deja_changes)
    """
    # Initialisation robuste du dict de suivi
    tables = ['pull', 't_shirt', 'jupe', 'robe', 'pantalon', 'chemise', 'manteau', 'short',
              'couvre_chef', 'bonnet', 'haut_sport', 'bas_sport', 'chaussure_sport',
              'veste', 'chaussure', 'costume', 'collants', 'maillot_bain_homme', 'maillot_bain_femme']
    if vetements_deja_changes is None or not isinstance(vetements_deja_changes, dict):
        vetements_deja_changes = {table: [] for table in tables}
    else:
        # S'assurer que toutes les clés existent
        for table in tables:
            if table not in vetements_deja_changes:
                vetements_deja_changes[table] = []

    # Récupérer le dressing utilisateur
    clothes_database = BDD_parmail(mail)
    item_actuel = tenue[index_item]
    type_item = item_actuel['type']
    id_item = item_actuel['id']

    # Liste des items disponibles pour ce type, triés par nb_utilisation
    clothes_bon_type = [c for c in clothes_database if c['type'] == type_item]
    clothes_bon_type = sorted(clothes_bon_type, key=lambda c: c['nb_utilisation'])

    # Réinitialiser la liste si tous les vêtements ont été proposés
    if len(clothes_bon_type) == len(vetements_deja_changes[type_item]):
        vetements_deja_changes[type_item] = []

    # Exclure les vêtements déjà proposés
    deja_ids = set(v['id'] for v in vetements_deja_changes[type_item])
    candidats = [c for c in clothes_bon_type if c['id'] not in deja_ids]

    # Si plus de candidats, on recommence à zéro (sécurité)
    if not candidats:
        vetements_deja_changes[type_item] = []
        candidats = clothes_bon_type.copy()

    # Trouver le prochain vêtement (différent de l'actuel)
    prochain = None
    for c in candidats:
        if c['id'] != id_item:
            prochain = c
            break
    if not prochain:
        # Si tous les autres ont été proposés, reprendre le premier différent
        for c in clothes_bon_type:
            if c['id'] != id_item:
                prochain = c
                break
    if not prochain:
        # Si un seul vêtement, on ne change rien
        return tenue, vetements_deja_changes

    # Mettre à jour la tenue et la liste des déjà changés
    tenue[index_item] = {
        "nom": prochain['nom'],
        "image": f"/static/images/{prochain['type'].lower().replace(' ', '')}{prochain['id']}.jpg"
            if os.path.exists(f"static/images/{prochain['type'].lower().replace(' ', '')}{prochain['id']}.jpg")
            else "/static/images/default.jpg",
        "id": prochain['id'],
        "type": prochain['type']
    }
    vetements_deja_changes[type_item].append(prochain)

    return tenue, vetements_deja_changes

def supprimer_vetement(id, user_email):
    """Supprime un vêtement de la base de données SQL et son image associée"""
    try:
        # Connexion à la base de données
        conn = get_db_connection()

        
        # Trouver le type du vêtement avant de le supprimer
        with conn.cursor() as cursor:
            for table in ['pull', 't_shirt', 'pantalon', 'robe', 'jupe', 'chemise', 'manteau', 
                         'short', 'bonnet', 'costume', 'chaussure', 'haut_sport', 'bas_sport', 
                         'chaussure_sport', 'maillot_bain_homme', 'maillot_bain_femme']:
                cursor.execute(f"SELECT * FROM {table} WHERE id = %s AND utilisateur = %s", (id, user_email))
                if cursor.fetchone():
                    # Suppression de l'entrée dans la base de données
                    cursor.execute(f"DELETE FROM {table} WHERE id = %s AND utilisateur = %s", (id, user_email))
                    conn.commit()
                    
                    # Suppression de l'image associée avec chemin corrigé
                    image_path = os.path.join('static', 'images', f"{table}{id}.jpg")
                    try:
                        if os.path.exists(image_path):
                            os.remove(image_path)
                            print(f"✅ Image supprimée : {image_path}")
                        else:
                            print(f"⚠️ Image non trouvée : {image_path}")
                    except Exception as img_err:
                        print(f"❌ Erreur lors de la suppression de l'image : {img_err}")
                    
                    return True
        
        print(f"❌ Aucun vêtement trouvé avec l'ID {id} pour l'utilisateur {user_email}")
        return False
        
    except Exception as e:
        print(f"❌ Erreur lors de la suppression : {e}")
        return False
        
    finally:
        if conn:
            conn.close()

def increment_usage_count(id,table , user_email):
    """Incrémente le compteur d'utilisation d'un vêtement"""
    conn = None
    try:
        conn = pymysql.connect(host='127.0.0.1', user='root', password='mdpsql', database='clothes')
        
        with conn.cursor() as cursor:
            # Chercher le vêtement dans toutes les tables

                try:
                    # Vérifier si le vêtement existe et appartient à l'utilisateur
                    cursor.execute(f"SELECT nb_utilisation FROM {table} WHERE id = %s AND utilisateur = %s", 
                                 (id, user_email))
                    result = cursor.fetchone()
                    
                    if result:
                        # Incrémenter le compteur
                        cursor.execute(f"UPDATE {table} SET nb_utilisation = nb_utilisation + 1 WHERE id = %s AND utilisateur = %s", 
                                     (id, user_email))
                        conn.commit()
                        print(f"✅ Utilisation incrémentée pour l'item {id} dans {table}")
                        return True
                except Exception as e:
                    print(f"Erreur pour la table {table}: {str(e)}")
                    
                    
        print(f"❌ Aucun vêtement trouvé avec l'ID {id} pour l'utilisateur {user_email}")
        return False
        
    except Exception as e:
        print(f"Erreur d'incrémentation : {str(e)}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()

def BDD_parmail_use_croiss(couleur = '', mail='local'): 
    conn = get_db_connection()
    cursor = conn.cursor()

    tables = ['pull', 't_shirt', 'jupe', 'robe', 'pantalon', 'chemise', 'manteau', 'short',
              'couvre_chef', 'bonnet', 'haut_sport', 'bas_sport', 'chaussure_sport',
              'veste', 'chaussure', 'costume', 'collants', 'maillot_bain_homme', 'maillot_bain_femme']

    clothes_database = []

    for table in tables:
        if couleur == '':
            cursor.execute(f"""
                SELECT id, nom, chaleur, couleur, nb_utilisation 
                FROM {table} 
                WHERE utilisateur = %s 
                ORDER BY nb_utilisation DESC
            """, (mail,))
        else:
            cursor.execute(f"""
                SELECT id, nom, chaleur, couleur, nb_utilisation 
                FROM {table} 
                WHERE utilisateur = %s AND couleur = %s
                ORDER BY nb_utilisation DESC
            """, (mail, couleur))

        rows = cursor.fetchall()
        for row in rows:
            clothes_database.append({
                "id": row[0],
                "nom": row[1],
                "type": table,
                "chaleur": row[2],
                "couleur": row[3],
                "nb_utilisation": row[4]
            })

    conn.close()
    return clothes_database

def BDD_parmail_use_decroiss(couleur = '', mail='local'): 
    conn = get_db_connection()
    cursor = conn.cursor()

    tables = ['pull', 't_shirt', 'jupe', 'robe', 'pantalon', 'chemise', 'manteau', 'short',
              'couvre_chef', 'bonnet', 'haut_sport', 'bas_sport', 'chaussure_sport',
              'veste', 'chaussure', 'costume', 'collants', 'maillot_bain_homme', 'maillot_bain_femme']

    clothes_database = []

    for table in tables:
        if couleur == '':
            cursor.execute(f"""
                SELECT id, nom, chaleur, couleur, nb_utilisation 
                FROM {table} 
                WHERE utilisateur = %s 
                ORDER BY nb_utilisation DESC
            """, (mail,))
        else:
            cursor.execute(f"""
                SELECT id, nom, chaleur, couleur, nb_utilisation 
                FROM {table} 
                WHERE utilisateur = %s AND couleur = %s
                ORDER BY nb_utilisation DESC
            """, (mail, couleur))

        rows = cursor.fetchall()
        for row in rows:
            clothes_database.append({
                "id": row[0],
                "nom": row[1],
                "type": table,
                "chaleur": row[2],
                "couleur": row[3],
                "nb_utilisation": row[4]
            })

    conn.close()
    return clothes_database

def BDD_parmail_par_couleur(coul, mail='local'):

    conn = get_db_connection()
    cursor = conn.cursor()

    tables = ['pull', 't_shirt', 'jupe', 'robe', 'pantalon', 'chemise', 'manteau', 'short',
              'couvre_chef', 'bonnet', 'haut_sport', 'bas_sport', 'chaussure_sport',
              'veste', 'chaussure', 'costume', 'collants', 'maillot_bain_homme', 'maillot_bain_femme']

    all_clothes = []

    for table in tables:
        cursor.execute(f"""
            SELECT id, nom, chaleur, couleur, nb_utilisation 
            FROM {table} 
            WHERE utilisateur = %s AND couleur = %s
            ORDER BY nb_utilisation ASC
        """, (mail, coul))

        rows = cursor.fetchall()
        for row in rows:
            all_clothes.append({
                "id": row[0],
                "nom": row[1],
                "type": table,
                "chaleur": row[2],
                "couleur": row[3],
                "nb_utilisation": row[4]
            })

    conn.close()

    return all_clothes

if __name__ == "__main__":
    print(f"{len(clothes_database)} articles chargés.")
