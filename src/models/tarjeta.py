# Archivo: src/models/tarjeta.py
# Funcionalidad: Definición del modelo de datos de Tarjeta de clientes y validación/descuento de saldo.
# Integrantes: Enrique Siracusa y Miguel Requena

class Tarjeta:
    """
    Representa una tarjeta de cliente para realizar pagos.
    """
    
    def __init__(self, hash_id: int, saldo: float) -> None:
        """
        Inicializa una tarjeta con su identificador y saldo.
        """
        self.hash_id: int = hash_id
        self.saldo: float = saldo

    def tiene_saldo(self, monto: float) -> bool:
        """
        Verifica si la tarjeta cuenta con saldo suficiente.
        """
        return self.saldo >= monto

    def descontar(self, monto: float) -> None:
        """
        Disminuye el saldo disponible de la tarjeta.
        """
        if self.tiene_saldo(monto):
            self.saldo -= monto
        else:
            self.saldo = 0.0
