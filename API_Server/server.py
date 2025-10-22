import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify
import os
import json 
import sys # For logging/debugging

# --- Secure Initialization ---
db = None

try:
    # 1. Read the JSON string from the environment variable set in Render
    firebase_config_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    
    if firebase_config_json:
        # 2. Parse the string into a dictionary
        service_account_info = json.loads(firebase_config_json)
        
        # 3. Initialize Firebase using the secure dictionary
        # Check if the app is already initialized (important for testing)
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        print("INFO: Firebase initialized securely.", file=sys.stderr)
    else:
        print("CRITICAL: FIREBASE_CREDENTIALS_JSON not found. DB connection failed.", file=sys.stderr)

except Exception as e:
    print(f"FATAL ERROR during Firebase init: {e}", file=sys.stderr)

app = Flask(__name__)

# --- API Endpoints ---

@app.route("/submit_score", methods=["POST"])
def submit_score():
    if not db:
        return jsonify({"error": "Server not connected to Database."}), 503

    try:
        data = request.json
        username = data.get("username", "").strip()
        score = data.get("score")
        maze_scores = data.get("maze_scores", {})
    except Exception:
        return jsonify({"error": "Invalid JSON format."}), 400

    if not username or score is None:
        return jsonify({"error": "Missing username or score"}), 400

    # Basic score validation
    try:
        score_float = float(score)
        if score_float < 0:
            return jsonify({"error": "Score cannot be negative."}), 400
    except ValueError:
        return jsonify({"error": "Score must be a valid number."}), 400

    # Use the username as the document ID for easy retrieval/updating
    user_ref = db.collection("leaderboard").document(username) 
    
    # Use a transaction to ensure atomic read/write if necessary, but 
    # for simple updates, a direct get/set is acceptable here.
    user_data = user_ref.get().to_dict() or {"total": 0, "mazes": {}}

    # Your logic: Update/add scores
    user_data["total"] = user_data["total"] + score_float # Accumulate total score
    user_data["mazes"].update(maze_scores)              # Update maze progress
    user_data["last_updated"] = firestore.SERVER_TIMESTAMP # Use server timestamp for accuracy
    
    user_ref.set(user_data) # Overwrites existing document with new data

    return jsonify({"message": "Score updated", "user_total": user_data["total"]}), 200


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    if not db:
        return jsonify({"error": "Server not connected to Database."}), 503
        
    try:
        # Sort by 'total' score in descending order
        # Note: If you want real-time sorting, you might need a composite index on Firestore
        # but for small data sets, stream and sort is fast enough.
        docs = db.collection("leaderboard").order_by("total", direction=firestore.Query.DESCENDING).stream()
        
        leaderboard_data = [
            {"username": doc.id, **doc.to_dict()} for doc in docs
        ]

        return jsonify(leaderboard_data), 200
    except Exception as e:
        print(f"Leaderboard retrieval error: {e}", file=sys.stderr)
        return jsonify({"error": "Failed to retrieve leaderboard data."}), 500


if __name__ == "__main__":
    # Render uses the PORT environment variable provided by the host.
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
