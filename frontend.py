import streamlit as st
import pickle
import pandas as pd
import requests

# Load movie data
movies_dict = pickle.load(open('movies.pkl', 'rb'))
movies_df = pd.DataFrame(movies_dict)  # Convert dictionary to DataFrame

# Load similarity matrix
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Get movie titles
movies_list = movies_df['title'].values

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
 # Your OMDB API key

def fetch_poster(movie_name):
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'Poster' in data and data['Poster'] != "N/A":
            return data['Poster']  # Return the poster URL from OMDB
        else:
            return "https://via.placeholder.com/500"  # Default image if no poster found

    except requests.exceptions.RequestException as e:
        print(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/500"  # Default fallback image

# Function to recommend movies
def recommend(movie):
    try:
        index = movies_df[movies_df['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        
        recommended_movie_names = []
        recommended_movie_posters = []
        for i in distances[1:6]:  # Get top 5 recommended movies
            movie_name = movies_df.iloc[i[0]].title
            recommended_movie_names.append(movie_name)
            recommended_movie_posters.append(fetch_poster(movie_name))  # ✅ Fixed here

        return recommended_movie_names, recommended_movie_posters
    except IndexError:
        return ["No recommendations found!"], []

# Streamlit UI
st.title("Movie Recommender System")

selected_movie_name = st.selectbox("Select a movie:", movies_list)

if st.button("Recommend"):
    recommended_names, recommended_posters = recommend(selected_movie_name)
    
    # Display recommended movies with posters
    cols = st.columns(5)  # Create 5 columns for displaying recommendations
    for i in range(len(recommended_names)):
        with cols[i]:
            st.image(recommended_posters[i], use_container_width=True)  # ✅ Updated
            st.write(recommended_names[i])
