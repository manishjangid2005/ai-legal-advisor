from flask import Flask, render_template, request, jsonify
import json, re
from pathlib import Path

app = Flask(__name__)
BASE = Path(__file__).resolve().parent
RULES_PATH = BASE / "data" / "legal_rules.json"

with open(RULES_PATH, "r", encoding="utf-8") as f:
    RULES = json.load(f)

def clean_text(t):
    return re.sub(r'[^a-z0-9\s]', '', t.lower())

def generate_answer(msg):
    text = clean_text(msg)
    for intent in RULES:
        for kw in intent.get("keywords", []):
            if kw in text:
                return intent["detailed_response"]

    words = set(text.split())
    best = None
    best_score = 0

    for intent in RULES:
        kws = set()
        for kw in intent.get("keywords", []):
            kws.update(kw.split())
        score = len(words & kws)

        if score > best_score:
            best_score = score
            best = intent

    if best and best_score > 0:
        return best["detailed_response"]

    return ("I'm sorry — I couldn't find a direct legal answer. "
            "Try asking about: traffic fines, cyberbullying, FIR process, fine amounts, or basic advisory steps.")

@app.route("/", methods=["GET"])
def home():   # CHANGED from index() → home()
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    msg = data.get("message","")
    answer = generate_answer(msg)
    return jsonify({"answer": answer})

# Remove ANY duplicate routes. Keep only this.

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
