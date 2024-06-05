from django.db import models
from reportlab.pdfgen import canvas
from django.db.models import Sum, Max
from django.utils import timezone
from datetime import date

class Producto(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    markup = models.DecimalField(max_digits=3, decimal_places=2)
    #imagen = models.ImageField(upload_to='productos/')

    def __str__(self):
        return self.nombre
    
    def stock_no_vencido(self):
        fecha_actual = timezone.now().date()
        cantidad_stock_no_vencido = Stock.objects.filter(producto=self, fecha_caducidad__gte=fecha_actual).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        return cantidad_stock_no_vencido
    
    def stock_mas_cercano_vencimiento(self):
        stock_cercano_vencimiento = Stock.objects.filter(producto=self).order_by('fecha_caducidad').first()
        return stock_cercano_vencimiento.cantidad

    def stock_total(self):
        total_comprado = Stock.objects.filter(producto=self).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        total_vendido = DetalleVenta.objects.filter(producto=self).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        return total_comprado - total_vendido
    
class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre


class Stock(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_caducidad = models.DateField(default=date(2000, 2, 8))

    
class Cliente(models.Model):
    nombre = models.CharField(max_length=200)
    email = models.EmailField()
    direccion = models.CharField(max_length=200, default='')
    latitud = models.FloatField(default=0.0)
    longitud = models.FloatField(default=0.0)

    def __str__(self):
        return self.nombre


class PuntoVenta(models.Model):
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=200, default='')
    latitud = models.FloatField(default=0.0)
    longitud = models.FloatField(default=0.0)

    def __str__(self):
        return self.nombre


class Venta(models.Model):
    id = models.AutoField(primary_key=True, default=1)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    punto_venta = models.ForeignKey(PuntoVenta, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Venta {self.id}'

    # Esta función crea un diccionario con la factura
    def crear_factura(self):
        factura = {
            'cliente': {
                'nombre': self.cliente.nombre,
                'email': self.cliente.email,
            },
            'punto_venta': {
                'nombre': self.punto_venta.nombre,
                'latitud': self.punto_venta.latitud,
                'longitud': self.punto_venta.longitud,
            },
            'fecha': self.fecha,
            'productos': [
                {
                    'nombre': detalle.producto.nombre,
                    'cantidad': detalle.cantidad,
                    'precio': detalle.producto.precio,
                    'markup': detalle.producto.markup,
                }
                for detalle in self.detalleventa_set.all()
            ],
        }

        return factura
    
    # Esta función genera un PDF con la factura
    def generar_pdf(factura):
        c = canvas.Canvas("factura.pdf")

        c.drawString(100, 750, f"Factura para: {factura['cliente']['nombre']}")
        c.drawString(100, 735, f"Email: {factura['cliente']['email']}")
        c.drawString(100, 720, f"Punto de venta: {factura['punto_venta']['nombre']}")
        c.drawString(100, 705, f"Fecha: {factura['fecha']}")

        y = 690
        for producto in factura['productos']:
            c.drawString(100, y, f"Producto: {producto['nombre']}")
            c.drawString(300, y, f"Cantidad: {producto['cantidad']}")
            c.drawString(500, y, f"Precio: {producto['precio']}")
            y -= 15

        c.save()
        # Asume que tienes un objeto venta con id=1
        #venta = Venta.objects.get(id=1)

        # Luego puedes llamar a la función crear_factura en esa instancia
        #factura = venta.crear_factura()

        # Generar el PDF
        #generar_pdf(factura)


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    cantidad = models.IntegerField()
    #fecha_caducidad = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'Detalle {self.id} de Venta {self.venta.id}'
    
    def fecha_vencimiento_mas_reciente(self):
        fecha_vencimiento = Stock.objects.filter(producto=self.producto).aggregate(Max('fecha_caducidad'))['fecha_caducidad__max']
        return fecha_vencimiento
    
    #def save(self, *args, **kwargs):
    #    self.fecha_caducidad = self.fecha_vencimiento_mas_reciente()
    #    super().save(*args, **kwargs)

class Empresa(models.Model):
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=200)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
