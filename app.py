from flask import Flask, render_template, request, jsonify
from models import db, WasteReport
from calculations import analyze_upload, business_esg_summary, MATERIAL_META
from werkzeug.utils import secure_filename
import os
from functools import wraps

# Intentar cargar YOLO, pero si falla, continuar sin él
try:
    from ultralytics import YOLO
    yolo_model = YOLO('yolov8n.pt')
    YOLO_AVAILABLE = True
    print("✅ YOLO cargado exitosamente")
except Exception as e:
    yolo_model = None
    YOLO_AVAILABLE = False
    print(f"⚠️ YOLO no disponible: {e}")
    print("⚠️ La detección de materiales por IA no funcionará, pero el resto de la app sí")

# Mapeo de clases YOLO a materiales de reciclaje
MATERIAL_MAPPING = {
    'bottle': 'PET',
    'cup': 'PLASTIC',
    'tv': 'ELECTRONICS',
    'cell phone': 'ELECTRONICS',
    'laptop': 'ELECTRONICS',
    'keyboard': 'ELECTRONICS',
    'remote': 'ELECTRONICS',
    'bowl': 'GLASS',
    'vase': 'GLASS'
}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecoyvy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

ALLOWED_EXT = {"png", "jpg", "jpeg", "webp", "gif"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

# ── Páginas ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/citizen")
def citizen():
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

@app.route("/test_yolo")
def test_yolo():
    return render_template("test_yolo.html")

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

@app.route('/api/detect-material', methods=['POST'])
def detect_material():
    if not YOLO_AVAILABLE:
        return jsonify({
            'error': 'YOLO no está disponible en este entorno. Por favor, probá en Google Colab o en otra computadora.'
        }), 503
    
    if 'image' not in request.files:
        return jsonify({'error': 'No se envió ninguna imagen'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío'}), 400

    # 1. Capturar coordenadas GPS (opcionales)
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    filename = secure_filename(file.filename)
    upload_folder = 'uploads'
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    try:
        results = yolo_model(filepath)
        detections = []
        primary_material = None
        
        # 2. Analizar la imagen
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = yolo_model.names[cls_id]
                
                if class_name in MATERIAL_MAPPING:
                    material_name = MATERIAL_MAPPING[class_name]
                    if primary_material is None:
                        primary_material = material_name # Tomamos el primero como principal
                        
                    detections.append({
                        'material': material_name,
                        'clase_yolo': class_name,
                        'confianza': round(confidence * 100, 2)
                    })

        # 3. Guardar en la Base de Datos si detectó algo
        if primary_material:
            lat = float(latitude) if latitude else None
            lng = float(longitude) if longitude else None
            
            new_report = WasteReport(
                material=primary_material.lower(),
                quantity=len(detections),
                weight_kg=0.1,  # Valor por defecto para la demo
                co2_saved_kg=0.05, # Valor por defecto
                eco_points=10,
                confidence=detections[0]['confianza'] / 100,
                latitude=lat,
                longitude=lng,
                photo_path=filepath,
                status='pending',
                user_type='citizen'
            )
            db.session.add(new_report)
            db.session.commit()
            print(f"✅ Reporte guardado en DB: {primary_material} en ({lat}, {lng})")

        # 4. Limpiar y responder
        os.remove(filepath)

        return jsonify({
            'success': True,
            'materiales_detectados': detections,
            'total': len(detections)
        })

    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

# ── API: Obtener todos los reportes para el mapa ─────────────────────────────

@app.route("/api/reports", methods=["GET"])
def get_reports():
    try:
        # Traemos todos los reportes de la base de datos
        reports = WasteReport.query.all()
        
        # Los convertimos a un formato JSON que el mapa puede leer
        reports_data = []
        for report in reports:
            reports_data.append({
                "id": report.id,
                "material": report.material,
                "latitude": report.latitude,
                "longitude": report.longitude,
                "confidence": report.confidence,
                "status": report.status,
                "timestamp": report.timestamp.strftime("%Y-%m-%d %H:%M") if report.timestamp else None
            })
            
        return jsonify(reports_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/map")
def public_map():
    return render_template("map.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
