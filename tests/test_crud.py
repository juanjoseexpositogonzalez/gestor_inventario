import os
import sqlite3
import pytest

from inventory import db, crud  # Añadimos import de crud aquí
from inventory.schemas import CATEGORIAS_PREDEFINIDAS

# -------------------------------------------------------------------
# Fixture que hace que, en cada prueba, get_connection() use un fichero
# sqlite temporal en tmp_path, y vuelva a inicializar ese esquema limpio
# -------------------------------------------------------------------

@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    """
    Sustituye `inventory.db.get_connection` y `inventory.crud.get_connection`
    por una función que abre la BD en tmp_path/"test.db". Luego invoca
    db._initialize_database() para crear tablas y categorías.
    """
    # 1. Ruta al fichero temporal
    temp_db_path = tmp_path / "test.db"

    # 2. Definimos un get_connection alternativo que use ese fichero
    def get_test_connection():
        conn = sqlite3.connect(str(temp_db_path))
        conn.row_factory = sqlite3.Row
        return conn

    # 3. Monkey­patch: tanto db.get_connection como crud.get_connection
    #    deben apuntar al nuevo get_test_connection()
    monkeypatch.setattr(db,   "get_connection", get_test_connection)
    monkeypatch.setattr(crud, "get_connection", get_test_connection)

    # 4. Ejecutamos la inicialización del esquema sobre esa BD vacía
    db._initialize_database()

    yield

    # Al salir de la prueba, tmp_path y su contenido se eliminan automáticamente



# -----------------------
#  Tests para add_product
# -----------------------

def test_add_product_and_search(tmp_path):
    # Llamamos a add_product con una categoría válida
    pid = crud.add_product("bebidas", "Coca-Cola", 1.20)
    assert isinstance(pid, str) and len(pid) > 0

    # Debe aparecer en search_product
    resultados = crud.search_product("Coca-Cola")
    assert len(resultados) == 1

    producto = resultados[0]
    assert producto["product_id"] == pid
    assert producto["category"] == "bebidas"
    assert producto["name"] == "Coca-Cola"
    assert producto["price"] == 1.20

    # Si llamamos con una categoría no predefinida, asigna “otros”
    pid2 = crud.add_product("juguetes", "Muñeca", 9.99)
    assert isinstance(pid2, str) and pid2 != ""

    res2 = crud.search_product("Muñeca")
    assert len(res2) == 1
    assert res2[0]["category"] == "otros"


# --------------------------
#  Tests para delete_product
# --------------------------

def test_delete_existing_and_nonexistent(tmp_path):
    # Agregamos un producto para borrarlo
    pid = crud.add_product("electrónica", "Televisor", 299.99)

    # Debe borrarse correctamente
    borrado = crud.delete_product(pid)
    assert borrado is True

    # Tras borrarlo, ya no existe
    resultados = crud.search_product("Televisor")
    assert resultados == []

    # Intentar borrar de nuevo debe devolver False
    borrado2 = crud.delete_product(pid)
    assert borrado2 is False


# -----------------------------
#  Tests para search_product
# -----------------------------

def test_search_partial_and_case(tmp_path):
    # Insertamos varios productos
    crud.add_product("papelería", "Cuaderno A5", 2.50)
    crud.add_product("papelería", "Carpeta", 3.00)
    crud.add_product("bebidas", "Café Molido", 4.20)

    # Búsqueda parcial “C”
    resultados = crud.search_product("C")
    # Esperamos al menos 3 coincidencias (Cuaderno, Carpeta, Café)
    assert len(resultados) >= 3

    # Búsqueda de algo que no existe → lista vacía
    vacio = crud.search_product("InexistenteXYZ")
    assert vacio == []


# -------------------------------
#  Tests para search_category
# -------------------------------

def test_search_category_existing_and_empty(tmp_path):
    # Insertamos productos en distintas categorías
    crud.add_product("alimentación", "Pan", 1.00)
    crud.add_product("alimentación", "Leche", 0.80)
    crud.add_product("bebidas", "Agua Mineral", 0.50)

    # Buscar categoría "alimentación"
    lista_alim = crud.search_category("alimentación")
    assert isinstance(lista_alim, list)
    # Debe contener exactamente 2 productos
    assert len(lista_alim) == 2
    nombres_alim = {p["name"] for p in lista_alim}
    assert "Pan" in nombres_alim and "Leche" in nombres_alim

    # Buscar categoría que existe pero sin productos directos
    lista_elec = crud.search_category("electrónica")
    # Aún no insertamos nada en "electrónica", así que vacía
    assert lista_elec == []

    # Buscar categoría no predefinida → devolvemos []
    lista_no = crud.search_category("juguetes")
    assert lista_no == []


# -----------------------------
#  Tests para get_categories
# -----------------------------

def test_get_categories_counts(tmp_path):
    # Al inicializar, ninguna tiene productos → todos a 0
    cuenta_init = crud.get_categories()
    # Debe tener todas las predefinidas con valor 0
    for cat in CATEGORIAS_PREDEFINIDAS:
        assert cat in cuenta_init
        assert cuenta_init[cat] == 0

    # Insertamos productos en categorías variadas
    crud.add_product("alimentación", "Manzana", 0.50)
    crud.add_product("alimentación", "Banana", 0.60)
    crud.add_product("bebidas", "Zumo", 1.20)

    cuenta_despues = crud.get_categories()
    assert cuenta_despues["alimentación"] == 2
    assert cuenta_despues["bebidas"] == 1
    # Las demás deben seguir en 0, salvo "otros"
    for cat in CATEGORIAS_PREDEFINIDAS:
        if cat not in ("alimentación", "bebidas"):
            assert cuenta_despues[cat] == 0


# ----------------------------
#  Tests para update_product
# ----------------------------

def test_update_product_full_and_partial(tmp_path):
    # Insertamos un producto inicial
    pid = crud.add_product("papelería", "Lápiz", 0.30)

    # 1) Intentar actualizar con un product_id inexistente → False
    assert crud.update_product("id_no_valido", "bebidas", "Lápiz Borrable", 0.50) is False

    # 2) Actualizar sólo el nombre y el precio
    ok1 = crud.update_product(pid, None, "Lápiz Rojo", 0.40)
    assert ok1 is True
    res = crud.search_product("Lápiz Rojo")
    assert len(res) == 1
    assert res[0]["price"] == 0.40
    # Categoría no debería haber cambiado (seguirá en papelería)
    assert res[0]["category"] == "papelería"

    # 3) Actualizar sólo la categoría a “bebidas”
    ok2 = crud.update_product(pid, "bebidas", None, None)
    assert ok2 is True
    res2 = crud.search_product("Lápiz Rojo")
    assert len(res2) == 1
    assert res2[0]["category"] == "bebidas"

    # 4) Actualizar con todos los campos a None → no hay nada que cambiar → False
    assert crud.update_product(pid, None, None, None) is False


# ----------------------------
#  Tests integrales combinados
# ----------------------------

def test_sequence_of_operations(tmp_path):
    """
    Test que encadena varias operaciones CRUD para simular un flujo real:
    1. Añadir producto
    2. Buscarlo
    3. Actualizarlo
    4. Buscar por categoría
    5. Borrarlo
    6. Comprobar categorías
    """
    # 1) Añadir
    pid = crud.add_product("electrónica", "Auriculares", 29.99)
    assert isinstance(pid, str)

    # 2) Buscarlo
    encontrados = crud.search_product("Auriculares")
    assert len(encontrados) == 1
    assert encontrados[0]["product_id"] == pid

    # 3) Actualizar nombre y precio
    assert crud.update_product(pid, None, "Auriculares Pro", 39.99) is True
    encontrados2 = crud.search_product("Pro")
    assert len(encontrados2) == 1
    assert encontrados2[0]["price"] == 39.99

    # 4) Buscar por categoría (debe regresar solo el mismo producto bajo “electrónica”)
    cat_list = crud.search_category("electrónica")
    assert len(cat_list) == 1
    assert cat_list[0]["name"] == "Auriculares Pro"

    # 5) Borrarlo
    assert crud.delete_product(pid) is True
    assert crud.search_product("Auriculares") == []

    # 6) Comprobar get_categories: “electrónica” ya debe contar 0
    cuentas = crud.get_categories()
    assert cuentas["electrónica"] == 0


# ---------------------------------------------------
#  Para verificar que no se rompe al agregar muchos
# ---------------------------------------------------

def test_bulk_insert_and_count(tmp_path):
    """
    Inserta 50 productos de prueba y comprueba que get_categories
    refleja el recuento correcto en cada una de las 5 categorías.
    """
    # Insertamos 50 productos, 10 en cada categoría
    for idx, cat in enumerate(CATEGORIAS_PREDEFINIDAS):
        for i in range(10):
            crud.add_product(cat, f"{cat.capitalize()} {i}", float(i + 0.5))

    cuentas = crud.get_categories()
    for cat in CATEGORIAS_PREDEFINIDAS:
        assert cuentas[cat] == 10

