# Archivo: src/models/producto.py
# Funcionalidad: Definición del modelo de datos de un Producto y gestión de sus atributos y stock.
# Integrantes: Enrique Siracusa y Miguel Requena

class Producto:
    """
    Representa un producto dentro de la máquina expendedora.
    """
    
    def __init__(self, cod: str, nombre: str, precio: float, despedida: str, coordenada: str, stock: int) -> None:
        """
        Inicializa un nuevo producto.
        """
        self.cod: str = cod
        self.nombre: str = nombre
        self.precio: float = precio
        self.despedida: str = despedida
        self.coordenada: str = coordenada
        self.stock: int = stock
 
    def hay_stock(self) -> bool:
        """
        Verifica si el producto tiene stock disponible.
        """
        return self.stock > 0
 
    def descontar(self, cantidad: int) -> None:
        """
        Disminuye la cantidad de stock disponible del producto.
        """
        self.stock -= cantidad
        if self.stock < 0:
            self.stock = 0
 
    def aumentar(self, cantidad: int) -> None:
        """
        Incrementa la cantidad de stock disponible del producto.
        """
        self.stock += cantidad
