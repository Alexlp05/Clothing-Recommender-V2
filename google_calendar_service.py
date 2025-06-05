from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKEN_DIR = 'tokens'
import logging

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s: %(message)s')

def authenticate_user():
    try:
        logging.info("Début du processus d'authentification")

        if not os.path.exists(TOKEN_DIR):
            os.makedirs(TOKEN_DIR)

        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        credentials = flow.run_local_server(port=0, prompt='consent')

        user_email = credentials.id_token['email']

        token_path = os.path.join(TOKEN_DIR, f"{user_email}.json")
        with open(token_path, 'w') as token_file:
            token_file.write(credentials.to_json())

        if os.path.exists(token_path):
            print(f"Token sauvegardé dans {token_path}")
        else:
            print("Erreur : token non sauvegardé")

        logging.info(f"Authentification réussie pour {user_email}")
        return credentials, user_email

    except Exception as e:
        logging.error(f"Erreur d'authentification : {e}")
        raise




def authenticate():
    """Alias simple si tu veux juste forcer une reconnexion sans enregistrer."""
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    credentials = flow.run_local_server(port=0, prompt='consent')
    return credentials


from datetime import datetime, timedelta, time

def get_events(credentials):
    try:
        # Création du service avec gestion d'erreurs
        service = build('calendar', 'v3', credentials=credentials)
        
        # Gestion précise des fuseaux horaires
        now = datetime.utcnow()
        
        # Utilisation de datetime.combine pour plus de précision
        start_of_day = datetime.combine(now.date(), datetime.min.time())
        end_of_day = datetime.combine(now.date(), datetime.max.time())
        
        # Conversion en format ISO avec gestion du fuseau horaire
        timeMin = start_of_day.isoformat() + 'Z'
        timeMax = end_of_day.isoformat() + 'Z'
        
        try:
            # Requête avec gestion des erreurs réseau
            events_result = service.events().list(
                calendarId='primary',
                timeMin=timeMin,
                timeMax=timeMax,
                maxResults=50,  # Augmentation du nombre max d'événements
                singleEvents=True,
                orderBy='startTime'
            ).execute()
        
        except HttpError as error:
            logging.error(f"Erreur HTTP lors de la récupération des événements : {error}")
            return []
        
        events = events_result.get('items', [])
        
        # Enrichissement des événements avec des informations supplémentaires
        for event in events:
            try:
                # Gestion des différents types d'événements
                if 'start' in event:
                    # Événement avec heure
                    if 'dateTime' in event['start']:
                        event['start_time'] = event['start']['dateTime'].split('T')[1][:5]
                        event['date'] = event['start']['dateTime'].split('T')[0]
                    # Événement sur toute la journée
                    elif 'date' in event['start']:
                        event['start_time'] = 'Toute la journée'
                        event['date'] = event['start']['date']
                
                if 'end' in event:
                    if 'dateTime' in event['end']:
                        event['end_time'] = event['end']['dateTime'].split('T')[1][:5]
                    elif 'date' in event['end']:
                        event['end_time'] = 'Toute la journée'
                
                # Informations supplémentaires
                event['duration'] = calculate_event_duration(event)
                
            except Exception as e:
                logging.warning(f"Erreur lors du traitement d'un événement : {e}")
        
        # Tri des événements par heure de début
        events.sort(key=lambda x: x.get('start', {}).get('dateTime', x.get('start', {}).get('date', '')))
        
        return events
    
    except Exception as e:
        logging.error(f"Erreur globale dans get_events : {e}")
        return []

def analyze_schedule_clothing(events):
    sports_keywords = ['sport','entraînement', 'séance de sport', 'gymnastique', 'course', 'footing', 'yoga', 'pilates', 'musculation', 'cyclisme', 'football', 'basketball', 'tennis', 'badminton', 'boxe', 'arts martiaux', 'ski', 'danse', 'crossfit', 'randonnée', 'vélo', 'escalade', 'lutte', 'vtt', 'skateboard', 'kickboxing', 'tennis de table', 'haltérophilie', 'foot', 'handball', 'rugby', 'saut en hauteur', 'athlétisme', 'stretching', 'marche', 'zumba', 'équitation', 'roller']
    plage_keywords = ['natation', 'paddle', 'surf', 'plage', 'canoe', 'aviron', 'kayak','baignade', 'mer', 'océan', 'piscine', 'bronzer', 'bronzette', 'maillot', 'bouée', 'snorkeling', 'plongée', 'jet ski', 'crème solaire', 'sable', 'vagues', 'tuba', 'palmes', 'lagon', 'rivage', 'rivière', 'bord de mer', 'parasol', 'serviette', 'transat']
    pro_keywords = ['work', 'meeting', 'boulot', 'réunion', 'travail', 'entretien', 'taf', 'rendez-vous', 'rdv', 'stage', 'alternance', 'conférence', 'présentation', 'séminaire', 'formation', 'congrès', 'jury', 'examen', 'oral', 'business', 'client', 'mission', 'audit','consultation', 'professionnel', 'corporate', 'workshop', 'atelier', 'entrepôt', 'bureaux', 'siège', 'direction', 'comité', 'entreprise', 'bureau', 'formel']


    recommendations = []

    for event in events:
        summary = event.get('summary', '').lower()

        if any(keyword in summary for keyword in sports_keywords):
            recommendations.append("sport")
        elif any(keyword in summary for keyword in plage_keywords):
            recommendations.append("plage")
        elif any(keyword in summary for keyword in pro_keywords):
            recommendations.append("pro")
        else:
            recommendations.append("chill")

    return recommendations


# 🔐 Sécurisation de l'authentification
def get_stored_credentials(user_email):
    token_path = os.path.join(TOKEN_DIR, f"{user_email}.json")
    
    if os.path.exists(token_path):
        try:
            credentials = Credentials.from_authorized_user_file(token_path, SCOPES)
            return credentials
        except Exception as e:
            print(f"Erreur de chargement des credentials : {e}")
    
    return None

def validate_credentials(credentials):
    """Validation avancée des credentials"""
    try:
        # Vérification de l'expiration
        if credentials.expired:
            logging.warning("Credentials expirés, tentative de refresh")
            credentials.refresh(Request())
        
        # Test minimal de l'API
        service = build('calendar', 'v3', credentials=credentials)
        service.calendarList().list(maxResults=1).execute()
        
        logging.info("Credentials valides")
        return True
    except Exception as e:
        logging.error(f"Credentials invalides : {e}")
        return False
    
def calculate_event_duration(event):
    """Calcul de la durée d'un événement"""
    try:
        if 'start' in event and 'end' in event:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            if start and end:
                start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(end.replace('Z', '+00:00'))
                
                duration = end_time - start_time
                hours, remainder = divmod(duration.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                
                return f"{int(hours)}h {int(minutes)}m"
        return "Durée non définie"
    except Exception as e:
        logging.warning(f"Erreur de calcul de durée : {e}")
        return "Durée non calculable"

