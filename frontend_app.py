from flask import Flask, request, jsonify, send_from_directory, render_template
from backend.chat_engine import process_user_input
import os

app = Flask(
    __name__,
    static_url_path="/",
    static_folder="frontend",
    template_folder="frontend"
)

# 🟢 Home route: serve the index.html
@app.route("/")
def index():
    return render_template("index.html")

# 🟢 Serve frontend assets like CSS or JS
@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory("frontend", path)

# 🟢 API Status route (for frontend fetch test)
@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({"status": "ok"})

# 🟢 Main chat route (POST)
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    try:
        response, gauges, emotion = process_user_input(user_input)
        return jsonify({
            "response": response,
            "gauges": gauges,
            "emotion": emotion
        })

    except Exception as e:
        print(f"[ERROR] Failed to process input: {e}")
        return jsonify({"error": "Internal server error"}), 500

# 🔵 Run the Flask server
if __name__ == "__main__":
    app.run(debug=True, port=5001)