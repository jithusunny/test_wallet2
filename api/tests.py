import json
import uuid
from http import HTTPStatus
from datetime import datetime

from django.test import TestCase

from .models import Wallet


def datetime_valid(dt_str):
    try:
        datetime.fromisoformat(dt_str)
    except:
        try:
            datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except:
            return False
        return True
    return True


class WalletOperationsTest(TestCase):

    def create_account_get_token(self, customer_xid):
        response = self.client.post('/api/v1/init', data={'customer_xid': customer_xid})
        res_json = json.loads(response.content.decode())
        return res_json['data']['token']


    def test_can_create_wallet_account(self):
        response = self.client.post('/api/v1/init', data={'customer_xid': 'ea0212d3-abd6-406f-8c67-868e814a2436'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Wallet.objects.count(), 1)


    def test_can_get_token_for_wallet_account_creation(self):
        response = self.client.post('/api/v1/init', data={'customer_xid': 'ea0212d3-abd6-406f-8c67-868e814a2436'})
        res_json = json.loads(response.content.decode())
        self.assertNotEqual(len(res_json['data']['token']), 0)


    def test_can_get_consistent_token_for_existing_wallet_accounts(self):
        first_token = self.create_account_get_token('ea0212d3-abd6-406f-8c67-868e814a2436')
        self.assertEqual(Wallet.objects.count(), 1)

        second_token = self.create_account_get_token('ea0212d3-abd6-406f-8c67-868e814a2436')
        self.assertEqual(Wallet.objects.count(), 1)

        self.assertEqual(first_token, second_token)


    def test_have_distinct_tokens_for_different_wallet_accounts(self):
        first_token = self.create_account_get_token('ea0212d3-abd6-406f-8c67-868e814a2436')
        self.assertEqual(Wallet.objects.count(), 1)

        second_token = self.create_account_get_token('fa0212d3-abd6-406f-8c67-868e814a2436')
        self.assertEqual(Wallet.objects.count(), 2)

        self.assertNotEqual(first_token, second_token)


    def test_can_enable_wallet(self):
        token = self.create_account_get_token('ea0212d3-abd6-406f-8c67-868e814a2436')
        header = {'HTTP_Authorization': 'Token ' + token}

        response = self.client.post('/api/v1/wallet', **header)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        e_res_json = json.loads(response.content.decode())

        self.assertNotEqual(len(e_res_json['data']['wallet']['id']), 0)
        self.assertEqual(e_res_json['data']['wallet']['owned_by'], 'ea0212d3-abd6-406f-8c67-868e814a2436')
        self.assertRegex(str(e_res_json['data']['wallet']['status']), r'(en|dis)abled')
        self.assertTrue(datetime_valid(e_res_json['data']['wallet']['enabled_at']))
        self.assertRegex(str(e_res_json['data']['wallet']['balance']), r'\d+')


    def test_can_check_authorization_to_enable_wallet(self):
        response = self.client.post('/api/v1/wallet')
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        header = {'HTTP_Authorization': 'test'}
        response = self.client.post('/api/v1/wallet', **header)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)


    def test_enable_will_fail_if_wallet_already_enabled(self):
        token = self.create_account_get_token('ea0212d3-abd6-406f-8c67-868e814a2436')
        header = {'HTTP_Authorization': 'Token ' + token}

        response = self.client.post('/api/v1/wallet', **header)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.client.post('/api/v1/wallet', **header)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


    def test_can_view_balance(self):
        token = self.create_account_get_token('ea0212d3-abd6-406f-8c67-868e814a2436')
        header = {'HTTP_Authorization': 'Token ' + token}

        self.client.post('/api/v1/wallet', **header)

        response = self.client.get('/api/v1/wallet', **header)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        e_res_json = json.loads(response.content.decode())

        self.assertNotEqual(len(e_res_json['data']['wallet']['id']), 0)
        self.assertEqual(e_res_json['data']['wallet']['owned_by'], 'ea0212d3-abd6-406f-8c67-868e814a2436')
        self.assertRegex(str(e_res_json['data']['wallet']['status']), r'(en|dis)abled')
        self.assertTrue(datetime_valid(e_res_json['data']['wallet']['enabled_at']))
        self.assertRegex(str(e_res_json['data']['wallet']['balance']), r'\d+')


    def test_can_check_authorization_to_view_balance(self):
        response = self.client.get('/api/v1/wallet')
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        header = {'HTTP_Authorization': 'test'}
        response = self.client.get('/api/v1/wallet', **header)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)


    def test_can_view_balance_only_while_enabled(self):
        token = self.create_account_get_token('ea0212d3-abd6-406f-8c67-868e814a2436')
        header = {'HTTP_Authorization': 'Token ' + token}

        response = self.client.get('/api/v1/wallet', **header)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


    def test_can_deposit_money(self):
        token = self.create_account_get_token('ea0212d3-abd6-406f-8c67-868e814a2436')
        header = {'HTTP_Authorization': 'Token ' + token}

        self.client.post('/api/v1/wallet', **header)

        response = self.client.post('/api/v1/wallet/deposits', 
            data={'amount': 60000, 'reference_id': str(uuid.uuid4())}, **header)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        res_json = json.loads(response.content.decode())

        self.assertNotEqual(len(res_json['data']['deposit']['id']), 0)
        self.assertEqual(res_json['data']['deposit']['deposited_by'], 'ea0212d3-abd6-406f-8c67-868e814a2436')
        self.assertNotEqual(len(res_json['data']['deposit']['status']), 0)
        self.assertTrue(datetime_valid(res_json['data']['deposit']['deposited_at']))
        self.assertRegex(str(res_json['data']['deposit']['amount']), r'\d+')
        self.assertNotEqual(len(res_json['data']['deposit']['reference_id']), 0)

        response = self.client.get('/api/v1/wallet', **header)
        res_json = json.loads(response.content.decode())
        self.assertEqual(res_json['data']['wallet']['balance'], 60000)


    def test_can_check_authorization_to_deposit_money(self):
        response = self.client.post('/api/v1/wallet/deposits')
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        header = {'HTTP_Authorization': 'test'}
        response = self.client.post('/api/v1/wallet/deposits', **header)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)


    def test_can_deposit_money_only_while_enabled(self):
        token = self.create_account_get_token('ea0212d3-abd6-406f-8c67-868e814a2436')
        header = {'HTTP_Authorization': 'Token ' + token}

        response = self.client.post('/api/v1/wallet/deposits', 
            data={'amount': 60000, 'reference_id': str(uuid.uuid4())}, **header)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)



    def test_can_withdraw_money(self):
        token = self.create_account_get_token('ea0212d3-abd6-406f-8c67-868e814a2436')
        header = {'HTTP_Authorization': 'Token ' + token}

        self.client.post('/api/v1/wallet', **header)

        response = self.client.post('/api/v1/wallet/deposits', 
            data={'amount': 60000, 'reference_id': str(uuid.uuid4())}, **header)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.client.post('/api/v1/wallet/withdrawals', 
            data={'amount': 30000, 'reference_id': str(uuid.uuid4())}, **header)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        res_json = json.loads(response.content.decode())

        self.assertNotEqual(len(res_json['data']['withdrawal']['id']), 0)
        self.assertEqual(res_json['data']['withdrawal']['withdrawn_by'], 'ea0212d3-abd6-406f-8c67-868e814a2436')
        self.assertNotEqual(len(res_json['data']['withdrawal']['status']), 0)
        self.assertTrue(datetime_valid(res_json['data']['withdrawal']['withdrawn_at']))
        self.assertRegex(str(res_json['data']['withdrawal']['amount']), r'\d+')
        self.assertNotEqual(len(res_json['data']['withdrawal']['reference_id']), 0)


        response = self.client.get('/api/v1/wallet', **header)
        res_json = json.loads(response.content.decode())
        self.assertEqual(res_json['data']['wallet']['balance'], 30000)


    def test_can_check_authorization_to_withdraw_money(self):
        response = self.client.post('/api/v1/wallet/withdrawals')
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        header = {'HTTP_Authorization': 'test'}
        response = self.client.post('/api/v1/wallet/withdrawals', **header)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)



    def test_cannot_withdraw_nonexistent_money(self):
        token = self.create_account_get_token('ea0212d3-abd6-406f-8c67-868e814a2436')
        header = {'HTTP_Authorization': 'Token ' + token}

        self.client.post('/api/v1/wallet', **header)

        response = self.client.post('/api/v1/wallet/deposits', 
            data={'amount': 30000, 'reference_id': str(uuid.uuid4())}, **header)
        self.assertEqual(response.status_code, HTTPStatus.OK)


        response = self.client.post('/api/v1/wallet/withdrawals', 
            data={'amount': 60000, 'reference_id': str(uuid.uuid4())}, **header)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


    def test_can_withdraw_money_only_while_enabled(self):
        token = self.create_account_get_token('ea0212d3-abd6-406f-8c67-868e814a2436')
        header = {'HTTP_Authorization': 'Token ' + token}

        response = self.client.post('/api/v1/wallet/withdrawals', 
            data={'amount': 60000, 'reference_id': str(uuid.uuid4())}, **header)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


    def test_can_disable_wallet(self):
        token = self.create_account_get_token('ea0212d3-abd6-406f-8c67-868e814a2436')
        header = {'HTTP_Authorization': 'Token ' + token}

        self.client.post('/api/v1/wallet', **header)

        self.client.patch('/api/v1/wallet', **header)
        response = self.client.get('/api/v1/wallet', **header)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

        self.client.post('/api/v1/wallet', **header)
        response = self.client.get('/api/v1/wallet', **header)
        self.assertEqual(response.status_code, HTTPStatus.OK)
