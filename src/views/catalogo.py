# Archivo: src/views/catalogo.py
# Funcionalidad: Representación en matriz visual del catálogo de productos y búsqueda por coordenadas/código.
# Integrantes: Enrique Siracusa y Miguel Requena

from typing import List, Optional
from src.models.producto import Producto
from src.utils.gestor_archivos import GestorArchivos

class Catalogo:
    """
    Gestiona los productos en venta de la máquina expendedora.
    """
    
    def __init__(self, productos: List[Producto]) -> None:
        """
        Inicializa el catálogo con una lista de productos.
        """
        self.productos: List[Producto] = productos

    def cargar(self, gestor: GestorArchivos) -> None:
        """
        Carga la lista de productos utilizando el gestor de archivos.
        """
        self.productos = []
        productos_base = gestor.cargar_productos_json()
        
        if not gestor.existe_estado():
            columnas = [chr(c) for c in range(ord('A'), ord('Z') + 1)]
            filas = [1, 2, 3, 4, 5, 6]
            
            idx = 0
            for col in columnas:
                for fila in filas:
                    if idx >= len(productos_base):
                        break
                    
                    p_json = productos_base[idx]
                    nuevo_producto = Producto(
                        cod=p_json["cod"],
                        nombre=p_json["prod"],
                        precio=float(p_json["precio"]),
                        despedida=p_json["despedida"],
                        coordenada=f"{col}{fila}",
                        stock=10
                    )
                    self.agregar_producto(nuevo_producto)
                    idx += 1
        else:
            estado = gestor.cargar_estado()
            productos_estado = estado.get("productos", [])
            mapa_estado = {p["cod"]: p for p in productos_estado}
            
            coordenadas_ocupadas = {p["coordenada"] for p in productos_estado if p.get("coordenada") and p["coordenada"] != "--"}
            
            columnas = [chr(c) for c in range(ord('A'), ord('Z') + 1)]
            filas = [1, 2, 3, 4, 5, 6]
            
            for idx, p_json in enumerate(productos_base):
                cod = p_json["cod"]
                info_estado = mapa_estado.get(cod)
                
                if info_estado:
                    coord = info_estado["coordenada"]
                    stock = info_estado["stock"]
                else:
                    coord = "--"
                    stock = 0
                
                if coord == "--":
                    limit = len(columnas) * len(filas)
                    if idx < limit:
                        col_idx = idx // len(filas)
                        fila_idx = idx % len(filas)
                        coord_defecto = f"{columnas[col_idx]}{filas[fila_idx]}"
                        
                        if coord_defecto not in coordenadas_ocupadas:
                            coord = coord_defecto
                            coordenadas_ocupadas.add(coord)
                    
                nuevo_producto = Producto(
                    cod=cod,
                    nombre=p_json["prod"],
                    precio=float(p_json["precio"]),
                    despedida=p_json["despedida"],
                    coordenada=coord,
                    stock=stock
                )
                self.agregar_producto(nuevo_producto)

    def mostrar_matriz(self) -> None:
        """
        Dibuja el catálogo en forma de matriz en la consola.
        """
        letras_columnas = self.columnas_usadas()
        numeros_filas = self.filas_usadas()
        
        if not letras_columnas or not numeros_filas:
            print("\n[Catálogo Vacío] No hay dimensiones ni productos para generar la matriz.\n")
            return

        mapa_coordenadas = {p.coordenada: p for p in self.productos}
        
        ANCHO_CELDA = 7 
        
        linea_letras = "    "  
        for letra in letras_columnas:
            linea_letras += f"{letra}".ljust(ANCHO_CELDA)
        print(linea_letras)
        
        for num in numeros_filas:
            linea_fila = f"{num}   "
            
            for letra in letras_columnas:
                coord = f"{letra}{num}"
                p = mapa_coordenadas.get(coord)
                
                if p and p.hay_stock() and p.cod:
                    codigo_limpio = p.cod[:5].ljust(5)
                else:
                    codigo_limpio = "     "
                
                linea_fila += f"{codigo_limpio}".ljust(ANCHO_CELDA)
                
            print(linea_fila.rstrip())
        print()

    def buscar_por_codigo(self, cod: str) -> Optional[Producto]:
        """
        Busca un producto por su código identificador.
        """
        for p in self.productos:
            if p.cod == cod:
                return p
        return None

    def buscar_por_coordenada(self, coord: str) -> Optional[Producto]:
        """
        Busca un producto usando su coordenada.
        """
        coord_normalizada = coord.strip().upper()
        for p in self.productos:
            if p.coordenada == coord_normalizada:
                return p
        return None

    def agregar_producto(self, p: Producto) -> None:
        """
        Agrega un producto al catálogo.
        """
        self.productos.append(p)

    def columnas_usadas(self) -> List[str]:
        """
        Obtiene la lista ordenada de letras de columnas en uso.
        """
        letras = {p.coordenada[0] for p in self.productos if len(p.coordenada) >= 2 and p.coordenada != "--"}
        max_char = 'H'
        for letra in letras:
            if letra.isalpha() and letra.isupper() and letra > max_char:
                max_char = letra
        return [chr(c) for c in range(ord('A'), ord(max_char) + 1)]

    def filas_usadas(self) -> List[int]:
        """
        Obtiene la lista ordenada de números de filas en uso.
        """
        filas = set()
        for p in self.productos:
            if len(p.coordenada) >= 2 and p.coordenada != "--":
                try:
                    filas.add(int(p.coordenada[1:]))
                except ValueError:
                    continue
        max_fila = 6
        for f in filas:
            if f > max_fila:
                max_fila = f
        return list(range(1, max_fila + 1))
