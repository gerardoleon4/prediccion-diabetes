import sys
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, redirect, render_template, request, url_for
from sqlalchemy import text

# conexion.py vive en scripts/
CARPETA = Path(__file__).parent
sys.path.append(str(CARPETA.parent / 'scripts'))
from conexion import obtener_conexion  # noqa: E402

app = Flask(__name__)

# Cargar el modelo cuando se inicia el servidor
modelo = joblib.load(CARPETA.parent / 'modelo' / 'diabetes.joblib')
conexion = obtener_conexion()

COLORES = {
    'Diabetico': '#c2410c',
    'No diabetico': '#0f766e',
}

DESCRIPCIONES = {
    'Diabetico': 'El perfil se parece al de las pacientes del estudio que fueron diagnosticadas con diabetes.',
    'No diabetico': 'El perfil se parece al de las pacientes del estudio que no tenían diabetes.',
}

# Valores de referencia clínicos para señalar qué datos conviene vigilar.
# La glucosa del estudio Pima es la de 2 horas en la prueba de tolerancia oral.
REFERENCIAS = [
    ('glucose', 140, 'Glucosa', 'mg/dL', 'alta en la prueba de tolerancia (desde 140)'),
    ('bmi', 30, 'IMC', 'kg/m²', 'en rango de obesidad (desde 30)'),
    ('blood_pressure', 90, 'Presión diastólica', 'mm Hg', 'alta (desde 90)'),
    ('age', 45, 'Edad', 'años', 'grupo con más riesgo (desde 45)'),
]

# Nombre del campo del formulario -> columna que espera el modelo
COLUMNAS = {
    'pregnancies': 'Pregnancies',
    'glucose': 'Glucose',
    'blood_pressure': 'BloodPressure',
    'skin_thickness': 'SkinThickness',
    'insulin': 'Insulin',
    'bmi': 'BMI',
    'pedigree': 'DiabetesPedigreeFunction',
    'age': 'Age',
}


def crear_tabla_predicciones():
    """Cada vez que alguien llena el formulario se guarda aquí quién fue y qué salió."""
    with conexion.begin() as c:
        c.execute(text("""
            CREATE TABLE IF NOT EXISTS predicciones (
                Id INT AUTO_INCREMENT PRIMARY KEY,
                Nombre VARCHAR(80) NOT NULL,
                Fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                Pregnancies FLOAT, Glucose FLOAT, BloodPressure FLOAT, SkinThickness FLOAT,
                Insulin FLOAT, BMI FLOAT, DiabetesPedigreeFunction FLOAT, Age FLOAT,
                Resultado VARCHAR(20) NOT NULL,
                Confianza INT NOT NULL
            )
        """))


def guardar_prediccion(nombre, numeros, resultado, confianza):
    columnas = ', '.join(COLUMNAS.values())
    parametros = ', '.join(':' + campo for campo in COLUMNAS)
    # las columnas FLOAT guardan 33.6 como 33.599998, por eso se compara con tolerancia
    mismos_datos = ' AND '.join(f'ABS({columna} - :{campo}) < 0.001' for campo, columna in COLUMNAS.items())
    with conexion.begin() as c:
        # un doble clic o un reenvío no debe guardar la misma evaluación dos veces
        repetida = c.execute(
            text(f"SELECT COUNT(*) FROM predicciones WHERE Nombre = :nombre AND {mismos_datos} "
                 "AND Fecha >= NOW() - INTERVAL 10 SECOND"),
            {'nombre': nombre, **numeros},
        ).scalar()
        if repetida:
            return
        c.execute(
            text(f"INSERT INTO predicciones (Nombre, {columnas}, Resultado, Confianza) "
                 f"VALUES (:nombre, {parametros}, :resultado, :confianza)"),
            {'nombre': nombre, **numeros, 'resultado': resultado, 'confianza': confianza},
        )


def valores_a_vigilar(numeros):
    return [
        {'nombre': nombre, 'valor': f"{numeros[campo]:g} {unidad}", 'nota': nota}
        for campo, umbral, nombre, unidad, nota in REFERENCIAS
        if numeros[campo] >= umbral
    ]


@app.route('/')
def inicio():
    return render_template('index.html', valores={}, prediccion=None, error=None, probabilidades=None)


@app.route('/predecir', methods=['POST'])
def predecir():
    valores = request.form
    nombre = request.form.get('nombre', '').strip()[:80]
    if not nombre:
        return render_template('index.html', valores=valores, prediccion=None, probabilidades=None,
                               error='Escribe tu nombre para guardar la evaluación.')
    try:
        numeros = {campo: float(request.form[campo].replace(',', '.')) for campo in COLUMNAS}
        if any(numero < 0 for numero in numeros.values()):
            raise ValueError('valor negativo')
        datos = {columna: [numeros[campo]] for campo, columna in COLUMNAS.items()}
        paciente_inventado = pd.DataFrame(datos)[modelo.feature_names_in_]
    except (KeyError, ValueError):
        return render_template('index.html', valores=valores, prediccion=None, probabilidades=None,
                               error='Revisa los datos: todos deben ser números de 0 en adelante.')

    prediccion_final = str(modelo.predict(paciente_inventado)[0])
    probas = modelo.predict_proba(paciente_inventado)[0]
    probabilidades = [
        {'clase': str(clase), 'valor': round(float(p) * 100), 'color': COLORES[str(clase)]}
        for clase, p in zip(modelo.classes_, probas)
    ]
    confianza = round(float(max(probas)) * 100)

    # si la base de datos no responde, igual se muestra la predicción
    try:
        guardar_prediccion(nombre, numeros, prediccion_final, confianza)
        guardado = True
    except Exception as error:
        app.logger.warning('No se pudo guardar la predicción: %s', error)
        guardado = False

    return render_template('index.html', valores=valores, prediccion=prediccion_final,
                           probabilidades=probabilidades, confianza=confianza,
                           descripcion=DESCRIPCIONES[prediccion_final],
                           vigilar=valores_a_vigilar(numeros),
                           nombre=nombre, guardado=guardado,
                           color=COLORES[prediccion_final], error=None)


@app.route('/registros')
def registros():
    filas = pd.read_sql(text("SELECT * FROM predicciones ORDER BY Id DESC LIMIT 100"), conexion)
    return render_template('registros.html', filas=filas.to_dict('records'),
                           borrados=request.args.get('borrados', type=int))


@app.route('/registros/borrar', methods=['POST'])
def borrar_registros():
    with conexion.begin() as c:
        borrados = c.execute(text("DELETE FROM predicciones")).rowcount
    return redirect(url_for('registros', borrados=borrados))


crear_tabla_predicciones()

if __name__ == '__main__':
    # host='0.0.0.0' para que otras computadoras o teléfonos en la red lleguen al servidor
    app.run(host='0.0.0.0', port=5002, debug=True)
