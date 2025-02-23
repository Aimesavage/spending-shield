from django.db import models
from djongo import models as djongo_models
from bson import ObjectId

class User(models.Model):
    id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)  # Changed from _id to id
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    income = models.DecimalField(max_digits=10, decimal_places=2)
    expenses = models.JSONField(default=dict)  # Store expenses as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.name

class Transaction(models.Model):
    id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    account_id = models.CharField(max_length=100)
    merchant_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    risk_score = models.FloatField(default=0.0)

    class Meta:
        db_table = 'transactions'

    def __str__(self):
        return f"{self.account_id} - ${self.amount}"
