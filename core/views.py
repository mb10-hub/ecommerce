from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from .models import Item, Order, OrderItem, Address, Payment, Coupon, Refund
from .forms import CheckoutForm, CouponForm, RefundForm
from django.utils import timezone

import random
import string
import stripe
stripe.api_key = settings.STRIPE_PUBLIC_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits,k=20 ))



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


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form, 
                'couponform': CouponForm(),
                'order': order, 
                'DISPLAY_COUPON__FORM': True

            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user, 
                address_type='S', 
                default=True
            )
            if shipping_address_qs.exists():
                context.update({'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user, 
                address_type='B', 
                default=True
            )
            if billing_address_qs.exists():
                context.update({'default_billing_address': billing_address_qs[0]})

            return render(self.request, "checkout-page.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")

    
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            if form.is_valid(): 

                use_default_shipping = form.cleaned_data.get('use_default_shipping')
                if use_default_shipping:
                    print("Using the default shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user, 
                        address_type='S', 
                        default=True
                   )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(self.request, "No default shipping address availiable") 
                        return redirect('core:checkout-page')
                
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get('shipping_address')  
                    shipping_address2 = form.cleaned_data.get('shipping_address2')
                    shipping_country = form.cleaned_data.get('shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')
                    # TODO: add functionality to the commented out
                    # same_shipping_address = form.cleaned_data.get('same_billing_address')
                    # save_info = form.cleaned_data.get('save_info')


                    if is_valid_form([shipping_address1,shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user = self.request.user,
                            street_address = shipping_address1,
                            apartment_address = shipping_address2,
                            country = shipping_country,
                            zip = shipping_zip,
                            address_type = 'S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get('set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()


                    else:
                        messages.info(self.request, "Please fill in the required shipping fields.")



                use_default_billing = form.cleaned_data.get('use_default_billing')
                same_billing_address = form.cleaned_data.get('same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()



                elif use_default_billing:
                    print("Using the default billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user, 
                        address_type='B', 
                        default=True
                   )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(self.request, "No default billing address availiable") 
                        return redirect('core:checkout-page')
                
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get('billing_address')  
                    billing_address2 = form.cleaned_data.get('billing_address2')
                    billing_country = form.cleaned_data.get('billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')
                    # TODO: add functionality to the commented out
                    # same_shipping_address = form.cleaned_data.get('same_billing_address')
                    # save_info = form.cleaned_data.get('save_info')


                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user = self.request.user,
                            street_address = billing_address1,
                            apartment_address = billing_address2,
                            country = billing_country,
                            zip = billing_zip,
                            address_type = 'B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get('set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()


                    else:
                        messages.info(self.request, "Please fill in the required billing fields.")

                payment_option = form.cleaned_data.get('payment_option')

                #TODO: add redirect to the selected payment option 
                if payment_option == 'S':
                    return redirect('core:payment-page', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment-page', payment_option='paypal')
                else:     
                    messages.warning(self.request, "Invalid payment option choose another.")
                    return redirect('core:checkout-page')

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        #order
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:

            context = {
                'order':order ,
                'DISPLAY_COUPON__FORM': False
            }
            return render(self.request, "payment-page.html", context)

        else:
            messages.warning(self.request, "You do not have a billing address")
            return redirect("core:checkout-page")

    
    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100) # convert from cents

        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token
            )

            #create payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            #assign the payment with the order
            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()


            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            messages.success(self.request, "Your order was successful!")
            return redirect("/")
            
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")


        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            print('Status is: %s' % e.http_status)
            print('Type is: %s' % e.error.type)
            print('Code is: %s' % e.error.code)
            # param is '' in this case
            print('Param is: %s' % e.error.param)
            print('Message is: %s' % e.error.message)
            messages.error(self.request, "Not Authenticated")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Network error")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")

        except Exception as e:
            # send email to ourselfs
            messages.error(self.request, "serious error has occurred. We have been notified.")
            return redirect("/")


        # messages.warning(self.request, "Invalid data received")
        # return redirect("/payment/stripe/")







class HomeView(ListView):
    model = Item
    # PRODUCTS PER PAGE
    paginate_by =  10
    # ORDERS IN DECENDING ORDER
    ordering = ['-id']
    template_name = "home-page.html"

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order-summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")



class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"

@login_required
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
            messages.info(request, "This item quantity updated in your cart.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date = ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")
       
@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        #check if the order is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item, 
                user = request.user, 
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed to your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("core:product-page", slug=slug)
    else:
        messages.info(request, "You dont have an active order.")
        return redirect("core:product-page", slug=slug)

@login_required
def remove_single_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        #check if the order is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item, 
                user = request.user, 
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -=1
                order_item.save()
            else:
                order.items.remove(order_item)

            messages.info(request, "This item quantity was updated in your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("core:product-page", slug=slug)
    else:
        messages.info(request, "You dont have an active order.")
        return redirect("core:product-page", slug=slug)

def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout-page")


class AddCouponView(View):

    def post(self, *args, **kwargs):
        form = CouponForm(request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added this coupon")
                return redirect("core:checkout-page")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")

class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request-refund.html", context)


    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get(('ref_code'))
            message = form.cleaned_data.get(('message'))
            email = form.cleaned_data.get(('email'))

            #edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_request = True
                order.save()

                #store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")