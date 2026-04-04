import sqlite3
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Den genauen Pfad zum database-Ordner finden
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Neue, frische Datenbank erstellen lassen
DB_PATH = os.path.join(BASE_DIR, "fitai_cloud.db")

# 1. AUTHENTIFIZIERUNG (Login / Register)
def get_connection():
    # Hilfsfunktion für die DB-Verbindung
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def register_user(email, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor() 
        hashed_pw = generate_password_hash(password)
        
        # FIX 1: 'email' statt 'username'
        cursor.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, hashed_pw))
        user_id = cursor.lastrowid
        
        # FIX 2: 'profiles' statt 'user_profiles'
        cursor.execute("INSERT INTO profiles (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
        return user_id, "Erfolg"
    except sqlite3.IntegrityError:
        return None, "Email existiert bereits"
    except Exception as e:
        return None, f"Fehler: {e}"

def check_login(email, password):
    """Prüft das Passwort beim Login."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # FIX 3: 'email' statt 'username'
    cursor.execute("SELECT id, password_hash FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        return user['id']
    return None

# ==========================================
# AB HIER BLEIBT ALLES WIE BEI DIR! 
# ==========================================

# 2. PROFIL-DATEN VERWALTEN
def get_user_profile(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, goal, weight, height, activity_level, diet_type FROM profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "name": row[0] if row[0] else "",
                "goal": row[1] if row[1] else "Abnehmen",
                "weight": row[2] if row[2] else 70.0,
                "height": row[3] if row[3] else 170.0,
                "activity_level": row[4] if row[4] else "Mittel (3-4x pro Woche)",
                "diet_type": row[5] if row[5] else "Ausgewogen"
            }
        return None
    except Exception:
        return None

def update_profile(user_id, name, goal, weight, height, activity_level, diet_type):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE profiles 
            SET name=?, goal=?, weight=?, height=?, activity_level=?, diet_type=?
            WHERE user_id=?
        ''', (name, goal, weight, height, activity_level, diet_type, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

# Fortschritt & Gewicht

def log_weight(user_id, weight, date):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO weight_history (user_id, weight, date) VALUES (?, ?, ?)", (user_id, weight, date))
    conn.commit()
    conn.close()

def get_weight_history(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT date, weight FROM weight_history WHERE user_id = ? ORDER BY date ASC", (user_id,))
        data = cursor.fetchall()
        conn.close()
        return data
    except sqlite3.OperationalError:
        return []
    

# Coach, Gamification & Chat

def get_coach_persona(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Fallback falls die Spalte noch nicht existiert
        cursor.execute("SELECT coach_persona FROM profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row and row[0] else "Empathischer Mentor"
    except sqlite3.OperationalError:
        return "Empathischer Mentor"

def update_coach_persona(user_id, persona):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE profiles SET coach_persona = ? WHERE user_id = ?", (persona, user_id))
    conn.commit()
    conn.close()

def add_xp(user_id, amount):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE profiles SET xp = xp + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def get_xp(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT xp FROM profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row and row[0] else 0
    except sqlite3.OperationalError:
        return 0

def get_chat_history(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT role, content FROM chat_history WHERE user_id = ? ORDER BY timestamp ASC", (user_id,))
        data = cursor.fetchall()
        conn.close()
        return [{"role": r[0], "content": r[1]} for r in data]
    except sqlite3.OperationalError:
        return []

def save_chat_message(user_id, role, content):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
    conn.commit()
    conn.close()

def save_meal_plan(user_id, plan_dict):
    """Speichert den generierten JSON-Plan dauerhaft in der Datenbank."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Automatisches Update: Wir fügen die Spalte hinzu, falls sie noch fehlt
    try:
        cursor.execute("ALTER TABLE profiles ADD COLUMN meal_plan TEXT")
    except sqlite3.OperationalError:
        pass # Spalte existiert bereits
        
    # Den Python-Dictionary-Plan in einen Text (String) umwandeln
    plan_str = json.dumps(plan_dict)
    
    cursor.execute("UPDATE profiles SET meal_plan = ? WHERE user_id = ?", (plan_str, user_id))
    conn.commit()
    conn.close()

def get_saved_meal_plan(user_id):
    """Holt den gespeicherten Plan beim Einloggen wieder aus der Datenbank."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT meal_plan FROM profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        # Wenn ein Plan da ist, wandeln wir den Text wieder in ein Dictionary um
        if row and row['meal_plan']:
            return json.loads(row['meal_plan'])
    except Exception:
        pass
    return None

# ==========================================
# 3. FOOD TRACKER (Neu!)
# ==========================================

def init_food_table():
    """Erstellt die Tracking-Tabelle automatisch, falls sie noch fehlt."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            food_text TEXT,
            calories INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def log_food(user_id, date, food_text, calories):
    """Speichert eine gegessene Mahlzeit in der Datenbank."""
    init_food_table() # Geht auf Nummer sicher, dass die Tabelle existiert
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO food_log (user_id, date, food_text, calories) VALUES (?, ?, ?, ?)", 
                   (user_id, date, food_text, calories))
    conn.commit()
    conn.close()

def get_consumed_calories(user_id, date):
    """Zählt alle Kalorien zusammen, die der Nutzer heute gegessen hat."""
    init_food_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(calories) FROM food_log WHERE user_id = ? AND date = ?", (user_id, date))
    total = cursor.fetchone()[0]
    conn.close()
    return total if total else 0

def get_todays_food(user_id, date):
    """Holt eine Liste aller Mahlzeiten, die der Nutzer heute eingetragen hat."""
    init_food_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, food_text, calories FROM food_log WHERE user_id = ? AND date = ?", (user_id, date))
    data = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "food_text": r[1], "calories": r[2]} for r in data]

def delete_food_log(log_id):
    """Löscht einen Eintrag aus dem Food-Tracker."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM food_log WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()

# ==========================================
# 4. EXERCISE TRACKER (Neu!)
# ==========================================

def init_exercise_table():
    """Erstellt die Sport-Tabelle, falls sie noch fehlt."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercise_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            activity_text TEXT,
            calories INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def log_exercise(user_id, date, activity_text, calories):
    """Speichert eine sportliche Aktivität."""
    init_exercise_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO exercise_log (user_id, date, activity_text, calories) VALUES (?, ?, ?, ?)", 
                   (user_id, date, activity_text, calories))
    conn.commit()
    conn.close()

def get_burned_calories(user_id, date):
    """Zählt alle verbrannten Kalorien für heute zusammen."""
    init_exercise_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(calories) FROM exercise_log WHERE user_id = ? AND date = ?", (user_id, date))
    total = cursor.fetchone()[0]
    conn.close()
    return total if total else 0

def get_todays_exercises(user_id, date):
    """Holt die Liste der heutigen Aktivitäten."""
    init_exercise_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, activity_text, calories FROM exercise_log WHERE user_id = ? AND date = ?", (user_id, date))
    data = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "activity_text": r[1], "calories": r[2]} for r in data]

def delete_exercise_log(log_id):
    """Löscht eine Aktivität."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM exercise_log WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()