import os
import random

from inventory.db import DB_PATH, _initialize_database
from inventory.crud import add_product
from inventory.schemas import CATEGORIAS_PREDEFINIDAS
from inventory.db import get_connection

def clean_products_table():
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM products;")
    conn.close()

def populate_database():
    """
    Elimina el fichero de base actual (si existe), vuelve a inicializar
    el esquema (tablas y categorías), y agrega 1000 productos de prueba
    repartidos equitativamente entre las categorías predefinidas.
    """
    # 1. Evita borrar el archivo si ya existe
    clean_products_table()

    # 2. Reconstruir la base de datos (crea tablas e inserta categorías)
    _initialize_database()

    # 3. Generar 1000 productos de prueba
    total = 1000
    num_cats = len(CATEGORIAS_PREDEFINIDAS)
    for i in range(total):
        # Elegir la categoría en ciclo (0,1,2,...)
        categoria = CATEGORIAS_PREDEFINIDAS[i % num_cats]
        # Construir un nombre identificable
        nombre = f"{categoria.capitalize()}_Producto_{i}"
        # Precio aleatorio entre 1.0 y 100.0, con dos decimales
        precio = round(random.uniform(1.0, 100.0), 2)
        # Insertar en la base
        add_product(categoria, nombre, precio)

    print(f"Base de datos poblada con {total} productos.")


if __name__ == "__main__":
    populate_database()
