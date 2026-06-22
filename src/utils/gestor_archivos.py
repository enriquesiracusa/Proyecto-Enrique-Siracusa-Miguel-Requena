# Archivo: src/utils/gestor_archivos.py
# Funcionalidad: Gestión de persistencia de datos (lectura y escritura de archivos JSON de productos, clientes, estado y reportes).
# Integrantes: Enrique Siracusa y Miguel Requena

import os
import json
from typing import List, Dict, Any
from src.models.tarjeta import Tarjeta

class GestorArchivos:
    """
    Maneja la lectura y escritura de archivos locales JSON y reportes de texto.
    """
    
    def __init__(self, ruta_productos_json: str, ruta_clientes_json: str, ruta_estado: str) -> None:
        """
        Inicializa las rutas de almacenamiento de archivos.
        """
        self.ruta_productos_json: str = ruta_productos_json
        self.ruta_clientes_json: str = ruta_clientes_json
        self.ruta_estado: str = ruta_estado

    def cargar_productos_json(self) -> List[Dict[str, Any]]:
        """
        Carga la lista de productos base desde el archivo JSON correspondiente.
        """
        try:
            if not os.path.exists(self.ruta_productos_json):
                return []
            with open(self.ruta_productos_json, 'r', encoding='utf-8') as archivo:
                datos = json.load(archivo)
                return datos if isinstance(datos, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        except Exception as e:
            print(f"[Error del Sistema] No se pudo leer productos: {e}")
            return []

    def cargar_clientes_json(self) -> List[Dict[str, Any]]:
        """
        Carga la lista de clientes y tarjetas desde el archivo JSON correspondiente.
        """
        try:
            if not os.path.exists(self.ruta_clientes_json):
                return []
            with open(self.ruta_clientes_json, 'r', encoding='utf-8') as archivo:
                datos = json.load(archivo)
                return datos if isinstance(datos, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        except Exception as e:
            print(f"[Error del Sistema] No se pudo leer clientes: {e}")
            return []

    def cargar_estado(self) -> Dict[str, Any]:
        """
        Carga el estado de guardado anterior de la máquina.
        """
        try:
            if not self.existe_estado():
                return {}
            with open(self.ruta_estado, 'r', encoding='utf-8') as archivo:
                datos = json.load(archivo)
                return datos if isinstance(datos, dict) else {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
        except Exception as e:
            print(f"[Error del Sistema] No se pudo leer el estado: {e}")
            return {}

    def guardar_estado(self, catalogo: Any, tarjetas: List[Tarjeta]) -> None:
        """
        Guarda el estado actual del inventario y las tarjetas.
        """
        try:
            lista_productos_serializados = []
            for p in catalogo.productos:
                lista_productos_serializados.append({
                    "cod": p.cod,
                    "coordenada": p.coordenada,
                    "stock": p.stock
                })
            
            lista_tarjetas_serializadas = []
            for t in tarjetas:
                lista_tarjetas_serializadas.append({
                    "hash_id": t.hash_id,
                    "saldo": t.saldo
                })
            
            estado_dinamico = {
                "productos": lista_productos_serializados,
                "tarjetas": lista_tarjetas_serializadas
            }
            
            with open(self.ruta_estado, 'w', encoding='utf-8') as archivo:
                json.dump(estado_dinamico, archivo, indent=4, ensure_ascii=False)
                
        except Exception as e:
            print(f"[Error Crítico] Falló la persistencia del estado actual del sistema: {e}")

    def existe_estado(self) -> bool:
        """
        Verifica si existe el archivo de estado de la máquina.
        """
        try:
            return os.path.exists(self.ruta_estado)
        except Exception:
            return False

    def escribir_reporte(self, datos: Dict[str, Any], gastos_usuarios: Dict[str, float] = None) -> None:
        """
        Genera el archivo de reporte final de ventas en formato de texto.
        """
        ruta_reporte = "reporte.txt"
        try:
            with open(ruta_reporte, 'w', encoding='utf-8') as archivo:
                archivo.write("=========================================\n")
                archivo.write("       REPORTE DE MÁQUINA EXPENDEDORA    \n")
                archivo.write("=========================================\n\n")
                
                for clave, valor in datos.items():
                    archivo.write(f" -> {clave.upper()}: {valor}\n")
                
                if gastos_usuarios:
                    archivo.write("\nGasto por Usuario / Tarjeta:\n")
                    for usuario, gasto in gastos_usuarios.items():
                        archivo.write(f" -> Tarjeta {usuario}: ${gasto:.2f}\n")
                    
                archivo.write("\n=========================================\n")
                archivo.write("       FIN DEL REPORTE GENERADO          \n")
                archivo.write("=========================================\n")
        except Exception as e:
            print(f"[Error Técnico] No se pudo generar el archivo físico del reporte: {e}")
