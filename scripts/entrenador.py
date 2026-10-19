import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from conexion import obtener_conexion
import joblib
from pathlib import Path

CARACTERISTICAS = [
    'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
    'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age',
]

conexion = obtener_conexion()
df_pacientes = pd.read_sql("SELECT * FROM diabetes", conexion)

# SEPARAR VARIABLES "X", "y"
X = df_pacientes[CARACTERISTICAS]
y = df_pacientes['Outcome'].map({1: 'Diabetico', 0: 'No diabetico'})

print("ENTRENANDO EL MODELO FINAL (Bosque Aleatorio)")
modelo_produccion = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42)
modelo_produccion.fit(X, y)
joblib.dump(modelo_produccion, Path(__file__).parent.parent / 'modelo' / 'diabetes.joblib', compress=3)
print("Modelo guardado en modelo/diabetes.joblib")
