from db import get_mongo

def consultar_por_departamento(nombre_departamento):
    """
    Busca todos los cupones generados para un departamento específico (Tarea A-10).
    """
    try:
        db = get_mongo()
        
        # Normalizamos el texto (quitamos espacios a los lados y pasamos a minúsculas)
        # Esto evita errores si el usuario escribe " Electronica " o "ELECTRONICA"
        depto_limpio = nombre_departamento.strip().lower()
        
        # Buscamos en la colección 'cupones' 
        # sort("fecha_hora", -1) ordena los resultados del más nuevo al más antiguo
        cupones = list(db.cupones.find({"departamento": depto_limpio}).sort("fecha_hora", -1))
        
        return cupones
    except Exception as e:
        print(f"Error en consulta por departamento: {e}")
        return []