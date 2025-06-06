
# Inventario de Productos con SQLite

Este proyecto implementa un sistema de inventario de productos en Python, utilizando SQLite para la persistencia de datos. Permite gestionar categorías predefinidas, añadir, buscar, actualizar y eliminar productos, y consultar el número de productos por categoría. Incluye además un conjunto completo de tests con pytest y un script para poblar la base de datos con 1000 productos de ejemplo.

---

## 1. Descripción

Sistema CRUD con persistencia en SQLite, gestión de categorías y productos. Pensado para ser modular y reutilizable en otros proyectos o ampliaciones futuras.

---

## 2. Requisitos

- Python 3.10+
- uv (recomendado para entornos virtuales)
- pytest (para ejecutar los tests)

---

## 3. Instalación

Este proyecto usa [`uv`](https://github.com/astral-sh/uv) como gestor de entornos y dependencias.

1. Crea el entorno virtual:

   ```bash
   uv venv
   uv pip install .
```

---

## 4. Estructura de ficheros

```
gestor_inventario/
├── inventory/
│   ├── db.py
│   ├── crud.py
│   ├── schemas.py
├── tests/
│   ├── test_crud.py
├── data/
│   └── inventario.db
├── populate_db.py
├── requirements.txt
├── README.md
```

---

## 5. Inicialización de la base de datos

La base de datos SQLite se crea automáticamente al importar cualquier función del paquete `inventory`. Se almacenará en `data/inventario.db`. Las tablas `categories` y `products` se crean si no existen, y se insertan las categorías predefinidas (`alimentación`, `bebidas`, `electrónica`, `papelería`, `otros`).

---

## 6. Uso del módulo CRUD

### `add_product(category, name, price) -> str`

Inserta un nuevo producto en la base de datos. Si la categoría no está en las predefinidas, se asigna "otros".

### `delete_product(product_id) -> bool`

Elimina un producto según su ID. Devuelve `True` si lo elimina correctamente, `False` si no se encontró.

### `search_product(name) -> List[Dict[str, object]]`

Busca productos cuyo nombre contenga el texto proporcionado (búsqueda parcial).

### `search_category(category) -> List[Dict[str, object]]`

Devuelve los productos de una categoría específica. Si la categoría no existe o no tiene productos, devuelve una lista vacía.

### `get_categories() -> Dict[str, int]`

Devuelve un diccionario con las categorías como claves y el número de productos por cada una.

### `update_product(product_id, category=None, name=None, price=None) -> bool`

Actualiza los campos especificados de un producto. Si todos los campos son `None`, devuelve `False`.

---

## 7. Ejecutar tests

Los tests se encuentran en `tests/test_crud.py`. Ejecuta:

```bash
pytest
```

El sistema utiliza una base de datos temporal para cada test mediante monkeypatching, por lo que no afecta a `inventario.db`.

---

## 8. Script para poblar la base con 1000 productos

Ejecuta:

```bash
uv run populate_db.py
```

Esto poblará `data/inventario.db` con 1000 productos distribuidos entre las categorías predefinidas.

---

## 9. Ejemplos de uso en línea de comandos

```python
from inventory.crud import add_product, search_product

pid = add_product("bebidas", "Coca-Cola", 1.20)
print(search_product("Coca"))
```

También puedes crear un script CLI como `main.py` con opciones de menú para añadir, buscar, actualizar y borrar productos.

---

## 10. Contribuciones

Las contribuciones están abiertas. Puedes enviar PRs o sugerencias directamente vía GitHub. Se agradece añadir tests para nuevas funcionalidades.

---

## 11. Licencia

MIT © 2025 Juanjo Expósito.
