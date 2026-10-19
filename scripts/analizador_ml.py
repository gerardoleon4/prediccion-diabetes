import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from conexion import obtener_conexion

CARACTERISTICAS = [
    'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
    'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age',
]

conexion = obtener_conexion()
df_pacientes = pd.read_sql("SELECT * FROM diabetes", conexion)

# Separar variables "X" (features) y "y" (etiqueta a predecir)
X = df_pacientes[CARACTERISTICAS]
y = df_pacientes['Outcome'].map({1: 'Diabetico', 0: 'No diabetico'})

# Dividir los datos en conjunto de entrenamiento y prueba (misma proporcion de cada clase en ambos)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"Pacientes para estudiar (entrenamiento): {len(X_train)}")
print(f"Pacientes para probar (prueba): {len(X_test)}")

# Crear y entrenar el modelo (Bosque Aleatorio: varios arboles de decision votando)
modelo = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42)
modelo.fit(X_train, y_train)

# Probar el modelo con pacientes que no vio durante el entrenamiento
y_pred = modelo.predict(X_test)

precision = accuracy_score(y_test, y_pred)
print(f"\nPrecision del modelo: {precision:.2%}")
print(classification_report(y_test, y_pred))
