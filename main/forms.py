from django import forms
class CheckOutForm(forms.Form):
    address = forms.CharField(widget=forms.Textarea, label='Adres')
    phone= forms.CharField(max_length=15, label='Telefon')
    