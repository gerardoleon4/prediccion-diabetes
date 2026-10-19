from pathlib import Path
import pandas as pd
from sqlalchemy import text
from sqlalchemy.types import Integer, Float
from conexion import obtener_conexion, obtener_conexion_servidor

ARCHIVO = Path(__file__).parent.parent / 'datos' / 'diabetes.csv'
TABLA = 'diabetes'


def arreglar_pedigri(valor):
    """El CSV trae DiabetesPedigreeFunction sin el "0." en los valores menores a 1:
    "627" es 0.627 y "78" es 0.078. Si el valor no tiene punto, son milesimas."""
    texto = str(valor).strip()
    if '.' not in texto:
        return int(texto) / 1000
    return float(texto)


def volcar_csv(archivo=ARCHIVO, tabla=TABLA):
    if not archivo.exists():
        raise SystemExit(f"No encuentro {archivo}. Copia diabetes.csv en la carpeta datos/.")

    # DiabetesPedigreeFunction se lee como texto: si no, pandas sube toda la columna a
    # float antes de que podamos ver si al valor original le faltaba el punto decimal.
    df = pd.read_csv(archivo, dtype={'DiabetesPedigreeFunction': str})
    df['DiabetesPedigreeFunction'] = df['DiabetesPedigreeFunction'].apply(arreglar_pedigri)
    df.insert(0, 'Id', range(1, len(df) + 1))

    servidor = obtener_conexion_servidor()
    nombre_bd = obtener_conexion().url.database
    with servidor.begin() as c:
        c.execute(text(f"CREATE DATABASE IF NOT EXISTS `{nombre_bd}`"))

    conexion = obtener_conexion()
    df.to_sql(
        tabla, conexion, if_exists='replace', index=False,
        dtype={
            'Id': Integer(),
            'Pregnancies': Integer(),
            'Glucose': Integer(),
            'BloodPressure': Integer(),
            'SkinThickness': Integer(),
            'Insulin': Integer(),
            'BMI': Float(),
            'DiabetesPedigreeFunction': Float(),
            'Age': Integer(),
            'Outcome': Integer(),
        },
    )
    with conexion.begin() as c:
        c.execute(text(f"ALTER TABLE `{tabla}` ADD PRIMARY KEY (Id)"))

    print(f"Listo: {len(df)} filas volcadas a {nombre_bd}.{tabla} "
          f"({(df['Outcome'] == 1).sum()} con diabetes, {(df['Outcome'] == 0).sum()} sin diabetes)")


if __name__ == "__main__":
    volcar_csv()
