## Fonctionnement général

Le projet consiste à recommander 5 articles personnalisés à un utilisateur à partir de son historique de lecture.

### Architecture MVP

1. L’utilisateur sélectionne un `user_id` dans l’interface Streamlit  
2. Une requête HTTP est envoyée à l’API Azure Functions  
3. Le moteur de recommandation calcule les articles les plus pertinents  
4. Les résultats enrichis (catégorie, date, longueur article) sont affichés

## Approche retenue

Le moteur principal repose sur une approche **Content-Based Filtering** utilisant :

- l’historique de clics utilisateur
- les embeddings des articles
- une similarité cosinus entre profil utilisateur et contenus disponibles

## Gestion des cold starts

- Nouvel utilisateur : fallback sur les articles les plus populaires
- Nouvel article : recommandable dès disponibilité de son embedding

## Auteur

Aurélien Gruzon  
Projet réalisé dans le cadre de la formation OpenClassrooms.