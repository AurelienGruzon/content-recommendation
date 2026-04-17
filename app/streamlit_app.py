from pathlib import Path
import sys

import pandas as pd
import requests
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.data.load_data import load_all_clicks

DATA_DIR = PROJECT_ROOT / "data" / "news-portal-user-interactions-by-globocom"
#API_URL = "http://localhost:7071/api/recommend_articles"
API_URL = "https://content-recommendation-bcgdhjabgtcyfua7.francecentral-01.azurewebsites.net/api/recommend_articles"


@st.cache_data
def get_available_user_ids(limit: int = 1000) -> list[int]:
    """
    Charge les user_id disponibles depuis le dataset complet.
    On limite volontairement la liste affichée pour garder une interface fluide.
    """
    clicks = load_all_clicks(DATA_DIR)
    user_ids = sorted(clicks["user_id"].dropna().astype(int).unique().tolist())
    return user_ids[:limit]


def format_timestamp(ts_ms: int) -> str:
    """
    Convertit un timestamp millisecondes en date lisible.
    """
    try:
        return pd.to_datetime(ts_ms, unit="ms").strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts_ms)


st.set_page_config(page_title="My Content - Recommandations", layout="wide")

st.title("📚 My Content - MVP Recommandation")
st.write(
    "Sélectionnez un identifiant utilisateur dans la liste ou saisissez-en un manuellement, "
    "puis lancez la recommandation."
)

available_user_ids = get_available_user_ids(limit=1000)

selected_user_id = st.selectbox(
    "Liste d'identifiants utilisateurs (échantillon réel du dataset)",
    options=available_user_ids,
    index=0,
)

manual_user_id = st.text_input(
    "Ou saisir un user_id manuellement",
    value=str(selected_user_id),
)

if st.button("Obtenir les recommandations"):
    try:
        user_id = int(manual_user_id)

        with st.spinner("Calcul des recommandations..."):
            response = requests.get(
                API_URL,
                params={"user_id": user_id},
                timeout=60,
            )

        if response.status_code == 200:
            data = response.json()

            st.success(f"Recommandations pour user_id = {data['user_id']}")

            recommendations = data.get("recommendations", [])

            if not recommendations:
                st.warning("Aucune recommandation retournée.")
            else:
                for idx, article in enumerate(recommendations, start=1):
                    with st.container():
                        st.markdown(f"### Recommandation {idx}")
                        st.write(f"**Article ID** : {article['article_id']}")
                        st.write(f"**Catégorie** : {article['category_id']}")
                        st.write(f"**Nombre de mots** : {article['words_count']}")
                        st.write(
                            f"**Date de création** : "
                            f"{format_timestamp(article['created_at_ts'])}"
                        )
                        st.divider()

        else:
            st.error(f"Erreur API ({response.status_code}) : {response.text}")

    except ValueError:
        st.error("Veuillez saisir un user_id entier valide.")
    except requests.RequestException as exc:
        st.error(f"Impossible de joindre l'API : {exc}")