import flet as ft
import threading

class VistaMaestraTarjetas(ft.Column):
    def __init__(self, page: ft.Page, titulo: str):
        super().__init__()
        self.page = page
        self.titulo = titulo
        self.expand = True
        
        # Variable placeholder (el hijo la define)
        self.on_click_agregar = None 
        
        # Referencias a controles principales
        self.barra_carga = None
        self.fila_tarjetas = None

    def inicializar(self):
        # 1. Barra de carga principal (de la pantalla, no del modal)
        self.barra_carga = ft.ProgressBar(width=400, color="blue", visible=False)

        # 2. Contenedor de tarjetas
        self.fila_tarjetas = ft.Row(
            wrap=True, 
            spacing=20, 
            run_spacing=20, 
            alignment=ft.MainAxisAlignment.START,
            controls=[] 
        )

        # 3. Estructura visual
        self.controls = [
            ft.Row(
                [
                    ft.Text(self.titulo, size=28, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(
                        "Nuevo", 
                        icon=ft.Icons.ADD, 
                        bgcolor=ft.Colors.BLUE, # Usar minúsculas
                        color=ft.Colors.WHITE,
                        on_click=self.on_click_agregar
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            self.barra_carga,
            ft.Divider(),
            ft.Container(
                expand=True,
                content=ft.ListView(
                    controls=[self.fila_tarjetas]
                )
            )
        ]

    # --- MÉTODOS ABSTRACTOS ---
    def generar_tarjetas(self):
        raise NotImplementedError("El hijo debe implementar esto")
    
    def generar_tarjetas_segundo_plano(self):
        raise NotImplementedError("El hijo debe implementar esto")

    # --- LÓGICA DE MODALES CON BARRA DE CARGA ---

    def mostrar_formulario(self, titulo_modal, campos_lista, funcion_guardar):
        
        # 1. Creamos la barra de carga local para este modal (oculta)
        pb_modal = ft.ProgressBar(width=400, color="orange", visible=False, height=4)
        
        # 2. Definimos los botones
        btn_cancelar = ft.TextButton("Cancelar")
        btn_guardar = ft.ElevatedButton("Guardar")

        # --- LÓGICA INTERNA DEL PROCESO DE GUARDADO ---
        
        def _hilo_guardar():
            """Esta función corre en segundo plano"""
            try:
                # Ejecutamos la función del hijo (guardar en DB)
                # Esta función debe devolver True si salió bien, False si falló
                resultado = funcion_guardar() 
                
                if resultado == False:
                    # Si falló, restauramos el modal
                    pb_modal.visible = False
                    btn_guardar.disabled = False
                    btn_cancelar.disabled = False
                    self.page.update()
                    return

                # Si salió bien (True o None), cerramos
                self.page.close(dlg)
                self.page.snack_bar = ft.SnackBar(ft.Text("¡Guardado con éxito!"), bgcolor="green")
                self.page.snack_bar.open = True
                self.page.update()
                
            except Exception as e:
                print(f"Error crítico en hilo: {e}")
                pb_modal.visible = False
                btn_guardar.disabled = False
                btn_cancelar.disabled = False
                self.page.update()

        def _click_boton_guardar(e):
            """Esto pasa al hacer clic: Bloquea UI y lanza hilo"""
            pb_modal.visible = True
            btn_guardar.disabled = True
            btn_cancelar.disabled = True
            self.page.update() # Refrescamos para ver la barra
            
            # Lanzamos el hilo
            hilo = threading.Thread(target=_hilo_guardar)
            hilo.start()

        # Asignamos las acciones a los botones
        btn_cancelar.on_click = lambda e: self.page.close(dlg)
        btn_guardar.on_click = _click_boton_guardar

        # 3. Armamos el Diálogo
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo_modal),
            content=ft.Column(
                controls=[
                    *campos_lista, # Desempaquetamos los campos
                    ft.Divider(height=10, color="transparent"),
                    pb_modal # La barra va aquí abajo
                ], 
                scroll=ft.ScrollMode.AUTO,
                tight=True, 
                width=400
            ),
            actions=[btn_cancelar, btn_guardar],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.open(dlg)

    def mostrar_confirmacion_borrar(self, item_nombre, funcion_borrar):
        pb_modal = ft.ProgressBar(width=400, color="orange", visible=False, height=4)
        btn_cancelar = ft.TextButton("Cancelar")
        btn_guardar = ft.ElevatedButton("Confirmar")

        def _borrar_y_cerrar(e):
            funcion_borrar()
            self.page.close(dlg)
            self.page.snack_bar = ft.SnackBar(ft.Text(f"{item_nombre} eliminado."))
            self.page.snack_bar.open = True
            self.page.update()

        def _hilo_borrar():
            """Esta función corre en segundo plano"""
            try:
                # Ejecutamos la función del hijo (guardar en DB)
                # Esta función debe devolver True si salió bien, False si falló
                resultado = funcion_borrar() 
                
                if resultado == False:
                    # Si falló, restauramos el modal
                    pb_modal.visible = False
                    btn_guardar.disabled = False
                    btn_cancelar.disabled = False
                    self.page.update()
                    return

                # Si salió bien (True o None), cerramos
                self.page.close(dlg)
                self.page.snack_bar = ft.SnackBar(ft.Text("¡Borrado con éxito!"), bgcolor="green")
                self.page.snack_bar.open = True
                self.page.update()
                
            except Exception as e:
                print(f"Error crítico en hilo: {e}")
                pb_modal.visible = False
                btn_guardar.disabled = False
                btn_cancelar.disabled = False
                self.page.update()

        def _click_boton_borrar (e):
            """Esto pasa al hacer clic: Bloquea UI y lanza hilo"""
            pb_modal.visible = True
            btn_guardar.disabled = True
            btn_cancelar.disabled = True
            self.page.update() # Refrescamos para ver la barra
            hilo = threading.Thread(target=_hilo_borrar)
            hilo.start()

        btn_cancelar.on_click = lambda e: self.page.close(dlg)
        btn_guardar.on_click = _click_boton_borrar

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Column(
                tight=True,
                controls=[
                    ft.Text(f"¿Estás seguro que deseas eliminar a '{item_nombre}'?"), # Desempaquetamos los campos
                    ft.Divider(height=10, color="transparent"),
                    pb_modal # La barra va aquí abajo
                ]), 
            actions=[
                btn_guardar,
                btn_cancelar
            ],
        )
        self.page.open(dlg)