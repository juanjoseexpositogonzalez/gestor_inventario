# main.py

import sys

from inventory.crud import (
    add_product,
    delete_product,
    search_product,
    search_category,
    get_categories,
    update_product
)

def menu():
    print("Inventario de Productos")
    print("=======================")
    print("1) Añadir producto")
    print("2) Borrar producto")
    print("3) Buscar producto por nombre")
    print("4) Buscar productos por categoría")
    print("5) Mostrar recuento de categorías")
    print("6) Actualizar producto")
    print("0) Salir")

def main():
    while True:
        menu()
        opción = input("Elige una opción: ").strip()
        if opción == "1":
            cat = input("Categoría: ")
            name = input("Nombre: ")
            price = float(input("Precio: "))
            pid = add_product(cat, name, price)
            print(f"Producto añadido con ID: {pid}")
        elif opción == "2":
            pid = input("ID de producto a borrar: ")
            if delete_product(pid):
                print("Producto borrado.")
            else:
                print("No se encontró el producto.")
        elif opción == "3":
            txt = input("Texto a buscar en nombre: ")
            res = search_product(txt)
            if res:
                for p in res:
                    print(f"{p['product_id']} | {p['category']} | {p['name']} | {p['price']}")
            else:
                print("No se encontraron coincidencias.")
        elif opción == "4":
            cat = input("Categoría a buscar: ")
            res = search_category(cat)
            if res:
                for p in res:
                    print(f"{p['product_id']} | {p['name']} | {p['price']}")
            else:
                print("No hay productos en esa categoría o la categoría no existe.")
        elif opción == "5":
            cuentas = get_categories()
            for cat, total in cuentas.items():
                print(f"{cat}: {total}")
        elif opción == "6":
            pid = input("ID del producto a actualizar: ")
            cat = input("Nueva categoría (enter para no cambiar): ").strip() or None
            name = input("Nuevo nombre (enter para no cambiar): ").strip() or None
            price_in = input("Nuevo precio (enter para no cambiar): ").strip()
            price = float(price_in) if price_in else None
            if update_product(pid, cat, name, price):
                print("Producto actualizado.")
            else:
                print("No se pudo actualizar (ID inválido o ningún cambio).")
        elif opción == "0":
            print("Saliendo...")
            sys.exit(0)
        else:
            print("Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    main()

