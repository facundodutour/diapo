import flet as ft
from vistaTarjetasPadre import VistaMaestraTarjetas
from tarjetaBase import TarjetaBase
from BD.clientes_api import *
import threading
from BD.utilidad import *

class VistaClientes(VistaMaestraTarjetas):
    def __init__(self, page):
        super().__init__(page, titulo="Gestión de Clientes") 
        self.montado = False
        # 1. Definimos qué hace el botón "Nuevo"
        self.on_click_agregar = self.abrir_crear_cliente
        self.inicializar()

    # --- A) AGREGAR ---
    def abrir_crear_cliente(self, e):
        self.txt_razon_social = ft.TextField(label="Razón social")
        self.txt_cuit = ft.TextField(label="CUIT", input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9\-]*$", replacement_string=""))
        self.txt_direccion = ft.TextField(label="Dirección", keyboard_type= ft.KeyboardType.STREET_ADDRESS)
        self.txt_email = ft.TextField(label="e-mail", keyboard_type= ft.KeyboardType.EMAIL)
        self.txt_telefono = ft.TextField(label="Telefono", keyboard_type= ft.KeyboardType.PHONE, input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9+\-]*$", replacement_string=""))
        self.mostrar_formulario(
            titulo_modal="Nuevo Cliente",
            campos_lista=[self.txt_razon_social, self.txt_cuit, self.txt_direccion, self.txt_email, self.txt_telefono],
            funcion_guardar=self.guardar_cliente_db 
        )

    def guardar_cliente_db(self):
        validar = [self.txt_razon_social, self.txt_cuit, self.txt_direccion, self.txt_email, self.txt_telefono]
        if not validar_campos_obligatorios(validar):
            return False
        
        if not es_email_valido(self.txt_email):
            return False

        ret, error = guardar_clientes(self.txt_razon_social.value, self.txt_cuit.value, self.txt_direccion.value, self.txt_email.value, self.txt_telefono.value)
        if (ret == False):
            self.page.open(ft.SnackBar(ft.Text(f"{error}"),duration=1000,bgcolor=ft.Colors.RED))
            return False
        self.page.open(ft.SnackBar(ft.Text(f"{error}"),duration=1000,bgcolor=ft.Colors.GREEN))
        self.generar_tarjetas_segundo_plano()
        return True

    # --- B) EDITAR ---
    def abrir_editar_cliente(self, datos_cliente):
        self.txt_razon_social = ft.TextField(label="Razón social", value=datos_cliente["razon_social"])
        self.txt_cuit = ft.TextField(label="CUIT", value=datos_cliente["cuit"], input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9\-]*$", replacement_string=""))
        self.txt_direccion = ft.TextField(label="Dirección", value=datos_cliente["direccion"], keyboard_type= ft.KeyboardType.STREET_ADDRESS)
        self.txt_email = ft.TextField(label="e-mail", value=datos_cliente["email"], keyboard_type= ft.KeyboardType.EMAIL)
        self.txt_telefono = ft.TextField(label="Telefono", value=datos_cliente["telefono"], keyboard_type= ft.KeyboardType.PHONE, input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9+\-]*$", replacement_string=""))
        id_objetivo = datos_cliente["id"]

        def funcion_actualizar_especifica():
            """
            Esta función 'recuerda' el id_objetivo aunque esté fuera de ella.
            """
            validar = [self.txt_razon_social, self.txt_cuit, self.txt_direccion, self.txt_email, self.txt_telefono]

            if not validar_campos_obligatorios(validar):
                return False
        
            if not es_email_valido(self.txt_email):
                return False
            # 1. Llamamos a la API de actualizar
            ret, error = actualizar_clientes(id_objetivo,self.txt_razon_social.value,self.txt_cuit.value,self.txt_direccion.value,self.txt_email.value,self.txt_telefono.value)
            
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
            titulo_modal=f"Editar {datos_cliente["razon_social"]}",
            campos_lista=[self.txt_razon_social, self.txt_cuit, self.txt_direccion, self.txt_email, self.txt_telefono],
            funcion_guardar=funcion_actualizar_especifica
        )

    # --- C) BORRAR ---
    def abrir_borrar_cliente(self, razon_social):

        def funcion_borrar_especifica():
            """
            Esta función 'recuerda' el id_objetivo aunque esté fuera de ella.
            """
            # 1. Llamamos a la API de actualizar
            ret, error = borrar_clientes(razon_social)
            
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
            item_nombre=razon_social,
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
        flag, datos = obtener_todo_clientes()

        if self.montado == False:
            print ("Cambio de vista")
            return

        if (flag == False):
            self.page.open(ft.SnackBar(ft.Text(f"{datos}"),duration=1000,bgcolor=ft.Colors.RED))
            self.barra_carga.visible = False
            self.update()
            return

        lista = []
        for d in datos:
            color =  ft.Colors.GREEN
            datos_extra = ft.Column([
                ft.Text(value = f"{d['direccion']}", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, tooltip=d["direccion"]),
                ft.Divider(),
                
                # --- CORRECCIÓN ---
                ft.Container(
                    # 1. El contenido es UNA Columna (que agrupa los textos)
                    content=ft.Column(
                        controls=[
                            ft.Text("Contacto:", weight="bold"),
                            ft.Text(f"{d["email"]}", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, tooltip=d["email"]),
                            ft.Text(f"{d["telefono"]}", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, tooltip=d["telefono"])
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
                titulo=d["razon_social"],
                subtitulo=d["cuit"],
                icono=ft.Icons.PERSON, # <--- CORREGIDO (minúscula)
                color_estado=color,
                #texto_estado="ejemplo",
                contenido_extra=datos_extra,
                # Lambdas para pasar los datos específicos de este camión
                on_editar=lambda e, x=d: self.abrir_editar_cliente(x),
                on_borrar=lambda e, x=d["razon_social"]: self.abrir_borrar_cliente(x),
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