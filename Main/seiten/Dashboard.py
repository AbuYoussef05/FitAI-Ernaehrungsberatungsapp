import streamlit as st
from datetime import date
from database.db_manager import get_user_profile, get_xp, add_xp, log_food, get_consumed_calories, get_todays_food, delete_food_log, log_exercise, get_todays_exercises, delete_exercise_log , get_burned_calories
from logic.calculations import calculate_calories_and_macros
from ai.gemini_service import analyze_food_input, analyze_exercise_input

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
    # 2. TRACKING (Essen & Sport)
    # ==========================================
    heute = str(date.today())
    
    col_food, col_sport = st.columns(2)

    with col_food:
        st.subheader("🍽️ Food-Tracking")
        tab_food_ki, tab_food_man = st.tabs(["🤖 KI", "✍️ Manuell"])
        with tab_food_ki:
            f_ki = st.text_input("Was gab es?", key="food_ki")
            if st.button("Essen schätzen 🚀"):
                res = analyze_food_input(f_ki)
                if res:
                    log_food(user_id, heute, res["gericht"], res["kalorien"])
                    st.rerun()
        with tab_food_man:
            f_n = st.text_input("Gericht", key="food_m")
            f_k = st.number_input("kcal", min_value=0, value=300, key="food_mk")
            if st.button("Essen loggen 💾"):
                log_food(user_id, heute, f_n, f_k)
                st.rerun()

    with col_sport:
        st.subheader("🏃‍♂️ Sport-Tracking")
        tab_sport_ki, tab_sport_man = st.tabs(["🤖 KI", "✍️ Manuell"])
        with tab_sport_ki:
            s_ki = st.text_input("Was hast du gemacht?", placeholder="z.B. 30 Min Joggen", key="sport_ki")
            if st.button("Sport schätzen 🔥"):
                res = analyze_exercise_input(s_ki)
                if res:
                    log_exercise(user_id, heute, res["aktivitaet"], res["kalorien"])
                    st.rerun()
        with tab_sport_man:
            s_n = st.text_input("Aktivität", key="sport_m")
            s_k = st.number_input("kcal verbrannt", min_value=0, value=200, key="sport_mk")
            if st.button("Sport loggen 💾"):
                log_exercise(user_id, heute, s_n, s_k)
                st.rerun()

    st.write("---")

    # Tagebücher anzeigen
    col_log1, col_log2 = st.columns(2)
    with col_log1:
        st.markdown("### 🍎 Essen heute")
        for m in get_todays_food(user_id, heute):
            c1, c2 = st.columns([0.8, 0.2])
            c1.caption(f"{m['food_text']} ({m['calories']} kcal)")
            if c2.button("🗑️", key=f"df_{m['id']}"):
                delete_food_log(m['id'])
                st.rerun()
    
    with col_log2:
        st.markdown("### ⚡ Sport heute")
        for e in get_todays_exercises(user_id, heute):
            c1, c2 = st.columns([0.8, 0.2])
            c1.caption(f"{e['activity_text']} (-{e['calories']} kcal)")
            if c2.button("🗑️", key=f"de_{e['id']}"):
                delete_exercise_log(e['id'])
                st.rerun()

    st.write("---")

    # ==========================================
    # 3. BERECHNUNG & METRIKEN
    # ==========================================
    gegessen = get_consumed_calories(user_id, heute)
    verbrannt = get_burned_calories(user_id, heute) # Jetzt aus der DB!

    uebrig = ziel_kalorien - gegessen + verbrannt

    bal_col1, bal_col2, bal_col3, bal_col4 = st.columns(4)
    bal_col1.metric("🎯 Ziel", f"{ziel_kalorien} kcal")
    bal_col2.metric("🍽️ Gegessen", f"{gegessen} kcal")
    bal_col3.metric("🏃‍♂️ Verbrannt", f"{verbrannt} kcal")

    if uebrig < 0:
        bal_col4.metric("🚨 Übrig", f"{uebrig} kcal", delta="Limit!", delta_color="inverse")
    else:
        bal_col4.metric("✅ Übrig", f"{uebrig} kcal")
    
    # ... hier kommt dein restlicher Gamification-Code (XP abholen etc.)

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