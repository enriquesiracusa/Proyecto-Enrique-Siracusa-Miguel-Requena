# Archivo: src/controllers/maquina_expendedora.py
# Funcionalidad: Controlador maestro que gestiona el ciclo de vida, menús y eventos de la máquina expendedora.
# Integrantes: Enrique Siracusa y Miguel Requena

import urllib.request
import json
from typing import List, Dict, Optional, Any
from src.models.tarjeta import Tarjeta
from src.controllers.venta import Venta
from src.views.catalogo import Catalogo
from src.utils.gestor_archivos import GestorArchivos
from src.utils.lector_entradas import leer_tarjeta
from src.controllers.administrador import ControladorAdministrador

class MaquinaExpendedora:
    """
    Controlador principal que gestiona el funcionamiento de la máquina expendedora.
    """
    
    def __init__(self, catalogo: Catalogo, tarjetas: List[Tarjeta], gestor: GestorArchivos, ventas: List[Venta]) -> None:
        """
        Inicializa la máquina expendedora con sus componentes.
        """
        self.catalogo: Catalogo = catalogo
        self.tarjetas: List[Tarjeta] = tarjetas
        self.gestor: GestorArchivos = gestor
        self.ventas: List[Venta] = ventas
        self._encendida: bool = False
        self.ultimo_mensaje: str = ""

    def iniciar(self) -> None:
        """
        Carga los datos iniciales y prepara el sistema.
        """
        print("[Sistema] Iniciando componentes de la Máquina Expendedora...")
        self.catalogo.cargar(self.gestor)
        
        self.tarjetas = []
        self.mapa_tarjetas = {}
        tarjetas_prueba = ["1234567890", "9876543210", "1223334444", "4444333221", "1010101010"]
        clientes_crudos = self.gestor.cargar_clientes_json()
        for i, cliente in enumerate(clientes_crudos):
            self.tarjetas.append(Tarjeta(hash_id=cliente["id"], saldo=float(cliente["saldo"])))
            if i < len(tarjetas_prueba):
                self.mapa_tarjetas[tarjetas_prueba[i]] = cliente["id"]
            
        if self.gestor.existe_estado():
            estado_previo = self.gestor.cargar_estado()
            tarjetas_estado = estado_previo.get("tarjetas", [])
            mapa_saldos = {t["hash_id"]: t["saldo"] for t in tarjetas_estado}
            for tarjeta in self.tarjetas:
                if tarjeta.hash_id in mapa_saldos:
                    tarjeta.saldo = mapa_saldos[tarjeta.hash_id]

        url_remota = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2526-3/main/productos.json"
        try:
            print("[Red] Intentando sincronizar precios con el servidor remoto GitHub...")
            with urllib.request.urlopen(url_remota, timeout=4) as respuesta:
                if respuesta.status == 200:
                    datos_remotos = json.loads(respuesta.read().decode('utf-8'))
                    mapa_precios_remotos = {p["cod"]: float(p["precio"]) for p in datos_remotos if "cod" in p and "precio" in p}
                    actualizaciones = 0
                    for producto in self.catalogo.productos:
                        if producto.cod in mapa_precios_remotos:
                            precio_nube = mapa_precios_remotos[producto.cod]
                            if producto.precio != precio_nube:
                                producto.precio = precio_nube
                                actualizaciones += 1
                    print(f"[Red] Sincronización exitosa. Se actualizaron {actualizaciones} precios de productos.")
        except Exception as e:
            print(f"[Red / Advertencia] No se pudo conectar al servidor remoto ({e}). Continuando con configuración local.")
        
        self._encendida = True

    def mostrar_prompt(self) -> None:
        """
        Muestra el catálogo y el menú de opciones en la consola.
        """
        if getattr(self, 'ultimo_mensaje', ''):
            print(self.ultimo_mensaje)
            self.ultimo_mensaje = ""
            print("-" * 111)
        self.catalogo.mostrar_matriz()
        print("Menú de Opciones:")
        print(" -> Ingrese la coordenada del producto para comprar (Ej: A1 o B3)")
        print(" -> Escriba 'RP' o 'REPORTE' para generar el reporte de ventas parcial")
        print(" -> Escriba 'RS' o 'RESTOCK' para ingresar al menú de administración")
        print(" -> Escriba 'SALIR' para apagar el sistema de la máquina")
        print("-" * 111)

    def procesar_entrada(self, entrada: str) -> None:
        """
        Procesa el comando ingresado por el usuario.
        """
        comando = entrada.strip().upper()
        if not comando:
            return

        if comando == "SALIR":
            print("\n[Analítica] Consolidando métricas y generando reporte final...")
            self.generar_reporte()
            
            print("[Sistema] Guardando el estado actual de la máquina antes de apagar...")
            self.gestor.guardar_estado(self.catalogo, self.tarjetas)
            print("[Sistema] Estado guardado. Máquina Expendedora apagada de manera segura. ¡Hasta luego!")
            self._encendida = False
        elif comando in ("RP", "REPORTE"):
            print("\n" + "*" * 40)
            print("      MÓDULO DE ADMINISTRACIÓN (REPORTE)   ")
            print("*" * 40)
            clave = input(" -> Ingrese la clave de administrador (o presione Enter para volver): ").strip()
            if not clave:
                self.ultimo_mensaje = "\n[Cancelado] Operación cancelada."
            elif clave != "admin123":
                self.ultimo_mensaje = "\n[Acceso Denegado] Clave incorrecta."
            else:
                self.generar_reporte()
                self.ultimo_mensaje = "\n[Analítica] Reporte de ventas generado exitosamente en 'reporte.txt'."
        elif comando in ("RESTOCK", "RS"):
            self.iniciar_restock()
        else:
            self.iniciar_venta_por_coordenada(comando)

    def iniciar_venta_por_coordenada(self, coordenada: str) -> None:
        """
        Inicia el proceso de venta de un producto mediante su coordenada.
        """
        producto = self.catalogo.buscar_por_coordenada(coordenada)
        if not producto:
            self.ultimo_mensaje = f"\n[Error] La coordenada '{coordenada}' no es válida."
            return
            
        if not producto.hay_stock():
            self.ultimo_mensaje = f"\n[Agotado] Lo sentimos, el producto '{producto.nombre}' no tiene existencias."
            return
            
        print(f"\n[Selección] Producto: {producto.nombre} | Precio: ${producto.precio:.2f}")
        tarjeta_input = leer_tarjeta(" -> Ingrese su Número de Tarjeta Prepago (o presione Enter para volver): ")
        if not tarjeta_input:
            self.ultimo_mensaje = "\n[Cancelado] Operación cancelada. Tarjeta vacía."
            return
            
        if hasattr(self, 'mapa_tarjetas') and tarjeta_input in self.mapa_tarjetas:
            hash_calculado = self.mapa_tarjetas[tarjeta_input]
        else:
            hash_calculado = hash(tarjeta_input) & 0xffffffffffffffff

        tarjeta_encontrada = None
        for tarjeta in self.tarjetas:
            if tarjeta.hash_id == hash_calculado:
                tarjeta_encontrada = tarjeta
                break
                
        if not tarjeta_encontrada:
            self.ultimo_mensaje = "\n[Seguridad] Tarjeta inválida o no registrada en el sistema financiero."
            return
            
        print(f"\n[Confirmación] Tarjeta válida. Saldo disponible: ${tarjeta_encontrada.saldo:.2f}")
        while True:
            confirmacion = input(" -> ¿Desea confirmar la compra? (S/N): ").strip().upper()
            if not confirmacion:
                self.ultimo_mensaje = "\n[Cancelado] Compra cancelada por el usuario."
                return
            if confirmacion in ("S", "N"):
                break
            print("[Error] Opción inválida. Ingrese únicamente 'S' o 'N'.")

        if confirmacion != "S":
            self.ultimo_mensaje = "\n[Cancelado] Compra cancelada por el usuario."
            return
            
        if not tarjeta_encontrada.tiene_saldo(producto.precio):
            self.ultimo_mensaje = f"\n[TRANSACCIÓN RECHAZADA] Fondos insuficientes. Saldo actual: ${tarjeta_encontrada.saldo:.2f} | Requerido: ${producto.precio:.2f}"
            return

        nueva_venta = Venta(producto=producto, tarjeta=tarjeta_encontrada, monto=producto.precio)
        nueva_venta.ejecutar()
        self.ventas.append(nueva_venta)
        self.ultimo_mensaje = f"\n[Dispensado] ¡Éxito! {nueva_venta.mensaje_dispensado()}"
        self.gestor.guardar_estado(self.catalogo, self.tarjetas)

    def iniciar_restock(self) -> None:
        """
        Abre el menú de administración y reabastecimiento.
        """
        admin_ctrl = ControladorAdministrador(self.catalogo, self.tarjetas, self.gestor)
        admin_ctrl.iniciar_restock()

    def generar_reporte(self) -> None:
        """
        Calcula las métricas de venta y escribe el reporte en un archivo.
        """
        total_recaudado = 0.0
        ventas_totales = len(self.ventas)
        frecuencia_productos = {}
        gastos_usuarios = {}

        reverso_mapa = {v: k for k, v in self.mapa_tarjetas.items()} if hasattr(self, 'mapa_tarjetas') else {}

        for venta in self.ventas:
            total_recaudado += venta.monto
            nombre_p = venta.producto.nombre
            frecuencia_productos[nombre_p] = frecuencia_productos.get(nombre_p, 0) + 1
            
            tarjeta_id = venta.tarjeta.hash_id
            usuario_id = reverso_mapa.get(tarjeta_id, f"Hash_{tarjeta_id}")
            gastos_usuarios[usuario_id] = gastos_usuarios.get(usuario_id, 0.0) + venta.monto

        if frecuencia_productos:
            producto_estrella = max(frecuencia_productos, key=lambda x: frecuencia_productos[x])
        else:
            producto_estrella = "Ninguno"

        metricas = {
            "total_recaudado": f"${total_recaudado:.2f}",
            "ventas_totales": ventas_totales,
            "producto_estrella": producto_estrella,
            "total_usuarios": len(gastos_usuarios)
        }

        self.gestor.escribir_reporte(metricas, gastos_usuarios)

    def encender(self) -> None:
        """
        Inicia el bucle continuo del simulador de la máquina expendedora.
        """
        self.iniciar()
        import os
        while self._encendida:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.mostrar_prompt()
            entrada_usuario = input("Elija una opción >> ")
            self.procesar_entrada(entrada_usuario)
