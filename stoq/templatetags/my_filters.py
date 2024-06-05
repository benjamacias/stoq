from django import template
import decimal
from stoq.models import Stock, Venta, DetalleVenta

register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def get_fecha_caducidad(producto):
    total_stock = 0
    stock = Stock.objects.filter(producto=producto).order_by('fecha_caducidad').first()
    return stock.fecha_caducidad if stock else None

@register.filter
def get_precio_compra(producto):
    stock = Stock.objects.filter(producto=producto).order_by('-fecha_ingreso').first()
    return stock.precio_compra if stock else None

@register.filter
def stock_total(producto):
    stock = Stock.objects.filter(producto=producto)
    return sum([s.cantidad for s in stock])

@register.filter
def get_valor_total(total):
    v=0
    Venta = DetalleVenta.objects.filter(venta=total)
    return sum([v + s.precio * s.cantidad for s in Venta])

