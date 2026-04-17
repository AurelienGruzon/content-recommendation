import json
from pathlib import Path

import azure.functions as func
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

ARTICLES_METADATA = pd.read_csv(DATA_DIR / "articles_metadata.csv")
CLICKS = pd.read_csv(DATA_DIR / "clicks_sample.csv")
EMBEDDINGS = np.load(DATA_DIR / "articles_embeddings_reduced.npy")


def get_user_history(user_id: int, clicks_df: pd.DataFrame) -> np.ndarray:
    return (
        clicks_df.loc[clicks_df["user_id"] == user_id, "click_article_id"]
        .dropna()
        .astype(np.int64)
        .unique()
    )


def build_user_profile(user_history: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
    user_history = np.asarray(user_history, dtype=np.int64)
    user_vectors = embeddings[user_history]
    return user_vectors.mean(axis=0).reshape(1, -1)


def get_most_popular_articles(clicks_df: pd.DataFrame, top_k: int = 5) -> list[int]:
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
    meta = articles_metadata.loc[
        articles_metadata["article_id"].isin(article_ids),
        ["article_id", "category_id", "created_at_ts", "words_count"],
    ].copy()

    if meta.empty:
        return []

    meta = meta.set_index("article_id").reindex(article_ids).reset_index()
    meta = meta.dropna(subset=["article_id"])

    meta["article_id"] = meta["article_id"].astype(int)
    meta["category_id"] = meta["category_id"].astype(int)
    meta["created_at_ts"] = meta["created_at_ts"].astype(int)
    meta["words_count"] = meta["words_count"].astype(int)

    return meta.to_dict(orient="records")


@app.route(route="recommend_articles", methods=["GET", "POST"])
def recommend_articles_http(req: func.HttpRequest) -> func.HttpResponse:
    try:
        user_id_raw = req.params.get("user_id")

        if user_id_raw is None:
            try:
                req_body = req.get_json()
            except ValueError:
                req_body = {}
            user_id_raw = req_body.get("user_id")

        if user_id_raw is None:
            return func.HttpResponse(
                json.dumps({"error": "Missing user_id"}),
                status_code=400,
                mimetype="application/json",
            )

        user_id = int(user_id_raw)

        recommendation_ids = recommend_articles(
            user_id=user_id,
            clicks_df=CLICKS,
            embeddings=EMBEDDINGS,
            top_k=5,
        )

        recommendation_payload = format_recommendations(
            recommendation_ids,
            ARTICLES_METADATA,
        )

        response = {
            "user_id": user_id,
            "recommendations": recommendation_payload,
        }

        return func.HttpResponse(
            json.dumps(response, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )

    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "user_id must be an integer"}),
            status_code=400,
            mimetype="application/json",
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
        )