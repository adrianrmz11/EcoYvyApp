from flask import Flask, render_template, request, jsonify
from calculations import analyze_upload, business_esg_summary, MATERIAL_META

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

ALLOWED_EXT = {"png", "jpg", "jpeg", "webp", "gif"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


# ── Páginas ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/citizen")
def citizen():
    # Materiales primarios del equipo primero, luego los extendidos
    primary   = ["pet", "can", "glass", "cardboard"]
    secondary = [k for k in MATERIAL_META if k not in primary]
    ordered   = {k: MATERIAL_META[k] for k in primary + secondary}
    return render_template("citizen.html", materials=ordered)


@app.route("/business")
def business():
    sample_records = [
        {"material": "pet",       "weight_kg": 45.0,  "verified": True},
        {"material": "can",       "weight_kg": 12.5,  "verified": True},
        {"material": "cardboard", "weight_kg": 80.0,  "verified": False},
        {"material": "glass",     "weight_kg": 30.0,  "verified": True},
        {"material": "metal",     "weight_kg": 20.0,  "verified": True},
        {"material": "electronics","weight_kg": 5.0,  "verified": True},
    ]
    esg = business_esg_summary(sample_records)
    return render_template("business.html", esg=esg, records=sample_records, meta=MATERIAL_META)


# ── API ────────────────────────────────────────────────────────────────────────

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    material   = request.form.get("material", "pet")
    item_count = max(1, int(request.form.get("item_count", 1)))
    file       = request.files.get("photo")

    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Imagen inválida o no adjuntada"}), 400
    if material not in MATERIAL_META:
        return jsonify({"error": f"Material '{material}' no reconocido"}), 400

    return jsonify(analyze_upload(material, item_count, mrv_verified=True))


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    role = data.get("role", "citizen")
    destinations = {"citizen": "/citizen", "recycler": "/citizen", "business": "/business"}
    return jsonify({"status": "ok", "message": f"Registered as {role}",
                    "role": role, "redirect": destinations.get(role, "/citizen")})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
