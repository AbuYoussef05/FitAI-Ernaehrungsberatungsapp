import streamlit as st
from database import db_manager
from database.db_setup import init_db
from seiten.Dashboard import show_dashboard
from seiten.Profil import show_profil
from seiten.Ernaehrung import show_ernaehrung
from seiten.Fortschritt import show_fortschritt
from seiten.Coach import show_coach
import os

# Der @st.cache_resource Befehl ist pure Magie. 
# Er merkt sich, dass er das hier schon gemacht hat, und führt es bei Klicks nicht nochmal aus.
@st.cache_resource
def starte_datenbank_einmalig():
    init_db()
    return "Datenbank ist bereit!"

# Hier drücken wir virtuell auf "Enter" im Terminal
starte_datenbank_einmalig()

st.set_page_config(page_title="FitAI", page_icon="💪", layout="centered")

# Session-State initialisieren
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = False
if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"

# Kopfbereich
col1, col2 = st.columns([3, 1.5])                                       
                                                                        
with col1:
    # 1. Den genauen Ordner der Datei herausfinden
    aktueller_ordner = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Pfad und Bildnamen sicher zusammenkleben
    bild_pfad = os.path.join(aktueller_ordner, "LOGO.png")
    
    # 3. Das Bild mit dem neuen Pfad laden
    st.image(bild_pfad, width=150)
    

with col2:
    if st.session_state.logged_in:
        if st.button("🚪 Abmelden", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.logged_in = False
            st.session_state.show_welcome = False
            st.session_state.menu = "Dashboard"
            st.rerun()

# Wenn eingeloggt
if st.session_state.logged_in:
    if st.session_state.show_welcome:
        st.title("Willkommen bei FitAI 🚀")
        st.success("Du bist erfolgreich eingeloggt!")
        st.write("Wähle jetzt eine Option aus der Seitenleiste.")
        st.session_state.show_welcome = False

    st.sidebar.title("Navigation")

    if st.sidebar.button("👤 Profil", use_container_width=True):
        st.session_state.menu = "Profil"
    if st.sidebar.button("📊 Dashboard", use_container_width=True):
        st.session_state.menu = "Dashboard"
    if st.sidebar.button("🥗 Ernährung", use_container_width=True):
        st.session_state.menu = "Ernährung"
    if st.sidebar.button("📈 Fortschritt", use_container_width=True):
        st.session_state.menu = "Fortschritt"
    if st.sidebar.button("🤖 Coach", use_container_width=True):
        st.session_state.menu = "Coach"

    menu = st.session_state.menu

    if menu == "Profil":
        show_profil()
    elif menu == "Dashboard":
        show_dashboard()
    elif menu == "Ernährung":
        show_ernaehrung()
    elif menu == "Fortschritt":
        show_fortschritt()
    elif menu == "Coach":
        show_coach()

# Wenn nicht eingeloggt
else:
    st.title("Willkommen bei FitAI 🚀")

    st.write("Bitte logge dich ein oder erstelle einen neuen Account, um dein Profil zu sehen.")
    tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Registrieren", "❓ Hilfe"])

    with tab1:
        st.subheader("Einloggen")
        login_user = st.text_input("Benutzername", key="login_name")
        login_pass = st.text_input("Passwort", type="password", key="login_pass")

        if st.button("Anmelden"):
            if login_user and login_pass:
                user_id = db_manager.check_login(login_user, login_pass)

                if user_id:
                    st.session_state.user_id = user_id
                    st.session_state.logged_in = True
                    st.session_state.show_welcome = True
                    st.session_state.menu = "Dashboard"
                    st.rerun()
                else:
                    st.error("Falscher Benutzername oder Passwort!")
            else:
                st.warning("Bitte fülle beide Felder aus.")

    with tab2:
        st.subheader("Neuen Account erstellen")
        reg_user = st.text_input("Wunsch-Benutzername", key="reg_name")
        reg_pass = st.text_input("Passwort", type="password", key="reg_pass")
        reg_pass_confirm = st.text_input("Passwort bestätigen", type="password", key="reg_pass_conf")

        if st.button("Account erstellen"):
            if reg_user and reg_pass and reg_pass_confirm:
                if reg_pass == reg_pass_confirm:
                    erfolg = db_manager.register_user(reg_user, reg_pass)

                    if erfolg:
                        st.success("Account erstellt! Du kannst dich jetzt im Login-Tab anmelden.")
                        st.balloons()
                    else:
                        st.error("Dieser Benutzername ist leider schon vergeben.")
                else:
                    st.error("Die Passwörter stimmen nicht überein!")
            else:
                st.warning("Bitte fülle alle Felder aus.")

    with tab3:
        st.subheader("Hilfe")
        st.write("Fit AI ist eine KI-gestützte Fitness-App, die dir hilft, deine Trainingsziele zu erreichen.")
        st.write("Hier kannst du dich einloggen oder registrieren, um loszulegen.")
