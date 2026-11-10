# Proyecto NoSQL Cupones

Este proyecto utiliza Flask, MongoDB y Redis. Sigue estos pasos para levantar el entorno de desarrollo local.

## 1. Configurar el Entorno Virtual (Python)
Abre una terminal en la raíz del proyecto y ejecuta:
1. Crea el entorno virtual: `python -m venv venv`
2. Activa el entorno:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
3. Instala las dependencias necesarias: `pip install -r requirements.txt`

## 2. Levantar MongoDB
1. Asegúrate de tener instalado **MongoDB Community Server** y **MongoDB Compass**.
2. Abre MongoDB Compass y conéctate a la URI por defecto: `mongodb://localhost:27017/`
3. La base de datos `tienda` se creará automáticamente cuando insertemos el primer dato.

## 3. Levantar Redis (En Windows usando WSL)
Si usas Windows, la forma más estable de correr Redis es mediante el Subsistema de Windows para Linux (WSL).
1. Abre tu terminal de Ubuntu/WSL.
2. Actualiza los paquetes: `sudo apt update`
3. Instala Redis: `sudo apt install redis-server`
4. Inicia el servicio en segundo plano: `sudo service redis-server start`
5. Verifica que está corriendo escribiendo `redis-cli ping` (debería responder `PONG`).

## 4. Ejecutar la Aplicación
Con las dos bases de datos corriendo y el entorno virtual activado (`venv`), ejecuta:
```bash
python app.py