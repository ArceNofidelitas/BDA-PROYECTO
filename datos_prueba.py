from db import get_mongo
from datetime import datetime

def insertar_datos_prueba():
    try:
        db = get_mongo()
        
        cupones_mock = [
            {
                "codigo": "ELEC-0001",
                "cliente": "ana", # El contrato dice cliente en minúscula, eso está bien
                "promocion_id": "promo123",
                "promocion_nombre": "Descuento en Laptops",
                "departamento": "Electrónica", # Ahora respetamos cómo viene del catálogo (Punto 2)
                "fecha_hora": datetime.now(),
                "origen": "test_gabriel" # Etiqueta para identificar tus pruebas (Punto 6)
            },
            {
                "codigo": "ELEC-0002",
                "cliente": "juan",
                "promocion_id": "promo123",
                "promocion_nombre": "Descuento en Laptops",
                "departamento": "Electrónica",
                "fecha_hora": datetime.now(),
                "origen": "test_gabriel"
            },
            {
                "codigo": "ROPA-0001",
                "cliente": "ana",
                "promocion_id": "promo999",
                "promocion_nombre": "Liquidación Zapatos",
                "departamento": "Ropa",
                "fecha_hora": datetime.now(),
                "origen": "test_gabriel"
            }
        ]
        
        # Solo borramos los que tengan TU etiqueta, respetando si Emmanuel metió otros para ana/juan (Punto 6)
        db.cupones.delete_many({"origen": "test_gabriel"})
        
        # Insertamos los nuevos
        db.cupones.insert_many(cupones_mock)
        print(" Datos de prueba de Gabriel insertados correctamente en MongoDB.")
        
    except Exception as e:
        print(f" Error al insertar datos de prueba: {e}")

if __name__ == '__main__':
    print("Iniciando carga de datos de prueba...")
    insertar_datos_prueba()