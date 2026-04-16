import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def get_user_history(user_id: int, clicks_df: pd.DataFrame) -> np.ndarray:
    """Retourne les article_id déjà consultés par l'utilisateur."""
    history = clicks_df.loc[
        clicks_df["user_id"] == user_id,
        "click_article_id"
    ].dropna().astype(np.int64).unique()

    return history


def build_user_profile(user_history: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
    """Construit le profil utilisateur par moyenne des embeddings vus."""
    user_history = np.asarray(user_history, dtype=np.int64)
    user_vectors = embeddings[user_history]
    return user_vectors.mean(axis=0).reshape(1, -1)


def get_most_popular_articles(clicks_df: pd.DataFrame, top_k: int = 5) -> list[int]:
    """Retourne les articles les plus populaires."""
    return (
        clicks_df["click_article_id"]
        .value_counts()
        .head(top_k)
        .index.astype(int)
        .tolist()
    )


def recommend_articles(
    user_id: int,
    clicks_df: pd.DataFrame,
    embeddings: np.ndarray,
    top_k: int = 5,
) -> list[int]:
    """Retourne les top_k recommandations pour un utilisateur."""
    history = get_user_history(user_id, clicks_df)

    if len(history) == 0:
        return get_most_popular_articles(clicks_df, top_k=top_k)

    user_profile = build_user_profile(history, embeddings)
    similarities = cosine_similarity(user_profile, embeddings)[0]
    candidate_ids = np.argsort(similarities)[::-1]

    history_set = set(history.tolist())

    recommendations = [
        int(article_id)
        for article_id in candidate_ids
        if int(article_id) not in history_set
    ][:top_k]

    return recommendations

def format_recommendations(
    article_ids: list[int],
    articles_metadata: pd.DataFrame,
) -> list[dict]:
    """Enrichit les recommandations avec les métadonnées."""
    meta = articles_metadata.loc[
        articles_metadata["article_id"].isin(article_ids),
        ["article_id", "category_id", "created_at_ts", "words_count"]
    ].copy()

    meta = meta.set_index("article_id").loc[article_ids].reset_index()

    return meta.to_dict(orient="records")