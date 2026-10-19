import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# Lee el archivo .env de la raiz del proyecto (no pisa variables ya definidas)
load_dotenv(Path(__file__).parent.parent / '.env')


def _url(con_base_de_datos=True):
    # Los valores salen del .env o de variables de entorno, sin editar el codigo
    return URL.create(
        drivername='mysql+mysqlconnector',
        username=os.getenv('DIABETES_DB_USER'),
        password=os.getenv('DIABETES_DB_PASSWORD'),
        host=os.getenv('DIABETES_DB_HOST', 'localhost'),
        database=os.getenv('DIABETES_DB_NAME', 'diabetesdataset') if con_base_de_datos else None,
    )


def obtener_conexion():
    return create_engine(_url())


def obtener_conexion_servidor():
    """Conexion al servidor sin elegir base de datos (para poder crearla)."""
    return create_engine(_url(con_base_de_datos=False))
