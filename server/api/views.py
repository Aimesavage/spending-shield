from bson import ObjectId
from bson.errors import InvalidId
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
import logging

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

