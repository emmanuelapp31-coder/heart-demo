import json, math, os
from flask import Flask, Response, request, jsonify
from page import HTML

BASE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE, "model.json")) as f:
    M = json.load(f)
NUM, CAT = M["num"], M["cat"]
HARD = {"age": (0, 120), "blood_pressure": (50, 260), "cholesterol": (80, 500),
        "bmi": (10, 70), "physical_activity": (0, 4), "stress_level": (1, 10)}

def parse_row(d):
    """Returns (feature vector, warnings). Raises ValueError with a readable message."""
    x, warns = [], []
    for k, mu, sd in zip(NUM, M["mean"], M["scale"]):
        try:
            v = float(d[k])
        except (KeyError, TypeError, ValueError):
            raise ValueError(f"{k} must be a number")
        lo, hi = HARD[k]
        if not (math.isfinite(v) and lo <= v <= hi):
            raise ValueError(f"{k} must be between {lo} and {hi}")
        tlo, thi = M["range"][k]
        if not (tlo <= v <= thi):
            warns.append(f"{k.replace('_', ' ')} {v:g} is outside the training range ({tlo:g} to {thi:g}), so the estimate is less reliable.")
        x.append((v - mu) / sd)
    for k in CAT:
        opts = [o.lower() for o in M["cats"][k]]
        v = str(d.get(k, "")).strip().lower()
        if v not in opts:
            raise ValueError(f"{k} must be one of: {', '.join(M['cats'][k])}")
        x.append(float(opts.index(v)))
    return x, warns

def probability(x):
    z = sum(w * v for w, v in zip(M["coef"], x)) + M["intercept"]
    return 1 / (1 + math.exp(-z))

def result(d):
    x, warns = parse_row(d)
    return {"probability": round(probability(x), 4), "base_rate": round(M["base_rate"], 4), "warnings": warns}

app = Flask(__name__)

@app.get("/")
def index():
    return Response(HTML, mimetype="text/html")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/info")
def info():
    with open(os.path.join(BASE, "metrics.json")) as f:
        return jsonify(json.load(f))

@app.post("/predict")
def predict():
    try:
        return jsonify(result(request.get_json(silent=True) or {}))
    except ValueError as e:
        return jsonify(error=str(e)), 400

@app.post("/predict_batch")
def predict_batch():
    rows = (request.get_json(silent=True) or {}).get("rows")
    if not isinstance(rows, list) or not rows or len(rows) > 1000:
        return jsonify(error="Send 1 to 1000 rows"), 400
    out = []
    for i, r in enumerate(rows, 1):
        try:
            out.append(result(r if isinstance(r, dict) else {}))
        except ValueError as e:
            return jsonify(error=f"Row {i}: {e}"), 400
    return jsonify(results=out)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
