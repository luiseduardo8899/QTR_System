import datetime
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.http import Http404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from random import *
from .forms import QuoteForm
import json
from django.http import JsonResponse
from product_quotes.models import SalesPerson
from product_quotes.models import Account
from product_quotes.models import Product
from product_quotes.models import Quote
from django.conf import settings
from django.core.files.storage import default_storage
import re
import xlwt
import glob
import hashlib
import sys
from algosdk.v2client import algod
from algosdk import mnemonic
from algosdk.future.transaction import PaymentTxn

BUF_SIZE = 65536  #64*1024 = 64kb : Buffer Size large enough to contain images


#START TAXABLE_IDS
CREATED     = 0    #On creation it is saved to /media 
REGISTERED  = 1    #Once it is sent as an algorand trasaction
ACCEPTED    = 2    #Once other party accepts
REJECTED    = 3    #If other party rejects
INVALIDATED = 4    #If both sides agree to invalidate document

def get_balance(address):
    algod_address = "https://testnet.algoexplorerapi.io"
    algod_client = algod.AlgodClient("", algod_address, headers={'User-Agent': 'DoYouLoveMe?'})
    print("Account Public Address: {}".format(address))
    account_info = algod_client.account_info(address)
    print(json.dumps(account_info, indent=4))
    account_balance = account_info.get('amount')
    print('Account balance: {} Algos\n\n'.format(account_balance/1000000))
    return account_balance

# utility for waiting on a transaction confirmation
def wait_for_confirmation(client, transaction_id, timeout):
    """
    Wait until the transaction is confirmed or rejected, or until 'timeout'
    number of rounds have passed.
    Args:
        transaction_id (str): the transaction to wait for
        timeout (int): maximum number of rounds to wait
    Returns:
        dict: pending transaction information, or throws an error if the transaction
            is not confirmed or rejected in the next timeout rounds
    """
    start_round = client.status()["last-round"] + 1;
    current_round = start_round

    while current_round < start_round + timeout:
        try:
            pending_txn = client.pending_transaction_info(transaction_id)
        except Exception:
            return
        if pending_txn.get("confirmed-round", 0) > 0:
            return pending_txn
        elif pending_txn["pool-error"]:
            raise Exception(
                'pool error: {}'.format(pending_txn["pool-error"]))
        client.status_after_block(current_round)
        current_round += 1
    raise Exception(
        'pending tx not found in timeout rounds, timeout value = : {}'.format(timeout))

def commit_quote_to_ledger(tx_address, rx_address, quote, quote_hash):
    # Use sandbox or your address and token
    #algod_address = "198.199.75.129:4001"
    #algod_token = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

    #ALGOEXPLORER API
    algod_address = "https://testnet.algoexplorerapi.io"
    algod_client = algod.AlgodClient("", algod_address, headers={'User-Agent': 'DoYouLoveMe?'})

    params = algod_client.suggested_params()
    print("PARAMS: {}".format(params))
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000
    accounts = quote.account.all()
    note_string= str({"Attention:":accounts[0].main_contact, "Company":accounts[0].company_name, "QUOTE":quote.quote_name, "QUOTE_HASH":quote_hash})
    print(note_string)
    note = note_string.encode()
    print(note)

    # create transaction
    unsigned_txn = PaymentTxn(tx_address, params, rx_address, 0, None, note)

    # sign transaction
    signed_txn = unsigned_txn.sign(settings.COMPANY_PRIVATE_KEY)

    # send transaction
    txid = algod_client.send_transaction(signed_txn)
    print("Sending transaction with txID: {}".format(txid))

    # wait for confirmation
    try:
        confirmed_txn = wait_for_confirmation(algod_client, txid, 4)
        return txid
    except Exception as err:
        print(err)
        return "ERROR_TX_FAILED"

def create_hash(filename, prev_hash, debug=0):
    sha256_hash = 0
    md5_hash = 0
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()

    with open(filename, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE) #read byte code
            if not data:
                break
            if(debug):
                print("FILE: BYTECODE:\n")
                print(data)
            md5.update(data)
            md5.update(prev_hash) #append previous document's hash
            md5_hash = md5.hexdigest()
            md5_digest_size = md5.digest_size
            md5_block_size = md5.block_size
            if(debug):
                print("\nMD5: --------------------")
                print(md5_hash)
                print(md5_digest_size)
                print(md5_block_size)
            sha256.update(data)
            sha256.update(prev_hash) #append previous document's hash
            sha256_hash = md5.hexdigest()
            sha256_digest_size = md5.digest_size
            sha256_block_size = md5.block_size
            if(debug):
                print("\nSHA256: --------------------")
                print(sha256_hash)
                print(sha256_digest_size)
                print(sha256_block_size)

    return md5_hash, sha256_hash


def check_hash(file, prev_hash, rx_hash):
    md5_hash, sha256_hash = create_hash(file, prev_hash)
    Bsha256_hash = str.encode(sha256_hash)
    if Bsha256_hash != rx_hash:
        print("FATAL_ERROR: calculated hash {} does not match hash provided {} ", sha256_hash, rx_hash )
        return 0
    else :
        print("HASH CHECK PASSED")
        return 1


def generate_quote_file(quote):
    filename = quote.quote_name
    book = xlwt.Workbook()
    sh = book.add_sheet(filename)

    #size the columns
    charwidth = 256
    numchar = [6,6,15,70, 20,15,15] #number of characters per column
    for ix in range(7):
        col =  sh.col(ix)
        col.width = charwidth * numchar[ix]

    style_title = xlwt.easyxf('font: bold on, color black, height 200;')
    sh.write(2, 3, "THE COMPANY. INC", style_title)
    sh.write(3, 3, "Austin, TX")
    sh.write(8,0, "To:")
    sh.write(9,0, "Attn:")
    accounts = quote.account.all()
    sh.write(8,1, accounts[0].company_name)
    sh.write(9,1, accounts[0].main_contact)
    sh.write(9,2, accounts[0].email)

    style = xlwt.easyxf('font: bold off, color black; borders: left thin, right thin, top thin, bottom thin; align: horiz center')
    titles = ['SALES PERSON', 'QUOTE EXPIRATION DATE', 'TAXABLE', 'TERMS']
    ix =2
    for title in titles:
        sh.write(13, ix, title, style )
        ix= ix +1

    ix =2
    row = 14
    date_time = datetime.date.today() + datetime.timedelta(quote.validity)
    expiration = date_time.strftime("%m/%d/%Y")
    sales_persons = quote.sales_person.all()
    sales_person_name = sales_persons[0].name+" "+sales_persons[0].last_name
    titles = [sales_person_name, expiration, quote.taxable, quote.term]
    for title in titles:
        sh.write(row, ix, title, style)
        ix= ix +1

    row = 16
    ix =0
    titles = ['ITEM', 'QTY', 'PRODUCT', 'DESCRIPTION', 'LIST PRICE ( per License)', 'DISCOUNT', 'NET PRICE']
    for title in titles:
        sh.write(row, ix, title,  style)
        ix= ix +1

    row = 17
    total_quote = 0
    item = 1
    products = quote.product.all()
    for p in products:
        net_price = ( p.list_price * quote.quantity * quote.discount ) / 100
        total_quote += net_price
        titles = [item, quote.quantity, p.product_code, p.description, p.list_price, quote.discount, net_price ]
        item = item +1
        ix =0
        for title in titles:
            sh.write(row, ix, title, style)
            ix += 1
        row += 1

    titles = ["TOTAL", "", total_quote]
    ix = 4
    for title in titles:
        sh.write(row, ix, title,  style)
        ix= ix +1

    book.save(filename+".xls")
    myfile =  open(filename+".xls", "rb")

    return myfile, filename

def generate_quote(request):
    #user = get_user(request)
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = QuoteForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            last_quote = Quote.objects.latest('create_date');
            last_id = last_quote.quote_id
            q = Quote()
            q.quote_id = last_id + 1
            q.create_date = datetime.datetime.now()
            # process the data in form.cleaned_data as required
            q.state = CREATED
            q.quote_name = form.cleaned_data['quote_name']
            q.txaddr = settings.COMPANY_ALGO_ADDRESS
            account= form.cleaned_data['account']
            q.rxaddr = account.algo_addr
            print("ALGO ADDRESS")
            print(account.algo_addr)
            q.quantity = form.cleaned_data['amount']
            #q.taxable = form.cleaned_data['taxable']
            q.taxable = 0
            q.discount = form.cleaned_data['discount']
            #q.term = form.cleaned_data['term']
            q.term = 1
            #q.validity = form.cleaned_data['validity']
            q.validity = 30;
            q.save()
            #Then add manytomany fields
            q.sales_person.add(form.cleaned_data['sales_person'])
            q.product.add(form.cleaned_data['product'])
            q.account.add(form.cleaned_data['account'])
            q.save()

            #generate xls version of the quote / save to media and provide URL
            myfile, filename = generate_quote_file(q)
            file_name = default_storage.save(filename+".xls", myfile)

            starting_hash = settings.COMPANY_PRIVATE_KEY #Use password authenticatio or 2 factor authentication to retrieve private key
            Bstarting_hash= str.encode(starting_hash)
            md5_hash, sha256hash = create_hash(filename+".xls", Bstarting_hash)
            q.sha256hash = sha256hash
            q.save()

            B256hash = str.encode(sha256hash)
            ok = check_hash(filename+".xls", Bstarting_hash, B256hash)

            #generate transacton with hash of the quote included in the note field
            if ok : 
                algod_txnid = commit_quote_to_ledger(settings.COMPANY_ALGO_ADDRESS, account.algo_addr, q, sha256hash)

            q.algod_txnid = algod_txnid
            q.save()

            # redirect to a new URL:
            return HttpResponseRedirect('/quotes/generate_quote/')
        else:
            print("FORM ERRORS:\n\t")
            print(form.errors)


    # if a GET (or any other method) we'll create a blank form
    else:
        form = QuoteForm()

    sales_persons = SalesPerson.objects.all()
    accounts = Account.objects.all()
    products = Product.objects.all()
    return render(request, 'generate_quote.html', {'form': form, 'sales_persons':sales_persons, 'accounts':accounts, 'products':products})

#def generate_license(request):
