import pandas as pd
from sqlalchemy import text
from conexion import obtener_conexion


def consultar(query, parametros=None):
    """Ejecuta una query SQL y devuelve un DataFrame.

    Los valores variables van como parametros (:nombre), nunca pegados al texto:
        consultar("SELECT * FROM diabetes WHERE Outcome = :valor", {"valor": 1})
    """
    conexion = obtener_conexion()
    return pd.read_sql(text(query), conexion, params=parametros)


if __name__ == "__main__":
    df = consultar("SELECT * FROM diabetes")
    print("ESTAS SON LAS PRIMERAS 5 FILAS QUE SE MUESTRAN DE LA BASE DE DATOS")
    print(df.head())

    df_conteo = consultar("""
        SELECT Outcome, COUNT(*) AS total
        FROM diabetes
        GROUP BY Outcome
    """)
    print('----------------------------------------------------------------------')
    print("CUANTAS PERSONAS TIENEN DIABETES (1) Y CUANTAS NO (0)")
    print(df_conteo)

    df_promedios = consultar("""
        SELECT Outcome,
               AVG(Glucose) AS glucosa_promedio,
               AVG(BMI) AS bmi_promedio,
               AVG(Age) AS edad_promedio
        FROM diabetes
        GROUP BY Outcome
    """)
    print('----------------------------------------------------------------------')
    print("PROMEDIOS DE GLUCOSA, BMI Y EDAD, SEGUN SI TIENEN DIABETES O NO")
    print(df_promedios)

    df_rangos = consultar("""
        SELECT MIN(Age) AS edad_min, MAX(Age) AS edad_max,
               MIN(Glucose) AS glucosa_min, MAX(Glucose) AS glucosa_max,
               MIN(BMI) AS bmi_min, MAX(BMI) AS bmi_max
        FROM diabetes
    """)
    print('----------------------------------------------------------------------')
    print("RANGOS DE EDAD, GLUCOSA Y BMI")
    print(df_rangos)
