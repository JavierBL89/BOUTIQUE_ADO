# 1. POINT 1 PRODUCT ADMIN LESSON 1 on notebook
from django import forms
from .widgets import CustomClearableFieldInput
from .models import Product, Category

# 3. POINT 3 PRODUCT ADMIN LESSON 1 on notebook
class ProductForm(forms.ModelForm):
    # 3. POINT 3 PRODUCT ADMIN LESSON 1 on notebook
    class Meta:
        model = Product
        fields = '__all__'
    ### 14. POINT 14 IN PRODUCT ADMIN FIXING IMAGE LESSON 1
    image = forms.ImageField(label='Image', required=False, widget=CustomClearableFieldInput
    )
    
    # 4. POINT 4 PRODUCT ADMIN LESSON 1 on notebook
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 5. POINT 5 PRODUCT ADMIN LESSON 1 on notebook
        categories = Category.objects.all()
        # 5. POINT 5 PRODUCT ADMIN LESSON 1 on notebook        
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]
        # 6. POINT 6 PRODUCT ADMIN LESSON 1 on notebook
        self.fields['category'].choices = friendly_names
        # 7. POINT 7 PRODUCT ADMIN LESSON 1 on notebook
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'