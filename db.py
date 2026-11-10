#De aqui hasta la linea 29 es de la A01
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import redis

# Configuración MongoDB
MONGO_URI = "mongodb://localhost:27017/"

# Configuración Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

def get_mongo():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        # El comando ping fuerza la conexión para verificar que el servidor esté arriba
        client.admin.command('ping')
        return client["tienda"]
    except ConnectionFailure:
        raise Exception("Error crítico: No se pudo conectar a MongoDB. Verifica que el servicio esté activo.")

def get_redis():
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        # Ping verifica si Redis está corriendo
        r.ping()
        return r
    except redis.ConnectionError:
        raise Exception("Error crítico: No se pudo conectar a Redis. Verifica que el servicio esté activo.")


#ESTO DE AQUI ES DE LA A-07
def inicializar_mongo():
    try:
        db = get_mongo()
        
        # 1. Índice en la colección 'promociones'
        db.promociones.create_index("departamento")
        
        # 2. Índices en la colección 'cupones'
        db.cupones.create_index("codigo", unique=True)
        db.cupones.create_index([("cliente", 1), ("promocion_id", 1)], unique=True)
        
        # 3. Crear la colección 'contadores' explícitamente si no existe
        if "contadores" not in db.list_collection_names():
            db.create_collection("contadores")
            
        print("✅ Índices y colecciones de MongoDB inicializados correctamente.")
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")




# --- PRUEBA DE CONEXIÓN E INICIALIZACIÓN --- A01
if __name__ == '__main__':
    print("Iniciando prueba de conexiones...")
    try:
        db = get_mongo()
        print("✅ MongoDB conectado exitosamente. Base de datos:", db.name)
        
        r = get_redis()
        print("✅ Redis conectado exitosamente.")
        
        print("\nEjecutando inicialización de Tarea A-07...")
        inicializar_mongo()
        
        print("\n¡Tareas A-02 y A-07 completadas!")
    except Exception as e:
        print("\n❌ FALLO EN LA PRUEBA:")
        print(e)