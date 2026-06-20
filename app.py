from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from models import db, WasteReport
from calculations import analyze_upload, business_esg_summary, MATERIAL_META

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecoyvy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "ecoyvy-admin-2026"
db.init_app(app)

ADMIN_USER = "admin"
ADMIN_PASS = "pass123"

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

with app.app_context():
    db.create_all()

ALLOWED_EXT = {"png", "jpg", "jpeg", "webp", "gif"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def detect_material_from_image(image_bytes: bytes, filename: str):
    try:
        import cv2
        import numpy as np

        nparr = np.frombuffer(image_bytes, np.uint8)
        img   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return None

        img = cv2.resize(img, (256, 256))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
        n = float(h.size)

        # Ratios de color en espacio HSV (H: 0-179, S: 0-255, V: 0-255)
        green   = ((h >= 35) & (h <= 85)  & (s > 60)).sum() / n
        brown   = ((h >= 5)  & (h <= 22)  & (s > 60) & (v < 190)).sum() / n
        blue    = ((h >= 95) & (h <= 130) & (s > 60)).sum() / n
        red     = (((h <= 8) | (h >= 170)) & (s > 80)).sum() / n
        yellow  = ((h >= 20) & (h <= 35)  & (s > 80)).sum() / n
        gray    = ((s < 40)  & (v > 60)   & (v < 210)).sum() / n
        white   = ((s < 30)  & (v > 200)).sum() / n
        black   = (v < 50).sum() / n
        colored = (s > 80).sum() / n  # píxeles vibrantes

        # Densidad de bordes (proxy de textura)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges  = cv2.Canny(gray_img, 50, 150)
        edge_d = edges.sum() / (255.0 * n)

        # Detección de forma circular (botellas / latas)
        circles  = cv2.HoughCircles(gray_img, cv2.HOUGH_GRADIENT, dp=1.2,
                                    minDist=80, param1=50, param2=30,
                                    minRadius=20, maxRadius=120)
        circular = 1.0 if circles is not None else 0.0

        scores = {
            'pet':         blue  * 1.8 + white   * 0.6 + circular * 0.5,
            'can':         (gray + colored) * 0.6 + (red + yellow) * 0.8 + circular * 0.9,
            'glass':       green * 0.9 + brown   * 0.5 + gray * 0.5 + edge_d * 0.4,
            'cardboard':   brown * 2.5,
            'plastic':     colored * 0.7 + white * 0.5,
            'aluminum':    gray  * 1.5 + circular * 0.4,
            'paper':       white * 2.0 + (1 - colored) * 0.3,
            'electronics': black * 1.5 + edge_d  * 0.6,
            'metal':       gray  * 1.0 + edge_d  * 0.5,
            'organic':     green * 2.0 + brown   * 0.4,
            'textile':     colored * 0.8 + (1 - edge_d) * 0.2,
        }

        best = max(scores, key=scores.get)
        return best if scores[best] > 0.08 else None

    except Exception:
        return None


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


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        if (request.form.get("username") == ADMIN_USER and
                request.form.get("password") == ADMIN_PASS):
            session["admin"] = True
            return redirect(url_for("business"))
        error = "Credenciales incorrectas"
    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("index"))


@app.route("/reports")
@admin_required
def reports():
    all_reports = WasteReport.query.order_by(WasteReport.timestamp.desc()).all()
    return render_template("reports.html", reports=all_reports)


@app.route("/business")
@admin_required
def business():
    db_records = WasteReport.query.order_by(WasteReport.timestamp.desc()).all()
    records = [
        {"material": r.material, "weight_kg": r.weight_kg, "verified": r.mrv_verified}
        for r in db_records
    ]
    esg = business_esg_summary(records)
    return render_template("business.html", esg=esg, records=records, meta=MATERIAL_META)


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

    image_bytes = file.read()
    detected    = detect_material_from_image(image_bytes, file.filename)
    if detected:
        material = detected

    result = analyze_upload(material, item_count, mrv_verified=True)
    result["ai_detected"] = detected is not None

    report = WasteReport(
        material     = result["material"],
        quantity     = result["item_count"],
        weight_kg    = result["weight_kg"],
        co2_saved_kg = result["co2_saved_kg"],
        eco_points   = result["ecopoints"],
        mrv_verified = result["mrv_verified"],
        confidence   = result["confidence"],
    )
    db.session.add(report)
    db.session.commit()
    result["report_id"] = report.id

    return jsonify(result)


@app.route("/api/history")
def api_history():
    limit = min(int(request.args.get("limit", 20)), 100)
    reports = (WasteReport.query
               .order_by(WasteReport.timestamp.desc())
               .limit(limit)
               .all())
    return jsonify([r.to_dict() for r in reports])


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    role = data.get("role", "citizen")
    destinations = {"citizen": "/citizen", "recycler": "/citizen", "business": "/business"}
    return jsonify({"status": "ok", "message": f"Registered as {role}",
                    "role": role, "redirect": destinations.get(role, "/citizen")})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
