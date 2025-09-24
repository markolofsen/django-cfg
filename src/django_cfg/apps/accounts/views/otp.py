from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
import logging
import traceback

from ..services import OTPService
from ..serializers.otp import (
    OTPRequestSerializer,
    OTPVerifySerializer,
    OTPRequestResponseSerializer,
    OTPVerifyResponseSerializer,
    OTPErrorResponseSerializer,
)
from ..serializers.profile import UserSerializer
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


class OTPViewSet(viewsets.GenericViewSet):
    """OTP authentication ViewSet with nested router support."""

    permission_classes = [permissions.AllowAny]
    serializer_class = OTPRequestSerializer  # Default serializer for the viewset
    
    def get_serializer_class(self):
        """Return the appropriate serializer class based on the action."""
        if self.action == 'request_otp':
            return OTPRequestSerializer
        elif self.action == 'verify_otp':
            return OTPVerifySerializer
        return super().get_serializer_class()

    @extend_schema(
        request=OTPRequestSerializer,
        responses={
            200: OTPRequestResponseSerializer,
            400: OTPErrorResponseSerializer,
            500: OTPErrorResponseSerializer,
        },
    )
    @action(detail=False, methods=["post"], url_path="request")
    def request_otp(self, request):
        """Request OTP code to email or phone."""
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["identifier"]
        channel = serializer.validated_data.get("channel")
        source_url = serializer.validated_data.get("source_url")
        
        # Auto-detect channel if not provided
        if not channel:
            channel = 'email' if '@' in identifier else 'phone'
        
        logger.debug(f"Starting OTP request for {channel}: {identifier}, source: {source_url}")

        try:
            if channel == 'email':
                success, error_type = OTPService.request_otp(identifier, source_url)
            else:
                # For phone OTP, we'll need to implement phone OTP service
                # For now, fallback to email-based service
                success, error_type = OTPService.request_otp(identifier, source_url)
        except Exception as e:
            # Log the full traceback for debugging
            logger.error(f"OTP request failed with exception: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return Response(
                {"error": "Internal server error during OTP request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if success:
            return Response(
                {"message": "OTP sent to your email address"}, status=status.HTTP_200_OK
            )
        else:
            if error_type == "invalid_email":
                logger.warning(f"Invalid identifier provided: {identifier}")
                return Response(
                    {"error": "Invalid identifier format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif error_type == "user_creation_failed":
                # Log additional details for user creation failure
                logger.error(f"User creation failed for identifier: {identifier}")
                logger.error(f"Error type: {error_type}")
                logger.error(
                    f"Full traceback for user creation failure: {traceback.format_exc()}"
                )
                return Response(
                    {"error": "Failed to create user account"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            else:
                logger.error(f"Unknown error type: {error_type} for identifier: {identifier}")
                return Response(
                    {"error": "Failed to send OTP"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

    @extend_schema(
        request=OTPVerifySerializer,
        responses={
            200: OTPVerifyResponseSerializer,
            400: OTPErrorResponseSerializer,
            410: OTPErrorResponseSerializer,
        },
    )
    @action(detail=False, methods=["post"], url_path="verify")
    def verify_otp(self, request):
        """Verify OTP code and return JWT tokens."""
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data["identifier"]
        otp = serializer.validated_data["otp"]
        channel = serializer.validated_data.get("channel")
        source_url = serializer.validated_data.get("source_url")
        
        # Auto-detect channel if not provided
        if not channel:
            channel = 'email' if '@' in identifier else 'phone'

        if channel == 'email':
            user = OTPService.verify_otp(identifier, otp, source_url)
        else:
            # For phone OTP, we'll need to implement phone OTP verification
            # For now, fallback to email-based service
            user = OTPService.verify_otp(identifier, otp, source_url)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            # Check if user was deleted after OTP was sent
            try:
                User = get_user_model()
                # For email identifiers, check by email; for phone, we'd need phone field
                if '@' in identifier:
                    User.objects.get(email=identifier)
                else:
                    # For phone numbers, we'd need to implement phone field lookup
                    # For now, assume email-based lookup
                    User.objects.get(email=identifier)
                # User exists but OTP is invalid
                return Response(
                    {"error": "Invalid or expired OTP"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except User.DoesNotExist:
                # User was deleted after OTP was sent
                return Response(
                    {"error": "User account has been deleted"},
                    status=status.HTTP_410_GONE,
                )
