from db import get_mongo
from datetime import datetime

def insertar_datos_prueba():
    try:
        db = get_mongo()
        
        # Cupones falsos para Ana y Juan
        cupones_mock = [
            {
                "codigo": "ELEC-0001",
                "cliente": "ana", # Normalizado en minúsculas según las reglas
                "promocion_id": "promo123",
                "promocion_nombre": "Descuento en Laptops",
                "departamento": "electronica",
                "fecha_hora": datetime.now()
            },
            {
                "codigo": "ELEC-0002",
                "cliente": "juan",
                "promocion_id": "promo123",
                "promocion_nombre": "Descuento en Laptops",
                "departamento": "electronica",
                "fecha_hora": datetime.now()
            },
            {
                "codigo": "ROPA-0001",
                "cliente": "ana",
                "promocion_id": "promo999",
                "promocion_nombre": "Liquidación Zapatos",
                "departamento": "ropa",
                "fecha_hora": datetime.now()
            }
        ]
        
        # Borramos los de prueba anteriores para evitar que el índice único bloquee la inserción si corres el script 2 veces
        db.cupones.delete_many({"cliente": {"$in": ["ana", "juan"]}})
        
        # Insertamos los nuevos
        db.cupones.insert_many(cupones_mock)
        print(" Datos de prueba para Ana y Juan insertados correctamente en MongoDB.")
        
    except Exception as e:
        print(f" Error al insertar datos de prueba: {e}")

if __name__ == '__main__':
    print("Iniciando carga de datos de prueba...")
    insertar_datos_prueba()