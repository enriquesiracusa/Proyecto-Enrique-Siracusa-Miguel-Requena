# Archivo: src/controllers/administrador.py
# Funcionalidad: Controlador que gestiona el menú de administración, reabastecimiento y edición de productos.
# Integrantes: Enrique Siracusa y Miguel Requena

import os
from typing import List
from src.models.tarjeta import Tarjeta
from src.models.producto import Producto
from src.views.catalogo import Catalogo
from src.utils.gestor_archivos import GestorArchivos
from src.utils.lector_entradas import (
    leer_entero,
    leer_decimal,
    leer_codigo_producto,
    leer_coordenada_nueva
)

class ControladorAdministrador:
    """
    Gestiona el menú de administración y reabastecimiento.
    """
    def __init__(self, catalogo: Catalogo, tarjetas: List[Tarjeta], gestor: GestorArchivos) -> None:
        self.catalogo: Catalogo = catalogo
        self.tarjetas: List[Tarjeta] = tarjetas
        self.gestor: GestorArchivos = gestor

    def iniciar_restock(self) -> None:
        """
        Inicia el proceso de autenticación y abre el menú principal de administración.
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "*" * 40)
        print("      MÓDULO DE ADMINISTRACIÓN (RESTOCK)   ")
        print("*" * 40)
        while True:
            clave = input(" -> Ingrese la clave de administrador (o presione Enter para volver): ").strip()
            if not clave:
                return
            if clave == "admin123":
                break
            print("[Error] Clave incorrecta. Intente de nuevo.\n")
            
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.catalogo.mostrar_matriz()
            print("[Acceso Concedido] 1. Reabastecer o agregar producto | 2. Cambiar Producto")
            opcion = input("Seleccione una opción (o presione Enter para volver): ").strip()
            if not opcion:
                return
            
            if opcion == "1":
                self._menu_reabastecer_o_agregar()
            elif opcion == "2":
                self._menu_cambiar_producto()
            else:
                print("[Error] Opción inválida. Debe ser 1 o 2. Intente de nuevo.\n")
                input("Presione Enter para continuar...")

    def _menu_cambiar_producto(self) -> None:
        """
        Muestra las opciones para modificar los datos de un producto.
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n[Catálogo Actual]")
        self.catalogo.mostrar_matriz()
        while True:
            criterio = input(" -> Ingrese la coordenada del producto a cambiar (Ej: A1) o presione Enter para volver: ").strip().upper()
            if not criterio:
                return
            producto = self.catalogo.buscar_por_coordenada(criterio)
            if producto:
                break
            print(f"[Error] No se encontró ningún producto en la coordenada '{criterio}'. Intente de nuevo.\n")
            
        nuevo_cod = leer_codigo_producto(f" -> Nuevo código (actual: {producto.cod}): ", self.catalogo, producto)
        if nuevo_cod is None:
            nuevo_cod = producto.cod

        nuevo_nom = input(f" -> Nuevo nombre (actual: {producto.nombre}): ").strip()
        nuevo_precio = leer_decimal(f" -> Nuevo precio (actual: ${producto.precio:.2f}): ", min_val=0.0, default=producto.precio)
        nuevo_stock = leer_entero(f" -> Nuevo stock (actual: {producto.stock}): ", min_val=0, default=producto.stock)
        nueva_despedida = input(f" -> Nuevo mensaje de despedida (actual: {producto.despedida}): ").strip()
        
        if nuevo_cod:
            producto.cod = nuevo_cod
        if nuevo_nom:
            producto.nombre = nuevo_nom
        producto.precio = nuevo_precio
        producto.stock = nuevo_stock
        if nueva_despedida:
            producto.despedida = nueva_despedida
            
        print(f"[Éxito] Producto en '{criterio}' actualizado correctamente.\n")
        self.gestor.guardar_estado(self.catalogo, self.tarjetas)
        input("Presione Enter para continuar...")

    def _menu_reabastecer_o_agregar(self) -> None:
        """
        Muestra el menú para agregar un producto o reabastecer stock.
        """
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.catalogo.mostrar_matriz()
            print("\n[Reabastecer o agregar producto]")
            print(" 1. Reabastecer un producto existente")
            print(" 2. Habilitar nuevo carril de producto")
            sub_opcion = input("Seleccione una opción (o presione Enter para volver): ").strip()
            if not sub_opcion:
                return
            if sub_opcion in ("1", "2"):
                break
            print("[Error] Opción inválida. Debe ser 1 o 2. Intente de nuevo.\n")
            input("Presione Enter para continuar...")

        if sub_opcion == "2":
            print("\n--- HABILITAR NUEVO CARRIL DE PRODUCTO ---")
            coord = leer_coordenada_nueva(" -> Ingrese la coordenada para el nuevo producto (Ej: I1, A7, etc. para redimensionar) o presione Enter para volver: ", self.catalogo)
            if not coord:
                return
                
            cod = leer_codigo_producto(" -> Ingrese el código del nuevo producto (Ej: PepG1) o presione Enter para volver: ", self.catalogo)
            if not cod:
                return
                
            nom = input(" -> Ingrese el nombre del producto: ").strip()
            
            precio = leer_decimal(" -> Ingrese el precio (o presione Enter para volver): ", min_val=0.0)
            if precio is None:
                return
                
            stock = leer_entero(" -> Ingrese el stock inicial (o presione Enter para volver): ", min_val=0)
            if stock is None:
                return
                
            despedida = input(" -> Ingrese el mensaje de despedida: ").strip()
            
            nuevo_prod = Producto(cod=cod, nombre=nom, precio=precio, despedida=despedida, coordenada=coord, stock=stock)
            self.catalogo.agregar_producto(nuevo_prod)
            print(f"[Éxito] Producto '{nom}' registrado correctamente en '{coord}'. ¡La matriz se ha redimensionado!\n")
            self.gestor.guardar_estado(self.catalogo, self.tarjetas)
            input("Presione Enter para continuar...")
            return

        while True:
            criterio = input(" -> Ingrese la coordenada o código del producto a reabastecer o presione Enter para volver: ").strip().upper()
            if not criterio:
                return
            producto = self.catalogo.buscar_por_coordenada(criterio) or self.catalogo.buscar_por_codigo(criterio)
            if producto:
                break
            print(f"[Error] No se encontró ningún producto con la identificación '{criterio}'. Intente de nuevo.\n")

        col_validas = [chr(c) for c in range(ord('A'), ord('Z') + 1)]
        filas_validas = [1, 2, 3, 4, 5, 6]
        coord_actual = producto.coordenada
        coordenada_valida = (
            len(coord_actual) >= 2 
            and coord_actual[0] in col_validas 
            and coord_actual[1:].isdigit() 
            and int(coord_actual[1:]) in filas_validas
        )
        
        if not coordenada_valida:
            coordenadas_ocupadas = {p.coordenada for p in self.catalogo.productos if p.coordenada != "--"}
            nueva_coord = None
            for col in col_validas:
                for fila in filas_validas:
                    coord_posible = f"{col}{fila}"
                    if coord_posible not in coordenadas_ocupadas:
                        nueva_coord = coord_posible
                        break
                if nueva_coord:
                    break
            
            if nueva_coord:
                producto.coordenada = nueva_coord
                print(f"[Ajuste] El producto '{producto.nombre}' no tenía una coordenada válida. Se le asignó la posición '{nueva_coord}'.")
            else:
                print("[Error] La matriz está llena. No se puede asignar una coordenada válida al producto.\n")
                return
                
        print(f"[Encontrado] Producto: {producto.nombre} | Posición: {producto.coordenada} | Inventario actual: {producto.stock} unidades.")
        cantidad = leer_entero(" -> Ingrese la cantidad de unidades a añadir (o presione Enter para volver): ", min_val=1)
        if cantidad is None:
            return
                
        producto.aumentar(cantidad)
        print(f"[Éxito] Inventario actualizado. Nuevo stock de '{producto.nombre}': {producto.stock} unidades.\n")
        self.gestor.guardar_estado(self.catalogo, self.tarjetas)
        input("Presione Enter para continuar...")
