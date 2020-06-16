from django.urls import path
from .views import (
    item_list, 
    product_page, 
    CheckoutView, 
    HomeView,
    OrderSummaryView, 
    ItemDetailView, 
    add_to_cart, 
    remove_from_cart, 
    remove_single_from_cart,
    PaymentView
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'), 
    path('product/<slug>/', ItemDetailView.as_view(), name='product-page'), 
    path('checkout/', CheckoutView.as_view(), name='checkout-page'), 
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'), 
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_from_cart, name='remove_single_from_cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment-page')
    
]