import pickle
import streamlit as st
import requests

# ---- Streamlit Config ----
st.set_page_config(page_title="Movie Recommender", layout="wide")

# ---- Load Data ----
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Ensure title column is clean
movies['title'] = movies['title'].str.strip().str.lower()

# TMDb API Key (Replace with your own key if needed)
API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

# ---- Caching API Calls ----
@st.cache_data(show_spinner=False)
def fetch_movie_details(movie_id):
    """Fetch movie details including poster and trailer from TMDb API"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US&append_to_response=videos"
    response = requests.get(url).json()
    
    poster_path = response.get("poster_path", "")
    poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Image"

    release_date = response.get("release_date", "Unknown")[:4]  # Extract year
    rating = response.get("vote_average", "N/A")

    # Get trailer if available
    videos = response.get("videos", {}).get("results", [])
    trailer_url = ""
    for video in videos:
        if video["site"] == "YouTube" and video["type"] == "Trailer":
            trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
            break
    
    return poster_url, trailer_url, release_date, rating

# ---- Movie Recommendation Logic ----
def recommend(movie):
    """Finds the most similar movies based on content features"""
    movie = movie.strip().lower()

    if movie not in movies['title'].values:
        return []

    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movies = []
    for i in distances[1:6]:  # Get top 5 recommendations
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title.title()
        poster, trailer, release_date, rating = fetch_movie_details(movie_id)
        recommended_movies.append((title, poster, trailer, release_date, rating))

    return recommended_movies

# ---- Custom CSS Styling for a Professional Look ----
st.markdown("""
    <style>
        /* Global styles */
        body {
            background-color: #f8f9fa;
        }
        .title {
            font-size: 40px !important;
            font-weight: bold;
            text-align: center;
            color: #2C3E50;
            padding: 10px;
        }
        .subtitle {
            font-size: 20px;
            text-align: center;
            color: #7F8C8D;
            padding-bottom: 20px;
        }
        .stButton>button {
            background-color: #e74c3c;
            color: white;
            border-radius: 8px;
            font-size: 18px;
            padding: 10px 20px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #c0392b;
            transform: scale(1.05);
        }
        .poster {
            border-radius: 15px;
            box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.2);
            margin-bottom: 10px;
        }
        .movie-box {
            text-align: center;
            padding: 10px;
        }
        .movie-title {
            font-size: 16px;
            font-weight: bold;
            color: #2C3E50;
            margin-top: 5px;
        }
        .movie-info {
            font-size: 14px;
            color: #7F8C8D;
        }
        /* New Watch Trailer Button */
        .trailer-btn {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 8px 15px;
            font-size: 14px;
            font-weight: bold;
            text-decoration: none;
            border-radius: 20px;
            transition: 0.3s;
        }
        .trailer-btn:hover {
            background-color: #2980b9;
            transform: scale(1.05);
        }
    </style>
""", unsafe_allow_html=True)

# ---- Header Section ----
st.markdown('<p class="title">🎬 Movie Recommender System</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Find movies similar to your favorites</p>', unsafe_allow_html=True)

# ---- Dropdown for Movie Selection (No default selection) ----
movie_list_display = movies['title'].str.title().sort_values().unique()
selected_movie = st.selectbox("🎬 Select a movie", [""] + list(movie_list_display))  # Empty default

# ---- Recommend Button ----
if st.button("🔍 Recommend"):
    if not selected_movie:
        st.warning("Please select a movie before proceeding!")
    else:
        with st.spinner("Fetching recommendations..."):
            recommendations = recommend(selected_movie)

        if recommendations:
            st.subheader("📌 Top Recommendations:")

            # Create a grid-based layout
            cols = st.columns(5)
            
            for i, (title, poster, trailer, release_date, rating) in enumerate(recommendations):
                with cols[i]:
                    st.markdown(f'<div class="movie-box">', unsafe_allow_html=True)
                    st.image(poster, use_container_width=True, caption=f"⭐ {rating} | 📅 {release_date}", output_format="auto", width=200)
                    st.markdown(f'<p class="movie-title">{title}</p>', unsafe_allow_html=True)
                    
                    if trailer:
                        st.markdown(f'<a href="{trailer}" target="_blank" class="trailer-btn">🎬 Watch Trailer</a>', unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("No recommendations found. Try another movie!")
