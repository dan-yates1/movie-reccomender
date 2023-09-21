from fastapi import FastAPI, HTTPException
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import pairwise_distances

app = FastAPI()

# Load data
movies = pd.read_csv('movies.csv')
ratings = pd.read_csv('ratings.csv')

# Create a user-item matrix
user_movie_ratings = ratings.pivot(index='userId', columns='movieId', values='rating')

# Compute the cosine similarity matrix using pairwise distances
cosine_sim = 1 - pairwise_distances(user_movie_ratings.fillna(0), metric='cosine')

# Convert into a DataFrame for better readability
cosine_sim_df = pd.DataFrame(cosine_sim, index=user_movie_ratings.index, columns=user_movie_ratings.index)

def recommend_movies_for_user(user_id: int, num_movies: int = 10):
    if user_id not in user_movie_ratings.index:
        raise ValueError("User ID not found in the database.")
    
    # Get the similarity scores for the user
    user_sim_scores = cosine_sim_df.loc[user_id]
    
    # Get the list of movies rated by this user
    user_movies = user_movie_ratings.loc[user_id].dropna().index
    
    # Sort users by similarity to the input user
    similar_users = user_sim_scores.sort_values(ascending=False).drop(user_id).index
    
    # Recommend movies from similar users
    recommended_movies = []
    for similar_user in similar_users:
        similar_user_movies = user_movie_ratings.loc[similar_user].dropna().index
        new_recommendations = set(similar_user_movies) - set(user_movies) - set(recommended_movies)
        recommended_movies.extend(new_recommendations)
        
        if len(recommended_movies) > num_movies:
            break

    recommended_df = movies[movies['movieId'].isin(recommended_movies[:num_movies])]
    return recommended_df.to_dict(orient='records')

@app.get("/recommendations/{user_id}")
async def get_recommendations(user_id: int, num_movies: int = 10):
    try:
        movies = recommend_movies_for_user(user_id, num_movies)
        return {"movies": movies}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
