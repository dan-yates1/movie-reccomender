from fastapi import FastAPI, HTTPException
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import pairwise_distances
from typing import List

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

movies = pd.read_csv('movies.csv')
ratings = pd.read_csv('ratings.csv')

user_movie_ratings = ratings.pivot(
    index='userId', columns='movieId', values='rating')

cosine_sim = 1 - \
    pairwise_distances(user_movie_ratings.fillna(0), metric='cosine')

cosine_sim_df = pd.DataFrame(
    cosine_sim, index=user_movie_ratings.index, columns=user_movie_ratings.index)


def recommend_movies_for_user(user_id: int, num_movies: int = 10):
    if user_id not in user_movie_ratings.index:
        raise ValueError("User ID not found in the database.")

    user_sim_scores = cosine_sim_df.loc[user_id]

    user_movies = user_movie_ratings.loc[user_id].dropna().index

    similar_users = user_sim_scores.sort_values(
        ascending=False).drop(user_id).index

    recommended_movies = []
    for similar_user in similar_users:
        similar_user_movies = user_movie_ratings.loc[similar_user].dropna(
        ).index
        new_recommendations = set(similar_user_movies) - \
            set(user_movies) - set(recommended_movies)
        recommended_movies.extend(new_recommendations)

        if len(recommended_movies) > num_movies:
            break

    recommended_df = movies[movies['movieId'].isin(
        recommended_movies[:num_movies])]
    return recommended_df.to_dict(orient='records')


@app.get("/recommendations/{user_id}")
async def get_recommendations(user_id: int, num_movies: int = 10):
    try:
        movies = recommend_movies_for_user(user_id, num_movies)
        return {"movies": movies}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/initial_recommendations/")
async def initial_recommendations(ratings: dict):
    # The ratings dictionary will contain movie IDs as keys and ratings as values.

    # For demonstration, if a user likes a movie, we'll just recommend movies that are
    # most similar to the one liked. A more sophisticated implementation can combine multiple
    # ratings and use a recommendation model.

    movie_id = list(ratings.keys())[0]
    rating_value = ratings[movie_id]

    if rating_value == 'like':  # Use collaborative filtering to find similar movies
        similar_movies = cosine_similarity(user_movie_ratings.fillna(0).T)
        similar_movies_df = pd.DataFrame(
            similar_movies, index=user_movie_ratings.columns, columns=user_movie_ratings.columns)
        recommendations = similar_movies_df[int(
            movie_id)].sort_values(ascending=False).head(10)
        recommended_movies = movies[movies['movieId'].isin(
            recommendations.index)].to_dict(orient='records')
        return {"movies": recommended_movies}

    elif rating_value == 'dislike':
        # Here, you can recommend some other popular movies or use another logic.
        # Just an example to return top 5 movies.
        return {"movies": get_top_movies(5)}


@app.post("/rate_movie/")
def rate_movie(user_id: int, movie_id: int, rating: float, db: Session = Depends(get_db)):
    user_rating = UserRating(user_id=user_id, movie_id=movie_id, rating=rating)
    db.add(user_rating)
    db.commit()
    return {"message": "Rating saved successfully!"}
