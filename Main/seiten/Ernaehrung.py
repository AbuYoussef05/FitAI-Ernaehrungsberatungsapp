import streamlit as st
from database.db_manager import get_user_profile, save_meal_plan, get_saved_meal_plan
from logic.calculations import calculate_calories_and_macros
from ai.gemini_service import generate_weekly_meal_plan, swap_single_meal

def show_ernaehrung():

    user_id = st.session_state.user_id
    profile_data = get_user_profile(user_id)

    if not profile_data or not profile_data.get("weight"):
        st.warning("⚠️ Bitte fülle zuerst dein Profil komplett aus.")
        st.stop()

    # 2. Kalorienbedarf berechnen (als Vorgabe für die KI)
    berechnete_ziele = calculate_calories_and_macros(
        weight=profile_data["weight"], 
        height=profile_data["height"], 
        age=30, gender="Männlich", 
        activity_level=profile_data["activity_level"], 
        goal=profile_data["goal"]
    )
    target_calories = berechnete_ziele['kalorien']

    # 3. Plan aus der DATENBANK laden (statt nur leeren Session State zu machen)
    if "meal_plan" not in st.session_state or st.session_state.meal_plan is None:
        gespeicherter_plan = get_saved_meal_plan(user_id)
        if gespeicherter_plan:
            st.session_state.meal_plan = gespeicherter_plan
        else:
            st.session_state.meal_plan = None

    # ==========================================
    # UI: ERNÄHRUNGS-SEITE
    # ==========================================
    st.title("🍽️ Dein KI-Ernährungsplan")
    st.markdown(f"Basierend auf deinem Ziel (**{profile_data['goal']}**) und deiner Ernährungsform (**{profile_data['diet_type']}**) plant unsere KI deine Woche mit ca. **{target_calories} kcal** pro Tag.")

    st.write("---")

    col_a, col_b = st.columns(2)
    with col_a:
        praeferenz = st.selectbox(
            "Besonderheiten für diesen Plan?", 
            ["Offen für alles", "Halal", "Vegan", "Vegetarisch", "Low Carb", "Pescatarisch"]
        )
    with col_b:
        # NEU: Das Textfeld für eigene Eingaben!
        extra_wunsch = st.text_input("Zusätzliche Wünsche / Allergien?", placeholder="z.B. Keine Tomaten, mehr Reis...")

    # Der magische Button (Jetzt mit 4 Variablen!)
    if st.button("✨ Neuen 7-Tage-Plan generieren", type="primary", use_container_width=True):
        with st.spinner("Gemini stellt deinen perfekten Plan zusammen..."):
            plan = generate_weekly_meal_plan(profile_data, target_calories, praeferenz, extra_wunsch)
            
            if plan and "wochenplan" in plan:
                st.session_state.meal_plan = plan
                st.session_state.praeferenz = praeferenz 
                st.session_state.extra_wunsch = extra_wunsch
                
                # HIER SPEICHERN WIR IN DIE DB!
                save_meal_plan(user_id, plan) 
                
                st.success("✅ Plan erfolgreich generiert und dauerhaft gespeichert!")
                st.rerun()
            else:
                st.error("❌ Es gab ein Problem bei der Generierung.")

    st.write("<br>", unsafe_allow_html=True)

    # ==========================================
    # ERGEBNIS-ANZEIGE (Mit Lösch- & Tausch-Funktion!)
    # ==========================================
    if st.session_state.meal_plan:
        tab_plan, tab_liste = st.tabs(["📅 Wochenplan", "🛒 Einkaufsliste"])
        
        plan_data = st.session_state.meal_plan.get("wochenplan", [])
        
        with tab_plan:
            st.subheader("Deine Mahlzeiten für diese Woche")
            
            for tag_idx, tag in enumerate(plan_data):
                wochentag = tag.get("tag", "Tag")
                
                with st.expander(f"📅 {wochentag}", expanded=False):
                    # Mit enumerate bekommen wir eine Nummer (idx) für jede Mahlzeit
                    for idx, mahlzeit in enumerate(tag.get("mahlzeiten", [])):
                        typ = mahlzeit.get("typ", "Mahlzeit")
                        gericht = mahlzeit.get("gericht", "Unbekannt")
                        kalorien = mahlzeit.get("kalorien", 0)
                        zutaten = mahlzeit.get("zutaten", [])
                        
                        # 3 Spalten: Text (breit), Tauschen-Button (schmal), Löschen-Button (schmal)
                        col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
                        
                        with col1:
                            st.markdown(f"**{typ}**: {gericht} (*{kalorien} kcal*)")
                            st.caption("Zutaten: " + ", ".join(zutaten))
                            
                        with col2:
                            # BUTTON: Austauschen
                            if st.button("🔄 Tauschen", key=f"swap_{tag_idx}_{idx}", help="Neue Mahlzeit generieren"):
                                with st.spinner("Generiere Alternative..."):
                                    neue_mahlzeit = swap_single_meal(
                                        meal_type=typ, 
                                        old_meal=gericht, 
                                        calories=kalorien, 
                                        diet_preference=st.session_state.get("praeferenz", "Offen für alles"),
                                        extra_infos=st.session_state.get("extra_wunsch", "")
                                    )
                                    if neue_mahlzeit:
                                        st.session_state.meal_plan["wochenplan"][tag_idx]["mahlzeiten"][idx] = neue_mahlzeit
                                        # HIER AUCH DAS UPDATE SPEICHERN!
                                        save_meal_plan(user_id, st.session_state.meal_plan)
                                        st.rerun()
                                        
                        with col3:
                            # BUTTON: Löschen
                            if st.button("🗑️ Löschen", key=f"del_{tag_idx}_{idx}"):
                                st.session_state.meal_plan["wochenplan"][tag_idx]["mahlzeiten"].pop(idx)
                                # UND HIER AUCH SPEICHERN!
                                save_meal_plan(user_id, st.session_state.meal_plan)
                                st.rerun()
                        
                        st.write("---")

        with tab_liste:
            st.subheader("Automatisierte Einkaufsliste")
                        
        # --- TAB 2: EINKAUFSLISTE ---
        with tab_liste:
            st.subheader("Automatisierte Einkaufsliste")
            st.write("Hier sind alle Zutaten aus deinem Wochenplan zusammengefasst:")
            
            # Alle Zutaten aus dem JSON extrahieren und in eine Liste packen
            alle_zutaten = []
            for tag in plan_data:
                for mahlzeit in tag.get("mahlzeiten", []):
                    alle_zutaten.extend(mahlzeit.get("zutaten", []))
                    
            # Duplikate entfernen (damit "Salz" nicht 10x auftaucht) und alphabetisch sortieren
            einzigartige_zutaten = sorted(list(set(alle_zutaten)))
            
            # Zutaten als Checkboxen darstellen
            with st.container(border=True):
                for zutat in einzigartige_zutaten:
                    st.checkbox(zutat.title(), key=f"check_{zutat}")