# Inventario de Productos con SQLite

Este proyecto implementa un sistema de inventario de productos en Python, utilizando SQLite para la persistencia de datos. Permite gestionar categorías predefinidas, añadir, buscar, actualizar y eliminar productos, y consultar el número de productos por categoría. Incluye además un conjunto completo de tests con pytest y un script para poblar la base de datos con 1000 productos de ejemplo.

---

## Tabla de Contenidos

1. [Descripción](#descripción)  
2. [Requisitos](#requisitos)  
3. [Instalación](#instalación)  
4. [Estructura de ficheros](#estructura-de-ficheros)  
5. [Inicialización de la base de datos](#inicialización-de-la-base-de-datos)  
6. [Uso del módulo CRUD](#uso-del-módulo-crud)  
   - [add_product](#add_product)  
   - [delete_product](#delete_product)  
   - [search_product](#search_product)  
   - [search_category](#search_category)  
   - [get_categories](#get_categories)  
   - [update_product](#update_product)  
7. [Ejecutar tests](#ejecutar-tests)  
8. [Script para poblar la base con 1000 productos](#script-para-poblar-la-base-con-1000-productos)  
9. [Ejemplos de uso en línea de comandos](#ejemplos-de-uso-en-línea-de-comandos)  
10. [Contribuciones](#contribuciones)  
11. [Licencia](#licencia)  

---

## Descripción

Este proyecto ofrece un paquete Python llamado `inventory` que gestiona un inventario de productos. Cada producto tiene:

- **ID** (UUID generado automáticamente).  
- **Categoría** (una de las predefinidas: `alimentación`, `bebidas`, `electrónica`, `papelería`, `otros`).  
- **Nombre** (texto).  
- **Precio** (número real).

Las operaciones disponibles son:

1. **add_product(category, name, price) → product_id**  
2. **delete_product(product_id) → bool**  
3. **search_product(name) → List[Dict]**  
4. **search_category(category) → List[Dict]**  
5. **get_categories() → Dict[str, int]**  
6. **update_product(product_id, category?, name?, price?) → bool**

La persistencia se realiza en un fichero SQLite (`data/inventario.db`). Al importar el módulo `inventory.db`, se crean automáticamente las tablas (`categories` y `products`) y se insertan las categorías predefinidas si no existían.

---

## Requisitos

- **Python 3.8+**  
- Paquetes de la biblioteca estándar:
  - `sqlite3`  
  - `os`, `uuid`, `typing`  
- **pytest** (solo para ejecutar los tests).

Para instalar `pytest`, puedes usar:

```bash
pip install pytest
```

---

## Instalación

1. Clona este repositorio en tu máquina local:

   ```bash
   git clone https://github.com/tu_usuario/mi_inventario.git
   cd mi_inventario
   ```

2. (Opcional) Crea y activa un entorno virtual:

   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux / macOS:
   source venv/bin/activate
   ```

3. Instala pytest para ejecutar los tests:

   ```bash
   pip install pytest
   ```

4. (Opcional) Añade otras dependencias al `requirements.txt` (si tuvieras librerías externas).

---

## Estructura de ficheros

```
mi_inventario/
├── data/
│   └── inventario.db        # Fichero SQLite (se crea automáticamente)
│
├── inventory/               # Paquete principal
│   ├── __init__.py
│   ├── db.py                # Conexión e inicialización de la BD
│   ├── schemas.py           # Definición de categorías y sentencias CREATE TABLE
│   └── crud.py              # Funciones add, delete, search, update, get_categories
│
├── tests/                   # Tests automatizados con pytest
│   └── test_crud.py
│
├── populate_db.py           # Script para “popular” la base con 1000 productos
├── main.py                  # (Opcional) Ejemplo de uso / CLI básica
├── pytest.ini               # Configuración de pytest (filterwarnings)
├── README.md                # Este archivo
└── requirements.txt         # Lista de dependencias (pytest)
```

- **`data/inventario.db`**  
  Fichero SQLite donde residen las tablas `categories` y `products`. Se crea en la primera ejecución de cualquier función de `inventory`.

- **`inventory/db.py`**  
  - Define las rutas (`BASE_DIR`, `DB_DIR`, `DB_PATH`).  
  - Función `get_connection()` que crea la carpeta `data/` si no existe y retorna un `sqlite3.Connection`.  
  - Función privada `_initialize_database()` que:
    1. Ejecuta `CREATE TABLE IF NOT EXISTS` de `categories` y `products`.  
    2. Inserta (con `INSERT OR IGNORE`) todas las categorías predefinidas (`CATEGORIAS_PREDEFINIDAS`).  
  - Al final del archivo, se invoca `_initialize_database()` al importar el módulo.

- **`inventory/schemas.py`**  
  - Lista `CATEGORIAS_PREDEFINIDAS = ["alimentación", "bebidas", "electrónica", "papelería", "otros"]`.  
  - Constantes `SQL_CREATE_TABLE_CATEGORIES` y `SQL_CREATE_TABLE_PRODUCTS` con las instrucciones SQL para crear las tablas.

- **`inventory/crud.py`**  
  Implementa las funciones CRUD:
  1. `add_product(category, name, price) → str`  
  2. `delete_product(product_id) → bool`  
  3. `search_product(name) → List[Dict[str, object]]`  
  4. `search_category(category) → List[Dict[str, object]]`  
  5. `get_categories() → Dict[str, int]`  
  6. `update_product(product_id, category?, name?, price?) → bool`

- **`tests/test_crud.py`**  
  - Fixture `use_temp_db` que parchea `get_connection()` tanto en `db` como en `crud` para que cada test use una base en memoria (fichero temporal).  
  - Pruebas unitarias para cada función CRUD y tests de flujo integral y bulk insert.

- **`populate_db.py`**  
  - Script que elimina la base existente (`data/inventario.db`), la inicializa nuevamente y agrega 1000 productos de ejemplo distribuídos uniformemente entre las categorías predefinidas.

- **`main.py`** (opcional)  
  - Un posible script de demostración o CLI que importe las funciones de `inventory.crud` y permita interacción básica desde consola.

- **`pytest.ini`**  
  Configura pytest para filtrar los `DeprecationWarning` de `pytest_freezegun`:
  ```ini
  [pytest]
  filterwarnings =
      ignore::DeprecationWarning:pytest_freezegun
  ```

