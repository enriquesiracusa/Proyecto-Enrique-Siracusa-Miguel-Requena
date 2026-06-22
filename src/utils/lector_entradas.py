# ---------------------------------------------------------------------------
# Archivo: src/utils/lector_entradas.py
# Funcionalidad: Biblioteca de funciones auxiliares para leer y validar entradas por consola de manera robusta.
# Integrantes: Enrique Siracusa y Miguel Requena
# ---------------------------------------------------------------------------

import re
from typing import Optional, Any

def leer_entero(prompt: str, min_val: Optional[int] = None, default: Optional[int] = None) -> Optional[int]:
    """
    Solicita un número entero por consola, aplicando validación de tipo y valor mínimo.
    Si la entrada está vacía y se definió un valor por defecto, retorna el default.
    Si está vacía y no hay default, retorna None (cancelar).
    """
    while True:
        entrada = input(prompt).strip()
        if not entrada:
            return default
        try:
            valor = int(entrada)
            if min_val is not None and valor < min_val:
                print(f"[Error] El valor debe ser mayor o igual a {min_val}. Intente de nuevo.\n")
                continue
            return valor
        except ValueError:
            print("[Error] Entrada inválida. Debe ingresar un número entero. Intente de nuevo.\n")

def leer_decimal(prompt: str, min_val: Optional[float] = None, default: Optional[float] = None) -> Optional[float]:
    """
    Solicita un número decimal (float) por consola, aplicando validación de tipo y valor mínimo.
    Si la entrada está vacía y se definió un valor por defecto, retorna el default.
    Si está vacía y no hay default, retorna None (cancelar).
    """
    while True:
        entrada = input(prompt).strip()
        if not entrada:
            return default
        try:
            valor = float(entrada)
            if min_val is not None and valor < min_val:
                print(f"[Error] El valor debe ser mayor o igual a {min_val}. Intente de nuevo.\n")
                continue
            return valor
        except ValueError:
            print("[Error] Entrada inválida. Debe ingresar un número decimal. Intente de nuevo.\n")

def leer_codigo_producto(prompt: str, catalogo: Any, producto_actual: Any = None) -> Optional[str]:
    """
    Solicita y valida un nuevo código de producto de 5 caracteres.
    Garantiza que no esté duplicado en el catálogo, a menos que sea el código del producto actual.
    Si la entrada está vacía y se definió un producto actual, retorna su código actual.
    """
    while True:
        entrada = input(prompt).strip()
        if not entrada:
            if producto_actual:
                return producto_actual.cod
            return None
        
        if len(entrada) != 5:
            print("[Error] El código del producto debe tener exactamente 5 caracteres. Intente de nuevo.\n")
            continue
            
        # Verificar duplicados
        existente = catalogo.buscar_por_codigo(entrada)
        if existente:
            if producto_actual and existente.coordenada == producto_actual.coordenada:
                return entrada
            print(f"[Error] Ya existe otro producto con el código '{entrada}'. Intente de nuevo.\n")
            continue
        return entrada

def leer_coordenada_nueva(prompt: str, catalogo: Any) -> Optional[str]:
    """
    Solicita y valida una nueva coordenada alfanumérica única (Ej: I1, A7).
    Garantiza que el formato sea correcto y que la coordenada no esté ocupada.
    """
    while True:
        entrada = input(prompt).strip().upper()
        if not entrada:
            return None
            
        if not re.match(r"^[A-Z][1-9]\d*$", entrada):
            print("[Error] Coordenada inválida. Debe ser una letra (A-Z) seguida de un número entero positivo (Ej: I1, A7). Intente de nuevo.\n")
            continue
            
        existe = catalogo.buscar_por_coordenada(entrada)
        if existe:
            print(f"[Error] Ya existe el producto '{existe.nombre}' en la coordenada '{entrada}'. Intente de nuevo.\n")
            continue
        return entrada

def leer_tarjeta(prompt: str) -> Optional[str]:
    """
    Solicita y valida un número de tarjeta prepago, asegurando que sea numérico.
    """
    while True:
        entrada = input(prompt).strip()
        if not entrada:
            return None
        if not entrada.isdigit():
            print("[Error] El número de tarjeta debe contener únicamente números (dígitos del 0 al 9). Intente de nuevo.\n")
            continue
        return entrada
