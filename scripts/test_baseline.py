from pathlib import Path

from src.data.load_data import load_clicks_sample, load_embeddings
from src.recommender.baseline import recommend_articles

DATA_DIR = Path("data/news-portal-user-interactions-by-globocom")

clicks_sample = load_clicks_sample(DATA_DIR)
embeddings = load_embeddings(DATA_DIR)

user_id = 681
reco = recommend_articles(user_id=user_id, clicks_df=clicks_sample, embeddings=embeddings)

print(f"user_id={user_id}")
print("recommendations=", reco)