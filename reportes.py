from db import get_mongo
import re

def quitar_tildes(texto):
    tildes = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
              'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'}
    for con_tilde, sin_tilde in tildes.items():
        texto = texto.replace(con_tilde, sin_tilde)
    return texto

def consultar_por_departamento(nombre_departamento=""):
    try:
        db = get_mongo()
        
        deptos_a_buscar = []
        
        # 1. Obtenemos TODOS los departamentos únicos que existen en los cupones
        cupones_deptos = db.cupones.distinct("departamento")
        
        if nombre_departamento:
            depto_buscado_limpio = quitar_tildes(nombre_departamento.strip().lower())
            
            # 2. Filtramos la lista ignorando mayúsculas y tildes en Python
            for depto in cupones_deptos:
                depto_actual_limpio = quitar_tildes(depto.lower())
                if depto_actual_limpio == depto_buscado_limpio:
                    deptos_a_buscar.append(depto)
                    
            if not deptos_a_buscar:
                return [] # Si no encontró nada que coincida, devolvemos vacío
        else:
            deptos_a_buscar = cupones_deptos

        # 3. Agrupamos directamente en la colección de cupones (mucho más rápido y seguro)
        pipeline = [
            {"$match": {"departamento": {"$in": deptos_a_buscar}}},
            {
                "$group": {
                    "_id": "$departamento",
                    "total_cupones": {"$sum": 1},
                    "clientes_distintos_set": {"$addToSet": "$cliente"}
                }
            },
            {
                "$project": {
                    "departamento": "$_id",
                    "total_cupones": 1,
                    "clientes_distintos": {"$size": "$clientes_distintos_set"},
                    "_id": 0
                }
            },
            {"$sort": {"departamento": 1}}
        ]
        
        resultados = list(db.cupones.aggregate(pipeline))
        return resultados
        
    except Exception as e:
        print(f"Error en consulta por departamento: {e}")
        return []