import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "fitai_cloud.db")

def init_db():
    """Erstellt alle Tabellen passend zu unserem aktuellen db_manager.py."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabelle 1: User (Alles in einer Tabelle)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    # Tabelle 2: Profile (Epic 1)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            goal TEXT,
            weight REAL,
            height REAL,
            activity_level TEXT,
            diet_type TEXT,
            coach_persona TEXT DEFAULT 'Empathischer Mentor',
            xp INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    try:
        cursor.execute("ALTER TABLE profiles ADD COLUMN coach_persona TEXT DEFAULT 'Empathischer Mentor'")
    except sqlite3.OperationalError:
        pass # Spalte existiert schon
        
    try:
        cursor.execute("ALTER TABLE profiles ADD COLUMN xp INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass # Spalte existiert schon

    # Tabelle 3: Gewichtsverlauf (Epic 4)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weight_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            weight REAL,
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabelle 4: Chat-Historie (Epic 5)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()
    
    # Test-Personas anlegen
    seed_personas()

def seed_personas():

    """Legt die 3 Test-Personas an, falls die Datenbank noch leer ist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # 1. Persona
        cursor.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", 
                       ("sportler@test.de", generate_password_hash("test1234")))
        sportler_id = cursor.lastrowid
        cursor.execute('''INSERT INTO profiles (user_id, name, goal, weight, height, activity_level, diet_type) 
                          VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                       (sportler_id, "Alex (Sportler)", "Ausdauer halten", 75.0, 180.0, "Hoch (5-6x pro Woche)", "Ausgewogen"))

        # 2. Persona
        cursor.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", 
                       ("student@test.de", generate_password_hash("test1234")))
        student_id = cursor.lastrowid
        cursor.execute('''INSERT INTO profiles (user_id, name, goal, weight, height, activity_level, diet_type) 
                          VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                       (student_id, "Ben (Student)", "Muskelaufbau", 68.0, 175.0, "Mittel (3-4x pro Woche)", "High Protein"))

        # 3. Persona
        cursor.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", 
                       ("beamter@test.de", generate_password_hash("test1234")))
        beamter_id = cursor.lastrowid
        cursor.execute('''INSERT INTO profiles (user_id, name, goal, weight, height, activity_level, diet_type) 
                          VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                       (beamter_id, "Christian (Beamter)", "Bewegungsmangel ausgleichen", 85.0, 178.0, "Niedrig (1-2x pro Woche)", "Standard"))

        conn.commit()

    conn.close()

if __name__ == "__main__":
    init_db()
