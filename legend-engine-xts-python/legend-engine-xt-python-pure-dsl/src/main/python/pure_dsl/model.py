"""
PureModel - Container for Pure elements.

The PureModel class is the main container that holds all Pure elements
and generates the complete Pure code file.

Example:
    model = PureModel("my::package")

    # Add elements
    model.add(person_class)
    model.add(address_class)
    model.add(person_address_association)

    # Generate Pure code
    print(model.to_pure())

    # Save to file
    model.save("model.pure")
"""

from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from pure_dsl.core import PureElement
from pure_dsl.profile import Profile
from pure_dsl.enumeration import Enum
from pure_dsl.classes import Class
from pure_dsl.association import Association
from pure_dsl.function import Function
from pure_dsl.measure import Measure
from pure_dsl.service import Service


class PureModel:
    """
    Container for Pure elements that generates a complete Pure file.

    PureModel manages:
    - Default package for elements without explicit packages
    - Import statements
    - Ordering of elements (profiles first, then enums, classes, etc.)
    - Code generation

    Example:
        >>> model = PureModel("my::domain")
        >>> model.add(person_class)
        >>> model.add(address_class)
        >>> model.add_import("meta::pure::profiles::*")
        >>> print(model.to_pure())
    """

    def __init__(self, default_package: Optional[str] = None):
        """
        Initialize a PureModel.

        Args:
            default_package: Default package for elements without explicit packages
        """
        self.default_package = default_package
        self._imports: Set[str] = set()
        self._profiles: List[Profile] = []
        self._enums: List[Enum] = []
        self._classes: List[Class] = []
        self._associations: List[Association] = []
        self._functions: List[Function] = []
        self._measures: List[Measure] = []
        self._services: List[Service] = []
        self._other_elements: List[PureElement] = []

    def add_import(self, import_path: str) -> "PureModel":
        """
        Add an import statement.

        Args:
            import_path: Import path (e.g., "meta::pure::profiles::*")

        Returns:
            self for chaining
        """
        self._imports.add(import_path)
        return self

    def add(self, element: PureElement) -> "PureModel":
        """
        Add an element to this model.

        The element will be assigned the default package if it doesn't
        have an explicit package.

        Args:
            element: Any PureElement (Class, Enum, Function, etc.)

        Returns:
            self for chaining
        """
        # Assign default package if not set
        if element.package is None and self.default_package:
            element.package = self.default_package

        # Sort into appropriate list
        if isinstance(element, Profile):
            self._profiles.append(element)
        elif isinstance(element, Enum):
            self._enums.append(element)
        elif isinstance(element, Class):
            self._classes.append(element)
        elif isinstance(element, Association):
            self._associations.append(element)
        elif isinstance(element, Function):
            self._functions.append(element)
        elif isinstance(element, Measure):
            self._measures.append(element)
        elif isinstance(element, Service):
            self._services.append(element)
        else:
            self._other_elements.append(element)

        return self

    def add_all(self, *elements: PureElement) -> "PureModel":
        """
        Add multiple elements to this model.

        Args:
            *elements: Elements to add

        Returns:
            self for chaining
        """
        for element in elements:
            self.add(element)
        return self

    def profile(self, name: str) -> Profile:
        """
        Create and add a Profile to this model.

        Args:
            name: Profile name

        Returns:
            The created Profile for further configuration
        """
        p = Profile(name, self.default_package)
        self._profiles.append(p)
        return p

    def enum(self, name: str) -> Enum:
        """
        Create and add an Enum to this model.

        Args:
            name: Enum name

        Returns:
            The created Enum for further configuration
        """
        e = Enum(name, self.default_package)
        self._enums.append(e)
        return e

    def class_(self, name: str) -> Class:
        """
        Create and add a Class to this model.

        Args:
            name: Class name

        Returns:
            The created Class for further configuration
        """
        c = Class(name, self.default_package)
        self._classes.append(c)
        return c

    def association(self, name: str) -> Association:
        """
        Create and add an Association to this model.

        Args:
            name: Association name

        Returns:
            The created Association for further configuration
        """
        a = Association(name, self.default_package)
        self._associations.append(a)
        return a

    def function(self, name: str) -> Function:
        """
        Create and add a Function to this model.

        Args:
            name: Function name

        Returns:
            The created Function for further configuration
        """
        f = Function(name, self.default_package)
        self._functions.append(f)
        return f

    def measure(self, name: str) -> Measure:
        """
        Create and add a Measure to this model.

        Args:
            name: Measure name

        Returns:
            The created Measure for further configuration
        """
        m = Measure(name, self.default_package)
        self._measures.append(m)
        return m

    def service(self, name: str) -> Service:
        """
        Create and add a Service to this model.

        Args:
            name: Service name

        Returns:
            The created Service for further configuration
        """
        s = Service(name, self.default_package)
        self._services.append(s)
        return s

    def to_pure(self) -> str:
        """
        Generate Pure code for all elements in this model.

        Elements are ordered as:
        1. Imports
        2. Profiles
        3. Enums
        4. Classes
        5. Associations
        6. Functions
        7. Measures
        8. Services
        9. Other elements

        Returns:
            Complete Pure code as a string
        """
        sections = []

        # Imports
        if self._imports:
            import_lines = sorted(self._imports)
            for imp in import_lines:
                sections.append(f"import {imp};")
            sections.append("")

        # Elements in order
        element_lists = [
            self._profiles,
            self._enums,
            self._classes,
            self._associations,
            self._functions,
            self._measures,
            self._services,
            self._other_elements,
        ]

        for elements in element_lists:
            for element in elements:
                sections.append(element.to_pure())
                sections.append("")

        # Join and clean up trailing newlines
        result = "\n".join(sections)
        return result.rstrip() + "\n"

    def save(self, path: Union[str, Path]) -> None:
        """
        Save the Pure code to a file.

        Args:
            path: File path to save to
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_pure())

    def __repr__(self) -> str:
        """String representation of this model."""
        counts = {
            "profiles": len(self._profiles),
            "enums": len(self._enums),
            "classes": len(self._classes),
            "associations": len(self._associations),
            "functions": len(self._functions),
            "measures": len(self._measures),
            "services": len(self._services),
        }
        non_zero = {k: v for k, v in counts.items() if v > 0}
        return f"PureModel(package={self.default_package!r}, {non_zero})"


# Convenience function for quick model creation
def pure_model(
    package: Optional[str] = None,
    imports: Optional[List[str]] = None,
) -> PureModel:
    """
    Create a new PureModel with optional imports.

    Example:
        model = pure_model(
            package="my::domain",
            imports=["meta::pure::profiles::*"]
        )

    Args:
        package: Default package for elements
        imports: Optional list of import paths

    Returns:
        PureModel instance
    """
    model = PureModel(package)
    if imports:
        for imp in imports:
            model.add_import(imp)
    return model
