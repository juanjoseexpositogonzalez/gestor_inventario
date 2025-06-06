import os
import sqlite3
from typing import Final

from inventory.schemas import (
    CATEGORIAS_PREDEFINIDAS,
    SQL_CREATE_TABLE_CATEGORIES,
    SQL_CREATE_TABLE_PRODUCTS
)

BASE_DIR: Final[str] = os.path.dirname(__file__)
DB_DIR: Final[str] = "data"
DB_FILENAME: Final[str] = "inventario.db"
DB_PATH: Final[str] = os.path.join(BASE_DIR, "..", DB_DIR, DB_FILENAME)


def get_connection() -> sqlite3.Connection:
    """
    Retorna una conexión a la base de datos SQLite en data/inventario.db.
    Si la carpeta 'data/' no existe, la crea antes de conectar.
    """
    # Construimos la ruta absoluta a la carpeta data/
    data_dir_path = os.path.join(BASE_DIR, "..", DB_DIR)

    # Si la carpeta no existe, la creamos (inkluyendo subdirectorios necesarios)
    if not os.path.exists(data_dir_path):
        os.makedirs(data_dir_path)

    # Conectamos al archivo inventario.db (se crea si no existía)
    conn = sqlite3.connect(DB_PATH)
    # Configuramos row_factory para poder acceder a columnas por nombre
    conn.row_factory = sqlite3.Row
    return conn

def _initialize_database() -> None:
    """
    Crea las tablas en la base de datos y rellena las categorías
    predefinidas. Solo debe ejecutarse una vez por arranque.
    """
    # Sentencia para insertar categorías sin duplicar (si ya existían, IGNORE)
    categorias_insert: str = "INSERT OR IGNORE INTO categories(name) VALUES (?);"

    # Abrimos conexión (get_connection ya se encarga de crear la carpeta data/ si no existe)
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            # 1. Crear tabla de categories
            cursor.execute(SQL_CREATE_TABLE_CATEGORIES)
            # 2. Crear tabla de products
            cursor.execute(SQL_CREATE_TABLE_PRODUCTS)
            # 3. Insertar cada categoría de la lista (sin duplicados)
            for nombre in CATEGORIAS_PREDEFINIDAS:
                cursor.execute(categorias_insert, (nombre,))
    except Exception as e:
        # Opcional: si quieres personalizar el mensaje de error
        raise RuntimeError(f"Error al inicializar la base de datos: {e}") from e
    finally:
        # Nos aseguramos de cerrar siempre la conexión
        conn.close()
            


try:
    _initialize_database()
except Exception as e:
    raise