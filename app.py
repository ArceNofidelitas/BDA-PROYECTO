from flask import Flask, render_template, request, flash, redirect, url_for
import json
from catalogo import procesar_carga_inicial 
from reportes import consultar_por_departamento
from db import inicializar_mongo # Corrección 3: Importamos la inicialización

app = Flask(__name__)
app.secret_key = 'super_secreto_cupones' 

# -------------------------------------------------------------
# STUBS para las integraciones de Haiskel (2) y Emmanuel (3)
# -------------------------------------------------------------
def listar_activas():
    # Stub temporal para Haiskel
    return [{"id": "promo_falsa", "nombre": "Promo Test", "descuento": 10}]
    
def obtener_cupon(cliente, promo_id):
    # Stub temporal para Emmanuel
    return {"codigo": "TEST-123", "mensaje": "Cupón de prueba"}

# Corrección 3: Ejecutamos la función de crear la colección y los índices
# Así nos aseguramos de que cliente+promo sean únicos cada vez que arranca el server
inicializar_mongo()

# -------------------------------------------------------------
# RUTAS DE LA APLICACIÓN
# -------------------------------------------------------------
@app.route('/')
def index():
    return render_template('base.html')

# Funcionalidad 1 (Integrante 1)
@app.route('/carga-inicial', methods=['GET', 'POST'])
def carga_inicial():
    if request.method == 'POST':
        if 'archivo_json' not in request.files:
            flash('No se seleccionó ningún archivo.', 'error')
            return redirect(request.url)
            
        archivo = request.files['archivo_json']
        if archivo.filename == '':
            flash('El archivo no tiene nombre válido.', 'error')
            return redirect(request.url)
            
        try:
            contenido = archivo.read().decode('utf-8-sig') 
            datos_json = json.loads(contenido)
            
            # Corrección 4: Se limpia la llamada duplicada. Se llama UNA sola vez.
            total, mensaje = procesar_carga_inicial(datos_json)
            
            if total > 0:
                flash(f'Éxito: {total} promociones cargadas.', 'success')
            else:
                flash(mensaje, 'error')
                
        except json.JSONDecodeError:
            flash('Error: El archivo no es un JSON válido o está corrupto.', 'error')
        except Exception as e:
            flash(f'Error inesperado: {str(e)}', 'error')
            
        return redirect(url_for('carga_inicial'))
        
    return render_template('carga.html')

# Funcionalidad 5 (Integrante 1)
@app.route('/consulta-departamento', methods=['GET', 'POST'])
def consulta_departamento():
    cupones = []
    departamento_buscado = ""
    
    if request.method == 'POST':
        departamento_buscado = request.form.get('departamento', '')
        
    # Llama siempre a la consulta, esté vacío o no (Corrección 1 para Emmanuel)
    cupones = consultar_por_departamento(departamento_buscado)
        
    return render_template('consulta.html', cupones=cupones, departamento=departamento_buscado)

# -------------------------------------------------------------
# RUTAS PENDIENTES (Haiskel y Emmanuel las llenarán)
# -------------------------------------------------------------
@app.route('/activar-promocion')
def activar_promocion():
    return render_template('base.html') # Haiskel armará su página aquí

@app.route('/ver-promociones')
def ver_promociones():
    return str(listar_activas()) # Haiskel conectará su lógica aquí

@app.route('/obtener-cupon')
def pedir_cupon():
    return str(obtener_cupon("test", "promo123")) # Emmanuel conectará su lógica aquí

if __name__ == '__main__':
    app.run(debug=True)