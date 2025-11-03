# Generated Proto Files

This directory contains auto-generated Python code from Protocol Buffer definitions.

**⚠️ DO NOT EDIT FILES IN THIS DIRECTORY MANUALLY**

## Files

- `crypto_service_pb2.py` - Generated message classes
- `crypto_service_pb2_grpc.py` - Generated service stubs and servicers

## Regenerating

To regenerate these files after changing `.proto` files:

```bash
cd ..  # Go to grpc_services directory
./generate_proto.sh
```

Or manually:

```bash
python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./generated \
    --grpc_python_out=./generated \
    ./proto/crypto_service.proto
```

## Import Usage

These files are imported by the service implementation:

```python
from apps.crypto.grpc_services.generated import crypto_service_pb2, crypto_service_pb2_grpc
```

## Git

These files are git-ignored (`.gitignore`) and should be regenerated on each environment.
