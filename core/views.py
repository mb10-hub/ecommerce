from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Item, Order, OrderItem
from django.utils import timezone

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

def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user = request.user, 
        ordered = False
        )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        #check if the order is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
        else:
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date = ordered_date)
        order.items.add(order_item)
    return redirect("core:product-page", slug=slug)
       