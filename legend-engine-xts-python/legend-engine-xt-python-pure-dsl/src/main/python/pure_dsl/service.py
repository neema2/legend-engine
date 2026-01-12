"""
Service definitions for Pure DSL.

Services define API endpoints with queries, mappings, and runtimes.

Example:
    service = Service("PersonService") \\
        .pattern("/api/persons") \\
        .owners("user1", "user2") \\
        .documentation("Get all persons") \\
        .single_execution(
            query="|Person.all()->project([x|$x.firstName, x|$x.lastName], ['First', 'Last'])",
            mapping="PersonMapping",
            runtime="H2Runtime"
        )
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from pure_dsl.core import PureElement


@dataclass
class ServiceExecution:
    """Base class for service executions."""
    query: str
    mapping: str
    runtime: str

    def to_pure(self) -> str:
        """Generate Pure code for this execution."""
        raise NotImplementedError


@dataclass
class SingleExecution(ServiceExecution):
    """A single execution service configuration."""

    def to_pure(self) -> str:
        """Generate Pure code for this execution."""
        lines = []
        lines.append("execution: Single")
        lines.append("{")
        lines.append(f"  query: {self.query};")
        lines.append(f"  mapping: {self.mapping};")
        lines.append(f"  runtime: {self.runtime};")
        lines.append("}")
        return "\n".join(lines)


@dataclass
class KeyedExecution:
    """An execution within a multi-execution keyed by a value."""
    key_value: str
    mapping: str
    runtime: str

    def to_pure(self) -> str:
        """Generate Pure code for this keyed execution."""
        lines = []
        lines.append(f"executions['{self.key_value}']:")
        lines.append("{")
        lines.append(f"  mapping: {self.mapping};")
        lines.append(f"  runtime: {self.runtime};")
        lines.append("}")
        return "\n".join(lines)


@dataclass
class MultiExecution:
    """A multi-execution service configuration."""
    query: str
    key: str
    executions: List[KeyedExecution] = field(default_factory=list)

    def add_execution(
        self,
        key_value: str,
        mapping: str,
        runtime: str,
    ) -> "MultiExecution":
        """Add a keyed execution."""
        self.executions.append(KeyedExecution(key_value, mapping, runtime))
        return self

    def to_pure(self) -> str:
        """Generate Pure code for this execution."""
        lines = []
        lines.append("execution: Multi")
        lines.append("{")
        lines.append(f"  query: {self.query};")
        lines.append(f"  key: '{self.key}';")

        for exec in self.executions:
            for line in exec.to_pure().split("\n"):
                lines.append("  " + line)

        lines.append("}")
        return "\n".join(lines)


class Service(PureElement):
    """
    A Pure Service definition.

    Services define API endpoints with queries, mappings, and runtimes.

    Example:
        >>> svc = Service("PersonService")
        >>> svc.pattern("/api/persons")
        >>> svc.owners("user1")
        >>> svc.single_execution(
        ...     query="|Person.all()",
        ...     mapping="PersonMapping",
        ...     runtime="H2Runtime"
        ... )
        >>> print(svc.to_pure())
    """

    def __init__(self, name: str, package: Optional[str] = None):
        """
        Initialize a Service.

        Args:
            name: Service name (can be qualified)
            package: Optional package override
        """
        # Handle qualified names
        if "::" in name and package is None:
            parts = name.rsplit("::", 1)
            package = parts[0]
            name = parts[1]

        super().__init__(name, package)
        self._pattern: Optional[str] = None
        self._owners: List[str] = []
        self._documentation: Optional[str] = None
        self._auto_activate: bool = True
        self._execution: Optional[Union[SingleExecution, MultiExecution]] = None

    def pattern(self, url_pattern: str) -> "Service":
        """
        Set the URL pattern for this service.

        Args:
            url_pattern: URL pattern (e.g., "/api/persons")

        Returns:
            self for chaining
        """
        self._pattern = url_pattern
        return self

    def owners(self, *owner_names: str) -> "Service":
        """
        Set the owners of this service.

        Args:
            *owner_names: Owner names

        Returns:
            self for chaining
        """
        self._owners.extend(owner_names)
        return self

    def documentation(self, doc: str) -> "Service":
        """
        Set the documentation for this service.

        Args:
            doc: Documentation string

        Returns:
            self for chaining
        """
        self._documentation = doc
        return self

    def auto_activate(self, enabled: bool = True) -> "Service":
        """
        Set whether to auto-activate updates.

        Args:
            enabled: True to enable auto-activation

        Returns:
            self for chaining
        """
        self._auto_activate = enabled
        return self

    def single_execution(
        self,
        query: str,
        mapping: str,
        runtime: str,
    ) -> "Service":
        """
        Configure a single execution for this service.

        Args:
            query: Pure query expression
            mapping: Mapping name
            runtime: Runtime name

        Returns:
            self for chaining
        """
        self._execution = SingleExecution(query, mapping, runtime)
        return self

    def multi_execution(
        self,
        query: str,
        key: str,
    ) -> MultiExecution:
        """
        Start configuring a multi-execution for this service.

        Args:
            query: Pure query expression
            key: Key name for execution selection

        Returns:
            MultiExecution for chaining
        """
        self._execution = MultiExecution(query, key)
        return self._execution

    def with_execution(
        self,
        execution: Union[SingleExecution, MultiExecution],
    ) -> "Service":
        """
        Set a pre-configured execution.

        Args:
            execution: Execution configuration

        Returns:
            self for chaining
        """
        self._execution = execution
        return self

    def to_pure(self) -> str:
        """Generate Pure code for this Service."""
        lines = []

        # Service declaration
        prefix = self._annotations_prefix()
        lines.append(f"Service {prefix}{self.qualified_name}")
        lines.append("{")

        # Pattern
        if self._pattern:
            lines.append(f"  pattern: '{self._pattern}';")

        # Owners
        if self._owners:
            lines.append("  owners:")
            lines.append("  [")
            for owner in self._owners:
                lines.append(f"    '{owner}',")
            # Remove trailing comma from last owner
            if lines[-1].endswith(","):
                lines[-1] = lines[-1][:-1]
            lines.append("  ];")

        # Documentation
        if self._documentation:
            lines.append(f"  documentation: '{self._documentation}';")
        else:
            lines.append("  documentation: '';")

        # Auto-activate
        lines.append(f"  autoActivateUpdates: {'true' if self._auto_activate else 'false'};")

        # Execution
        if self._execution:
            exec_str = self._execution.to_pure()
            for line in exec_str.split("\n"):
                lines.append("  " + line)

        lines.append("}")

        return "\n".join(lines)


def service(
    name: str,
    pattern: str,
    query: str,
    mapping: str,
    runtime: str,
    owners: Optional[List[str]] = None,
    documentation: Optional[str] = None,
    package: Optional[str] = None,
) -> Service:
    """
    Factory function to create a simple single-execution service.

    Example:
        svc = service(
            "PersonService",
            pattern="/api/persons",
            query="|Person.all()->project([x|$x.name], ['Name'])",
            mapping="PersonMapping",
            runtime="H2Runtime",
            owners=["user1"],
            documentation="Get all persons"
        )

    Args:
        name: Service name
        pattern: URL pattern
        query: Pure query expression
        mapping: Mapping name
        runtime: Runtime name
        owners: Optional list of owner names
        documentation: Optional documentation
        package: Optional package

    Returns:
        Service instance
    """
    svc = Service(name, package)
    svc.pattern(pattern)

    if owners:
        svc.owners(*owners)

    if documentation:
        svc.documentation(documentation)

    svc.single_execution(query, mapping, runtime)

    return svc
