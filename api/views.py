import datetime
import functools

from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .decorators import *
from .models import Wallet
from .services import authenticate_customer



@api_view(['POST'])
def wallet_init(request):
    auth_resp = authenticate_customer(
        request.POST['customer_xid'],
        # request.POST['password'],
    )

    w, _ = Wallet.objects.update_or_create(
        customer_xid=request.POST['customer_xid'],
        defaults={'token': auth_resp['data']['token']},
    )

    return Response({
        'status': 'success',
        'data': {
            'token': w.token
        }
    })



@api_view(['POST', 'GET', 'PATCH'])
@valid_token_required
def wallet(request, w):
    if request.method == 'POST':
        if w.is_enabled:
            return Response({
                'status': 'fail',
                'data': {
                    'Enable': 'Already enabled'
                }}, 
                status=status.HTTP_403_FORBIDDEN)
        
        w.is_enabled = True
        w.save()
    elif request.method == 'GET':
        if not w.is_enabled:
            return Response({
                'status': 'fail',
                'data': {
                    'Enable': 'Wallet is not enabled'
                }}, 
                status=status.HTTP_403_FORBIDDEN)
    elif request.method == 'PATCH':
        w.is_enabled = False
        w.save()
        return Response({
            'status': 'success',
            'data': {
                'wallet': {
                    'id': w.uuid,
                    'owned_by': w.customer_xid,
                    'status': 'enabled' if w.is_enabled else 'disabled',
                    'disabled_at': datetime.datetime.now(),
                    'balance': w.balance,
                },
            }
        }) 

    return Response({
        'status': 'success',
        'data': {
            'wallet': {
                'id': w.uuid,
                'owned_by': w.customer_xid,
                'status': 'enabled' if w.is_enabled else 'disabled',
                'enabled_at': datetime.datetime.now(),
                'balance': w.balance,
            },
        }
    }) 


@api_view(['POST'])
@valid_token_required
@wallet_is_enabled
def deposit(request, w):
    w.balance += int(request.POST['amount'])
    w.save()

    return Response({
        'status': 'success',
        'data': {
            'deposit': {
                'id': w.uuid,
                'deposited_by': w.customer_xid,
                'status': 'success',
                'deposited_at': datetime.datetime.now(),
                'amount': request.POST['amount'],
                'reference_id': request.POST['reference_id'], 
            },
        }
    }) 


@api_view(['POST'])
@valid_token_required
@wallet_is_enabled
def withdraw(request, w):
    if int(request.POST['amount']) > w.balance:
        return Response({
            'status': 'fail',
            'data': {
                'Amount': 'Insufficient balance'
            }}, 
            status=status.HTTP_403_FORBIDDEN)

    w.balance -= int(request.POST['amount'])
    w.save()

    return Response({
        'status': 'success',
        'data': {
            'withdrawal': {
                'id': w.uuid,
                'withdrawn_by': w.customer_xid,
                'status': 'success',
                'withdrawn_at': datetime.datetime.now(),
                'amount': request.POST['amount'],
                'reference_id': request.POST['reference_id'], 
            },
        }
    }) 
