"""
Tests for simplified limits configuration model.

Tests the LimitsConfig model for proper validation,
Django settings generation, and configuration consistency.
"""

import pytest
from pydantic import ValidationError

from django_cfg.models.limits import LimitsConfig


class TestLimitsConfig:
    """Test simplified LimitsConfig model."""

    def test_default_values(self):
        """Test default values are set correctly."""
        config = LimitsConfig()
        
        assert config.max_upload_mb == 10.0
        assert config.max_memory_mb == 2.0
        assert config.max_request_mb == 50.0
        assert config.allowed_extensions is None
        assert config.blocked_extensions is None
        assert config.request_timeout == 30
        assert config.enabled is True
        assert config.strict_mode is False

    def test_custom_values(self):
        """Test custom values are accepted."""
        config = LimitsConfig(
            max_upload_mb=20.0,
            max_memory_mb=5.0,
            max_request_mb=100.0,
            allowed_extensions=["jpg", "png", "pdf"],
            blocked_extensions=["exe", "bat"],
            request_timeout=60,
            enabled=True,
            strict_mode=True,
        )
        
        assert config.max_upload_mb == 20.0
        assert config.max_memory_mb == 5.0
        assert config.max_request_mb == 100.0
        assert config.allowed_extensions == ["jpg", "png", "pdf"]
        assert config.blocked_extensions == ["exe", "bat"]
        assert config.request_timeout == 60
        assert config.enabled is True
        assert config.strict_mode is True

    def test_validation_memory_size_too_large(self):
        """Test validation fails when memory size exceeds upload size."""
        with pytest.raises(ValidationError) as exc_info:
            LimitsConfig(
                max_upload_mb=10.0,
                max_memory_mb=20.0,  # Larger than max_upload_mb
            )
        
        assert "max_memory_mb cannot be larger than max_upload_mb" in str(exc_info.value)

    def test_validation_conflicting_extensions(self):
        """Test validation fails when extensions are both allowed and blocked."""
        with pytest.raises(ValidationError) as exc_info:
            LimitsConfig(
                allowed_extensions=["jpg", "png", "exe"],
                blocked_extensions=["exe", "bat"],
            )
        
        assert "Extensions cannot be both allowed and blocked" in str(exc_info.value)

    def test_extension_cleaning(self):
        """Test that extensions are cleaned properly."""
        config = LimitsConfig(
            allowed_extensions=[".jpg", "PNG", " pdf "],
            blocked_extensions=[".exe", "BAT"],
        )
        
        assert config.allowed_extensions == ["jpg", "png", "pdf"]
        assert config.blocked_extensions == ["exe", "bat"]

    def test_invalid_extension_format(self):
        """Test validation fails for invalid extension formats."""
        with pytest.raises(ValidationError) as exc_info:
            LimitsConfig(
                allowed_extensions=["jpg", "png/gif", "pdf"],
            )
        
        assert "Invalid file extension" in str(exc_info.value)

    def test_size_limits_validation(self):
        """Test size limits are within valid ranges."""
        # Test minimum values
        config = LimitsConfig(
            max_upload_mb=0.1,  # 100KB minimum
            max_memory_mb=0.1,
            max_request_mb=0.1,
        )
        assert config.max_upload_mb == 0.1

        # Test maximum values should not raise error
        config = LimitsConfig(
            max_upload_mb=1024.0,  # 1GB maximum
            max_memory_mb=100.0,
            max_request_mb=1024.0,
        )
        assert config.max_upload_mb == 1024.0

    def test_to_django_settings_disabled(self):
        """Test Django settings generation when limits are disabled."""
        config = LimitsConfig(enabled=False)
        settings = config.to_django_settings()
        
        assert settings == {}

    def test_to_django_settings_enabled(self):
        """Test Django settings generation when limits are enabled."""
        config = LimitsConfig(
            max_upload_mb=20.0,
            max_memory_mb=5.0,
            max_request_mb=25.0,
            allowed_extensions=["jpg", "png"],
            blocked_extensions=["exe"],
            enabled=True,
        )
        
        settings = config.to_django_settings()
        
        # Check core Django settings
        assert settings["FILE_UPLOAD_MAX_MEMORY_SIZE"] == 5 * 1024 * 1024  # 5MB in bytes
        assert settings["DATA_UPLOAD_MAX_MEMORY_SIZE"] == 5 * 1024 * 1024  # 5MB in bytes
        assert settings["DATA_UPLOAD_MAX_NUMBER_FIELDS"] == 1000  # Default
        
        # Check custom settings
        assert settings["ALLOWED_FILE_EXTENSIONS"] == ["jpg", "png"]
        assert settings["BLOCKED_FILE_EXTENSIONS"] == ["exe"]
        
        # Check limits config is included
        assert "LIMITS_CONFIG" in settings
        limits_config = settings["LIMITS_CONFIG"]
        assert limits_config["enabled"] is True
        assert limits_config["max_upload_bytes"] == 20 * 1024 * 1024  # 20MB in bytes
        assert limits_config["max_memory_bytes"] == 5 * 1024 * 1024   # 5MB in bytes
        assert limits_config["max_request_bytes"] == 25 * 1024 * 1024 # 25MB in bytes

    def test_smart_defaults_allowed_extensions(self):
        """Test smart default allowed extensions."""
        config = LimitsConfig()
        
        # Test that smart defaults are used when None
        settings = config.to_django_settings()
        allowed_exts = settings["ALLOWED_FILE_EXTENSIONS"]
        
        # Should include common file types
        assert "jpg" in allowed_exts
        assert "png" in allowed_exts
        assert "pdf" in allowed_exts
        assert "txt" in allowed_exts
        assert "mp4" in allowed_exts
        assert "zip" in allowed_exts

    def test_smart_defaults_blocked_extensions(self):
        """Test smart default blocked extensions."""
        config = LimitsConfig()
        
        # Test that smart defaults are used when None
        settings = config.to_django_settings()
        blocked_exts = settings["BLOCKED_FILE_EXTENSIONS"]
        
        # Should include dangerous file types
        assert "exe" in blocked_exts
        assert "bat" in blocked_exts
        assert "php" in blocked_exts
        assert "js" in blocked_exts
        assert "py" in blocked_exts
        assert "sh" in blocked_exts

    def test_get_validator_config(self):
        """Test validator configuration generation."""
        config = LimitsConfig(
            max_upload_mb=20.0,
            max_memory_mb=5.0,
            max_request_mb=25.0,
            allowed_extensions=["jpg", "png"],
            request_timeout=60,
            strict_mode=True,
        )
        
        validator_config = config.get_validator_config()
        
        assert validator_config["max_upload_bytes"] == 20 * 1024 * 1024
        assert validator_config["max_memory_bytes"] == 5 * 1024 * 1024
        assert validator_config["max_request_bytes"] == 25 * 1024 * 1024
        assert validator_config["request_timeout"] == 60
        assert validator_config["allowed_extensions"] == ["jpg", "png"]
        assert validator_config["strict_mode"] is True

    def test_model_serialization(self):
        """Test model can be serialized and deserialized."""
        original_config = LimitsConfig(
            max_upload_mb=30.0,
            max_memory_mb=10.0,
            enabled=True,
            strict_mode=True,
        )
        
        # Serialize to dict
        config_dict = original_config.model_dump()
        
        # Deserialize back
        restored_config = LimitsConfig(**config_dict)
        
        assert restored_config.max_upload_mb == 30.0
        assert restored_config.max_memory_mb == 10.0
        assert restored_config.enabled is True
        assert restored_config.strict_mode is True

    def test_megabyte_to_byte_conversion(self):
        """Test that megabyte values are correctly converted to bytes."""
        config = LimitsConfig(
            max_upload_mb=1.5,   # 1.5MB
            max_memory_mb=0.5,   # 0.5MB
            max_request_mb=2.0,  # 2MB
        )
        
        settings = config.to_django_settings()
        
        assert settings["FILE_UPLOAD_MAX_MEMORY_SIZE"] == int(0.5 * 1024 * 1024)  # 512KB
        assert settings["LIMITS_CONFIG"]["max_upload_bytes"] == int(1.5 * 1024 * 1024)  # 1.5MB
        assert settings["LIMITS_CONFIG"]["max_request_bytes"] == int(2.0 * 1024 * 1024)  # 2MB


class TestLimitsConfigIntegration:
    """Integration tests for limits configuration."""

    def test_realistic_development_config(self):
        """Test a realistic development configuration."""
        config = LimitsConfig(
            max_upload_mb=50.0,  # 50MB for dev
            max_memory_mb=10.0,  # 10MB
            max_request_mb=100.0,  # 100MB
            allowed_extensions=["jpg", "jpeg", "png", "gif", "pdf", "txt", "docx"],
            request_timeout=60,  # Longer timeout for dev
            enabled=True,
            strict_mode=True,  # Strict in development
        )
        
        # Should not raise any validation errors
        assert config.enabled is True
        assert config.strict_mode is True
        
        # Generate Django settings
        settings = config.to_django_settings()
        assert len(settings) > 0
        assert settings["FILE_UPLOAD_MAX_MEMORY_SIZE"] == 10 * 1024 * 1024

    def test_realistic_production_config(self):
        """Test a realistic production configuration."""
        config = LimitsConfig(
            max_upload_mb=10.0,  # 10MB for prod
            max_memory_mb=2.0,   # 2MB
            max_request_mb=15.0, # 15MB
            allowed_extensions=["jpg", "jpeg", "png", "pdf"],  # Limited types
            request_timeout=30,  # Shorter timeout
            enabled=True,
            strict_mode=False,  # Less strict in production
        )
        
        # Should not raise any validation errors
        assert config.enabled is True
        assert config.strict_mode is False
        
        # Generate Django settings
        settings = config.to_django_settings()
        assert len(settings) > 0
        assert settings["DATA_UPLOAD_MAX_NUMBER_FIELDS"] == 1000

    def test_minimal_config(self):
        """Test minimal configuration with defaults."""
        config = LimitsConfig()
        
        # Should work with all defaults
        settings = config.to_django_settings()
        assert len(settings) > 0
        assert "LIMITS_CONFIG" in settings
        assert settings["LIMITS_CONFIG"]["enabled"] is True

    def test_disabled_config(self):
        """Test disabled configuration."""
        config = LimitsConfig(enabled=False)
        
        # Should return empty settings
        settings = config.to_django_settings()
        assert settings == {}

    def test_custom_extensions_override_defaults(self):
        """Test that custom extensions override smart defaults."""
        config = LimitsConfig(
            allowed_extensions=["jpg", "png"],  # Only these two
            blocked_extensions=["exe"],         # Only this one
        )
        
        settings = config.to_django_settings()
        
        # Should use custom values, not smart defaults
        assert settings["ALLOWED_FILE_EXTENSIONS"] == ["jpg", "png"]
        assert settings["BLOCKED_FILE_EXTENSIONS"] == ["exe"]

    def test_fractional_megabytes(self):
        """Test that fractional megabytes work correctly."""
        config = LimitsConfig(
            max_upload_mb=2.5,   # 2.5MB
            max_memory_mb=1.25,  # 1.25MB
        )
        
        settings = config.to_django_settings()
        
        # Check byte conversion
        assert settings["FILE_UPLOAD_MAX_MEMORY_SIZE"] == int(1.25 * 1024 * 1024)
        assert settings["LIMITS_CONFIG"]["max_upload_bytes"] == int(2.5 * 1024 * 1024)