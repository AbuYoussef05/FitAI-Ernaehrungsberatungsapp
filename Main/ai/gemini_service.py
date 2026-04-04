from google import genai
from google.genai import types
import streamlit as st
import json

# API Key aus den Secret holen
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"Setup-Fehler: API Key nicht gefunden. {e}")
    client = None

# Modell definieren 
MODEL_ID = "gemini-2.5-flash"

# 1. UPDATE DER HAUPTFUNKTION (Jetzt mit extra_infos)
def generate_weekly_meal_plan(profile, target_calories, diet_preference, extra_infos=""):
    """Generiert einen 7-Tage Ernährungsplan als JSON-Objekt."""
    if not client:
        return None

    prompt = f"""
    Erstelle einen 7-Tage Ernährungsplan für {profile.get('name', 'den Nutzer')}.
    Sein Ziel: {profile.get('goal')}, Kalorienziel pro Tag: {target_calories} kcal.
    WICHTIGE REGEL: Die Ernährungsform ist '{diet_preference}'. 
    SONDERWÜNSCHE / ALLERGIEN: {extra_infos if extra_infos else 'Keine'}
    
    Antworte AUSSCHLIESSLICH im JSON-Format ohne weiteren Text.
    
    Format-Beispiel:
    {{
      "wochenplan": [
        {{
          "tag": "Montag",
          "mahlzeiten": [
            {{
              "typ": "Frühstück",
              "gericht": "Haferflocken mit Beeren",
              "kalorien": 400,
              "zutaten": ["Haferflocken", "Beeren", "Milch"]
            }}
          ]
        }}
      ]
    }}
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        if not response.text: return None
        return json.loads(response.text)
    except Exception as e:
        print(f"KI Fehler beim Ernährungsplan: {e}")
        return None

# 2. NEUE FUNKTION HINZUFÜGEN (Für den "Austauschen"-Button)
def swap_single_meal(meal_type, old_meal, calories, diet_preference, extra_infos=""):
    """Generiert EINE neue Ersatz-Mahlzeit als JSON."""
    if not client: return None

    prompt = f"""
    Generiere EINE neue, alternative Mahlzeit für das {meal_type}.
    Sie soll ca. {calories} kcal haben.
    WICHTIG: Es darf NICHT '{old_meal}' sein.
    Ernährungsform: '{diet_preference}'. Sonderwünsche: {extra_infos if extra_infos else 'Keine'}.
    
    Antworte AUSSCHLIESSLICH im JSON-Format für diese EINE Mahlzeit:
    {{
      "typ": "{meal_type}",
      "gericht": "Neuer Name",
      "kalorien": {calories},
      "zutaten": ["Zutat 1", "Zutat 2"]
    }}
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"KI Fehler beim Austauschen: {e}")
        return None

def generate_chat_response(prompt, persona, user_name, goal, history=None):
    """Lässt den KI-Coach auf eine Nachricht antworten (mit Gedächtnis)."""
    if not client:
        return f"*(Offline-Modus)* Hey {user_name}, ich bin aktuell nicht erreichbar!"
    
    # Bisherigen Chatverlauf als Text für die KI zusammenbauen
    history_text = ""
    if history:
        history_text = "Bisheriger Verlauf unseres Gesprächs:\n"
        # letzte 4 Nachrichten merken
        for msg in history[-4:]: 
            rolle = "Nutzer" if msg["role"] == "user" else "Coach"
            history_text += f"[{rolle}]: {msg['content']}\n"

    system_prompt = f"""
    Du bist ein Fitness-Coach. Dein Charakter: '{persona}'.
    Dein Klient heißt {user_name} und sein Ziel ist {goal}.
    
    {history_text}
    
    Antworte in deiner Rolle kurz und motivierend auf seine NEUESTE Nachricht: '{prompt}'
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=system_prompt
        )
        return response.text
    except Exception as e:
        return f"*(System)* Fehler bei der KI-Antwort: {e}"
    
def analyze_food_input(food_input):
    """KI schätzt die Kalorien für eingegebenes Essen."""
    if not client:
        return None

    prompt = f"""
    Der Nutzer hat folgendes gegessen: '{food_input}'.
    Schätze realistisch die Kalorien für diese Mahlzeit.
    Antworte AUSSCHLIESSLICH im JSON-Format, ohne Markdown oder weiteren Text!
    
    Format-Beispiel:
    {{
      "gericht": "Zusammenfassung des Essens",
      "kalorien": 450
    }}
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        if not response.text:
            return None
        return json.loads(response.text)
    except Exception as e:
        print(f"KI Fehler beim Food-Tracking: {e}")
        return None
    
def analyze_exercise_input(exercise_input):
    """KI schätzt verbrannte Kalorien basierend auf der Aktivität."""
    if not client:
        return None

    prompt = f"""
    Der Nutzer hat folgenden Sport gemacht: '{exercise_input}'.
    Schätze realistisch die verbrannten Kalorien.
    Antworte AUSSCHLIESSLICH im JSON-Format:
    {{
      "aktivitaet": "Zusammenfassung der Aktivität",
      "kalorien": 250
    }}
    """
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"KI Fehler beim Sport-Tracking: {e}")
        return None