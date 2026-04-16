import requests
import streamlit as st

API_URL = "http://localhost:7071/api/recommend_articles"

st.set_page_config(page_title="My Content - Recommandations", layout="wide")

st.title("📚 My Content - MVP Recommandation")

st.write("Sélectionnez un utilisateur pour obtenir 5 recommandations d’articles.")

# Exemple simple de liste d'utilisateurs
sample_user_ids = [0, 1, 2, 10, 50, 100, 500, 1000]

selected_user_id = st.selectbox(
    "Choisissez un user_id",
    options=sample_user_ids,
)

if st.button("Obtenir les recommandations"):
    with st.spinner("Calcul des recommandations..."):
        response = requests.get(
            API_URL,
            params={"user_id": selected_user_id},
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()

            st.success(f"Recommandations pour user {data['user_id']}")

            for idx, article in enumerate(data["recommendations"], start=1):
                st.card if False else None  # évite warning IDE

                with st.container():
                    st.markdown(f"### Article {idx}")
                    st.write(f"**Article ID** : {article['article_id']}")
                    st.write(f"**Catégorie** : {article['category_id']}")
                    st.write(f"**Nombre de mots** : {article['words_count']}")
                    st.write(f"**Timestamp** : {article['created_at_ts']}")
                    st.divider()
        else:
            st.error(f"Erreur API : {response.text}")