"""
Swift Codable Generator - Main generator for Swift Codable types.

Generates simple Swift Codable structs and APIEndpoints from IR.
No OpenAPIRuntime dependency required.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import BaseGenerator, GeneratedFile
from .type_mapper import SwiftTypeMapper
from .models_generator import SwiftModelsGenerator
from .endpoints_generator import SwiftEndpointsGenerator

if TYPE_CHECKING:
    from django_cfg.modules.django_client.core.ir import IRContext, IROperationObject, IRSchemaObject


class SwiftCodableGenerator(BaseGenerator):
    """
    Swift Codable generator for iOS apps.

    Generates:
    - APIEndpoints.swift: API path constants organized by resource
    - {Group}Types.swift: Codable structs for each API group
    - PaginatedResponse.swift: Generic paginated response wrapper

    No external dependencies - just Foundation and Swift standard library.
    """

    def __init__(
        self,
        context: IRContext,
        generate_endpoints: bool = True,
        generate_models: bool = True,
        **kwargs,
    ):
        """
        Initialize Swift Codable generator.

        Args:
            context: IRContext from parser
            generate_endpoints: Whether to generate APIEndpoints.swift
            generate_models: Whether to generate model types
            **kwargs: Additional arguments passed to BaseGenerator
        """
        super().__init__(context, **kwargs)

        self.generate_endpoints_file = generate_endpoints
        self.generate_models_file = generate_models

        # Initialize sub-generators
        self.type_mapper = SwiftTypeMapper()
        self.models_generator = SwiftModelsGenerator(self.type_mapper)
        self.endpoints_generator = SwiftEndpointsGenerator()

    def generate(self) -> list[GeneratedFile]:
        """
        Generate all Swift files.

        Returns:
            List of GeneratedFile objects
        """
        files = []

        # Group operations by tag
        ops_by_tag = self.group_operations_by_tag()

        # Generate APIEndpoints.swift (combined for all groups)
        if self.generate_endpoints_file:
            endpoints_file = self._generate_endpoints_file(ops_by_tag)
            files.append(endpoints_file)

        # Generate model types for each group
        if self.generate_models_file:
            models_file = self._generate_models_file()
            files.append(models_file)

        # Generate CLAUDE.md documentation
        claude_file = self._generate_claude_md(ops_by_tag)
        files.append(claude_file)

        return files

    def _generate_endpoints_file(
        self,
        ops_by_tag: dict[str, list[IROperationObject]],
    ) -> GeneratedFile:
        """Generate APIEndpoints.swift."""
        group_name = self.group_name or "API"
        content = self.endpoints_generator.generate_endpoints(ops_by_tag, group_name)
        return GeneratedFile(
            path=f"{self._to_pascal_case(group_name)}Endpoints.swift",
            content=content,
            description="API endpoint path constants",
        )

    def _generate_models_file(self) -> GeneratedFile:
        """Generate Types.swift with all models."""
        group_name = self.group_name or "API"
        content = self.models_generator.generate_models(
            self.context.schemas,
            group_name,
        )
        return GeneratedFile(
            path=f"{self._to_pascal_case(group_name)}Types.swift",
            content=content,
            description=f"Codable types for {group_name} API",
        )

    @staticmethod
    def generate_shared_files() -> list[GeneratedFile]:
        """
        Generate shared Swift files (JSONValue, PaginatedResponse, etc.).

        These should be generated once and placed in a Shared folder,
        not per-group.
        """
        return [
            SwiftCodableGenerator._generate_json_value_file(),
            SwiftCodableGenerator._generate_paginated_response_file(),
        ]

    @staticmethod
    def _generate_paginated_response_file() -> GeneratedFile:
        """Generate PaginatedResponse.swift for generic pagination."""
        content = '''// PaginatedResponse.swift
// Auto-generated - Generic paginated response wrapper

import Foundation

/// Generic paginated response from Django REST Framework
public struct PaginatedResponse<T: Codable & Sendable>: Codable, Sendable {
    public let count: Int
    public let hasNext: Bool
    public let hasPrevious: Bool
    public let nextPage: Int?
    public let page: Int
    public let pageSize: Int
    public let pages: Int
    public let previousPage: Int?
    public let results: [T]

    enum CodingKeys: String, CodingKey {
        case count
        case hasNext = "has_next"
        case hasPrevious = "has_previous"
        case nextPage = "next_page"
        case page
        case pageSize = "page_size"
        case pages
        case previousPage = "previous_page"
        case results
    }

    public init(
        count: Int,
        hasNext: Bool,
        hasPrevious: Bool,
        nextPage: Int?,
        page: Int,
        pageSize: Int,
        pages: Int,
        previousPage: Int?,
        results: [T]
    ) {
        self.count = count
        self.hasNext = hasNext
        self.hasPrevious = hasPrevious
        self.nextPage = nextPage
        self.page = page
        self.pageSize = pageSize
        self.pages = pages
        self.previousPage = previousPage
        self.results = results
    }
}

// MARK: - Convenience Extensions

extension PaginatedResponse {
    /// Whether there are more pages to load
    public var hasMorePages: Bool { hasNext }

    /// Whether this is the first page
    public var isFirstPage: Bool { page == 1 }

    /// Whether this is the last page
    public var isLastPage: Bool { !hasNext }

    /// Whether the results are empty
    public var isEmpty: Bool { results.isEmpty }
}
'''
        return GeneratedFile(
            path="PaginatedResponse.swift",
            content=content,
            description="Generic paginated response wrapper",
        )

    @staticmethod
    def _generate_json_value_file() -> GeneratedFile:
        """Generate JSONValue.swift for dynamic JSON handling."""
        content = '''// JSONValue.swift
// Auto-generated - Codable wrapper for dynamic JSON values

import Foundation

/// Type-safe representation of any JSON value
public enum JSONValue: Codable, Sendable, Hashable {
    case string(String)
    case int(Int)
    case double(Double)
    case bool(Bool)
    case object([String: JSONValue])
    case array([JSONValue])
    case null

    public init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()

        if container.decodeNil() {
            self = .null
        } else if let bool = try? container.decode(Bool.self) {
            self = .bool(bool)
        } else if let int = try? container.decode(Int.self) {
            self = .int(int)
        } else if let double = try? container.decode(Double.self) {
            self = .double(double)
        } else if let string = try? container.decode(String.self) {
            self = .string(string)
        } else if let array = try? container.decode([JSONValue].self) {
            self = .array(array)
        } else if let object = try? container.decode([String: JSONValue].self) {
            self = .object(object)
        } else {
            throw DecodingError.typeMismatch(
                JSONValue.self,
                DecodingError.Context(codingPath: decoder.codingPath, debugDescription: "Unknown JSON value")
            )
        }
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case .string(let value): try container.encode(value)
        case .int(let value): try container.encode(value)
        case .double(let value): try container.encode(value)
        case .bool(let value): try container.encode(value)
        case .object(let value): try container.encode(value)
        case .array(let value): try container.encode(value)
        case .null: try container.encodeNil()
        }
    }

    // MARK: - Convenience accessors

    public var stringValue: String? {
        if case .string(let value) = self { return value }
        return nil
    }

    public var intValue: Int? {
        if case .int(let value) = self { return value }
        return nil
    }

    public var doubleValue: Double? {
        if case .double(let value) = self { return value }
        if case .int(let value) = self { return Double(value) }
        return nil
    }

    public var boolValue: Bool? {
        if case .bool(let value) = self { return value }
        return nil
    }

    public var objectValue: [String: JSONValue]? {
        if case .object(let value) = self { return value }
        return nil
    }

    public var arrayValue: [JSONValue]? {
        if case .array(let value) = self { return value }
        return nil
    }

    public var isNull: Bool {
        if case .null = self { return true }
        return false
    }

    public subscript(key: String) -> JSONValue? {
        if case .object(let dict) = self {
            return dict[key]
        }
        return nil
    }

    public subscript(index: Int) -> JSONValue? {
        if case .array(let arr) = self, index >= 0 && index < arr.count {
            return arr[index]
        }
        return nil
    }
}
'''
        return GeneratedFile(
            path="JSONValue.swift",
            content=content,
            description="Codable wrapper for dynamic JSON values",
        )

    def _generate_claude_md(
        self,
        ops_by_tag: dict[str, list[IROperationObject]],
    ) -> GeneratedFile:
        """Generate CLAUDE.md documentation."""
        group_name = self.group_name or "API"

        pascal_group = self._to_pascal_case(group_name)

        lines = [
            f"# {group_name.title()} Swift API",
            "",
            "Auto-generated Swift Codable types for REST API.",
            "",
            "## Files",
            "",
            "| File | Description |",
            "|------|-------------|",
            f"| `{pascal_group}Endpoints.swift` | API path constants |",
            f"| `{pascal_group}Types.swift` | Codable models (including paginated types) |",
            "",
            "## Usage",
            "",
            "```swift",
            "// List endpoint (paginated)",
            f"let result: PaginatedMachineList = try await rest.get(",
            f"    path: {pascal_group}API.Machines.list",
            ")",
            "",
            "// Detail endpoint",
            "let machine: Machine = try await rest.get(",
            f"    path: {pascal_group}API.Machines.detail(machineId)",
            ")",
            "```",
            "",
            "## Endpoints",
            "",
        ]

        for tag, operations in sorted(ops_by_tag.items()):
            lines.append(f"### {tag.title()}")
            lines.append("")
            for op in sorted(operations, key=lambda x: x.path):
                lines.append(f"- `{op.http_method} {op.path}`")
            lines.append("")

        lines.append("## Regeneration")
        lines.append("")
        lines.append("```bash")
        lines.append("cd /projects/solution/django")
        lines.append(f"poetry run python manage.py generate_client --swift-codable --groups {group_name}")
        lines.append("```")
        lines.append("")

        return GeneratedFile(
            path="CLAUDE.md",
            content="\n".join(lines),
            description="AI documentation for Swift API",
        )

    def _to_pascal_case(self, name: str) -> str:
        """Convert to PascalCase."""
        parts = name.replace("-", "_").split("_")
        return "".join(part.capitalize() for part in parts)

    # Required abstract method implementations

    def generate_schema(self, schema: "IRSchemaObject") -> str:
        """Generate code for a single schema."""
        # Handled by models_generator
        return ""

    def generate_enum(self, schema: "IRSchemaObject") -> str:
        """Generate enum code from schema."""
        # Handled by models_generator
        return ""

    def generate_operation(self, operation: "IROperationObject") -> str:
        """Generate code for a single operation."""
        # Handled by endpoints_generator
        return ""
