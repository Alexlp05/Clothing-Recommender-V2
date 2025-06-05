import os
import traceback  # Added missing import
from flask import Flask, render_template, request, redirect, url_for, flash, session
from weather_service import get_weather
from google_calendar_service import authenticate_user, get_events, analyze_schedule_clothing
from recommendation_engine import recommend_clothes
from werkzeug.utils import secure_filename
from datetime import datetime
from pytz import timezone
from database import Creer_item, insert_clothing_item
from google.oauth2.credentials import Credentials
from flask_dance.contrib.google import make_google_blueprint, google
from google.auth.transport.requests import Request
from flask import jsonify
from io import BytesIO
import base64
from database import BDD_total, BDD_parmail, delete_clothing_item, supprimer_vetement, increment_usage_count
from datetime import timedelta
import time
from dotenv import load_dotenv
from PIL import Image
from flask import jsonify, request
from database import changer_item_dans_tenue, BDD_parmail_use_croiss, BDD_parmail_use_decroiss, BDD_parmail_par_couleur

load_dotenv()

app = Flask(__name__)

app.config.update(
    PERMANENT_SESSION_LIFETIME=timedelta(days=1),
    SESSION_REFRESH_EACH_REQUEST=True,
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    MAX_CONTENT_LENGTH=64 * 1024 * 1024,  # 64MB pour l'upload initial
    UPLOAD_FOLDER='static/images',
    ALLOWED_EXTENSIONS={'jpg', 'jpeg', 'png'}
)

# Check if the API key is available
weather_api_key = "c6e9868daeba44a3a56110247251905"
if not weather_api_key:
    raise RuntimeError("La variable d'environnement WEATHER_API_KEY n'est pas définie.")

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


app.secret_key = os.getenv('FLASK_SECRET_KEY', 'une_chaine_secrete_aleatoire_et_suffisamment_longue')

# ADD THESE LINES:
app.config['GOOGLE_OAUTH_CLIENT_ID'] = os.getenv('GOOGLE_OAUTH_CLIENT_ID', '1067722559381-5nk22fq73q37dq831n9qhjhg2j5lgtc6.apps.googleusercontent.com')
app.config['GOOGLE_OAUTH_CLIENT_SECRET'] = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET', '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')

# OAuth Google Blueprint
google_bp = make_google_blueprint(
    client_id=app.config['GOOGLE_OAUTH_CLIENT_ID'], # Use the config variable here too for consistency
    client_secret=app.config['GOOGLE_OAUTH_CLIENT_SECRET'], # Use the config variable here too
    scope=[
        "openid",
        "email", 
        "profile", 
        "https://www.googleapis.com/auth/calendar.readonly"
    ],
    offline=True,
    reprompt_consent=True
)
# ... rest of your code


app.register_blueprint(google_bp, url_prefix="/login")

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKEN_DIR = 'tokens'
os.makedirs(TOKEN_DIR, exist_ok=True)

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

list_vet = {}

def load_user_credentials():
    if not google.authorized:
        return None
        
    try:
        # Création directe des credentials depuis le token Google
        return Credentials(
            token=google.token["access_token"],
            refresh_token=google.token.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=app.config['GOOGLE_OAUTH_CLIENT_ID'],
            client_secret=app.config['GOOGLE_OAUTH_CLIENT_SECRET'],
            scopes=SCOPES
        )
    except Exception as e:
        print(f"❌ Erreur credentials: {str(e)}")
        return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image_path, max_size_mb=5, min_quality=30):
    """Redimensionne une image avec gestion sécurisée des fichiers"""
    temp_path = None
    temp_img = None
    
    try:
        if not os.path.exists(image_path):
            print(f"❌ Fichier non trouvé: {image_path}")
            return False
            
        # Créer un nom de fichier temporaire unique
        temp_path = f"{image_path}.tmp_{int(time.time())}"
        
        # Ouvrir l'image et appliquer la rotation EXIF
        with Image.open(image_path) as img:
            # Corriger l'orientation EXIF
            try:
                exif = img._getexif()
                if exif:
                    orientation = exif.get(274)  # 274 est le tag pour l'orientation
                    if orientation:
                        rotate_values = {
                            3: 180,
                            6: 270,
                            8: 90
                        }
                        if orientation in rotate_values:
                            img = img.rotate(rotate_values[orientation], expand=True)
            except:
                pass  # Si pas d'EXIF, on continue normalement
            
            # Convertir en RGB si nécessaire
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Conserver une copie en mémoire
            temp_img = img.copy()
            
        # Taille actuelle
        current_size = os.path.getsize(image_path) / (1024 * 1024)
        print(f"📏 Taille actuelle: {current_size:.2f}MB")
        
        # Dimensions originales
        width, height = temp_img.size
        print(f"📐 Dimensions originales: {width}x{height}")
        
        # Redimensionner si nécessaire
        max_dimension = 2000
        if width > max_dimension or height > max_dimension:
            ratio = min(max_dimension/width, max_dimension/height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            temp_img = temp_img.resize((new_width, new_height), Image.LANCZOS)
            print(f"📏 Nouvelles dimensions: {new_width}x{new_height}")
        
        # Essayer différentes qualités
        quality = 95
        while quality >= min_quality:
            try:
                # Sauvegarder en temporaire
                temp_img.save(temp_path, 'JPEG', 
                            quality=quality,
                            optimize=True,
                            progressive=True)
                
                new_size = os.path.getsize(temp_path) / (1024 * 1024)
                print(f"📦 Taille avec qualité {quality}%: {new_size:.2f}MB")
                
                if new_size <= max_size_mb:
                    # Fermer l'image avant manipulation des fichiers
                    temp_img = None
                    
                    # Sous Windows, on doit d'abord supprimer la destination
                    if os.path.exists(image_path):
                        os.remove(image_path)
                    
                    # Puis renommer le temporaire
                    os.rename(temp_path, image_path)
                    print(f"✅ Image optimisée avec succès")
                    print(f"   Taille finale: {new_size:.2f}MB (qualité: {quality}%)")
                    return True
                
                os.remove(temp_path)
            except Exception as save_error:
                print(f"❌ Erreur lors de la sauvegarde: {save_error}")
            
            quality -= 5
        
        print("❌ Impossible d'atteindre la taille cible")
        return False
        
    except Exception as e:
        print(f"❌ Erreur de redimensionnement: {str(e)}")
        return False
        
    finally:
        # Nettoyage
        if temp_img:
            temp_img = None
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

def process_user_request(credentials, city, genre, style, user_email):
    """Centralise la logique de traitement des requêtes"""
    result = {
        'events': [],
        'schedule_recommendations': [],
        'recommendation1': [],
        'recommendation2': [],
        'temperature': None,
        'condition': None,
        'icon': None
    }
    
    try:
        # Récupérer les événements
        events = get_events(credentials) or []
        schedule_recommendations = analyze_schedule_clothing(events) or []
        
        result.update({
            'events': events,
            'schedule_recommendations': schedule_recommendations
        })
        
        # Récupérer la météo
        weather_data = get_weather(city, weather_api_key)
        if weather_data and all(x is not None for x in weather_data):
            temp, cond, icon = weather_data
            result.update({
                'temperature': temp,
                'condition': cond,
                'icon': icon
            })
            
            # Générer les recommandations
            recommendations = recommend_clothes(
                temp,
                cond,
                genre,
                schedule_recommendations,
                user_email,
                style
            ) or []
            
            if recommendations:
                result.update({
                    'recommendation1': recommendations[0] if len(recommendations) > 0 else [],
                    'recommendation2': recommendations[1] if len(recommendations) > 1 else []
                })
        
    except Exception as e:
        print(f"❌ Erreur dans process_user_request: {e}")
        
    return result

def save_credentials(email, credentials):
    """Sauvegarde sécurisée des credentials"""
    token_path = os.path.join(TOKEN_DIR, f"{email}.json")
    try:
        with open(token_path, 'w') as f:
            f.write(credentials.to_json())
    except IOError as e:
        print(f"Erreur sauvegarde token : {e}")

@app.template_filter('datetimeformat')
def datetimeformat(value):
    if value:
        dt = datetime.fromisoformat(value)
        local_tz = timezone("Europe/Paris")
        local_time = dt.astimezone(local_tz)
        return local_time.strftime('%d %b %Y, %H:%M')
    return value

def get_user_events_and_recommendations(credentials):
    """Factorisation de la récupération d’événements et analyse"""
    events = []
    schedule_recommendations = []
    try:
        events = get_events(credentials)
        schedule_recommendations = analyze_schedule_clothing(events)
    except Exception as e:
        print(f"Erreur Google Calendar : {e}")
    return events, schedule_recommendations

@app.route('/', methods=['GET', 'POST'])
def index():
    if not google.authorized:
        return redirect(url_for('login'))

    try:
        # 1. Récupération des infos utilisateur
        resp = google.get('/oauth2/v2/userinfo')
        if not resp.ok:
            raise ValueError(f"Erreur API Google ({resp.status_code})")
        user_info = resp.json()
        user_email = user_info['email']

        # 2. Mise à jour de la session
        session.update({
            'user_email': user_email,
            'user_name': user_info.get('name', user_email.split('@')[0]),
            '_fresh': True,
            '_last_activity': datetime.now().isoformat()
        })

        # 3. Gestion des credentials
        credentials = load_user_credentials()
        if not credentials:
            flash("Session expirée", "warning")
            return redirect(url_for('logout'))

        # 4. Initialisation des valeurs par défaut
        default_values = {
            'error_message': None,
            'recommendation1': [],
            'recommendation2': [],
            'temperature': None,
            'condition': None,
            'icon': None,
            'events': [],
            'city': request.form.get('city', ''),
            'genre': request.form.get("genre", "femme").lower(),
            'style': request.form.get("style", "discret"),
            'schedule_recommendations': []
        }

        # 5. Traitement POST avec ville
        if request.method == 'POST' and default_values['city']:
            session['vetements_deja_changes'] = None
            session['vetements_deja_changes2'] = None
            try:
                result = process_user_request(
                    credentials,
                    default_values['city'],
                    default_values['genre'],
                    default_values['style'],
                    user_email
                )
                default_values.update(result)
            except Exception as e:
                default_values['error_message'] = f"Erreur : {str(e)}"
                print(f"Erreur traitement : {e}")
        else:
            # GET : afficher le planning même sans ville (utiliser une valeur par défaut)
            ville = default_values['city'] or "Paris"
            try:
                result = process_user_request(
                    credentials,
                    ville,
                    default_values['genre'],
                    default_values['style'],
                    user_email
                )
                default_values.update(result)
                # Déterminer la ville par défaut basée sur la localisation IP si aucune ville n'est fournie
                if not default_values['city']:
                    try:
                        ip_info = requests.get("https://ipinfo.io/json", timeout=2).json()
                        ville_ip = ip_info.get("city", "Paris")
                        default_values['city'] = ville_ip
                    except Exception as e:
                        print(f"Erreur détection ville par IP: {e}")
                        default_values['city'] = ville
                else:
                    default_values['city'] = ville
            except Exception as e:
                default_values['error_message'] = f"Erreur : {str(e)}"
                print(f"Erreur traitement : {e}")

        # 6. Rendu du template avec les valeurs
        return render_template('index.html', 
                            avg_temperature=default_values['temperature'],
                            **default_values)

    except Exception as e:
        print(f"ERREUR SYSTÈME : {str(e)}")
        traceback.print_exc()
        session.clear()
        return redirect(url_for('login'))

@app.route('/change_item_in_outfit', methods=['POST'])
def change_item_in_outfit():
    try:
        data = request.get_json()
        tenue = data.get('tenue')
        index = data.get('index')
        user_email = session.get('user_email', 'local')

        # Récupérer ou initialiser la liste des déjà changés
        vetements_deja_changes = session.get('vetements_deja_changes', None)

        recommendation, vetements_deja_changes = changer_item_dans_tenue(
            tenue, index, mail=user_email, vetements_deja_changes=vetements_deja_changes
        )

        # Mettre à jour la session
        session['vetements_deja_changes'] = vetements_deja_changes

        return jsonify({'nouvelle_tenue': recommendation})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/change_item_in_outfit2', methods=['POST'])
def change_item_in_outfit2():
    try:
        data = request.get_json()
        tenue = data.get('tenue')
        index = data.get('index')
        user_email = session.get('user_email', 'local')

        # Récupérer ou initialiser la liste des déjà changés pour la tenue 2
        vetements_deja_changes2 = session.get('vetements_deja_changes2', None)

        recommendation, vetements_deja_changes2 = changer_item_dans_tenue(
            tenue, index, mail=user_email, vetements_deja_changes=vetements_deja_changes2
        )

        # Mettre à jour la session
        session['vetements_deja_changes2'] = vetements_deja_changes2

        return jsonify({'nouvelle_tenue': recommendation})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/select_outfit', methods=['POST'])
def select_outfit():
    if 'user_email' not in session:
        flash('Veuillez vous connecter pour sélectionner une tenue')
        return redirect(url_for('login'))
        
    user_email = session.get('user_email')
    outfit_data = request.form.get('outfit_items')
    
    if not outfit_data:
        flash('Aucune tenue sélectionnée')
        return redirect(url_for('index'))
        
    try:
        # Convertir la chaîne en liste de dictionnaires
        import ast
        outfit_items = ast.literal_eval(outfit_data)
        
        if not isinstance(outfit_items, list):
            raise ValueError("Format de données incorrect")
            
        # Incrémenter l'utilisation pour chaque vêtement
        for item in outfit_items:
            if isinstance(item, dict) and 'id' in item and 'type' in item:
                try:
                    increment_usage_count(item['id'], item['type'], user_email)
                    print(f"✅ Incrémentation pour {item['type']} #{item['id']}")
                except Exception as e:
                    print(f"❌ Erreur d'incrémentation pour {item}: {str(e)}")
                    
        flash('✨ Utilisation de la tenue enregistrée!')
        
    except Exception as e:
        print(f"❌ Erreur lors de la sélection de la tenue: {str(e)}")
        flash('Une erreur est survenue lors de l\'enregistrement')
        
    return redirect(url_for('index'))

@app.errorhandler(413)
def request_entity_too_large(error):
    flash("Le fichier est trop volumineux. Taille maximum: 16MB")
    return redirect(url_for('upload_file')), 413

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    message = None
    user_email = session.get('user_email')
    
    if request.method == 'POST':
        if 'user_email' not in session:
            return redirect(url_for('login'))
        
        if 'file' not in request.files:
            return render_template('upload.html', message='Aucun fichier ou image reçu.')
            
        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', message='Aucun fichier choisi.')
            
        if not allowed_file(file.filename):
            return render_template('upload.html', message='Seuls les fichiers JPG, JPEG et PNG sont autorisés.')
            
        try:
            # Récupérer les données du formulaire
            couleur_vetement = request.form.get('couleur', '').strip()
            type_vetement = request.form.get('type', '').strip()
            nom_vetement = request.form.get('nom', '').strip()
            try:
                chaleur_vetement = int(request.form.get('chaleur', 0))
            except ValueError:
                chaleur_vetement = 0

            # Validation des données requises
            if not all([type_vetement, couleur_vetement]):
                return render_template('upload.html', 
                                    message='Le type et la couleur sont requis.')

            # Sauvegarder le fichier temporairement
            filename = secure_filename(file.filename)
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_path)
            
            # Redimensionner AVANT de créer l'item
            if not resize_image(temp_path):
                raise ValueError("Impossible de redimensionner l'image à une taille acceptable")
            
            # Créer l'item avec l'image redimensionnée
            item = Creer_item(temp_path, couleur_vetement, type_vetement, 
                            chaleur_vetement, nom_vetement, user_email)
            
            # Renommer avec l'ID généré
            new_filename = f"{item['type']}{item['id']}.jpg"
            new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            os.rename(temp_path, new_path)
            
            # Mettre à jour le chemin et sauvegarder
            item['image_path'] = new_path
            insert_clothing_item(item)
            message = f'✨ Article ajouté avec succès!'
                
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
            message = f"Erreur lors du traitement: {str(e)}"
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass

    return render_template('upload.html', message=message)


@app.route('/camera', methods=['GET'])
def camera():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('camera.html')


@app.route('/login')
def login():
    if google.authorized:
        try:
            resp = google.get('/oauth2/v2/userinfo')
            if resp.ok:
                return redirect(url_for('index'))  # Évite la boucle
        except:
            pass
            
    return redirect(url_for('google.login'))

@app.route('/logout')
def logout():
    email = session.get('user_email')
    if email:
        token_path = os.path.join(TOKEN_DIR, f"{email}.json")
        try:
            if os.path.exists(token_path):
                os.remove(token_path)
        except Exception as e:
            print(f"⚠️ Erreur suppression token: {str(e)}")
    
    session.clear()
    if 'google' in globals():
        google.token = None
    return redirect(url_for('login'))

from pprint import pprint
import requests

@app.route('/debug_token')
def debug_token():
    if not google.authorized:
        return "Non connecté"
    token = google.token
    pprint(token)
    return "Token affiché dans la console."

@app.route('/debug_calendar')
def debug_calendar():
    debug_info = {
        'user_email': session.get('user_email'),
        'google_authorized': google.authorized if 'google' in globals() else False,
        'token_exists': False,
        'token_details': None,
        'credentials_valid': False,
        'events_count': 0,
        'events_error': None,
        'credentials_error': None
    }
    
    # Vérifier si l'utilisateur est connecté
    user_email = session.get('user_email')
    if user_email:
        token_path = os.path.join(TOKEN_DIR, f"{user_email}.json")
        debug_info['token_exists'] = os.path.exists(token_path)
        
        # Tenter de charger les identifiants
        try:
            credentials = load_user_credentials()
            if credentials:
                debug_info['credentials_valid'] = True
                debug_info['token_details'] = {
                    'valid': not credentials.expired,
                    'expires_at': credentials.expiry.isoformat() if hasattr(credentials, 'expiry') else 'Unknown'
                }
                
                # Tenter de récupérer les événements
                try:
                    events = get_events(credentials)
                    debug_info['events_count'] = len(events)
                    debug_info['events'] = events[:3]  # Afficher les 3 premiers événements seulement
                except Exception as e:
                    debug_info['events_error'] = str(e)
            else:
                debug_info['credentials_error'] = "Impossible de charger les identifiants"
        except Exception as e:
            debug_info['credentials_error'] = str(e)
    
    return render_template('debug.html', debug_info=debug_info)

@app.route('/delete/<string:type>/<int:id>')
def delete_clothing(type, id):
    if 'user_email' not in session:
        return redirect(url_for('login'))
        
    user_email = session.get('user_email')
    try:
        # Delete from database first
        if delete_clothing_item(id, type):
            # If database deletion succeeded, try to delete the image
            image_path = os.path.join('static', 'images', f"{type}{id}.jpg")
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    print(f"✅ Image supprimée : {image_path}")
                except Exception as img_err:
                    print(f"❌ Erreur lors de la suppression de l'image : {img_err}")
            else:
                print(f"⚠️ Image non trouvée : {image_path}")
            flash('Vêtement supprimé avec succès!')
        else:
            flash('Vêtement non trouvé ou non autorisé')
            
    except Exception as e:
        print(f"Erreur de suppression: {str(e)}")
        flash('Erreur lors de la suppression du vêtement')
        
    return redirect(url_for('wardrobe'))

@app.route('/wardrobe')
def wardrobe():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    user_email = session.get('user_email')
    filtre = request.args.get('filtre')
    valeur = request.args.get('valeur', '').strip()
    # Récupérer tous les vêtements de l'utilisateur
    if filtre == "croissant":
        clothes = BDD_parmail_use_croiss(user_email)
    elif filtre == "decroissant":
        clothes = BDD_parmail_use_decroiss(user_email)
    elif filtre == "couleur" and valeur:
        clothes = BDD_parmail_par_couleur(valeur, user_email)
    else:
        clothes = BDD_parmail(user_email)

    clothes_by_type = {}
    for item in clothes:
        if item['type'] not in clothes_by_type:
            clothes_by_type[item['type']] = []
        clothes_by_type[item['type']].append(item)

    return render_template('wardrobe.html', 
                         clothes_by_type=clothes_by_type, 
                         total_items=len(clothes))

if __name__ == '__main__':
    app.run(debug=True)