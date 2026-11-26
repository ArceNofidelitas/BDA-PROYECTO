from flask import Flask, render_template, request, flash, redirect, url_for
import json
from catalogo import procesar_carga_inicial, listar_promociones
from reportes import consultar_por_departamento
from db import inicializar_mongo  # Corrección 3: Importamos la inicialización
from activas import activar, listar_activas  # Integrante 2 (Haiskel): Redis y promociones activas

app = Flask(__name__)
app.secret_key = 'super_secreto_cupones'

# ------------------------------------------------------------------
# STUB temporal para la integración de Emmanuel (Integrante 3)
# ------------------------------------------------------------------
def obtener_cupon(cliente, promo_id):
    # Stub temporal para Emmanuel
    return {"codigo": "TEST-123", "mensaje": "Cupón de prueba"}

# Corrección 3: Ejecutamos la función de crear la colección y los índices
# Así nos aseguramos de que cliente+promo sean únicos cada vez que arranca el server
inicializar_mongo()

# ------------------------------------------------------------------
# RUTAS DE LA APLICACIÓN
# ------------------------------------------------------------------
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

# Funcionalidad 2 (Integrante 2 - Haiskel)
@app.route('/activar-promocion', methods=['GET', 'POST'])
def activar_promocion():
    if request.method == 'POST':
        promo_id = request.form.get('promo_id', '').strip()
        cupones = request.form.get('cupones', '').strip()
        minutos = request.form.get('minutos', '').strip()

        exito, mensaje = activar(promo_id, cupones, minutos)
        flash(mensaje, 'success' if exito else 'error')
        return redirect(url_for('activar_promocion'))

    promociones = listar_promociones()
    return render_template('activar.html', promociones=promociones)

# Funcionalidad 3 (Integrante 2 - Haiskel)
@app.route('/promociones-activas')
@app.route('/ver-promociones')
def ver_promociones():
    promociones_activas = []
    try:
        promociones_activas = listar_activas()
    except Exception as e:
        flash(f'Error al consultar Redis: {str(e)}', 'error')

    return render_template('activas.html', promociones=promociones_activas)

# Funcionalidad 4 (Integrante 3 - Emmanuel)
@app.route('/obtener-cupon')
def pedir_cupon():
    return str(obtener_cupon("test", "promo123"))  # Emmanuel conectará su lógica aquí

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

if __name__ == '__main__':
    app.run(debug=True)
