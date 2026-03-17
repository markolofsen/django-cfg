"""
gRPC Connections page — REMOVED.

This page previously displayed grpc_connection_states and grpc_connection_events
from D1. Those 3 tables were dropped because the write path was never wired:
  services/connection_state/ (amark_connected_safe / amark_disconnected_safe /
  amark_error_safe) was dead code — never called from streaming handlers.
  Tables were always empty in production.

Connection state tracking belongs in Redis / in-process memory, not D1.
If real-time connection visibility is needed in the future, wire up a proper
Redis-backed presence system and build a new Streamlit page on top of that.
"""

from __future__ import annotations

import streamlit as st


def render_grpc_connections() -> None:
    st.title("gRPC Connections")
    st.info(
        "Connection state tracking was removed: the underlying D1 tables "
        "(grpc_connection_states, grpc_connection_events, grpc_connection_metrics) "
        "were always empty because the write path was never connected to the "
        "streaming handlers. Use grpc_request_logs (Overview page) for request-level "
        "audit data instead."
    )
