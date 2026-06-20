from app import app, db
from models import WasteReport

with app.app_context():
    total = WasteReport.query.count()
    print(f"\n📊 Total de reportes en la base de datos: {total}\n")
    
    # Mostrar algunos ejemplos
    reportes = WasteReport.query.limit(5).all()
    print("Ejemplos de reportes:")
    print("-" * 70)
    for r in reportes:
        print(f"Material: {r.material:12} | Cantidad: {r.quantity:3} | Peso: {r.weight_kg:.3f}kg | CO2: {r.co2_saved_kg:.3f}kg | EcoPoints: {r.eco_points}")
    print("-" * 70)
    
    # Mostrar totales acumulados
    total_peso = db.session.query(db.func.sum(WasteReport.weight_kg)).scalar()
    total_co2 = db.session.query(db.func.sum(WasteReport.co2_saved_kg)).scalar()
    total_puntos = db.session.query(db.func.sum(WasteReport.eco_points)).scalar()
    
    print(f"\n📈 TOTALES ACUMULADOS:")
    print(f"   Peso total reciclado: {total_peso:.2f} kg")
    print(f"   CO₂ evitado: {total_co2:.2f} kg")
    print(f"   EcoPoints totales: {total_puntos:.0f}")
    print()