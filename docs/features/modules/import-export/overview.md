---
title: Import/Export Overview
description: Django-CFG overview feature guide. Production-ready import/export overview with built-in validation, type safety, and seamless Django integration.
sidebar_label: Overview & Philosophy
sidebar_position: 1
keywords:
  - django-cfg overview
  - django overview
  - overview django-cfg
---

# Import/Export Module

Django-CFG includes a **seamless integration with django-import-export** that provides beautiful admin interfaces for importing and exporting data with zero configuration overhead.

## Overview

The Django Import/Export module provides:
- **Registry integration** - Access components through django-cfg imports
- **Unfold styling** - Automatic beautiful admin interface styling
- **Zero overhead** - Direct re-exports without unnecessary wrappers
- **Full compatibility** - 100% compatible with original django-import-export
- **Admin integration** - Ready-to-use admin classes and mixins

## Quick Start

### Installation

```bash
# Install django-import-export (required dependency)
pip install django-import-export
```

### Basic Usage

```python
from django_cfg import ImportExportModelAdmin, BaseResource
from django.contrib import admin
from .models import Vehicle

class VehicleResource(BaseResource):
    class Meta:
        model = Vehicle
        fields = ('id', 'brand', 'model', 'year', 'price', 'mileage')
        export_order = ('id', 'brand', 'model', 'year', 'price', 'mileage')

@admin.register(Vehicle)
class VehicleAdmin(ImportExportModelAdmin):
    resource_class = VehicleResource
    list_display = ('brand', 'model', 'year', 'price')
    list_filter = ('brand', 'year')
    search_fields = ('brand', 'model')
```

## Available Components

### Admin Classes

```python
from django_cfg import ImportExportMixin, ImportExportModelAdmin

# Mixin for existing admin classes
class MyExistingAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = MyResource
    # ... existing admin configuration

# Complete admin class with import/export
class MyModelAdmin(ImportExportModelAdmin):
    resource_class = MyResource
    list_display = ('name', 'created_at')
```

### Forms

```python
from django_cfg import ImportForm, ExportForm, SelectableFieldsExportForm

# Standard import form
class CustomImportForm(ImportForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Custom form modifications

# Export form with field selection
class CustomExportForm(SelectableFieldsExportForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Custom export options
```

### Resources

```python
from django_cfg import BaseResource
from import_export import fields, widgets

class ProductResource(BaseResource):
    # Custom field with widget
    category_name = fields.Field(
        column_name='category',
        attribute='category__name',
        widget=widgets.ForeignKeyWidget(Category, 'name')
    )
    
    # Calculated field
    total_value = fields.Field(
        column_name='total_value',
        attribute='total_value',
        readonly=True
    )
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'category_name', 'price', 'quantity', 'total_value')
        export_order = fields
        
    def dehydrate_total_value(self, product):
        """Calculate total value for export"""
        return product.price * product.quantity
    
    def before_import_row(self, row, **kwargs):
        """Modify row data before import"""
        # Convert price to decimal
        if 'price' in row:
            row['price'] = float(row['price'].replace(',', '.'))
```

## Advanced Features

### Custom Import/Export Workflows

```python
from django_cfg import BaseResource
from import_export.results import Result

class AdvancedProductResource(BaseResource):
    class Meta:
        model = Product
        fields = ('name', 'category', 'price', 'supplier_code')
        
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """Pre-process entire dataset"""
        # Validate dataset structure
        required_columns = ['name', 'price']
        missing_columns = [col for col in required_columns if col not in dataset.headers]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
    
    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        """Post-process after import"""
        if not dry_run and not result.has_errors():
            # Send notification about successful import
            self.send_import_notification(result.totals)
    
    def send_import_notification(self, totals):
        """Send notification about import results"""
        from django_cfg.modules.django_email import send_email
        
        send_email(
            subject=f"Import completed: {totals['new']} new, {totals['update']} updated",
            message=f"Product import completed successfully.",
            recipient_list=['admin@company.com']
        )

    def skip_row(self, instance, original, row, import_validation_errors=None):
        """Skip rows based on custom logic"""
        # Skip products with invalid prices
        if hasattr(instance, 'price') and instance.price <= 0:
            return True
        return super().skip_row(instance, original, row, import_validation_errors)
```

### Batch Operations

```python
class BatchProductResource(BaseResource):
    class Meta:
        model = Product
        batch_size = 1000  # Process in batches of 1000
        use_bulk = True    # Use bulk operations for better performance
        
    def before_save_instance(self, instance, using_transactions, dry_run):
        """Modify instance before saving"""
        # Auto-generate SKU if not provided
        if not instance.sku:
            instance.sku = self.generate_sku(instance)
        
        # Set default category
        if not instance.category_id:
            instance.category = Category.objects.get(name='Uncategorized')
    
    def generate_sku(self, instance):
        """Generate unique SKU"""
        import uuid
        return f"PRD-{uuid.uuid4().hex[:8].upper()}"
```

### Multi-Format Export

```python
from django_cfg import BaseResource
from import_export.formats import base_formats

class MultiFormatResource(BaseResource):
    class Meta:
        model = Product
        
    def get_export_formats(self):
        """Define available export formats"""
        return [
            base_formats.CSV,
            base_formats.XLSX,
            base_formats.JSON,
            base_formats.YAML,
        ]
    
    def export(self, queryset=None, *args, **kwargs):
        """Custom export with additional processing"""
        dataset = super().export(queryset, *args, **kwargs)
        
        # Add metadata to export
        dataset.append_separator('# Export Metadata')
        dataset.append(['# Generated:', timezone.now().isoformat()])
        dataset.append(['# Total Records:', len(queryset) if queryset else 0])
        
        return dataset
```

## Real-World Examples

### E-commerce Product Import

```python
class EcommerceProductResource(BaseResource):
    # Custom fields for complex data
    category_path = fields.Field(
        column_name='category_path',
        attribute='category__get_full_path',
        widget=widgets.CharWidget()
    )
    
    tags = fields.Field(
        column_name='tags',
        attribute='tags',
        widget=widgets.ManyToManyWidget(Tag, field='name', separator='|')
    )
    
    class Meta:
        model = Product
        fields = (
            'sku', 'name', 'description', 'category_path', 
            'price', 'cost', 'weight', 'tags', 'is_active'
        )
        
    def before_import_row(self, row, **kwargs):
        """Process row before import"""
        # Handle category creation
        if 'category_path' in row:
            category = self.get_or_create_category(row['category_path'])
            row['category'] = category.id
            
        # Process tags
        if 'tags' in row and row['tags']:
            tag_names = row['tags'].split('|')
            tags = []
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name.strip())
                tags.append(tag.id)
            row['tags'] = '|'.join(map(str, tags))
    
    def get_or_create_category(self, category_path):
        """Create category hierarchy from path"""
        parts = category_path.split(' > ')
        parent = None
        
        for part in parts:
            category, created = Category.objects.get_or_create(
                name=part.strip(),
                parent=parent
            )
            parent = category
            
        return parent
```

### User Data Import with Validation

```python
class UserImportResource(BaseResource):
    email = fields.Field(
        column_name='email',
        attribute='email',
        widget=widgets.CharWidget()
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active')
        
    def before_import_row(self, row, **kwargs):
        """Validate and clean user data"""
        # Validate email format
        email = row.get('email', '').strip().lower()
        if email and not self.is_valid_email(email):
            raise ValueError(f"Invalid email format: {email}")
        row['email'] = email
        
        # Generate username from email if not provided
        if not row.get('username') and email:
            username = email.split('@')[0]
            # Ensure username is unique
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            row['username'] = username
    
    def is_valid_email(self, email):
        """Simple email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def after_save_instance(self, instance, using_transactions, dry_run):
        """Send welcome email to new users"""
        if not dry_run and instance.pk:
            from django_cfg.modules.django_email import send_template_email
            
            send_template_email(
                template='emails/welcome.html',
                context={'user': instance},
                recipient_list=[instance.email],
                subject='Welcome to our platform!'
            )
```

### Financial Data Export

```python
class FinancialReportResource(BaseResource):
    # Calculated fields for financial reporting
    revenue = fields.Field(
        column_name='revenue',
        attribute='revenue',
        readonly=True
    )
    
    profit_margin = fields.Field(
        column_name='profit_margin_percent',
        attribute='profit_margin_percent',
        readonly=True
    )
    
    class Meta:
        model = Order
        fields = (
            'id', 'order_date', 'customer__name', 'total_amount',
            'revenue', 'profit_margin', 'status'
        )
        
    def dehydrate_revenue(self, order):
        """Calculate revenue (excluding taxes and fees)"""
        return order.total_amount - order.tax_amount - order.processing_fee
    
    def dehydrate_profit_margin(self, order):
        """Calculate profit margin percentage"""
        revenue = self.dehydrate_revenue(order)
        cost = order.get_total_cost()
        if revenue > 0:
            return round(((revenue - cost) / revenue) * 100, 2)
        return 0
    
    def get_queryset(self):
        """Optimize queryset for export"""
        return super().get_queryset().select_related(
            'customer'
        ).prefetch_related(
            'items__product'
        )
```

## Admin Integration

### Custom Admin with Import/Export

```python
from django_cfg import ImportExportModelAdmin, BaseResource
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages

class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    
    # Standard admin configuration
    list_display = ('name', 'category', 'price', 'stock', 'is_active')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'sku')
    
    # Import/Export configuration
    import_template_name = 'admin/import_export/import.html'
    export_template_name = 'admin/import_export/export.html'
    
    def get_urls(self):
        """Add custom URLs for import/export"""
        urls = super().get_urls()
        custom_urls = [
            path(
                'bulk-update/',
                self.admin_site.admin_view(self.bulk_update_view),
                name='product_bulk_update'
            ),
        ]
        return custom_urls + urls
    
    def bulk_update_view(self, request):
        """Custom bulk update view"""
        if request.method == 'POST':
            # Handle bulk update logic
            updated_count = self.perform_bulk_update(request.FILES.get('file'))
            messages.success(
                request, 
                f'Successfully updated {updated_count} products.'
            )
            return redirect('..')
        
        return render(request, 'admin/product_bulk_update.html')
    
    def perform_bulk_update(self, file):
        """Perform bulk update from uploaded file"""
        # Implementation for bulk update
        pass
```

### Custom Import Form

```python
from django_cfg import ImportForm
from django import forms

class CustomProductImportForm(ImportForm):
    update_existing = forms.BooleanField(
        required=False,
        initial=True,
        help_text='Update existing products if SKU matches'
    )
    
    send_notifications = forms.BooleanField(
        required=False,
        initial=False,
        help_text='Send email notifications for new products'
    )
    
    category_default = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        help_text='Default category for products without category'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['input_format'].help_text = 'Select the format of your import file'

# Use custom form in admin
class ProductAdmin(ImportExportModelAdmin):
    import_form_class = CustomProductImportForm
```

## Configuration Options

### Module Configuration

```python
# config.py
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    # Import/Export settings
    import_export_use_transactions: bool = True
    import_export_skip_admin_log: bool = False
    import_export_tmp_storage_class: str = 'import_export.tmp_storages.TempFolderStorage'
    
    # Batch processing
    import_export_batch_size: int = 1000
    import_export_chunk_size: int = 100
    
    # File handling
    import_export_max_file_size: int = 10 * 1024 * 1024  # 10MB
    import_export_allowed_formats: list = ['csv', 'xlsx', 'json']
```

## 🧪 Testing Import/Export

### Test Resources

```python
from django.test import TestCase
from django_cfg import BaseResource
from .models import Product, Category

class ProductResourceTest(TestCase):
    def setUp(self):
        self.resource = ProductResource()
        self.category = Category.objects.create(name='Electronics')
    
    def test_import_product(self):
        """Test importing a single product"""
        dataset = Dataset()
        dataset.headers = ['name', 'category', 'price']
        dataset.append(['Laptop', 'Electronics', '999.99'])
        
        result = self.resource.import_data(dataset, dry_run=True)
        
        self.assertFalse(result.has_errors())
        self.assertEqual(result.totals['new'], 1)
    
    def test_export_products(self):
        """Test exporting products"""
        Product.objects.create(
            name='Laptop',
            category=self.category,
            price=999.99
        )
        
        dataset = self.resource.export()
        
        self.assertEqual(len(dataset), 1)
        self.assertIn('Laptop', dataset[0])
    
    def test_import_validation(self):
        """Test import validation"""
        dataset = Dataset()
        dataset.headers = ['name', 'price']
        dataset.append(['', '999.99'])  # Empty name should fail
        
        result = self.resource.import_data(dataset, dry_run=True)
        
        self.assertTrue(result.has_errors())
```

## Related Documentation

- [**Module System Overview**](./overview) - Django-CFG modules
- [**Admin Interface**](/fundamentals/system/utilities) - Admin customization
- [**Configuration Guide**](/fundamentals/configuration) - Module configuration
- [**Django Import-Export Docs**](https://django-import-export.readthedocs.io/) - Official documentation

The Import/Export module provides seamless data management for your Django applications! 📊

TAGS: import-export, admin, data-management, csv, xlsx, bulk-operations
DEPENDS_ON: [admin, configuration, unfold]
USED_BY: [data-migration, reporting, bulk-updates]
