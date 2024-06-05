"""
URL configuration for byzcount project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from stoq import views
from stoq.views import vista_venta, get_precio_producto, lista_ventas, actualizar_precio, actualizar_markup, nueva_cantidad, estadisticas_view




urlpatterns = [
    path('admin/', admin.site.urls),
    path('', estadisticas_view, name='estadisticas'),
    #path('login/', views.login_view, name='login'),
    path('productos/', views.productos_view, name='productos'),
    path('agregar_producto/', views.agregar_producto_view, name='agregar_producto'),
    path('agregar_cantidad/<int:pk>/', views.agregar_cantidad_view, name='agregar_cantidad'),
    #path('agregar_stock/', views.crear_stock, name='agregar_stock'),
    path('stock_producto/<int:pk>/', views.stock_producto, name='stock_producto'),
    re_path(r'agregar_stock/(?P<pk>\d+)?', views.crear_stock, name='agregar_stock'),#esto es para que se pueda agregar stock a un producto
    re_path(r'clientes/(?P<pk>\d+)?', views.lista_clientes, name='lista_clientes'),
    re_path(r'vista_venta/(?P<pk>\d+)?', views.vista_venta, name='vista_venta'),
    path('get_precio_producto/', get_precio_producto, name='get_precio_producto'),
    path('lista_ventas/', lista_ventas, name='lista_ventas'),
    path('actualizar_precio/<int:pk>', actualizar_precio, name='actualizar_precio'),
    path('actualizar_markup/<int:pk>', actualizar_markup, name='actualizar_markup'),
    path('actualizar_markup/<int:pk>', actualizar_markup, name='actualizar_markup'),
    path('nueva_cantidad/<int:pk>', views.nueva_cantidad, name='nueva_cantidad'),

]

