from django import forms
from django.forms import formset_factory
from .models import Producto, Stock, Cliente, DetalleVenta, Venta

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'cantidad', 'precio', 'markup']

class AgregarCantidadForm(forms.Form):
    cantidad = forms.IntegerField()

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['producto', 'proveedor','cantidad', 'precio_compra', 'fecha_caducidad']

    def __init__(self, *args, **kwargs):
        producto_id = kwargs.pop('producto_id', None)
        super(StockForm, self).__init__(*args, **kwargs)
        if producto_id:
            self.fields['producto'].initial = Producto.objects.get(id=producto_id)

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'email', 'direccion']

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'precio']  # Reemplaza 'producto', 'cantidad' con los campos de tu modelo DetalleVenta