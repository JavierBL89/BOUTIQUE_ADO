from django.shortcuts import (
    render, redirect, reverse, get_object_or_404, HttpResponse
)
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
#### 12. POINT 12 LESSON STRIPE 4 on notebook
### AND 6. POINT 1 CHECKOUT SUCCESS, LESSON STRIPE 6
from .forms import OrderForm
from .models import Order, OrderLineItem
### 7. POINT 7 PROFILE 8, LESSON PROFILES on notebook
from profiles.forms import UserProfileForm
from profiles.models import UserProfile

from products.models import Product
# from profiles.models import UserProfile
# from profiles.forms import UserProfileForm
from bag.contexts import bag_contents

# import stripe
import json
import stripe

### 3.1. POINT 3.1 LESSON STRIPE 14 on notebook
@require_POST
def cache_checkout_data(request):
    try:
        ### 3.3. POINT 3.3 LESSON STRIPE 14 on notebook
        pid = request.POST.get('client_secret').split('_secret')[0]
        ### 3.4. POINT 3.4 LESSON STRIPE 14 on notebook
        stripe.api_key = settings.STRIPE_SECRET_KEY
        ### 3.5 POINT 3.5 LESSON STRIPE 14 on notebook
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        ### 4. POINT 4 LESSON STRIPE 14 on notebook
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, ('Sorry, your payment cannot be '
                                 'processed right now. Please try '
                                 'again later.'))
        return HttpResponse(content=e, status=400)

def checkout(request):
    #### 1. POINT 1 LESSON STRIPE 4 on notebook
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    # 1. POINT 1 LESSON STRIPE 6 on the notebooke
    if request.method == 'POST':
        # 2. POINT 2 LESSON STRIPE 6 on the notebooke
        bag = request.session.get('bag', {})
        # 3. POINT 3 LESSON STRIPE 6 on the notebooke
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        # 4. POINT 4 LESSON STRIPE 6 on the notebooke
        order_form = OrderForm(form_data)
        # 5. POINT 5 LESSON STRIPE 6 on the notebooke
        if order_form.is_valid():
                                   ## ### 9. POINT 9 STRIPE LESSON 16 on notebook
            order = order_form.save(commit=False)
            ## ### 9. POINT 9 STRIPE LESSON 16 on notebook
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            # 5. POINT 5 LESSON STRIPE 6 on the notebook
            order.save()
            # 6. POINT 1 LESSON STRIPE 6 on the notebook
            for item_id, item_data in bag.items():
                try:
                    # 7 . POINT 7 LESSON STRIPE 6 on the notebooke
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        # 8. POINT 8 LESSON STRIPE 6 on the notebooke
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                # 9. POINT 9 LESSON STRIPE 6 on the notebooke
                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your bag wasn't "
                        "found in our database. "
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))
                    
            # 10. POINT 10 LESSON STRIPE 6 on the notebooke
            # Save the info to the user's profile if all is well
            request.session['save_info'] = 'save-info' in request.POST
            return redirect(reverse('checkout_success',
                                    args=[order.order_number]))
        # 11. POINT 11 LESSON STRIPE 6 on the notebooke
        else:
            messages.error(request, ('There was an error with your form. '
                                     'Please double check your information.'))
    else:
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(request,
                           "There's nothing in your bag at the moment")
            return redirect(reverse('products'))

        current_bag = bag_contents(request)
        total = current_bag['grand_total']
        stripe_total = round(total * 100)
        #### 2. POINT 2 LESSON STRIPE 4 on notebook
        stripe.api_key = stripe_secret_key
        #### 3. POINT 3 LESSON STRIPE 4 on notebook
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        #### 8.1.1 POINT 8.1.1 LESSON PROFILES 8 on notebook
             # Attempt to prefill the form with any info
             # the user maintains in their profile
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(initial={
                    'full_name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                    'country': profile.default_country,
                    'postcode': profile.default_postcode,
                    'town_or_city': profile.default_town_or_city,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'county': profile.default_county,
                })
            #### 8.2.2 POINT 8.2.2 LESSON PROFILES 8 on notebook
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        #### 8.2.2 POINT 8.2.2 LESSON PROFILES 8 on notebook
        else:
            order_form = OrderForm()
    #### 5. POINT 5 LESSON STRIPE 4 on notebook
    if not stripe_public_key:
        messages.warning(request, ('Stripe public key is missing. '
                                   'Did you forget to set it in '
                                   'your environment?'))

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        #### 4. POINT 4 LESSON STRIPE 4 on notebook
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)

#### CREATE CHECKOUT_SUCCESS VIEW, LESSON STRIPE 6, on the notebook
def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    ### 1. POINT 1 CHECKOUT SUCCESS, LESSON STRIPE 6 
    save_info = request.session.get('save_info')
    ### 2. POINT 2 CHECKOUT SUCCESS, LESSON STRIPE 6
    order = get_object_or_404(Order, order_number=order_number)
    
    ### ##### 1. POINT 1 PROFILE 8, LESSON PROFILES on notebook
    if request.user.is_authenticated:
        ### 2. POINT 2 PROFILE 8, LESSON PROFILES on notebook
        profile = UserProfile.objects.get(user=request.user)
        
        ### 3. POINT 3 PROFILE 8, LESSON PROFILES on notebook
           # Attach the user's profile to the order
        order.user_profile = profile
        ### 4. POINT 4 PROFILE 8, LESSON PROFILES on notebook
        order.save()

        ### 5. POINT 5 PROFILE 8, LESSON PROFILES on notebook
        # Save the user's info
        if save_info:
            profile_data = {
                'default_phone_number': order.phone_number,
                'default_country': order.country,
                'default_postcode': order.postcode,
                'default_town_or_city': order.town_or_city,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_county': order.county,
            }
            ### 6. POINT 6 PROFILE 8, LESSON PROFILES on notebook
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()
    ### 3. POINT 3 CHECKOUT SUCCESS, LESSON STRIPE 6
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')
    ### 4. POINT 4 CHECKOUT SUCCESS, LESSON STRIPE 6
    if 'bag' in request.session:
        del request.session['bag']
    ### 5. POINT 5 CHECKOUT SUCCESS, LESSON STRIPE 6
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)