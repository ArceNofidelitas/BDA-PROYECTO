from db import get_mongo


def quitar_tildes(texto):
    tildes = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
    }
    for con_tilde, sin_tilde in tildes.items():
        texto = texto.replace(con_tilde, sin_tilde)
    return texto


def consultar_por_departamento(nombre_departamento=""):
    try:
        db = get_mongo()

        # 1. Obtenemos los departamentos desde el catálogo de promociones
        #    (y sumamos cualquier departamento presente en cupones para no perder registros de prueba)
        deptos_promos = [d for d in db.promociones.distinct("departamento") if d]
        deptos_cupones = [d for d in db.cupones.distinct("departamento") if d]
        todos_deptos = list(dict.fromkeys(deptos_promos + deptos_cupones))

        if not todos_deptos:
            return []

        deptos_a_buscar = []
        if nombre_departamento and nombre_departamento.strip():
            depto_buscado_limpio = quitar_tildes(nombre_departamento.strip().lower())
            for depto in todos_deptos:
                if quitar_tildes(depto.strip().lower()) == depto_buscado_limpio:
                    deptos_a_buscar.append(depto)

            if not deptos_a_buscar:
                return []
        else:
            deptos_a_buscar = todos_deptos

        # 2. Agregación en cupones: total de cupones y clientes distintos por departamento
        pipeline = [
            {"$match": {"departamento": {"$in": deptos_a_buscar}}},
            {
                "$group": {
                    "_id": "$departamento",
                    "total_cupones": {"$sum": 1},
                    "clientes_distintos_set": {"$addToSet": "$cliente"},
                }
            },
            {
                "$project": {
                    "departamento": "$_id",
                    "total_cupones": 1,
                    "clientes_distintos": {"$size": "$clientes_distintos_set"},
                    "_id": 0,
                }
            },
        ]

        agregados = list(db.cupones.aggregate(pipeline))
        resumen_por_depto = {fila["departamento"]: fila for fila in agregados}

        # 3. Construimos el resultado incluyendo los departamentos con 0 cupones
        resultados = []
        for depto in sorted(deptos_a_buscar, key=lambda d: quitar_tildes(d.lower())):
            if depto in resumen_por_depto:
                resultados.append(resumen_por_depto[depto])
            else:
                resultados.append(
                    {
                        "departamento": depto,
                        "total_cupones": 0,
                        "clientes_distintos": 0,
                    }
                )

        return resultados

    except Exception as e:
        print(f"Error en consulta por departamento: {e}")
        return []
