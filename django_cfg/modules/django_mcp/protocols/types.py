"""MCP Protocol Type Definitions."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class MCPServerInfo(BaseModel):
    """Server information for initialize response."""
    name: str
    version: str


class MCPCapabilities(BaseModel):
    """Server capabilities for initialize response."""
    logging: Optional[Dict[str, Any]] = None
    prompts: Optional[Dict[str, Any]] = None
    resources: Optional[Dict[str, Any]] = None
    tools: Optional[Dict[str, Any]] = None


class MCPInitializeResult(BaseModel):
    """Result of MCP initialize handshake."""
    protocolVersion: str = "2025-03-26"
    capabilities: MCPCapabilities
    serverInfo: MCPServerInfo


class MCPToolDefinition(BaseModel):
    """Definition of an MCP tool exposed to agents."""
    name: str
    description: str
    inputSchema: Dict[str, Any]  # JSON Schema for tool parameters


class MCPResourceDefinition(BaseModel):
    """Definition of an MCP resource."""
    uri: str
    name: str
    description: str
    mimeType: str = "application/json"


class MCPToolCallResult(BaseModel):
    """Result of an MCP tool execution."""
    content: List[Dict[str, Any]]
    isError: bool = False
