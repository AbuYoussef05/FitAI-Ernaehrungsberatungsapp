import streamlit as st
from database.db_manager import get_user_profile, get_coach_persona, update_coach_persona, get_chat_history, save_chat_message
from ai.gemini_service import generate_chat_response

def show_coach():

    user_id = st.session_state.user_id
    profile = get_user_profile(user_id)

    st.title("🤖 Dein digitaler Coach")

    # ==========================================
    # TEIL A: COACH-EINSTELLUNGEN
    # ==========================================
    with st.expander("⚙️ Coach-Einstellungen", expanded=False):
        aktueller_coach = get_coach_persona(user_id)
        
        # Optionen für den Charakter
        optionen = ["Empathischer Mentor", "Strenger Drill-Instructor", "Wissenschaftlicher Experte"]
        aktueller_index = optionen.index(aktueller_coach) if aktueller_coach in optionen else 0
        
        neuer_coach = st.selectbox(
            "Wähle den Charakter deines Coaches:",
            optionen,
            index=aktueller_index
        )
        
        if st.button("Charakter speichern"):
            update_coach_persona(user_id, neuer_coach)
            st.success(f"Dein Coach ist jetzt ein {neuer_coach}!")
            st.rerun()

    st.write("---")

    # ==========================================
    # TEIL B: CHAT-HISTORIE LADEN
    # ==========================================
    history = get_chat_history(user_id)

    # Zeige alle alten Nachrichten an
    for msg in history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ==========================================
    # TEIL C: NEUE NACHRICHT EINGEBEN
    # ==========================================
    prompt = st.chat_input("Frag deinen Coach etwas (z.B. 'Was soll ich nach dem Training essen?')...")

    if prompt:
        # 1. Nutzer-Nachricht anzeigen und in der Datenbank speichern
        with st.chat_message("user"):
            st.markdown(prompt)
        save_chat_message(user_id, "user", prompt)

        # 2. KI-Antwort über den gemini_service generieren
        with st.chat_message("assistant"):
            with st.spinner(f"{aktueller_coach} tippt..."):
                
                # Hier rufen wir die API auf
                antwort = generate_chat_response(
                    prompt=prompt, 
                    persona=aktueller_coach, 
                    user_name=profile.get('name', 'Nutzer'), 
                    goal=profile.get('goal', 'Fit werden')
                )
                
                # Antwort anzeigen und in der Datenbank speichern
                st.markdown(antwort)
                save_chat_message(user_id, "assistant", antwort)