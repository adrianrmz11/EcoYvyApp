"""
seed_db.py
Script para poblar la base de datos con datos de prueba realistas.
"""

import random
from datetime import datetime, timedelta
from app import app, db
from models import WasteReport
from calculations import estimate_weight, calculate_co2_avoided, calculate_ecopoints

# Materiales disponibles
MATERIALES = ['pet', 'glass', 'can', 'cardboard', 'plastic', 'electronics', 'organic']

def generar_fecha_aleatoria():
    """Genera una fecha aleatoria dentro de los últimos 30 días."""
    hoy = datetime.now()
    dias_atras = random.randint(0, 30)
    horas_atras = random.randint(0, 23)
    return hoy - timedelta(days=dias_atras, hours=horas_atras)

def seed_database():
    """Función principal para inyectar datos en la base de datos."""
    
    with app.app_context():
        print("🧹 Limpiando datos anteriores...")
        WasteReport.query.delete()
        db.session.commit()
        
        print("🌱 Generando 50 reportes de prueba...")
        
        for i in range(50):
            material = random.choice(MATERIALES)
            cantidad = random.randint(1, 20)
            
            peso_kg = estimate_weight(material, cantidad)
            co2_kg = calculate_co2_avoided(peso_kg)
            
            mrv_verificado = random.random() < 0.3
            eco_points = calculate_ecopoints(peso_kg, mrv_verificado)
            
            fecha = generar_fecha_aleatoria()
            confianza = round(random.uniform(0.75, 0.99), 2)
            
            reporte = WasteReport(
                material=material,
                quantity=cantidad,
                weight_kg=peso_kg,
                co2_saved_kg=co2_kg,
                eco_points=eco_points,
                mrv_verified=mrv_verificado,
                confidence=confianza,
                timestamp=fecha
            )
            
            db.session.add(reporte)
            
        db.session.commit()
        print(f"✅ ¡Éxito! Se insertaron 50 reportes en la base de datos.")

if __name__ == '__main__':
    try:
        seed_database()
    except Exception as e:
        print(f"❌ Error: {e}")