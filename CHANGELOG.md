# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.25] - 2025-09-24

### Added
- **Payment System Enhancements**: Unified payment provider configurations
  - New `PaymentsConfig` model with provider-specific settings
  - Enhanced validation utilities for API keys and subscription access
  - Improved webhook handling and reliability
  - Support for multiple payment providers (NowPayments, Cryptomus, etc.)
- **Template System**: Enhanced project template management
  - Improved template extraction and project name replacement
  - Better integration with CLI `create-project` command
  - More reliable template archiving system

### Changed
- **Project Structure**: Reorganized template location
  - Moved Django sample project to `examples/django_sample`
  - Improved template packaging for better distribution
- **Dependencies**: Updated dependency management
  - Better version constraint handling
  - Improved package compatibility

### Fixed
- **Payment Validation**: Enhanced security for payment processing
  - Improved API key validation
  - Better webhook verification
  - Fixed subscription access control issues
- **CLI Tools**: Improved reliability of project creation
  - Fixed template extraction issues
  - Better error handling for project setup
  - Improved project name replacement logic

### Security
- **Payment Processing**: Enhanced security measures
  - Stronger API key validation
  - Improved webhook verification
  - Better access control for subscription features

## [Previous Versions]

### [1.2.24] and earlier
- Core Django-CFG functionality
- Basic payment provider support
- Configuration management system
- CLI tools for project creation
- Health monitoring modules
- Database and Redis integration

---

**Note**: This changelog focuses on user-facing features and API changes in the Django-CFG package.