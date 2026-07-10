from app import app, db, WasteReport
from datetime import datetime, timedelta
import random

# Coordenadas de diferentes barrios de Asunción
LOCATIONS = [
    # Centro
    (-25.2637, -57.5759, "Centro"),
    # Villa Morra
    (-25.2850, -57.5950, "Villa Morra"),
    # Recoleta
    (-25.2750, -57.5650, "Recoleta"),
    # Sajonia
    (-25.2550, -57.5850, "Sajonia"),
    # Trinidad
    (-25.3050, -57.5750, "Trinidad"),
    # Las Mercedes
    (-25.2950, -57.5550, "Las Mercedes"),
    # San Vicente
    (-25.2450, -57.5950, "San Vicente"),
    # Mburucuya
    (-25.2750, -57.6050, "Mburucuya"),
    # Carmelitas
    (-25.2650, -57.6150, "Carmelitas"),
    # Santa Ana
    (-25.2350, -57.5650, "Santa Ana"),
]

# Materiales disponibles
MATERIALS = ['pet', 'glass', 'plastic', 'metal', 'cardboard', 'electronics']

def create_demo_data():
    """Crear datos de prueba para el mapa"""
    
    with app.app_context():
        # Limpiar reportes existentes (opcional)
        # WasteReport.query.delete()
        # db.session.commit()
        
        print(" Creando reportes de demostración...")
        
        # Crear 15 reportes aleatorios
        for i in range(15):
            lat, lng, barrio = random.choice(LOCATIONS)
            
            # Agregar variación aleatoria pequeña
            lat += random.uniform(-0.01, 0.01)
            lng += random.uniform(-0.01, 0.01)
            
            material = random.choice(MATERIALS)
            weight = round(random.uniform(0.1, 2.0), 2)
            confidence = round(random.uniform(0.75, 0.98), 2)
            
            report = WasteReport(
                material=material,
                quantity=random.randint(1, 5),
                weight_kg=weight,
                co2_saved_kg=round(weight * 0.5, 2),
                eco_points=random.randint(10, 50),
                confidence=confidence,
                latitude=lat,
                longitude=lng,
                photo_path=f'uploads/demo_{i}.jpg',
                status=random.choice(['pending', 'collected', 'verified']),
                user_type='citizen',
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 72))
            )
            
            db.session.add(report)
        
        db.session.commit()
        print(f"✅ ¡15 reportes creados exitosamente!")
        print(f"📍 Ubicaciones: {len(LOCATIONS)} barrios de Asunción")
        print(f"🗑️ Materiales: {', '.join(MATERIALS)}")

if __name__ == "__main__":
    create_demo_data()