# 1. POINT 1 ON THE ADMIN,SIGNS ADN FORMS on the notebook
from django import forms
from .models import Order

# 2. POINT 2 ON THE ADMIN,SIGNS ADN FORMS on the notebook
class OrderForm(forms.ModelForm):
    class Meta:
        # 3. POINT 3 ON THE ADMIN,SIGNS ADN FORMS on the notebook
        model = Order
        fields = ('full_name', 'email', 'phone_number',
                  'street_address1', 'street_address2',
                  'town_or_city', 'postcode', 'country',
                  'county',)

    # 4. POINT 4 ON THE ADMIN,SIGNS ADN FORMS on the notebook
    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        # 5. POINT 5 ON THE ADMIN,SIGNS ADN FORMS on the notebook
        super().__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County, State or Locality',
        }
        
        # 6. POINT 6 ON THE ADMIN,SIGNS ADN FORMS on the notebook
        self.fields['full_name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if field != 'country':
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False