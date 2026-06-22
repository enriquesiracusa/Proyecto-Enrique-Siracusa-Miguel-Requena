# Archivo: src/controllers/venta.py
# Funcionalidad: Orquestación transaccional y validaciones comerciales de cada venta individual.
# Integrantes: Enrique Siracusa y Miguel Requena

from src.models.producto import Producto
from src.models.tarjeta import Tarjeta

class Venta:
    """
    Gestiona la compra de un producto con una tarjeta.
    """
    
    def __init__(self, producto: Producto, tarjeta: Tarjeta, monto: float) -> None:
        """
        Inicializa una venta con el producto, la tarjeta y el monto.
        """
        self.producto: Producto = producto
        self.tarjeta: Tarjeta = tarjeta
        self.monto: float = monto

    def confirmar(self) -> bool:
        """
        Valida que haya stock del producto y saldo suficiente en la tarjeta.
        """
        if not self.producto.hay_stock():
            print(f"\n[TRANSACCIÓN RECHAZADA] El producto '{self.producto.nombre}' está agotado.")
            return False
            
        if not self.tarjeta.tiene_saldo(self.monto):
            print(f"\n[TRANSACCIÓN RECHAZADA] Fondos insuficientes. Saldo actual: ${self.tarjeta.saldo:.2f} | Requerido: ${self.monto:.2f}")
            return False
            
        return True

    def ejecutar(self) -> None:
        """
        Realiza el cobro de la tarjeta y descuenta el stock del producto.
        """
        self.producto.descontar(1)
        self.tarjeta.descontar(self.monto)

    def mensaje_dispensado(self) -> str:
        """
        Retorna el mensaje de despedida del producto comprado.
        """
        return self.producto.despedida
