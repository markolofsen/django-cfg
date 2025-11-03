#!/bin/bash
#
# Generate Python code from proto files
#
# Usage:
#   ./generate_proto.sh
#

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROTO_DIR="$SCRIPT_DIR/proto"
OUTPUT_DIR="$SCRIPT_DIR/generated"

echo "🔨 Generating Python code from proto files..."
echo "   Proto dir: $PROTO_DIR"
echo "   Output dir: $OUTPUT_DIR"
echo ""

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Generate Python code
python -m grpc_tools.protoc \
    -I"$PROTO_DIR" \
    --python_out="$OUTPUT_DIR" \
    --grpc_python_out="$OUTPUT_DIR" \
    "$PROTO_DIR"/*.proto

echo "✅ Generated files:"
ls -lh "$OUTPUT_DIR"/*_pb2*.py

# Fix imports in generated _grpc.py files (make them relative)
echo ""
echo "🔧 Fixing imports in generated gRPC files..."
for file in "$OUTPUT_DIR"/*_pb2_grpc.py; do
    if [ -f "$file" ]; then
        # Fix: import xxx_pb2 -> from . import xxx_pb2
        sed -i.bak 's/^import \([a-z_]*_pb2\) as/from . import \1 as/g' "$file"
        rm "$file.bak"
        echo "   Fixed: $(basename $file)"
    fi
done

echo ""
echo "✅ Proto generation complete!"
