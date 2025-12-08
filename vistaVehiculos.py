import flet as ft
from vistaTarjetasPadre import VistaMaestraTarjetas
from tarjetaBase import TarjetaBase
from BD.vehiculos_api import *
import threading
from BD.utilidad import *

class VistaCamiones(VistaMaestraTarjetas):
    def __init__(self, page):
        super().__init__(page, titulo="Gestión de Flota") 
        self.montado = False
        # 1. Definimos qué hace el botón "Nuevo"
        self.on_click_agregar = self.abrir_crear_camion 
        self.inicializar()

    # --- A) AGREGAR ---
    def abrir_crear_camion(self, e):
        self.txt_patente = ft.TextField(label="Patente")
        self.txt_modelo = ft.TextField(label="Marca y Modelo")
        self.txt_anio = ft.TextField(label="Año", input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""), max_length=4)
        self.txt_V_VTV = ft.TextField(label="Vencimiento VTV")
        self.txt_V_seguro = ft.TextField(label="Vencimiento seguro")
        self.mostrar_formulario(
            titulo_modal="Nuevo Camión",
            campos_lista=[self.txt_patente, self.txt_modelo, self.txt_anio, self.txt_V_VTV, self.txt_V_seguro],
            funcion_guardar=self.guardar_camion_db 
        )

    def guardar_camion_db(self):
        validar = [self.txt_patente, self.txt_modelo, self.txt_anio, self.txt_V_seguro, self.txt_V_VTV]
        if not validar_campos_obligatorios(validar):
            return False
        
        if not validar_formato_fecha (self.txt_V_VTV):
            return False
        
        if not validar_formato_fecha (self.txt_V_seguro):
            return False
        
        fecha_vtv = convertir_fecha_para_db(self.txt_V_VTV.value)
        fecha_seguro = convertir_fecha_para_db(self.txt_V_seguro.value)

        ret, error = guardar_vehiculos(self.txt_patente.value,self.txt_modelo.value,self.txt_anio.value,fecha_vtv,fecha_seguro)
        if (ret == False):
            self.page.open(ft.SnackBar(ft.Text(f"{error}"),duration=1000,bgcolor=ft.Colors.RED))
            return False

        self.generar_tarjetas_segundo_plano()
        return True

    # --- B) EDITAR ---
    def abrir_editar_camion(self, datos_camion):
        self.txt_patente = ft.TextField(label="Patente", value=datos_camion["patente"])
        self.txt_modelo = ft.TextField(label="Marca y Modelo", value=datos_camion["marca_modelo"])
        self.txt_anio = ft.TextField(label="Año", value=datos_camion["anio"], input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""), max_length=4)
        self.txt_V_VTV = ft.TextField(label="Vencimiento VTV", value=datos_camion["vencimiento_vtv"])
        self.txt_V_seguro = ft.TextField(label="Vencimiento seguro", value=datos_camion["vencimiento_seguro"])
        id_objetivo = datos_camion["id"]

        def funcion_actualizar_especifica():
            """
            Esta función 'recuerda' el id_objetivo aunque esté fuera de ella.
            """
            # 1. Llamamos a la API de actualizar
            exito, msj = actualizar_vehiculos(id_objetivo,self.txt_patente.value,self.txt_modelo.value,self.txt_anio.value,self.txt_V_VTV.value,self.txt_V_seguro.value)
            
            if exito:
                self.generar_tarjetas_segundo_plano() # Recargamos la grilla
                return True # Cierra modal
            else:
                self.page.open(ft.SnackBar(ft.Text(f"{msj}"),duration=1000,bgcolor=ft.Colors.RED))
                self.barra_carga.visible = False
                self.update()
                return False
            
        self.mostrar_formulario(
            titulo_modal=f"Editar {datos_camion['patente']}",
            campos_lista=[self.txt_patente, self.txt_modelo, self.txt_anio, self.txt_V_VTV, self.txt_V_seguro],
            funcion_guardar=funcion_actualizar_especifica
        )

    # --- C) BORRAR ---
    def abrir_borrar_camion(self, patente):

        def funcion_borrar_especifica():
            """
            Esta función 'recuerda' el id_objetivo aunque esté fuera de ella.
            """
            # 1. Llamamos a la API de actualizar
            exito, msj = borrar_vehiculos(patente)
            
            if exito:
                self.generar_tarjetas_segundo_plano() # Recargamos la grilla
                return True # Cierra modal
            else:
                self.page.open(ft.SnackBar(ft.Text(f"{msj}"),duration=1000,bgcolor=ft.Colors.RED))
                self.barra_carga.visible = False
                self.update()
                return False

        self.mostrar_confirmacion_borrar(
            item_nombre=patente,
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
        flag, datos = obtener_todo_vehiculos()

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
            fecha_hoy = datetime.now().date()
            if ((d["vencimiento_vtv"] < fecha_hoy) or (d["vencimiento_seguro"] < fecha_hoy)):
                color = ft.Colors.RED
            else:
                color = ft.Colors.BLUE
            #color = ft.Colors.RED#ft.Colors.RED if d["estado"] == "VENCIDO" else ft.Colors.BLUE
            datos_extra = ft.Column([
                ft.Divider(),
                
                # --- CORRECCIÓN ---
                ft.Container(
                    # 1. El contenido es UNA Columna (que agrupa los textos)
                    content=ft.Column(
                        controls=[
                            ft.Text("Vencimientos:", weight="bold"),
                            ft.Text(f"VTV: {d["vencimiento_vtv"]}", color=ft.Colors.RED),
                            ft.Text(f"Seguro: {d["vencimiento_seguro"]}"),
                            ft.Text (f"SENASA: 10/12/2027"),
                            ft.Text (f"Matafuegos: 4/7/2023", color=ft.Colors.RED),
                            ft.Text (f"Patente: 10/12/2025", color=ft.Colors.ORANGE),
                            ft.ElevatedButton (text="Historial")
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
                titulo=d["patente"],
                subtitulo=f"{d["marca_modelo"]} {d["anio"]}",
                icono=ft.Icons.DIRECTIONS_BUS, # <--- CORREGIDO (minúscula)
                color_estado=color,
                #texto_estado=d["estado"],
                contenido_extra=datos_extra,
                # Lambdas para pasar los datos específicos de este camión
                on_editar=lambda e, x=d: self.abrir_editar_camion(x),
                on_borrar=lambda e, x=d["patente"]: self.abrir_borrar_camion(x),
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