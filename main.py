import flet as ft
from vistaVehiculos import VistaCamiones
from vistaClientes import VistaClientes
from vistaChoferes import VistaChoferes
from vistaViajes import VistaViajes
from vistaFacturas import VistaFacturas
def main (page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT

    page.title = "Gestión transporte"
    page.window.width = 1100      # Ancho deseado
    page.window.height = 700      # Alto deseado
    
    page.window_min_width = 800
    page.window_min_height = 600
    
    page.window_maximized = True 

    page.window.center()
    page.update()

    view_choferes = VistaChoferes(page)
    view_vehiculos = VistaCamiones(page)
    view_clientes = VistaClientes(page)
    view_viajes = VistaViajes(page)
    view_facturas = VistaFacturas(page)
    view_dashboard = None

    area_contenido = ft.Container(
        content=view_dashboard, 
        expand=True, 
        padding=30,
        bgcolor=ft.Colors.GREY_100 
    )

    def cambiar_ruta(e):
        idx = e.control.selected_index
        if idx == 0:
            area_contenido.content = None

        elif idx == 1:
            area_contenido.content = view_viajes

        elif idx == 2:
            area_contenido.content = view_facturas

        elif idx == 3:
            area_contenido.content = view_choferes
        
        elif idx == 4:
            area_contenido.content = view_vehiculos

        elif idx == 5:
            area_contenido.content = view_clientes
        
        area_contenido.update()
        



    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=400,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Inicio"),
            ft.NavigationRailDestination(icon=ft.Icons.MAP_OUTLINED, selected_icon=ft.Icons.MAP, label="Viajes"),
            ft.NavigationRailDestination(icon=ft.Icons.POINT_OF_SALE_OUTLINED, selected_icon=ft.Icons.POINT_OF_SALE, label="Facturas"),
            ft.NavigationRailDestination(icon=ft.Icons.PEOPLE_OUTLINE, selected_icon=ft.Icons.PEOPLE, label="Choferes"),
            ft.NavigationRailDestination(icon=ft.Icons.DIRECTIONS_CAR_OUTLINED, selected_icon=ft.Icons.DIRECTIONS_CAR_FILLED, label="Vehiculos"),
            ft.NavigationRailDestination(icon=ft.Icons.BUSINESS_OUTLINED, selected_icon=ft.Icons.BUSINESS, label="Clientes"),
        ],
        on_change=cambiar_ruta,
        bgcolor=ft.Colors.BLUE_GREY_50, # CORREGIDO: Color seguro
    )

    layout = ft.Row(
        [
            rail,
            ft.VerticalDivider(width=1, color=ft.Colors.GREY_300),
            area_contenido
        ],
        expand=True,
    )


    page.add (layout)

ft.app(target=main)