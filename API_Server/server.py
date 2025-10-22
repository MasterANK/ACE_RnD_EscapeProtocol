from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Initialize Firebase (keep this private on your Render server)
cred = credentials.Certificate("firebase-admin.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route("/submit_score", methods=["POST"])
def submit_score():
    data = request.json
    username = data.get("username")
    score = data.get("score")
    maze_scores = data.get("maze_scores", {})  # e.g. {"Maze 1": 800, "Maze 2": 950}

    if not username or score is None:
        return jsonify({"error": "Missing username or score"}), 400

    user_ref = db.collection("leaderboard").document(username)
    user_data = user_ref.get().to_dict() or {"total": 0, "mazes": {}}

    # Update user data
    user_data["total"] += score
    user_data["mazes"].update(maze_scores)
    user_ref.set(user_data)

    return jsonify({"message": "Score updated", "user": user_data}), 200


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    docs = db.collection("leaderboard").stream()
    leaderboard_data = [
        {"username": doc.id, **doc.to_dict()} for doc in docs
    ]
    leaderboard_data.sort(key=lambda x: x["total"], reverse=True)
    return jsonify(leaderboard_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

