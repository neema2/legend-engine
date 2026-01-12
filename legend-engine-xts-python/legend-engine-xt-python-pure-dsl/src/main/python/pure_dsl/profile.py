"""
Profile definition for Pure DSL.

Profiles define stereotypes and tags that can be applied to other Pure elements.

Example:
    profile = Profile("my::package::MyProfile") \\
        .with_stereotypes("deprecated", "internal", "api") \\
        .with_tags("doc", "since", "author")

    print(profile.to_pure())
    # Profile my::package::MyProfile
    # {
    #   stereotypes: [deprecated, internal, api];
    #   tags: [doc, since, author];
    # }
"""

from typing import List, Optional

from pure_dsl.core import PureElement


class Profile(PureElement):
    """
    A Pure Profile definition.

    Profiles define stereotypes and tags that provide metadata for
    other Pure elements like Classes, Properties, Enums, etc.

    Example:
        >>> profile = Profile("doc")
        >>> profile.with_stereotypes("deprecated", "internal")
        >>> profile.with_tags("doc", "since")
        >>> print(profile.to_pure())
    """

    def __init__(self, name: str, package: Optional[str] = None):
        """
        Initialize a Profile.

        Args:
            name: Profile name (can be qualified like "my::package::MyProfile")
            package: Optional package override
        """
        # Handle qualified names
        if "::" in name and package is None:
            parts = name.rsplit("::", 1)
            package = parts[0]
            name = parts[1]

        super().__init__(name, package)
        self._stereotypes: List[str] = []
        self._tags: List[str] = []

    def with_stereotype(self, name: str) -> "Profile":
        """
        Add a stereotype to this profile.

        Args:
            name: Stereotype name

        Returns:
            self for chaining
        """
        self._stereotypes.append(name)
        return self

    def with_stereotypes(self, *names: str) -> "Profile":
        """
        Add multiple stereotypes to this profile.

        Args:
            *names: Stereotype names

        Returns:
            self for chaining
        """
        self._stereotypes.extend(names)
        return self

    def with_tag(self, name: str) -> "Profile":
        """
        Add a tag to this profile.

        Args:
            name: Tag name

        Returns:
            self for chaining
        """
        self._tags.append(name)
        return self

    def with_tags(self, *names: str) -> "Profile":
        """
        Add multiple tags to this profile.

        Args:
            *names: Tag names

        Returns:
            self for chaining
        """
        self._tags.extend(names)
        return self

    def to_pure(self) -> str:
        """Generate Pure code for this Profile."""
        lines = [f"Profile {self.qualified_name}"]
        lines.append("{")

        if self._stereotypes:
            st_list = ", ".join(self._stereotypes)
            lines.append(f"  stereotypes: [{st_list}];")

        if self._tags:
            tag_list = ", ".join(self._tags)
            lines.append(f"  tags: [{tag_list}];")

        lines.append("}")
        return "\n".join(lines)
