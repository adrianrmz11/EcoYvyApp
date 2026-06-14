"""
Tests unitarios para calculations.py
Verifica que los cálculos ESG/MRV funcionen correctamente
"""

import pytest
from calculations import estimate_weight, calculate_co2_avoided, calculate_ecopoints, MATERIAL_META


class TestWeightEstimation:
    """Tests para estimación de peso"""
    
    def test_pet_bottle_weight(self):
        """5 botellas PET deben pesar 0.15 kg (0.030 kg c/u)"""
        result = estimate_weight("pet", 5)
        assert result == 0.15
    
    def test_glass_bottle_weight(self):
        """2 botellas de vidrio deben pesar 0.70 kg (0.350 kg c/u)"""
        result = estimate_weight("glass", 2)
        assert result == 0.70
    
    def test_aluminum_can_weight(self):
        """10 latas de aluminio deben pesar 0.15 kg (0.015 kg c/u)"""
        result = estimate_weight("can", 10)
        assert result == 0.15
    
    def test_cardboard_weight(self):
        """3 cajas de cartón deben pesar 0.60 kg (0.200 kg c/u)"""
        result = estimate_weight("cardboard", 3)
        assert result == 0.60
    
    def test_unknown_material_weight(self):
        """Material desconocido debe usar peso genérico (0.050 kg)"""
        result = estimate_weight("unknown_material", 10)
        assert result == 0.50


class TestCO2Calculation:
    """Tests para cálculo de CO₂ evitado"""
    
    def test_co2_from_pet_weight(self):
        """0.15 kg de PET debe evitar 0.36 kg de CO₂"""
        result = calculate_co2_avoided(0.15)
        assert result == 0.36
    
    def test_co2_from_glass_weight(self):
        """0.70 kg de vidrio debe evitar 1.68 kg de CO₂"""
        result = calculate_co2_avoided(0.70)
        assert result == 1.68
    
    def test_co2_zero_weight(self):
        """0 kg debe generar 0 kg de CO₂ evitado"""
        result = calculate_co2_avoided(0)
        assert result == 0.0


class TestEcoPointsCalculation:
    """Tests para cálculo de EcoPoints"""
    
    def test_ecopoints_without_mrv(self):
        """0.15 kg sin MRV debe dar 15 puntos"""
        result = calculate_ecopoints(0.15, mrv_verified=False)
        assert result == 15
    
    def test_ecopoints_with_mrv(self):
        """0.15 kg con MRV debe dar 18 puntos (15 × 1.25 = 18.75, redondeado)"""
        result = calculate_ecopoints(0.15, mrv_verified=True)
        assert result == 18
    
    def test_ecopoints_larger_weight(self):
        """1.0 kg con MRV debe dar 125 puntos"""
        result = calculate_ecopoints(1.0, mrv_verified=True)
        assert result == 125


class TestMaterialMetadata:
    """Tests para verificar que MATERIAL_META esté completo"""
    
    def test_pet_in_materials(self):
        """PET debe estar en MATERIAL_META"""
        assert "pet" in MATERIAL_META
    
    def test_glass_in_materials(self):
        """Glass debe estar en MATERIAL_META"""
        assert "glass" in MATERIAL_META
    
    def test_can_in_materials(self):
        """Can debe estar en MATERIAL_META"""
        assert "can" in MATERIAL_META
    
    def test_material_has_label(self):
        """Cada material debe tener label e icon"""
        for material, data in MATERIAL_META.items():
            assert "label" in data, f"{material} no tiene label"
            assert "icon" in data, f"{material} no tiene icon"


# Tests adicionales para casos edge
class TestEdgeCases:
    """Tests para casos límite"""
    
    def test_zero_quantity(self):
        """0 unidades debe dar 0 kg"""
        result = estimate_weight("pet", 0)
        assert result == 0.0
    
    def test_large_quantity(self):
        """1000 botellas PET deben pesar 30 kg"""
        result = estimate_weight("pet", 1000)
        assert result == 30.0
    
    def test_negative_quantity(self):
        """Cantidad negativa debe manejarse (depende de la implementación)"""
        # Esto depende de cómo esté implementado calculate_weight
        # Si no maneja negativos, este test fallará y sabrás que necesitas validación
        result = estimate_weight("pet", -5)
        assert result >= 0  # Esperamos que no retorne negativos
