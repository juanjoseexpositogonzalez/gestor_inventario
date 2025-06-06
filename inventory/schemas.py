from typing import List

CATEGORIAS_PREDEFINIDAS: List[str] = [
    "alimentación",
    "bebidas",
    "electrónica",
    "papelería",
    "otros"
]


SQL_CREATE_TABLE_CATEGORIES: str = """
CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);
"""

SQL_CREATE_TABLE_PRODUCTS: str = """
CREATE TABLE IF NOT EXISTS products (
    id          TEXT PRIMARY KEY,
    category_id INTEGER NOT NULL,
    name        TEXT NOT NULL,
    price       REAL NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
"""

# Obtener el id de una categoría dado su nombre
SQL_SELECT_CATEGORY_ID = """
SELECT id
  FROM categories
 WHERE name = ?;
"""

# Insertar un nuevo producto
SQL_INSERT_PRODUCT_IN_DB = """
INSERT INTO products (
    id,
    category_id,
    name,
    price
) VALUES (?, ?, ?, ?);
"""

# Borrar un producto por su id
SQL_DELETE_PRODUCT_IN_DB = """
DELETE FROM products
 WHERE id = ?;
"""

# Buscar productos cuyo nombre contenga cierto texto
SQL_SEARCH_PRODUCTS_BY_NAME = """
SELECT
    p.id       AS product_id,
    c.name     AS category,
    p.name     AS name,
    p.price    AS price
  FROM products p
  JOIN categories c
    ON p.category_id = c.id
 WHERE p.name LIKE '%' || ? || '%';
"""

# Buscar productos que pertenezcan a una categoría (por nombre de categoría)
SQL_SEARCH_PRODUCTS_BY_CATEGORY = """
SELECT
    p.id    AS product_id,
    p.name  AS name,
    p.price AS price
  FROM products p
  JOIN categories c
    ON p.category_id = c.id
 WHERE c.name = ?;
"""

# Obtener todas las categorías con su recuento de productos
SQL_SELECT_ALL_CATEGORIES_COUNT = """
SELECT
    c.name  AS category,
    COUNT(p.id) AS total
  FROM categories c
  LEFT JOIN products p
    ON p.category_id = c.id
 GROUP BY c.name;
"""
