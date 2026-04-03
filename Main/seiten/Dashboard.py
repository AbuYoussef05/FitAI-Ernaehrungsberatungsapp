import streamlit as st
from datetime import date
from database.db_manager import get_user_profile, get_xp, add_xp, log_food, get_consumed_calories, get_todays_food, delete_food_log
from logic.calculations import calculate_calories_and_macros
from ai.gemini_service import analyze_food_input

def show_dashboard():
    
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("🔒 Bitte logge dich zuerst über die Hauptseite ein!")
        st.stop()

    user_id = st.session_state.user_id
    profile_data = get_user_profile(user_id)

    if not profile_data or not profile_data.get("weight"):
        st.warning("⚠️ Bitte fülle zuerst dein Profil komplett aus.")
        st.stop()

    berechnete_ziele = calculate_calories_and_macros(
        weight=profile_data["weight"], height=profile_data["height"], 
        age=30, gender="Männlich", activity_level=profile_data["activity_level"], goal=profile_data["goal"]
    )
    ziel_kalorien = berechnete_ziele['kalorien']

    # ==========================================
    # 1. GAMIFICATION: LEVEL SYSTEM (Wieder da!)
    # ==========================================
    aktuelle_xp = get_xp(user_id)
    # Simples Level-System: Alle 100 XP steigt man ein Level auf
    aktuelles_level = (aktuelle_xp // 100) + 1
    xp_im_aktuellen_level = aktuelle_xp % 100
    fortschritt_zum_naechsten = xp_im_aktuellen_level / 100.0

    col_title, col_level = st.columns([2, 1])
    with col_title:
        st.title(f"Willkommen, {profile_data['name']}! 👋")
        st.caption(f"Dein Hauptziel: **{profile_data['goal']}**")

    with col_level:
        # Die Level-Anzeige oben rechts
        with st.container(border=True):
            st.markdown(f"<h3 style='text-align: center; margin-bottom: 0;'>⭐ Level {aktuelles_level}</h3>", unsafe_allow_html=True)
            st.progress(fortschritt_zum_naechsten)
            st.caption(f"<div style='text-align: center;'>{xp_im_aktuellen_level} / 100 XP bis Level {aktuelles_level + 1}</div>", unsafe_allow_html=True)
    st.write("---")

    # ==========================================
    # 2. TRACKING (KI & Manuell + Tagebuch)
    # ==========================================
    st.subheader("🏃‍♂️ Heutiges Tracking")
    heute = str(date.today())

    tab_ki, tab_manuell = st.tabs(["🤖 Mit KI schätzen", "✍️ Manuell eintragen"])

    # TAB 1: KI-EINGABE
    with tab_ki:
        food_eingabe = st.text_input("Was gab es heute?", placeholder="z.B. Ein Croissant und ein Kaffee", key="ki_input")
        if st.button("Mit KI tracken 🚀", use_container_width=True):
            if food_eingabe:
                with st.spinner("KI berechnet Kalorien..."):
                    ergebnis = analyze_food_input(food_eingabe)
                    if ergebnis and "kalorien" in ergebnis:
                        log_food(user_id, heute, ergebnis["gericht"], ergebnis["kalorien"])
                        st.success(f"✅ Erfasst: {ergebnis['gericht']} ({ergebnis['kalorien']} kcal)")
                        st.rerun()
                    else:
                        st.error("Das konnte die KI leider nicht verarbeiten.")
            else:
                st.warning("Bitte gib ein Essen ein!")

    # TAB 2: MANUELLE EINGABE
    with tab_manuell:
        col_m1, col_m2 = st.columns([3, 1])
        with col_m1:
            manuell_name = st.text_input("Name der Mahlzeit", placeholder="z.B. Proteinriegel Schoko")
        with col_m2:
            manuell_kcal = st.number_input("Kalorien (kcal)", min_value=1, max_value=5000, value=250)
        
        if st.button("Manuell speichern 💾", use_container_width=True):
            if manuell_name:
                log_food(user_id, heute, manuell_name, manuell_kcal)
                st.success(f"✅ Erfasst: {manuell_name} ({manuell_kcal} kcal)")
                st.rerun()
            else:
                st.warning("Bitte gib der Mahlzeit einen Namen!")

    st.write("---")

    # ÜBERSICHT: HEUTE GEGESSEN
    st.markdown("### 🍽️ Dein Food-Tagebuch (Heute)")
    heutige_mahlzeiten = get_todays_food(user_id, heute)
    
    if heutige_mahlzeiten:
        for meal in heutige_mahlzeiten:
            col_text, col_btn = st.columns([0.85, 0.15])
            with col_text:
                st.markdown(f"**{meal['food_text']}** — *{meal['calories']} kcal*")
            with col_btn:
                if st.button("❌", key=f"del_{meal['id']}", help="Eintrag löschen"):
                    delete_food_log(meal['id'])
                    st.rerun()
    else:
        st.info("Du hast heute noch nichts getrackt.")

    st.write("<br>", unsafe_allow_html=True)

    # ==========================================
    # 3. STATISTIKEN & XP-BELOHNUNG (Wieder da!)
    # ==========================================
    gegessen = get_consumed_calories(user_id, heute)
    verbrannt = st.slider("🔥 Verbrannte Kalorien durch Sport", min_value=0, max_value=2000, value=0, step=50)

    uebrig = ziel_kalorien - gegessen + verbrannt

    bal_col1, bal_col2, bal_col3, bal_col4 = st.columns(4)
    bal_col1.metric("🎯 Tagesziel", f"{ziel_kalorien} kcal")
    bal_col2.metric("🍽️ Gegessen", f"{gegessen} kcal")
    bal_col3.metric("🏃‍♂️ Verbrannt", f"{verbrannt} kcal")

    # 🎁 XP-Logik für eingehaltene Kalorien
    if uebrig < 0:
        bal_col4.metric("🚨 Übrig", f"{uebrig} kcal", delta="Überschritten!", delta_color="inverse")
    elif gegessen > 0 and uebrig <= 200:
        bal_col4.metric("✅ Übrig", f"{uebrig} kcal", delta="Perfekt im Plan!", delta_color="normal")
        # Dieser Button erscheint nur, wenn man sein Ziel fast exakt getroffen hat!
        if st.button("🎁 Tagesziel erreicht! +50 XP abholen", type="primary", use_container_width=True):
            add_xp(user_id, 50)
            st.balloons() 
            st.success("Herzlichen Glückwunsch! 50 XP erhalten.")
            st.rerun() 
    else:
        bal_col4.metric("ℹ️ Übrig", f"{uebrig} kcal", delta="Noch Platz", delta_color="off")

    st.write("---")
    
    # ==========================================
    # 4. COACH & DAILY LOGIN BONUS (Wieder da!)
    # ==========================================
    col_meals, col_progress = st.columns([2, 1])

    with col_meals:
        st.subheader("🍽️ Ernährungsplan")
        st.info("Gehe links auf 'Ernährung', um deinen KI-Plan anzusehen!")
        
    with col_progress:
        st.subheader("🤖 Dein Coach")
        # 🎁 XP-Logik für täglichen Login
        if st.button("Täglicher Login-Bonus (+10 XP)", use_container_width=True):
            add_xp(user_id, 10)
            st.toast("10 XP für deinen Login heute erhalten!", icon="🔥")
            st.rerun()