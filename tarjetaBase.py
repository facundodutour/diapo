import flet as ft

class TarjetaBase(ft.Card):
    def __init__(
        self, 
        titulo: str, 
        subtitulo: str, 
        icono: str, 
        color_estado: str = ft.Colors.BLUE, 
        texto_estado: str = "",
        contenido_extra: ft.Control = None, # <--- NUEVO PARÁMETRO (Opcional)
        on_editar=None, 
        on_borrar=None
    ):
        super().__init__()
        self.elevation = 5
        self.surface_tint_color = ft.Colors.WHITE

        # 1. Preparamos la lista de cosas que van dentro de la tarjeta
        elementos_columna = [
            ft.ListTile(
                leading=ft.Icon(icono, size=40, color=color_estado),
                title=ft.Text(titulo, weight="bold", size=16, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, tooltip=titulo),
                subtitle=ft.Column([
                    ft.Text(subtitulo, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, tooltip=subtitulo),
                    ft.Text(texto_estado, color=color_estado, size=12, weight="bold")
                ]),
            )
        ]

        # 2. SI HAY CONTENIDO EXTRA, LO AGREGAMOS AQUÍ
        if contenido_extra is not None:
            elementos_columna.append(ft.Divider(height=10, color="transparent")) # Un separador invisible
            elementos_columna.append(contenido_extra)

        # 3. Agregamos la línea divisoria y los botones al final
        elementos_columna.append(ft.Divider())
        elementos_columna.append(
             ft.Row(
                [
                    ft.TextButton("Eliminar", icon=ft.Icons.DELETE, icon_color="red", on_click=on_borrar),
                    ft.ElevatedButton("Editar", icon=ft.Icons.EDIT, on_click=on_editar)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )

        # 4. Armamos el contenedor final
        self.content = ft.Container(
            width=300,
            padding=10,
            border=ft.border.all(2, color_estado),
            border_radius=10,
            content=ft.Column(elementos_columna) # Le pasamos la lista dinámica
        )