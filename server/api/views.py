from bson import ObjectId
from bson.errors import InvalidId
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import User, Transaction
from .serializers import UserSerializer
import logging
from rest_framework.decorators import api_view
from .services.transaction_service import analyze_transaction, create_transaction_record
from decimal import Decimal
import random  # Temporary for demo purposes

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ViewSet):
    # Create
    def create(self, request):
        logger.debug(f"Creating user with data: {request.data}")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.debug(f"Created user with ID: {user.id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Read (List)
    def list(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    # Read (Single)
    def retrieve(self, request, pk=None):
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(pk)
            user = User.objects.get(id=object_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except (User.DoesNotExist, InvalidId):
            return Response(status=status.HTTP_404_NOT_FOUND)

    # Update
    def update(self, request, pk=None):
        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(pk)
            user = User.objects.get(id=object_id)
            serializer = UserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except (User.DoesNotExist, InvalidId):
            return Response(status=status.HTTP_404_NOT_FOUND)

    # Delete
    def destroy(self, request, pk=None):
        try:
            logger.debug(f"Attempting to delete user with ID: {pk}")
            # Convert string ID to ObjectId
            object_id = ObjectId(pk)
            user = User.objects.get(id=object_id)
            logger.debug(f"Found user: {user}")
            user.delete()
            logger.debug("User deleted successfully")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            logger.error(f"User with ID {pk} not found")
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def analyze_transaction_view(request):
    try:
        risk_score = analyze_transaction(request.data)
        return Response({"risk_score": risk_score}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_transaction_view(request):
    try:
        account_id = request.data.get('account_id')
        merchant_id = request.data.get('merchant_id')
        amount = request.data.get('amount')
        description = request.data.get('description')
        
        transaction_info, risk_score = create_transaction_record(
            account_id, merchant_id, amount, description
        )
        
        return Response({
            "transaction": transaction_info,
            "risk_score": risk_score
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

def create_transaction_record(account_id, merchant_id, amount, description):
    try:
        # Create and save the transaction
        transaction = Transaction.objects.create(
            account_id=account_id,
            merchant_id=merchant_id,
            amount=Decimal(str(amount)),
            description=description,
            risk_score=0.0  # We'll update this after creation
        )
        
        # Simple risk analysis (for demo purposes)
        risk_factors = {
            'amount': float(amount),
            'merchant_category': 'RETAIL',  # Default category
            'merchant_type': 'ONLINE',      # Default type
            'num_transactions_last_hour': random.randint(0, 5),
            'total_spent_last_hour': random.randint(0, 1000)
        }
        
        # Calculate risk score (0-100)
        risk_score = min(100, (float(amount) / 1000 * 30) +  # Amount factor
                        (risk_factors['num_transactions_last_hour'] * 10) +  # Frequency factor
                        (risk_factors['total_spent_last_hour'] / 1000 * 20))  # Spending pattern factor
        
        # Update transaction with risk score
        transaction.risk_score = risk_score
        transaction.save()
        
        # Format response
        transaction_info = {
            'id': str(transaction.id),
            'account_id': transaction.account_id,
            'merchant_id': transaction.merchant_id,
            'amount': float(transaction.amount),
            'description': transaction.description,
            'timestamp': transaction.timestamp.isoformat(),
            'risk_score': risk_score
        }
        
        return transaction_info, risk_score
        
    except Exception as e:
        raise Exception(f"Failed to create transaction: {str(e)}")

@api_view(['GET'])
def get_transactions(request):
    try:
        transactions = Transaction.objects.all().order_by('-timestamp')
        transaction_list = []
        
        for transaction in transactions:
            # Convert Decimal128 to float
            amount = float(str(transaction.amount))
            
            transaction_list.append({
                'id': str(transaction.id),
                'account_id': transaction.account_id,
                'merchant_id': transaction.merchant_id,
                'amount': amount,
                'description': transaction.description,
                'timestamp': transaction.timestamp.isoformat(),
                'risk_score': float(transaction.risk_score)
            })
        
        return Response(transaction_list, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error in get_transactions: {str(e)}")  # Debug print
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

