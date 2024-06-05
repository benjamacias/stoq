from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from decimal import Decimal, InvalidOperation
from django.http import HttpResponse, JsonResponse
from django.db.models.functions import TruncMonth
from .models import Producto, Cliente
from .forms import ProductoForm
from .forms import AgregarCantidadForm
from .forms import StockForm
from .forms import ClienteForm
from .forms import DetalleVentaForm
from django.urls import reverse

from .models import Venta, Stock
from django.forms import formset_factory
from django.db.models import Sum, Max, F
import requests


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse("Logged in successfully")
        else:
            return HttpResponse("Invalid username or password")
    else:
        # Render the login form
        return render(request, 'login.html')


def productos_view(request):
    q = request.GET.get('q', '')
    productos = Producto.objects.filter(nombre__icontains=q)
    return render(request, 'productos.html', {'productos': productos})


def agregar_producto_view(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('productos')
            except Exception:
                form.add_error('nombre', 'Un producto con este nombre ya existe.')
    else:
        form = ProductoForm()
    return render(request, 'agregar_producto.html', {'form': form})


def agregar_cantidad_view(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = AgregarCantidadForm(request.POST)
        if form.is_valid():
            cantidad = form.cleaned_data.get('cantidad')
            producto.cantidad += cantidad
            producto.save()
            return redirect('stock_producto')
    else:
        form = AgregarCantidadForm()
    return render(request, 'agregar_cantidad.html', {'form': form})


def crear_stock(request, pk=None):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('stock_producto', pk=pk)
    if pk is not None:
        form = StockForm(producto_id=pk)
    else:
        form = StockForm()
    return render(request, 'agregar_stock.html', {'form': form})


def stock_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    stocks = producto.stock_set.all()
    return render(request, 'stock_producto.html', {'producto': producto, 'stocks': stocks})


#def lista_clientes(request, pk=None):
    clientes = Cliente.objects.all()
    cliente = get_object_or_404(Cliente, pk=pk) if pk else None
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente) if cliente else ClienteForm()
    return render(request, 'clientes.html', {'clientes': clientes, 'form': form})

def lista_clientes(request, pk=None):
    clientes = Cliente.objects.all()
    cliente = get_object_or_404(Cliente, pk=pk) if pk else None
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save(commit=False)
            direccion = form.cleaned_data['direccion']
            response = requests.get('https://maps.googleapis.com/maps/api/geocode/json', params={'address': direccion, 'key': 'AIzaSyDO_INEjUhy0ydbvip__M8d8mrdU5UOyVg'})
            geodata = response.json()
            if geodata['results']:
                cliente.latitud = geodata['results'][0]['geometry']['location']['lat']
                cliente.longitud = geodata['results'][0]['geometry']['location']['lng']
            cliente.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente) if cliente else ClienteForm()
    return render(request, 'clientes.html', {'clientes': clientes, 'form': form})

from django.shortcuts import render
from .models import Venta

def vista_venta(request, pk=None):
    if pk is not None:
        venta = get_object_or_404(Venta, id=pk)
        detalles = venta.detalles.all()
        #detalles_list = detalles.objects.filter(venta=venta)
        paginator = Paginator(detalles, 4) # Muestra 4 detalles por página

        page_number = request.GET.get('page')
        detalles = paginator.get_page(page_number)

        #total = detalles.annotate(total=F('precio') * F('cantidad')).aggregate(total=Sum('total'))['total']
        total = sum(detalle.precio * detalle.cantidad for detalle in detalles)
        if request.method == 'POST':
            form = DetalleVentaForm(request.POST)
            if form.is_valid():
                detalle_venta = form.save(commit=False)
                detalle_venta.venta = venta
                detalle_venta.save()
                return redirect('vista_venta', pk=venta.id)
        else:
            form = DetalleVentaForm()
        return render(request, 'ventas.html', {'venta': venta, 'detalles': detalles, 'form': form, 'total': total})
    else:
        ventas = Venta.objects.all()
        return render(request, 'lista_ventas.html', {'ventas': ventas})

def lista_ventas(request):
    ventas = Venta.objects.all()
    return render(request, 'lista_ventas.html', {'ventas': ventas})

# Para vista venta, compare este snippet de byzcount/stoq/templates/ventas.html:
def get_precio_producto(request):
    producto_id = request.GET.get('producto_id')
    if producto_id is not None:
        try:
            producto = Producto.objects.get(id=producto_id)
            return JsonResponse({'precio': producto.precio})
        except Producto.DoesNotExist:
            pass
    return JsonResponse({'precio': None})

def actualizar_precio(request, pk):
    producto = Producto.objects.get(id=pk)
    if request.method == 'POST':
        try:
            nuevo_precio = Decimal(request.POST.get('nuevo_precio'))
        except InvalidOperation:
            return HttpResponse('Error: El valor ingresado no es un número válido.', status=400)

        producto.precio = nuevo_precio
        producto.save()
        return redirect('productos')
    else:
        return render(request, 'actualizar_precio.html', {'producto': producto})
    
def actualizar_markup(request, pk):
    producto = Producto.objects.get(id=pk)
    if request.method == 'POST':
        try:
            nuevo_markup = Decimal(request.POST.get('nuevo_markup'))
        except InvalidOperation:
            return HttpResponse('Error: El valor ingresado no es un número válido.', status=400)

        if nuevo_markup > 9.0:
            return HttpResponse('Error: El markup no puede ser mayor que 9.0.', status=400)

        producto.markup = nuevo_markup
        producto.save()
        return redirect('productos')
    else:
        return render(request, 'actualizar_markup.html', {'producto': producto})
    
def nueva_cantidad(request, pk):
    producto = Producto.objects.get(id=pk)
    if request.method == 'POST':
        try:
            nueva_cantidad = Decimal(request.POST.get('nueva_cantidad'))
        except InvalidOperation:
            return HttpResponse('Error: El valor ingresado no es un número válido.', status=400)

        if nueva_cantidad < -0.1:
            return HttpResponse('Error: La cantidad minima es 0', status=400)

        producto.cantidad = nueva_cantidad
        producto.save()
        return redirect('productos')
    else:
        return render(request, 'actualizar_markup.html', {'producto': producto})

def estadisticas_view(request):
    # Agrupar los stocks por producto y mes, sumar la cantidad y obtener el precio de compra máximo
    stats = Stock.objects.annotate(
        mes=TruncMonth('fecha_ingreso')  # Extrae el mes de la fecha
    ).values('producto__nombre', 'mes').annotate(
        total_comprado=Sum('cantidad'),
        max_precio_compra=Max('precio_compra')  # Obtiene el precio de compra máximo
    ).order_by('producto__nombre', 'mes')

    # Convertir el resultado en un diccionario anidado
    stats_dict = {}
    for item in stats:
        producto = item['producto__nombre']
        mes = item['mes'].strftime('%Y-%m')  # Formatea la fecha como 'YYYY-MM'
        cantidad = item['total_comprado']
        max_precio_compra = item['max_precio_compra']
        if producto not in stats_dict:
            stats_dict[producto] = {}
        stats_dict[producto][mes] = {'cantidad': cantidad, 'max_precio_compra': max_precio_compra}
    # Renderizar la plantilla con las estadísticas
    return render(request, 'inicio.html', {'estadisticas': stats_dict})