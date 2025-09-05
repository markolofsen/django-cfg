# Tests for accounts app

# Import all test classes to make them discoverable
from .test_models import (
    CustomUserModelTest,
    CustomUserSourceMethodsTest,
    OTPSecretModelTest,
    RegistrationSourceModelTest,
    UserRegistrationSourceModelTest,
)

from .test_services import OTPServiceTest

from .test_serializers import (
    UserProfileUpdateSerializerTest,
    RegistrationSourceSerializerTest,
    UserRegistrationSourceSerializerTest,
    UserWithSourcesSerializerTest,
    OTPRequestSerializerTest,
    OTPVerifySerializerTest,
)

from .test_views import (
    OTPViewsTest,
    UserViewsTest,
    TokenRefreshViewTest,
    IntegrationTest,
)

from .test_signals import AccountSignalsTestCase
