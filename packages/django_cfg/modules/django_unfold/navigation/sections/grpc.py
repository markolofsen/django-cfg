from django_cfg.modules.django_admin.icons import Icons
from django_cfg.modules.django_unfold.models.navigation import NavigationSection
from django_cfg.modules.django_unfold.navigation.builder import NavBuilder


def build_grpc_section() -> NavigationSection:
    return NavigationSection(
        title="gRPC",
        separator=True,
        collapsible=True,
        items=[
            NavBuilder.direct_item("Monitor", Icons.MONITOR_HEART, "/cfg/admin/admin/dashboard/grpc/"),
            NavBuilder.item("Request Logs", Icons.LIST_ALT, "grpc", "grpcrequestlog"),
            NavBuilder.item("API Keys", Icons.KEY, "grpc", "grpcapikey"),
            NavBuilder.item("Server Status", Icons.HEALTH_AND_SAFETY, "grpc", "grpcserverstatus"),
            NavBuilder.item("Agent Connections", Icons.WIFI, "grpc", "grpcagentconnectionstate"),
            NavBuilder.item("Connection Events", Icons.TIMELINE, "grpc", "grpcagentconnectionevent"),
            NavBuilder.item("Connection Metrics", Icons.ANALYTICS, "grpc", "grpcagentconnectionmetric"),
        ],
    )
