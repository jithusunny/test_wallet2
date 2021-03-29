import uuid

from django.db import models


class Wallet(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)

	customer_xid = models.TextField(unique=True, default='')
	token = models.CharField(max_length=40)
	balance = models.IntegerField(default=0)

	is_enabled = models.BooleanField(default=False)

