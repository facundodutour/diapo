import flet as ft

# --- DATOS SIMULADOS (MOCK DATA) ---
DATOS_PAGOS = [
    {"vencimiento": "10/12/2025", "categoria": "Seguros", "proveedor": "La Segunda", "detalle": "Póliza Flota", "importe": 150000, "estado": "Vencida"},
    {"vencimiento": "15/12/2025", "categoria": "Combustible", "proveedor": "YPF Ruta", "detalle": "Carga AA-123-BB", "importe": 85400, "estado": "Pendiente"},
    {"vencimiento": "20/12/2025", "categoria": "Mantenimiento", "proveedor": "Taller El Tuerca", "detalle": "Frenos", "importe": 45000, "estado": "Lejano"},
]

DATOS_CAJA = [
    {"fecha": "12/12/2025", "concepto": "Cobro Factura #1456", "cat": "Ingreso", "ingreso": 250000, "egreso": 0, "saldo": 1250000},
    {"fecha": "12/12/2025", "concepto": "Pago Combustible", "cat": "Gasto", "ingreso": 0, "egreso": 45000, "saldo": 1205000},
    {"fecha": "11/12/2025", "concepto": "Adelanto Chofer", "cat": "Sueldos", "ingreso": 0, "egreso": 20000, "saldo": 1225000},
]

class GestionFinancieraApp(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = True # Para que ocupe toda la pantalla
        
        # --- FUNCIÓN HELPER PARA TARJETAS (KPIs) ---
        # Esta función crea las tarjetitas de colores con iconos
        def crear_kpi(titulo, valor, color_texto, icono, color_fondo=ft.Colors.WHITE):
            return ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(icono, color=color_texto, size=30),
                        bgcolor=ft.Colors.with_opacity(0.1, color_texto),
                        padding=10,
                        border_radius=10
                    ),
                    ft.Column([
                        ft.Text(titulo, size=12, color=ft.Colors.GREY_600, weight="bold"),
                        ft.Text(valor, size=20, weight="bold", color=ft.Colors.BLACK)
                    ], spacing=2)
                ], alignment=ft.MainAxisAlignment.START),
                bgcolor=color_fondo,
                padding=15,
                border_radius=10,
                border=ft.border.all(1, ft.Colors.GREY_200),
                expand=True # Importante para que se distribuyan igual
            )

        # =================================================================
        # MÓDULO 5: PAGOS (CUENTAS A PAGAR)
        # =================================================================
        
        # 1. KPIs Superiores
        kpis_pagos = ft.Row([
            crear_kpi("Total a Pagar", "$ 720.400", ft.Colors.BLUE_GREY, ft.Icons.MONEY_OFF),
            crear_kpi("Vencido (Urgente)", "$ 150.000", ft.Colors.RED, ft.Icons.WARNING),
            crear_kpi("Vence esta semana", "$ 130.400", ft.Colors.ORANGE, ft.Icons.CALENDAR_MONTH),
        ], spacing=20)

        # 2. Barra de Herramientas
        barra_pagos = ft.Row([
            ft.ElevatedButton("Nuevo Gasto", icon=ft.Icons.ADD, bgcolor=ft.Colors.BLUE, color="white"),
            ft.Dropdown(
                width=200, 
                label="Filtrar por Categoría", 
                options=[ft.dropdown.Option("Todas"), ft.dropdown.Option("Combustible")],
                content_padding=10,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # 3. Tabla de Pagos
        filas_pagos = []
        for p in DATOS_PAGOS:
            # Lógica de colores para el estado
            if p["estado"] == "Vencida":
                bg_estado = ft.Colors.RED_50
                color_estado = ft.Colors.RED
                icono = ft.Icons.WARNING
            elif p["estado"] == "Pendiente":
                bg_estado = ft.Colors.ORANGE_50
                color_estado = ft.Colors.ORANGE
                icono = ft.Icons.ACCESS_TIME
            else:
                bg_estado = ft.Colors.GREEN_50
                color_estado = ft.Colors.GREEN
                icono = ft.Icons.CHECK

            # Construcción de la fila
            filas_pagos.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(p["vencimiento"])),
                ft.DataCell(ft.Text(p["categoria"])),
                ft.DataCell(ft.Column([
                    ft.Text(p["proveedor"], weight="bold"),
                    ft.Text(p["detalle"], size=12, italic=True, color="grey")
                ], spacing=0)),
                ft.DataCell(ft.Text(f"$ {p['importe']:,.0f}")),
                ft.DataCell(ft.Container(
                    content=ft.Row([ft.Icon(icono, size=14, color=color_estado), ft.Text(p["estado"], color=color_estado)], spacing=5),
                    bgcolor=bg_estado, padding=5, border_radius=5
                )),
                ft.DataCell(ft.IconButton(ft.Icons.PAYMENT, icon_color="green", tooltip="Pagar"))
            ]))

        tabla_pagos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Vence")),
                ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Proveedor / Detalle")),
                ft.DataColumn(ft.Text("Importe"), numeric=True),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acción")),
            ],
            rows=filas_pagos,
            heading_row_color=ft.Colors.GREY_100,
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, "grey"),
            expand=True # Para que ocupe espacio horizontal
        )

        # Contenedor final de la pestaña PAGOS
        tab_pagos_content = ft.Container(
            content=ft.Column([
                kpis_pagos,
                ft.Divider(color="transparent", height=10),
                barra_pagos,
                ft.Divider(color="transparent", height=10),
                tabla_pagos
            ], scroll=ft.ScrollMode.AUTO),
            padding=20
        )

        # =================================================================
        # MÓDULO 6: CAJA (TESORERÍA)
        # =================================================================
        
        # 1. Cabecera con Saldo Gigante
        header_caja = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text("SALDO ACTUAL EN CAJA", color="white", size=12),
                    ft.Text("$ 1.250.000", color="white", size=30, weight="bold"),
                    ft.Row([ft.Icon(ft.Icons.TRENDING_UP, color="green"), ft.Text("+5% vs Ayer", color="green")])
                ]),
                bgcolor=ft.Colors.BLUE_GREY_900,
                padding=20, border_radius=10, expand=2
            ),
            crear_kpi("Ingresos Hoy", "$ 350.000", ft.Colors.GREEN, ft.Icons.ARROW_DOWNWARD),
            crear_kpi("Egresos Hoy", "$ 65.000", ft.Colors.RED, ft.Icons.ARROW_UPWARD),
        ], spacing=20)

        # 2. Tabla de Movimientos
        filas_caja = []
        for c in DATOS_CAJA:
            # Formato condicional colores
            txt_ingreso = ft.Text(f"$ {c['ingreso']:,.0f}", color="green", weight="bold") if c['ingreso'] > 0 else ft.Text("-")
            txt_egreso = ft.Text(f"$ {c['egreso']:,.0f}", color="red", weight="bold") if c['egreso'] > 0 else ft.Text("-")

            filas_caja.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(c["fecha"])),
                ft.DataCell(ft.Column([ft.Text(c["concepto"], weight="bold"), ft.Text(c["cat"], size=12, color="grey")], spacing=0)),
                ft.DataCell(txt_ingreso),
                ft.DataCell(txt_egreso),
                ft.DataCell(ft.Text(f"$ {c['saldo']:,.0f}", weight="bold")),
            ]))

        tabla_caja = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Concepto")),
                ft.DataColumn(ft.Text("Ingreso"), numeric=True),
                ft.DataColumn(ft.Text("Egreso"), numeric=True),
                ft.DataColumn(ft.Text("Saldo Parcial"), numeric=True),
            ],
            rows=filas_caja,
            heading_row_color=ft.Colors.GREY_100,
            expand=True
        )

        # Contenedor final de la pestaña CAJA
        tab_caja_content = ft.Container(
            content=ft.Column([
                header_caja,
                ft.Divider(color="transparent", height=20),
                ft.Text("Movimientos Recientes", size=20, weight="bold"),
                tabla_caja
            ], scroll=ft.ScrollMode.AUTO),
            padding=20
        )

        # =================================================================
        # ARMADO DE TABS PRINCIPALES
        # =================================================================
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Cuentas a Pagar",
                    icon=ft.Icons.MONEY_OFF,
                    content=tab_pagos_content
                ),
                ft.Tab(
                    text="Caja y Tesorería",
                    icon=ft.Icons.ACCOUNT_BALANCE_WALLET,
                    content=tab_caja_content
                ),
            ],
            expand=True
        )

        # AQUI AGREGAMOS LOS TABS A LA LISTA DE CONTROLES PRINCIPALES
        self.controls = [self.tabs]

# --- BLOQUE PARA EJECUTAR ---
def main(page: ft.Page):
    page.title = "Finanzas Servientrega"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    app = GestionFinancieraApp()
    page.add(app)

if __name__ == "__main__":
    ft.app(target=main)