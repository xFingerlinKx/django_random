from django.shortcuts import render
from .models import SalesOrder
from rest_framework.viewsets import ModelViewSet

from .serializers import OrderSerializer


def orders_page(request):
    orders = SalesOrder.objects.all()
    return render(request, 'index.html', {'orders': orders})


class OrderView(ModelViewSet):
    queryset = SalesOrder.objects.all()
    serializer_class = OrderSerializer


def orders_app(request):
    return render(request, 'main_app.html')
