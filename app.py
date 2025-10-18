from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import csv
import math
from collections import Counter, defaultdict
import os

app = Flask(__name__)
CORS(app)

# ===============================
# LOAD DATASET (NO PANDAS)
# ===============================
DATA_PATH = "items_4000.csv"
movies = []

print("Loading dataset...")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        title = row.get("title", "").strip()
        genres = row.get("genres", "").strip()
        description = row.get("description", "").strip()
        year = row.get("year", "").strip()

        movies.append({
            "title": title,
            "genres": genres,
            "description": description,
            "year": year
        })

print(f"Loaded {len(movies)} movies.")

# ===============================
# TEXT PROCESSING UTILITIES
# ===============================
def tokenize(text):
    """Basic word tokenizer."""
    tokens = []
    word = ""
    for ch in text.lower():
        if ch.isalnum():
            word += ch
        elif word:
            tokens.append(word)
            word = ""
    if word:
        tokens.append(word)
    return tokens


# Combine movie features into a single text
corpus = [
    (m["genres"] + " " + m["description"] + " " + str(m["year"])).strip()
    for m in movies
]

# Tokenize all movie documents
documents = [tokenize(doc) for doc in corpus]
vocab = set(word for doc in documents for word in doc)
vocab = list(vocab)

# ===============================
# COMPUTE TF-IDF MANUALLY
# ===============================
def compute_tfidf(docs):
    """Compute TF-IDF vectors manually."""
    N = len(docs)
    df = defaultdict(int)
    for doc in docs:
        for word in set(doc):
            df[word] += 1

    tfidf_vectors = []
    for doc in docs:
        tf = Counter(doc)
        vector = {}
        for word, count in tf.items():
            idf = math.log((1 + N) / (1 + df[word])) + 1
            vector[word] = (count / len(doc)) * idf
        tfidf_vectors.append(vector)
    return tfidf_vectors


print("Building TF-IDF vectors...")
tfidf_vectors = compute_tfidf(documents)
print("Model ready ✅")

# ===============================
# COSINE SIMILARITY (MANUAL)
# ===============================
def cosine_sim(v1, v2):
    common = set(v1.keys()) & set(v2.keys())
    num = sum(v1[w] * v2[w] for w in common)
    denom1 = math.sqrt(sum(v**2 for v in v1.values()))
    denom2 = math.sqrt(sum(v**2 for v in v2.values()))
    if denom1 == 0 or denom2 == 0:
        return 0.0
    return num / (denom1 * denom2)

# ===============================
# RECOMMENDATION FUNCTION
# ===============================
def recommend_movies(user_genre, user_description, user_year, n=5):
    """Recommend movies based on genre + description + year input."""
    query_text = f"{user_genre} {user_description} {user_year}"
    query_tokens = tokenize(query_text)

    # Compute TF-IDF for user input (same formula)
    N = len(documents)
    df = defaultdict(int)
    for doc in documents:
        for word in set(doc):
            df[word] += 1

    tf = Counter(query_tokens)
    query_vec = {}
    for word, count in tf.items():
        idf = math.log((1 + N) / (1 + df.get(word, 0))) + 1
        query_vec[word] = (count / len(query_tokens)) * idf

    # Compute similarity with all movies
    scores = []
    for i, vec in enumerate(tfidf_vectors):
        score = cosine_sim(query_vec, vec)
        scores.append((i, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    top = scores[:n]
    recs = []
    for i, score in top:
        rec = movies[i].copy()
        rec["similarity"] = round(score, 4)
        recs.append(rec)
    return recs

# ===============================
# API ROUTES
# ===============================
@app.route("/recommend", methods=["POST"])
def recommend_endpoint():
    """POST endpoint to get recommendations."""
    data = request.get_json()
    genre = data.get("genre", "")
    description = data.get("description", "")
    year = data.get("year", "")

    if not (genre or description or year):
        return jsonify({"error": "Please provide at least one input field."}), 400

    recs = recommend_movies(genre, description, year)
    return jsonify(recs)

@app.route("/items", methods=["GET"])
def get_items():
    return jsonify([m["title"] for m in movies[:100]])

# ===============================
# SERVE FRONTEND
# ===============================
FRONTEND_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

@app.route("/")
def serve_index():
    
    return send_from_directory(FRONTEND_FOLDER, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(FRONTEND_FOLDER, path)

# ===============================
# RUN SERVER
# ===============================
if __name__ == "__main__":
    print("Starting Flask server at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)