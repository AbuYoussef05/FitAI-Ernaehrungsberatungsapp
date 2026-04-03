import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from database.db_manager import log_weight, get_weight_history, get_user_profile
from ai.gemini_service import client

def show_fortschritt():
    user_id = st.session_state.user_id
    profile = get_user_profile(user_id)

    st.title("📈 Dein Fortschritt & KI-Analyse")
    st.write("---")

    # ==========================================
    # 1. TRACKING-EINGABE (Gewicht)
    # ==========================================
    with st.expander("➕ Heutige Daten loggen", expanded=True):
        col1, col2 = st.columns(2)
        new_weight = col1.number_input("Gewicht (kg)", min_value=30.0, max_value=250.0, value=float(profile["weight"]), step=0.1)
        log_date = col2.date_input("Datum", date.today())
        
        if st.button("💾 Speichern", type="primary"):
            log_weight(user_id, new_weight, str(log_date))
            st.success("Daten erfolgreich gespeichert!")
            st.rerun()

    st.write("---")

    # ==========================================
    # DATEN LADEN & PLOTLY DIAGRAMM
    # ==========================================
    history = get_weight_history(user_id)

    if history:
        df = pd.DataFrame(history, columns=["Datum", "Gewicht"])
        df["Datum"] = pd.to_datetime(df["Datum"])
        df = df.sort_values(by="Datum")
        
        st.subheader("📊 Dein Gewichtsverlauf")
        fig = px.line(df, x="Datum", y="Gewicht", markers=True, 
                    title="Gewicht über Zeit", 
                    color_discrete_sequence=["#00b87c"])
        fig.update_layout(yaxis_title="Gewicht in kg", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
        
        # WARN-SYSTEM
        st.subheader("⚙️ System-Analyse")
        if len(df) >= 2:
            erstes_gewicht = df.iloc[0]["Gewicht"]
            letztes_gewicht = df.iloc[-1]["Gewicht"]
            differenz = letztes_gewicht - erstes_gewicht
            ziel = profile.get("goal", "Abnehmen")
            
            if ziel == "Abnehmen" and differenz > 0:
                st.warning(f"⚠️ **Achtung:** Dein Ziel ist Abnehmen, aber du hast {differenz:.1f} kg zugenommen.")
                if differenz > 1.5:
                    st.error("🚨 **Starke Abweichung erkannt!**")
                    st.info("💡 **Vorschlag:** Wir sollten deinen Kalorienbedarf neu berechnen.")
            elif ziel == "Muskelaufbau" and differenz < 0:
                st.warning(f"⚠️ **Achtung:** Dein Ziel ist Muskelaufbau, aber du hast {abs(differenz):.1f} kg abgenommen.")
            else:
                st.success("✅ **Super!** Du bist auf einem guten Weg in Richtung deines Ziels.")
        else:
            st.info("Trage an mindestens 2 verschiedenen Tagen dein Gewicht ein, um das Warn-System zu aktivieren.")

        st.write("---")

        # KI-MUSTERERKENNUNG
        st.subheader("🤖 KI-Fortschrittsanalyse")
        if st.button("✨ Fortschritt analysieren", use_container_width=True):
            if client:
                with st.spinner("Gemini analysiert deine Daten..."):
                    prompt = f"""
                    Analysiere diesen Gewichtsverlauf: {history}
                    Ziel des Nutzers: {profile.get('goal')}.
                    Gib ein kurzes Feedback (max. 3 Sätze).
                    """
                    try:
                        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                        st.info(f"**Coach sagt:**\n\n{response.text}")
                    except Exception:
                        st.error("API blockiert. **Coach sagt:** Du stagnierst leicht. Achte auf dein Kaloriendefizit!")
            else:
                st.info("**Coach sagt (Mock):** Du stagnierst leicht. Achte auf dein Kaloriendefizit!")

    else:
        st.info("Noch keine Daten vorhanden. Trag oben dein erstes Gewicht ein!")