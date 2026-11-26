from db import get_redis
from catalogo import obtener_promocion

PREFIJO_PROMO = "promo:"

# Script Lua atómico para activar una promoción en Redis (Tareas B-02 y B-03).
# Devuelve 0 si la llave promo:{id} ya existe (activa o agotada con TTL vigente).
# Si no existe, crea el Hash con nombre, departamento y cupones, fija el TTL y devuelve 1.
LUA_ACTIVAR_PROMO = """
if redis.call('EXISTS', KEYS[1]) == 1 then
    return 0
end
redis.call('HSET', KEYS[1], 'nombre', ARGV[1], 'departamento', ARGV[2], 'cupones', ARGV[3])
redis.call('EXPIRE', KEYS[1], tonumber(ARGV[4]))
return 1
"""


def formatear_tiempo_restante(segundos_restantes):
    """Convierte segundos restantes al formato legible 'vence en N minutos y M segundos'."""
    segundos = max(0, int(segundos_restantes))
    minutos, segs = divmod(segundos, 60)
    etiqueta_min = "minuto" if minutos == 1 else "minutos"
    etiqueta_seg = "segundo" if segs == 1 else "segundos"
    return f"vence en {minutos} {etiqueta_min} y {segs} {etiqueta_seg}"


def _parsear_entero_positivo(valor):
    """Valida que un valor represente un entero estricto mayor que 0."""
    if isinstance(valor, bool) or valor is None:
        return None
    if isinstance(valor, int):
        return valor if valor > 0 else None
    if isinstance(valor, str):
        texto = valor.strip()
        if not texto or not texto.isdigit():
            return None
        numero = int(texto)
        return numero if numero > 0 else None
    return None


def _buscar_promocion_catalogo(promo_id):
    """Busca la promoción en MongoDB respetando _id como string o entero."""
    promo = obtener_promocion(promo_id)
    if promo is not None:
        return promo

    if isinstance(promo_id, str) and promo_id.strip().isdigit():
        return obtener_promocion(int(promo_id.strip()))

    return None


def activar(promo_id, cupones, minutos):
    """
    Activa una promoción del catálogo en Redis con cantidad de cupones y TTL en segundos (Tarea B-03).

    Retorna:
        tuple[bool, str]: (exito, mensaje)
    """
    if promo_id is None or str(promo_id).strip() == "":
        return False, "Debes seleccionar una promoción válida del catálogo."

    promo_id_limpio = promo_id.strip() if isinstance(promo_id, str) else promo_id

    cupones_int = _parsear_entero_positivo(cupones)
    if cupones_int is None:
        return False, "La cantidad de cupones debe ser un número entero mayor que 0."

    minutos_int = _parsear_entero_positivo(minutos)
    if minutos_int is None:
        return False, "La duración en minutos debe ser un número entero mayor que 0."

    try:
        promo = _buscar_promocion_catalogo(promo_id_limpio)
        if not promo:
            return False, "La promoción seleccionada no existe en el catálogo."

        id_real = str(promo["_id"])
        nombre = str(promo.get("nombre", "")).strip()
        # Se guarda el departamento exactamente como viene en el catálogo (sin .lower())
        departamento = str(promo.get("departamento", "")).strip()

        llave = f"{PREFIJO_PROMO}{id_real}"
        ttl_segundos = minutos_int * 60

        r = get_redis()
        activada = r.eval(
            LUA_ACTIVAR_PROMO,
            1,
            llave,
            nombre,
            departamento,
            str(cupones_int),
            str(ttl_segundos),
        )

        if activada == 0:
            return False, "La promoción ya está activa."

        etiqueta_cup = "cupón" if cupones_int == 1 else "cupones"
        etiqueta_min = "minuto" if minutos_int == 1 else "minutos"
        return (
            True,
            f"Promoción '{nombre}' activada con {cupones_int} {etiqueta_cup} durante {minutos_int} {etiqueta_min}.",
        )
    except Exception as e:
        return False, f"Error al activar la promoción: {str(e)}"


def listar_activas():
    """
    Recorre con SCAN las llaves promo:* en Redis y retorna las promociones vigentes (Tarea B-05).
    No incluye promociones vencidas; sí incluye promociones agotadas (0 cupones) mientras su TTL siga activo.

    Retorna:
        list[dict]: Cada elemento cumple el contrato con:
            - id (str)
            - nombre (str)
            - departamento (str)
            - cupones (int)
            - segundos_restantes (int)
            - tiempo_restante (str, auxiliar para la vista)
    """
    r = get_redis()
    activas = []

    for llave in r.scan_iter(match=f"{PREFIJO_PROMO}*"):
        ttl = r.ttl(llave)
        # -2: llave ya expiró; -1: sin TTL; 0: expirando
        if ttl is None or ttl <= 0:
            continue

        datos = r.hgetall(llave)
        if not datos:
            continue

        promo_id = llave[len(PREFIJO_PROMO):]
        try:
            cupones_disp = int(datos.get("cupones", 0))
        except (TypeError, ValueError):
            cupones_disp = 0

        activas.append(
            {
                "id": promo_id,
                "nombre": datos.get("nombre", ""),
                "departamento": datos.get("departamento", ""),
                "cupones": cupones_disp,
                "segundos_restantes": int(ttl),
                "tiempo_restante": formatear_tiempo_restante(ttl),
            }
        )

    activas.sort(key=lambda item: (item["segundos_restantes"], item["nombre"].lower()))
    return activas
