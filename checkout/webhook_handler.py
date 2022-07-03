### 2. POINT 2 ON STRIPE 10 LESSON on notebook
from django.http import HttpResponse
from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

import time
import json

##### 3. POINT 3 ON STRIPE 10 LESSON on notebook
class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request
    
    #### 2. POITN 2 ON PROFILE LESSON 10 on notebook
    def _send_confirmation_email(self, order):
        #### 4. POITN 4 ON PROFILE LESSON 10 on notebook
        cust_email = order.email

        #### 5. POITN 5 ON PROFILE LESSON 10 on notebook
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order})
        
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})
        
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )

    # 4. POITN 4 ON STRIPE 11 LESSON on notebook
    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    # 1. POITN I ON STRIPE 11 LESSON on notebook
    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        intent = event.data.object
        ## 1. POINT 1 STRIPE LESSON 15 on notebook
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info
        ### 2. POINT 2 STRIPE LESSON 15 on notebook
        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount / 100, 2)
        
        ### 3. POINT 3 STRIPE LESSON 15 on notebook
        # Clean data in the shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None
            
        ## ##### 1. PONT 1 PROFILE LESSON 9 on notebook
        profile = None
        ## ##### 2. PONT 2 PROFILE LESSON 9 on notebook
        username = intent.metadata.username
        if username != 'AnonymousUser':
            ## ##### 3. PONT 3 PROFILE LESSON 9 on notebook
            profile = UserProfile.objects.get(user__username=username)
            ## ##### 4. PONT 4 PROFILE LESSON 9 on notebook
            if save_info:
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_postcode = shipping_details.address.postal_code
                profile.default_town_or_city = shipping_details.address.city
                profile.default_street_address1 = shipping_details.address.line1
                profile.default_street_address2 = shipping_details.address.line2
                profile.default_county = shipping_details.address.state
                profile.save()

        ### 5. POINT 5 STRIPE LESSON 15 on notebook
        order_exists = False
        ### ### 1. POINT 1 STRIPE LESSON 16 on notebook
        attempt = 1
        ### ### 2. POINT 2 STRIPE LESSON 16 on notebook
        while attempt <= 5:
            ### 6. POINT 6 STRIPE LESSON 15 on notebook
            try:
                order = Order.objects.get(
                   full_name__iexact=shipping_details.name,
                   email__iexact=billing_details.email,
                   phone_number__iexact=shipping_details.phone,
                   country__iexact=shipping_details.address.country,
                   postcode__iexact=shipping_details.address.postal_code,
                   town_or_city__iexact=shipping_details.address.city,
                   street_address1__iexact=shipping_details.address.line1,
                   street_address2__iexact=shipping_details.address.line2,
                   county__iexact=shipping_details.address.state,
                   grand_total=grand_total,
                   original_bag=bag,
                   stripe_pid=pid,
               )
                ### 7. POINT 7 STRIPE LESSON 15 on notebook
                order_exists = True
                break
             ### ### 2. POINT 2 STRIPE LESSON 16 on notebook
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        ### ### 4. POINT 4 STRIPE LESSON 16 on notebook
        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200)
        else:
            order = None
            try:
                ### 9. POINT 9 STRIPE LESSON 15 on notebook
                order = Order.objects.create(
                        full_name=shipping_details.name,
                        email=billing_details.email,
                        user_profile=profile,
                        phone_number=shipping_details.phone,
                        country=shipping_details.address.country,
                        postcode=shipping_details.address.postal_code,
                        town_or_city=shipping_details.address.city,
                        street_address1=shipping_details.address.line1,
                        street_address2=shipping_details.address.line2,
                        county=shipping_details.address.state,
                        original_bag=bag,
                        stripe_pid=pid,
                    )
                ### 8. POINT 8 STRIPE LESSON 15 on notebook
                for item_id, item_data in json.loads(bag).items():
                        product = Product.objects.get(id=item_id)
                        if isinstance(item_data, int):
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=item_data,
                            )
                            order_line_item.save()
                        else:
                            for size, quantity in item_data['items_by_size'].items():
                                order_line_item = OrderLineItem(
                                    order=order,
                                    product=product,
                                    quantity=quantity,
                                    product_size=size,
                                )
                                order_line_item.save()
            ### 9. POINT 9 STRIPE LESSON 15 on notebook
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        self._send_confirmation_email(order)
        ### ### 5. POINT 5 STRIPE LESSON 16 on notebook
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)
    
        

    # 2. POINT 2 ON STRIPE 11 LESSON on notebook
    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)