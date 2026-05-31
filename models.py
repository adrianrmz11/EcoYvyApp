from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class WasteReport(db.Model):
    __tablename__ = 'waste_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    material = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    weight_kg = db.Column(db.Float, nullable=False)
    co2_saved_kg = db.Column(db.Float, nullable=False)
    eco_points = db.Column(db.Integer, default=0)
    mrv_verified = db.Column(db.Boolean, default=True)
    confidence = db.Column(db.Float, default=0.90)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "material": self.material,
            "weight_kg": self.weight_kg,
            "co2_saved_kg": self.co2_saved_kg,
            "eco_points": self.eco_points,
            "mrv_verified": self.mrv_verified,
            "timestamp": self.timestamp.isoformat()
        }