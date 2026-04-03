import streamlit as st
from database.db_manager import get_user_profile, update_profile

def show_profil():
    st.title("👤 Mein Profil")
    st.markdown("Hier kannst du deine persönlichen Daten eingeben und dein Profil anpassen.")

    user_id = st.session_state.user_id
    profile_data = get_user_profile(user_id)

    if st.session_state.get('user_id') is None:
        st.warning("Bitte auf der Startseite einloggen!")
        st.stop()

    with st.form("profil_form"):
        st.subheader("1. Persönliche Daten")
        col1, col2 = st.columns(2)
        name = col1.text_input("Dein Name / Spitzname", value=profile_data["name"])
    
        st.write("---")
        st.subheader("2. Biometrie & Aktivität")
        col3, col4 = st.columns(2)
        weight = col3.number_input("Aktuelles Gewicht (kg)", min_value=30.0, max_value=250.0, value=float(profile_data["weight"]), step=0.5)
        height = col4.number_input("Körpergröße (cm)", min_value=100.0, max_value=250.0, value=float(profile_data["height"]), step=1.0)
    
        # Dropdowns für vordefinierte Werte
        activity_level = st.selectbox(
            "Wie aktiv bist du im Alltag / Training?", 
            ["Niedrig (1-2x pro Woche)", "Mittel (3-4x pro Woche)", "Hoch (5-6x pro Woche)", "Extrem (Täglich)"],
            index=["Niedrig (1-2x pro Woche)", "Mittel (3-4x pro Woche)", "Hoch (5-6x pro Woche)", "Extrem (Täglich)"].index(profile_data["activity_level"]) if profile_data["activity_level"] in ["Niedrig (1-2x pro Woche)", "Mittel (3-4x pro Woche)", "Hoch (5-6x pro Woche)", "Extrem (Täglich)"] else 1
        )

        st.write("---")
        st.subheader("3. Deine Ziele")
        col5, col6 = st.columns(2)
        goal = col5.selectbox(
            "Was ist dein Hauptziel?",
            ["Abnehmen", "Gewicht halten", "Muskelaufbau", "Ausdauer verbessern"],
            index=["Abnehmen", "Gewicht halten", "Muskelaufbau", "Ausdauer verbessern"].index(profile_data["goal"]) if profile_data["goal"] in ["Abnehmen", "Gewicht halten", "Muskelaufbau", "Ausdauer verbessern"] else 0
        )
        
        diet_type = col6.selectbox(
            "Ernährungsform",
            ["Ausgewogen", "High Protein", "Vegan", "Vegetarisch", "Keto", "Low Carb"],
            index=["Ausgewogen", "High Protein", "Vegan", "Vegetarisch", "Keto", "Low Carb"].index(profile_data["diet_type"]) if profile_data["diet_type"] in ["Ausgewogen", "High Protein", "Vegan", "Vegetarisch", "Keto", "Low Carb"] else 0
        )
        
        # Speichern-Button
        submitted = st.form_submit_button("💾 Profil speichern", type="primary")
        
        if submitted:
            # Die neuen Daten an unsere Datenbank-Funktion senden
            erfolg = update_profile(user_id, name, goal, weight, height, activity_level, diet_type)
            if erfolg:
                st.success("✅ Profil erfolgreich aktualisiert!")
                st.balloons() # Kleine Streamlit-Spielerei zur Belohnung
            else:
                st.error("❌ Fehler beim Speichern der Daten.")