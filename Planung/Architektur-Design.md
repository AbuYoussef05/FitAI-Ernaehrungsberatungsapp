# Projektdokumentation FITAI
**Phase 2: Architektur-Design**

**Projektgruppe:** Yakoub El-Saidi, Nico Zajontz, Aida Qukovci

## 1. Systemarchitektur

Für die Umsetzung von FITAI wählen wir eine **monolithische Architektur auf Basis von Streamlit**. Da es sich um ein prototypisches projekt handelt, verzichten wir auf eine komplexe Trennung von Client (Mobile App) und Server (Backend). 

Stattdessen werden Frontend-Darstellung und Backend-Logik innerhalb derselben Python-Codebasis vereint. Die App ist zustandsgesteuert (State-driven): Der Datenaustausch zwischen den verschiedenen Seiten (z.B. von der Zieleingabe zum Dashboard) wird über den `st.session_state` von Streamlit abgewickelt. Die Architektur ist leichtgewichtig, lokal lauffähig und ideal für die schnelle Integration von Datenanalyse- und KI-Modellen.

## 2. Identifikation der Komponenten und deren Schnittstellen

Das System unterteilt sich in vier logische Hauptkomponenten:

### A. Frontend (User Interface / Streamlit Pages)
Diese Komponente deckt die direkte Interaktion mit dem User ab.
* **Onboarding & Profil:** Eingabemasken für Biometrie (Gewicht), Ziele, Allergien, Ernährungsform und Trainingsfrequenz.
* **Dashboard:** Visualisierung des aktuellen Fortschritts (Schrittzähler, verbrauchte/aufgenommene Kalorien, Trainingshistorie).
* **Plan-Ansicht:** Darstellung der generierten Essens- und Trainingspläne inklusive Export-Möglichkeit der Einkaufsliste.
* **Coach-Interface:** Ein Chat-Fenster zur direkten Kommunikation mit dem digitalen Coach.

### B. Core-Logik (Python Backend-Module)
Hier finden die Berechnungen und die Datenverarbeitung statt.
* **Data Processor:** Berechnet den Kalorienbedarf (z.B. Harris-Benedict-Formel) basierend auf den Profil- und Zieldaten. Gleicht Ist- und Soll-Werte ab, um bei Abweichungen Warnungen auszugeben und Ziele neu zu berechnen.
* **Gamification Engine:** Ein Logik-Modul, das den Fortschritt auswertet und dafür Erfahrungspunkte (XP) vergibt sowie Level-Aufstiege steuert.
* **AI-Handler:** Konstruiert die Prompts (Eingaben) für die KI, indem es User-Daten (z.B. "Vegan", "Ziel: Muskelaufbau", "Allergie: Nüsse") zusammenfasst und an das externe KI-Modell sendet.

### C. Datenhaltung
* **Lokale Datenbank:** Eine **SQLite**-Datenbank speichert die User-Profile, den Verlauf der Gewichts- und Kaloriendaten sowie die Chathistorie. 
* **Schnittstelle:** Die Anbindung an die Python-Logik erfolgt direkt über das integrierte `sqlite3`-Modul oder `SQLAlchemy`.

### D. Externe Schnittstellen & Mocks
Um die Anforderungen umzusetzen, binden wir externe APIs an bzw. simulieren diese für den Prototyp:
* **KI-Schnittstelle (Google Gemini API):** Die Python-Logik sendet Anfragen an das Gemini-Modell, um die Ernährungspläne zu generieren, Verhaltensmuster zu analysieren und die Antworten des digitalen Coaches (mit anpassbarer Persona) zu erzeugen.
* **Picnic API (Mock):** Die Funktion zur Erstellung der Einkaufsliste generiert im Prototyp ein JSON-File oder eine formatierte Textliste, die die strukturierte Übergabe an einen Online-Supermarkt simuliert.
* **Schrittzähler (Mock):** Da Streamlit im Browser läuft und keinen Zugriff auf Smartphone-Sensoren hat, wird der Schrittzähler über manuelle Eingaben oder Schieberegler im UI simuliert.

## 3. Technologie-Entscheidungen (Tech-Stack)

Die Auswahl der Technologien ist speziell auf die Teamgröße und den Fokus auf KI- und Datenintegration zugeschnitten.

* **Programmiersprache: Python 3**
  * *Begründung:* Python ist der Industriestandard für Datenverarbeitung und KI. Es ermöglicht uns, komplexe Berechnungen und die API-Anbindung an die KI effizient zu programmieren.
* **Framework: Streamlit**
  * *Begründung:* Streamlit wandelt Python-Skripte direkt in interaktive Web-Apps um. Wir müssen keine Zeit in das Erlernen von HTML, CSS oder JavaScript investieren und können uns voll auf die Kernlogik (Ernährung, KI, Gamification) konzentrieren.
* **Datenbank: SQLite**
  * *Begründung:* SQLite erfordert keine Server-Einrichtung. Die gesamte Datenbank liegt als lokale Datei vor, was das Teilen des Projekts im Team und bei der Abgabe extrem vereinfacht.
* **Visualisierung: Plotly / Streamlit Charts**
  * *Begründung:* Für die Fortschrittsanalyse (Gewichtskurven, Kalorien-Balkendiagramme) bieten diese Bibliotheken interaktive Diagramme, die sich mit wenigen Zeilen Code in Streamlit integrieren lassen.
* **KI-Modell: Google Gemini API**
  * *Begründung:* Bietet verlässliche Text- und JSON-Generierung bei hoher Geschwindigkeit. Für unser Projekt ist der großzügige, kostenlose Tarif ("Free Tier") der API ein entscheidender Vorteil. Zudem lässt sich die API über das Python-SDK nahtlos in unser Streamlit-Backend integrieren.
* **Versionierung: Git & OpenCode GitLab**
  * *Begründung:* Zwingend notwendig für die reibungslose Zusammenarbeit im Team. OpenCode bietet uns als GitLab-Instanz eine sichere Umgebung für unser Code-Repository. So können wir zu dritt gleichzeitig an verschiedenen Modulen arbeiten, ohne uns gegenseitig den Code zu überschreiben.