import flet as ft
from vistaTarjetasPadre import VistaMaestraTarjetas
from tarjetaBase import TarjetaBase
from BD.choferes_api import *
import threading
from BD.utilidad import *

class VistaChoferes(VistaMaestraTarjetas):
    def __init__(self, page):
        super().__init__(page, titulo="Gestión de Choferes") 
        self.montado = False
        # 1. Definimos qué hace el botón "Nuevo"
        self.on_click_agregar = self.abrir_crear_chofer
        self.inicializar()

    # --- A) AGREGAR ---
    def abrir_crear_chofer(self, e):
        self.txt_nombre = ft.TextField(label="Nombre")
        self.txt_vencimiento_registro = ft.TextField(label="Vencimiento registro")
        self.mostrar_formulario(
            titulo_modal="Nuevo Chofer",
            campos_lista=[self.txt_nombre, self.txt_vencimiento_registro],
            funcion_guardar=self.guardar_chofer_db 
        )

    def guardar_chofer_db(self):
        validar = [self.txt_nombre, self.txt_vencimiento_registro]
        if not validar_campos_obligatorios(validar):
            return False
        
        if not validar_formato_fecha(self.txt_vencimiento_registro):
            return False

        ret, error = guardar_choferes(self.txt_nombre.value, self.txt_vencimiento_registro.value)
        if (ret == False):
            self.page.open(ft.SnackBar(ft.Text(f"{error}"),duration=1000,bgcolor=ft.Colors.RED))
            return False
        self.page.open(ft.SnackBar(ft.Text(f"{error}"),duration=1000,bgcolor=ft.Colors.GREEN))
        self.generar_tarjetas_segundo_plano()
        return True

    # --- B) EDITAR ---
    def abrir_editar_chofer(self, datos_cliente):
        self.txt_nombre = ft.TextField(label="Nombre", value=datos_cliente["nombre"])
        self.txt_vencimiento_registro = ft.TextField(label="Vencimiento registro", value=datos_cliente["vencimiento_registro"])
        id_objetivo = datos_cliente["id"]

        def funcion_actualizar_especifica():
            """
            Esta función 'recuerda' el id_objetivo aunque esté fuera de ella.
            """
            validar = [self.txt_nombre, self.txt_vencimiento_registro]

            if not validar_campos_obligatorios(validar):
                return False
        
            if not validar_formato_fecha(self.txt_vencimiento_registro):
                return False
            # 1. Llamamos a la API de actualizar
            vencimiento_registro_convertido = convertir_fecha_para_db(self.txt_vencimiento_registro.value)
            ret, error = actualizar_choferes(id_objetivo, self.txt_nombre.value, vencimiento_registro_convertido)
            
            if ret:
                self.page.open(ft.SnackBar(ft.Text(f"{error}"),duration=1000,bgcolor=ft.Colors.GREEN))
                self.generar_tarjetas_segundo_plano() # Recargamos la grilla
                return True # Cierra modal
            else:
                self.page.open(ft.SnackBar(ft.Text(f"{error}"),duration=1000,bgcolor=ft.Colors.RED))
                self.barra_carga.visible = False
                self.update()
                return False
            
        self.mostrar_formulario(
            titulo_modal=f"Editar {datos_cliente["nombre"]}",
            campos_lista=[self.txt_nombre,self.txt_vencimiento_registro],
            funcion_guardar=funcion_actualizar_especifica
        )

    # --- C) BORRAR ---
    def abrir_borrar_chofer(self, d):

        def funcion_borrar_especifica():
            """
            Esta función 'recuerda' el id_objetivo aunque esté fuera de ella.
            """
            # 1. Llamamos a la API de actualizar
            ret, error = borrar_choferes(d["id"])
            
            if ret:
                self.page.open(ft.SnackBar(ft.Text(f"{error}"),duration=1000,bgcolor=ft.Colors.GREEN))
                self.generar_tarjetas_segundo_plano() # Recargamos la grilla
                return True # Cierra modal
            else:
                self.page.open(ft.SnackBar(ft.Text(f"{error}"),duration=1000,bgcolor=ft.Colors.RED))
                self.barra_carga.visible = False
                self.update()
                return False

        self.mostrar_confirmacion_borrar(
            item_nombre=d["nombre"],
            funcion_borrar=funcion_borrar_especifica
        )

    
    def generar_tarjetas_segundo_plano (self):
        self.barra_carga.visible = True

        self.update() # Actualizamos para que aparezca la barrita YA

        # 2. Lanzamos al "segundo empleado" a trabajar
        # target = la función que tarda mucho
        hilo = threading.Thread(target=self.generar_tarjetas)
        hilo.start()
        # Aquí la función termina inmediatamente y la app NO se traba.


    def generar_tarjetas(self):
        # Estos son los datos que pediste que se muestren
        flag, datos = obtener_todo_choferes()
        if self.montado == False:
            print ("Cambio vista")
            return
        
        if (flag == False):
            self.page.open(ft.SnackBar(ft.Text(f"{datos}"),duration=1000,bgcolor=ft.Colors.RED))
            self.barra_carga.visible = False
            self.update()
            return

        lista = []
        for d in datos:
            fecha_hoy = datetime.now().date()
            if d["vencimiento_registro"] < fecha_hoy:
                color = ft.Colors.RED
            else:
                color = ft.Colors.BLUE
            datos_extra = ft.Column([
                ft.Divider(),
                # --- CORRECCIÓN ---
                ft.Container(
                    # 1. El contenido es UNA Columna (que agrupa los textos)
                    content=ft.Column(
                        controls=[
                            ft.Text(f"LINTI: 10/10/2025", color=ft.Colors.RED),
                            ft.Text(f"Licencia de conducir: 10/10/2025", color=ft.Colors.RED),
                            ft.Text(f"Psicofísico: 10/10/2025", color=ft.Colors.RED),
                            ft.Text(f"Libreta sanitaria: 10/10/2025", color=ft.Colors.RED),
                        ],
                        # 2. Esto centra los textos horizontalmente DENTRO de la columna
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2 # Espacio pequeño entre líneas
                    ),
                    # 3. Esto alinea la Columna entera en el centro del Container
                    alignment=ft.alignment.center,
                    padding=5,
                    bgcolor=ft.Colors.GREY_100, # Opcional: para resaltar la zona
                    border_radius=5
                )
            ])
            card = TarjetaBase(
                titulo=(d["nombre"]),
                subtitulo="23857483",
                icono=ft.Icons.PERSON, # <--- CORREGIDO (minúscula)
                color_estado=color,
                #texto_estado="ejemplo",
                contenido_extra=datos_extra,
                # Lambdas para pasar los datos específicos de este camión
                on_editar=lambda e, x=d: self.abrir_editar_chofer(x),
                on_borrar=lambda e, x=d: self.abrir_borrar_chofer(x),
            )
            lista.append(card)

        if hasattr(self, 'fila_tarjetas'):
            self.fila_tarjetas.controls = lista
        self.barra_carga.visible = False
        if (self.page):
            self.update()

    
    def did_mount(self):
        # Este método lo ejecuta Flet automáticamente cuando la vista
        # ya está visible en la pantalla y tiene un UID válido.
        self.montado = True
        self.barra_carga.visible = True
        self.update()
        hilo = threading.Thread(target=self.generar_tarjetas)
        hilo.start()

    def will_unmount(self):
        # Se ejecuta cuando el usuario cambia de vista
        self.montado = False