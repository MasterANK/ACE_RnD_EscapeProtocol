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
    """
    Receives individual maze metrics, securely updates the user's total 
    score, moves, distance, and time on the server.
    
    The expected payload structure includes a detailed 'maze_scores' list:
    "maze_scores": {"Maze Name": [score, moves, distance, time_elapsed]}
    """
    if not db:
        return jsonify({"error": "Server not connected to Database."}), 503

    try:
        data = request.json
        username = data.get("username", "").strip()
        
        # 1. New Maze Performance Metrics from Client (Per-Maze Data - used for secure aggregation)
        # The aggregation relies ONLY on these top-level fields for correctness.
        score = data.get("score")
        moves = data.get("moves", 0)
        distance = data.get("distance", 0.0)
        time_elapsed = data.get("time_elapsed", 0.0)
        
        # 2. Per-Maze Detail (used only for storage/tracking completion)
        # This dict now contains the list: {maze_name: [score, move_count, total_distance, elapsed]}
        maze_scores = data.get("maze_scores", {}) 

        # Convert and validate metrics
        moves_int = int(moves) if moves is not None else 0
        distance_float = float(distance) if distance is not None else 0.0
        time_float = float(time_elapsed) if time_elapsed is not None else 0.0
        score_float = float(score)

    except (ValueError, TypeError) as e:
        print(f"Validation Error: {e}", file=sys.stderr)
        return jsonify({"error": "Invalid data format or type received. Check all six fields."}), 400

    if not username or score is None:
        return jsonify({"error": "Missing username or score"}), 400

    user_ref = db.collection("leaderboard").document(username) 
    
    # Initialize all total fields safely with 0 if user is new
    user_data = user_ref.get().to_dict() or {
        "total": 0.0, 
        "mazes": {}, 
        "total_moves": 0,          
        "total_distance": 0.0,     
        "total_time": 0.0          
    }

    # CORE LOGIC: Accumulate all four metrics securely on the server
    
    # 1. Score Accumulation (Relies on top-level 'score' for the correct increment)
    user_data["total"] = user_data["total"] + score_float
    
    # 2. Metric Accumulation (Relies on top-level metrics for the correct increment)
    user_data["total_moves"] = user_data.get("total_moves", 0) + moves_int
    user_data["total_distance"] = user_data.get("total_distance", 0.0) + distance_float
    user_data["total_time"] = user_data.get("total_time", 0.0) + time_float
    
    # 3. Maze Completion Tracking (Stores the new detailed list structure, which is acceptable in Firestore)
    user_data["mazes"].update(maze_scores)
    user_data["last_updated"] = firestore.SERVER_TIMESTAMP 
    
    user_ref.set(user_data) 

    return jsonify({
        "message": "Score and all metrics updated", 
        "user_total": user_data["total"],
        "total_moves": user_data["total_moves"] 
    }), 200


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    """
    Retrieves and returns the aggregated leaderboard data, sorted by total score.
    """
    if not db:
        return jsonify({"error": "Server not connected to Database."}), 503
        
    try:
        # Sort by total score descending
        docs = db.collection("leaderboard").order_by("total", direction=firestore.Query.DESCENDING).stream()
        
        leaderboard_data = []
        for doc in docs:
            data = doc.to_dict()
            # Compile data for the Streamlit app
            leaderboard_data.append({
                "username": doc.id,
                "total": data.get("total", 0.0),
                "total_moves": data.get("total_moves", 0),
                "total_distance": data.get("total_distance", 0.0),
                "total_time": data.get("total_time", 0.0),
                # Calculate number of completed mazes from the 'mazes' map
                "mazes_completed": len(data.get("mazes", {}))
            })

        return jsonify(leaderboard_data), 200
    except Exception as e:
        print(f"Leaderboard retrieval error: {e}", file=sys.stderr)
        return jsonify({"error": "Failed to retrieve leaderboard data."}), 500


if __name__ == "__main__":
    # Use environment variable for port or default to 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)