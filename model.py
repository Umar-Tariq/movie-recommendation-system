import numpy as np
import pandas as pd
import ast
import nltk
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Load data
movies = pd.read_csv('/content/drive/MyDrive/datasets/Movie/tmdb_5000_movies.csv')
credits = pd.read_csv('/content/drive/MyDrive/datasets/Movie/tmdb_5000_credits.csv')

# Merge datasets
movies = movies.merge(credits, on='title')

# Keep only useful columns
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
movies.dropna(inplace=True)

# --- Helper Functions ---

# Convert JSON string to list of names
def convert(text):
    return [i['name'] for i in ast.literal_eval(text)]

def convert3(text):
    return [i['name'] for i in ast.literal_eval(text)[:3]]

def fetch_director(text):
    return [i['name'] for i in ast.literal_eval(text) if i['job'] == 'Director']

def collapse(L):
    return [i.replace(" ", "") for i in L]

# Apply transformations
movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(convert3)
movies['crew'] = movies['crew'].apply(fetch_director)
movies['overview'] = movies['overview'].apply(lambda x: x.split())

# Remove spaces from tags
for col in ['cast', 'crew', 'genres', 'keywords']:
    movies[col] = movies[col].apply(collapse)

# Combine all tags
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']
new = movies.drop(columns=['overview', 'genres', 'keywords', 'cast', 'crew'])

# Convert list to string
new['tags'] = new['tags'].apply(lambda x: " ".join(x))

# Stemming
ps = PorterStemmer()
def stem(text):
    return " ".join([ps.stem(i) for i in text.split()])

new["tags"] = new['tags'].apply(stem)

# Vectorization
cv = CountVectorizer(max_features=5000, stop_words='english')
vector = cv.fit_transform(new['tags']).toarray()

# Similarity matrix
similarity = cosine_similarity(vector)

# Lowercase titles for consistency
new['title'] = new['title'].str.lower()

# Recommendation function with error handling
def recommend(movie):
    movie = movie.lower()
    if movie not in new['title'].values:
        print("Movie not found.")
        return
    index = new[new['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    for i in distances[1:6]:
        print(new.iloc[i[0]].title.title())  # Title-cased for nice formatting

# Example usage
recommend('Batman Begins')

# Save data and similarity matrix
pickle.dump(new, open('movie_list.pkl', 'wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))
