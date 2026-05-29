# ecoyvy_mvp_resources/logic/calculator.py

def estimate_weight(material, quantity):
    """
    Estima el peso en kg basado en el material y cantidad de unidades.
    Factores basados en pesos promedio de residuos (botellas, latas, etc).
    """
    # Peso promedio por unidad en kg
    weights_per_unit = {
        'pet': 0.030,        # Botella PET 500ml vacía
        'glass': 0.350,      # Botella vidrio 330ml
        'can': 0.015,        # Lata de aluminio
        'cardboard': 0.200   # Caja pequeña promedio
    }
    
    unit_weight = weights_per_unit.get(material.lower(), 0.100) # Default 100g si no se conoce
    total_weight_kg = quantity * unit_weight
    
    return round(total_weight_kg, 2)


def calculate_co2_avoided(weight_kg):
    """
    Calcula CO2 evitado en kg.
    Factor general de reciclaje (aprox 2.4 kg CO2 evitado por kg de plástico reciclado vs virgen).
    """
    # Factor promedio de emisión evitada (ton CO2e / ton material)
    EMISSION_FACTOR = 2.4 
    
    co2_avoided = weight_kg * EMISSION_FACTOR
    return round(co2_avoided, 2)


def calculate_ecopoints(weight_kg):
    """
    Calcula los puntos de recompensa.
    Regla: 1 kg = 100 EcoPoints (ajustable según economía del juego).
    """
    POINTS_PER_KG = 100
    points = int(weight_kg * POINTS_PER_KG)
    return points

# --- BLOQUE DE PRUEBA 
if __name__ == "__main__":
    print("🧪 Testing EcoYvy Calculator Logic...")
    
    # Prueba: 5 botellas PET
    kgs = estimate_weight('pet', 5)
    co2 = calculate_co2_avoided(kgs)
    points = calculate_ecopoints(kgs)
    
    print(f"✅ 5 PET Bottles = {kgs} kg")
    print(f"🌿 CO2 Avoided: {co2} kg")
    print(f"💎 EcoPoints Earned: {points}")