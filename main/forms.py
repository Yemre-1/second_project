from django import forms
from .models import Product
class CheckOutForm(forms.Form):
    address = forms.CharField(widget=forms.Textarea, label='Adres')
    phone= forms.CharField(max_length=15, label='Telefon')
class CommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'rows':2, 'placeholder':'Yorumunu yaz...'}), label='') 
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description' , 'price' , 'category']       