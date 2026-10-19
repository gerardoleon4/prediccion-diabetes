# Predictor de diabetes

Proyecto de Machine Learning que predice si el perfil clínico de una paciente coincide con **diabetes** a partir de 8 datos: embarazos, glucosa, presión arterial, grosor de piel, insulina, índice de masa corporal, antecedentes familiares y edad. Usa el dataset [Pima Indians Diabetes](https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database): 768 mujeres de 21 años o más (268 con diabetes y 500 sin diabetes).

> Es un proyecto educativo: el resultado **no es un diagnóstico médico**.

## Flujo

1. **Volcado a MySQL.** `scripts/volcado.py` lee `datos/diabetes.csv`, corrige la columna `DiabetesPedigreeFunction` (el CSV trae `627` en vez de `0.627`), crea la base `diabetesdataset` y carga la tabla `diabetes`.
2. **Conexión.** `scripts/conexion.py` se conecta a la base con SQLAlchemy usando el archivo `.env`.
3. **Análisis.** `scripts/analizador.py` muestra las primeras filas, cuántas pacientes tienen diabetes y los promedios de glucosa, BMI y edad por grupo.
4. **Evaluación.** `scripts/analizador_ml.py` divide 80/20, entrena un **Random Forest** (200 árboles, `class_weight='balanced'` porque hay menos pacientes con diabetes) y mide la efectividad con las pacientes de prueba.
5. **Entrenamiento.** `scripts/entrenador.py` entrena el modelo final con las 768 pacientes y lo guarda en `modelo/diabetes.joblib`.
6. **Uso del modelo.** `scripts/clasificador.py` predice desde la terminal y `web/app.py` (Flask) desde una página web, mostrando el resultado y qué tan seguro está el modelo.
7. **Cliente ↔ servidor.** La computadora es el servidor (Flask + modelo + MySQL) y cualquier teléfono en la misma red es el cliente: abre `http://IP-de-la-computadora:5002`, llena el formulario con su nombre y recibe la predicción. Cada evaluación se guarda en la tabla `predicciones` y se puede consultar en `/registros`.

## Cómo correrlo

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env              # y poner la contraseña
```

Crear el usuario de MySQL (una sola vez):

```sql
CREATE USER 'diabetes_user'@'localhost' IDENTIFIED BY 'tu_contraseña';
GRANT ALL PRIVILEGES ON diabetesdataset.* TO 'diabetes_user'@'localhost';
```

```bash
.venv/bin/python scripts/volcado.py        # CSV -> MySQL
.venv/bin/python scripts/analizador.py     # exploración
.venv/bin/python scripts/analizador_ml.py  # efectividad del modelo
.venv/bin/python scripts/entrenador.py     # genera modelo/diabetes.joblib
.venv/bin/python scripts/clasificador.py   # predecir desde la terminal
.venv/bin/python web/app.py                # http://127.0.0.1:5002
```

`clasificador.py` solo necesita `modelo/diabetes.joblib`. La aplicación web también usa la base de datos para guardar las evaluaciones (crea la tabla `predicciones` sola al iniciar).

## Estructura

```
prediccion-diabetes/
├── datos/            diabetes.csv original
├── scripts/          conexion, volcado, analizador, analizador_ml, entrenador, clasificador
├── modelo/           diabetes.joblib
└── web/              app.py, templates/index.html y static/
```

## Tecnologías

Python · pandas · scikit-learn · MySQL + SQLAlchemy · joblib · Flask
