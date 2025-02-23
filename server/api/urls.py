from django.urls import path
from .views import (
    UserViewSet, 
    analyze_transaction_view,
    create_transaction_view,
    get_transactions
)

urlpatterns = [
    path('users/', UserViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('users/<str:pk>/', UserViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),
    path('analyze-transaction/', analyze_transaction_view, name='analyze-transaction'),
    path('create-transaction/', create_transaction_view, name='create-transaction'),
    path('transactions/', get_transactions, name='get-transactions'),
]
