from reportes import consultar_por_departamento
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html') # Menú principal

# Funcionalidad 1 (Integrante 1)
from flask import Flask, render_template, request, flash, redirect, url_for
import json
# Importamos la función de la lógica de negocio que acabas de crear
from catalogo import procesar_carga_inicial 

app = Flask(__name__)
# Flask requiere una clave secreta para poder mostrar mensajes de error o éxito (flash) en pantalla
app.secret_key = 'super_secreto_cupones' 

@app.route('/')
def index():
    return render_template('base.html')

# --- FUNCIONALIDAD 1: CARGA INICIAL (Integrante 1) ---
@app.route('/carga-inicial', methods=['GET', 'POST'])
def carga_inicial():
    if request.method == 'POST':
        # 1. Validar que se haya subido un archivo
        if 'archivo_json' not in request.files:
            flash('No se seleccionó ningún archivo.', 'error')
            return redirect(request.url)
            
        archivo = request.files['archivo_json']
        if archivo.filename == '':
            flash('El archivo no tiene nombre válido.', 'error')
            return redirect(request.url)
            
        # 2. Leer y procesar el archivo JSON
        try:
            # Agregamos -sig para ignorar los caracteres invisibles de Windows
            contenido = archivo.read().decode('utf-8-sig') 
            datos_json = json.loads(contenido)
            
            # 3. Enviar a catalogo.py para que guarde en MongoDB
            total, mensaje = procesar_carga_inicial(datos_json)
            
            # 3. Enviar a catalogo.py para que guarde en MongoDB
            total, mensaje = procesar_carga_inicial(datos_json)
            
            if total > 0:
                flash(f'Éxito: {total} promociones cargadas o actualizadas en el catálogo.', 'success')
            else:
                flash(mensaje, 'error')
                
        except json.JSONDecodeError:
            flash('Error: El archivo no es un JSON válido o está corrupto.', 'error')
        except Exception as e:
            flash(f'Error inesperado: {str(e)}', 'error')
            
        return redirect(url_for('carga_inicial'))
        
    # Si es GET, mostramos la pantalla HTML
    return render_template('carga.html')


# Funcionalidad 2 (Integrante 2)
@app.route('/activar-promocion')
def activar_promocion():
    return "Ruta de Activar Promoción funcionando"

# Funcionalidad 3 (Integrante 2)
@app.route('/promociones-activas')
def promociones_activas():
    return "Ruta de Promociones Activas funcionando"

# Funcionalidad 4 (Integrante 3)
@app.route('/obtener-cupon')
def obtener_cupon():
    return "Ruta de Obtener Cupón funcionando"


# Funcionalidad 5 (Integrante 1)
@app.route('/consulta-departamento', methods=['GET', 'POST'])
def consulta_departamento():
    cupones = []
    departamento_buscado = ""
    
    if request.method == 'POST':
        # Capturamos lo que el usuario escribió en el buscador
        departamento_buscado = request.form.get('departamento', '')
        
        if departamento_buscado:
            # Llamamos a tu función de reportes.py
            cupones = consultar_por_departamento(departamento_buscado)
            
            if not cupones:
                flash(f'No se encontraron cupones para el departamento "{departamento_buscado}".', 'error')
                
    return render_template('consulta.html', cupones=cupones, departamento=departamento_buscado)

if __name__ == '__main__':
    app.run(debug=True)