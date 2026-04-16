import json
import sys
from pathlib import Path

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.data.load_data import (
    load_all_clicks,
    load_articles_metadata,
    load_embeddings,
)
from src.recommender.baseline import recommend_articles, format_recommendations

DATA_DIR = PROJECT_ROOT / "data" / "news-portal-user-interactions-by-globocom"

# Chargement au démarrage
ARTICLES_METADATA = load_articles_metadata(DATA_DIR)
CLICKS = load_all_clicks(DATA_DIR)
EMBEDDINGS = load_embeddings(DATA_DIR)


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
            json.dumps(response),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
        )