---
title: Proto Generation
description: Automatic .proto file generation from Django models
sidebar_label: Proto Generation
sidebar_position: 5
keywords:
  - grpc proto generation
  - django models to protobuf
  - automatic proto files
---

# Automatic Proto Generation

Django-CFG can automatically generate `.proto` files from your Django models, eliminating the need to manually maintain Protocol Buffer definitions.

## Overview

The proto generator (`GRPCProtoConfig`) scans your Django models and creates corresponding `.proto` message definitions with appropriate field types and service definitions.

### How It Works

```
Django Model → Proto Generator → .proto file → protoc → Python stubs
```

1. **Django Model**: Define your model with Django ORM
2. **Proto Generator**: Analyzes model fields and types
3. **.proto File**: Generated Protocol Buffer definition
4. **protoc**: Compiles to Python gRPC stubs
5. **gRPC Service**: Ready to use in your application

---

## Configuration

### Basic Setup

```python
# api/config.py
from django_cfg import DjangoConfig, GRPCConfig, GRPCProtoConfig

class MyConfig(DjangoConfig):
    grpc: GRPCConfig = GRPCConfig(
        enabled=True,
        proto=GRPCProtoConfig(
            auto_generate=True,      # Enable automatic generation
            output_dir="protos",     # Output directory (relative to BASE_DIR)
            package_prefix="api",    # Package prefix for proto files
            include_services=True,   # Generate CRUD service definitions
            field_naming="snake_case" # Field naming convention
        ),
        auto_register_apps=True,
        enabled_apps=["myapp"],      # Apps to scan for models
    )
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `auto_generate` | `bool` | `True` | Enable automatic proto generation |
| `output_dir` | `str` | `"protos"` | Output directory (relative to `BASE_DIR`) |
| `package_prefix` | `str` | `""` | Package prefix (e.g., `"api"` → `package api.myapp;`) |
| `include_services` | `bool` | `True` | Generate gRPC service definitions (CRUD) |
| `field_naming` | `str` | `"snake_case"` | Field naming: `"snake_case"` or `"camelCase"` |

---

## Field Type Mapping

Django fields are automatically mapped to Protocol Buffer types:

| Django Field | Proto Type | Notes |
|--------------|-----------|-------|
| `CharField`, `TextField`, `EmailField`, `URLField` | `string` | All text fields |
| `IntegerField`, `SmallIntegerField` | `int32` | 32-bit integers |
| `BigIntegerField` | `int64` | 64-bit integers |
| `PositiveIntegerField` | `uint32` | Unsigned 32-bit |
| `FloatField` | `float` | Floating point |
| `DecimalField` | `string` | Preserves precision |
| `BooleanField` | `bool` | Boolean values |
| `DateField`, `DateTimeField`, `TimeField` | `string` | ISO 8601 format |
| `JSONField` | `string` | JSON as string |
| `BinaryField` | `bytes` | Binary data |
| `ForeignKey`, `OneToOneField` | `int64` | Related object ID |
| `ManyToManyField` | `repeated int64` | Array of IDs |

### Optional Fields

Fields are marked as `optional` if:
- `null=True`
- `blank=True`
- Field has a `default` value

---

## Example: From Model to Proto

### Django Model

```python
# apps/products/models.py
from django.db import models

class Product(models.Model):
    """Product model."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
```

### Generated Proto

```protobuf
syntax = "proto3";

package api.products;

import "google/protobuf/empty.proto";

message Product {
  int64 id = 1;
  string name = 2;
  optional string description = 3;      // blank=True → optional
  string price = 4;                     // DecimalField → string
  optional int32 stock = 5;             // has default → optional
  optional bool is_active = 6;          // has default → optional
  int64 category = 7;                   // ForeignKey → int64
  repeated int64 tags = 8;              // ManyToManyField → repeated
  optional string created_at = 9;       // auto_now_add → optional
  optional string updated_at = 10;      // auto_now → optional
}

// CRUD service (if include_services=True)
service ProductService {
  rpc Create(CreateProductRequest) returns (Product);
  rpc Get(GetProductRequest) returns (Product);
  rpc Update(UpdateProductRequest) returns (Product);
  rpc Delete(DeleteProductRequest) returns (google.protobuf.Empty);
  rpc List(ListProductRequest) returns (ListProductResponse);
}
```

---

## Generating Proto Files

### Command Line

```bash
# Generate proto for specific app
python manage.py generate_protos --app products

# Generate for all enabled apps
python manage.py generate_protos --all

# Specify output directory
python manage.py generate_protos --app products --output protos/
```

### Programmatic Generation

```python
from django_cfg.apps.integrations.grpc.utils.proto_gen import generate_proto_for_app
from pathlib import Path

# Generate proto file
count = generate_proto_for_app(
    app_label='products',
    output_dir=Path('protos')
)
print(f"Generated {count} proto file(s)")
```

### Testing Generation

Use the provided test script:

```bash
# Test proto generation
poetry run python test_grpc_proto.py
```

**Output:**
```
✅ Proto generation works correctly!
✅ File created: /protos/products.proto
📏 Size: 1234 bytes
```

---

## Compiling Proto Files

After generation, compile `.proto` files to Python:

```bash
# Navigate to proto directory
cd protos/

# Compile with protoc
python -m grpc_tools.protoc \
  -I. \
  --python_out=. \
  --grpc_python_out=. \
  products.proto

# This generates:
# - products_pb2.py         (message classes)
# - products_pb2_grpc.py    (service stubs)
```

### Automated Compilation

Add to your build process:

```python
# manage.py or build script
import subprocess
from pathlib import Path

def compile_protos():
    """Compile all .proto files."""
    protos_dir = Path('protos')
    proto_files = protos_dir.glob('*.proto')

    for proto_file in proto_files:
        subprocess.run([
            'python', '-m', 'grpc_tools.protoc',
            f'-I{protos_dir}',
            f'--python_out={protos_dir}',
            f'--grpc_python_out={protos_dir}',
            str(proto_file)
        ], check=True)

    print(f"✅ Compiled {len(list(proto_files))} proto file(s)")
```

---

## Advanced Usage

### Custom Field Naming

```python
proto=GRPCProtoConfig(
    field_naming="camelCase"  # Convert snake_case to camelCase
)
```

**Result:**
```protobuf
message Product {
  int64 id = 1;
  string productName = 2;        // product_name → productName
  string currentPrice = 3;       // current_price → currentPrice
  optional string createdAt = 4; // created_at → createdAt
}
```

### Exclude Certain Models

```python
# apps/products/models.py
class Product(models.Model):
    # ... fields ...

    class Meta:
        # Exclude from proto generation
        grpc_exclude = True
```

### Custom Proto Package

```python
proto=GRPCProtoConfig(
    package_prefix="com.mycompany.api"
)
```

**Result:**
```protobuf
package com.mycompany.api.products;
```

### Disable Service Generation

```python
proto=GRPCProtoConfig(
    include_services=False  # Only generate message definitions
)
```

---

## Troubleshooting

### Issue: Proto File Not Generated

**Check:**
1. `auto_generate=True` in configuration
2. App is in `enabled_apps` list
3. Models exist in the app
4. Output directory is writable

**Debug:**
```python
from django.conf import settings
print(settings.GRPC_PROTO)
# Output: {'auto_generate': True, 'output_dir': 'protos', ...}
```

### Issue: Field Type Mismatch

**Problem:** Field mapped to wrong proto type

**Solution:** Create custom field mapper:

```python
from django_cfg.apps.integrations.grpc.utils.proto_gen import ProtoFieldMapper

class CustomProtoFieldMapper(ProtoFieldMapper):
    FIELD_TYPE_MAP = {
        **ProtoFieldMapper.FIELD_TYPE_MAP,
        models.MyCustomField: "string",  # Add custom mapping
    }
```

### Issue: Compilation Errors

**Problem:** `protoc` fails to compile generated files

**Check:**
1. Valid proto syntax
2. All imports exist
3. No duplicate field numbers
4. Field names are valid identifiers

**Validate:**
```bash
# Check proto syntax
protoc --decode_raw < products.proto

# List all messages
protoc --descriptor_set_out=/dev/stdout products.proto | protoc --decode_raw
```

---

## Best Practices

### 1. Version Control

**Include in Git:**
```gitignore
# .gitignore
protos/*.proto         # Include: source .proto files

# Exclude generated files
protos/*_pb2.py
protos/*_pb2_grpc.py
protos/__pycache__/
```

### 2. CI/CD Integration

```yaml
# .github/workflows/ci.yml
- name: Generate and compile protos
  run: |
    poetry run python test_grpc_proto.py
    cd protos && python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. *.proto
```

### 3. Keep Models Clean

```python
# Good: Simple, clear models
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)

# Avoid: Complex computed properties, methods that should be services
class Product(models.Model):
    # ... fields ...

    @property
    def discounted_price(self):  # Won't be in proto
        return self.price * 0.9
```

### 4. Document Proto Files

Add comments to your Django models:

```python
class Product(models.Model):
    """Product information.

    Proto: Products.Product
    """
    name = models.CharField(
        max_length=200,
        help_text="Product display name"  # Add to docstrings
    )
```

---

## Testing

### Unit Tests

```python
# tests/test_proto_generation.py
from django.test import TestCase
from django_cfg.apps.integrations.grpc.utils.proto_gen import ProtoGenerator
from apps.products.models import Product

class ProtoGenerationTest(TestCase):
    def test_generate_product_message(self):
        """Test proto generation for Product model."""
        generator = ProtoGenerator(package_prefix="api")
        proto_content = generator.generate_message(Product)

        self.assertIn("message Product", proto_content)
        self.assertIn("string name", proto_content)
        self.assertIn("string price", proto_content)

    def test_field_types(self):
        """Test field type mapping."""
        from django_cfg.apps.integrations.grpc.utils.proto_gen import ProtoFieldMapper

        mapper = ProtoFieldMapper()

        # Test mappings
        from django.db import models
        self.assertEqual(mapper.get_proto_type(models.CharField()), "string")
        self.assertEqual(mapper.get_proto_type(models.IntegerField()), "int32")
        self.assertEqual(mapper.get_proto_type(models.DecimalField()), "string")
```

### Integration Tests

```bash
# Run full proto generation test
poetry run python test_grpc_proto.py

# Expected output:
# ✅ Proto generation works correctly!
# ✅ File created: /protos/products.proto
```

---

## Example: Complete Workflow

### 1. Define Model

```python
# apps/shop/models.py
class Order(models.Model):
    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
```

### 2. Configure Generation

```python
# api/config.py
grpc=GRPCConfig(
    enabled=True,
    proto=GRPCProtoConfig(
        auto_generate=True,
        output_dir="protos",
        package_prefix="shop",
    ),
    enabled_apps=["shop"],
)
```

### 3. Generate Proto

```bash
poetry run python test_grpc_proto.py
# ✅ Generated: protos/shop.proto
```

### 4. Compile

```bash
cd protos/
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. shop.proto
# ✅ Generated: shop_pb2.py, shop_pb2_grpc.py
```

### 5. Use in Service

```python
# apps/shop/grpc_services.py
from django_cfg.apps.integrations.grpc.services import BaseService
import shop_pb2
import shop_pb2_grpc

class OrderService(BaseService):
    """Order gRPC service."""

    def GetOrder(self, request, context):
        order = Order.objects.get(id=request.id)
        return shop_pb2.Order(
            id=order.id,
            order_number=order.order_number,
            customer=order.customer_id,
            total_amount=str(order.total_amount),
            status=order.status,
        )
```

---

## Next Steps

- [Configuration Reference](./configuration.md) - All configuration options
- [Getting Started](./getting-started.md) - Build your first service
- [Best Practices](./faq.md#best-practices) - Production tips

---

**Last Updated:** 2025-11-04
**Django-CFG Version:** 1.5.8+
