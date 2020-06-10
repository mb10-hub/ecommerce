from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Item

def item_list(request):
    context = {
        'items':Item.objects.all()

    }


    return render(request, "home-page.html", context)

def product_page(request):
    context = {
        'items':Item.objects.all()
    }
    return render(request, "product-page.html", context)

def checkout_page(request):
    context = {}
    return render(request, "checkout-page.html", context)

class HomeView(ListView):
    model = Item
    template_name = "home-page.html"

class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"