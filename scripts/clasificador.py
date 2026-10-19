import pandas as pd
import joblib
from pathlib import Path

# CARGAR EL MODELO ENTRENADO (NO NECESITA LA BASE DE DATOS)
modelo = joblib.load(Path(__file__).parent.parent / 'modelo' / 'diabetes.joblib')

PREGUNTAS = {
    'Pregnancies': 'NUMERO DE EMBARAZOS',
    'Glucose': 'GLUCOSA (mg/dL)',
    'BloodPressure': 'PRESION ARTERIAL (mm Hg)',
    'SkinThickness': 'GROSOR DE PIEL (mm)',
    'Insulin': 'INSULINA (mu U/ml)',
    'BMI': 'INDICE DE MASA CORPORAL (kg/m²)',
    'DiabetesPedigreeFunction': 'ANTECEDENTES FAMILIARES (ej. 0.45)',
    'Age': 'EDAD',
}

while True:
    print('----------------------------------------------------------------------')
    print("PREDICTOR DE DIABETES (USANDO modelo/diabetes.joblib)")
    print('ESCRIBE "salir" PARA FINALIZAR EL PROGRAMA')
    try:
        paciente = {}
        for numero, columna in enumerate(modelo.feature_names_in_, start=1):
            dato = input(f"{numero}-ESCRIBE {PREGUNTAS[columna]}: ")
            if dato.lower() == "salir":
                raise SystemExit
            paciente[columna] = [float(dato)]

        paciente_nuevo = pd.DataFrame(paciente)
        prediccion = modelo.predict(paciente_nuevo)[0]
        probabilidad = modelo.predict_proba(paciente_nuevo)[0].max()
        print(f" RESULTADO: {prediccion} ({probabilidad * 100:.0f}% de confianza)")
    except ValueError:
        print("ERROR EN LOS VALORES, NO SON VALIDOS")
