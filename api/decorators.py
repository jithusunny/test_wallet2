import functools

from rest_framework.response import Response
from rest_framework import status

from .models import Wallet


def valid_token_required(func):
    def wrapper(*args, **kwargs):
        request = args[0]

        if 'Authorization' not in request.headers:
            return Response({
                'status': 'fail',
                'data': {
                    'Authorization': 'Authorization header is missing'
                }}, 
                status=status.HTTP_400_BAD_REQUEST)
        
        auth_header = request.headers['Authorization']

        try:
            token = auth_header.split(' ')[1]
            w = Wallet.objects.get(token=token)
        except:
            return Response({
                'status': 'fail',
                'data': {
                    'Authorization': 'Invalid credentials'
                }}, 
                status=status.HTTP_401_UNAUTHORIZED)

        token = request.headers['Authorization'].split(' ')[1]
        w = Wallet.objects.get(token=token)

        return func(*args, w, **kwargs)
    return wrapper


def wallet_is_enabled(func):
    def wrapper(*args, **kwargs):
        request = args[0]
        wallet = args[1]

        if not wallet.is_enabled:
            return Response({
                'status': 'fail',
                'data': {
                    'Enable': 'Wallet is not enabled'
                }}, 
                status=status.HTTP_403_FORBIDDEN)

        return func(*args, **kwargs)
    return wrapper
