#!/bin/bash
# Generate Python code from proto files
# Usage: ./generate_proto.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROTO_DIR="$SCRIPT_DIR"
OUTPUT_DIR="$SCRIPT_DIR/../generated"

echo "🔧 Generating Python code from proto files..."
echo "   Proto dir: $PROTO_DIR"
echo "   Output dir: $OUTPUT_DIR"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Generate Python code
python -m grpc_tools.protoc \
    -I"$PROTO_DIR" \
    --python_out="$OUTPUT_DIR" \
    --grpc_python_out="$OUTPUT_DIR" \
    --pyi_out="$OUTPUT_DIR" \
    "$PROTO_DIR"/*.proto

echo "✅ Proto generation complete!"
echo "   Generated files in: $OUTPUT_DIR"

