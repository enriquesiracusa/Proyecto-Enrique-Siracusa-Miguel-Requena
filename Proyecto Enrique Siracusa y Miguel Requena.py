# ---------------------------------------------------------------------------
# Archivo: Proyecto Enrique Siracusa y Miguel Requena.py
# Funcionalidad: Punto de entrada principal para el inicio y arranque del simulador de la Máquina Expendedora.
# Integrantes: Enrique Siracusa y Miguel Requena
# Proyecto Final: Sistema de Máquina Expendedora con POO (Versión Unificada)
# Ejecución requerida: PYTHONHASHSEED=0 python "Proyecto Enrique Siracusa y Miguel Requena.py"
# ---------------------------------------------------------------------------

import os
import sys

# Parche crítico para compatibilidad de hash de tarjeta
if os.environ.get("PYTHONHASHSEED") != "0":
    os.environ["PYTHONHASHSEED"] = "0"
    import subprocess
    try:
        script_path = os.path.abspath(__file__)
        result = subprocess.run([sys.executable, script_path])
        sys.exit(result.returncode)
    except Exception:
        pass

from src.utils.gestor_archivos import GestorArchivos
from src.views.catalogo import Catalogo
from src.controllers.maquina_expendedora import MaquinaExpendedora

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RUTA_PROD: str = os.path.join(BASE_DIR, "productos.json")
    RUTA_CLIE: str = os.path.join(BASE_DIR, "clientes.json")
    RUTA_ESTA: str = os.path.join(BASE_DIR, "estado_maquina.json")
    
    print("=" * 60)
    print("   SISTEMA DE CONTROL DE MÁQUINA EXPENDEDORA CORPORATIVA")
    print("=" * 60)
    
    gestor_archivos = GestorArchivos(
        ruta_productos_json=RUTA_PROD, 
        ruta_clientes_json=RUTA_CLIE, 
        ruta_estado=RUTA_ESTA
    )
    
    catalogo_sistema = Catalogo(productos=[])
    
    maquina = MaquinaExpendedora(
        catalogo=catalogo_sistema,
        tarjetas=[],
        gestor=gestor_archivos,
        ventas=[]
    )
    
    maquina.encender()
