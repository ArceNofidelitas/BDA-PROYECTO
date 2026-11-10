from db import get_mongo
from pymongo import UpdateOne

def listar_promociones():
    """Devuelve todas las promociones del catálogo (Tarea A-06)."""
    try:
        db = get_mongo()
        # Retorna una lista con todos los documentos de la colección
        return list(db.promociones.find({}))
    except Exception as e:
        print(f"Error al listar promociones: {e}")
        return []

def obtener_promocion(id_promo):
    """Busca una promoción específica por su _id (Tarea A-06)."""
    try:
        db = get_mongo()
        # Busca el documento cuyo _id coincida
        return db.promociones.find_one({"_id": id_promo})
    except Exception as e:
        print(f"Error al obtener promoción {id_promo}: {e}")
        return None

def procesar_carga_inicial(datos_json):
    """Procesa el JSON y hace insert o update por id (Tarea A-05)."""
    try:
        db = get_mongo()
        
        # 1. Identificar si es una lista directa o un objeto que contiene una lista
        lista_promos = []
        if isinstance(datos_json, list):
            lista_promos = datos_json
        elif isinstance(datos_json, dict):
            # Busca el primer valor que sea una lista dentro del objeto
            for valor in datos_json.values():
                if isinstance(valor, list):
                    lista_promos = valor
                    break
                    
        if not lista_promos:
            return 0, "Error: El archivo JSON no contiene una lista válida de promociones."

        # 2. Preparar operaciones masivas (Bulk Write) para mayor eficiencia
        operaciones = []
        for promo in lista_promos:
            # Capturamos el id que viene del JSON
            promo_id = promo.get("id") or promo.get("_id")
            
            if promo_id:
                # Mongo utiliza _id como llave primaria obligatoria
                promo["_id"] = promo_id 
                # Eliminamos el "id" viejo si existe para no tener datos duplicados
                if "id" in promo:
                    del promo["id"]
                
                # UpdateOne con upsert=True: si el _id existe lo actualiza, si no, lo inserta
                # Al usar $set pasamos el objeto entero, guardando atributos propios tal cual vengan
                operaciones.append(UpdateOne({"_id": promo_id}, {"$set": promo}, upsert=True))

        # 3. Ejecutar la operación en la base de datos
        if operaciones:
            resultado = db.promociones.bulk_write(operaciones)
            total_procesadas = len(operaciones)
            return total_procesadas, "Éxito"
        else:
            return 0, "El JSON no contenía promociones con un campo 'id' válido."

    except Exception as e:
        return 0, f"Error interno en la base de datos: {str(e)}"