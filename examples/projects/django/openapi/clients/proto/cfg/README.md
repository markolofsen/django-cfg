# Protocol Buffer Definitions

Generated from OpenAPI specification for package `cfg.v1`

## Structure

Each service has its own folder containing:
- `messages.proto` - Message definitions (models)
- `service.proto` - Service and RPC definitions

## Services

- **Auth**: `accounts__auth/` (1 operations)
- **Bulk Email**: `newsletter__bulk_email/` (1 operations)
- **Campaigns**: `newsletter__campaigns/` (6 operations)
- **Centrifugo Admin API**: `centrifugo__centrifugo_admin_api/` (12 operations)
- **Centrifugo Monitoring**: `centrifugo__centrifugo_monitoring/` (8 operations)
- **Centrifugo Testing**: `centrifugo__centrifugo_testing/` (8 operations)
- **Dashboard - API Zones**: `dashboard__dashboard_api_zones/` (2 operations)
- **Dashboard - Activity**: `dashboard__dashboard_activity/` (2 operations)
- **Dashboard - Charts**: `dashboard__dashboard_charts/` (4 operations)
- **Dashboard - Commands**: `dashboard__dashboard_commands/` (2 operations)
- **Dashboard - Overview**: `dashboard__dashboard_overview/` (1 operations)
- **Dashboard - Statistics**: `dashboard__dashboard_statistics/` (3 operations)
- **Dashboard - System**: `dashboard__dashboard_system/` (2 operations)
- **Lead Submission**: `leads__lead_submission/` (1 operations)
- **Logs**: `newsletter__logs/` (1 operations)
- **Newsletters**: `newsletter__newsletters/` (2 operations)
- **Subscriptions**: `newsletter__subscriptions/` (3 operations)
- **Testing**: `newsletter__testing/` (1 operations)
- **User Profile**: `accounts__user_profile/` (6 operations)
- **accounts**: `accounts/` (2 operations)
- **centrifugo**: `centrifugo/` (2 operations)
- **endpoints**: `endpoints/` (3 operations)
- **health**: `health/` (2 operations)
- **knowbase**: `knowbase/` (57 operations)
- **leads**: `leads/` (6 operations)
- **newsletter**: `newsletter/` (3 operations)
- **payments**: `payments/` (8 operations)
- **support**: `support/` (12 operations)
- **tasks**: `tasks/` (10 operations)

## Compilation

### Python (grpc_tools)
```bash
# Install dependencies
pip install grpcio grpcio-tools

# Compile each service
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. accounts__auth/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. newsletter__bulk_email/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. newsletter__campaigns/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. centrifugo__centrifugo_admin_api/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. centrifugo__centrifugo_monitoring/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. centrifugo__centrifugo_testing/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. dashboard__dashboard_api_zones/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. dashboard__dashboard_activity/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. dashboard__dashboard_charts/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. dashboard__dashboard_commands/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. dashboard__dashboard_overview/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. dashboard__dashboard_statistics/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. dashboard__dashboard_system/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. leads__lead_submission/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. newsletter__logs/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. newsletter__newsletters/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. newsletter__subscriptions/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. newsletter__testing/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. accounts__user_profile/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. accounts/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. centrifugo/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. endpoints/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. health/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. knowbase/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. leads/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. newsletter/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. payments/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. support/*.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. tasks/*.proto
```

### Go
```bash
# Install dependencies
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Compile each service
protoc -I. --go_out=. --go-grpc_out=. accounts__auth/*.proto
protoc -I. --go_out=. --go-grpc_out=. newsletter__bulk_email/*.proto
protoc -I. --go_out=. --go-grpc_out=. newsletter__campaigns/*.proto
protoc -I. --go_out=. --go-grpc_out=. centrifugo__centrifugo_admin_api/*.proto
protoc -I. --go_out=. --go-grpc_out=. centrifugo__centrifugo_monitoring/*.proto
protoc -I. --go_out=. --go-grpc_out=. centrifugo__centrifugo_testing/*.proto
protoc -I. --go_out=. --go-grpc_out=. dashboard__dashboard_api_zones/*.proto
protoc -I. --go_out=. --go-grpc_out=. dashboard__dashboard_activity/*.proto
protoc -I. --go_out=. --go-grpc_out=. dashboard__dashboard_charts/*.proto
protoc -I. --go_out=. --go-grpc_out=. dashboard__dashboard_commands/*.proto
protoc -I. --go_out=. --go-grpc_out=. dashboard__dashboard_overview/*.proto
protoc -I. --go_out=. --go-grpc_out=. dashboard__dashboard_statistics/*.proto
protoc -I. --go_out=. --go-grpc_out=. dashboard__dashboard_system/*.proto
protoc -I. --go_out=. --go-grpc_out=. leads__lead_submission/*.proto
protoc -I. --go_out=. --go-grpc_out=. newsletter__logs/*.proto
protoc -I. --go_out=. --go-grpc_out=. newsletter__newsletters/*.proto
protoc -I. --go_out=. --go-grpc_out=. newsletter__subscriptions/*.proto
protoc -I. --go_out=. --go-grpc_out=. newsletter__testing/*.proto
protoc -I. --go_out=. --go-grpc_out=. accounts__user_profile/*.proto
protoc -I. --go_out=. --go-grpc_out=. accounts/*.proto
protoc -I. --go_out=. --go-grpc_out=. centrifugo/*.proto
protoc -I. --go_out=. --go-grpc_out=. endpoints/*.proto
protoc -I. --go_out=. --go-grpc_out=. health/*.proto
protoc -I. --go_out=. --go-grpc_out=. knowbase/*.proto
protoc -I. --go_out=. --go-grpc_out=. leads/*.proto
protoc -I. --go_out=. --go-grpc_out=. newsletter/*.proto
protoc -I. --go_out=. --go-grpc_out=. payments/*.proto
protoc -I. --go_out=. --go-grpc_out=. support/*.proto
protoc -I. --go_out=. --go-grpc_out=. tasks/*.proto
```

### TypeScript (ts-proto)
```bash
# Install dependencies
npm install ts-proto

# Compile each service
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. accounts__auth/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. newsletter__bulk_email/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. newsletter__campaigns/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. centrifugo__centrifugo_admin_api/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. centrifugo__centrifugo_monitoring/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. centrifugo__centrifugo_testing/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. dashboard__dashboard_api_zones/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. dashboard__dashboard_activity/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. dashboard__dashboard_charts/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. dashboard__dashboard_commands/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. dashboard__dashboard_overview/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. dashboard__dashboard_statistics/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. dashboard__dashboard_system/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. leads__lead_submission/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. newsletter__logs/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. newsletter__newsletters/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. newsletter__subscriptions/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. newsletter__testing/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. accounts__user_profile/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. accounts/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. centrifugo/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. endpoints/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. health/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. knowbase/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. leads/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. newsletter/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. payments/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. support/*.proto
protoc -I. --plugin=./node_modules/.bin/protoc-gen-ts_proto --ts_proto_out=. tasks/*.proto
```

## Usage Example

After compilation, you can use the generated clients in your application.

### Python
```python
import grpc
from cfg_v1 import service_pb2, service_pb2_grpc

# Create channel
channel = grpc.insecure_channel('localhost:50051')

# Create stub
stub = service_pb2_grpc.YourServiceStub(channel)

# Make request
request = service_pb2.YourRequest(field='value')
response = stub.YourMethod(request)
```

---

*Generated by django-cfg django_client module*