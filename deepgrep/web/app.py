# app.py - Production-ready Flask application with logging and rate limiting
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from decouple import config
from deepgrep.core.engine import find_matches
from deepgrep.core.history import SearchHistoryDB
from deepgrep.core.semantic_engine import SemanticEngine
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration from environment variables
PORT = config('PORT', default=8000, cast=int)
DEBUG = config('DEBUG', default=True, cast=bool)
HOST = config('HOST', default='0.0.0.0')
RATE_LIMIT_ENABLED = config('RATE_LIMIT_ENABLED', default=True, cast=bool)
RATE_LIMIT_REQUESTS = config('RATE_LIMIT_REQUESTS', default=100, cast=int)
RATE_LIMIT_WINDOW = config('RATE_LIMIT_WINDOW', default=60, cast=int)

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[f"200 per minute"],
    enabled=RATE_LIMIT_ENABLED
)

# Initialize engines once (heavy models loaded at import time)
logger.info("Initializing semantic engine and history database...")
semantic_engine = SemanticEngine()
history_db = SearchHistoryDB()
logger.info("Application initialization complete")

@app.route("/")
def home():
    logger.info("GET / - Home page requested")
    return render_template("index.html")

@app.route("/search", methods=["POST"])
@limiter.limit(f"{RATE_LIMIT_REQUESTS}/minute")
def search_regex():
    logger.info("POST /search - Regex search request received")
    data = request.get_json()
    pattern = data.get("pattern")
    text = data.get("text")
    
    if not pattern or not text:
        logger.warning("POST /search - Missing pattern or text in request")
        return jsonify({"error": "Missing pattern or text"}), 400

    matches = []
    # Process lines in chunks or use map to speed up for long input; keep simple here
    for line in text.splitlines():
        matches.extend(find_matches(line, pattern))

    history_db.log_search(pattern, len(matches), ["web_input"])
    all_history = history_db.list_all(limit=50)
    
    logger.info(f"POST /search - Successfully found {len(matches)} matches for pattern '{pattern}'")

    return jsonify({
        "matches": matches,
        "history": [
            {"pattern": r[0], "matches": r[2], "timestamp": r[1]} for r in all_history
        ]
    })

@app.route("/semantic", methods=["POST"])
@limiter.limit(f"{RATE_LIMIT_REQUESTS}/minute")
def search_semantic():
    logger.info("POST /semantic - Semantic search request received")
    data = request.get_json()
    keyword = data.get("keyword")
    text = data.get("text")
    
    if not keyword or not text:
        logger.warning("POST /semantic - Missing keyword or text in request")
        return jsonify({"error": "Missing keyword or text"}), 400

    matches = semantic_engine.find_semantic_matches(text, keyword)
    history_db.log_search(keyword, len(matches), ["web_input"])
    all_history = history_db.list_all(limit=50)
    
    logger.info(f"POST /semantic - Successfully found {len(matches)} semantic matches for keyword '{keyword}'")

    return jsonify({
        "matches": [{"word": w, "similarity": round(s, 3)} for w, s in matches],
        "history": [
            {"pattern": r[0], "matches": r[2], "timestamp": r[1]} for r in all_history
        ]
    })

if __name__ == "__main__":
    # Remove in-production NLTK downloads; expect preinstalled corpora
    # import nltk
    # nltk.download('wordnet')
    logger.info(f"Starting Flask server on {HOST}:{PORT} (debug={DEBUG})")
    app.run(host=HOST, port=PORT, debug=DEBUG)