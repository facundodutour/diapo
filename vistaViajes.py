import flet as ft
from vistaListaPadre import VistaMaestraLista
from tarjetaBase import TarjetaBase
from BD.viajes_api import *
import threading
from BD.utilidad import *

class VistaViajes(VistaMaestraLista):
    def __init__(self, page):
        super().__init__(page, titulo="Gestión de Viajes") 
        self.modo_actual = "0"
        self.montado = False
        self.patente_seleccionada = None
        # 1. Definimos qué hace el botón "Nuevo"
        self.on_click_agregar = self.abrir_crear_viaje
        columnas = [

            ft.Text("ID"),
            ft.Text("Fecha"),
            ft.Text("Chofer"),   
            ft.Text("Vehiculo"),
            ft.Text("Destino"),
            ft.Text("Estado"),
            ft.Text("Cliente"),
            ft.Text("Numero de viaje/ HR/ Remito/ OC"),
            ft.Text("Importe"),
            ft.Text("Comisión"),
            ft.Text("Editar"),
            ft.Text("Borrar")
        ]
        self.inicializar(columnas)

    def contenido_extra_top(self):
        
        # Guardamos la fila en una variable "self" para poder ocultarla después
        # cuando cambien a "Terciarizados"
        self.fila_patentes = ft.Row(
            controls=[
            ],
            alignment=ft.MainAxisAlignment.CENTER # Centramos los chips
        )
        self.actualizar_patentes()

        self.botones_tipos = ft.SegmentedButton(
             segments=[
                    ft.Segment(value="0", label=ft.Text("Propios")),
                    ft.Segment(value="1", label=ft.Text("Tercerizados")),
                ],
                selected={"0"},
                allow_multiple_selection=False,
                on_change=self.cambiar_modo,
                disabled = False
            )
        
        self.txt_buscador = ft.TextField(hint_text="Buscar por chofer, destino, remito...", expand=True, prefix_icon=ft.Icons.SEARCH, on_change=self.generar_filas_segundo_plano)

        self.dd_estado_filtro = ft.Dropdown(
            width=150,
            label="Estado",
            options=[
                ft.dropdown.Option(key="Todos", text="Todos"),
                ft.dropdown.Option(key = "0", text="En tránsito"),
                ft.dropdown.Option(key = "1", text="Finalizado"),
            ],
            value="Todos",
            on_change=self.generar_filas_segundo_plano
        )

        self.facturacion_filtro = ft.SegmentedButton(
            segments=[
                ft.Segment(value="Todos", label=ft.Text("Todos")),
                ft.Segment(value="0", label=ft.Text("A Facturar")), # Lo más usado
                ft.Segment(value="1", label=ft.Text("Facturado")),
            ],
            selected={"Todos"},
            on_change=self.generar_filas_segundo_plano
        )

        self.busqueda_filtros = ft.Container(content=ft.Row([
                    self.txt_buscador,
                    self.dd_estado_filtro,
                    self.facturacion_filtro
                ]
            )
        )
        return ft.Column([
            ft.Container(
                # CORRECCIÓN AQUÍ:
                # Envolvemos todo en una Columna porque el Container solo acepta un hijo
                content=ft.Column([
                    self.botones_tipos,
                    self.fila_patentes, # Agregamos la fila que creamos arriba
                    self.busqueda_filtros
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER), # Alinea lo de adentro
                
                alignment=ft.alignment.center,
                padding=10
            )
        ])
    
    def cambiar_chip (self, e):
        patente_tocada = e.control.label.value
        self.fila_patentes.disabled=True

        # 1. Lógica de Toggle:
        # Si la que toqué es igual a la que ya estaba seleccionada, la limpio (None).
        # Si es diferente, la guardo como la nueva seleccionada.
        if self.patente_seleccionada == patente_tocada:
            self.patente_seleccionada = None 
        else:
            self.patente_seleccionada = patente_tocada

        # 2. Actualización visual
        for chip in self.fila_patentes.controls:
            # Ahora chip.selected será True solo si hay una patente seleccionada 
            # Y coincide con este chip.
            chip.selected = (self.patente_seleccionada == chip.label.value)
            chip.update()

        # 3. Resto de tu lógica
        # OJO: self.patente_seleccionada ahora puede ser None.
        # Asegúrate de que 'generar_filas_segundo_plano' sepa manejar eso.
        self.patente_anterior = self.patente_seleccionada
        self.generar_filas_segundo_plano()

    def actualizar_patentes (self):
        if (self.montado == False):
            return
        self.fila_patentes.controls.clear()
        flag, datos = obtener_patentes()
        if (flag == False):
            self.page.open(ft.SnackBar(ft.Text(f"{datos}"),duration=1000,bgcolor=ft.Colors.RED))
            return False
        chips = []
        for x in datos:
            esta_seleccionado = (str(x["patente"]) == getattr(self, 'patente_seleccionada', None))
            chips.append (ft.Chip(label=ft.Text(f"{x["patente"]}"), on_click=self.cambiar_chip, selected=esta_seleccionado))
        self.fila_patentes.controls = chips
        if self.page:
            self.fila_patentes.update()
        return True

    def cambiar_modo (self, e):
        self.botones_tipos.disabled = True
        self.botones_tipos.update()
        seleccion = list(e.control.selected)[0]
        self.modo_actual = seleccion

        # 1. Lógica Visual: Ocultar/Mostrar chips
        self.tabla.rows.clear()
        if seleccion == "0":
            self.fila_patentes.visible = True
            self.tabla.columns = [
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Chofer")),      # Específico de Propios
                ft.DataColumn(ft.Text("Vehiculo")),
                ft.DataColumn(ft.Text("Destino")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Numero de viaje/ HR/ Remito/ OC")),
                ft.DataColumn(ft.Text("Importe")),
                ft.DataColumn(ft.Text("Comisión")), # Específico de Propios [cite: 30]
                ft.DataColumn(ft.Text("Editar")),
                ft.DataColumn(ft.Text("Borrar")),
            ]
        else:
            self.fila_patentes.visible = False
            self.tabla.columns = [
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Destino")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Numero de viaje/ HR/ Remito/ OC")),
                ft.DataColumn(ft.Text("Importe")),       
                ft.DataColumn(ft.Text("Editar")),
                ft.DataColumn(ft.Text("Borrar")),
            ]
        
        # Actualizamos la tabla para que se vean los nuevos títulos
        self.tabla.update()
        # Actualizamos la cabecera para que se oculte/muestre la fila
        self.fila_patentes.update() 

        # 2. Lógica de Datos: Recargar la tabla
        self.generar_filas_segundo_plano()       

    # --- A) AGREGAR ---
    def abrir_crear_viaje(self, e):
        # 1. Dropdown Principal
        self.dd_categoria = ft.Dropdown(
            label="Tipo de viaje",
            options=[
                ft.dropdown.Option(key="0",text="Propio"),
                ft.dropdown.Option(key="1",text="Tercerizado"),
            ],
            on_change=self.cambiar_categoria, # EL GATILLO
            width=400,
        )

        # 2. El "Hueco" vacío
        self.contenedor_dinamico = ft.Column()

        # 3. Barra de carga (Opcional, la iniciamos oculta)
        self.barra_carga = ft.ProgressBar(width=400, color="blue", visible=False)

        # 4. Mostrar el modal
        self.mostrar_formulario(
            titulo_modal="Nuevo Viaje",
            campos_lista=[
                self.dd_categoria, 
                self.barra_carga, # Agregamos la barra aquí
                ft.Divider(), 
                self.contenedor_dinamico
            ],
            funcion_guardar=self.guardar_viaje_db 
        )

    def cambiar_categoria(self, e):
        # 1. Limpieza inicial
        self.contenedor_dinamico.controls.clear()
        
        # Activamos barra de carga y actualizamos para que se vea
        self.dd_categoria.disabled = True
        self.dd_categoria.update()
        self.barra_carga.visible = True
        self.barra_carga.update()

        # 2. Obtener Clientes (Simulando DB)
        flag_clientes, datos_clientes = obtener_clientes()
        flag_choferes, datos_choferes = obtener_choferes()
        flag_vehiculos, datos_vehiculos = obtener_patentes()
        # Ocultamos carga
        self.barra_carga.visible = False
        self.barra_carga.update()

        if flag_clientes == False:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"{datos_clientes}"), bgcolor=ft.Colors.RED)
            self.page.snack_bar.open = True
            self.page.update()
            return
        

        if flag_choferes == False:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"{datos_choferes}"), bgcolor=ft.Colors.RED)
            self.page.snack_bar.open = True
            self.page.update()
            return

        if flag_vehiculos == False:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"{datos_vehiculos}"), bgcolor=ft.Colors.RED)
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # 3. Crear Dropdown de Clientes con KEY (ID)
        self.dd_cliente = ft.Dropdown(
            label="Cliente", 
            options=[
                ft.dropdown.Option(key=str(c["id"]), text=c["razon_social"]) 
                for c in datos_clientes
            ],
            width=400
        )

        self.dd_vehiculo = ft.Dropdown(
            label="Vehiculo", 
            options=[
                ft.dropdown.Option(key=str(c["patente"]), text=c["patente"]) 
                for c in datos_vehiculos
            ],
            width=400
        )

        # 4. Campos Comunes
        self.txt_fecha = ft.TextField(label="Fecha", width=400)
        self.txt_destino = ft.TextField(label="Destino", width=400)
        self.txt_remito = ft.TextField(label="Remito/Nro Viaje", width=400)
        self.txt_importe = ft.TextField(label="Importe (Venta)", width=400, prefix_text="$", input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""))
        self.dd_estado = ft.Dropdown(
            label="Estado del viaje",
            options=[
                ft.dropdown.Option(key=("0"), text="En transito"), 
                ft.dropdown.Option(key=("1"), text="Finalizado") 
            ],
            width=400
        )

        lista_campos = [
            self.txt_fecha,
            self.dd_cliente, 
            self.txt_destino, 
            self.dd_estado,
            self.txt_remito, 
            self.txt_importe
        ]

        # 5. Lógica Condicional (Propio vs Tercerizado)
        tipo_viaje = self.dd_categoria.value

        if tipo_viaje == "0":
            self.dd_chofer = ft.Dropdown(
                label="Chofer", 
                options=[
                    ft.dropdown.Option(key=str(c["id"]), text=c["nombre"]) 
                    for c in datos_choferes
                ],
                width=400
            )

            self.dd_vehiculo = ft.Dropdown(
                label="Vehiculo", 
                options=[
                    ft.dropdown.Option(key=str(c["patente"]), text=c["patente"]) 
                    for c in datos_vehiculos
                ],
                width=400
            )

            self.txt_porcentaje = ft.TextField(label="Porcentaje chofer", value="17", suffix_text="%", width=400, input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""))
            
            lista_campos.insert(2, self.dd_chofer)
            lista_campos.insert(3, self.dd_vehiculo)
            lista_campos.append(self.txt_porcentaje)

        # 6. RELLENAR Y MOSTRAR
        self.dd_categoria.disabled = False
        self.dd_categoria.update()
        self.contenedor_dinamico.controls.extend(lista_campos)
        self.contenedor_dinamico.update() # <--- ¡ESTO ES LO QUE HACE QUE APAREZCA!


    def guardar_viaje_db(self):
        tipo_viaje = self.dd_categoria
        cliente_id = self.dd_cliente
        fecha = self.txt_fecha
        destino = self.txt_destino
        importe_venta = self.txt_importe
        estado_viaje = self.dd_estado
        remito = self.txt_remito.value if self.txt_remito.value else None
        estado = self.dd_estado
        validar = [tipo_viaje,cliente_id,fecha,destino,importe_venta,estado_viaje,estado]

        if not validar_formato_fecha(self.txt_fecha):
            return False

        fecha_convertida = convertir_fecha_para_db(self.txt_fecha.value)
        if tipo_viaje.value == "0":
            chofer_id = self.dd_chofer
            vehiculo_id = self.dd_vehiculo
            porcentaje = self.txt_porcentaje
            propio = [chofer_id,porcentaje, chofer_id]
            validar.extend(propio)

            if not validar_campos_obligatorios(validar):
                return False
            porcentaje = int (porcentaje.value)
            importe_venta = int (importe_venta.value)
            ret, error = guardar_viajes_propios(fecha_convertida, cliente_id.value, destino.value, remito, importe_venta, (porcentaje * importe_venta / 100), chofer_id.value, tipo_viaje.value, estado.value, vehiculo_id.value)
        else:
            if not validar_campos_obligatorios(validar):
                return False
            importe_venta = int (importe_venta.value)
            ret, error = guardar_viajes_tercerizados(fecha_convertida, cliente_id.value, destino.value, remito, importe_venta, tipo_viaje.value, estado.value)

        if (ret == False):
            self.page.open(ft.SnackBar(ft.Text(f"{error}"),duration=1000,bgcolor=ft.Colors.RED))
            return False

        self.page.open(ft.SnackBar(ft.Text(f"{error}"),duration=1000,bgcolor=ft.Colors.GREEN))
        self.generar_filas_segundo_plano()
        return True

    def abrir_editar_viaje_segundo_plano(self, e):
        # 1. Recuperamos los datos del botón
        datos_viaje = e.control.data
        
        # 2. Mostramos la barra de carga VISUALMENTE
        self.barra_carga.visible = True
        self.update() # Importante: Actualizar la pantalla YA para que se vea la barra

        hilo = threading.Thread(target=self.abrir_editar_viaje, args=(datos_viaje,))
        hilo.start()

    # --- B) EDITAR ---
    def abrir_editar_viaje(self, datos_viaje):
        id_viaje = datos_viaje["id"] # Guardamos el ID para actualizar luego

        # 2. Cargamos las listas necesarias
        flag, datos_clientes, datos_vehiculos, datos_choferes = obtener_formulario()
        if (flag == False):
            self.page.open(ft.SnackBar(ft.Text(f"{datos_clientes}"),duration=1000,bgcolor=ft.Colors.RED))
            return False

        self.barra_carga.visible = False
        self.update()

        # 3. Detectamos el tipo de viaje (Propio o Tercerizado)
        # Asumimos que si tiene "chofer_id" o "patente" es Propio (0), sino Tercerizado (1)
        # O puedes usar tu variable self.modo_actual si aplica
        es_propio = True 
        if datos_viaje["tipo"] == True:
            es_propio = False

        # --- CREACIÓN DE CAMPOS ---

        # Fecha (Pre-cargada)
        try:
            fecha = datos_viaje["fecha"].strftime("%d/%m/%Y")   
        except ValueError:
            fecha = datos_viaje["fecha"]
        self.txt_fecha = ft.TextField(label="Fecha", value=str(fecha), width=400)

        # Dropdown Clientes (Pre-seleccionado)
        self.dd_cliente = ft.Dropdown(
            label="Cliente",
            value=str(datos_viaje.get("cliente_id", "")), # Selecciona el actual
            options=[ft.dropdown.Option(key=str(c["id"]), text=c["razon_social"]) for c in datos_clientes],
            width=400
        )

        self.txt_destino = ft.TextField(label="Destino", value=datos_viaje["destino"], width=400)
        self.txt_remito = ft.TextField(label="Remito/Nro Viaje", value=str(datos_viaje["numero_remito"]), width=400)
        
        # Precio (dependiendo si es propio es 'precio_pactado', si es tercero 'costo')
        precio_actual = datos_viaje.get("precio_pactado")
        self.txt_importe = ft.TextField(
            label="Importe", 
            value=str(precio_actual), 
            prefix_text="$", 
            width=400, 
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string="")
        )

        # Estado (Pre-seleccionado)
        estado_actual = "1" if datos_viaje["estado"] else "0" # Asumiendo True=Finalizado
        self.dd_estado = ft.Dropdown(
            label="Estado",
            value=estado_actual,
            options=[
                ft.dropdown.Option(key="0", text="En transito"),
                ft.dropdown.Option(key="1", text="Finalizado")
            ],
            width=400
        )

        # Lista base de campos
        lista_campos = [self.txt_fecha, self.dd_cliente, self.txt_destino, self.dd_estado, self.txt_remito, self.txt_importe]

        # --- CAMPOS ESPECÍFICOS (PROPIO VS TERCERO) ---
        if es_propio:
            # Chofer
            self.dd_chofer = ft.Dropdown(
                label="Chofer",
                value=str(datos_viaje.get("chofer_id", "")),
                options=[ft.dropdown.Option(key=str(c["id"]), text=c["nombre"]) for c in datos_choferes],
                width=400
            )
            # Vehículo
            self.dd_vehiculo = ft.Dropdown(
                label="Vehiculo",
                value=str(datos_viaje.get("vehiculo_patente", "")), # Ojo: Asegúrate si usas ID o String Patente
                options=[ft.dropdown.Option(key=str(v["patente"]), text=v["patente"]) for v in datos_vehiculos],
                width=400
            )
            self.txt_porcentaje = ft.TextField(
                label="Porcentaje %", 
                value=str(datos_viaje.get("porcentaje_chofer", "17")), 
                width=400,
                input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string="")
            )
            
            # Insertamos en el orden visual correcto
            lista_campos.insert(2, self.dd_chofer)
            lista_campos.insert(3, self.dd_vehiculo)
            lista_campos.append(self.txt_porcentaje)



        def funcion_actualizar_especifica():
            """
            Esta función 'recuerda' el id_objetivo aunque esté fuera de ella.
            """
            validar = lista_campos

            if not validar_campos_obligatorios(validar):
                return False


            if not validar_formato_fecha(self.txt_fecha):
                return False

            fecha_convertida = convertir_fecha_para_db(self.txt_fecha.value)
            # 1. Llamamos a la API de actualizar
            if (es_propio):
                print(datos_viaje)
                ret, error = actualizar_viajes(datos_viaje.get("id_viaje"), fecha_convertida, self.dd_cliente.value, self.txt_destino.value, int(self.txt_importe.value), self.dd_estado.value, self.txt_remito.value, self.txt_porcentaje.value, self.dd_chofer.value, self.dd_vehiculo.value)
            else:
                ret, error = actualizar_viajes(datos_viaje.get("id_viaje"), fecha_convertida, self.dd_cliente.value, self.txt_destino.value, int(self.txt_importe.value), self.dd_estado.value, self.txt_remito.value)

            if ret:
                self.page.open(ft.SnackBar(ft.Text(f"{error}"),duration=1000,bgcolor=ft.Colors.GREEN))
                self.generar_filas_segundo_plano() # Recargamos la grilla
                return True # Cierra modal
            else:
                self.page.open(ft.SnackBar(ft.Text(f"{error}"),duration=1000,bgcolor=ft.Colors.RED))
                self.barra_carga.visible = False
                self.update()
                return False
            
        self.mostrar_formulario(
            titulo_modal=f"Editar viaje: {datos_viaje["id_viaje"]}",
            campos_lista=lista_campos,
            funcion_guardar=funcion_actualizar_especifica
        )

    # --- C) BORRAR ---
    def abrir_borrar_viaje(self, e):

        datos = e.control.data

        def funcion_borrar_especifica():
            """
            Esta función 'recuerda' el id_objetivo aunque esté fuera de ella.
            """
            # 1. Llamamos a la API de actualizar
            ret, error = borrar_viajes(datos["id_viaje"])
            
            if ret:
                self.page.open(ft.SnackBar(ft.Text(f"{error}"),duration=1000,bgcolor=ft.Colors.GREEN))
                self.generar_filas_segundo_plano() # Recargamos la grilla
                return True # Cierra modal
            else:
                self.page.open(ft.SnackBar(ft.Text(f"{error}"),duration=1000,bgcolor=ft.Colors.RED))
                self.barra_carga.visible = False
                self.update()
                return False

        self.mostrar_confirmacion_borrar(
            item_nombre=datos["id_viaje"],
            funcion_borrar=funcion_borrar_especifica
        )

    
    def generar_filas_segundo_plano (self, e = None):
        self.barra_carga.visible = True

        self.update() # Actualizamos para que aparezca la barrita YA

        # 2. Lanzamos al "segundo empleado" a trabajar
        # target = la función que tarda mucho
        hilo = threading.Thread(target=self.generar_filas)
        hilo.start()
        # Aquí la función termina inmediatamente y la app NO se traba.


    def generar_filas(self):
        # Estos son los datos que pediste que se muestren

        if list(self.facturacion_filtro.selected)[0] == "Todos":
            facturacion_filtro = None
        else:
            facturacion_filtro = list(self.facturacion_filtro.selected)[0]

        if (self.dd_estado_filtro.value == "Todos"):
            estado_filtro = None
        else:
            estado_filtro = self.dd_estado_filtro.value

        if (self.modo_actual == "0"):
            flag, datos = obtener_todo_viajes(self.modo_actual, self.patente_seleccionada, self.txt_buscador.value, estado_filtro, facturacion_filtro)
        else:
            flag, datos = obtener_todo_viajes(self.modo_actual, None, self.txt_buscador.value, estado_filtro, facturacion_filtro)

        if (self.montado == False):
            print ("Cambio de vista")
            return
        if (flag == False):
            self.page.open(ft.SnackBar(ft.Text(f"{datos}"),duration=1000,bgcolor=ft.Colors.RED))
            self.barra_carga.visible = False
            self.update()
            return

        lista = []
        for d in datos:
            celdas = []
            if d["estado"] == False:
                estado = "En transito"
            else:
                estado = "Finalizado"

            try:
                fecha = d["fecha"].strftime("%d/%m/%Y")   
            except ValueError:
                fecha = d["fecha"]
            # Lógica diferente para armar la celda según el modo
            if (d["numero_remito"] == None):
                remito = "No cargado"
            else:
                remito = str(d["numero_remito"])
            if self.modo_actual == "0":
                celdas = [
                    ft.DataCell(ft.Text(str(d["id_viaje"]))),
                    ft.DataCell(ft.Text(str(fecha))),
                    ft.DataCell(ft.Text(str(d["nombre"]))), # Dato Chofer
                    ft.DataCell(ft.Text(str(d["vehiculo_patente"]))), # Dato Chofer
                    ft.DataCell(ft.Text(str(d["destino"]))),
                    ft.DataCell(ft.Text(str(estado))),
                    ft.DataCell(ft.Text(str(d["razon_social"]))),
                    ft.DataCell(ft.Text(remito)),
                    ft.DataCell(ft.Text(f"${d['precio_pactado']}")),
                    ft.DataCell(ft.Text(f"${d['porcentaje_chofer']}")),      # Dato Comisión
                    ft.DataCell(ft.IconButton(icon=ft.Icons.EDIT, icon_color="blue", on_click=self.abrir_editar_viaje_segundo_plano, data=d)),
                    ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE, icon_color="red", on_click=self.abrir_borrar_viaje, data=d))
                ]
            else:
                celdas = [
                    ft.DataCell(ft.Text(str(d["id_viaje"]))),
                    ft.DataCell(ft.Text(str(fecha))),
                    ft.DataCell(ft.Text(str(d["destino"]))),
                    ft.DataCell(ft.Text(str(estado))),
                    ft.DataCell(ft.Text(str(d["razon_social"]))),
                    ft.DataCell(ft.Text(remito)),
                    ft.DataCell(ft.Text(f"${d['precio_pactado']}")),        # Dato Costo
                    ft.DataCell(ft.IconButton(icon=ft.Icons.EDIT, icon_color="blue", on_click=self.abrir_editar_viaje_segundo_plano, data=d)),
                    ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE, icon_color="red", on_click=self.abrir_borrar_viaje, data=d))
                ]
            lista.append(ft.DataRow(cells=celdas))
        if (self.modo_actual == "0"):
            self.actualizar_patentes()
        if hasattr(self, 'tabla'):
            self.tabla.rows = lista
        self.barra_carga.visible = False
        if (self.page):
            self.fila_patentes.disabled = False
            self.botones_tipos.disabled = False
            self.botones_tipos.update()
            self.update()

    
    def did_mount(self):
        # Este método lo ejecuta Flet automáticamente cuando la vista
        # ya está visible en la pantalla y tiene un UID válido.
        self.montado = True
        self.barra_carga.visible = True
        self.update()
        hilo = threading.Thread(target=self.generar_filas)
        hilo.start()

    def will_unmount(self):
        # Se ejecuta cuando el usuario cambia de vista
        self.montado = False