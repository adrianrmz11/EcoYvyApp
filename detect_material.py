from ultralytics import YOLO
import json

# Cargar modelo YOLOv8 pre-entrenado
model = YOLO('yolov8n.pt')  # 'n' = nano (más rápido, menos preciso)
# Si querés más precisión: YOLO('yolov8s.pt') o YOLO('yolov8m.pt')

# Mapeo de clases YOLO a materiales de reciclaje
MATERIAL_MAPPING = {
    'bottle': 'PET',
    'cup': 'PLASTIC',
    'dining table': 'CARDBOARD',  # Aproximación
    'chair': 'PLASTIC',  # Si es de plástico
    'tv': 'ELECTRONICS',
    'cell phone': 'ELECTRONICS',
    'laptop': 'ELECTRONICS',
    'keyboard': 'ELECTRONICS',
    'remote': 'ELECTRONICS',
}

def detect_material(image_path):
    """
    Detecta materiales en una imagen usando YOLO
    
    Args:
        image_path: Ruta a la imagen o URL
        
    Returns:
        dict: Materiales detectados con confianza
    """
    # Ejecutar detección
    results = model(image_path)
    
    materiales_detectados = []
    
    # Procesar resultados
    for result in results:
        boxes = result.boxes
        for box in boxes:
            # Obtener clase y confianza
            cls_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = model.names[cls_id]
            
            # Verificar si es un material de reciclaje
            if class_name in MATERIAL_MAPPING:
                material = MATERIAL_MAPPING[class_name]
                materiales_detectados.append({
                    'material': material,
                    'clase_original': class_name,
                    'confianza': round(confidence * 100, 2),
                    'bbox': box.xyxy[0].tolist()  # Coordenadas del bounding box
                })
    
    return {
        'materiales': materiales_detectados,
        'total_detectados': len(materiales_detectados)
    }

if __name__ == "__main__":
    # Ejemplo de uso
    import sys
    
    if len(sys.argv) > 1:
        imagen = sys.argv[1]
    else:
        imagen = "test_image.jpg"  # Imagen por defecto
    
    print(f"🔍 Analizando imagen: {imagen}")
    resultado = detect_material(imagen)
    
    print("\n" + "="*50)
    print("RESULTADOS DE DETECCIÓN:")
    print("="*50)
    
    if resultado['total_detectados'] > 0:
        for mat in resultado['materiales']:
            print(f"\n✅ Material: {mat['material']}")
            print(f"   Clase YOLO: {mat['clase_original']}")
            print(f"   Confianza: {mat['confianza']}%")
    else:
        print("\n❌ No se detectaron materiales de reciclaje")
    
    print("\n" + "="*50)
    print(json.dumps(resultado, indent=2))
