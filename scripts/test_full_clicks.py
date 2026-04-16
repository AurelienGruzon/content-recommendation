from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data.load_data import load_all_clicks, load_embeddings, load_articles_metadata
from src.recommender.baseline import recommend_articles, format_recommendations

DATA_DIR = Path("data/news-portal-user-interactions-by-globocom")

clicks = load_all_clicks(DATA_DIR)
embeddings = load_embeddings(DATA_DIR)
articles_metadata = load_articles_metadata(DATA_DIR)

user_id = 0
reco_ids = recommend_articles(user_id=user_id, clicks_df=clicks, embeddings=embeddings)
reco_payload = format_recommendations(reco_ids, articles_metadata)

print(f"user_id={user_id}")
print("recommendation_ids=", reco_ids)
print("recommendation_payload=", reco_payload)