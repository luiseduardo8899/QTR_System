from django import forms
from django.forms import ModelForm
from product_quotes.models import Quote
from product_quotes.models import SalesPerson
from product_quotes.models import Account
from product_quotes.models import Product
#from crispy_forms.helper import FormHelper
#from crispy_forms.layout import Layout, Submit, Row, Column

from django.forms import ModelChoiceField

class AccountModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.company_name

class SalesPersonModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.name, obj.last_name

class ProductModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.description

class QuoteForm(forms.Form):
    sales_person = SalesPersonModelChoiceField(queryset=SalesPerson.objects.all(), required=True)
    quote_name = forms.CharField(label="Quote name in the format:: Q.ACNT.DATE ", widget=forms.Textarea, max_length=800, required=False)
    account = AccountModelChoiceField(queryset=Account.objects.all())
    #txaddr = forms.CharField(label="Algorand tx address", widget=forms.Textarea, max_length=58, required=True)
    #rxaddr = forms.CharField(label="Algorand rx address", widget=forms.Textarea, max_length=58, required=True)
    product = ProductModelChoiceField(queryset=Product.objects.all())
    amount = forms.DecimalField(label="Number of Licenses", widget=forms.NumberInput)
    discount = forms.DecimalField(label="Discount in percentage ( i.e 50 = 50% ) ", widget=forms.NumberInput)

