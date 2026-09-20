import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import date

st.set_page_config(page_title="Lumen Sports AI", page_icon="🏆", layout="wide")

st.title("🏆 Lumen Sports AI")
st.caption("Estimaciones estadísticas — no son garantías ni asesoramiento financiero.")

SPORTS = {
    "NBA": "basketball/nba",
    "NFL": "football/nfl",
    "MLB": "baseball/mlb",
    "NHL": "hockey/nhl",
    "Fútbol — Premier League": "soccer/eng.1",
    "Fútbol — La Liga": "soccer/esp.1",
    "Fútbol — Champions League": "soccer/uefa.champions",
    "NCAAF": "football/college-football",
    "NCAAB": "basketball/mens-college-basketball",
}

def logistic(x):
    return 1 / (1 + np.exp(-x))

def estimate(home_rating, away_rating, home_advantage, home_form, away_form):
    edge = (home_rating - away_rating) + home_advantage + (home_form - away_form) * 0.35
    home_win = float(logistic(edge / 8))
    away_win = 1 - home_win
    return home_win, away_win

@st.cache_data(ttl=300)
def get_scoreboard(league, selected_date):
    url = f"https://site.api.espn.com/apis/site/v2/sports/{league}/scoreboard"
    response = requests.get(url, params={"dates": selected_date}, timeout=15)
    response.raise_for_status()
    return response.json()

with st.sidebar:
    st.header("⚙️ Configuración")
    mode = st.radio("Modo", ["Automático (ESPN)", "Manual"], index=0)
    sport = st.selectbox("Deporte / liga", list(SPORTS.keys()))
    selected_date = st.date_input("Fecha", value=date.today())

if mode == "Automático (ESPN)":
    st.subheader(f"Partidos disponibles — {sport}")
    try:
        data = get_scoreboard(SPORTS[sport], selected_date.strftime("%Y%m%d"))
        events = data.get("events", [])
        if not events:
            st.info("No se encontraron partidos para esa fecha. Prueba otra fecha o usa el modo manual.")
        for event in events:
            competition = event.get("competitions", [{}])[0]
            competitors = competition.get("competitors", [])
            if len(competitors) < 2:
                continue
            names = [c.get("team", {}).get("displayName", "Equipo") for c in competitors]
            home = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
            away = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1])
            home_name = home.get("team", {}).get("displayName", "Local")
            away_name = away.get("team", {}).get("displayName", "Visitante")
            with st.expander(f"{home_name} vs {away_name}"):
                st.warning("La fuente proporciona el partido, pero no siempre proporciona todas las variables predictivas.")
                c1, c2 = st.columns(2)
                with c1:
                    hr = st.slider("Rating local", 60, 100, 80, key=f"hr{event['id']}")
                    hf = st.slider("Forma local (-10 a +10)", -10, 10, 0, key=f"hf{event['id']}")
                with c2:
                    ar = st.slider("Rating visitante", 60, 100, 78, key=f"ar{event['id']}")
                    af = st.slider("Forma visitante (-10 a +10)", -10, 10, 0, key=f"af{event['id']}")
                ha = st.slider("Ventaja de local", 0.0, 8.0, 2.5, 0.5, key=f"ha{event['id']}")
                p_home, p_away = estimate(hr, ar, ha, hf, af)
                st.metric(f"{home_name} gana", f"{p_home:.1%}")
                st.metric(f"{away_name} gana", f"{p_away:.1%}")
                st.caption("Estos valores son un modelo inicial configurable; no representan una predicción validada para apuestas.")
    except Exception as exc:
        st.error("No se pudo cargar la fuente automática.")
        st.code(str(exc))
        st.info("Puedes usar el modo manual mientras revisas la conexión.")

else:
    st.subheader("🧮 Calculadora manual")
    home_name = st.text_input("Equipo local", "Equipo A")
    away_name = st.text_input("Equipo visitante", "Equipo B")
    c1, c2 = st.columns(2)
    with c1:
        hr = st.slider("Rating local", 60, 100, 80)
        hf = st.slider("Forma local (-10 a +10)", -10, 10, 0)
    with c2:
        ar = st.slider("Rating visitante", 60, 100, 78)
        af = st.slider("Forma visitante (-10 a +10)", -10, 10, 0)
    ha = st.slider("Ventaja de local", 0.0, 8.0, 2.5, 0.5)
    p_home, p_away = estimate(hr, ar, ha, hf, af)
    results = pd.DataFrame({
        "Resultado": [f"{home_name} gana", f"{away_name} gana"],
        "Probabilidad": [p_home, p_away]
    })
    st.dataframe(results.style.format({"Probabilidad": "{:.1%}"}), use_container_width=True)
    st.bar_chart(results.set_index("Resultado"))
    st.info("Para una versión de producción se deben añadir bases de datos históricas, lesiones, cuotas, calibración y pruebas fuera de muestra.")

st.divider()
st.caption("Proyecto inicial de Lumen Sports AI. Verifica datos y resultados independientemente.")
