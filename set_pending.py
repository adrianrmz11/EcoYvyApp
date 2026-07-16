from app import app, db, WasteReport

# Entramos en el contexto de la aplicación para poder usar la base de datos
with app.app_context():
    # Obtener todos los reportes que existen actualmente
    reports = WasteReport.query.all()
    
    # Marcar los primeros 8 reportes como 'pending' (pendiente)
    for report in reports[:8]:
        report.status = 'pending'
    
    # Guardar los cambios en la base de datos
    db.session.commit()
    
    print(f"✅ {len(reports[:8])} reportes marcados como 'pending'")
    print(f"📊 Total de reportes en la DB: {len(reports)}")