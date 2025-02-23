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
