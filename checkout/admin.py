# 1. POINT 1 ON THE ADMIN,SIGNS ADN FORMS on the notebook
from django.contrib import admin
from .models import Order, OrderLineItem

# 7. POINT 7 ON THE ADMIN,SIGNS ADN FORMS on the notebook
class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)


# 2. POINT 2 ON THE ADMIN,SIGNS ADN FORMS on the notebook
class OrderAdmin(admin.ModelAdmin):

    # 8. POINT 8 ON THE ADMIN,SIGNS ADN FORMS on the notebook
    inlines = (OrderLineItemAdminInline,)
    # 3. POINT 3 ON THE ADMIN,SIGNS ADN FORMS on the notebook
    readonly_fields = ('order_number', 'date',
                       'delivery_cost', 'order_total',
                       'grand_total', 'original_bag',
                       'stripe_pid')
    # 4. POINT 4 ON THE ADMIN,SIGNS ADN FORMS on the notebook
    fields = ('order_number', 'user_profile', 'date', 'full_name',
              'email', 'phone_number', 'country',
              'postcode', 'town_or_city', 'street_address1',
              'street_address2', 'county', 'delivery_cost',
              'order_total', 'grand_total', 'original_bag',
              'stripe_pid')

# 5. POINT 5 ON THE ADMIN,SIGNS ADN FORMS on the notebook
    list_display = ('order_number', 'date', 'full_name',
                    'order_total', 'delivery_cost',
                    'grand_total',)

# 6. POINT 6 ON THE ADMIN,SIGNS ADN FORMS on the notebook
    ordering = ('-date',)

# 9. POINT 9 ON THE ADMIN,SIGNS ADN FORMS on the notebook
admin.site.register(Order, OrderAdmin)