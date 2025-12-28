"""
Admin interface for gRPC app.
"""

from .config import (
    grpcapikey_config,
    grpcrequestlog_config,
    grpcserverstatus_config,
    grpcagentconnectionstate_config,
    grpcagentconnectionevent_config,
    grpcagentconnectionmetric_config,
)
from .grpc_api_key import GrpcApiKeyAdmin
from .grpc_request_log import GRPCRequestLogAdmin
from .grpc_server_status import GRPCServerStatusAdmin
from .connection_state import (
    GrpcAgentConnectionStateAdmin,
    GrpcAgentConnectionEventAdmin,
    GrpcAgentConnectionMetricAdmin,
)

__all__ = [
    # Existing admins
    "GrpcApiKeyAdmin",
    "GRPCRequestLogAdmin",
    "GRPCServerStatusAdmin",
    # Connection state admins
    "GrpcAgentConnectionStateAdmin",
    "GrpcAgentConnectionEventAdmin",
    "GrpcAgentConnectionMetricAdmin",
    # Configs
    "grpcapikey_config",
    "grpcrequestlog_config",
    "grpcserverstatus_config",
    "grpcagentconnectionstate_config",
    "grpcagentconnectionevent_config",
    "grpcagentconnectionmetric_config",
]
