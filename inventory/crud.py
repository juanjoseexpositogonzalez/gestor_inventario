import uuid
from typing import List, Dict, Optional

from inventory.db import get_connection
from inventory.schemas import (
    CATEGORIAS_PREDEFINIDAS,
    SQL_SELECT_CATEGORY_ID,
    SQL_INSERT_PRODUCT_IN_DB,
    SQL_DELETE_PRODUCT_IN_DB,
    SQL_SEARCH_PRODUCTS_BY_NAME,
    SQL_SEARCH_PRODUCTS_BY_CATEGORY,
    SQL_SELECT_ALL_CATEGORIES_COUNT
)

def add_product(category: str, name: str, price: float) -> str:
    """
    Inserta un producto en la tabla 'products' con un id generado por uuid.
    Si la categoría no está en CATEGORIAS_PREDEFINIDAS, asigna "otros".

    Args:
        category (str): Categoría del producto.
        name (str): Nombre del producto.
        price (float): Precio del producto.

    Returns:
        str: El 'product_id' generado si se insertó correctamente.
             En caso de error, lanza RuntimeError.
    """
    # 1. Validar categoría; si no existe en la lista, usar "otros"
    if category not in CATEGORIAS_PREDEFINIDAS:
        category = "otros"

    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()

            # 2. Obtener el category_id correspondiente al nombre de categoría
            cursor.execute(SQL_SELECT_CATEGORY_ID, (category,))
            fila = cursor.fetchone()
            if fila:
                category_id = fila["id"]
            else:
                # Por seguridad: si no existe "otros", buscamos su id
                cursor.execute(SQL_SELECT_CATEGORY_ID, ("otros",))
                fila_otros = cursor.fetchone()
                if fila_otros:
                    category_id = fila_otros["id"]
                else:
                    # Esto no debería pasar, porque 'otros' se creó en la inicialización
                    raise RuntimeError(
                        f"La categoría 'otros' no existe en la base de datos."
                    )

            # 3. Generar el ID único para el producto
            product_id = str(uuid.uuid4())

            # 4. Insertar en la tabla 'products'
            cursor.execute(
                SQL_INSERT_PRODUCT_IN_DB,
                (product_id, category_id, name, price)
            )

        # Si llegamos aquí, el INSERT fue exitoso (se hizo commit en el with)
        return product_id

    except Exception as e:
        # Podemos relaizar rollback implícito (el 'with conn' ya hace rollback si hay excepción)
        raise RuntimeError(f"Error al insertar el producto en la base de datos: {e}") from e

    finally:
        # Nos aseguramos de cerrar la conexión
        conn.close()


def delete_product(product_id: str) -> bool:
    """
    Elimina un producto de la tabla 'products' dado su product_id.

    Args:
        product_id (str): ID del producto a borrar.

    Returns:
        bool: True si se eliminó exactamente un registro; False en caso contrario.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(SQL_DELETE_PRODUCT_IN_DB, (product_id,))

        if cursor.rowcount == 1:
            conn.commit()
            return True
        else:
            conn.rollback()
            return False

    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Error al borrar el producto en la base de datos: {e}") from e

    finally:
        conn.close()


def search_product(name: str) -> List[Dict[str, object]]:
    """
    Busca todos los productos cuyo nombre contenga la cadena 'name' (case-insensitive).

    Args:
        name (str): Fragmento o nombre completo del producto a buscar.

    Returns:
        List[Dict[str, object]]: Lista de diccionarios con las claves:
            - "product_id" (str)
            - "category"   (str)
            - "name"       (str)
            - "price"      (float)
        Si no hay coincidencias, devuelve lista vacía.
    """
    conn = get_connection()
    resultados: List[Dict[str, object]] = []

    try:
        cursor = conn.cursor()
        cursor.execute(SQL_SEARCH_PRODUCTS_BY_NAME, (name,))
        rows = cursor.fetchall()

        for row in rows:
            resultados.append({
                "product_id": row["product_id"],
                "category":   row["category"],
                "name":       row["name"],
                "price":      row["price"],
            })

        return resultados

    except Exception as e:
        raise RuntimeError(f"Error al buscar productos en la base de datos: {e}") from e

    finally:
        conn.close()


def search_category(category: str) -> List[Dict[str, object]]:
    """
    Devuelve todos los productos que pertenecen a la categoría exacta 'category'.

    Args:
        category (str): Nombre de la categoría a buscar.

    Returns:
        List[Dict[str, object]]: Lista de diccionarios con las claves:
            - "product_id" (str)
            - "category"   (str) – siempre igual al parámetro 'category'
            - "name"       (str)
            - "price"      (float)
        Si la categoría no existe o no tiene productos, devuelve lista vacía.
    """
    conn = get_connection()
    resultados: List[Dict[str, object]] = []

    try:
        cursor = conn.cursor()

        # COMPROBAR QUE LA CATEGORÍA EXISTE
        if category not in CATEGORIAS_PREDEFINIDAS:
            # Si no existe, devolvemos lista vacía
            return []

        cursor.execute(SQL_SEARCH_PRODUCTS_BY_CATEGORY, (category,))
        rows = cursor.fetchall()

        for row in rows:
            resultados.append({
                "product_id": row["product_id"],
                "category":   category,
                "name":       row["name"],
                "price":      row["price"],
            })

        return resultados

    except Exception as e:
        raise RuntimeError(f"Error al buscar productos por categoría: {e}") from e

    finally:
        conn.close()


def get_categories() -> Dict[str, int]:
    """
    Obtiene todas las categorías junto con el número de productos que tienen.

    Returns:
        Dict[str, int]: Diccionario donde:
            - La clave es el nombre de la categoría (str).
            - El valor es el entero (int) de productos en esa categoría.
    """
    conn = get_connection()
    resultado: Dict[str, int] = {}

    try:
        cursor = conn.cursor()
        cursor.execute(SQL_SELECT_ALL_CATEGORIES_COUNT)
        rows = cursor.fetchall()

        for row in rows:
            resultado[row["category"]] = row["total"]

        return resultado

    except Exception as e:
        raise RuntimeError(f"Error al obtener categorías: {e}") from e

    finally:
        conn.close()


def update_product(
    product_id: str,
    category: Optional[str],
    name: Optional[str],
    price: Optional[float]
) -> bool:
    """
    Actualiza los campos de un producto dado su 'product_id'. 
    Solo modifica aquellos parámetros que no sean None.

    Args:
        product_id (str): ID del producto a actualizar.
        category   (Optional[str]): Nueva categoría. Si no está en predefinidas, se usa "otros". 
                                    Si es None, no se cambia.
        name       (Optional[str]): Nuevo nombre. Si es None, no se cambia.
        price      (Optional[float]): Nuevo precio. Si es None, no se cambia.

    Returns:
        bool: True si se actualizó exactamente un registro, False en otro caso.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # 1. Verificar que exista el producto
        cursor.execute("SELECT 1 FROM products WHERE id = ?;", (product_id,))
        if cursor.fetchone() is None:
            # No hay ningún producto con ese id
            return False

        # 2. Preparar la lista de campos a actualizar
        campos_a_actualizar: List[str] = []
        valores: List[object] = []

        # 2.1. Si 'category' no es None, obtenemos su category_id
        if category is not None:
            if category not in CATEGORIAS_PREDEFINIDAS:
                category = "otros"

            # Buscamos el id numérico de la categoría
            cursor.execute(SQL_SELECT_CATEGORY_ID, (category,))
            fila_cat = cursor.fetchone()
            if fila_cat:
                cat_id = fila_cat["id"]
            else:
                # Por seguridad, nos aseguramos de usar el id de "otros"
                cursor.execute(SQL_SELECT_CATEGORY_ID, ("otros",))
                fila_otros = cursor.fetchone()
                if fila_otros:
                    cat_id = fila_otros["id"]
                else:
                    raise RuntimeError("La categoría 'otros' no está en la base de datos.")

            campos_a_actualizar.append("category_id = ?")
            valores.append(cat_id)

        # 2.2. Si 'name' no es None, agregamos al SET
        if name is not None:
            campos_a_actualizar.append("name = ?")
            valores.append(name)

        # 2.3. Si 'price' no es None, agregamos al SET
        if price is not None:
            campos_a_actualizar.append("price = ?")
            valores.append(price)

        # 2.4. Si no hay nada que actualizar, salimos
        if not campos_a_actualizar:
            return False

        # 3. Construir la cláusula SET de manera dinámica
        set_clause = ", ".join(campos_a_actualizar)

        sql_update = f"""
        UPDATE products
           SET {set_clause}
         WHERE id = ?;
        """
        valores.append(product_id)

        # 4. Ejecutar el UPDATE
        cursor.execute(sql_update, tuple(valores))

        # 5. Comprobar cuántas filas afectó
        if cursor.rowcount == 1:
            conn.commit()
            return True
        else:
            conn.rollback()
            return False

    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Error al actualizar el producto: {e}") from e

    finally:
        conn.close()