from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.contrib.auth import get_user_model

from ..serializers.profile import UserSerializer, UserProfileUpdateSerializer, AvatarUploadSerializer

User = get_user_model()


@extend_schema(
    tags=['User Profile'],
    summary="Get current user profile",
    description="Retrieve the current authenticated user's profile information.",
    responses={
        200: UserSerializer,
        401: {"description": "Authentication credentials were not provided."}
    }
)
class UserProfileView(generics.RetrieveAPIView):
    """Get current user profile details."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@extend_schema(
    tags=['User Profile'],
    summary="Update user profile",
    description="Update the current authenticated user's profile information.",
    request=UserProfileUpdateSerializer,
    responses={
        200: UserSerializer,
        400: {"description": "Invalid data provided."},
        401: {"description": "Authentication credentials were not provided."}
    },
    examples=[
        OpenApiExample(
            "Valid Profile Update",
            value={
                "first_name": "John",
                "last_name": "Doe",
                "company": "Tech Corp",
                "phone": "+1 (555) 123-4567",
                "position": "Software Engineer"
            },
            request_only=True,
            status_codes=["200"]
        )
    ]
)
class UserProfileUpdateView(generics.UpdateAPIView):
    """Update current user profile."""
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        """Update user profile and return updated data."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return full user data
        user_serializer = UserSerializer(instance)
        return Response(user_serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['User Profile'],
    summary="Partial update user profile",
    description="Partially update the current authenticated user's profile information. Supports avatar upload.",
    request=UserProfileUpdateSerializer,
    responses={
        200: UserSerializer,
        400: {"description": "Invalid data provided."},
        401: {"description": "Authentication credentials were not provided."}
    },
    examples=[
        OpenApiExample(
            "Profile Update with Avatar",
            value={
                "first_name": "John",
                "last_name": "Doe",
                "company": "Tech Corp",
                "phone": "+1 (555) 123-4567",
                "position": "Software Engineer"
            },
            request_only=True,
            status_codes=["200"]
        )
    ]
)
class UserProfilePartialUpdateView(generics.UpdateAPIView):
    """Partially update current user profile."""
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        """Update user profile and return updated data."""
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


@extend_schema(
    tags=['User Profile'],
    summary="Upload user avatar",
    description="Upload avatar image for the current authenticated user. Accepts multipart/form-data with 'avatar' field.",
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'avatar': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Avatar image file (JPEG, PNG, GIF, WebP, max 5MB)'
                }
            },
            'required': ['avatar']
        }
    },
    responses={
        200: UserSerializer,
        400: {"description": "Invalid file or validation error."},
        401: {"description": "Authentication credentials were not provided."}
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_avatar(request):
    """Upload avatar for current user."""
    if 'avatar' not in request.FILES:
        return Response(
            {'error': 'No avatar file provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    avatar_file = request.FILES['avatar']
    user = request.user
    
    # Validate file
    serializer = AvatarUploadSerializer(user, data={'avatar': avatar_file}, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Save avatar
    serializer.save()
    
    # Return updated user data
    user_serializer = UserSerializer(user)
    return Response(user_serializer.data, status=status.HTTP_200_OK) 