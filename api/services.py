import os
import requests
import binascii

from .models import Wallet

def authenticate_customer(customer_xid, password=None):

    # Authenticate, obtain token using Customer Service
    
    # url = 'http://api.example.com/authenticate_customer' 
    # params = {'customer_xid': customer_xid, 'password': password}

    # resp = requests.get(url, params=params)
    # return resp.json()


    # Mock Authentication and token retrieval
    w = Wallet.objects.filter(customer_xid=customer_xid).first()

    if w:
        token = w.token
    else:
        token = binascii.hexlify(os.urandom(20)).decode()

    return {
        'status': 'success',
        'data': {
            'token': token
        }
    }
    