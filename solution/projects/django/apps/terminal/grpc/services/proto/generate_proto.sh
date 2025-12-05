#!/bin/bash
# Terminal gRPC Proto Generator
#
# Generates:
# 1. Python files for Django gRPC server
# 2. TypeScript files for grpc-terminal package
#
# Usage: ./generate_proto.sh
#
# Version: 2.0.0
# Date: 2025-12-04

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================"
echo "Terminal gRPC Proto Generator"
echo "============================================"

# Paths
PROTO_DIR="$SCRIPT_DIR"
GENERATED_DIR="$SCRIPT_DIR/../generated"

# grpc-terminal package paths
PACKAGE_DIR="$SCRIPT_DIR/../../../../../../frontend/packages/grpc-terminal"
PACKAGE_PROTO_DIR="$PACKAGE_DIR/src/grpc/proto"
PACKAGE_GENERATED_DIR="$PACKAGE_DIR/src/grpc/generated"

# ============================================
# 1. Generate Python files for Django
# ============================================
echo ""
echo "1. Generating Python files for Django..."

# Clean and create output directory
rm -rf "$GENERATED_DIR"
mkdir -p "$GENERATED_DIR"
touch "$GENERATED_DIR/__init__.py"

# Find all proto files
PROTO_FILES=$(find . -name "*.proto" -type f)

# Generate for each proto file
while IFS= read -r proto_file; do
    [ -z "$proto_file" ] && continue

    echo "   Processing: $(basename "$proto_file")"

    # Generate Python and gRPC Python files with type stubs
    python -m grpc_tools.protoc \
        -I. \
        --python_out="$GENERATED_DIR" \
        --grpc_python_out="$GENERATED_DIR" \
        --pyi_out="$GENERATED_DIR" \
        "$proto_file" || { echo "   ERROR: Failed to generate $proto_file"; exit 1; }

    echo "   ✅ $(basename "$proto_file")"
done <<< "$PROTO_FILES"

# Fix relative imports in generated files
echo ""
echo "   Fixing Python imports..."

# Fix imports in *_grpc.py files
find "$GENERATED_DIR" -name "*_grpc.py" | while read -r f; do
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' 's/^import \(.*_pb2\) as/from . import \1 as/' "$f"
    else
        sed -i 's/^import \(.*_pb2\) as/from . import \1 as/' "$f"
    fi
done

# Fix imports in *_pb2.py files (cross-proto imports)
find "$GENERATED_DIR" -name "*_pb2.py" | while read -r f; do
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' 's/^import \(.*_pb2\) as/from . import \1 as/' "$f"
    else
        sed -i 's/^import \(.*_pb2\) as/from . import \1 as/' "$f"
    fi
done

echo "   ✅ Python imports fixed"

# ============================================
# 2. Generate TypeScript files for grpc-terminal package
# ============================================
echo ""
echo "2. Generating TypeScript files for grpc-terminal package..."

# Check if package directory exists
if [ ! -d "$PACKAGE_DIR" ]; then
    echo "   ⚠️  Package directory not found: $PACKAGE_DIR"
    echo "   Creating package structure..."
    mkdir -p "$PACKAGE_PROTO_DIR"
    mkdir -p "$PACKAGE_GENERATED_DIR"
fi

# Create directories
mkdir -p "$PACKAGE_PROTO_DIR"
mkdir -p "$PACKAGE_GENERATED_DIR"

# Copy proto files to package
echo "   Copying proto files..."
while IFS= read -r proto_file; do
    [ -z "$proto_file" ] && continue
    cp "$proto_file" "$PACKAGE_PROTO_DIR/"
done <<< "$PROTO_FILES"
echo "   ✅ Proto files copied to package"

# Generate TypeScript files
echo "   Generating TypeScript files..."

# Check if @protobuf-ts/plugin is installed in package
if [ -f "$PACKAGE_DIR/node_modules/.bin/protoc-gen-ts" ]; then
    PROTOC_GEN_TS="$PACKAGE_DIR/node_modules/.bin/protoc-gen-ts"
elif [ -f "$PACKAGE_DIR/../../node_modules/.bin/protoc-gen-ts" ]; then
    PROTOC_GEN_TS="$PACKAGE_DIR/../../node_modules/.bin/protoc-gen-ts"
else
    # Try npx from package directory
    cd "$PACKAGE_DIR"

    npx protoc \
        --ts_out="$PACKAGE_GENERATED_DIR" \
        --ts_opt=generate_dependencies \
        --ts_opt=long_type_string \
        --proto_path="$PACKAGE_PROTO_DIR" \
        "$PACKAGE_PROTO_DIR"/*.proto 2>&1 && {
        echo "   ✅ TypeScript files generated"
    } || {
        echo "   ⚠️  TypeScript generation failed"
        echo "   Installing @protobuf-ts/plugin..."
        pnpm add -D @protobuf-ts/plugin @protobuf-ts/runtime @protobuf-ts/runtime-rpc @protobuf-ts/grpc-transport

        # Retry generation
        npx protoc \
            --ts_out="$PACKAGE_GENERATED_DIR" \
            --ts_opt=generate_dependencies \
            --ts_opt=long_type_string \
            --proto_path="$PACKAGE_PROTO_DIR" \
            "$PACKAGE_PROTO_DIR"/*.proto 2>&1 && {
            echo "   ✅ TypeScript files generated (after install)"
        } || {
            echo "   ❌ TypeScript generation failed"
        }
    }

    cd "$SCRIPT_DIR"
fi

# ============================================
# Summary
# ============================================
echo ""
echo "============================================"
echo "Generation complete!"
echo "============================================"
echo ""
echo "Python files: $GENERATED_DIR"
ls -la "$GENERATED_DIR" | grep -E "\.py$|\.pyi$" || true
echo ""

if [ -d "$PACKAGE_GENERATED_DIR" ]; then
    echo "TypeScript files: $PACKAGE_GENERATED_DIR"
    ls -la "$PACKAGE_GENERATED_DIR" 2>/dev/null | grep -E "\.ts$|\.js$" || echo "   (no files yet)"
fi

echo ""
echo "Done!"
