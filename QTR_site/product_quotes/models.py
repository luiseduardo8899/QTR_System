from django.db import models
from django.utils import timezone
import datetime


#START TAXABLE_IDS
CREATED     = 0    #On creation it is saved to /media 
REGISTERED  = 1    #Once it is sent as an algorand trasaction
ACCEPTED    = 2    #Once other party accepts
REJECTED    = 3    #If other party rejects
INVALIDATED = 4    #If both sides agree to invalidate document

STATE_IDS = (
    (CREATED,       "created_tag"),
    (REGISTERED,    "registered_tag"),    
    (ACCEPTED,      "accepted_tag"),        
    (REJECTED,      "rejected_tag"),        
    (INVALIDATED,   "invalidated_tag"),  
)

#START TAXABLE_IDS
NON_TAXABLE = 0
TAXABLE = 1
SEE_TCS = 2

TAXABLE_IDS = (
    (NON_TAXABLE , "nontaxable_tag"  ), 
    (TAXABLE , "taxable_tag"  ), 
    (SEE_TCS , "see_tcs_tags"  ), 
)

#START TERM_IDS
NET15 = 0
NET30 = 1
NET45 = 2
NET60 = 3
NET90 = 4
OTHER = 5

TERM_IDS = (
    (NET15 , "net15_tag"  ),
    (NET30 , "net30_tag"  ),
    (NET45 , "net45_tag"  ),
    (NET60 , "net60_tag"  ),
    (NET90 , "net90_tag"  ),
    (OTHER , "other_tag"  ),
)


class SalesPerson(models.Model):
    salesid = models.IntegerField(default=0)                #unique identifier
    name =  models.CharField(max_length=200)                # first name
    last_name =  models.CharField(max_length=200, default="")           #last name
    phone_number =  models.CharField(max_length=200, default="")        #phone number
    create_date = models.DateTimeField('date published')
    email = models.EmailField(max_length=254, default="")               #email

    def __str__(self):
        return "SalesPerson# %s" % self.name

class Account(models.Model):
    account_id = models.IntegerField(default=0)    
    create_date = models.DateTimeField('date published')
    company_name =  models.CharField(max_length=200)  
    main_contact =  models.CharField(max_length=200)  #Main contact person for quotes/PO
    email = models.EmailField(max_length=254)         #Contact email / AP address
    algo_addr = models.CharField(max_length=200)      #Account's Algorand address

    def __str__(self):
        return "Account#%s" % self.company_name

class Product(models.Model):
    product_code = models.CharField(max_length=200) #Product Code ID
    description = models.CharField(max_length=200)  #Descripton of the product
    lease_term = models.IntegerField(default =12)   #Lease term in months ( default is 1 year )
    list_price =  models.IntegerField(default=1)    #Official List price before any discounting

    def __str__(self):
        return "Product#%s" % self.product_code

#Class Quote
#Class for all Product entries 
class Quote(models.Model):
    quote_id = models.IntegerField(default=0, primary_key=True)                #Unique integer identifier for the quote
    quote_name = models.CharField(max_length=200)           #Unique Quote name : Q+customer.company_name+create_date
    create_date = models.DateTimeField('date published')
    state = models.IntegerField(choices=STATE_IDS, default=CREATED) 
    sales_person = models.ManyToManyField(SalesPerson)     #Sales Person
    account =  models.ManyToManyField(Account)             #After creating object,  use quote.add(<Account pointer>) #Account to which we are sending this quote
    txaddr = models.CharField(max_length=200)              #TX Sender Algorand address
    rxaddr = models.CharField(max_length=200)              #RX Receiving Algorand address
    product =  models.ManyToManyField(Product)             #After creating object,  use quote.add(<Product pointer>)
    quantity = models.IntegerField(max_length=200)         #Quantity of products
    taxable = models.IntegerField(choices=TAXABLE_IDS, default=0) 
    discount = models.IntegerField(default=0)               #Percentage of discount, must be 0%-99%
    term = models.IntegerField(choices=TERM_IDS, default=1) #Payment terms
    validity = models.IntegerField(default=30)              #Number of days the quote is valid


    def __str__(self):
        return "Quote#%s" % self.quote_name

    class Meta:
        ordering = ['create_date']

    def get_products(self):
        products = self.product_set.all()
        if len(products) != 0 :
            return products
        else:
            return "NO PRODUCTS FOUND"

#Class PO
#Class for all PO entries 
class PO(models.Model):
    po_id = models.IntegerField(default=0)      #Unique identifier #Hash of PO document 
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)  #Quote to which this PO corresponds
    po_name = models.CharField(max_length=200)  #PO+account.company_name+create_date
    account =  models.ManyToManyField(Account)  #After creating object,  use PO.add(<Account pointer>) # Account to which this PO is sent to
    state = models.IntegerField(choices=STATE_IDS, default=CREATED) 
    txaddr = models.CharField(max_length=200)   #TX Sender Algorand address
    rxaddr = models.CharField(max_length=200)   #RX Receiving Algorand address
    create_date = models.DateTimeField('date published')
    sales_person = models.ManyToManyField(SalesPerson)     #Sales Person, use PO.add(<SalesPerson pointer>)
    validity = models.IntegerField(default=30) #Number of days the quote is valid
    po_url = models.URLField(max_length=200)   #URL to PO file
    txn_url = models.URLField(max_length=200)  #URL to Algorand transaction ID

    def __str__(self):
        return "PO#%s" % self.po_name
