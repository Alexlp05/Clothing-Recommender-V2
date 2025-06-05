import os
from database import BDD_parmail
from google_calendar_service import get_events
from collections import Counter

def couleur_score(couleur, couleurs_utilisees):
    """
    Calcule un score pour la couleur en fonction de la diversité et de l'harmonie.
    Plus la couleur est différente des couleurs déjà utilisées, plus le score est élevé.
    """
    if not couleurs_utilisees:
        return 1.0  # Favorise la première couleur
    # Bonus si la couleur n'est pas encore utilisée
    if couleur not in couleurs_utilisees:
        return 1.5
    # Sinon, pénalise la répétition
    return 0.7

def EstPlusProche(clothes, indice_chaleur, couleurs_utilisees):
    """
    Sélectionne l'élément de clothes le plus proche de l'indice_chaleur,
    en tenant compte du nb_utilisation et des couleurs déjà utilisées.
    Les couleurs différentes sont favorisées.
    """
    if not clothes:
        return None, '/static/images/default.jpg', None, None, None

    best_score = float('-inf')
    best_item = clothes[0]

    for clothing in clothes:
        ecart_chaleur = abs(clothing["chaleur"] - indice_chaleur)
        score_chaleur = max(0, 10 - ecart_chaleur)  # Plus proche, mieux c'est
        score_utilisation = -clothing["nb_utilisation"]  # Moins utilisé, mieux c'est
        score_couleur = couleur_score(clothing["couleur"], couleurs_utilisees)
        score_total = score_chaleur + score_utilisation + score_couleur * 2  # Couleur plus importante

        if score_total > best_score:
            best_score = score_total
            best_item = clothing

    filename = best_item['type'].lower().replace(' ', '') + str(best_item['id']) + '.jpg'
    path = f"static/images/{filename}"
    if not os.path.exists(path):
        filename = 'default.jpg'
    image_path = f"/static/images/{filename}"

    return best_item['nom'], image_path, best_item['couleur'], best_item['id'], best_item['type']

def EstPlusProche2(clothes, indice_chaleur, couleurs_utilisees):
    """
    Variante expressive : favorise la diversité de couleurs et l'originalité.
    """
    if not clothes:
        return None, '/static/images/default.jpg', None, None, None

    couleur_counts = Counter(couleurs_utilisees)
    best_score = float('-inf')
    best_item = clothes[0]

    for clothing in clothes:
        ecart_chaleur = abs(clothing["chaleur"] - indice_chaleur)
        score_chaleur = max(0, 10 - ecart_chaleur)
        score_utilisation = -clothing["nb_utilisation"]
        # Favorise les couleurs peu utilisées
        score_couleur = 2.0 if couleur_counts[clothing["couleur"]] == 0 else 1.0 / (1 + couleur_counts[clothing["couleur"]])
        score_total = score_chaleur + score_utilisation + score_couleur * 3  # Couleur très importante

        if score_total > best_score:
            best_score = score_total
            best_item = clothing

    filename = best_item['type'].lower().replace(' ', '') + str(best_item['id']) + '.jpg'
    path = f"static/images/{filename}"
    if not os.path.exists(path):
        filename = 'default.jpg'
    image_path = f"/static/images/{filename}"

    return best_item['nom'], image_path, best_item['couleur'], best_item['id'], best_item['type']

def reco_to_2_classes(recommendations):
    if not recommendations:
        return 2, 1  # valeurs par défaut
    retour1 = 2  # valeur par défaut
    retour2 = 1  # valeur par défaut

    if "pro" in recommendations:
        retour1 = 3
        retour2 = 2
        if "sport" in recommendations:
            retour2 = 4
        elif "plage" in recommendations:
            retour2 = 5

    elif "sport" in recommendations:
        retour1 = 4
        if "plage" in recommendations:
            retour2 = 5

    elif "plage" in recommendations:
        retour1 = 5
    return retour1, retour2

def get_clothes_types(genre, temperature, classe):
    indice_chaleur = (40 - temperature)/5
    if classe == 4:
        return ['bas_sport', 't_shirt', 'haut_sport', 'chaussure_sport', indice_chaleur] if temperature <= 20 else \
                ['bas_sport', 't_shirt', 'chaussure_sport', indice_chaleur]
    if genre == "homme":
        if classe == 5:
            return ['chaussure_sport','maillot_bain_homme','t_shirt',indice_chaleur]
        if temperature <= 10:
            return ['pull', 'pantalon', 't_shirt', 'manteau', 'chaussure', indice_chaleur] if classe == 1 else \
                   ['chemise', 'pantalon', 'manteau', 'chaussure', indice_chaleur] if classe == 2 else \
                   ['costume', 'chemise', 'manteau', 'chaussure', indice_chaleur]
        elif temperature <= 20:
            return ['pantalon', 't_shirt', 'pull', 'chaussure', indice_chaleur] if classe == 1 else \
                   ['pantalon', 'chemise', 'veste', 'chaussure', indice_chaleur] if classe == 2 else \
                   ['costume', 'chemise', 'manteau', 'chaussure', indice_chaleur]
        elif temperature <= 30:
            return ['pull', 't_shirt', 'pantalon', 'chaussure', indice_chaleur] if classe == 1 else \
                   ['veste', 'pantalon', 'chemise', 'chaussure', indice_chaleur] if classe == 2 else \
                   ['costume', 'chemise', 'chaussure', indice_chaleur]
        else:
            return ['t_shirt', 'short', 'chaussure', indice_chaleur] if classe == 1 else \
                   ['chemise', 'short', 'chaussure', indice_chaleur] if classe == 2 else \
                   ['chemise', 'short', 'chaussure', indice_chaleur]

    elif genre == "femme":
        if classe == 5:
            return ['chaussure_sport','maillot_bain_femme','t_shirt',indice_chaleur]
        if temperature <= 10:
            return ['pull', 'pantalon', 't_shirt', 'manteau', 'chaussure', indice_chaleur] if classe == 1 else \
                   ['chemise', 'jupe', 'collants', 'manteau', 'chaussure', indice_chaleur] if classe == 2 else \
                   ['chemise', 'costume', 'manteau', 'chaussure', indice_chaleur]
        elif temperature <= 20:
            return ['t_shirt', 'pantalon', 'manteau', 'chaussure', indice_chaleur] if classe == 1 else \
                   ['veste', 'collants', 'robe', 'chaussure', indice_chaleur] if classe == 2 else \
                   ['chemise', 'collants','jupe', 'veste', 'chaussure', indice_chaleur]
        elif temperature <= 30:
            return ['veste', 'pantalon', 't_shirt', 'chaussure', indice_chaleur] if classe == 1 else \
                   ['robe', 'collants', 'chaussure', indice_chaleur] if classe == 2 else \
                   ['veste', 'jupe', 'chemise', 'chaussure', indice_chaleur]
        else:
            return ['short', 't_shirt', 'chaussure', indice_chaleur] if classe == 1 else \
                   ['robe', 'chaussure', indice_chaleur] if classe == 2 else \
                   ['jupe', 'chemise', 'chaussure', indice_chaleur]
                   
def adjust_for_weather(type_clothes, condition, temperature):
    if not condition:
        return type_clothes

    c = condition.lower()
    if ("rain" in c) and temperature <= 20:
        if "manteau" not in type_clothes and "veste" not in type_clothes and "haut_sport" not in type_clothes:
            type_clothes.insert(-1, "manteau")
        if "veste" in type_clothes and "couvre_chef" not in type_clothes and "bonnet" not in type_clothes:
            type_clothes.insert(-1, "couvre_chef")
        type_clothes[-1] += 1

    elif ("rain" in c) and temperature > 20:
        if "veste" not in type_clothes and "costume" not in type_clothes and "manteau" not in type_clothes:
            type_clothes.insert(-1, "veste")
        type_clothes[-1] += 1

    if "snow" in c and "couvre_chef" not in type_clothes and "bonnet" not in type_clothes:
        type_clothes.insert(-1, "bonnet")
        type_clothes[-1] += 1

    if "sun" in c and all(x not in c for x in ["rain", "cloud", "snow"]) and "couvre_chef" not in type_clothes:
        type_clothes.insert(-1, "couvre_chef")
        type_clothes[-1] -= 1


    return type_clothes

def lister_types_vetements(clothes_database):

    types = set()  # Utilisation d’un set pour éviter les doublons

    for vetement in clothes_database:

        types.add(vetement["type"])

    return types

def recommend_clothes(temperature, condition, genre, recommendations, mail='local', humeur = 'discret', classe1=0, classe2=0):
    clothes_database = BDD_parmail(mail)
    total_types = lister_types_vetements(clothes_database)
    if classe1 == 0 and classe2 == 0:
        classe1, classe2 = reco_to_2_classes(recommendations)
 
    recommended_clothes = []

    for classe in [classe1, classe2]:
        recommended_clothes_c = []
        couleurs_utilisees = []
        type_clothes = get_clothes_types(genre, temperature, classe)
        type_clothes = adjust_for_weather(type_clothes, condition, temperature)

       
        if "costume" in type_clothes and "costume" not in total_types:
            type_clothes.insert(-1, "pantalon")
            type_clothes.insert(-1, "veste")

        indice_chaleur = type_clothes[-1]
        for type in type_clothes[:-1]:
            clothes_bon_type = [c for c in clothes_database if c['type'] == type]
            if clothes_bon_type:
                if humeur == 'discret':
                    nom, image, couleur, ide, typ = EstPlusProche(clothes_bon_type, indice_chaleur,couleurs_utilisees)
                if humeur == 'expressif':
                    nom, image, couleur, ide, typ = EstPlusProche2(clothes_bon_type, indice_chaleur,couleurs_utilisees)
                recommended_clothes_c.append({"nom": nom, "image": image, "id": ide, "type":typ})
                couleurs_utilisees.append(couleur)
        recommended_clothes.append(recommended_clothes_c)
    return recommended_clothes