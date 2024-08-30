from django import forms

class PaymentForm(forms.Form):
    email = forms.EmailField()
    amount = forms.IntegerField(widget=forms.HiddenInput())  # Amount in kobo
